# agent-llm.py

import os
import json
import requests
from openai import OpenAI

# --------------------------------------------------
# Configuration
# --------------------------------------------------

COINS = ["bitcoin", "ethereum", "solana", "cardano"]

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# --------------------------------------------------
# Step 1: Scrape public crypto data
# --------------------------------------------------

def fetch_crypto_data(coins):
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coins),
        "order": "market_cap_desc",
        "per_page": len(coins),
        "page": 1,
        "sparkline": "false",
    }

    response = requests.get(
        COINGECKO_URL,
        params=params,
        timeout=20,
        headers={
            "User-Agent": "CryptoResearchAgent/1.0"
        }
    )

    response.raise_for_status()
    return response.json()


# --------------------------------------------------
# Step 2: Clean the scraped data
# --------------------------------------------------

def clean_crypto_data(raw_data):
    cleaned = []

    for coin in raw_data:
        cleaned.append({
            "name": coin.get("name"),
            "symbol": coin.get("symbol", "").upper(),
            "price_usd": coin.get("current_price"),
            "market_cap_usd": coin.get("market_cap"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "24h_volume_usd": coin.get("total_volume"),
            "24h_change_percent": coin.get("price_change_percentage_24h"),
            "high_24h": coin.get("high_24h"),
            "low_24h": coin.get("low_24h"),
            "last_updated": coin.get("last_updated"),
        })

    return cleaned


# --------------------------------------------------
# Step 3: Give the public data to the LLM
# --------------------------------------------------

def analyze_with_llm(crypto_data):
    prompt = f"""
You are a crypto market research assistant.

Analyze the following publicly available cryptocurrency
market data.

IMPORTANT:
- Do not invent missing information.
- Do not claim to predict future prices.
- Clearly distinguish facts from observations.
- Do not provide personalized financial advice.
- Keep the analysis concise.

Data:

{json.dumps(crypto_data, indent=2)}

Return:

1. Market snapshot
2. Biggest 24h movers
3. Market-cap comparison
4. Volume comparison
5. Notable observations
6. Data limitations
"""

    response = client.responses.create(
        model="gpt-5",
        input=prompt
    )

    return response.output_text


# --------------------------------------------------
# Step 4: Save results
# --------------------------------------------------

def save_report(crypto_data, analysis):
    report = {
        "source": "CoinGecko public API",
        "crypto_data": crypto_data,
        "llm_analysis": analysis
    }

    with open("crypto_report.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)


# --------------------------------------------------
# Main Agent
# --------------------------------------------------

def main():
    print("Starting Crypto Research Agent...")

    print("Fetching public crypto data...")
    raw_data = fetch_crypto_data(COINS)

    print("Cleaning data...")
    crypto_data = clean_crypto_data(raw_data)

    print("Sending data to LLM...")
    analysis = analyze_with_llm(crypto_data)

    print("\n========== CRYPTO REPORT ==========\n")
    print(analysis)

    save_report(crypto_data, analysis)

    print("\nReport saved to crypto_report.json")


if __name__ == "__main__":
    main()
