# temporal-ai-agent

Temporal AI Agent



### Tool Configuration

### LLM Provider Configuration

The agent can use OpenAI's GPT-4o, Google Gemini, Anthropic Claude, or a local LLM via Ollama. Set the `LLM_PROVIDER` environment variable in your `.env` file to choose the desired provider:

- `LLM_PROVIDER=openai` for OpenAI's GPT-4o
- `LLM_PROVIDER=google` for Google Gemini
- `LLM_PROVIDER=anthropic` for Anthropic Claude
- `LLM_PROVIDER=deepseek` for DeepSeek-V3
- `LLM_PROVIDER=ollama` for running LLMs via [Ollama](https://ollama.ai) (not recommended for this use case)

### Option 1: OpenAI

If using OpenAI, ensure you have an OpenAI key for the GPT-4o model. Set this in the `OPENAI_API_KEY` environment variable in `.env`.

### Option 2: Google Gemini

To use Google Gemini:

1. Obtain a Google API key and set it in the `GOOGLE_API_KEY` environment variable in `.env`.
2. Set `LLM_PROVIDER=google` in your `.env` file.

### Option 3: Anthropic Claude (recommended)

I find that Claude Sonnet 3.5 performs better than the other hosted LLMs for this use case.

To use Anthropic:

1. Obtain an Anthropic API key and set it in the `ANTHROPIC_API_KEY` environment variable in `.env`.
2. Set `LLM_PROVIDER=anthropic` in your `.env` file.

### Option 4: Deepseek-V3

To use Deepseek-V3:

1. Obtain a Deepseek API key and set it in the `DEEPSEEK_API_KEY` environment variable in `.env`.
2. Set `LLM_PROVIDER=deepseek` in your `.env` file.

### Option 5: Local LLM via Ollama (not recommended)

To use a local LLM with Ollama:

1. Install [Ollama](https://ollama.com) and the [Qwen2.5 14B](https://ollama.com/library/qwen2.5) model.
   - Run `ollama run <OLLAMA_MODEL_NAME>` to start the model. Note that this model is about 9GB to download.
   - Example: `ollama run qwen2.5:14b`

2. Set `LLM_PROVIDER=ollama` in your `.env` file and `OLLAMA_MODEL_NAME` to the name of the model you installed.

Note: I found the other (hosted) LLMs to be MUCH more reliable for this use case. However, you can switch to Ollama if desired, and choose a suitably large model if your computer has the resources.


## Running the Application

### React UI
Start the frontend:
```bash
cd frontend
npm install
npx vite
```
Access the UI at `http://localhost:5173`

