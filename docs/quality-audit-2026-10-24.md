What this repo does: PCAP Lab sends a seeded mix of normal HTTP requests and attack-shaped requests to a local dummy server. It records packets and writes an answer key for each student. Assumed load: one teacher running a local batch, with several student processes in parallel, on Linux or macOS.

This report records the audit of commit `18e51eb` and the fixes made afterward. Locations below refer to that original commit. Every finding below has been addressed in this change; no additional smaller findings were withheld.

## Must fix

1. **Student IDs can escape the output directory** (`generator/pcap_generator.py:L24-28`, `generator/traffic_engine.py:L41`).
   - **What this is:** Student IDs become directory names for generated files.
   - **Problem:** An ID such as `../outside` or `/tmp/outside` writes outside the chosen output folder. The documented sudo workflow makes the damage larger.
   - **Fix:** Validate IDs in the shared engine before either entry point can create files. Reject empty IDs, dot directories, path separators, and null bytes.
   - **If we skip it:** A student list can overwrite files outside the lab output directory.

2. **Clean can delete source files and unrelated data** (`main.py:L191-209`, `generator/shell.py:L190-194`).
   - **What this is:** Both entry points delete generated output.
   - **Problem:** `clean --output-dir .` removes the checkout; the shell also deletes arbitrary files placed inside `output`. The cache walk enters unrelated trees such as virtual environments.
   - **Fix:** Share one cleanup function that accepts only student directories containing generated artifact names. Reject unrelated content and symlinks; remove the broad cache sweep.
   - **If we skip it:** A mistaken path or an unrelated file in `output` can cause permanent data loss.

3. **Repeated students overwrite or mix existing results** (`generator/pcap_generator.py:L28-29,L58-77`, `generator/utils/capture.py:L22-24`).
   - **What this is:** Each student owns a PCAP and answer key.
   - **Problem:** An existing capture is deleted before tcpdump can start. Duplicate IDs in a parallel batch write the same files, and a failed rerun can leave an old answer key beside a new capture.
   - **Fix:** Reject duplicates and existing output before starting the batch. Reserve each directory with exclusive creation and remove only that newly created directory on failure.
   - **If we skip it:** A failed run destroys valid work or silently produces mismatched evidence.

4. **Missing dependencies look like successful operation** (`requirements.txt:L1-5`, `generator/shell.py:L10-34`, `generator/utils/http_client.py:L7-27`).
   - **What this is:** The shell needs Questionary and HTTP generation needs Requests.
   - **Problem:** Questionary is absent from requirements. Fake replacement modules make the shell exit silently or let the HTTP client send nothing when installation is incomplete.
   - **Fix:** Declare Questionary and use normal dependency imports. Missing packages now fail clearly rather than impersonating a working library.
   - **If we skip it:** A clean installation cannot use the shell and can claim to generate traffic without sending requests.

5. **Capture can report success without usable packets** (`generator/utils/capture.py:L52-87`, `generator/pcap_generator.py:L47-50`).
   - **What this is:** tcpdump must be listening before traffic starts and must finish writing before results are accepted.
   - **Problem:** A fixed half-second sleep does not establish readiness. Runtime capture errors and missing files are ignored, and a forced kill is not reaped; the key is written before capture completion.
   - **Fix:** Wait for tcpdump's listening message with a deadline, use immediate packet delivery, stop and reap it, and reject failed or empty captures. Write the key only after capture validation.
   - **If we skip it:** Slow startup, a wrong interface, disk failure, or an interrupted capture produces a misleading successful lab.

6. **Replay rewrites the wrong server port** (`main.py:L124-164`, `generator/pcap_generator.py:L30`).
   - **What this is:** tcprewrite maps the captured server port to the target port.
   - **Problem:** Generation chooses a dynamic server port, while replay always maps 8080. A capture made on port 45678 is unchanged by that mapping.
   - **Fix:** Save `server_port` in the answer key and read it during replay. Add an explicit `--source-port` override; retain 8080 only when there is no answer key, and reject malformed or incomplete keys.
   - **If we skip it:** Replay sends packets to the old ephemeral port instead of the requested target port.

