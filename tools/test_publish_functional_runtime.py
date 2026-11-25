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
    return {"id": 457688306, "tag_name": publication.TAG,
            "draft": draft, "prerelease": True, "target_commitish": COMMIT,
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
        with mock.patch.object(publication, "find_release", return_value=release()), \
             mock.patch.object(publication, "verify_remote") as verify, \
             mock.patch.object(publication, "gh") as gh, contextlib.redirect_stdout(io.StringIO()):
            publication.publish(self.directory, REPO, COMMIT)
        verify.assert_called_once()
        gh.assert_not_called()

    def test_existing_different_asset_is_not_overwritten(self):
        with mock.patch.object(publication, "find_release", return_value=release()), \
             mock.patch.object(publication, "verify_remote", side_effect=publication.PublicationError("Different bytes")), \
             mock.patch.object(publication, "gh") as gh:
            with self.assertRaises(publication.PublicationError):
                publication.publish(self.directory, REPO, COMMIT)
        gh.assert_not_called()

    def test_partial_public_release_is_not_silently_completed(self):
        with mock.patch.object(publication, "find_release", return_value=release(names={publication.JAVA_NAME})), \
             mock.patch.object(publication, "gh") as gh:
            with self.assertRaises(publication.PublicationError):
                publication.publish(self.directory, REPO, COMMIT)
        gh.assert_not_called()

    def test_new_release_is_draft_then_verified_then_prerelease(self):
        with mock.patch.object(publication, "find_release", side_effect=[None, release(True, set())]), \
             mock.patch.object(publication, "api", return_value=None), \
             mock.patch.object(publication, "read_release", side_effect=[release(True), release()]), \
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
        with mock.patch.object(publication, "find_release", return_value=release(True, existing)), \
             mock.patch.object(publication, "api", return_value={"object": {"type": "commit", "sha": COMMIT}}), \
             mock.patch.object(publication, "read_release", side_effect=[release(True), release()]), \
             mock.patch.object(publication, "verify_remote") as verify, \
             mock.patch.object(publication, "gh") as gh, contextlib.redirect_stdout(io.StringIO()):
            publication.publish(self.directory, REPO, COMMIT)
        calls = [call.args[0] for call in gh.call_args_list]
        self.assertEqual([args[1] for args in calls], ["upload", "edit"])
        self.assertNotIn(str((self.directory / publication.JAVA_NAME).resolve()), calls[0])
        self.assertEqual(verify.call_count, 2)

    def test_existing_tag_at_another_commit_is_never_moved(self):
        with mock.patch.object(publication, "find_release", return_value=None), \
             mock.patch.object(publication, "api", return_value={"object": {"type": "commit", "sha": "b" * 40}}), \
             mock.patch.object(publication, "gh") as gh:
            with self.assertRaises(publication.PublicationError):
                publication.publish(self.directory, REPO, COMMIT)
        gh.assert_not_called()

    def test_uncertain_create_failure_is_not_retried(self):
        with mock.patch.object(publication, "find_release", return_value=None), \
             mock.patch.object(publication, "api", return_value=None), \
             mock.patch.object(publication, "gh", side_effect=publication.PublicationError("Unknown write result")) as gh:
            with self.assertRaises(publication.PublicationError):
                publication.publish(self.directory, REPO, COMMIT)
        self.assertEqual(gh.call_count, 1)
        self.assertEqual(gh.call_args.args[0][1], "create")

    def test_remote_download_is_hashed_not_accepted_by_name(self):
        local = publication.verify_local(self.directory)
        def download(args, **kwargs):
            folder = Path(args[args.index("--dir") + 1])
            (folder / publication.JAVA_NAME).write_bytes(b"different remote bytes")
        with mock.patch.object(publication, "gh", side_effect=download):
            with self.assertRaises(publication.PublicationError):
                publication.verify_remote(REPO, release(names={publication.JAVA_NAME}), local)

    def test_unexpected_remote_asset_name_is_rejected(self):
        with self.assertRaises(publication.PublicationError):
            publication.asset_names(release(names={"../private"}))

    def test_pending_draft_with_rest_tag_404_resumes_same_release_id(self):
        """Reproduce the observed empty draft: its pending tag has no REST URL."""
        id_reads = []
        reads = []
        def respond(path, **kwargs):
            reads.append(path)
            if "/releases/tags/" in path:
                raise publication.PublicationError("Observed REST pending-tag HTTP 404")
            if path.endswith("releases?per_page=100&page=1"):
                return [release(True, set())]
            if path.endswith("git/ref/tags/" + publication.TAG):
                return None
            if path.endswith("releases/457688306"):
                id_reads.append(path)
                return [release(True, set()), release(True), release()][len(id_reads) - 1]
            self.fail("Unexpected endpoint: " + path)
        with mock.patch.object(publication, "api", side_effect=respond), \
             mock.patch.object(publication, "verify_remote"), \
             mock.patch.object(publication, "gh") as gh, contextlib.redirect_stdout(io.StringIO()):
            publication.publish(self.directory, REPO, COMMIT)
        self.assertEqual(len(id_reads), 3)
        self.assertFalse(any("/releases/tags/" in path for path in reads))
        self.assertEqual([call.args[0][1] for call in gh.call_args_list], ["upload", "edit"])
        self.assertTrue(all("create" not in call.args[0] and "delete" not in call.args[0] for call in gh.call_args_list))

    def test_draft_lookup_scans_collection_pages_and_reads_exact_id(self):
        first = [{"id": n + 1, "tag_name": "unrelated-" + str(n)} for n in range(100)]
        with mock.patch.object(publication, "api", side_effect=[first, [release(True)], release(True)]) as api:
            found = publication.find_release(REPO)
        self.assertEqual(found["id"], 457688306)
        paths = [call.args[0] for call in api.call_args_list]
        self.assertTrue(paths[0].endswith("page=1"))
        self.assertTrue(paths[1].endswith("page=2"))
        self.assertTrue(paths[2].endswith("releases/457688306"))

    def test_duplicate_pending_drafts_are_not_selected_or_recreated(self):
        duplicate = dict(release(True), id=457688307)
        with mock.patch.object(publication, "api", return_value=[release(True), duplicate]), \
             mock.patch.object(publication, "gh") as gh:
            with self.assertRaises(publication.PublicationError):
                publication.find_release(REPO)
        gh.assert_not_called()

    def test_id_readback_rejects_a_different_release_identity(self):
        with mock.patch.object(publication, "api", return_value=dict(release(True), id=1)):
            with self.assertRaises(publication.PublicationError):
                publication.read_release(REPO, 457688306)

    def test_stage_and_http_status_are_reported_without_raw_diagnostics(self):
        result = mock.Mock(returncode=1, stdout="", stderr="gh: opaque-unit-test-secret (HTTP 403)")
        with self.assertRaises(publication.PublicationError) as error:
            publication.gh(["api", "synthetic"], stage="Read draft after asset upload", runner=mock.Mock(return_value=result))
        self.assertIn("Read draft after asset upload", str(error.exception))
        self.assertIn("HTTP 403", str(error.exception))
        self.assertNotIn("opaque-unit-test-secret", str(error.exception))

    def test_only_explicit_missing_read_accepts_http_404(self):
        result = mock.Mock(returncode=1, stdout="", stderr="gh: Not Found (HTTP 404)")
        runner = mock.Mock(return_value=result)
        self.assertIsNone(publication.gh(["api", "synthetic"], allow_missing=True, runner=runner))
        with self.assertRaises(publication.PublicationError) as error:
            publication.gh(["api", "synthetic"], stage="Confirm draft by ID", runner=runner)
        self.assertIn("HTTP 404", str(error.exception))


if __name__ == "__main__":
    unittest.main()
