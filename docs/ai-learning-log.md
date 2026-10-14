# AI Learning Log: Engineer A

## Cycle 1: Blank check
- **Question:** Does `fellow_id == ""` catch an ID of only spaces?
- **AI explanation:** No. `"   "` is not `""`. `.strip()` removes spaces, so compare the stripped value.
- **My experiment:** `"   ".strip()` on a typed-in string never checks user input. I ran `"F001"`, `""`, `"   "`, `None`. Results: [fill in]
- **Decision:** Use `fellow_id.strip() == ""` after the type check. Same fix for approver.

## Cycle 2: ASCII digits
- **Question:** Is `.isdigit()` enough for request IDs?
- **AI explanation:** No. It accepts digits from other scripts, such as full-width `１`.
- **My experiment:** Ran `"A００１".isdigit()` and `validate_request_id("A００１")`. Results: [fill in]
- **Decision:** Check each character against `"0123456789"`.

## Cycle 3: The "A" bug
- **Question:** Why did `validate_request_id("A")` pass?
- **AI explanation:** A slice of a string is always a string, even an empty one, so my check never fired.
- **My experiment:** Ran `"A"` before and after the fix. Results: [fill in]
- **Decision:** Reject when `digits == ""`.

## What I can explain without AI
- Why validation comes before writing to the dictionary.
- Why the type check comes before `.strip()`.
- Validation (reject) versus sanitization (fix).