7. **Replay temporary files collide and survive failures** (`main.py:L143-178`).
   - **What this is:** Address rewriting needs a temporary PCAP.
   - **Problem:** Every run uses `<pcap>.tmp`, overwriting an existing file or another replay's output. A failed rewrite leaves that file behind.
   - **Fix:** Give each invocation its own temporary directory and clean it on rewrite failure, replay failure, and success.
   - **If we skip it:** Concurrent replay corrupts inputs and a privileged rewrite can overwrite unrelated temporary content.

8. **Invalid options silently produce the wrong lab** (`main.py:L34-46`, `generator/traffic_engine.py:L41-46,L140-143`).
   - **What this is:** Request counts, attack counts, ratios, worker counts, and encoding levels control generation.
   - **Problem:** Zero requests and negative attack counts can succeed with no work. An out-of-range ratio is silently clamped, and `nan` can crash count calculation.
   - **Fix:** Validate CLI ranges and shared engine inputs, including NaN and counts above an explicitly specified request total. Validate replay IPv4 addresses and port ranges too.
   - **If we skip it:** The output does not match the requested exercise, or invalid input crashes after work begins.

9. **Obfuscation changes the meaning of attacks** (`generator/utils/obfuscator.py:L9-21`).
   - **What this is:** Higher levels URL-encode attack payloads.
   - **Problem:** Random capitalization also changes `cat /etc/passwd` or `alert(document.cookie)` into case-sensitive commands or expressions that no longer work.
   - **Fix:** Encode without changing letter case, and encode path separators as well. Verify that decoding the selected number of layers restores the original payload.
   - **If we skip it:** The answer key labels broken commands as meaningful attacks.

10. **The default registry depends on the working directory** (`generator/attack_registry.py:L15,L33-42`, `generator/traffic_engine.py:L64-73,L100-104`).
    - **What this is:** The registry maps attack names to Python classes.
    - **Problem:** A different working directory can substitute its own `generator/attacks.json`. A list instead of an object crashes lookup, and missing classes can silently turn requested attacks into normal traffic.
    - **Fix:** Resolve the built-in registry beside its module, validate its shape, and fail when an enabled strategy is unavailable. Explicit custom paths remain supported.
    - **If we skip it:** Invoking the script from another directory changes the exercise or loads unintended classes.

11. **HTTP failures and proxy settings hide missing traffic** (`generator/utils/http_client.py:L36-39,L49-66`, `generator/traffic_engine.py:L102-115`).
    - **What this is:** The HTTP client sends each generated request.
    - **Problem:** Connection errors are ignored, so the answer key can claim attacks that never reached the server. Environment proxies can route loopback traffic away from the capture; sessions are never closed by the engine.
    - **Fix:** Fail clearly on transport errors, disable environment proxies for the internal client, close responses and sessions, and keep delay randomness consistent in the error path.
    - **If we skip it:** An unreachable server or configured proxy yields false ground truth and leaks client resources across long batches.

12. **The answer key cannot locate an attack in time** (`generator/traffic_engine.py:L109-126`, `README.md:L31`).
    - **What this is:** The answer key is the evidence used to identify attack requests in a trace.
    - **Problem:** The README promises timestamps, but entries contain neither timestamps nor request positions. Obfuscation level is also missing from saved settings.
    - **Fix:** Store each attack's one-based request index and Unix send timestamp, and record the obfuscation level. Describe the timestamp as the send time, not the exact kernel packet timestamp.
    - **If we skip it:** Repeated payloads are ambiguous and saved settings cannot reproduce the selected encoding level.

13. **Routine generation errors crash the interactive shell** (`generator/shell.py:L215-233`).
    - **What this is:** The shell loads a student list and starts a batch.
    - **Problem:** A missing list file or a tcpdump permission failure exits the shell with a traceback. A blank list file produces a misleading batch-complete message.
    - **Fix:** Report file, validation, and generation errors and return to the menu. Reject an empty resolved list and read student files as UTF-8 in both entry points.
    - **If we skip it:** A recoverable configuration error ends the session and forces the user to configure it again.

