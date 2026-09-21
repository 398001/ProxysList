import argparse
import asyncio
import os
import re
import sys
import time
import aiohttp
from aiohttp_socks import ProxyConnector

# Windows Selector nutzen, um Socket-Fehler zu vermeiden
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

PROXY_SOURCES = {
    "http": [
        "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt",
        "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/http_proxies.txt",
        "https://raw.githubusercontent.com/proxio-io/proxy-list/main/http.txt",
        "https://raw.githubusercontent.com/proxio-io/proxy-list/main/https.txt",
        "https://raw.githubusercontent.com/relayglass/free-proxy-list/main/protocol/http/http.txt",
        "https://raw.githubusercontent.com/relayglass/free-proxy-list/main/protocol/https/https.txt",
    ],
    "socks4": [
        "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks4.txt",
        "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/socks4_proxies.txt",
        "https://raw.githubusercontent.com/proxio-io/proxy-list/main/socks4.txt",
        "https://raw.githubusercontent.com/relayglass/free-proxy-list/main/protocol/socks4/socks4.txt",
    ],
    "socks5": [
        "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/socks5.txt",
        "https://raw.githubusercontent.com/dpangestuw/Free-Proxy/main/socks5_proxies.txt",
        "https://raw.githubusercontent.com/proxio-io/proxy-list/main/socks5.txt",
        "https://raw.githubusercontent.com/relayglass/free-proxy-list/main/protocol/socks5/socks5.txt",
    ],
}

PROXY_REGEX = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b")
TEST_URL = "http://httpbin.org/ip"

# PERFORMANCE-EINSTELLUNGEN
TCP_TIMEOUT = 0.6       # Timeout für die schnelle TCP-Vorprüfung
HANDSHAKE_TIMEOUT = 2.5 # Timeout für den echten Protokoll-Test
BATCH_SIZE = 400        # Sicheres Socket-Limit

async def fetch_urls(session: aiohttp.ClientSession, url: str) -> set:
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                text = await resp.text()
                return set(PROXY_REGEX.findall(text))
    except Exception:
        pass
    return set()

# PHASE 1: Schneller TCP-Ping
async def ping_proxy(proxy_str: str) -> str | None:
    ip, port = proxy_str.split(":")
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, int(port)), timeout=TCP_TIMEOUT
        )
        writer.close()
        await writer.wait_closed()
        return proxy_str
    except Exception:
        return None

# PHASE 2: Echter Protokoll-Handshake
async def validate_proxy(semaphore: asyncio.Semaphore, protocol: str, proxy_str: str) -> str | None:
    proxy_url = f"{protocol}://{proxy_str}"
    async with semaphore:
        try:
            connector = ProxyConnector.from_url(proxy_url)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(TEST_URL, timeout=aiohttp.ClientTimeout(total=HANDSHAKE_TIMEOUT)) as resp:
                    if resp.status == 200:
                        return proxy_url
        except Exception:
            pass
        return None

async def scan_protocol(protocol: str, proxies: set) -> list[str]:
    print(f"\n--- Scanne {len(proxies)} {protocol.upper()} Proxys ---")
    proxy_list = list(proxies)
    total = len(proxy_list)
    tcp_alive = []

    # Phase 1
    print(f"[Phase 1] TCP-Ping ({TCP_TIMEOUT}s Timeout)...")
    for i in range(0, total, BATCH_SIZE):
        batch = proxy_list[i : i + BATCH_SIZE]
        tasks = [ping_proxy(p) for p in batch]
        results = await asyncio.gather(*tasks)
        tcp_alive.extend([res for res in results if res is not None])
        
        current = min(i + BATCH_SIZE, total)
        percent = int((current / total) * 100)
        print(f"\r progress: {current}/{total} ({percent}%) | Offene Ports: {len(tcp_alive)}", end="", flush=True)

    print(f"\n -> {len(tcp_alive)} offene Ports gefunden.")
    if not tcp_alive:
        return []

    # Phase 2
    print(f"[Phase 2] Validiere echten {protocol.upper()}-Handshake für {len(tcp_alive)} Proxys...")
    semaphore = asyncio.Semaphore(100)
    val_tasks = [validate_proxy(semaphore, protocol, p) for p in tcp_alive]
    val_results = await asyncio.gather(*val_tasks)
    
    verified = [p for p in val_results if p is not None]
    print(f" -> Bestätigt: {len(verified)} echte {protocol.upper()}-Proxys einsatzbereit.")
    return verified

def save_results(working_proxies: dict):
    print("\nSpeichere Ergebnisse in Dateien...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    all_working = []
    
    for proto, proxies in working_proxies.items():
        filename = os.path.join(script_dir, f"{proto}_working.txt")
        with open(filename, "w", encoding="utf-8") as f:
            for p in proxies:
                f.write(f"{p}\n")
        all_working.extend(proxies)
        print(f" -> {filename} ({len(proxies)} Einträge)")

    all_file = os.path.join(script_dir, "all_working.txt")
    with open(all_file, "w", encoding="utf-8") as f:
        for p in all_working:
            f.write(f"{p}\n")
    print(f" -> {all_file} ({len(all_working)} Einträge Gesamt)")

async def run_checker():
    start_time = time.time()
    print("1. Lade Proxy-Listen herunter...")
    cleaned = {"http": set(), "socks4": set(), "socks5": set()}

    async with aiohttp.ClientSession() as session:
        for proto, urls in PROXY_SOURCES.items():
            tasks = [fetch_urls(session, u) for u in urls]
            results = await asyncio.gather(*tasks)
            for res in results:
                cleaned[proto].update(res)

    total_proxies = sum(len(p) for p in cleaned.values())
    print(f"Gesamt: {total_proxies} eindeutige Proxys geladen.")

    print("\n2. Starte Prüfung (TCP-Precheck + Protokoll-Handshake)...")
    working_proxies = {}
    for proto, proxies in cleaned.items():
        working_proxies[proto] = await scan_protocol(proto, proxies)

    save_results(working_proxies)

    elapsed = round(time.time() - start_time, 2)
    print(f"\n================ SKRIPT ABGESCHLOSSEN ================")
    print(f"Dauer: {elapsed}s | Bestätigte Proxys: {sum(len(v) for v in working_proxies.values())}")

async def main():
    parser = argparse.ArgumentParser(description="Xeno Proxy Checker")
    parser.add_argument("--loop", type=int, help="Intervall in Minuten für automatischen Wiederholungs-Check")
    args = parser.parse_args()

    if args.loop:
        print(f"--- DAEMON MODUS AKTIV: Check läuft alle {args.loop} Minuten ---")
        while True:
            await run_checker()
            print(f"\nWarte {args.loop} Minuten bis zum nächsten Durchlauf...")
            await asyncio.sleep(args.loop * 60)
    else:
        await run_checker()

if __name__ == "__main__":
    asyncio.run(main())
