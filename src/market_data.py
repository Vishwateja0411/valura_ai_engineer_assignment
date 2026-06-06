def get_benchmark_name(user: dict) -> str:
    preferences = user.get("preferences", {})
    if preferences.get("preferred_benchmark"):
        return preferences["preferred_benchmark"]

    country = user.get("country")
    if country == "UK":
        return "FTSE 100"
    if country in {"SG", "EU"}:
        return "MSCI World"
    if country == "JP":
        return "NIKKEI 225"
    return "S&P 500"


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def cost_basis_position_value(position: dict) -> float:
    return _safe_float(position.get("quantity")) * _safe_float(position.get("avg_cost"))
