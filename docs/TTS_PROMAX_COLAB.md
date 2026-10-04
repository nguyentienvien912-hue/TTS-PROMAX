# TTS PROMAX — Colab GPU

This customized VoiceStudio source retains the upstream layout, backend, engines, module names, API routes and storage keys. Only display branding and the default dark palette are changed. Other palettes and light mode remain available in Settings.

1. Open `notebooks/TTS_PROMAX_Colab.ipynb` in Google Colab.
2. Select Runtime > Change runtime type > GPU (T4 or better).
3. Run setup cells in order, authorize Drive mounting, and upload the accompanying `TTS_PROMAX_source.zip` when asked.
4. The notebook installs the upstream dependencies with its existing torch constraints and builds the current Electron web renderer via `bun run build:web`.
5. Run launch and open-app cells. Use the private Google-session port proxy. Run the smoke cell to generate and play real speech.

Drive storage defaults to `MyDrive/TTS_PROMAX/data` for database, voices, projects and outputs; model caches use `MyDrive/TTS_PROMAX/models`. Python packages and application source remain on Colab's temporary disk. Set `USE_DRIVE = False` before setup for temporary storage. Do not run multiple sessions against one database. Drive can slow cache loads; model VRAM needs depend on engine. Colab disconnections stop running jobs; files already written to Drive persist. Tokens remain in Colab Secrets/runtime, outside Drive.

Colab is a web deployment. Native desktop features (tray, global dictation shortcut, local app integration) require Electron; this customization does not remove or redesign them. Runtime GPU availability and an end-to-end generation must be verified inside the user's Colab session.

Upstream: https://github.com/debpalash/VoiceStudio. Existing licenses and attribution are retained.
