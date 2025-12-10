# Advance Care Planning Agent

## Recent Updates

### Conversation Memory System
The bot now includes conversation history functionality that allows it to maintain context across multiple interactions. Each user's conversation is tracked separately and the system can reference previous exchanges to provide more coherent and contextual responses.

**New Features:**
- Persistent conversation tracking per user
- Context-aware responses using conversation history
- Commands to manage conversation history (clear, show history)
- Enhanced prompt engineering for better contextual understanding

## Environment

Please install [uv](https://docs.astral.sh/uv/getting-started/installation/), a Python package and project manager.

after that, `uv sync` to update the environment and `uv run main.py` to run the app (if all backend setting is done).

## Miscellaneous points

Documents should probably be stored in AWS or something in the future. Folder for it for now.

Currently just some random information in the documents.

Currently uses ollama as this is free

## Running RAG
The process is a bit long, but won't be needed if we switch to OpenAI (though it's currently free, OpenAI API will cost)

Ollama is needed (at least before we switch to OpenAI), can be downloaded at <a href="https://ollama.com/download" target="_blank">https://ollama.com/download</a>

Next, you need to pull the embedding model with:

```
ollama pull mxbai-embed-large
```

and the chat model with

```
ollama pull llama3
```

To run RAG.py, you need to serve it. Call

```
ollama serve
```

in a separate terminal (make sure to exit the ollama program as this will occupe the port otherwise)
You can then run LLM normally