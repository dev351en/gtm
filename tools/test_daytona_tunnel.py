"""Offline connector regressions: no credentials, external network, or Daytona access."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
from urllib.error import HTTPError

import daytona_tunnel as tunnel


KEY = "unit-test-key-never-a-credential"
TOKEN = "unit-test-token-never-a-session"
SETTINGS = {"key": KEY, "sandbox": tunnel.DEFAULT_SANDBOX}


def packet(payload):
    return tunnel.encode_varint(len(payload)) + payload


def status_payload(version="26.3"):
    data = json.dumps({"version": {"name": version, "protocol": 999},
                       "players": {"online": 1, "max": 4},
                       "description": "Synthetic offline test"}).encode()
    return b"\x00" + tunnel.encode_varint(len(data)) + data


class FakeClock:
    def __init__(self):
        self.value = 0.0

    def now(self):
        return self.value

    def sleep(self, amount):
        self.value += amount


class FakeSsh:
    def __init__(self, poll_results=None, forwarding_results=None):
        self.poll_results = list(poll_results or [None])
        self.forwarding_results = list(forwarding_results or [True])
        self.closed = 0

    def poll(self):
        if len(self.poll_results) > 1:
            return self.poll_results.pop(0)
        return self.poll_results[0]

    def failure(self):
        return tunnel.ConnectionFailure("Synthetic SSH failure")

    def forwarding_ready(self):
        if len(self.forwarding_results) > 1:
            return self.forwarding_results.pop(0)
        return self.forwarding_results[0]

    def close(self):
        self.closed += 1


class FakeSocket:
    def __init__(self, payload):
        self.payload = io.BytesIO(payload)
        self.sent = []
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def settimeout(self, timeout):
        self.timeout = timeout

    def recv(self, count):
        return self.payload.read(min(count, 3))  # Exercise fragmented reads.

    def sendall(self, data):
        self.sent.append(data)


class FakeResponse:
    def __init__(self, data):
        self.data = data if isinstance(data, bytes) else json.dumps(data).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self, count):
        return self.data[:count]


class FakeOpener:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return FakeResponse(result)


class SettingsTests(unittest.TestCase):
    def test_environment_works_without_secret_file(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assertEqual(tunnel.load_settings(Path(folder), {"DAYTONA_API_KEY": KEY}), SETTINGS)

    def test_local_file_quotes_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / ".secrets.env").write_text('DAYTONA_API_KEY="ignored-secret-key"\nOTHER=value\n', encoding="utf-8")
            self.assertEqual(tunnel.load_settings(root, {"DAYTONA_API_KEY": KEY}), SETTINGS)
            self.assertEqual(tunnel.load_settings(root, {})["key"], "ignored-secret-key")

    def test_missing_key_does_not_read_generic_dotenv(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / ".env").write_text("DAYTONA_API_KEY=" + KEY)
            with self.assertRaises(tunnel.ConnectionFailure):
                tunnel.load_settings(root, {})

    def test_invalid_secret_is_not_echoed(self):
        with tempfile.TemporaryDirectory() as folder:
            secret = KEY + "\r\nAuthorization: injected"
            with self.assertRaises(tunnel.ConnectionFailure) as error:
                tunnel.load_settings(Path(folder), {"DAYTONA_API_KEY": secret})
            self.assertNotIn(KEY, str(error.exception))

    def test_bad_sandbox_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(tunnel.ConnectionFailure):
                tunnel.load_settings(Path(folder), {"DAYTONA_API_KEY": KEY, "DAYTONA_SANDBOX_ID": "../other"})

    def test_oversized_secret_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / ".secrets.env").write_bytes(b"x" * 65537)
            with self.assertRaises(tunnel.ConnectionFailure):
                tunnel.load_settings(root, {"DAYTONA_API_KEY": KEY})


class ApiScopeTests(unittest.TestCase):
    def test_only_expected_get_create_and_exact_revoke_are_requested(self):
        opener = FakeOpener({"id": tunnel.DEFAULT_SANDBOX, "state": "started"}, {"token": TOKEN}, b"")
        api = tunnel.DaytonaAccess(SETTINGS, opener)
        api.require_running()
        self.assertEqual(api.create_token(), TOKEN)
        api.revoke_token(TOKEN)
        base = tunnel.API_ROOT + "/sandbox/" + tunnel.DEFAULT_SANDBOX
        self.assertEqual([(r.get_method(), r.full_url) for r in opener.requests], [
            ("GET", base), ("POST", base + "/ssh-access?expiresInMinutes=60"),
            ("DELETE", base + "/ssh-access?token=" + TOKEN)])
        self.assertTrue(all(r.get_header("Authorization") == "Bearer " + KEY for r in opener.requests))

    def test_stopped_sandbox_does_not_create_access(self):
        opener = FakeOpener({"id": tunnel.DEFAULT_SANDBOX, "state": "stopped"})
        with self.assertRaises(tunnel.ConnectionFailure):
            tunnel.DaytonaAccess(SETTINGS, opener).require_running()
        self.assertEqual(len(opener.requests), 1)

    def test_wrong_sandbox_response_is_rejected(self):
        opener = FakeOpener({"id": "different-id", "state": "started"})
        with self.assertRaises(tunnel.ConnectionFailure):
            tunnel.DaytonaAccess(SETTINGS, opener).require_running()

    def test_invalid_token_is_rejected(self):
        opener = FakeOpener({"token": "token\nProxyCommand=bad"})
        with self.assertRaises(tunnel.ConnectionFailure):
            tunnel.DaytonaAccess(SETTINGS, opener).create_token()

    def test_api_error_has_no_secret_response_or_url(self):
        failure = HTTPError("https://invalid/" + KEY, 403, TOKEN, {}, None)
        with self.assertRaises(tunnel.ConnectionFailure) as error:
            tunnel.DaytonaAccess(SETTINGS, FakeOpener(failure)).require_running()
        message = str(error.exception)
        self.assertIn("403", message)
        self.assertNotIn(KEY, message)
        self.assertNotIn(TOKEN, message)

    def test_redirects_are_refused(self):
        handler = tunnel.NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "", {}, "https://different.invalid"))

    def test_oversized_or_nonobject_response_is_rejected(self):
        for response in (b"x" * (tunnel.MAX_RESPONSE + 1), [], b"not JSON"):
            with self.subTest(kind=type(response).__name__):
                with self.assertRaises(tunnel.ConnectionFailure):
                    tunnel.DaytonaAccess(SETTINGS, FakeOpener(response)).require_running()


class ProtocolTests(unittest.TestCase):
    def test_status_and_nonce_ping_over_fragmented_stream(self):
        nonce = b"12345678"
        sock = FakeSocket(packet(status_payload()) + packet(b"\x01" + nonce))
        connect = mock.Mock(return_value=sock)
        result = tunnel.minecraft_status(connector=connect, nonce_factory=lambda _: nonce)
        self.assertEqual(result, {"version": "26.3", "protocol": 999})
        connect.assert_called_once_with(("127.0.0.1", 25565), timeout=2.0)
        self.assertTrue(sock.sent[0].endswith(b"\x01\x00"))
        self.assertEqual(sock.sent[1], b"\x09\x01" + nonce)
        self.assertTrue(sock.closed)

    def test_wrong_ping_nonce_cannot_report_ready(self):
        sock = FakeSocket(packet(status_payload()) + packet(b"\x01different"))
        with self.assertRaises(ValueError):
            tunnel.minecraft_status(connector=lambda *a, **k: sock, nonce_factory=lambda _: b"12345678")

    def test_non_minecraft_status_is_rejected(self):
        for content in (b"\x01{}", b"\x00\x02{}", b"\x00\x02{}extra", b"\x00\x10{}"):
            with self.subTest(content=content):
                with self.assertRaises((ValueError, UnicodeError)):
                    tunnel.decode_status(content)

    def test_control_characters_are_not_exposed_in_version(self):
        result = tunnel.decode_status(status_payload("26.3\n\x1b[31m"))
        self.assertNotIn("\n", result["version"])
        self.assertNotIn("\x1b", result["version"])

    def test_frame_limit_is_enforced_before_reading_body(self):
        sock = FakeSocket(tunnel.encode_varint(tunnel.MAX_STATUS + 17))
        with self.assertRaises(ValueError):
            tunnel.minecraft_status(connector=lambda *a, **k: sock)

    def test_truncated_and_overlong_varints_fail(self):
        for value in (b"", b"\x80", b"\x80\x80\x80\x80\x80\x00"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    tunnel.read_varint(io.BytesIO(value).read)

    def test_global_status_deadline_is_enforced(self):
        clock = FakeClock()
        sock = FakeSocket(packet(status_payload()))
        def connect(*args, **kwargs):
            clock.value = 3
            return sock
        with self.assertRaises(TimeoutError):
            tunnel.minecraft_status(timeout=2, connector=connect, clock=clock.now)


class ReadinessTests(unittest.TestCase):
    def test_port_race_cannot_probe_a_different_local_minecraft(self):
        clock = FakeClock()
        probe = mock.Mock(return_value={"version": "unrelated local server"})
        ssh = FakeSsh([None, None, 255], [False])
        with self.assertRaises(tunnel.ConnectionFailure):
            tunnel.wait_for_game(ssh, probe=probe, clock=clock.now, sleep=clock.sleep)
        probe.assert_not_called()

    def test_probe_waits_for_ssh_forwarding_establishment(self):
        clock = FakeClock()
        probe = mock.Mock(return_value={"version": "26.3"})
        ssh = FakeSsh(forwarding_results=[False, False, True])
        status = tunnel.wait_for_game(ssh, probe=probe, clock=clock.now, sleep=clock.sleep)
        self.assertEqual(status["version"], "26.3")
        self.assertGreaterEqual(clock.value, 0.2)
        probe.assert_called_once()

    def test_no_ready_before_valid_game_response(self):
        clock = FakeClock()
        probe = mock.Mock(side_effect=[ConnectionRefusedError(), {"version": "26.3"}])
        status = tunnel.wait_for_game(FakeSsh(), probe=probe, clock=clock.now, sleep=clock.sleep)
        self.assertEqual(status["version"], "26.3")
        self.assertEqual(probe.call_count, 2)

    def test_dead_ssh_prevents_game_probe(self):
        probe = mock.Mock()
        with self.assertRaises(tunnel.ConnectionFailure):
            tunnel.wait_for_game(FakeSsh([255]), probe=probe)
        probe.assert_not_called()

    def test_ssh_exit_during_probe_is_not_ready(self):
        clock = FakeClock()
        with self.assertRaises(tunnel.ConnectionFailure):
            tunnel.wait_for_game(FakeSsh([None, 255]), probe=lambda **k: {"version": "26.3"},
                                 clock=clock.now, sleep=clock.sleep)

    def test_readiness_timeout_does_not_restart_anything(self):
        clock = FakeClock()
        probe = mock.Mock(side_effect=OSError("Synthetic unavailable server"))
        with self.assertRaises(tunnel.ConnectionFailure):
            tunnel.wait_for_game(FakeSsh(), timeout=1, probe=probe, clock=clock.now, sleep=clock.sleep)
        self.assertGreaterEqual(clock.value, 1)

    def test_repeated_game_failure_closes_monitor(self):
        clock = FakeClock()
        probe = mock.Mock(side_effect=OSError("Synthetic unavailable server"))
        with self.assertRaises(tunnel.ConnectionFailure):
            tunnel.monitor_game(FakeSsh(), probe=probe, clock=clock.now, sleep=clock.sleep)
        self.assertEqual(probe.call_count, 3)

    def test_lost_ssh_exits_monitor_without_false_success(self):
        probe = mock.Mock()
        with self.assertRaises(tunnel.ConnectionFailure):
            tunnel.monitor_game(FakeSsh([0]), probe=probe)
        probe.assert_not_called()


class LifetimeTests(unittest.TestCase):
    def test_listener_attempt_before_failed_bind_is_not_established(self):
        process = mock.Mock()
        process.stderr = io.BytesIO(
            b"debug1: Local forwarding listening on 127.0.0.1 port 25565.\r\n"
            b"bind [127.0.0.1]:25565: Address already in use\r\n"
            b"Could not request local forwarding.\r\n")
        process.poll.return_value = 255
        owned = tunnel.OwnedSshProcess(["ssh", "synthetic"], popen=mock.Mock(return_value=process))
        owned._reader.join(timeout=1)
        self.assertFalse(owned.forwarding_ready())
        owned.close()

    def test_completed_session_after_listener_is_established(self):
        process = mock.Mock()
        process.stderr = io.BytesIO(
            b"debug1: Local forwarding listening on 127.0.0.1 port 25565.\r\n"
            b"debug1: channel 0: new [port listener]\r\n"
            b"debug1: Entering interactive session.\r\n")
        process.poll.return_value = None
        owned = tunnel.OwnedSshProcess(["ssh", "synthetic"], popen=mock.Mock(return_value=process))
        owned._reader.join(timeout=1)
        self.assertTrue(owned.forwarding_ready())
        owned.close()

    def patches(self, api, ssh, wait=None, monitor=None):
        stack = contextlib.ExitStack()
        stack.enter_context(mock.patch.object(tunnel, "require_ssh", return_value="ssh"))
        stack.enter_context(mock.patch.object(tunnel, "require_free_port"))
        stack.enter_context(mock.patch.object(tunnel, "DaytonaAccess", return_value=api))
        stack.enter_context(mock.patch.object(tunnel, "OwnedSshProcess", return_value=ssh))
        stack.enter_context(mock.patch.object(tunnel, "wait_for_game", side_effect=wait, return_value={"version": "26.3"}))
        stack.enter_context(mock.patch.object(tunnel, "monitor_game", side_effect=monitor))
        return stack

    def test_failed_readiness_cleans_only_owned_process_and_token(self):
        api = mock.Mock()
        api.create_token.return_value = TOKEN
        ssh = FakeSsh()
        output = io.StringIO()
        with self.patches(api, ssh, wait=tunnel.ConnectionFailure("Synthetic startup failure")), contextlib.redirect_stdout(output):
            with self.assertRaises(tunnel.ConnectionFailure):
                tunnel.run_connection(SETTINGS)
        self.assertEqual(ssh.closed, 1)
        api.revoke_token.assert_called_once_with(TOKEN)
        self.assertNotIn("READY:", output.getvalue())
        self.assertNotIn(TOKEN, output.getvalue())

    def test_ctrl_c_cleans_owned_process_and_token(self):
        api = mock.Mock()
        api.create_token.return_value = TOKEN
        ssh = FakeSsh()
        with self.patches(api, ssh, monitor=KeyboardInterrupt()), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(KeyboardInterrupt):
                tunnel.run_connection(SETTINGS)
        self.assertEqual(ssh.closed, 1)
        api.revoke_token.assert_called_once_with(TOKEN)

    def test_check_mode_makes_no_api_or_ssh_session(self):
        api, ssh = mock.Mock(), FakeSsh()
        with self.patches(api, ssh), contextlib.redirect_stdout(io.StringIO()):
            tunnel.run_connection(SETTINGS, check_only=True)
        api.require_running.assert_not_called()
        api.create_token.assert_not_called()
        self.assertEqual(ssh.closed, 0)

    def test_access_creation_failure_does_not_revoke_other_sessions(self):
        api = mock.Mock()
        api.create_token.side_effect = tunnel.ConnectionFailure("Synthetic creation failure")
        with self.patches(api, FakeSsh()), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(tunnel.ConnectionFailure):
                tunnel.run_connection(SETTINGS)
        api.revoke_token.assert_not_called()

    def test_spawn_failure_still_revokes_only_created_token(self):
        api = mock.Mock()
        api.create_token.return_value = TOKEN
        with self.patches(api, FakeSsh()), mock.patch.object(tunnel, "OwnedSshProcess", side_effect=tunnel.ConnectionFailure("Synthetic spawn failure")), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(tunnel.ConnectionFailure):
                tunnel.run_connection(SETTINGS)
        api.revoke_token.assert_called_once_with(TOKEN)

    def test_secure_loopback_ssh_arguments(self):
        command = tunnel.ssh_command("ssh", TOKEN)
        self.assertIn("127.0.0.1:25565:127.0.0.1:25565", command)
        self.assertIn("ExitOnForwardFailure=yes", command)
        self.assertIn("StrictHostKeyChecking=accept-new", command)
        self.assertNotIn("StrictHostKeyChecking=no", command)
        self.assertEqual(command[-3:], ["-l", TOKEN, "ssh.app.daytona.io"])
        self.assertIn("-N", command)
        self.assertNotIn(KEY, command)

    def test_owned_process_uses_no_shell_and_terminates_only_itself(self):
        process = mock.Mock()
        process.stderr = io.BytesIO(b"")
        process.poll.return_value = None
        popen = mock.Mock(return_value=process)
        owned = tunnel.OwnedSshProcess(["ssh", "synthetic"], popen=popen)
        owned.close()
        self.assertFalse(popen.call_args.kwargs["shell"])
        process.terminate.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=3)
        process.kill.assert_not_called()

    def test_only_owned_process_is_killed_if_graceful_exit_times_out(self):
        process = mock.Mock()
        process.stderr = io.BytesIO(b"")
        process.poll.return_value = None
        process.wait.side_effect = [subprocess.TimeoutExpired("synthetic", 3), 0]
        owned = tunnel.OwnedSshProcess(["ssh", "synthetic"], popen=mock.Mock(return_value=process))
        owned.close()
        process.terminate.assert_called_once_with()
        process.kill.assert_called_once_with()

    def test_token_bearing_ssh_error_is_not_echoed(self):
        process = mock.Mock()
        process.stderr = io.BytesIO((TOKEN + "@ssh.app.daytona.io: Host key verification failed.").encode())
        process.poll.return_value = 255
        owned = tunnel.OwnedSshProcess(["ssh", "synthetic"], popen=mock.Mock(return_value=process))
        failure = str(owned.failure())
        owned.close()
        self.assertIn("host-key", failure)
        self.assertNotIn(TOKEN, failure)


if __name__ == "__main__":
    unittest.main()
