# CodexAPI

A local OpenAI-compatible API proxy that routes requests through your ChatGPT account. Drop it in front of any OpenAI-compatible client and use GPT-5 and Codex models without a direct API key.

## How it works

CodexAPI authenticates with ChatGPT via OAuth, then exposes a local HTTP server that speaks the OpenAI API format. Any tool that supports a custom base URL (Cursor, Continue, Open WebUI, LiteLLM, etc.) works out of the box.

```
Your client  ──►  CodexAPI (:8000)  ──►  chatgpt.com
(OpenAI format)   (local proxy)         (your account)
```

## Supported models

| Model | Reasoning efforts |
|---|---|
| `gpt-5` | `low` `medium` `high` |
| `gpt-5.1` | `none` `low` `medium` `high` |
| `gpt-5.2` | `none` `minimal` `low` `medium` `high` `xhigh` |
| `gpt-5.4` | `none` `minimal` `low` `medium` `high` `xhigh` |
| `gpt-5-codex` | `low` `medium` `high` |
| `gpt-5.1-codex-mini` | `low` `medium` `high` |
| `gpt-5.1-codex` | `low` `medium` `high` |
| `gpt-5.1-codex-max` | `low` `medium` `high` `xhigh` |
| `gpt-5.2-codex` | `low` `medium` `high` `xhigh` |
| `gpt-5.3-codex` | `none` `minimal` `low` `medium` `high` `xhigh` |

### Model name syntax

Reasoning effort and per-request options can be embedded directly in the model name:

```
gpt-5.4                                          # default effort (medium)
gpt-5.4-high                                     # explicit effort
gpt-5.4-high-[web_search:true]                   # with web search
gpt-5.4-high-[reasoning_summary:detailed]        # with reasoning summary
gpt-5.4-high-[web_search:true,reasoning_summary:concise]
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat completions |
| `POST` | `/v1/completions` | OpenAI-compatible text completions |
| `GET` | `/v1/models` | List all available models |

Both streaming (`"stream": true`) and non-streaming responses are supported.

## Getting started

### Prerequisites

- Python 3.13+
- A ChatGPT account (Plus, Pro, Team, or Enterprise)

### Install

```bash
pip install .
```

### 1. Login

Authenticate with your ChatGPT account. This opens a browser and stores tokens locally.

```bash
codexapi login
```

If you are on a headless machine:

```bash
codexapi login --no-browser
```

It will print an authorization URL. Open it in any browser, complete login, then paste the redirect URL back into the terminal.

### 2. Serve

```bash
codexapi serve
```

Options:

| Flag | Env var | Default | Description |
|---|---|---|---|
| `--host` | — | `127.0.0.1` | Bind address |
| `--port` | `PORT` | `8000` | Port |
| `--reasoning-summary` | `CHATGPT_LOCAL_REASONING_SUMMARY` | `auto` | `auto` `concise` `detailed` `none` |
| `--enable-web-search` | `CHATGPT_LOCAL_ENABLE_WEB_SEARCH` | `false` | Enable web search by default |

### 3. Use

Point any OpenAI-compatible client at `http://localhost:8000`:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5.4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Configuration

Configuration is read from environment variables or a `.env` file in the working directory.

| Variable | Description |
|---|---|
| `CHATGPT_LOCAL_HOME` | Directory where auth tokens are stored (default: `~/.codexapi`) |
| `CHATGPT_LOCAL_REASONING_SUMMARY` | Default reasoning summary verbosity (`auto` / `concise` / `detailed` / `none`) |
| `CHATGPT_LOCAL_ENABLE_WEB_SEARCH` | Enable web search by default (`true` / `false`) |
| `PORT` | Server port |

## Docker

### First-time login

```bash
docker compose --profile login run --rm login
```

Follow the printed URL in your browser, then paste the redirect URL back into the terminal. Tokens are stored in a Docker volume and persist across restarts.

### Run the server

```bash
docker compose up --build
```

The server is available at `http://localhost:8000`.

### Re-authenticate

```bash
docker compose --profile login run --rm --build login
```

### Environment

Copy `.env.example` to `.env` and adjust as needed before running:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `CHATGPT_LOCAL_HOME` | Set to `/data` to match the Docker volume mount |
| `CHATGPT_LOCAL_REASONING_SUMMARY` | `auto` / `concise` / `detailed` / `none` |
| `CHATGPT_LOCAL_ENABLE_WEB_SEARCH` | `true` / `false` |
| `PORT` | Host port to expose (default: `8000`) |

## CLI reference

```
codexapi login     Authenticate with ChatGPT and store tokens
codexapi serve     Start the OpenAI-compatible server
codexapi info      Print the currently stored account and token info
```

## License

MIT
