\# GameSmith



\*\*An autonomous multi-agent system that designs, codes, playtests, and self-corrects a text-adventure puzzle game — with no human in the loop.\*\*



Built to demonstrate stateful multi-agent orchestration using LangGraph: specialized agents coordinated by a graph-based orchestrator that routes work dynamically based on live execution results, not a fixed script.



\---



\## What it does



Give it a theme:

```bash

python main.py --theme "haunted lab escape"

```



It will:

1\. \*\*Design\*\* a puzzle (rooms, items, win condition) as structured data

2\. \*\*Code\*\* a playable implementation of that design

3\. \*\*Execute\*\* the generated code inside an isolated Docker sandbox

4\. \*\*Playtest\*\* it — attempt to actually solve the puzzle it just built

5\. \*\*Critique\*\* the result — if the puzzle is unsolvable or the code crashes, diagnose \*why\* and route back to the right agent to fix it (bad code → recode; bad puzzle concept → redesign)

6\. Repeat until it produces a verified-solvable game, or exhausts its retry budget and reports what went wrong



The output is a real, playable text adventure — the kind of game format popularized by \*Zork\* and \*Colossal Cave Adventure\* — generated and verified entirely by the agent pipeline.



\## Why this project



Most "AI agent" portfolio projects are a single LLM call wrapped in a chat UI. This project is built to demonstrate the harder, more realistic parts of agentic systems:



\- \*\*Stateful graph orchestration\*\*, not a linear chain — the control flow branches and loops based on data, using LangGraph's conditional edges

\- \*\*A real self-correction loop\*\* — a critic node that distinguishes \*why\* something failed (implementation bug vs. flawed design) and routes to a different agent accordingly, rather than blindly retrying the same step

\- \*\*Sandboxed, untrusted code execution\*\* — LLM-generated code runs in an isolated, resource-limited Docker container with no network access and a hard timeout

