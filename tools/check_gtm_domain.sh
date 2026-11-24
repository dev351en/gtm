#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../source"
out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT
javac -encoding UTF-8 -d "$out" src/main/java/com/sdcraft/core/gtm/*.java src/test/java/com/sdcraft/core/gtm/{FoundationChecks,CivicChecks,InfrastructureChecks,NearMissChecks}.java
for suite in FoundationChecks CivicChecks InfrastructureChecks NearMissChecks; do
  java -cp "$out" "com.sdcraft.core.gtm.$suite"
done
