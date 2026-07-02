# interactive-text-game

An autonomous multi-agent system that designs, codes, playtests, and self-corrects a text-adventure puzzle game with no human in the loop.

This project demonstrates stateful multi-agent orchestration using LangGraph. It uses specialized agents coordinated by a graph-based orchestrator that routes work dynamically based on live execution results, rather than following a fixed, linear script.

---

## What it does

You provide a basic theme like this:

python main.py --theme "haunted lab escape"

The pipeline then handles the rest automatically:

1. **Design:** It maps out a puzzle including rooms, items, and win conditions as structured data.
2. **Code:** It writes a complete, playable Python implementation matching that design.
3. **Execute:** It runs the generated code inside an isolated Docker sandbox.
4. **Playtest:** It deploys an agent to act as a player and try to actually solve the puzzle it just built.
5. **Critique:** If the puzzle turns out to be unsolvable or the code crashes, a critic diagnoses whether it was an implementation bug or a flawed design concept, then routes it back to the right agent for a fix.
6. **Repeat:** It iterates until it produces a verified, fully working game or hits its retry limit.

The final output is a real, playable text adventure game in the style of classics like Zork, built and verified entirely by the pipeline.

The full design rationale, state schema, and routing logic can be found in docs/design_doc.md.

---

## Why this project

Most AI agent portfolio projects are just a single prompt call wrapped in a chat UI. This project was built to tackle the more realistic challenges of building agentic systems:

* **Stateful graph orchestration:** The control flow branches and loops based on real-time data using conditional edges rather than a rigid, linear sequence.
* **True self-correction loops:** A critic node identifies exactly why something failed (bad code versus a broken design concept) and sends it back to the specific agent responsible, rather than blindly retrying the same step.
* **Sandboxed code execution:** Because the generated code is untrusted, it runs in an isolated, resource-limited Docker container with no network access and a hard timeout.
* **Realistic scoping:** The project is deliberately built to run entirely on free-tier tooling to prove what can be done under strict constraints.

This architecture mirrors the patterns used by autonomous coding tools like Devin or Cursor's agent mode, applied to a safe, self-contained playground.

---

## Architecture Flow

The workflow below illustrates how the orchestrator dynamically routes tasks based on evaluation metrics:

```
                  [ User Input: Theme ]
                            │
                            ▼
                  ┌───────────────────┐
                  │   Orchestrator    │◄──────────────┐
                  │   (LangGraph)     │                │
                  └─────────┬─────────┘                │
                            │                            │
                            ▼                            │
                  ┌──────────────────┐                  │
                  │  Designer Agent   │                  │
                  │ (theme → puzzle   │                  │
                  │  spec as JSON)    │                  │
                  └────────┬─────────┘                  │
                            ▼                            │
                  ┌──────────────────┐                  │
                  │   Code Agent      │                  │
                  │ (spec → Python    │                  │
                  │  game code)       │                  │
                  └────────┬─────────┘                  │
                            ▼                            │
                  ┌──────────────────┐                  │
                  │ Sandbox Executor  │                  │
                  │ (Docker: run the  │                  │
                  │  generated game)  │                  │
                  └────────┬─────────┘                  │
                            ▼                            │
                  ┌──────────────────┐                  │
                  │ Playtester Agent  │                  │
                  │ (tries to solve   │                  │
                  │  the puzzle)      │                  │
                  └────────┬─────────┘                  │
                            ▼                            │
                  ┌──────────────────┐                  │
                  │   Critic Node     │                  │
                  │ (pass? fail? why?)│                  │
                  └────────┬─────────┘                  │
                ┌───────────┼───────────────┐            │
          Fail: bad code            Fail: bad design      │
          → retry Code Agent        → retry Designer ─────┘
                            │
                      Pass  │
                            ▼
                  ┌──────────────────┐
                  │  Final Output     │
                  │ (playable game +  │
                  │  attempt log)     │
                  └──────────────────┘

```

---

## Tech stack

* **Orchestration:** LangGraph was chosen for its graph-based state machine capabilities, conditional routing, and native support for loops.
* **LLM:** Gemini free tier handles structured generation and provides the necessary reasoning for generating specifications and code at no cost.
* **Sandbox:** Docker handles standard isolation for running the untrusted, automated code.
* **Language:** Python 3.11 or higher runs both the LangGraph workflow and the underlying game engine.

The system relies entirely on free tooling, eliminating API costs and cloud hosting expenses. Text-based design choices keep token costs minimal compared to graphical engines, allowing the focus to remain purely on orchestration logic.

---

## Project structure

The directory structure breaks down into these distinct functional modules:

```text
interactive-text-game/
├── src/
│   ├── engine/          # Core game engine logic (State machine, commands) — [No AI Dependency]
│   ├── agents/          # Individual specialized agent prompting & runtime (Designer, Code, Tester)
│   ├── graph/           # LangGraph workflows, state definitions, and dynamic routing
│   └── sandbox/         # Docker client controllers, constraints, and execution handlers
├── tests/                # System unit tests for verification of engine & graph logic
├── generated_games/      # Pipeline outputs containing completely playable verified text games
├── docs/                 # Architectural deep-dives and design specifications
├── .env.example          # Template file for local environmental variable setup
├── requirements.txt      # Python package dependencies
└── README.md             # Project overview

```

---

## Setup

First, clone the repository and navigate into the project directory:

git clone URL
cd interactive-text-game

Set up and activate a virtual environment:

For Windows:
python -m venv venv
venv\Scripts\activate

For macOS and Linux:
python3 -m venv venv
source venv/bin/activate

Install the required dependencies:

pip install -r requirements.txt

Copy the example environment file to create your local configurations:

cp .env.example .env

Open the newly created .env file and add your free Gemini API key to the GOOGLE_API_KEY variable.

Ensure Docker Desktop is installed and running on your machine, as it is required to execute the sandboxed game code. Once ready, run the generator with your chosen theme:

python main.py --theme "your theme here"

---

## Design decisions

* **Separate retry counters:** A crashing script and an impossible puzzle layout are two entirely separate issues. Splitting the retry tracking ensures the system can differentiate between patching an implementation bug and throwing out a broken concept.
* **Text over graphics:** Keeping the format text-based keeps token usage near zero, allowing the system to iterate frequently on a free API tier while focusing on core engineering challenges rather than asset generation.
* **Targeted playtesting:** The playtester agent attempts to verify the designer's intended solution path first rather than brute-forcing every single action combination. This saves significant API costs while keeping verification reliable.
* **Strict sandbox rules:** The execution container runs with no network access, strict memory caps, a hard timeout, and no external package installation to ensure untrusted code cannot harm the host system.

---

## Status

The project is currently in active development. The system design and architecture are complete, while the remaining milestones are being built out sequentially:

* Completed system design and architecture
* In progress building the core game engine framework
* Planned implementation of the designer agent
* Planned implementation of the code agent and sandbox executor
* Planned implementation of the playtester and critic loop
* Planned integration of the full orchestrator graph
