# Day 3 quiz: answers and reasoning

Multiple-response questions score only if every pick is right. 12+ means you're on track.

| Q | Answer | Rule (task) |
|---|---|---|
| 1 | **B** | Explicit criteria beat vague instructions. This is the guide's own example (4.1). A is confidence filtering, C doubles cost without defining what's wrong, and D doesn't change what counts as an issue. |
| 2 | **D** | "Be conservative" and "only high-confidence" don't improve precision compared with categorical criteria (4.1). The model is confident about its false positives too. |
| 3 | **A** | High false-positive categories undermine trust in the accurate ones, so temporarily disable them while you fix their prompts (4.1). B is confidence filtering again, and C and D don't touch the cause. |
| 4 | **C** | Explicit severity criteria with concrete code examples for each level (4.1). A adds a label without criteria, and D is a label with more digits. |
| 5 | **B** | Few-shot examples are the most effective technique for consistent format when detailed instructions alone aren't working (4.2). C treats the symptom, and A and D are more instructions. |
| 6 | **B, D** | 2–4 targeted examples on ambiguous cases, showing why one choice beat the alternative (4.2). A dilutes attention, C tests memory instead of the prompt, and E skips the cases that need help. |
| 7 | **A** | Few-shot examples of varied document structures fix empty or null extraction of fields on unfamiliar layouts (4.2). B forces fabrication, and D is an adjective. |
| 8 | **C** | `tool_use` with a JSON schema is the most reliable way to get schema-compliant output and eliminates syntax errors (4.3). A and B repair what C prevents. |
| 9 | **D** | `"any"` guarantees a tool call while letting the model pick which schema fits, for when the document type is unknown (4.3). B forces the wrong tool for receipts and contracts, and A allows a text reply. |
| 10 | **B** | Forcing a named tool makes that particular extraction run before enrichment steps (4.3). A and D are only suggestions, and C lets it pick any tool. |
| 11 | **A** | Fields the source may lack should be nullable, so the model isn't pushed to fabricate a value for a required field (4.3). C leaves the force in place, and B catches only some inventions. |
| 12 | **C** | Strict schemas prevent syntax errors, not semantic ones such as line items that don't sum to the total (4.3). Validation and retry (Day 4) handle it. B isn't a semantic check, and such constraints aren't supported in strict mode anyway. |
| 13 | **A, E** | An enum with `"other"` + a detail string for extensible categories, and `"unclear"` for ambiguous cases (4.3). B loses the clean enum downstream code relies on, C is unmaintainable, and D is already true and doesn't help. |
| 14 | **B** | Include format normalisation rules in the prompt alongside the strict schema (4.3). The schema can require YYYY-MM-DD, but it can't say which digits are the day. |
| 15 | **B, D** | `auto` may return text; a forced tool must be called (4.3). C describes forced selection, not `any`. A: `auto` guarantees nothing. E: no schema or tool setting guarantees semantics. |

## Pattern to notice

Questions 2, 3, 11 and 13 all have a wrong option that **adds force without information**: be conservative, a confidence threshold, a required field, or a bigger enum. The right answer either *tells the model something new* (criteria, examples, normalisation rules) or *gives it a legitimate way out* (null, `"other"`, `"unclear"`). When you're torn, ask: *which option gives the model information or a valid exit, and which one only pushes harder?*
