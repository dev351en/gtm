#!/usr/bin/env sh
set -eu

# Run from an extracted repair payload, never from inside the target server.
GTM_PAYLOAD=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
GTM_INSTALLER="$GTM_PAYLOAD/install_runtime_repair.py"
if [ ! -f "$GTM_INSTALLER" ]; then
    GTM_INSTALLER="$GTM_PAYLOAD/tools/install_runtime_repair.py"
fi
if [ ! -f "$GTM_INSTALLER" ] || [ ! -f "$GTM_PAYLOAD/repair-manifest.json" ]; then
    printf '%s\n' 'Extract the complete GTM repair package before running Update-GTM.sh.' >&2
    exit 2
fi
if [ "$#" -lt 1 ]; then
    printf '%s\n' 'Stop the server and its launcher first.' \
        'Usage: ./Update-GTM.sh /path/to/existing/server [--bedrock]' \
        'Undo:  ./Update-GTM.sh /path/to/existing/server --rollback BACKUP_ID' >&2
    exit 2
fi
GTM_SERVER=$1
shift
if command -v python3 >/dev/null 2>&1; then
    GTM_PYTHON=python3
elif command -v python >/dev/null 2>&1; then
    GTM_PYTHON=python
else
    printf '%s\n' 'Python 3.10 or newer is required to run the verified updater.' >&2
    exit 2
fi
if ! "$GTM_PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    printf '%s\n' 'Python 3.10 or newer is required to run the verified updater.' >&2
    exit 2
fi
case "${1-}" in
    '')
        exec "$GTM_PYTHON" "$GTM_INSTALLER" apply --payload "$GTM_PAYLOAD" --server "$GTM_SERVER"
        ;;
    --bedrock)
        [ "$#" -eq 1 ] || { printf '%s\n' 'Unexpected updater arguments.' >&2; exit 2; }
        exec "$GTM_PYTHON" "$GTM_INSTALLER" apply --payload "$GTM_PAYLOAD" --server "$GTM_SERVER" --bedrock
        ;;
    --rollback)
        [ "$#" -eq 2 ] || { printf '%s\n' 'Provide the backup ID printed by the updater.' >&2; exit 2; }
        exec "$GTM_PYTHON" "$GTM_INSTALLER" rollback --server "$GTM_SERVER" --backup "$2"
        ;;
    *)
        printf '%s\n' 'Use --bedrock or --rollback BACKUP_ID; do not pass other flags.' >&2
        exit 2
        ;;
esac
