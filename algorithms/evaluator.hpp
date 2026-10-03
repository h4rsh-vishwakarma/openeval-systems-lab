#pragma once

#include <nlohmann/json.hpp>

namespace openeval {

// Evaluates webhook events using the same validation and first-seen rules as
// the Python golden evaluator. Throws nlohmann::json::type_error on bad input.
nlohmann::json evaluate_golden(const nlohmann::json& events);

}  // namespace openeval
