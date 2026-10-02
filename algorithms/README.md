# C++ algorithm exercise

Compile with `g++ -O2 -std=c++17 benchmark.cpp -o benchmark` and run `./benchmark`. It prints measured wall times for array traversal, hash set insertion, binary search, breadth first traversal, and sorting. Complexity: array sum O(n) time/O(1) extra space; hash insertion expected O(n) time/O(n) space; n binary searches O(n log n) time/O(1) extra space; BFS O(V+E) time/O(V) space; sort O(n log n) time with implementation dependent extra space. These are microbenchmarks, not production performance claims.

Verified on 2026-10-02 in an Alpine 3.20 container with g++: all five modules compiled and ran. One run measured 0 ms for array sum, 89 ms for hash insertion, 1 ms for binary search, 0 ms for BFS, and 5 ms for sorting. The millisecond clock rounds small workloads to zero.
