# Contribution workflow

Contributions move through a traceable issue, branch, tests, pull request, review, CI, and merge sequence.

1. **Issue:** describe the problem, intended behavior, and acceptance criteria. Maintainers label and scope it before implementation.
2. **Branch:** branch from the current default branch using `feat/`, `fix/`, or `refactor/` naming.
3. **Implementation and tests:** add focused unit tests for logic and integration coverage for API or service behavior. Keep fixtures synthetic.
4. **Pull request:** link the issue, summarize the design, list verification commands and results, and call out limitations.
5. **Review:** reviewers check correctness, security boundaries, compatibility, and test quality. Authors address comments in commits and explain any proposed alternative.
6. **CI and merge:** merge only after required checks pass and approvals are recorded. Use the repository's merge policy and keep the issue/PR links intact.
7. **Release:** update release notes with supported behavior, evidence, setup, and limitations; tag a reviewed, passing commit.

An example end-to-end feature is evaluator result pagination: issue analysis, implementation, unit and integration coverage, review revisions, CI validation, then merge. Do not claim that a step occurred until GitHub records it.
