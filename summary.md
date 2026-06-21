# Module 01 — Agentic RAG: Summary

The module splits into **Part 1: RAG** (lessons 1–10) and **Part 2: Agents** (lessons 11–16).

## Module map — [lessons/](lessons/)

| # | Lesson | Theme |
|---|--------|-------|
| 01–04 | Intro, Environment, RAG, Dataset | Setup & concepts |
| 05–07 | Search, Building Prompt, The LLM | RAG pieces |
| 08 | RAG Helper | Refactor into reusable files |
| 09 | Data Ingestion | Persistent index (sqlitesearch) |
| 10 | Wrap-up Part 1 | Recap + directions forward |
| 11 | Agents (intro) | Why fixed pipelines fail |
| 12 | Quick RAG Revision | Optional Part-2 setup |
| 13 | Function Calling | Giving the LLM a tool |
| 14 | The Agentic Loop | The while-loop that drives an agent |
| 15 | ToyAIKit | A minimal framework wrapping the loop |
| 16 | Other Frameworks | Production options + when *not* to use agents |

---

## 06 — Building the Prompt
The LLM can't see your documents unless you pass them in, so you build a prompt combining the user's question with the search results.

**Two-part structure:**
- **Instructions (system prompt)** — fixed text defining the LLM's role and behavior. Reused on every request.
- **User prompt** — built fresh each request, carrying the question + retrieved context.

The pieces: `INSTRUCTIONS` (answer from context, else say "I don't know" — grounds answers, reduces hallucinations), `USER_PROMPT_TEMPLATE` (with `{question}` and `{context}` placeholders), `build_context()` (turns result dicts into one formatted string of section / Q / A blocks), and `build_prompt()` (formats the final user prompt). The prompt is the bridge between search and the LLM — a bad one lets the model hallucinate, a good one keeps answers grounded.

## 07 — The LLM
The final RAG component — takes the built prompt and generates the answer.

- Uses OpenAI's **Responses API** (`responses.create`) rather than the legacy Chat Completions API. Other providers (Groq, Gemini) only expose `chat.completions`.
- Read the answer via `response.output_text` (shortcut for the deep `output[0].content[0].text`). `response.usage` reports token counts (incl. cached input).
- Cost: course uses **gpt-5.4-mini** — a typical query costs a fraction of a cent.
- **Message history**: a list of role-tagged messages (`developer` for instructions, `user` for the prompt). The LLM is stateless, so the full history must be passed each call.
- Wires up into `llm(instructions, user_prompt, model)` and `rag(query, model)`. Design is **modular** — swap search, prompt, or model independently.

## 08 — RAG Helper
Repeating the search→prompt→LLM code everywhere is wasteful, so it's refactored into two reusable files: **`ingest.py`** (`load_faq_data`, `build_index`) and **`rag_helper.py`** (a **`RAGBase`** class). A class is used because `index` and `llm_client` become constructor arguments instead of globals — so you can pass any index/client and subclass to override one piece. The `index` param is anything with a `search` method, which sets up the swap in lesson 09.

## 09 — Data Ingestion
minsearch is **in-memory** — it re-indexes on every restart, which breaks at scale. The fix: **separate ingestion from querying** into two processes sharing a persistent index. Uses **sqlitesearch** (SQLite FTS5, same API as minsearch, ships with Python). One notebook writes docs to `faq.db`; another reads/searches it concurrently. Because RAG is modular, you just **swap the index** into `RAGBase` — no RAG code changes. Same pattern scales to Elasticsearch/OpenSearch/Qdrant.

## 10 — Wrap-up of Part 1
Recap of Part 1 + two directions forward: **Agents** (Part 2) and **Vector Search** (Module 2). Also covers Elasticsearch (industry standard, BM25 + vectors + scaling) and **fine-tuning vs RAG** — RAG is cheaper, easier to update, and works with any LLM, so reach for fine-tuning only when genuinely needed.

## 11 — Agents (intro)
A fixed RAG pipeline runs search **once** with the exact query — one typo and it fails with no recovery. An **agent** hands control to the LLM, which can fix typos, search again with new terms, or ask clarifying questions. An agent = an LLM that decides which actions to take and in what order. Part 2 covers function calling, the agentic loop, and frameworks.

## 12 — Quick RAG Revision (optional)
Standalone Part-2 setup. Demonstrates the failure concretely: `rag("How do I run Ollama locally?")` works, but `"Olama"` (typo) matches nothing in lexical search — the fixed pipeline can't retry. Motivates the agent.

## 13 — Function Calling
The core mechanism. You define a `search` tool with a **JSON schema** (the `description` is what the model reads to decide when to call it). Send the question with `tools=[search_tool]`; the model returns a **`function_call`** (often rewriting your question into better keywords) instead of an answer. You execute it, append the result via `call_id`, and call the API **a second time** with the full history so the model can answer. LLMs are stateless — you resend everything. "Agentic RAG" = more round-trips = more cost.

## 14 — The Agentic Loop
One function call isn't enough when the model needs several. An **agent has three parts: Instructions, Tools, Memory** (message history). The lesson builds a `while True` loop: call model → run any function calls → append outputs → repeat until a response has **no function calls** (the exit condition). Shown recovering from the "Olama" typo on its own. Also covers steering via instructions: encouraging multiple searches and restricting off-topic questions (a lightweight guardrail). This handwritten loop is what every framework hides.

## 15 — ToyAIKit
A minimal teaching framework wrapping that exact loop (`runners` has the same `while True`). Register tools with `Tools().add_tool(search)` — with a **type hint + docstring**, it auto-generates the JSON schema (every modern framework does this). A `runner` runs the loop, tracks **cost/tokens**, and supports multi-turn via `previous_messages`. Not for production — used because it's readable.

## 16 — Other Frameworks
The concepts transfer everywhere. Surveys **OpenAI Agents SDK**, **PydanticAI** (the author's favorite — type-safe, multi-provider), **LangChain/LangGraph**, **Google ADK**, plus CrewAI/AutoGen/Semantic Kernel/Smolagents/Anthropic Tool Use. Closing wisdom: **avoid agents when you can** — they add API calls, latency, cost, and unpredictability. Try plain RAG or a single LLM call first; reach for an agent only when the simpler approach genuinely can't handle the problem.

---

**Throughline:** build RAG → make it modular/persistent → hand control to the LLM (agents) → let a framework run the loop, but don't over-reach for agents.
</content>
</invoke>