14. **The advertised Python 3.8 support fails at import** (`generator/pcap_generator.py:L59`, `.github/workflows/ci.yml:L18`, `README.md:L8`).
    - **What this is:** The README advertises Python 3.8 and newer.
    - **Problem:** `list[TrafficEngine]` is evaluated at import and is unsupported on Python 3.8. CI only exercises Python 3.10.
    - **Fix:** Use `typing.List` and test Python 3.8, 3.10, and 3.14 in CI.
    - **If we skip it:** Users on a documented supported version cannot import the generator.

15. **Replay and determinism documentation promises more than the code does** (`README.md:L24,L97,L112-120`).
    - **What this is:** The guide explains how to use generated traces for detection exercises.
    - **Problem:** It promises complete reproducibility despite dynamic ports and timestamps, and suggests raw packet replay validates a live WAF. Recorded TCP sessions do not establish fresh HTTP sessions, and loopback link headers do not directly match Ethernet.
    - **Fix:** Document reproducible request choices and payloads, passive packet replay, link-layer compatibility, and live HTTP testing as a separate workflow.
    - **If we skip it:** Teachers expect identical PCAP bytes or interpret a failed raw replay as evidence about WAF rules.

## Should fix

16. **Tests miss the destructive paths and write to real output** (`tests/test_generator.py:L130-178`, `tests/test_capture.py:L1-28`).
    - **What this is:** Tests are meant to verify generation without altering user artifacts.
    - **Problem:** Batch tests use the real `output` directory. Existing tests do not exercise path escape, overwrite protection, replay cleanup, capture completion, or repeated request determinism.
    - **Fix:** Move batch output to pytest temporary directories and add focused regression cases for the confirmed bugs. The suite grows from 39 to 102 cases.
    - **If we skip it:** Running tests can touch user results and the same faults can return unnoticed.

17. **Unused fallback code suggests settings that do nothing** (`generator/config.py:L1,L13-15`, `generator/utils/obfuscator.py:L9-11`).
    - **What this is:** A constant claims to select a fallback interface, and a case-randomizing helper no longer has a caller after the payload fix.
    - **Problem:** Repository-wide searches show no consumer of `DEFAULT_INTERFACE`; retaining the helper after fix 9 would leave dead code.
    - **Fix:** Delete those unused definitions and imports. Keep the normal-traffic compatibility function because tests still call it.
    - **If we skip it:** Readers can change a setting that never affects interface selection or revive unsafe case randomization.

Verdict: All 17 confirmed findings are addressed. Ship after CI passes.

Lean: -51 lines, -0 dependencies possible (41 lines of fake dependency blocks and 10 lines of unused helper/config code). Questionary is a missing required dependency, so declaring it is necessary.

Not checked: No live external WAF/IDS validation or Ethernet replay was performed. Local macOS loopback captures were generated and decoded successfully, both sequentially and with two worker processes; tcprewrite also mapped the captured dynamic port to 80 in a real PCAP. Linux and the Python version matrix are validated by CI, not by local execution. Generated profiling logs were not treated as executable code.

## Review of the original latest commit

What this change does: Commit `18e51eb` adds `.DS_Store` to `.gitignore`. It does not alter runtime behavior.

Looks good. Ship.

Checked the full diff, the ignore file, and references to tracked platform metadata. Assumed the same local batch workload as the audit.

## Review of the corrective change

What this change does: It prevents output loss and invalid labs, makes capture and HTTP errors visible, and fixes replay port selection and temporary file cleanup. It adds regression tests and corrects documentation without redesigning the interface.

Looks good. Ship, subject to CI.

Checked the full diff, callers in both entry points, all generator/runtime modules, registry mappings, existing and new tests, dependencies, README, and workflow configuration. No unresolved findings were found in this pass.

Not checked: New TUI designs are proposals only. Their interactions, cancellation, and worker progress are not implemented or claimed as tested.
