#!/usr/bin/env sh
set -eu
cd -- "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if [ -x "runtime/java/bin/java" ]; then
  gtm_java="$(pwd)/runtime/java/bin/java"
elif [ -n "${JAVA_HOME:-}" ] && [ -x "$JAVA_HOME/bin/java" ]; then
  gtm_java="$JAVA_HOME/bin/java"
else
  gtm_java="java"
fi
exec "$gtm_java" --add-modules jdk.httpserver -jar launcher/gtm-launcher.jar "$@"
