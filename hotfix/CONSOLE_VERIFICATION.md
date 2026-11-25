# Local control centre verification

This report covers the web console shipped by the 1.0.4 repair overlay. It distinguishes Java policy tests, requests to the running Paper server, and browser inspection. It does not claim a production deployment or Bedrock validation.

## Implementation and reviewed corrections

The control centre is served by the game plugin on `127.0.0.1:8765`. Its Overview, Server console, Players, Runtime & assets, and JEEVA pages read the running server. It does not require a separate Node service or an external AI subscription. JEEVA is explicitly labelled as a local guide with deterministic answers.

The repair uses Paper's real console sender for command dispatch. The earlier reflective sender proxy could fail when a Minecraft command casts its sender to Paper's concrete implementation. Command output is available through the server's live log.

Commands enter a single bounded queue and execute on the Bukkit main thread. A START audit entry must be successfully written before dispatch. A waiting request that times out is cancelled before it can execute; a command that has already started keeps its queue slot until completion. A failed result-audit write is reported as a warning after the action, without falsely presenting the command as unexecuted. Shutdown cancels queued work and closes the HTTP listener, scheduler task, executor, and current access-token file.

The bearer token is generated after the port bind succeeds, written atomically with owner-only permissions where supported, and never embedded in the static page. Host and Origin checks reject cross-origin requests. Credential commands are refused, including aliases and nested `execute ... run` forms. Lifecycle commands require explicit confirmation, including their namespaced and wrapped forms. The UI inserts log, command, and guide text with `textContent`. Displayed logs redact the current access token and known credential forms.

## Automated policy and queue tests

`ConsoleSecurityTest` has 12 tests and `ConsoleCommandQueueTest` has 10 tests. All 22 passed with Java 25 and the pinned JUnit Platform 1.11.4 runner. They were also part of the aggregate run in which all 52 repair-module JUnit tests passed.

Coverage includes:

- exact bearer-token comparison, loopback Host checks, Origin rejection, command length/control-character validation, lifecycle confirmation, namespaced commands, credential aliases, and nested command wrappers;
- credential redaction, including quoted values, namespaced login commands, and ANSI escape sequences;
- queue serialization, cancellation before execution, timeout while an action is already running, scheduling failure, command failure, and release of a completed queue slot;
- audit failure before dispatch, audit failure after dispatch, and a lifecycle command closing its own queue without deadlocking.

The full overlay compiled and its JAR was built by Gradle with Java 25. The aggregate tests used the standalone pinned JUnit runner after dependency retrieval interrupted the Gradle `check` invocation; this report does not describe that interrupted Gradle invocation as successful.

## Actual HTTP integration

The probe is [`tools/probe_web_console.py`](../tools/probe_web_console.py). It was executed by the native staging harness in the same process/network environment as Paper, rather than against a mock. It reads the token locally and does not print or include it in its report.

At **2026-11-25 14:35:58 UTC**, the probe recorded **23 passed checks out of 23** against the running **Minecraft 26.3 / SDCraftCore 1.0.4-r4-repair** server. The report is saved as [`console-http-verification.json`](console-http-verification.json).

| Actual request or observation | Result |
| --- | --- |
| Dashboard, JavaScript, CSS, and local security headers | 200; passed |
| Missing or incorrect API bearer | 401; passed |
| Foreign Host, foreign Origin, and sandboxed `null` Origin | 403; passed |
| Authenticated live server snapshot and bounded server log | 200; passed |
| Multiline command, credential command, null/array command, and non-boolean confirmation | 400; passed |
| Unconfirmed lifecycle command and wrapped lifecycle command | 409; passed; command not dispatched |
| Malformed JSON, incorrect media type, and oversized request | 400; passed |
| JEEVA weapon guidance | 200; native starter delivery described accurately |
| Actual Paper console command `list` | 200; accepted by the real console sender |
| Audit record for `list` | Matching START and RESULT entries |

The only command actually dispatched by this HTTP probe is the read-only `list` command. Rejection checks do not shut down or modify the game.

## Browser inspection

The actual running page at `http://127.0.0.1:8765/` was opened in the CUA Chrome browser on 25 November 2026. Its sign-in card rendered with the intended dark background, gold controls, readable text, and no missing assets. The captured page is [`control-centre-login.jpg`](../docs/repair-evidence/control-centre-login.jpg). This is a screenshot of the running service, not a generated mock-up.

The native desktop's Chromium launcher initially failed because its installed shell wrapper referenced a missing Chromium executable. The CUA browser fallback successfully reached the same live service. The browser's advertised authentication rules require credential entry through its secure user flow and prohibit programmatic token entry through the browser tools. No token was exposed and no authentication check was bypassed. The browser inspection therefore stops at the actual sign-in screen: authenticated page appearance, narrow-view layout, and browser button interactions remain unverified. The separate 23-check HTTP probe did authenticate internally and exercised the real service and read-only command dispatch.

## Scope and practical limits

The console intentionally binds to loopback. A browser must run on the server's machine, or the owner must use an independently configured authenticated tunnel. A local URL opened on another computer does not address the game server. Tokens rotate on plugin startup, so a previous browser session may need to reconnect.

The live Players page reports a resource-pack load acknowledgement separately from authentication; that acknowledgement alone is not visual evidence. JEEVA provides the documented local guidance and does not represent a connected generative model. The server console is an owner administration surface: authenticated commands run with console permissions and produce local audit records.
