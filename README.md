# LLM-TEST

A collection of Python experiments for working with LLMs, AI agents, reasoning, model configuration, and API-based workflows.

## Overview

This repository contains different experiments built while exploring:

- Large Language Models (LLMs)
- AI agents
- OpenAI API
- Prompt engineering
- Model temperature
- Reasoning benchmarks
- API response handling
- Public data research workflows
- Python-based automation

The repository is mainly used for experimenting with different LLM workflows and agent-based applications.

## Projects

### Crypto Research Agent

`agent-llm.py` implements a simple crypto research agent.

The agent:

1. Fetches publicly available cryptocurrency market data from the CoinGecko API.
2. Extracts relevant market information.
3. Cleans and structures the data.
4. Sends the structured data to an OpenAI model.
5. Generates a concise market research report.
6. Saves the collected data and LLM analysis to `crypto_report.json`.

The current configuration researches:

- Bitcoin
- Ethereum
- Solana
- Cardano

### Data Collected

The agent collects publicly available information such as:

- Current price
- Market capitalization
- Market-cap rank
- 24-hour trading volume
- 24-hour price change
- 24-hour high
- 24-hour low
- Last updated timestamp

The agent does not access private wallets, accounts, credentials, or restricted information.

## Other Experiments

| File | Purpose |
|------|---------|
| `agent-llm.py` | Crypto research agent with LLM analysis |
| `python-agent.py` | Python-based flight booking agent experiment |
| `Benchmark.py` | Reasoning benchmark experiments |
| `llm-test.py` | LLM problem and response generation |
| `model-temperature .py` | Model temperature experiments |
| `response.py` | OpenAI API response handling |
| `main.py` | Python/LLM experimentation |
| `app.py` | Application experiments |
| `image.py` | Image-related API experiments |
| `Ex.py` | General Python/LLM experiments |

## Tech Stack

- Python
- OpenAI API
- CoinGecko API
- Requests
- JSON
- LLMs

## Setup

Clone the repository:

```bash
git clone https://github.com/Akshay-gurav-31/LLM-TEST.git
cd LLM-TEST
