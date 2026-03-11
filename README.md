# CodexAPI

![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![uv](https://img.shields.io/badge/uv-workspace-blueviolet)
![Stars](https://img.shields.io/github/stars/kkristof200/codex-api)
![Forks](https://img.shields.io/github/forks/kkristof200/codex-api)
![Open PRs](https://img.shields.io/github/issues-pr/kkristof200/codex-api)
![Open Issues](https://img.shields.io/github/issues/kkristof200/codex-api)
![Contributors](https://img.shields.io/github/contributors/kkristof200/codex-api)


A local OpenAI-compatible API proxy that routes requests through your ChatGPT account. Drop it in front of any OpenAI-compatible client and use GPT-5 and Codex models without a direct API key.

```
Your client  ──►  CodexAPI (:8000)  ──►  chatgpt.com
(OpenAI format)   (local proxy)         (your account)
```

---

## Table of contents

- [Quick start](#quick-start)
- [Setup](#setup)
  - [Option A — CLI (local)](#option-a--cli-local)
  - [Option B — Docker](#option-b--docker)
  - [Option C — Client library only](#option-c--client-library-only)
- [Use](#use)
- [Supported models](#supported-models)
- [Endpoints](#endpoints)
- [Configuration](#configuration)
- [CLI reference](#cli-reference)

---

## Quick start

```bash
# 1. Install
git clone https://github.com/kkristof200/codex-api && cd codex-api
pip install uv && uv sync

# 2. Login
codexapi login

# 3. Serve
codexapi serve
```

Then point any OpenAI-compatible client at `http://localhost:8000`.

---

## Setup

### Option A — CLI (local)

> [!NOTE]
> Requires Python 3.13+ and a ChatGPT account (Plus, Pro, Team, or Enterprise).

**1. Install**

```bash
git clone https://github.com/kkristof200/codex-api
cd codex-api
pip install uv
uv sync
```

Or install only the server package with pip (no uv required):

```bash
pip install ./packages/codexapi-server
```

**2. Login**

```bash
codexapi login
```

> [!TIP]
> On a headless machine, use `--no-browser`. CodexAPI will print an authorization URL — open it in any browser, complete login, then paste the redirect URL back into the terminal.
>
> ```bash
> codexapi login --no-browser
> ```

**3. Serve**

```bash
codexapi serve
```

Available options


| Flag                  | Env var                           | Default     | Description                        |
| --------------------- | --------------------------------- | ----------- | ---------------------------------- |
| `--host`              | —                                 | `127.0.0.1` | Bind address                       |
| `--port`              | `PORT`                            | `8000`      | Port                               |
| `--reasoning-summary` | `CHATGPT_LOCAL_REASONING_SUMMARY` | `auto`      | `auto` `concise` `detailed` `none` |
| `--enable-web-search` | `CHATGPT_LOCAL_ENABLE_WEB_SEARCH` | `false`     | Enable web search by default       |




---

### Option B — Docker

> [!NOTE]
> Requires Docker and Docker Compose.

**1. Configure**

```bash
cp .env.example .env
```

Environment variables


| Variable                          | Description                                                    |
| --------------------------------- | -------------------------------------------------------------- |
| `CHATGPT_LOCAL_HOME`              | Set to `/data` to match the Docker volume (default in example) |
| `CHATGPT_LOCAL_REASONING_SUMMARY` | `auto` / `concise` / `detailed` / `none`                       |
| `CHATGPT_LOCAL_ENABLE_WEB_SEARCH` | `true` / `false`                                               |
| `PORT`                            | Host port to expose (default: `8000`)                          |




**2. Login**

```bash
docker compose --profile login run --rm --build --service-ports login
```

Your browser will open (or a URL will be printed). Complete login — the container exits automatically and tokens are saved to a persistent Docker volume.

> [!TIP]
> If the browser redirect page fails to load, copy the URL from your browser's address bar and paste it into the terminal when prompted. This is normal when the container's port mapping isn't fully established.

**3. Serve**

```bash
docker compose up --build serve
```

The server is available at `http://localhost:8000`.

**Re-authenticate** when the token expires:

```bash
docker compose --profile login run --rm --build --service-ports login
```

---

### Option C — Client library only

Install just the core library to make requests programmatically without the server:

```bash
pip install ./packages/codexapi-client
```

Or directly from GitHub:

```bash
pip install "codexapi-client @ git+https://github.com/kkristof200/codex-api.git#subdirectory=packages/codexapi-client"
```

```python
from codexapi_client import CodexAPI, OpenAIChatCompletionAdaptorHTTP

codex = CodexAPI()
result = codex.request_http(
    model_name="gpt-5.4",
    reasoning_effort="medium",
    chatgpt_acc_id="your-account-id",
    auth_token="your-token",
    messages=[{
        "type": "message",
        "role": "user",
        "content": [{"type": "input_text", "text": "Hello!"}]
    }],
    adaptor=OpenAIChatCompletionAdaptorHTTP(),
)
```

---

## Use

Point any OpenAI-compatible client at `http://localhost:8000`:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-5.4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Supported models


| Model                | Reasoning efforts                              |
| -------------------- | ---------------------------------------------- |
| `gpt-5`              | `low` `medium` `high`                          |
| `gpt-5.1`            | `none` `low` `medium` `high`                   |
| `gpt-5.2`            | `none` `minimal` `low` `medium` `high` `xhigh` |
| `gpt-5.4`            | `none` `minimal` `low` `medium` `high` `xhigh` |
| `gpt-5-codex`        | `low` `medium` `high`                          |
| `gpt-5.1-codex-mini` | `low` `medium` `high`                          |
| `gpt-5.1-codex`      | `low` `medium` `high`                          |
| `gpt-5.1-codex-max`  | `low` `medium` `high` `xhigh`                  |
| `gpt-5.2-codex`      | `low` `medium` `high` `xhigh`                  |
| `gpt-5.3-codex`      | `none` `minimal` `low` `medium` `high` `xhigh` |


### Model name syntax

Reasoning effort and per-request options can be embedded directly in the model name:

```
gpt-5.4                                          # default effort (medium)
gpt-5.4-high                                     # explicit effort
gpt-5.4-high-[web_search:true]                   # with web search
gpt-5.4-high-[reasoning_summary:detailed]        # with reasoning summary
gpt-5.4-high-[web_search:true,reasoning_summary:concise]
```

---

## Endpoints


| Method | Path                   | Description                        |
| ------ | ---------------------- | ---------------------------------- |
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat completions |
| `POST` | `/v1/completions`      | OpenAI-compatible text completions |
| `GET`  | `/v1/models`           | List all available models          |


Both streaming (`"stream": true`) and non-streaming responses are supported.

---

## Configuration


| Variable                          | Description                                                                    |
| --------------------------------- | ------------------------------------------------------------------------------ |
| `CHATGPT_LOCAL_HOME`              | Directory where auth tokens are stored (default: `~/.chatgpt-local`)           |
| `CHATGPT_LOCAL_REASONING_SUMMARY` | Default reasoning summary verbosity (`auto` / `concise` / `detailed` / `none`) |
| `CHATGPT_LOCAL_ENABLE_WEB_SEARCH` | Enable web search by default (`true` / `false`)                                |
| `PORT`                            | Server port                                                                    |


---

## CLI reference

```
codexapi login     Authenticate with ChatGPT and store tokens
codexapi serve     Start the OpenAI-compatible server
codexapi info      Print the currently stored account and token info
```

---

## Credits
This project was inspired by [ChatMock](https://github.com/RayBytes/ChatMock)
