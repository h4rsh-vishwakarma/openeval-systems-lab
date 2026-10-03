# C++ algorithm exercise

Compile with `g++ -O2 -std=c++17 benchmark.cpp -o benchmark` and run `./benchmark`. It prints measured wall times for array traversal, hash set insertion, binary search, breadth first traversal, and sorting. Complexity: array sum O(n) time/O(1) extra space; hash insertion expected O(n) time/O(n) space; n binary searches O(n log n) time/O(1) extra space; BFS O(V+E) time/O(V) space; sort O(n log n) time with implementation dependent extra space. These are microbenchmarks, not production performance claims.

Verified on 2026-10-02 in an Alpine 3.20 container with g++: all five modules compiled and ran. One run measured 0 ms for array sum, 89 ms for hash insertion, 1 ms for binary search, 0 ms for BFS, and 5 ms for sorting. The millisecond clock rounds small workloads to zero.

## C++ golden evaluator

`evaluator.cpp` implements the webhook golden evaluator in C++17. It validates that input is an array of event objects, accepts only non-empty string IDs and non-negative numeric amounts (booleans are not numbers), preserves first-seen ID order, and counts invalid events. JSON parsing/serialization uses the system `nlohmann-json3-dev` package.

Compile and test locally on Linux with:

```bash
sudo apt-get install nlohmann-json3-dev g++
mkdir -p algorithms/build
g++ -std=c++17 -O2 -Wall -Wextra -Werror algorithms/evaluator.cpp algorithms/evaluator_cli.cpp -o algorithms/build/openeval-cpp-evaluator
g++ -std=c++17 -O2 -Wall -Wextra -Werror tests/cpp/test_evaluator.cpp algorithms/evaluator.cpp -o algorithms/build/test-cpp-evaluator
algorithms/build/test-cpp-evaluator
printf '[{"id":"a","amount":1},{"id":"a","amount":1}]' | algorithms/build/openeval-cpp-evaluator
algorithms/build/openeval-cpp-evaluator --benchmark 10000
```

The Python worker exposes it as the `cpp_golden` implementation. In Docker, the worker image compiles the executable; CI compiles/tests it before running the Python evaluator bridge tests. The benchmark uses 100 deterministic synthetic events and reports timings from the current runner; do not compare CI timings as a stable performance claim.
