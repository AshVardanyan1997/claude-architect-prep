# Day 1 quiz: Deployment & ownership (12 questions, 24 min)

Before you answer each one, picture the deployment: which runtime, which machine, which file. Then ask *which layer should own this behaviour?* Answers are in `../answers/quiz-answers.md`. Only open them once you have finished.

---

**1.** A customer support agent built with the Claude Agent SDK sometimes calls `process_refund` before confirming the customer's identity, even though the system prompt says "Always verify identity before any refund." What is the most effective fix?

- A. Move the instruction to the top of the system prompt and put it in capitals
- B. Add few-shot examples that show verification happening before refunds
- C. Add a programmatic precondition (hook) that blocks `process_refund` until `get_customer` has returned a verified customer ID
- D. Lower the temperature so the agent follows instructions more consistently

**2.** A team's Claude Code reliably follows their testing conventions, but a newly hired engineer's Claude Code ignores them in the same repository. The tech lead says they "added the conventions to CLAUDE.md months ago." What is the most likely cause and fix?

- A. The new engineer needs to run `/compact` so the conventions load
- B. The conventions are in the tech lead's user-level `~/.claude/CLAUDE.md`; move them to a project-level `CLAUDE.md` committed to the repo
- C. The conventions should be registered as an MCP resource in `.mcp.json`
- D. The new engineer should paste the conventions at the start of each session

**3.** In a multi-agent research system, the coordinator spawns a synthesis subagent with the prompt "Synthesize the research findings into a final report." The reports are generic and ignore what the web-search subagent found. What is the most likely cause?

- A. Subagents don't inherit the coordinator's context; the findings must be included explicitly in the synthesis subagent's prompt
- B. The synthesis subagent's `max_tokens` is too low
- C. The synthesis subagent needs access to the web-search tool so it can repeat the searches
- D. The `Task` tool runs subagents sequentially, so the findings aren't ready yet

**4.** A company extracts data from invoices in two ways: (1) users upload one invoice in the app and wait on screen for the extracted fields; (2) a backlog of 200,000 archived invoices needs processing for a quarterly report due in two weeks. Which API usage is best?

- A. Message Batches API for both, to cut costs by 50%
- B. Synchronous Messages API for both, for consistent behaviour
- C. Message Batches API for uploads, with a priority flag for faster results
- D. Synchronous Messages API for uploads; Message Batches API for the archive, correlating results by `custom_id`

**5.** A GitHub Actions job runs Claude Code to review pull requests. The step hangs until the job times out. What is the most likely fix?

- A. Increase the job timeout to 60 minutes
- B. Invoke Claude Code with `-p` (print / non-interactive mode) so it doesn't wait for interactive input
- C. Add `--resume` so the job continues the previous review session
- D. Move the review prompt from the workflow file into CLAUDE.md

**6.** A support agent built directly on the Claude Messages API runs as 4 replicas behind a load balancer. Where should the conversation history live?

- A. In an external session store (e.g. Redis or a database) keyed by conversation ID, loaded and re-sent with each API request
- B. Nowhere on your side: the Messages API keeps it server-side, keyed by the API key
- C. In each replica's memory, which is sufficient as long as the load balancer distributes evenly
- D. In a CLAUDE.md file the agent appends to after each turn

**7.** A team wants every developer's Claude Code to use the same GitHub MCP server. The GitHub token must not be committed to the repository. What should they do?

- A. Each developer adds the server and their token to `~/.claude.json`
- B. Add the server and a literal token to `.mcp.json`, then add `.mcp.json` to `.gitignore`
- C. Add the server to the project's `.mcp.json` and reference the token as `${GITHUB_TOKEN}`, set as an environment variable on each machine
- D. Build a custom MCP server that wraps the GitHub API with the token hard-coded server-side

**8.** A support agent has two tools, `lookup_order` ("Looks up information") and `get_customer` ("Retrieves information"). When customers ask to change their account email, the agent often calls `lookup_order`. What is the best first fix?

- A. Add a system-prompt rule: "Use get_customer for account questions"
- B. Merge both tools into a single `lookup` tool with a `type` parameter
- C. Set `tool_choice` to force `get_customer` on every turn
- D. Rewrite both tool descriptions to state each tool's purpose, inputs, example requests, and when *not* to use it

**9.** A legal-tech pipeline processes contracts in known steps: classify the contract type, extract fields with a type-specific schema, then validate. What architecture fits best?

- A. A fixed workflow: a classification call routes to a forced tool call with that type's schema, followed by validation in code
- B. An autonomous agent given all schemas as tools that decides the order of operations
- C. A coordinator that spawns one subagent per field to extract fields in parallel
- D. A single prompt that asks for JSON text, parsed with a regular expression

**10.** In long support conversations, the agent's history is progressively summarised to save context. After about 40 turns it sometimes quotes the wrong refund amount and order number. What is the best fix?

- A. Switch to a model with a larger context window
- B. Instruct the agent to re-read the whole conversation before answering
- C. Keep key transactional facts (amounts, order IDs, dates) in a structured "case facts" block that is sent verbatim with each request, outside the summarised history
- D. Stop summarising and drop the oldest turns once the context is full

**11.** A multi-agent research system is built with the Claude Agent SDK and deployed as a worker container. Where do its subagents run?

- A. Each subagent must be deployed as a separate microservice with its own container
- B. In the browser of the user who requested the report
- C. Each subagent runs on a separate CI runner
- D. Inside the worker's process, as separate conversations with their own system prompts, tools, and fresh context, spawned by the coordinator through the `Task` tool

**12.** Midway through a conversation, a customer writes, "I want to talk to a human." The agent has the tools and could probably resolve the issue itself. What should it do?

- A. Try to resolve the issue first, and escalate only if that fails
- B. Escalate immediately via `escalate_to_human`, with a structured handoff summary of the case
- C. Run sentiment analysis and escalate only if the sentiment score is below a threshold
- D. Ask clarifying questions to gather full context, then escalate
