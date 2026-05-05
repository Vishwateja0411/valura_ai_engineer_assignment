from src.market_data import cost_basis_position_value, get_benchmark_name


DISCLAIMER = (
    "This is not investment advice. It is an educational portfolio health "
    "summary based on the data provided and should not be treated as a personal "
    "recommendation to buy, sell, or hold any security."
)


def _round_pct(value: float) -> float:
    return round(value, 1)


def _risk_flag(top_position_pct: float, top_3_positions_pct: float, holding_count: int) -> str:
    if holding_count == 0:
        return "none"
    if top_position_pct >= 35 or top_3_positions_pct >= 70:
        return "high"
    if top_position_pct >= 20 or top_3_positions_pct >= 50:
        return "warning"
    return "ok"


def _position_values(positions: list[dict]) -> list[dict]:
    values = []
    for position in positions:
        value = cost_basis_position_value(position)
        values.append(
            {
                "ticker": position.get("ticker", "UNKNOWN"),
                "currency": position.get("currency", ""),
                "value": value,
            }
        )
    return sorted(values, key=lambda item: item["value"], reverse=True)


def _empty_portfolio_response(user: dict) -> dict:
    benchmark = get_benchmark_name(user)
    risk_profile = user.get("risk_profile", "moderate")
    observations = [
        {
            "severity": "info",
            "text": (
                "No holdings are recorded yet, so the next useful step is to "
                f"choose a starter allocation that fits a {risk_profile} risk profile."
            ),
        },
        {
            "severity": "info",
            "text": (
                f"Use {benchmark} as a simple reference point while comparing broad, "
                "diversified funds before picking individual stocks."
            ),
        },
    ]

    return {
        "concentration_risk": {
            "top_position_pct": 0.0,
            "top_3_positions_pct": 0.0,
            "flag": "none",
        },
        "performance": {
            "total_return_pct": None,
            "annualized_return_pct": None,
            "note": "No positions are available to calculate performance.",
        },
        "benchmark_comparison": {
            "benchmark": benchmark,
            "portfolio_return_pct": None,
            "benchmark_return_pct": None,
            "alpha_pct": None,
            "note": "Benchmark comparison starts after the first holding is added.",
        },
        "observations": observations,
        "disclaimer": DISCLAIMER,
    }


def _performance_stub() -> dict:
    return {
        "total_return_pct": 0.0,
        "annualized_return_pct": 0.0,
        "note": (
            "Using cost basis as the current value because no live market data "
            "provider was supplied in this run."
        ),
    }


def _benchmark_stub(benchmark: str) -> dict:
    return {
        "benchmark": benchmark,
        "portfolio_return_pct": 0.0,
        "benchmark_return_pct": None,
        "alpha_pct": None,
        "note": "Benchmark return is unavailable without a market data provider.",
    }


def _build_observations(user: dict, values: list[dict], top_position_pct: float, top_3_positions_pct: float, flag: str) -> list[dict]:
    observations = []
    top = values[0]
    risk_profile = user.get("risk_profile", "moderate")
    income_focus = user.get("preferences", {}).get("income_focus", False)

    if flag == "high":
        observations.append(
            {
                "severity": "warning",
                "text": (
                    f"{_round_pct(top_position_pct)}% of the portfolio is in "
                    f"{top['ticker']}. That is the biggest risk to watch first."
                ),
            }
        )
    elif flag == "warning":
        observations.append(
            {
                "severity": "warning",
                "text": (
                    f"The top three holdings make up {_round_pct(top_3_positions_pct)}% "
                    "of the portfolio, so diversification deserves a closer look."
                ),
            }
        )
    else:
        observations.append(
            {
                "severity": "info",
                "text": "No single position dominates the portfolio on the data provided.",
            }
        )

    if income_focus:
        observations.append(
            {
                "severity": "info",
                "text": (
                    "Because this profile is income-focused, review whether dividend "
                    "holdings and bond funds still support cash-flow needs without "
                    "taking too much interest-rate risk."
                ),
            }
        )
    elif risk_profile == "aggressive":
        observations.append(
            {
                "severity": "info",
                "text": (
                    "The profile is aggressive, but concentration can still hurt if "
                    "several growth holdings fall together."
                ),
            }
        )
    else:
        observations.append(
            {
                "severity": "info",
                "text": (
                    "A moderate profile usually benefits from balancing stock exposure "
                    "with broad funds or stabilizing assets."
                ),
            }
        )

    currencies = {item["currency"] for item in values if item["currency"]}
    if len(currencies) > 1:
        observations.append(
            {
                "severity": "info",
                "text": (
                    "This portfolio has holdings in multiple currencies, so FX moves "
                    "can affect results even when the stocks themselves do not move."
                ),
            }
        )

    return observations[:3]


def run(user: dict, llm=None) -> dict:
    positions = user.get("positions", [])
    if not positions:
        return _empty_portfolio_response(user)

    values = _position_values(positions)
    total_value = sum(item["value"] for item in values)
    if total_value <= 0:
        return _empty_portfolio_response(user)

    top_position_pct = values[0]["value"] / total_value * 100
    top_3_positions_pct = sum(item["value"] for item in values[:3]) / total_value * 100
    flag = _risk_flag(top_position_pct, top_3_positions_pct, len(values))
    benchmark = get_benchmark_name(user)

    observations = _build_observations(
        user=user,
        values=values,
        top_position_pct=top_position_pct,
        top_3_positions_pct=top_3_positions_pct,
        flag=flag,
    )

    return {
        "concentration_risk": {
            "top_position_pct": _round_pct(top_position_pct),
            "top_3_positions_pct": _round_pct(top_3_positions_pct),
            "flag": flag,
            "top_position": values[0]["ticker"],
        },
        "performance": _performance_stub(),
        "benchmark_comparison": _benchmark_stub(benchmark),
        "observations": observations,
        "disclaimer": DISCLAIMER,
    }
