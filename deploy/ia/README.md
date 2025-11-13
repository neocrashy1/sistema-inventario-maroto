# Levitii IA stack

This folder contains a Docker Compose stack to run a local LLM server (text-generation-webui) and a lightweight agent that queries it to produce suggestions for the repository.

How it works
- `tgw` (text-generation-webui) serves a local HTTP API at port 7860 and hosts models under `./models`.
- `agent` calls the TGW `/api/prompt` endpoint and writes `ia_suggestions.json` into the mounted project folder.

Notes and security
- The default `AUTONOMOUS=false`: agent will not commit or push changes. Set `AUTONOMOUS=true` only in an isolated environment after validating behavior.
- The first run requires a model placed under `deploy/ia/models/` or using the web UI to download/install a model.
