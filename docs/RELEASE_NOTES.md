# Release notes

## Unreleased

- Added offset/limit pagination for evaluator check results, including total count and `has_more` metadata.
- Refactored evaluator selection into `EvaluatorRegistry` strategies while preserving existing implementation identifiers and score output.
- Added unit and integration coverage for registry dispatch and result pagination.
- Added a C++17 golden evaluator exposed as `cpp_golden`, with input validation, deterministic output, a benchmark mode, and CI compilation/tests.

No `v1.0.0` release has been published by this change. Create release notes for that version only after the reviewed commit passes CI and the release tag is pushed.
