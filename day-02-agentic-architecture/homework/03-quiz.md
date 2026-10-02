# Day 2 quiz: Agentic architecture (15 questions, 30 min)

Three of these are **multiple-response**, like on the real exam: the question says how many to pick, and you need all of them right to score it. Answers are in `../answers/quiz-answers.md`. Log misses in `../../error-log.md`.

---

**1.** Your agent loop ends when the assistant's text contains "Task complete." In production, some runs stop before the requested file is written, and others keep calling tools after saying they're finished. What should the loop use to decide whether to continue?

- A. A stricter phrase, such as "FINAL ANSWER:", that the system prompt requires at the end
- B. A maximum of 8 iterations, after which the loop returns whatever it has
- C. The response's `stop_reason`: continue while it is `"tool_use"`, finish on `"end_turn"`
- D. Whether the response contains any text block

**2. (Select TWO.)** Which of these are anti-patterns for deciding when an agentic loop terminates?

- A. Checking whether the assistant response contains text content as the completion signal
- B. Appending tool results to the conversation before the next request
- C. Using an arbitrary iteration cap as the primary stopping mechanism
- D. Continuing while `stop_reason` is `"tool_use"`
- E. Returning every tool result from one response in a single user message

**3.** A research coordinator reliably produces well-cited reports, but for "renewable energy policy" the reports cover only solar and wind. The logs show three subtasks: "solar subsidies", "wind farm permitting", "rooftop solar adoption". Every subagent completed its task correctly. What is the root cause?

- A. The search subagent's queries are too narrow
- B. The synthesis subagent drops findings it considers off-topic
- C. The coordinator's task decomposition is too narrow for the topic
- D. The subagents need a larger context window

**4.** A coordinator always runs search → analysis → synthesis, even for simple factual questions that one search answers. Latency and cost are high. What is the best improvement?

- A. Have the coordinator analyse each query and invoke only the subagents it needs
- B. Merge the three subagents into one agent with all the tools
- C. Cache the synthesis output for repeated questions
- D. Switch every subagent to a smaller model

**5.** You configure a coordinator with three `AgentDefinition`s, but it never spawns any subagents and tries to do all the work itself. What is the most likely cause?

- A. The subagent descriptions are too short
- B. The coordinator's `allowedTools` doesn't include `"Task"`
- C. The subagents' system prompts are missing
- D. `fork_session` isn't enabled

**6.** The coordinator delegates three independent searches. The logs show one `Task` call per coordinator turn, across three turns, and each waits for the previous one. How do you make them run in parallel?

- A. Run three separate coordinators, one per search
- B. Have the coordinator emit all three `Task` calls in a single response
- C. Give each subagent a shorter system prompt
- D. Use the Message Batches API for the searches

**7. (Select TWO.)** You're delegating report writing to a synthesis subagent. What should its prompt include so it can produce an accurate, cited report?

- A. The complete findings returned by the search and analysis subagents
- B. Nothing extra, because subagents inherit the coordinator's conversation history
- C. Findings in a structured format that keeps each claim with its source, document name and date
- D. Only the original user question, so the subagent can do its own research
- E. A summary of the findings with the source references removed to save tokens

**8.** A team's coordinator prompt is a 40-line numbered procedure ("1. Search X. 2. Then search Y…"). It works for the topics the team tested, but adapts poorly to new ones. What does the exam guide recommend?

- A. Add more numbered steps to cover more topics
- B. Write the coordinator prompt as research goals and quality criteria, so subagents and the coordinator can adapt
- C. Move the procedure into a hook so it's enforced deterministically
- D. Split the coordinator into one coordinator per topic

**9.** A customer writes: "Refund order 1182, change my shipping address, and explain why I was charged twice in May." What's the best way for the support agent to handle this?

- A. Handle the first request, then ask the customer to submit the others separately
- B. Escalate, because the message has several concerns
- C. Decompose it into three items, investigate each (in parallel where independent) using shared context, then give one unified reply
- D. Answer only the billing question, since it's the most complex

**10.** Three MCP tools return dates in different formats: a Unix timestamp, ISO 8601 and "05/04/26". The agent sometimes misreads them. What's the most reliable fix?

- A. Add a system-prompt instruction explaining each format
- B. A `PostToolUse` hook that normalises every date to ISO 8601 before the model sees the result
- C. Few-shot examples of reading each date format
- D. Ask the tool owners to change their APIs

**11.** You're asked to "add comprehensive tests to a large legacy codebase" with Claude. Which decomposition fits best?

- A. A fixed prompt chain: generate tests for each file in alphabetical order
- B. One request with the whole codebase that asks for all tests at once
- C. Dynamic decomposition: map the structure, identify high-impact areas, then follow a prioritised plan that adapts as dependencies are discovered
- D. One subagent per file, all running in parallel with no coordination

**12.** Yesterday you investigated an auth bug in a named Claude Code session. Overnight, teammates changed 3 of the 40 files you analysed. What's the most efficient way to continue?

- A. Resume the session and tell it exactly which files changed so it re-analyses only those
- B. Resume the session without comment; it will notice the changes
- C. Start over and re-explore all 40 files
- D. Fork the session and continue in the fork

**13. (Select TWO.)** When is starting a **new** session with an injected structured summary better than resuming the old session?

- A. When most of the old session's tool results are now stale because the code changed substantially
- B. When the earlier context is still almost entirely valid
- C. When the old session's context is cluttered with outdated findings that could mislead the agent
- D. Whenever the old session is more than an hour old
- E. When you want to compare two approaches from the same starting point

**14.** In a research system, the synthesis agent often needs quick fact checks (dates, names, numbers). Each check currently goes synthesis → coordinator → search agent → coordinator → synthesis, which adds 40% latency. 85% of the checks are simple lookups. What's the best design?

- A. Give the synthesis agent all of the search agent's tools
- B. Give the synthesis agent a narrowly scoped `verify_fact` tool for simple lookups, and keep complex checks going through the coordinator
- C. Have the synthesis agent batch all checks to the end of its pass
- D. Have the search agent cache extra context for every source

**15.** A document-analysis subagent hits a timeout on one of five sources. How should the failure reach the coordinator?

- A. Retry forever inside the subagent until the source responds
- B. Return the four successful analyses as a complete result and don't mention the failure
- C. Return a structured error with the failure type, what was attempted, the partial results, and possible alternatives, so the coordinator can decide what to do
- D. Raise an exception that terminates the whole research workflow
