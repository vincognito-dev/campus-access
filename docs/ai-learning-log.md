# AI Learning Log

## Engineer A: Learning Cycle 1
- **Question:** How do I robustly check if an ID string contains only standard ASCII digits 0-9 without accidentally letting native Unicode variants (like full-width numbers `１２３`) pass via `.isdigit()`?
- **AI Explanation:** `.isdigit()` returns True for various Unicode characters that represent numbers. To restrict validation strictly to ASCII chars `0-9`, use `.isascii() and .isdigit()` together, or check against a set/regex character block `^[0-9]+$`.
- **Experiment:** Tested `'１２３'.isdigit()` -> `True`. Tested `any(c not in '0123456789' for c in '１２３')` -> `True`.
- **Verification:** Using basic inclusion or a regex ensures perfect adherence to the ASCII requirements.
- **Final Decision:** We will use a standard loop check or regex matching `^A[0-9]{3}$` to lock down allowed structural patterns.

## Engineer A: Learning Cycle 2
- **Question:** How can I safely read a JSON file and validate structural fields without polluting my in-memory system if validation halfway fails?
- **AI Explanation:** Parse the JSON file completely into a local disconnected temporary dictionary first. Perform checks over all loaded components. If all records meet the schemas, swap the real memory dictionary references.
- **Experiment:** Verified that throwing an exception inside a parsing loop leaves the old instance clean if the assignment statement is kept at the very end of the function block.
- **Final Decision:** Implement "All-or-Nothing" atomic JSON loading.

## Engineer B: Learning Cycle 1
- **Question:** How should the UI enforce state machine transitions safely without duplicating the state machine logic?
- **AI Explanation:** UI forms should pass intents down to the domain logic engine. The core logic engine validates state transitions and raises exceptions if unauthorized. The UI captures those failures and displays them cleanly as error prompts.
- **Experiment:** Wrote a prototype state validation map: `ALLOWED_TRANSITIONS = {"requested": ["approved"], ...}`.
- **Final Decision:** Put state constraints cleanly inside the registry management module; let the UI trap errors gracefully.

## Engineer B: Learning Cycle 2
- **Question:** How can I test interactive loops with `unittest` without blocking execution waiting for a real user's terminal `input()`?
- **AI Explanation:** Use `unittest.mock.patch` to override the built-in `input` function with a predefined iterable sequence of strings.
- **Experiment:** Tested mock side-effects returning `['1', 'F001', 'visitor', '9']` which simulates creating a request and then exiting the app.
- **Final Decision:** We will simulate end-to-end integration scenarios using mocked inputs to fulfill the CLI retry tests.
