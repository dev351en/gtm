"""Offline release-state tests; gh is replaced and no GitHub request is made."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import publish_functional_runtime as publication


COMMIT = "a" * 40
REPO = "dev351en/gtm"


def release(draft=False, names=None):
    return {"draft": draft, "prerelease": True, "target_commitish": COMMIT,
            "html_url": "https://github.com/dev351en/gtm/releases/tag/" + publication.TAG,
            "assets": [{"name": name} for name in sorted(publication.ASSET_NAMES if names is None else names)]}


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        for name in publication.ASSET_NAMES - {"SHA256SUMS", "assembly-report.json"}:
            (self.directory / name).write_bytes(("Synthetic " + name).encode())
        (self.directory / "assembly-report.json").write_text(json.dumps({"status": "PASS", "server_started": False}))
        (self.directory / "SHA256SUMS").write_text("".join(
            publication.sha256(self.directory / name) + "  " + name + "\n"
            for name in sorted(publication.ASSET_NAMES - {"SHA256SUMS"})))

    def test_local_changed_asset_blocks_publication_before_any_request(self):
        (self.directory / publication.ART_NAME).write_bytes(b"changed")
        with mock.patch.object(publication, "api") as api:
            with self.assertRaises(publication.PublicationError):
                publication.publish(self.directory, REPO, COMMIT)
            api.assert_not_called()

    def test_identical_published_release_is_verified_and_never_rewritten(self):
        with mock.patch.object(publication, "api", return_value=release()), \
             mock.patch.object(publication, "verify_remote") as verify, \
             mock.patch.object(publication, "gh") as gh, contextlib.redirect_stdout(io.StringIO()):
            publication.publish(self.directory, REPO, COMMIT)
        verify.assert_called_once()
        gh.assert_not_called()

    def test_existing_different_asset_is_not_overwritten(self):
        with mock.patch.object(publication, "api", return_value=release()), \
             mock.patch.object(publication, "verify_remote", side_effect=publication.PublicationError("Different bytes")), \
             mock.patch.object(publication, "gh") as gh:
            with self.assertRaises(publication.PublicationError):
                publication.publish(self.directory, REPO, COMMIT)
        gh.assert_not_called()

    def test_partial_public_release_is_not_silently_completed(self):
        with mock.patch.object(publication, "api", return_value=release(names={publication.JAVA_NAME})), \
             mock.patch.object(publication, "gh") as gh:
            with self.assertRaises(publication.PublicationError):
                publication.publish(self.directory, REPO, COMMIT)
        gh.assert_not_called()

    def test_new_release_is_draft_then_verified_then_prerelease(self):
        responses = [None, None, release(True, set()), release(True), release()]
        with mock.patch.object(publication, "api", side_effect=responses), \
             mock.patch.object(publication, "verify_remote") as verify, \
             mock.patch.object(publication, "gh") as gh, contextlib.redirect_stdout(io.StringIO()):
            publication.publish(self.directory, REPO, COMMIT)
        calls = [call.args[0] for call in gh.call_args_list]
        self.assertEqual([args[1] for args in calls], ["create", "upload", "edit"])
        self.assertIn("--draft", calls[0])
        self.assertIn("--prerelease", calls[0])
        self.assertIn("--draft=false", calls[-1])
        self.assertIn("--prerelease", calls[-1])
        self.assertTrue(all("--clobber" not in args for args in calls))
        self.assertEqual(verify.call_count, 2)

    def test_matching_partial_draft_uploads_only_missing_files(self):
        existing = {publication.JAVA_NAME}
        responses = [release(True, existing), {"object": {"type": "commit", "sha": COMMIT}},
                     release(True), release()]
        with mock.patch.object(publication, "api", side_effect=responses), \
             mock.patch.object(publication, "verify_remote") as verify, \
             mock.patch.object(publication, "gh") as gh, contextlib.redirect_stdout(io.StringIO()):
            publication.publish(self.directory, REPO, COMMIT)
        calls = [call.args[0] for call in gh.call_args_list]
        self.assertEqual([args[1] for args in calls], ["upload", "edit"])
        self.assertNotIn(str((self.directory / publication.JAVA_NAME).resolve()), calls[0])
        self.assertEqual(verify.call_count, 2)

    def test_existing_tag_at_another_commit_is_never_moved(self):
        with mock.patch.object(publication, "api", side_effect=[None, {"object": {"type": "commit", "sha": "b" * 40}}]), \
             mock.patch.object(publication, "gh") as gh:
            with self.assertRaises(publication.PublicationError):
                publication.publish(self.directory, REPO, COMMIT)
        gh.assert_not_called()

    def test_uncertain_create_failure_is_not_retried(self):
        with mock.patch.object(publication, "api", side_effect=[None, None]), \
             mock.patch.object(publication, "gh", side_effect=publication.PublicationError("Unknown write result")) as gh:
            with self.assertRaises(publication.PublicationError):
                publication.publish(self.directory, REPO, COMMIT)
        self.assertEqual(gh.call_count, 1)
        self.assertEqual(gh.call_args.args[0][1], "create")

    def test_remote_download_is_hashed_not_accepted_by_name(self):
        local = publication.verify_local(self.directory)
        def download(args):
            folder = Path(args[args.index("--dir") + 1])
            (folder / publication.JAVA_NAME).write_bytes(b"different remote bytes")
        with mock.patch.object(publication, "gh", side_effect=download):
            with self.assertRaises(publication.PublicationError):
                publication.verify_remote(REPO, release(names={publication.JAVA_NAME}), local)

    def test_unexpected_remote_asset_name_is_rejected(self):
        with self.assertRaises(publication.PublicationError):
            publication.asset_names(release(names={"../private"}))


if __name__ == "__main__":
    unittest.main()
