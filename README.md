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
| 1 | Fri Oct 2 | [Deployment mental model](day-01-deployment-mental-model/) | ready |
| 2 | Sat Oct 3 | Agentic architecture & orchestration (27%) | coming |
| 3 | Sun Oct 4 | Prompt engineering & structured output, part 1 (20%) | coming |
| 4 | Mon Oct 5 | Prompt engineering part 2, batch, Claude Code in CI | coming |
| 5 | Tue Oct 6 | Claude Code configuration (20%) + tools & MCP (18%) | coming |
| 6 | Wed Oct 7 | Context & reliability (15%) + timed 60-question mock | coming |
| 7 | Thu Oct 8 | Review the error log, targeted drills, cheat sheet | coming |

## Other files

- [error-log.md](error-log.md): one line for every quiz miss. Day 7 is built from it.
- Builds call the real Claude API with your key. Each build folder has a `.env.example`: copy it to `.env` and put the key there. `.env` is git-ignored, so never paste the key into chat or commit it. Each build costs a few cents per run.
