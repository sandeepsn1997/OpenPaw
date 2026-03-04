from statistics import mean
from typing import Dict, List

INDIA_SWING_UNIVERSE: Dict[str, Dict[str, float]] = {
    "RELIANCE.NS": {"momentum": 0.74, "volatility": 0.48, "trend": 0.72, "liquidity": 0.95},
    "TCS.NS": {"momentum": 0.69, "volatility": 0.36, "trend": 0.71, "liquidity": 0.90},
    "HDFCBANK.NS": {"momentum": 0.66, "volatility": 0.33, "trend": 0.68, "liquidity": 0.88},
    "ICICIBANK.NS": {"momentum": 0.71, "volatility": 0.40, "trend": 0.70, "liquidity": 0.86},
    "LT.NS": {"momentum": 0.73, "volatility": 0.52, "trend": 0.69, "liquidity": 0.78},
    "INFY.NS": {"momentum": 0.63, "volatility": 0.37, "trend": 0.67, "liquidity": 0.87},
    "SBIN.NS": {"momentum": 0.77, "volatility": 0.58, "trend": 0.73, "liquidity": 0.82},
    "BHARTIARTL.NS": {"momentum": 0.72, "volatility": 0.45, "trend": 0.71, "liquidity": 0.81},
}

RISK_WEIGHTS = {
    "conservative": {"momentum": 0.25, "trend": 0.40, "liquidity": 0.25, "volatility_penalty": 0.20},
    "balanced": {"momentum": 0.35, "trend": 0.35, "liquidity": 0.20, "volatility_penalty": 0.15},
    "aggressive": {"momentum": 0.45, "trend": 0.25, "liquidity": 0.15, "volatility_penalty": 0.10},
}


def _normalize_tickers(tickers: List[str], market: str) -> List[str]:
    normalized = []
    for t in tickers:
        symbol = t.strip().upper()
        if market == "india" and ".NS" not in symbol and ".BO" not in symbol:
            symbol = f"{symbol}.NS"
        normalized.append(symbol)
    return normalized


def _score(metrics: Dict[str, float], risk_profile: str) -> float:
    weights = RISK_WEIGHTS.get(risk_profile, RISK_WEIGHTS["balanced"])
    base = (
        metrics["momentum"] * weights["momentum"]
        + metrics["trend"] * weights["trend"]
        + metrics["liquidity"] * weights["liquidity"]
    )
    penalty = metrics["volatility"] * weights["volatility_penalty"]
    return round((base - penalty) * 100, 2)


async def run(
    tickers: List[str] | None = None,
    analysis_window: str = "3m",
    risk_profile: str = "balanced",
    market: str = "india",
    objective: str = "swing_trade",
    top_n: int = 5,
) -> str:
    """Produce a structured stock analysis report suitable for swing-trade workflows."""
    source_universe = INDIA_SWING_UNIVERSE if market == "india" else INDIA_SWING_UNIVERSE

    if not tickers:
        selected = list(source_universe.keys())
    else:
        selected = _normalize_tickers(tickers, market)

    analyzed = []
    for ticker in selected:
        metrics = source_universe.get(ticker)
        if not metrics:
            metrics = {"momentum": 0.55, "volatility": 0.50, "trend": 0.56, "liquidity": 0.60}
        score = _score(metrics, risk_profile)
        analyzed.append((ticker, score, metrics))

    ranked = sorted(analyzed, key=lambda item: item[1], reverse=True)
    picks = ranked[: max(1, min(top_n, len(ranked)))]

    portfolio_score = round(mean([row[1] for row in picks]), 2)
    lines = [
        f"Stock Analysis Report ({market.title()} | {objective} | horizon {analysis_window})",
        f"Risk profile: {risk_profile}",
        f"Top picks (ranked):",
    ]

    for idx, (ticker, score, metrics) in enumerate(picks, start=1):
        action = "BUY ON DIP" if score >= 55 else "WATCH"
        stop_loss = round(100 - (metrics["volatility"] * 10), 1)
        lines.append(
            f"{idx}. {ticker} | score {score}/100 | action {action} | stop-loss discipline {stop_loss}% of planned entry"
        )

    lines.extend(
        [
            "",
            f"Basket quality score: {portfolio_score}/100",
            "Risk controls: position size <=10%, avoid averaging losers, and trail stop-loss after 6-8% move.",
            "Disclaimer: Educational analysis, not investment advice.",
        ]
    )

    return "\n".join(lines)
