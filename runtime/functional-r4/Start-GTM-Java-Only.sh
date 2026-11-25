#!/usr/bin/env sh
set -eu
gtm_script_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec sh "$gtm_script_dir/Start-GTM.sh" --java-only "$@"
