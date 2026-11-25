# Laptop Bedrock NetherNet connection correction

## Observed blocker and corrected startup

The pinned Geyser **2.12.1 build 1308** emitted a concrete warning when the laptop candidate used `bedrock.address: 127.0.0.1`: NetherNet cannot establish gameplay on a loopback bind, including for a client on that same machine. The old template also advertised `127.0.0.1:19132`. A Java server reaching its `Done` message did not establish a working Bedrock connection.

The launcher now selects one **current local RFC1918 IPv4 address** and supplies the supported `-DgeyserUdpAddress` override before Paper starts. It checks TCP signaling and UDP gameplay on that exact address and passes matching explicit port overrides to Geyser. Transport is `nethernet`, signaling is `builtin`, `advertise-addresses` is empty, and STUN discovery remains false. In the exact pinned implementation, that combination advertises the specific effective bind address. Java and pack HTTP remain on `127.0.0.1`.

This is a connection-path correction. Offline launcher/socket fixtures and pinned implementation inspection establish the configuration behavior; they do not establish a native Windows or Bedrock client session. Actual server startup and actual client acceptance must be recorded separately in the release evidence.

## How the laptop selects its address

`launcher/launcher.properties` contains `bedrock.bind=auto`. Selection happens on the laptop at launch, never during ZIP assembly:

1. Enumerate IPv4 addresses assigned to local network interfaces and retain only up, non-loopback interfaces with addresses in `10.0.0.0/8`, `172.16.0.0/12` or `192.168.0.0/16`.
2. Ask the OS for the source address it would route toward a numeric TEST-NET-1 destination using a UDP channel `connect`, then close it. There is no DNS lookup and no `send` or `write`; no application datagram is transmitted. Select that address only if it is in the eligible local set.
3. If the route is unavailable or ineligible, use the sole eligible address. If none or several remain, stop with instructions rather than guessing an interface.
4. An explicit `bedrock.bind=<IPv4>` takes precedence but must match an eligible address currently assigned to the laptop. It cannot be a hostname, wildcard, public IP, loopback, link-local address, CGNAT address or stale address from another machine.

For multiple Wi-Fi, Ethernet or VPN adapters, set the property to the actual private IPv4 of the adapter intended for play and run `Start-GTM.bat --check` again. The OS route preference can select a VPN interface; the explicit property is the supported way to choose a different current private adapter. No build-machine address is embedded in the bundle.

`--check` reports the chosen IPv4, interface name and port after both TCP and UDP bind checks succeed. These checks release their temporary sockets immediately. Another process or an adapter change can still take the address or port between preflight and Geyser startup; the launcher does not claim that a preflight check is a successful client connection. After Paper starts, it prints the configured Bedrock address with an instruction to check Geyser's own startup result.

## Java-only and inactive profiles

If no suitable private adapter exists, double-click `Start-GTM-Java-Only.bat` or run `sh Start-GTM-Java-Only.sh` for Java play. Both wrappers use the normal launcher with `--java-only` and forward any additional arguments. The launcher temporarily preserves the two exact reviewed Geyser/Floodgate JARs outside Paper's plugin scan, before any optional bootstrap can initialize, and restores the byte-identical originals after shutdown. It prints that selection and does not print a Bedrock join address. `--java-only` can be combined with `--check`, which inspects without moving files, and does not accept the EULA; neither wrapper silently supplies acceptance. The regular scripts accept the same flag directly.

Setting `bedrock.enabled=false`, or omitting an enabled Bedrock profile, selects the same reversible plugin exclusion. The child retains `-DgeyserUdpPort=-1` only as additional protection. The exact build1308 bytecode performs Minecraft discovery and starts its asset-cache work before reaching that port check; the property alone is therefore insufficient to prevent bootstrap work. The [Java-only guide](LAUNCHER_JAVA_ONLY_R4.md) records the pinned methods, stopped-world recovery journal and offline fixtures. Plugin settings, saved authentication and identity keys are preserved.

The portable Geyser YAML retains `127.0.0.1` as an **inert fallback**, with a comment that the launcher must override it. This prevents a manual bypass from silently changing the server to an all-interface listener. NetherNet is not playable using that fallback. Always use `Start-GTM`; direct `java -jar paper...` bypasses the required runtime selection. The launcher never starts Geyser on `0.0.0.0` and does not suppress its warning.

## Effective configuration and identity

