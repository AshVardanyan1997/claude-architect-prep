# CCAR-F prep: Claude Certified Architect – Foundations

One week of prep for the exam on **Fri 2026-10-09**. The full schedule, exam facts and decision rules are in [PLAN.md](PLAN.md).

## How each day works

Every day has its own folder. Work through it top to bottom:

```
day-NN-topic/
├── README.md     ← start here: today's goal and order of work
├── lesson/       ← 1. read the notes
├── homework/     ← 2. do the build (code goes in here), 3. take the quiz
└── answers/      ← 4. check the quiz, then log misses in ../error-log.md
```

## Days

| Day | Date | Topic | Status |
|---|---|---|---|
| 1 | Fri Oct 2 | [Deployment mental model](day-01-deployment-mental-model/) | done: quiz 12/12, build reviewed |
| 2 | Sat Oct 3 | [Agentic architecture & orchestration (27%)](day-02-agentic-architecture/) | done: quiz 14/15, build reviewed |
| 3 | Sun Oct 4 | [Prompt engineering & structured output, part 1 (20%)](day-03-prompt-engineering/) | done: quiz 14/15 |
| 4 | Wed Oct 7 | [Tools & MCP (18%) + Claude Code configuration (20%)](day-04-tools-mcp-claude-code/) | ready |
| 5 | Thu Oct 8 | Prompt engineering part 2 + Claude Code in CI, error log review. Stop by evening | coming |

**Mock exam (Oct 6, claudecertificationguide.com, third-party):** 815/1000, passed. D1 13/14, D2 7/11, D3 9/12, D4 9/12, D5 11/11. The last two days were re-planned around D2 and D3.

## Other files

- [error-log.md](error-log.md): one line for every quiz miss. Day 7 is built from it.
- Builds call the real Claude API with your key. Each build folder has a `.env.example`: copy it to `.env` and put the key there. `.env` is git-ignored, so never paste the key into chat or commit it. Each build costs a few cents per run.
