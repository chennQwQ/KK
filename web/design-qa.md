# Design QA

## Result

final result: blocked

## Verified

- `npm.cmd run build` completed successfully.
- Vite production bundle was generated in `web/dist/`.
- Foreground dev server command starts successfully:

```powershell
node_modules\.bin\vite.cmd --host 127.0.0.1 --port 5173
```

The foreground run reported:

```text
Local: http://127.0.0.1:5173/
```

## Blocked Checks

Automated browser QA could not run in this environment because both the in-app Browser and Chrome fallback failed to start through the Windows sandbox with `CreateProcessAsUserW failed: 5`.

Persistent background dev server startup also did not survive across tool invocations in this environment. The app can still be run manually with the foreground command above.

## Manual QA Scope

When browser automation is available, verify:

- Desktop layout at 1440px width matches the selected Research Console direction.
- Tablet and mobile layouts do not overlap text or controls.
- History search filters conversations.
- Source ordering tabs switch visible order.
- Feedback buttons show selected state.
- Composer submits without breaking when FastAPI is offline.
- Model selector remains usable.

