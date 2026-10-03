#include "../../algorithms/evaluator.hpp"

#include <cassert>
#include <string>

int main() {
    const nlohmann::json events = nlohmann::json::array({
        {{"id", "a"}, {"amount", 10}},
        {{"id", "a"}, {"amount", 10}},
        {{"id", "b"}, {"amount", 0.5}},
        {{"id", ""}, {"amount", 1}},
        {{"id", "negative"}, {"amount", -1}},
        {{"id", "boolean"}, {"amount", true}},
    });
    const auto result = openeval::evaluate_golden(events);
    assert(result.at("stored_ids") == nlohmann::json::array({"a", "b"}));
    assert(result.at("stored_count") == 2);
    assert(result.at("rejected_count") == 3);
    assert(openeval::evaluate_golden(events) == result);

    bool rejected_non_array = false;
    try {
        (void)openeval::evaluate_golden(nlohmann::json::object());
    } catch (const nlohmann::json::type_error&) {
        rejected_non_array = true;
    }
    assert(rejected_non_array);

    bool rejected_non_object = false;
    try {
        (void)openeval::evaluate_golden(nlohmann::json::array({"bad-event"}));
    } catch (const nlohmann::json::type_error&) {
        rejected_non_object = true;
    }
    assert(rejected_non_object);
    return 0;
}
