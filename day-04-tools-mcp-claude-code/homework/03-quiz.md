# Day 4 quiz: Tools & MCP + Claude Code configuration (15 questions, 30 min)

Three questions are **multiple-response**: the question says how many to pick, and you need all of them right to score it. Answers are in `../answers/quiz-answers.md`. Log misses in `../../error-log.md`.

---

**1.** A team's Claude Code follows the team's API conventions for the lead developer, but not for a new hire who cloned the same repo yesterday. What's the most likely cause?

- A. The new hire's Claude Code version is older
- B. The conventions are in a `.claude/rules/` file without a `paths:` field
- C. The conventions are in the lead developer's `~/.claude/CLAUDE.md`, which isn't shared through version control
- D. The project CLAUDE.md is too long, so the new hire's sessions truncate it

**2.** Test files live next to their source files in 30 different folders. You want test conventions loaded whenever Claude edits a test file, and not otherwise. What's the best approach?

- A. A `.claude/rules/testing.md` file with `paths: ["**/*.test.*"]` in its frontmatter
- B. A CLAUDE.md file in each of the 30 folders containing the test conventions
- C. The test conventions in the root CLAUDE.md, under a "Testing" heading
- D. A `/test-conventions` command that developers run before editing tests

**3.** A project skill that analyses the whole codebase produces several thousand lines of output. After running it, developers find their conversation cluttered and Claude loses track of earlier context. What should you change?

- A. Add `allowed-tools: Read` to the skill's frontmatter
- B. Move the skill into CLAUDE.md so it's always loaded
- C. Ask developers to run `/clear` after the skill finishes
- D. Add `context: fork` to the skill's frontmatter so it runs in an isolated sub-agent

**4. (Select TWO.)** The team wants a shared Jira MCP server available to everyone, authenticated with each developer's own token. Which steps are correct?

- A. Put the team's token in `.mcp.json` so it works without setup
- B. Reference the token as `${JIRA_TOKEN}` in `.mcp.json`, and have each developer set the environment variable
- C. Configure the server in the project's `.mcp.json` and commit it
- D. Configure the server in the lead developer's `~/.claude.json`
- E. Ask each developer to paste their own token into `.mcp.json` before committing

**5.** A team adds an MCP tool `search_tickets`, but Claude Code keeps using Grep on the repository when asked about open bugs. The tool's description is "Searches tickets." What's the best fix?

- A. Remove Grep from the allowed tools
- B. Expand the MCP tool's description: what it searches, input format with an example, what it returns, and that ticket data isn't in the repo
- C. Add "Always use MCP tools first" to CLAUDE.md
- D. Rename the tool to `grep_tickets` so it sounds like Grep

**6.** An agent has `analyze_content` ("Analyzes content") and `analyze_document` ("Analyzes documents"). It often calls the wrong one for web search results. What's the most effective fix?

- A. Merge them into one `analyze` tool with a `type` parameter
- B. Add a system-prompt rule listing which tool to use for each input type
- C. Rename `analyze_content` to `extract_web_results` and give it a web-specific description that says when to use the other tool
- D. Add few-shot examples of each tool call to the system prompt

**7.** Every failure from an MCP tool returns `{"isError": true, "content": "Operation failed"}`. The agent retries validation errors repeatedly and gives up on transient timeouts. What fixes this?

- A. Increase the agent's retry limit
- B. Log the full stack trace in the error content
- C. Remove `isError` so the agent treats the text as a normal result
- D. Return structured metadata: an `errorCategory`, an `isRetryable` flag, and a message saying what to do next

**8.** A customer lookup tool returns `isError: true` when no customer matches the search. The agent then retries several times and tells the user the system is down. What's the right fix?

- A. Mark the error as `isRetryable: false`
- B. Return a successful result with an empty list, because no match is a valid answer
- C. Add "don't retry customer lookups" to the system prompt
- D. Make the tool raise an exception instead

**9. (Select TWO.)** A `process_refund` tool must reject refunds over the $500 policy limit. What should its error response include so the agent handles it well?

- A. `isRetryable: false`
- B. `errorCategory: "transient"`
- C. A customer-friendly explanation the agent can relay, and what to do instead
- D. An exception that stops the agent loop
- E. A success response with `amount: 0`

**10.** A synthesis subagent was given all 18 tools in the system, including web search. It sometimes runs web searches instead of writing the report, and its tool choices are unreliable. What should you do?

- A. Restrict it to the few tools its role needs, plus a narrow cross-role tool for any frequent need
- B. Add "Don't search the web" to its system prompt
- C. Give it a larger context window
- D. Set `tool_choice` to `"any"` so it always calls a tool

**11.** You need to migrate a logging library used in 45+ files, and there are two viable migration strategies. How should you use Claude Code?

- A. Direct execution, so the migration finishes faster
- B. Ask for all 45 files to be changed in one message without review
- C. Plan mode to explore and choose an approach, then execute the agreed plan
- D. One session per file, in parallel

**12.** A single function throws a clear `KeyError` with a stack trace pointing to the exact line. How should you use Claude Code?

- A. Plan mode, to explore the codebase first
- B. Direct execution
- C. The Explore subagent, to isolate the investigation
- D. Plan mode with an interview first

**13.** Claude needs to change a configuration value whose surrounding text appears four times in the file. The Edit tool fails because the anchor isn't unique. What does the exam guide recommend?

- A. Use Grep to replace the text
- B. Use Bash with `sed` to replace every occurrence
- C. Retry Edit until it succeeds
- D. Read the full file, then Write the modified version

**14.** A developer wants a personal variation of the team's `/review` skill with stricter rules. Teammates must not be affected. Where should it go?

- A. `~/.claude/skills/`, under a different name such as `review-strict`
- B. `.claude/skills/review/`, overwriting the team version locally without committing
- C. The project CLAUDE.md, as an extra instruction
- D. `.claude/skills/review-strict/`, committed to the repo

**15. (Select TWO.)** You're implementing caching in an unfamiliar service with Claude Code. Your prose description of the expected key format keeps being interpreted differently. Which techniques help most?

- A. Give 2–3 concrete input → output examples of the key format
- B. Use the interview pattern: have Claude ask about invalidation and failure modes before implementing
- C. Repeat the description in capital letters
- D. Report the interacting problems one at a time in separate messages
- E. Ask for "higher quality, production-ready" code
