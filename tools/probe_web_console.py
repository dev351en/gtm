#!/usr/bin/env python3
"""Bounded HTTP checks against an explicitly started local Paper staging server.

Reads the console token from that server's private file and never writes it into
the report or stdout. The only executed game command is the read-only `list`.
Lifecycle, credential and malformed command requests must be rejected.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import http.client
import json
from pathlib import Path
import sys


def probe(server_root: Path, port: int) -> dict:
    token = (server_root / "plugins/SDCraftCore/console-access.token").read_text(encoding="utf-8").strip()
    if len(token) < 32:
        raise ValueError("No valid local staging console token")
    cases: list[dict] = []
    observed = {}

    def request(method: str, path: str, *, payload=None, raw: bytes | None = None,
                auth=True, headers=None):
        values = {"Host": f"127.0.0.1:{port}"}
        if auth:
            values["Authorization"] = f"Bearer {token}"
        if payload is not None:
            raw = json.dumps(payload).encode("utf-8")
            values["Content-Type"] = "application/json"
        if headers:
            values.update(headers)
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=8)
        try:
            connection.request(method, path, body=raw, headers=values)
            response = connection.getresponse()
            data = response.read(131073)
            if len(data) > 131072:
                raise ValueError("Console response exceeded bounded probe size")
            if token.encode() in data:
                raise AssertionError("Console response exposed the access token")
            response_headers = {k.lower(): v for k, v in response.getheaders()}
            decoded = json.loads(data) if response_headers.get("content-type", "").startswith("application/json") else data.decode("utf-8")
            return response.status, response_headers, decoded
        finally:
            connection.close()

    def check(name: str, status: int, method="GET", path="/api/status", *, predicate=None, **kwargs):
        record = {"name": name, "expected_status": status}
        try:
            actual, headers, data = request(method, path, **kwargs)
            record["actual_status"] = actual
            record["passed"] = actual == status and (predicate(headers, data) if predicate else True)
        except Exception as failure:
            record["passed"] = False
            record["failure_type"] = type(failure).__name__
            data = None
        cases.append(record)
        return data

    check("Static dashboard served with local security headers", 200, path="/", auth=False,
          predicate=lambda h, d: "GTM" in d and h.get("cache-control") == "no-store"
          and h.get("x-frame-options") == "DENY" and "frame-ancestors 'none'" in h.get("content-security-policy", "")
          and h.get("referrer-policy") == "no-referrer")
    check("Dashboard JavaScript served", 200, path="/console.js", auth=False,
          predicate=lambda h, d: "text/javascript" in h.get("content-type", "") and "api/command" in d)
    check("Dashboard CSS served", 200, path="/console.css", auth=False,
          predicate=lambda h, d: "text/css" in h.get("content-type", ""))
    check("Missing API bearer rejected", 401, auth=False)
    check("Incorrect API bearer rejected", 401, headers={"Authorization": "Bearer invalid-local-test-token"})
    check("Foreign Host rejected", 403, headers={"Host": "console.invalid:8765"})
    check("Foreign Origin rejected", 403, headers={"Origin": "https://console.invalid"})
    check("Sandboxed null Origin rejected", 403, headers={"Origin": "null"})
    status = check("Authenticated live Paper snapshot", 200,
                   predicate=lambda h, d: d.get("ready") is True and isinstance(d.get("players"), list)
                   and isinstance(d.get("worlds"), list) and isinstance(d.get("plugins"), list)
                   and isinstance(d.get("tps"), (float, int)))
    if isinstance(status, dict) and status.get("ready"):
        observed = {key: status.get(key) for key in ("version", "minecraft", "tps", "mspt")}
        observed["player_count"] = len(status.get("players", []))
    check("Authenticated bounded server log", 200, path="/api/logs",
          predicate=lambda h, d: isinstance(d.get("lines"), list) and len(d["lines"]) <= 120)
    for name, payload, expected in [
        ("Multiline command rejected", {"command": "list\nstop"}, 400),
        ("Lifecycle command requires explicit confirmation", {"command": "stop"}, 409),
        ("Wrapped lifecycle command requires confirmation", {"command": "execute run minecraft:stop"}, 409),
        ("Credential command rejected", {"command": "login probe-secret"}, 400),
        ("Null command is a client error", {"command": None}, 400),
        ("Array command is a client error", {"command": []}, 400),
        ("Non-boolean confirmation rejected", {"command": "list", "confirmed": "true"}, 400),
    ]:
        check(name, expected, "POST", "/api/command", payload=payload)
    check("Malformed JSON is a client error", 400, "POST", "/api/command", raw=b"{broken",
          headers={"Content-Type": "application/json"})
    check("Incorrect media type rejected", 400, "POST", "/api/command", raw=b'{"command":"list"}',
          headers={"Content-Type": "application/json-invalid"})
    check("Oversized request rejected", 400, "POST", "/api/command", payload={"command": "x" * 9000})
    check("Local guide answers without inventing a persistent weapon queue", 200, "POST", "/api/guide",
          payload={"question": "Where are my guns?"},
          predicate=lambda h, d: d.get("mode") == "local" and "/gun" in d.get("answer", "")
          and "persistent delivery queue" not in d.get("answer", ""))
    command = check("Real Paper console executes read-only list", 200, "POST", "/api/command",
                    payload={"command": "list", "confirmed": False},
                    predicate=lambda h, d: d.get("accepted") is True and d.get("running") is False and bool(d.get("requestId")))
    audit_record = {"name": "Command has matching START and RESULT audit entries", "passed": False}
    if isinstance(command, dict) and command.get("requestId"):
        audit_path = server_root / "plugins/SDCraftCore/console-audit.log"
        if audit_path.is_file():
            records = [line.split("\t") for line in audit_path.read_text(encoding="utf-8").splitlines()
                       if "\t" + command["requestId"] + "\t" in line]
            audit_record["passed"] = len(records) == 2 and [r[3] for r in records] == ["START", "RESULT"]
    cases.append(audit_record)
    return {"schema": "GTM_REPAIR_CONSOLE_HTTP_PROBE_V1", "at": datetime.now(timezone.utc).isoformat(),
            "scope": "Actual loopback HTTP server and read-only Paper console command; no native client or Daytona deployment claim.",
            "observed": observed, "passed": all(case["passed"] for case in cases),
            "checks": cases, "passed_count": sum(case["passed"] for case in cases), "total_count": len(cases)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be 1024..65535")
    report = probe(args.server.resolve(), args.port)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Console HTTP probe: {report['passed_count']}/{report['total_count']} passed; token omitted from report.")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
