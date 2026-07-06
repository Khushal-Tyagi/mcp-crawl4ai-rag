---
name: c-build-triage
description: 'Agentic C code build and run triage loop. Use when: generating C code, building on a remote Yocto SSH system, fixing build errors in a loop, deploying binary to a target system via SSH, running and fixing runtime errors in a loop, accessing target via serial or SSH, copying files between remote systems.'
argument-hint: 'Describe the C code task or provide the source file to triage'
---

# C Build Triage — Agentic Loop

## When to Use
- You need to generate, build, deploy, and run C code on remote embedded systems
- Build or runtime errors need iterative AI-assisted fixing
- Target system is accessible via SSH and/or serial connection

## Architecture

```
Cursor (Windows)
   │
   ├─► [Phase 1] Generate C code using RAG context
   │
   ├─► [Phase 2] SSH to Yocto build server
   │       └─► SCP file → run build → if error → feed back to AI → patch → retry
   │
   ├─► [Phase 3] SCP binary to deployment target (SSH)
   │
   └─► [Phase 4] Run on target (SSH or serial)
           └─► if runtime error → feed back to AI → patch → restart Phase 2
```

## Prerequisites
- Your existing Python SSH connection functions are available (import and call them)
- Your existing Python serial connection functions are available (import and call them)
- Build server is reachable via SSH
- Deployment target is reachable via SSH or serial
- You know: remote file drop path, build command, success indicator, binary output path

## Procedure

### Phase 1 — Code Generation
1. Use `gather_task_context` or `search_repository_code` to retrieve relevant indexed code/specs.
2. Generate the C source file grounded in retrieved context.
3. Note the local path of the generated `.c` file.

### Phase 2 — Remote Build Loop
```
max_retries = 10
attempt = 0

while attempt < max_retries:
    1. SCP generated file to build server at <REMOTE_DROP_PATH> using your SSH SCP function
    2. Run build command over SSH using your SSH exec function
       - Capture stdout + stderr
    3. Check output for success indicator (e.g. "Build succeeded", exit code 0)
    4. If SUCCESS → break, proceed to Phase 3
    5. If FAILURE:
       - Extract error lines from stderr
       - Feed errors back to AI as context:
         "Build failed with the following errors: <errors>. Fix the C code."
       - AI patches the file
       - attempt += 1
       - continue loop

If max_retries exceeded → report failure with last error, ask user to intervene
```

### Phase 3 — Artifact Transfer
1. SCP the compiled binary from build server output path to deployment target using your SSH SCP function.
2. Confirm transfer (check file exists on target via SSH).

### Phase 4 — Remote Execution Loop
```
max_retries = 10
attempt = 0

while attempt < max_retries:
    1. Run binary on target via SSH exec function (or serial if SSH unavailable)
    2. Capture stdout + stderr + exit code
    3. If exit code 0 and no error patterns → SUCCESS, report output to user
    4. If error:
       - Feed runtime output back to AI:
         "Runtime error on target: <output>. Fix the C code."
       - AI patches the file
       - Restart from Phase 2 (rebuild + redeploy)
       - attempt += 1

If max_retries exceeded → report last runtime output, ask user to intervene
```

## Serial vs SSH for Target Access
- Prefer SSH if available on the target.
- Use your serial connection function if target is only reachable via serial port.
- If target is connected to a Windows host via serial (accessible through RealVNC or SSH to Windows):
  - Try SSH to Windows host first (requires OpenSSH server enabled on Windows)
  - Then relay serial commands via `plink`, `putty -serial`, or a Python serial relay script on that host

## Key Parameters to Confirm Before Starting
| Parameter | Description |
|-----------|-------------|
| `BUILD_SERVER_HOST` | SSH host of Yocto build server |
| `BUILD_SERVER_USER` | SSH username |
| `REMOTE_DROP_PATH` | Path to place the .c file on build server |
| `BUILD_COMMAND` | Command to trigger build (e.g. `make`, `bitbake <recipe>`) |
| `BUILD_SUCCESS_PATTERN` | String or exit code indicating success |
| `BINARY_OUTPUT_PATH` | Path of compiled output on build server |
| `TARGET_HOST` | SSH host of deployment target |
| `TARGET_RUN_COMMAND` | Command to execute the binary on target |
| `USE_SERIAL` | true/false — whether to use serial for target access |

## Error Feedback Format (for AI patch loop)
Always include:
- The full compiler error or runtime output (not just last line)
- The current source file content
- The build command that was used

## Notes
- Always preserve a local copy of the last working version before patching
- Log each attempt with timestamp, attempt number, and error summary
- If the same error repeats 3 times without change, escalate to user rather than looping further