| Component | Effective address or setting |
|---|---|
| Java Paper | `127.0.0.1`, configured Java TCP port |
| Resource-pack HTTP | `127.0.0.1`, separate pack TCP port; both bind and client host are checked |
| Bedrock builtin signaling | Selected local private IPv4, TCP 19132 by default |
| Bedrock NetherNet gameplay | Same selected IPv4, UDP 19132 by default |
| Advertised Bedrock address | Pinned Geyser derives the specific effective bind; no hardcoded advertised host |
| STUN | Disabled |
| Bedrock authentication | Existing Floodgate configuration and signed Bedrock-login validation retained |
| Java identity policy | Existing `online-mode`, core authentication and player UUID policy retained |
| No validated Bedrock endpoint | The reviewed optional Geyser/Floodgate JARs are excluded before Paper's plugin scan and restored after shutdown |

The listener is reachable on that selected private network, subject to the laptop firewall. The launcher does not open firewall rules, create public forwarding, change router settings, start a tunnel or alter account/session files. It does not require a paid service. Bedrock's builtin HTTP signaling uses the game's first-join server-identity confirmation; review the expected local server prompt normally. Existing Geyser identity material and Floodgate keys are not regenerated or replaced by this correction.

The builder validates the reviewed networking fields, Floodgate auth type and `validate-bedrock-login: true`. A private imported configuration with different or ambiguous fields is rejected for review in a separate copy. The builder does not rewrite that imported source. Duplicate mapping keys cannot make the preflight read one value while Geyser applies another.

## Evidence and tests

The launcher is compiled directly with Java 25 and tested independently of the core Gradle cache. `tools/test_laptop_bundle.py` includes pure address/route/interface policy cases, the actual host's private-interface TCP and UDP conflict checks, child-process JVM-argument assertions, unchanged YAML/identity settings, a portable crossplay-build fixture, explicit disabled and Java-only behavior, and loopback-only pack service checks. The 25 November run executed **35 cases: 32 passed, three skipped, zero failures or errors**. The test host exposed no eligible private IPv4, so the three actual-private-interface cases were explicitly skipped; the pure policy cases and actual Java-only child process checks passed. The shell wrapper ran successfully from a bundle path containing spaces, forwarded `--check` without accepting the EULA, and launched/stopped the fixture process with Geyser explicitly disabled. The exact executed result is retained in `reports/LAPTOP_NETHERNET_FIXTURES_R4.log`, with its limits in `reports/LAPTOP_NETHERNET_VALIDATION_R4.json`.

The child process used by those historical network fixtures is labeled `FixtureServer`. It prints JVM properties and exercises launcher process/HTTP/clean-stop behavior; it is not Paper, Geyser or a game client. Its earlier `-1` assertion establishes the child argument, not absence of Geyser bootstrap. The later reversible exclusion has its own [18-case filesystem/process evidence](reports/LAUNCHER_JAVA_ONLY_R4.json); the new full-launcher optional-JAR child fixture remains separately reported. No native-client result is inferred. Pinned-JAR bytecode excerpts are retained in `reports/GEYSER_NETHERNET_PINNED_BYTECODE_R4.txt`, including the exact JAR SHA-256 and the methods that choose the bind, advertised address and ports.

Primary references consulted on 25 November 2026:

- [Geyser's NetherNet migration explanation](https://geysermc.org/blog/preparing-for-nethernet/): current Bedrock transport transition, TCP signaling plus UDP gameplay, and the loopback warning.
- [Geyser's supported system properties](https://geysermc.org/wiki/geyser/geyser-command-line-arguments-and-system-properties/): `geyserUdpAddress`, `geyserUdpPort`, `geyserWebrtcPort`, `geyserSignalingPort`, transport/signaling overrides and the explicit `-1` disable mode.
- [Mojang's NetherNet onboarding guide](https://mojang.github.io/bedrock-protocol-docs/guides/nether-net-onboarding-guide/): actual signaling, advertised candidate reachability and DTLS/SCTP gameplay transport.

The pinned JAR places `advertise-addresses` on its `SignalingConfig` interface. Its inspected implementation is authoritative for this exact bundle even where a current web page describes a different nesting. The launcher explicitly passes an empty `-DgeyserAdvertiseAddresses=` to neutralize an inherited JVM override. In build 1308, `advertisedAddresses()` splits that property, `addresses(...)` filters blank entries, and an empty result falls back to the configured empty list. It does not produce an invalid empty candidate. A separate direct invocation of that pinned private static method returned `[]` for an empty property and removed blank/duplicate entries; see `reports/GEYSER_EMPTY_ADVERTISE_CHECK_R4.log`. It used the existing Paper dependency cache and created no server or listener. Empty configuration plus a specific bind and disabled STUN is the behavior used here; the filtering method is included in the retained bytecode evidence.
