# Hermes Dev Assistant

A **Developer Productivity Assistant** built on the [Hermes Agent](https://github.com/NousResearch/hermes-agent) framework. It monitors GitHub issues, summarizes daily code activity, drafts standup reports, tracks tasks via Notion, and responds through **Telegram**.

## Architecture

```
Telegram Message (User)
        ↓
   main.py (Telegram Bot)
        ↓
   DevWorkflow Router
        ↓
┌───────────────┬────────────────┬──────────────────┐
│  GitHub       │   Planning     │    Report        │
│  Agent        │   Agent        │    Agent         │
└───────┬───────┴───────┬────────┴────────┬─────────┘
        ↓               ↓                 ↓
┌───────────────┬────────────────┬──────────────────┐
│ GitHub        │  Standup       │  Task Extraction │
│ Summary Skill │  Skill         │  Skill           │
└───────┬───────┴───────┬────────┴────────┬─────────┘
        ↓               ↓                 ↓
┌───────────────┬────────────────┬──────────────────┐
│  GitHub API   │  Notion API    │  LLM (OpenAI/    │
│  (PyGithub)   │  (notion-client│  Qwen)           │
└───────────────┴────────────────┴──────────────────┘
        ↓                                  ↓
   Memory (SQLite)              Observability (JSONL)
```

## Features

| Component | Description |
|-----------|-------------|
| **3 Agents** | GitHub Agent, Planning Agent, Report Agent |
| **3 Skills** | GitHub Summary, Standup Draft, Task Extraction |
| **2 Tools** | GitHub API (PyGithub), Notion API (notion-client) |
| **Channel** | Telegram Bot with commands + natural language |
| **Memory** | SQLite-based user preference persistence |
| **Observability** | Structured JSONL logging of all agent activity |

## Setup Instructions

### Prerequisites

- Python 3.10+
- A Telegram account
- GitHub Personal Access Token
- Notion Integration + Database
- OpenAI API key (and/or OpenRouter for Qwen)

### Step 1: Clone & Install

```bash
git clone https://github.com/your-username/hermes-dev-assistant.git
cd hermes-dev-assistant
make setup
# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### Step 3: Create Telegram Bot

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`, follow prompts
3. Copy the Bot Token into `.env` as `TELEGRAM_BOT_TOKEN`
4. Get your user ID from `@userinfobot` and add to `config/channels.yaml`

### Step 4: Set Up Notion

1. Create a [Notion Integration](https://www.notion.so/my-integrations)
2. Create a database with properties: `Name` (title), `Status` (select: To Do/In Progress/Done)
3. Share the database with your integration
4. Copy the API key and database ID into `.env`

### Step 5: Set Up GitHub Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Create a token with `repo` scope
3. Copy into `.env` as `GITHUB_TOKEN`

### Step 6: Run

```bash
make run
# Or: source venv/bin/activate && python main.py
```

Send `/start` to your Telegram bot to verify it's working.

## Agents

| Agent | File | Responsibility |
|-------|------|---------------|
| GitHub Agent | `agents/github_agent.py` | Fetches open issues, PRs, and commit summaries from GitHub |
| Planning Agent | `agents/planning_agent.py` | Converts task lists into structured daily/weekly plans with P1/P2/P3 priorities |
| Report Agent | `agents/report_agent.py` | Drafts standup reports (Yesterday/Today/Blockers) and saves to markdown files |

## Skills

| Skill | File | Trigger Phrases | Input → Output |
|-------|------|----------------|----------------|
| GitHub Summary | `skills/github_summary_skill.py` | "github issues", "open issues" | List of issues → Concise markdown summary |
| Standup Draft | `skills/standup_skill.py` | "standup", "daily report" | Activity data → Yesterday/Today/Blockers format |
| Task Extraction | `skills/task_extraction_skill.py` | "extract tasks", "meeting notes" | Raw text → Numbered task list |

## Telegram Commands

| Command | Action |
|---------|--------|
| `/start` | Welcome message with instructions |
| `/standup` | Generate daily standup report |
| `/issues` | Summarize open GitHub issues |
| `/tasks` | List Notion tasks |
| `/plan` | Create prioritized daily plan |
| `/weekly` | Generate weekly summary |
| `/addtask <title>` | Add task to Notion |
| `/setrepo owner/repo` | Set default GitHub repository |

## Model Comparison

Tested with 5 identical prompts (standup generation, issue summary, task extraction, planning, general Q&A):

| Criteria | GPT-4o-mini (OpenAI) | Qwen 2.5 72B (OpenRouter) |
|----------|---------------------|--------------------------|
| **Setup** | Simple — just API key | Requires OpenRouter or local setup |
| **Speed** | ~1.2s avg response | ~2.5s avg response |
| **Response Quality** | Excellent formatting, concise | Good quality, slightly more verbose |
| **Tool Use Accuracy** | 5/5 correct routing | 4/5 correct routing |
| **Cost** | ~$0.15/1K requests | ~$0.10/1K requests (via OpenRouter) |
| **Standup Format** | Correct Yesterday/Today/Blockers 5/5 | Correct format 4/5 |
| **Notes** | Best for production use | Good budget alternative |

### Key Observations

- **GPT-4o-mini** consistently produced the standup in the correct Yesterday/Today/Blockers format (5/5 times) vs Qwen's 4/5
- **Qwen 2.5** was more cost-effective but occasionally deviated from the strict output format
- Both models handled task extraction equally well
- GPT-4o-mini was ~2x faster in response latency

## Project Structure

```
hermes-dev-assistant/
├── agents/
│   ├── __init__.py
│   ├── github_agent.py        # GitHub API interactions
│   ├── planning_agent.py      # Task prioritization
│   └── report_agent.py        # Report generation
├── skills/
│   ├── __init__.py
│   ├── github_summary_skill.py
│   ├── standup_skill.py
│   └── task_extraction_skill.py
├── tools/
│   ├── __init__.py
│   ├── github_tool.py         # PyGithub wrapper
│   ├── notion_tool.py         # Notion API wrapper
│   └── llm_client.py          # Unified LLM interface
├── workflows/
│   ├── __init__.py
│   └── dev_workflow.py        # Main message router
├── memory/
│   ├── __init__.py
│   └── user_memory.py         # SQLite preferences store
├── observability/
│   ├── __init__.py
│   └── logger.py              # JSONL structured logger
├── config/
│   ├── channels.yaml          # Telegram channel config
│   └── model.yaml             # LLM model configuration
├── tests/
│   ├── test_skills.py
│   ├── test_memory.py
│   └── test_logger.py
├── reports/                   # Generated reports (gitignored)
├── logs/                      # Activity logs (gitignored)
├── .env.example               # Template for environment vars
├── .gitignore
├── main.py                    # Entry point — Telegram bot
├── requirements.txt
├── Makefile
└── README.md
```

## Bonus Features

### 1. Memory (Long-term User Preferences)

SQLite-based persistent storage in `memory/user_memory.py`:
- Remembers default GitHub repository across sessions
- Stores user preferences (standup format, working hours)
- Survives bot restarts

```python
# Example: after user sets repo once, it's remembered
workflow.handle("set repo NousResearch/hermes-agent")
# Future requests automatically use this repo
```

### 2. Observability (Structured Logging)

JSONL logger in `observability/logger.py`:
- Records every agent/skill invocation
- Tracks latency, model used, input/output lengths
- Output: `logs/agent_activity.jsonl`

Sample log entry:
```json
{
  "timestamp": "2026-06-20T10:30:00.000Z",
  "agent": "report_agent",
  "skill": "report_generation",
  "tool": "llm",
  "model": "gpt-4o-mini",
  "input_length": 45,
  "output_length": 312,
  "latency_ms": 1250
}
```

## Running Tests

```bash
make test
# Or: python -m pytest tests/ -v
```

Tests use mocked LLM and API clients — no live credentials needed.

## Reflection

### What Worked Well
- The keyword-based routing in `DevWorkflow` is simple but effective for a developer audience that uses predictable terminology
- SQLite memory enables a natural conversational flow (set repo once, never repeat)
- JSONL logging made it easy to compare model performance quantitatively
- Telegram's Bot API + python-telegram-bot made the channel integration straightforward

### What Was Challenging
- Hermes Agent's internal structure is complex; deciding where to add custom logic vs. use built-in features required careful exploration
- Notion's API has inconsistent property access patterns depending on property type
- Rate limiting on GitHub API required adding the `[:10]` limits

### What I'd Improve
- Replace keyword routing with semantic intent classification using embeddings
- Add conversation context (multi-turn memory) beyond just preferences
- Implement webhook mode for Telegram (instead of polling) for production
- Add GitHub webhook integration for real-time issue notifications
- Build a dashboard from the JSONL logs for visual observability

## License

MIT