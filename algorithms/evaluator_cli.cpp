#include "evaluator.hpp"

#include <chrono>
#include <cstdlib>
#include <iostream>
#include <string>

namespace {

nlohmann::json sample_events() {
    nlohmann::json events = nlohmann::json::array();
    for (int index = 0; index < 100; ++index) {
        events.push_back({{"id", "event-" + std::to_string(index % 80)}, {"amount", index % 20}});
    }
    return events;
}

int run_benchmark(int iterations) {
    if (iterations < 1 || iterations > 10000000) {
        std::cerr << "iterations must be in [1, 10000000]\n";
        return 2;
    }

    const auto events = sample_events();
    nlohmann::json result;
    const auto start = std::chrono::steady_clock::now();
    for (int index = 0; index < iterations; ++index) {
        result = openeval::evaluate_golden(events);
    }
    const auto elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
    std::cout << nlohmann::json{{"workload", "100 synthetic events"},
                               {"iterations", iterations},
                               {"elapsed_seconds", elapsed},
                               {"evaluations_per_second", iterations / elapsed},
                               {"stored_count", result.at("stored_count")},
                               {"rejected_count", result.at("rejected_count")}}
                     .dump()
              << '\n';
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc == 3 && std::string(argv[1]) == "--benchmark") {
        try {
            return run_benchmark(std::stoi(argv[2]));
        } catch (const std::exception& error) {
            std::cerr << "invalid benchmark arguments: " << error.what() << '\n';
            return 2;
        }
    }
    if (argc != 1) {
        std::cerr << "usage: openeval-cpp-evaluator [--benchmark ITERATIONS]\n";
        return 2;
    }

    try {
        nlohmann::json events;
        std::cin >> events;
        std::cout << openeval::evaluate_golden(events).dump() << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << "invalid evaluator input: " << error.what() << '\n';
        return 2;
    }
}
