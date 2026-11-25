"""Publication boundaries: synthetic assets only; never calls GitHub."""
import hashlib
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import publish_repair_candidate as release

REPO = "dev351en/gtm"
COMMIT = "a" * 40


def release_record(*, draft=False):
    return {"id": 17, "tag_name": release.TAG, "draft": draft, "prerelease": True,
            "target_commitish": COMMIT, "html_url": "https://github.com/dev351en/gtm/releases/tag/" + release.TAG,
            "assets": [{"name": name} for name in sorted(release.ASSETS)]}


class RepairPublicationTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        capture = redirect_stdout(self.output)
        capture.__enter__()
        self.addCleanup(capture.__exit__, None, None, None)
        for tool in ("api", "gh"):
            guard = mock.patch.object(release, tool, side_effect=AssertionError("Unmocked GitHub access in a fixture test"))
            guard.start()
            self.addCleanup(guard.stop)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        for name in release.ASSETS - {"SHA256SUMS", "release-report.json"}:
            (self.folder / name).write_bytes(("Synthetic fixture " + name).encode())
        self.report = {"status": "PASS", "pack_url": f"https://github.com/{REPO}/releases/download/{release.TAG}/{release.JAVA_NAME}"}
        self.save()

    def save(self):
        (self.folder / "release-report.json").write_text(json.dumps(self.report))
        (self.folder / "SHA256SUMS").write_text("".join(
            release.hash_file(self.folder / name) + "  " + name + "\n"
            for name in sorted(release.ASSETS - {"SHA256SUMS"})))

    def test_corrupt_asset_stops_before_network(self):
        (self.folder / release.JAVA_NAME).write_bytes(b"corrupt")
        with mock.patch.object(release, "api") as api, self.assertRaises(release.PublicationError):
            release.publish(self.folder, REPO, COMMIT)
        api.assert_not_called()

    def test_wrong_pack_download_url_stops_before_network(self):
        self.report["pack_url"] = "https://example.invalid/old-pack.zip"
        self.save()
        with mock.patch.object(release, "api") as api, self.assertRaises(release.PublicationError):
            release.publish(self.folder, REPO, COMMIT)
        api.assert_not_called()

    def test_unchecked_asset_cannot_be_omitted_from_checksums(self):
        checksum = self.folder / "SHA256SUMS"
        checksum.write_text("\n".join(checksum.read_text().splitlines()[:-1]))
        with self.assertRaises(release.PublicationError): release.local_assets(self.folder, REPO)

    def test_other_source_tag_is_never_moved(self):
        with mock.patch.object(release, "find_release", return_value=None), \
             mock.patch.object(release, "api", return_value={"object": {"sha": "b" * 40}}), \
             mock.patch.object(release, "gh") as gh, self.assertRaises(release.PublicationError):
            release.publish(self.folder, REPO, COMMIT)
        gh.assert_not_called()

    def test_partial_public_release_is_not_completed_or_replaced(self):
        existing = {"draft": False, "prerelease": True, "assets": [{"name": release.JAVA_NAME}]}
        with mock.patch.object(release, "find_release", return_value=existing), \
             mock.patch.object(release, "api", return_value={"object": {"type": "commit", "sha": COMMIT}}), \
             mock.patch.object(release, "gh") as gh, self.assertRaises(release.PublicationError):
            release.publish(self.folder, REPO, COMMIT)
        gh.assert_not_called()

    def test_other_commit_draft_is_left_unchanged(self):
        existing = {"draft": True, "target_commitish": "b" * 40, "assets": []}
        with mock.patch.object(release, "find_release", return_value=existing), \
             mock.patch.object(release, "api", return_value=None), \
             mock.patch.object(release, "gh") as gh, self.assertRaises(release.PublicationError):
            release.publish(self.folder, REPO, COMMIT)
        gh.assert_not_called()

    def test_remote_readback_checks_bytes(self):
        def download(args, **unused):
            folder = Path(args[args.index("--dir") + 1])
            (folder / release.JAVA_NAME).write_bytes(b"wrong downloaded content")
        with mock.patch.object(release, "gh", side_effect=download), self.assertRaises(release.PublicationError):
            release.verify_remote(REPO, {"assets": [{"name": release.JAVA_NAME}]}, release.local_assets(self.folder, REPO))

    def test_duplicate_and_unknown_remote_names_refused(self):
        for values in [[release.JAVA_NAME, release.JAVA_NAME], ["../../private"]]:
            with self.subTest(values=values), self.assertRaises(release.PublicationError):
                release.names({"assets": [{"name": name} for name in values]})

    def test_identical_public_assets_at_other_source_commit_are_refused(self):
        with mock.patch.object(release, "find_release", return_value=release_record()), \
             mock.patch.object(release, "api", return_value={"object": {"type": "commit", "sha": "b" * 40}}), \
             mock.patch.object(release, "verify_remote") as remote, \
             mock.patch.object(release, "gh") as gh, self.assertRaises(release.PublicationError):
            release.publish(self.folder, REPO, COMMIT)
        remote.assert_not_called()
        gh.assert_not_called()

    def test_existing_public_release_must_still_have_its_source_tag(self):
        with mock.patch.object(release, "find_release", return_value=release_record()), \
             mock.patch.object(release, "api", return_value=None), \
             mock.patch.object(release, "verify_remote") as remote, self.assertRaises(release.PublicationError):
            release.publish(self.folder, REPO, COMMIT)
        remote.assert_not_called()

    def test_matching_public_release_is_verified_without_writes(self):
        with mock.patch.object(release, "find_release", return_value=release_record()), \
             mock.patch.object(release, "api", return_value={"object": {"type": "commit", "sha": COMMIT}}) as api, \
             mock.patch.object(release, "verify_remote") as remote, \
             mock.patch.object(release, "gh") as gh:
            release.publish(self.folder, REPO, COMMIT)
        api.assert_called_once_with(f"repos/{REPO}/git/ref/tags/{release.TAG}", allow_missing=True)
        remote.assert_called_once()
        gh.assert_not_called()

    def test_matching_annotated_tag_resolves_to_its_commit(self):
        tag_sha = "c" * 40
        with mock.patch.object(release, "find_release", return_value=release_record()), \
             mock.patch.object(release, "api", side_effect=[
                 {"object": {"type": "tag", "sha": tag_sha}},
                 {"object": {"type": "commit", "sha": COMMIT}}]) as api, \
             mock.patch.object(release, "verify_remote"), mock.patch.object(release, "gh") as gh:
            release.publish(self.folder, REPO, COMMIT)
        self.assertEqual(api.call_args_list[-1], mock.call(f"repos/{REPO}/git/tags/{tag_sha}"))
        gh.assert_not_called()

    def test_annotated_tag_resolution_is_bounded(self):
        with mock.patch.object(release, "api", return_value={"object": {"type": "tag", "sha": "c" * 40}}) as api, \
             self.assertRaises(release.PublicationError):
            release.require_tag_target(REPO, COMMIT)
        self.assertEqual(api.call_count, 5)  # one ref plus at most four tag objects

    def test_release_readback_requires_same_id_and_tag(self):
        for changes in [{"id": 18}, {"tag_name": "another-release"}, {"draft": None}]:
            with self.subTest(changes=changes), \
                 mock.patch.object(release, "api", return_value=release_record() | changes), \
                 self.assertRaises(release.PublicationError):
                release.read_release(REPO, 17)

    def test_changed_draft_identity_stops_before_publication(self):
        draft = release_record(draft=True)
        with mock.patch.object(release, "find_release", return_value=draft), \
             mock.patch.object(release, "api", side_effect=[
                 {"object": {"type": "commit", "sha": COMMIT}},
                 draft | {"tag_name": "another-release"}]), \
             mock.patch.object(release, "verify_remote"), mock.patch.object(release, "gh") as gh, \
             self.assertRaises(release.PublicationError):
            release.publish(self.folder, REPO, COMMIT)
        gh.assert_not_called()

    def test_resumed_draft_is_published_only_after_identity_and_tag_checks(self):
        draft, public = release_record(draft=True), release_record()
        tag = {"object": {"type": "commit", "sha": COMMIT}}
        with mock.patch.object(release, "find_release", return_value=draft), \
             mock.patch.object(release, "api", side_effect=[tag, draft, tag, public, tag]) as api, \
             mock.patch.object(release, "verify_remote") as remote, mock.patch.object(release, "gh") as gh:
            release.publish(self.folder, REPO, COMMIT)
        self.assertEqual(remote.call_count, 2)
        self.assertEqual(api.call_count, 5)
        gh.assert_called_once_with(["release", "edit", release.TAG, "--repo", REPO,
                                    "--draft=false", "--prerelease", "--latest=false"],
                                   stage="Publish verified repair candidate")

    def test_final_tag_mismatch_never_reports_verified_publication(self):
        draft, public = release_record(draft=True), release_record()
        tag = {"object": {"type": "commit", "sha": COMMIT}}
        moved = {"object": {"type": "commit", "sha": "b" * 40}}
        with mock.patch.object(release, "find_release", return_value=draft), \
             mock.patch.object(release, "api", side_effect=[tag, draft, tag, public, moved]), \
             mock.patch.object(release, "verify_remote"), mock.patch.object(release, "gh") as gh, \
             mock.patch("builtins.print") as printed, self.assertRaises(release.PublicationError):
            release.publish(self.folder, REPO, COMMIT)
        self.assertEqual(gh.call_count, 1)
        self.assertNotIn("--force", gh.call_args.args[0])
        printed.assert_not_called()

    def test_created_draft_listing_delay_retries_reads_without_recreating(self):
        draft, public = release_record(draft=True), release_record()
        empty_draft = draft | {"assets": []}
        tag = {"object": {"type": "commit", "sha": COMMIT}}
        with mock.patch.object(release, "find_release", side_effect=[None, None, None, empty_draft]) as lookup, \
             mock.patch.object(release, "api", side_effect=[None, draft, tag, public, tag]), \
             mock.patch.object(release, "verify_remote") as remote, \
             mock.patch.object(release, "gh") as gh, mock.patch.object(release.time, "sleep") as sleep:
            release.publish(self.folder, REPO, COMMIT)
        self.assertEqual(lookup.call_args_list, [mock.call(REPO)] * 4)
        self.assertEqual(sleep.call_args_list, [mock.call(1), mock.call(2)])
        self.assertEqual([call.args[0][:2] for call in gh.call_args_list],
                         [["release", "create"], ["release", "upload"], ["release", "edit"]])
        self.assertEqual(remote.call_count, 2)
        self.assertIn("--target", gh.call_args_list[0].args[0])
        self.assertIn(COMMIT, gh.call_args_list[0].args[0])
        self.assertNotIn("--clobber", gh.call_args_list[1].args[0])

    def test_created_draft_visibility_retry_is_bounded_and_never_recreates(self):
        with mock.patch.object(release, "find_release", return_value=None) as lookup, \
             mock.patch.object(release, "api", return_value=None), \
             mock.patch.object(release, "verify_remote") as remote, \
             mock.patch.object(release, "gh") as gh, mock.patch.object(release.time, "sleep") as sleep, \
             self.assertRaisesRegex(release.PublicationError, "five read-only lookups"):
            release.publish(self.folder, REPO, COMMIT)
        self.assertEqual(lookup.call_count, 6)  # initial lookup plus five after creation
        self.assertEqual(sleep.call_args_list, [mock.call(1), mock.call(2), mock.call(3), mock.call(4)])
        self.assertEqual(sum(call.args[0] for call in sleep.call_args_list), 10)
        gh.assert_called_once()
        self.assertEqual(gh.call_args.args[0][:2], ["release", "create"])
        remote.assert_not_called()

    def test_created_draft_wrong_commit_is_not_retried_or_uploaded(self):
        wrong_draft = release_record(draft=True) | {"target_commitish": "b" * 40}
        with mock.patch.object(release, "find_release", side_effect=[None, wrong_draft]) as lookup, \
             mock.patch.object(release, "api", return_value=None), \
             mock.patch.object(release, "verify_remote") as remote, \
             mock.patch.object(release, "gh") as gh, mock.patch.object(release.time, "sleep") as sleep, \
             self.assertRaisesRegex(release.PublicationError, "exact source commit"):
            release.publish(self.folder, REPO, COMMIT)
        self.assertEqual(lookup.call_count, 2)
        sleep.assert_not_called()
        gh.assert_called_once()
        self.assertEqual(gh.call_args.args[0][:2], ["release", "create"])
        remote.assert_not_called()

    def test_created_draft_identity_error_is_not_treated_as_absent(self):
        wrong_identity = release_record(draft=True) | {"tag_name": "another-release"}
        with mock.patch.object(release, "api", side_effect=[
                 [], None, [{"id": 17, "tag_name": release.TAG}], wrong_identity]) as api, \
             mock.patch.object(release, "verify_remote") as remote, \
             mock.patch.object(release, "gh") as gh, mock.patch.object(release.time, "sleep") as sleep, \
             self.assertRaisesRegex(release.PublicationError, "different repair release identity"):
            release.publish(self.folder, REPO, COMMIT)
        self.assertEqual(api.call_count, 4)
        self.assertEqual(api.call_args_list[-1], mock.call(f"repos/{REPO}/releases/17"))
        sleep.assert_not_called()
        gh.assert_called_once()
        self.assertEqual(gh.call_args.args[0][:2], ["release", "create"])
        remote.assert_not_called()

    def test_failed_creation_has_no_followup_lookup_or_retry(self):
        with mock.patch.object(release, "find_release", return_value=None) as lookup, \
             mock.patch.object(release, "api", return_value=None), \
             mock.patch.object(release, "gh", side_effect=release.PublicationError("Creation failed")) as gh, \
             mock.patch.object(release.time, "sleep") as sleep, \
             self.assertRaisesRegex(release.PublicationError, "Creation failed"):
            release.publish(self.folder, REPO, COMMIT)
        lookup.assert_called_once_with(REPO)
        gh.assert_called_once()
        sleep.assert_not_called()


if __name__ == "__main__": unittest.main()
