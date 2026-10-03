#include "evaluator.hpp"

#include <string>
#include <unordered_set>
#include <vector>

namespace openeval {

nlohmann::json evaluate_golden(const nlohmann::json& events) {
    if (!events.is_array()) {
        throw nlohmann::json::type_error::create(302, "events must be an array", &events);
    }

    std::unordered_set<std::string> seen;
    std::vector<std::string> stored_ids;
    std::size_t rejected_count = 0;

    for (const auto& event : events) {
        if (!event.is_object()) {
            throw nlohmann::json::type_error::create(302, "each event must be an object", &event);
        }

        const auto id = event.find("id");
        const auto amount = event.find("amount");
        const bool valid_id = id != event.end() && id->is_string() && !id->get_ref<const std::string&>().empty();
        const bool numeric_amount = amount != event.end() &&
                                    (amount->is_number_integer() || amount->is_number_unsigned() || amount->is_number_float());
        const bool valid_amount = numeric_amount && amount->get<double>() >= 0.0;

        if (!valid_id || !valid_amount) {
            ++rejected_count;
            continue;
        }

        const auto& event_id = id->get_ref<const std::string&>();
        if (seen.insert(event_id).second) {
            stored_ids.push_back(event_id);
        }
    }

    return {{"stored_ids", stored_ids},
            {"stored_count", stored_ids.size()},
            {"rejected_count", rejected_count}};
}

}  // namespace openeval
