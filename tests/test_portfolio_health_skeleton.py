def test_portfolio_health_does_not_crash_on_empty_portfolio(load_user, mock_llm):
    from src.portfolio_health import run

    user = load_user("usr_004")
    response = run(user, llm=mock_llm)

    assert response is not None
    assert "disclaimer" in response
    assert response["concentration_risk"]["flag"] == "none"
    assert any("starter allocation" in item["text"] for item in response["observations"])


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
