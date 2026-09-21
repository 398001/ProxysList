import asyncio
import os
import re
import sys
import time
import aiohttp

# Windows Selector nutzen, um Proactor-Crashs zu vermeiden
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

# OPTIMIERTE EINSTELLUNGEN FOR SPEED & WINDOWS STABILITÄT
TIMEOUT = 0.6          # 600ms Timeout
BATCH_SIZE = 450       # Sicheres Windows-Limit (< 512 Sockets)

async def fetch_urls(session, url):
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                text = await resp.text()
                return set(PROXY_REGEX.findall(text))
    except Exception:
        pass
    return set()

async def ping_proxy(proxy_str, protocol):
    ip, port = proxy_str.split(":")
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, int(port)), timeout=TIMEOUT
        )
        writer.close()
        await writer.wait_closed()
        return f"{protocol}://{proxy_str}"
    except Exception:
        return None

async def fast_scan_protocol(protocol, proxies):
    print(f"\nScanne {len(proxies)} {protocol.upper()} Proxys...")
    proxy_list = list(proxies)
    total = len(proxy_list)
    alive = []

    for i in range(0, total, BATCH_SIZE):
        batch = proxy_list[i : i + BATCH_SIZE]
        tasks = [ping_proxy(p, protocol) for p in batch]
        
        results = await asyncio.gather(*tasks)
        alive.extend([res for res in results if res is not None])
        
        current = min(i + BATCH_SIZE, total)
        percent = int((current / total) * 100)
        print(f"\r progress: {current}/{total} ({percent}%) | Gefunden: {len(alive)}", end="", flush=True)

    print(f"\n -> Fertig! {len(alive)} live Proxys gefunden.")
    return alive

def save_results(working_proxies):
    print("\n3. Speichere Ergebnisse in Dateien...")
    all_working = []
    
    # Pfad des Skripts ermitteln (F:\Projects\DDoS\)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
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

async def main():
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

    print("\n2. Starte Massen-Scan...")
    working_proxies = {}
    for proto, proxies in cleaned.items():
        working_proxies[proto] = await fast_scan_protocol(proto, proxies)

    save_results(working_proxies)

    elapsed = round(time.time() - start_time, 2)
    print(f"\n================ SKRIPT ABGESCHLOSSEN ================")
    print(f"Dauer: {elapsed} Sekunden für {total_proxies} Proxys.")
    print(f"Ergebnis: {sum(len(v) for v in working_proxies.values())} funktionierende Verbindungen gesichert.")

if __name__ == "__main__":
    asyncio.run(main())