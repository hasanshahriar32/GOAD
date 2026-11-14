# Reviewed QuillBot language-editing pass

QuillBot was actually used through its live website in a local Chromium browser. TinyFish was installed and its tools became visible, but its backend returned `Unknown tool` for profile listing and browser automation. The local browser fallback initially encountered Cloudflare verification; the normal visible browser subsequently loaded the editor. No CAPTCHA bypass or password entry by the assistant was used.

The Standard-mode pilot covers the opening introduction paragraph. Six completed Fluency-mode passages cover the abstract in three chunks, the next introduction paragraph, and the two conclusion paragraphs. Actual service inputs and outputs are retained in `PILOT_RESULT.json` and `BATCH_RESULTS.json`. The incomplete mixed-passage attempt is marked `INTERRUPTED_ATTEMPT_NOT_APPLIED.json` and was not used. After the user confirmed the tab would remain unchanged, the completed pass checked both the input and selected mode before accepting each output.

Seven selected language edits are recorded in `ACCEPTED_EDITS.json`. Several are reviewed hybrids: a useful grammatical construction was retained while technical words or qualifications were restored. The manuscript's AI-assistance disclosure now names QuillBot. This is not a claim of independently human authorship.

## Examples of rejected changes

- `remediation` became `rehabilitation`: wrong technical term.
- Issuer-scoped identity became identity restricted to the issuer: changes the evidence contract.
- `66 successful ... including 13 administrative uses` lost `including`: obscures the relationship between the counts.
- Scanning configuration and investigating certificate use `answer different questions` became `yield different results`: confuses task definitions with comparative outcomes.
- Required deployment `measurements` became `calculations`: changes the needed evidence.
- Classification became categorization and neural-positive cases became situations: less precise technical vocabulary.

No equations, results, experimental inputs or reference keys were changed by this pass. No QuillBot score, Human score or new Turnitin score is claimed. The service outputs are editing suggestions, and retained passages still require the authors' final review.
