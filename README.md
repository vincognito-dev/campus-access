# Campus Access: Access-Card Request Manager

A Python command-line application that manages campus access-card requests
(visitor, student, staff). A request is created, approved by a staff
identifier, issued, and returned. Invalid actions are rejected, and data
is saved to JSON and reloaded safely.

Built by two engineers using only the Python standard library.

- Engineer A: Okefu Enyitobi, registration, validation, storage
- Engineer B: Elijah Mamodu, approval workflow, CLI

## Requirements

- Python 3.8
- No external packages

## How to run

From the repository root (the folder containing `main.py`):

    python3 main.py

## How to test

From the repository root:

    python3 -m unittest discover -s tests -v

Tests use temporary files and never touch real data.

## Workflow

    requested -> approved -> issued -> returned

- Only a request with a nonempty approver can be issued.
- States cannot be skipped, and `returned` is final.
- A failed action leaves the record exactly unchanged.

## Request fields

| Field | Description |
|---|---|
| id | A001, A002, ... (unique, also after a restart) |
| fellow_id | Nonempty text, no surrounding spaces |
| card_type | visitor, student or staff |
| status | requested, approved, issued or returned |
| approved_by | None until approved, then a nonempty string |

## Project structure

    campus-access/
    ├── main.py                  # starts the CLI
    ├── campus_access/
    │   ├── validation.py        # input checks (A)
    │   ├── storage.py           # store, IDs, save/load (A)
    │   ├── workflow.py          # approve, issue, return (B)
    │   └── cli.py               # menu (B)
    ├── tests/
    └── docs/
        ├── design-decisions.md
        └── ai-learning-log.md

## Data safety

- All input is validated before any record is written.
- Saving writes to a temporary file first, so a failed save never damages
  an existing file.
- Loading validates every record and rejects bad files (corrupt JSON,
  duplicate IDs, missing keys, invalid states) without changing the data
  already in memory.

## Git workflow

- `feat/1-request-validation` (Engineer A)
- `feat/2-access-workflow` (Engineer B)
- No direct feature pushes to `main`. Every PR is reviewed by the other engineer.

## Documentation

- [Design decisions](docs/design-decisions.md)
- [AI learning log](docs/ai-learning-log.md)