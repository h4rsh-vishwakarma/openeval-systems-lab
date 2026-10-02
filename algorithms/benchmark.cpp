#include <algorithm>
#include <chrono>
#include <iostream>
#include <queue>
#include <random>
#include <unordered_set>
#include <vector>

int main() {
    constexpr int n = 100000;
    std::mt19937 rng(42);
    std::vector<int> values(n);
    for (int& value : values) value = static_cast<int>(rng());
    auto measure = [](const char* name, auto work) {
        auto start = std::chrono::steady_clock::now();
        auto result = work();
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now() - start).count();
        std::cout << name << ",elapsed_ms=" << ms << ",result=" << result << '\n';
    };
    measure("array_sum", [&] { long long sum = 0; for (int v : values) sum += v; return sum; });
    measure("hash_unique", [&] { std::unordered_set<int> unique(values.begin(), values.end()); return static_cast<long long>(unique.size()); });
    std::sort(values.begin(), values.end());
    measure("binary_search", [&] { long long hits = 0; for (int i = 0; i < n; ++i) hits += std::binary_search(values.begin(), values.end(), i); return hits; });
    std::vector<std::vector<int>> graph(n);
    for (int i = 0; i + 1 < n; ++i) graph[i].push_back(i + 1);
    measure("graph_bfs", [&] { std::queue<int> q; q.push(0); long long visited = 0; while (!q.empty()) { int node = q.front(); q.pop(); ++visited; for (int next : graph[node]) q.push(next); } return visited; });
    measure("sort", [&] { std::shuffle(values.begin(), values.end(), rng); std::sort(values.begin(), values.end()); return static_cast<long long>(values.front()); });
}
