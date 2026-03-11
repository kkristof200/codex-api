# CodexAPI

A local OpenAI-compatible API proxy that routes requests through your ChatGPT account. Drop it in front of any OpenAI-compatible client and use GPT-5 and Codex models without a direct API key.

## How it works

CodexAPI authenticates with ChatGPT via OAuth, then exposes a local HTTP server that speaks the OpenAI API format. Any tool that supports a custom base URL (Cursor, Continue, Open WebUI, LiteLLM, etc.) works out of the box.

```
Your client  ──►  CodexAPI (:8000)  ──►  chatgpt.com
(OpenAI format)   (local proxy)         (your account)
```

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

## Endpoints


| Method | Path                   | Description                        |
| ------ | ---------------------- | ---------------------------------- |
| `POST` | `/v1/chat/completions` | OpenAI-compatible chat completions |
| `POST` | `/v1/completions`      | OpenAI-compatible text completions |
| `GET`  | `/v1/models`           | List all available models          |


Both streaming (`"stream": true`) and non-streaming responses are supported.

---

## Setup

There are three ways to run CodexAPI depending on your use case.

### Option A — Install as a CLI tool (recommended for local use)

**Prerequisites:** Python 3.13+, a ChatGPT account (Plus, Pro, Team, or Enterprise)

**1. Install**

Clone the repo and install with uv (recommended):

```bash
git clone https://github.com/you/codex-api
cd codex-api
pip install uv
uv sync
```

Or install only the server package with pip:

```bash
pip install ./packages/codexapi-server
```

**2. Login**

```bash
codexapi login
```

This opens your browser for ChatGPT OAuth. On a headless machine use `--no-browser` — it will print an authorization URL, and after you complete login in any browser, paste the redirect URL back into the terminal:

```bash
codexapi login --no-browser
```

**3. Serve**

```bash
codexapi serve
```


| Flag                  | Env var                           | Default     | Description                        |
| --------------------- | --------------------------------- | ----------- | ---------------------------------- |
| `--host`              | —                                 | `127.0.0.1` | Bind address                       |
| `--port`              | `PORT`                            | `8000`      | Port                               |
| `--reasoning-summary` | `CHATGPT_LOCAL_REASONING_SUMMARY` | `auto`      | `auto` `concise` `detailed` `none` |
| `--enable-web-search` | `CHATGPT_LOCAL_ENABLE_WEB_SEARCH` | `false`     | Enable web search by default       |


---

### Option B — Docker

**Prerequisites:** Docker, Docker Compose, a ChatGPT account

**1. Configure**

Copy `.env.example` to `.env` and adjust as needed:

```bash
cp .env.example .env
```


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

Your browser will open (or a URL will be printed). Complete login, then the container exits automatically and tokens are saved to a persistent Docker volume.

> On some systems the browser redirect may not reach the container. If that happens, copy the redirect URL from your browser's address bar and paste it into the terminal when prompted.

**3. Serve**

```bash
docker compose up --build serve
```

The server is available at `http://localhost:8000`.

**Re-authenticate** (when the token expires):

```bash
docker compose --profile login run --rm --build --service-ports login
```

---

### Option C — Use the client library only

If you only need to make requests programmatically without the server:

```bash
pip install ./packages/codexapi-client
# or from GitHub:
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
    messages=[{"type": "message", "role": "user", "content": [{"type": "input_text", "text": "Hello!"}]}],
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

## CLI reference

```
codexapi login     Authenticate with ChatGPT and store tokens
codexapi serve     Start the OpenAI-compatible server
codexapi info      Print the currently stored account and token info
```

## License

MIT