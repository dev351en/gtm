#!/usr/bin/env python3
"""Read-only Daytona connectivity/resource inspection. Never creates or modifies sandboxes."""
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, HTTPRedirectHandler, build_opener

BASE = 'https://app.daytona.io/api'
MAX_RESPONSE = 1024 * 1024
STATES = {'started', 'stopped', 'archived', 'paused', 'starting', 'stopping', 'creating', 'error', 'destroyed', 'build_failed', 'pending_build', 'pulling_snapshot', 'building_snapshot'}
QUOTA_FIELDS = {'cpu','memory','disk','maxCpu','maxMemory','maxDisk','usedCpu','usedMemory','usedDisk','cpuLimit','memoryLimit','diskLimit','maxCpuPerSandbox','maxMemoryPerSandbox','maxDiskPerSandbox','cpuUsage','memoryUsage','diskUsage','totalCpu','totalMemory','totalDisk','cpuQuota','memoryQuota','diskQuota','reservedCpu','reservedMemory','reservedDisk'}

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def token_id(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', value):
        raise ValueError('Invalid or missing sandbox/organization identifier')
    return quote(value, safe='')

def get_json(path, key):
    request = Request(BASE + path, headers={'Authorization': 'Bearer ' + key, 'Accept': 'application/json'}, method='GET')
    with build_opener(NoRedirect()).open(request, timeout=12) as response:
        payload = response.read(MAX_RESPONSE + 1)
    if len(payload) > MAX_RESPONSE:
        raise ValueError('Response exceeds diagnostic limit')
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError('Unexpected API response schema')
    return data

def safe_sandbox(data):
    result = {k: data[k] for k in ('cpu','memory','disk') if type(data.get(k)) is int and data[k] >= 0}
    state = data.get('state')
    result['state'] = state if isinstance(state, str) and state.lower() in STATES else 'unrecognized'
    return result

def safe_usage(data):
    # Unknown schemas deliberately produce no computed quota or spending decision.
    rows = data.get('regionUsage')
    if not isinstance(rows, list):
        return []
    return [{k: v for k, v in row.items() if k in QUOTA_FIELDS and type(v) in (int, float) and 0 <= v < 10**12}
            for row in rows[:64] if isinstance(row, dict)]

def inspect(key, sandbox_id, organization_id=None, getter=get_json):
    if not key or '\r' in key or '\n' in key:
        raise ValueError('Missing or invalid credential')
    sandbox = getter('/sandbox/' + token_id(sandbox_id), key)
    org = organization_id or sandbox.get('organizationId')
    report = {'game_sandbox': safe_sandbox(sandbox), 'billing_verified': False, 'provisioning_allowed': False,
              'note': 'Read-only metadata. Verify wallet, expiry, actual disk use and backup before provisioning or deployment.'}
    if org:
        report['quota_fields'] = safe_usage(getter('/organizations/' + token_id(org) + '/usage', key))
    else:
        report['quota_fields'] = []
        report['quota_note'] = 'Organization identifier unavailable.'
    return report

def main():
    try:
        print(json.dumps(inspect(os.environ.get('DAYTONA_API_KEY',''), os.environ.get('GTM_GAME_SANDBOX_ID',''),
                                 os.environ.get('DAYTONA_ORGANIZATION_ID')), indent=2, allow_nan=False))
        return 0
    except HTTPError as exc:
        print(f'Daytona read-only inspection failed: HTTP {exc.code}.', file=sys.stderr)
    except (URLError, TimeoutError, ValueError, OSError) as exc:
        print(f'Daytona read-only inspection failed: {type(exc).__name__}.', file=sys.stderr)
    return 1

if __name__ == '__main__':
    sys.exit(main())
