import re

from src.schemas import SafetyVerdict


BLOCK_MESSAGES = {
    "insider_trading": (
        "I can't help with trading on confidential or material non-public "
        "information. I can explain insider-trading rules or help think through "
        "lawful, public-information research instead."
    ),
    "market_manipulation": (
        "I can't help design or coordinate activity meant to manipulate market "
        "prices, volume, or order books. I can explain what market manipulation "
        "is and how investors can avoid it."
    ),
    "money_laundering": (
        "I can't help hide funds, avoid reporting duties, or obscure the source "
        "of money. I can explain AML rules and compliant record-keeping at a "
        "high level."
    ),
    "guaranteed_returns": (
        "I can't promise guaranteed investment returns or name a certain winner. "
        "I can discuss historical ranges, risks, and diversified planning "
        "assumptions."
    ),
    "reckless_advice": (
        "I can't encourage putting essential savings, retirement money, or "
        "borrowed funds into high-risk concentrated trades. I can help compare "
        "the risks and safer alternatives."
    ),
    "sanctions_evasion": (
        "I can't help bypass sanctions, screening, or traceability controls. I "
        "can explain sanctions compliance obligations in general terms."
    ),
    "fraud": (
        "I can't help create false financial documents or misrepresent trading "
        "activity. I can help explain legitimate documentation and dispute "
        "processes."
    ),
}


EDUCATIONAL_STARTS = (
    "what is",
    "what are",
    "explain",
    "describe",
    "how does",
    "how do regulators",
    "why",
    "are ",
    "is ",
)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _looks_educational(query: str) -> bool:
    q = _clean(query)
    return q.startswith(EDUCATIONAL_STARTS) or "penalt" in q or "requirements" in q


def _block(category: str) -> SafetyVerdict:
    return SafetyVerdict(blocked=True, category=category, message=BLOCK_MESSAGES[category])


def check(query: str) -> SafetyVerdict:
    q = _clean(query)
    if not q:
        return SafetyVerdict(blocked=False)

    educational = _looks_educational(q)

    if not educational:
        if (
            ("confidential" in q and any(word in q for word in ("trade", "buy", "shares", "merger", "news")))
            or ("unannounced" in q and any(word in q for word in ("acquisition", "merger", "earnings")))
            or ("friend at" in q and "tip" in q)
            or ("before" in q and "announcement" in q and "earnings" in q)
            or ("material non-public" in q and any(word in q for word in ("trade", "buy", "sell")))
            or ("inside" in q and any(word in q for word in ("tip", "information", "news")) and any(word in q for word in ("buy", "sell", "trade")))
        ):
            return _block("insider_trading")

        if (
            "pump up" in q
            or ("pump-and-dump" in q and any(word in q for word in ("join", "run", "start")))
            or ("pump and dump" in q and any(word in q for word in ("join", "run", "start")))
            or "coordinated buying" in q
            or "move this stock" in q
            or "wash trade" in q
            or "create volume" in q
            or ("spoof" in q and any(word in q for word in ("help me", "place", "fake")))
            or ("layering" in q and any(word in q for word in ("help me", "do", "place")))
        ):
            return _block("market_manipulation")

        if (
            "without reporting" in q
            or "avoid the 10k" in q
            or "avoid reporting" in q
            or "obscure the source" in q
            or "layer my trades" in q
            or "hide trading profits" in q
            or ("tax authorities" in q and any(word in q for word in ("hide", "evade", "avoid")))
        ):
            return _block("money_laundering")

        if (
            "guarantee me" in q
            or "promise me" in q
            or "100% certain" in q
            or "certain to go up" in q
            or "foolproof way" in q
            or ("risk-free" in q and any(word in q for word in ("stock", "equity", "crypto", "return")))
        ):
            return _block("guaranteed_returns")

        if (
            "all my retirement savings" in q
            or "entire emergency fund" in q
            or "mortgage my house" in q
            or "margin loan to buy" in q
            or "borrow money to buy" in q
            or ("put it all" in q and any(word in q for word in ("options", "crypto", "single stock")))
        ):
            return _block("reckless_advice")

        if (
            "bypass ofac" in q
            or "bypass sanctions" in q
            or ("sanctioned" in q and any(word in q for word in ("without it being traced", "hide", "route trades", "shell company")))
        ):
            return _block("sanctions_evasion")

        if (
            "fake contract note" in q
            or "fake statement" in q
            or ("forge" in q and any(word in q for word in ("document", "statement", "contract")))
        ):
            return _block("fraud")

    return SafetyVerdict(blocked=False)
