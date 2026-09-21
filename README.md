# Simple Async Proxy Checker

A fast Python script that downloads free proxy lists, removes duplicates, and checks which ones are actually working.

Saved output goes into text files split by protocol (`http_working.txt`, `socks4_working.txt`, `socks5_working.txt`) and a combined list (`all_working.txt`).

## Requirements

```bash
pip install aiohttp
```

## How to use

Just run the script:

```bash
python Proxy-Checker.py
```

It takes about a minute to scan ~40k proxies and updates the `.txt` files in the same folder.