\- \*\*Honest scoping under constraints\*\* — built entirely on free-tier tooling (see \[Design Decisions](#design-decisions))



This mirrors the architecture pattern used by autonomous coding agents (e.g. Cognition's Devin, Cursor's agent mode) — applied here to a safer, self-contained domain instead of live production codebases.



\## Architecture



```

&#x20;                       \[ User Input: Theme ]

&#x20;                               │

&#x20;                               ▼

&#x20;                     ┌───────────────────┐

&#x20;                     │   Orchestrator    │◄──────────────┐

&#x20;                     │   (LangGraph)     │                │

&#x20;                     └─────────┬─────────┘                │

&#x20;                               │                            │

&#x20;                               ▼                            │

&#x20;                     ┌──────────────────┐                  │

&#x20;                     │  Designer Agent   │                  │

&#x20;                     │ (theme → puzzle   │                  │

&#x20;                     │  spec as JSON)    │                  │

&#x20;                     └────────┬─────────┘                  │

&#x20;                               ▼                            │

&#x20;                     ┌──────────────────┐                  │

&#x20;                     │   Code Agent      │                  │

&#x20;                     │ (spec → Python    │                  │

&#x20;                     │  game code)       │                  │

&#x20;                     └────────┬─────────┘                  │

&#x20;                               ▼                            │

&#x20;                     ┌──────────────────┐                  │

&#x20;                     │ Sandbox Executor  │                  │

&#x20;                     │ (Docker: run the  │                  │

&#x20;                     │  generated game)  │                  │

&#x20;                     └────────┬─────────┘                  │

&#x20;                               ▼                            │

&#x20;                     ┌──────────────────┐                  │

&#x20;                     │ Playtester Agent  │                  │

&#x20;                     │ (tries to solve   │                  │

&#x20;                     │  the puzzle)      │                  │

&#x20;                     └────────┬─────────┘                  │

&#x20;                               ▼                            │

&#x20;                     ┌──────────────────┐                  │

&#x20;                     │   Critic Node     │                  │

&#x20;                     │ (pass? fail? why?)│                  │

&#x20;                     └────────┬─────────┘                  │

&#x20;                   ┌───────────┼───────────────┐            │

&#x20;             Fail: bad code            Fail: bad design      │

&#x20;             → retry Code Agent        → retry Designer ─────┘

&#x20;                               │

&#x20;                         Pass  │

&#x20;                               ▼

&#x20;                     ┌──────────────────┐

&#x20;                     │  Final Output     │

&#x20;                     │ (playable game +  │

&#x20;                     │  attempt log)     │

&#x20;                     └──────────────────┘

```



Full design rationale, state schema, and routing logic: \[`docs/design\_doc.md`](docs/design\_doc.md)



\## Tech stack



| Component | Choice | Why |

|---|---|---|

| Orchestration | \[LangGraph](https://github.com/langchain-ai/langgraph) | Graph-based state machine with conditional routing and native loop support |

| LLM | Gemini (free tier) | No-cost structured generation, sufficient reasoning for spec/code generation |

| Sandbox | Docker | Industry-standard isolation for untrusted, LLM-generated code |

| Language | Python 3.11+ | Native to LangGraph and the game engine |



\*\*Built entirely on free tooling\*\* — no paid API usage, no cloud hosting costs. See \[Design Decisions](#design-decisions) for the reasoning (e.g. why text-based over graphical).



\## Project structure



```

gamesmith/

├── src/

│   ├── engine/          # Core game engine (rooms, items, state, commands) — no AI

│   ├── agents/          # Designer, Code, Playtester agent implementations

│   ├── graph/           # LangGraph state schema, node wiring, conditional edges

│   └── sandbox/         # Docker execution + safety constraints

├── tests/                # Unit tests for engine + agent logic

├── generated\_games/      # Output: playable games produced by the pipeline

├── docs/

│   └── design\_doc.md     # Full architecture + design rationale

├── .env.example           # Required environment variables (no real keys)

├── requirements.txt

└── README.md

```



\## Setup



```bash

git clone <repo-url>

cd gamesmith

python -m venv venv

venv\\Scripts\\activate        # Windows

pip install -r requirements.txt

```



Copy `.env.example` to `.env` and add your own free \[Gemini API key](https://aistudio.google.com/apikey):

```

GOOGLE\_API\_KEY=your\_key\_here

```



Docker Desktop must be installed and running (used for sandboxed code execution).



```bash

python main.py --theme "your theme here"

```



\## Design decisions



A few choices worth calling out explicitly, since they were deliberate tradeoffs rather than defaults:



\- \*\*Separate retry counters for code failures vs. design failures.\*\* A crashing implementation and an unsolvable puzzle concept require different fixes — conflating them into one retry counter would mean the system can't tell "patch the code" from "the idea itself is broken."

\- \*\*Text-based, not graphical.\*\* Keeps token cost per state near-zero (a room description is a few hundred tokens; sprite/position state would multiply that), and keeps the project's focus on orchestration logic rather than asset generation.

\- \*\*Playtester verifies the Designer's intended solution path first\*\*, rather than brute-forcing every possible action combination — brute-force is more thorough but far more expensive on a free API tier. Full brute-force verification is a documented stretch goal, not a cut corner.

\- \*\*Sandbox constraints:\*\* no network access inside the container, hard execution timeout, memory cap, and no arbitrary package installation — since the code being run is LLM-generated and untrusted by default.



\## Status



🚧 In active development. See \[`docs/design\_doc.md`](docs/design\_doc.md) for the full build roadmap.



\- \[x] System design and architecture

\- \[ ] Core game engine (Stage 1)

\- \[ ] Designer agent (Stage 2)

\- \[ ] Code agent + sandbox executor (Stage 3)

\- \[ ] Playtester + critic loop (Stage 4)

\- \[ ] Full orchestrator graph (Stage 5)

