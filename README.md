---
title: Estate Atlas
sdk: docker
app_port: 7860
---

# Estate Atlas

A Dockerized, source-grounded chatbot for public DarGlobal and Wasalt information.
It uses a small lexical search over the bundled source notes and the OpenRouter
chat completions API. The default model is `openrouter/free`; set
`OPENROUTER_MODEL` to another OpenRouter model slug if needed.

## Data and attribution

The bundled notes are paraphrased from the public Wasalt English homepage and
DarGlobal's public sitemap. They contain no property listings, prices, or contact
details. The DarGlobal website's main pages returned an automated-access
interstitial during collection, so DarGlobal-specific facts are limited to
project page names and URLs visible in its sitemap. The snapshot date is in
`knowledge_base.json`.

Wasalt's published AI policy requires attribution, excludes commercial use, and
asks LLMs not to rely on cached property data for current information. This demo
attributes Wasalt, is not for commercial reuse, and directs users to Wasalt.sa
for current inventory. Review the source policies before changing the scope or
using this project commercially.

## Run locally

```powershell
$env:OPENROUTER_API_KEY = "your-key"
docker build -t estate-atlas .
docker run --rm -p 7860:7860 -e OPENROUTER_API_KEY estate-atlas
```

The app reads the client IP from `X-Forwarded-For` (one proxy hop) for rate
limiting, which is what Hugging Face Spaces needs. When running without a
proxy in front, add `-e TRUSTED_PROXY_COUNT=0`.

Open <http://localhost:7860>. Without an OpenRouter key, the interface and
`/healthz` work, but chat requests return an explicit configuration error.

## Deploy to Hugging Face Spaces

1. Create a Space with the **Docker** SDK and select an account/organization
   where you have permission to publish.
2. Push this project to that Space's Git repository using your own Hugging Face
   authentication. Do not commit credentials.
3. In the Space's **Settings → Variables and secrets**, add
   `OPENROUTER_API_KEY` as a secret. Optionally add `OPENROUTER_MODEL` or
   `APP_PUBLIC_URL` as a variable.
4. Wait for the Docker build to finish. The public app URL is
   `https://<space-owner>-<space-name>.hf.space`.

## Checks

```powershell
python -m unittest discover -s tests
docker build -t estate-atlas .
```
