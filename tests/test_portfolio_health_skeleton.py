def test_portfolio_health_does_not_crash_on_empty_portfolio(load_user, mock_llm):
    from src.portfolio_health import run

    user = load_user("usr_004")
    response = run(user, llm=mock_llm)

    assert response is not None
    assert "disclaimer" in response
    assert response["concentration_risk"]["flag"] == "none"
    assert any("starter allocation" in item["text"] for item in response["observations"])


def test_portfolio_health_handles_missing_cost_basis_fields(mock_llm):
    from src.portfolio_health import run

    user = {
        "user_id": "usr_missing_cost",
        "risk_profile": "moderate",
        "positions": [
            {"ticker": "AAPL", "quantity": None, "avg_cost": 150.0, "currency": "USD"},
            {"ticker": "MSFT", "quantity": 10, "avg_cost": None, "currency": "USD"},
        ],
    }

    response = run(user, llm=mock_llm)

    assert response is not None
    assert response["concentration_risk"]["flag"] == "none"
    assert response["benchmark_comparison"]["benchmark"] == "S&P 500"


def test_portfolio_health_flags_concentration(load_user, mock_llm):
    from src.portfolio_health import run

    user = load_user("usr_003")
    response = run(user, llm=mock_llm)

    assert response["concentration_risk"]["flag"] in {"high", "warning"}
    assert response["concentration_risk"]["top_position"] == "NVDA"


def test_portfolio_health_includes_disclaimer(load_user, mock_llm):
    from src.portfolio_health import run

    user = load_user("usr_001")
    response = run(user, llm=mock_llm)

    assert response["disclaimer"]
    assert "not investment advice" in response["disclaimer"].lower()


def test_portfolio_health_handles_multi_currency_user(load_user, mock_llm):
    from src.portfolio_health import run

    user = load_user("usr_006")
    response = run(user, llm=mock_llm)

    assert response["benchmark_comparison"]["benchmark"] == "MSCI World"
    assert any("multiple currencies" in item["text"] for item in response["observations"])
