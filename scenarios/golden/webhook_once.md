# Golden task: process webhooks once

Input: a sequence of objects with a nonempty string `id` and a nonnegative numeric `amount`. Process each valid ID once in first seen order. Invalid objects count as rejected; duplicates do not count as rejected. Output: `stored_ids`, `stored_count`, `rejected_count`.

The reference function is `services/evaluator/core.py::golden`. Evaluation runs valid, duplicate, invalid and mixed fixtures, plus optional submitted input. Each exact output match contributes one point; the score is passed checks divided by total checks.
