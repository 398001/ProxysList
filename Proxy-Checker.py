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
        "https://raw.githubusercontent.com/jfadev/bottok/1579ed605512fddd9559ea61dfce5104289a27a1/proxies.txt",
        "https://raw.githubusercontent.com/cvandeplas/pystemon/7e3665674f60250c198b23ad4b87d4393e8e65bb/proxies.txt",
        "https://raw.githubusercontent.com/hendrikbgr/YandexMail-Account-Creator/9ec5d04d7986628def4c42460d7676e57574d8bc/proxies.txt",
        "https://raw.githubusercontent.com/Theyka/Turnstile-Solver/c28af92c479bec96178fdca2dc2bacdb227b5b0f/proxies.txt",
        "https://raw.githubusercontent.com/Snivyn/NERYS-product-monitor-lite/7ce64f7352c0f5b6629281ce1561de8975f6a20a/proxies.txt",
        "https://raw.githubusercontent.com/yzyio/adidas-multi-session/774034868f59255f26b2e831bec7f2e3bf44127c/proxies.txt",
        "https://raw.githubusercontent.com/2ri4eUI/CFW-BOT/76d05aad2290ab098f8558566e388243c5a9af1e/proxies.txt",
        "https://raw.githubusercontent.com/3urobeat/steam-idler/67631480880e57c9a92bb0a9b0b274daf0371f02/proxies.txt",
        "https://raw.githubusercontent.com/tuwid/darkc0de-old-stuff/76f002efe42dce80a1f5be7870650cd2a8ead43e/proxies.txt",
        "https://raw.githubusercontent.com/SaeidB/insta_create/c127e5456c0029e58039832afc766537d8594113/proxies.txt",
        "https://raw.githubusercontent.com/Cyber-Dioxide/Gmail-Brute/ebb98c3563e3933431e81dec85d8d74b44168761/proxies.txt",
        "https://raw.githubusercontent.com/Snivyn/ebay-watcher/d80e4348cb491a4aa34f9cc119ae7b8bfe5a9993/proxies.txt",
        "https://raw.githubusercontent.com/melihozkara/il-ilce-mahalle-sokak-veritabani/a734ac44ca521c4b6a44aad23b1d2ae170e0b22d/proxies.txt",
        "https://raw.githubusercontent.com/natewong1313/recaptcha-fullauto/0429a9bd8bfd734fc4fe313908817042eaf59913/proxies.txt",
        "https://raw.githubusercontent.com/srevarun/CC_Checker-Python/ba5b73411c01d6ffb00f4afa31be660ef2a55187/proxies.txt",
        "https://raw.githubusercontent.com/Kuucheen/KC-Checker/a120584a2b494133ff93e45112d6e77372b6148f/proxies.txt",
        "https://raw.githubusercontent.com/x0day/MultiProxies/415d6371cf24a1df72ca8bc1ba2cd40608d3bbdc/db/proxies.txt",
        "https://raw.githubusercontent.com/l3mpik/slither-feeder-bot/05d060ffd7fb15df5c1b2d5bbc1905f8f4a47837/proxies.txt",
        "https://raw.githubusercontent.com/nejason57mars/mcbot/566ed41a9ab420391f0ac315beef5a69aba13024/proxies.txt",
        "https://raw.githubusercontent.com/paveL1boyko/MuskEmpireBot/c3063216cce6326e78807867125d112d7fed173d/proxies.txt",
        "https://raw.githubusercontent.com/ayyitsc9/nike-account-resetter/d18109a1a4a81b918d8f487bf88bff0c0f7206aa/proxies.txt",
        "https://raw.githubusercontent.com/MachineKillin/Email-Account-Generator-Checker/cd95a6d56e526d31ed5347086a655ebea40ec916/proxies.txt",
        "https://raw.githubusercontent.com/samoculus/Shopify-Scraper/10a5451a4d405474173bf2c8bd6aa32d671ef952/proxies.txt",
        "https://raw.githubusercontent.com/0MeMo07/NGL-Spammer/e96b760fa0aecfec1667fcd2fb64e9d2ed6a72db/proxies.txt",
        "https://raw.githubusercontent.com/car-mrazomor/nike-account-creator/cee7e6b6c7f7b3a822f67f0a626506fe4abf70dc/proxies.txt",
        "https://raw.githubusercontent.com/InsolenceWillow/insolencetvgo/52aa2250bbe367a1d87ce96c6edd45f0fefcd851/proxies.txt",
        "https://raw.githubusercontent.com/Rootmarm/sentry-2.0/f660c31c64b280758ee6a3d83234b1d9d9ea3dc1/proxies.txt",
        "https://raw.githubusercontent.com/ben-sb/AdidasMonitor/bfd6940dc139821f548765d2f394997e52069d0f/proxies.txt",
        "https://raw.githubusercontent.com/Nomzegh/zetachain-automation/869bad1016e77bd728980e1881d626be6a4980dd/proxies.txt",
        "https://raw.githubusercontent.com/ALDON94/X_INSTA/55dfaacb7b46c7a5d035e5f44d4d18a39732db86/Proxies.txt",
        "https://raw.githubusercontent.com/acierp/funcaptcha-solver/bdf0fb883a57a6cebc5885f338b9eea26f9fc707/proxies.txt",
        "https://raw.githubusercontent.com/TCWTEAM/Daptcha/61eb5a19aa838635b524460bd02a4dc89577c559/proxies.txt",
        "https://raw.githubusercontent.com/jonathan6661/P1sty/60e6ceec597347d12dfbd8777b4855568b843e71/proxies.txt",
        "https://raw.githubusercontent.com/spyboy-productions/PhantomCrawler/40a6e6ca6d2f23125c6410471826bf11e79b4649/proxies.txt",
        "https://raw.githubusercontent.com/im-hanzou/nodepay-autoref/6c3a1e04377f1c7c78023755074c98c05cce9a18/proxies.txt",
        "https://raw.githubusercontent.com/cicere/pumpfun-comment-bot/94913e1f1f5c1ceba6e08d84931508ed9b2a41fb/proxies.txt",
        "https://raw.githubusercontent.com/Dra-ID/Premium-Call/21566865c74a2a151688ff5f01cbf6d6cad665b9/proxies.txt",
        "https://raw.githubusercontent.com/Setiawan007/Gmail-Maker-BOTV2/94d7a7b1cb2cb6891e040b5146e89b683befe3f6/proxies.txt",
        "https://raw.githubusercontent.com/KeyWeeUsr/OnionProxy/1735137fe5d7d7806217620e4fa6e26da9e761b2/proxies.txt",
        "https://raw.githubusercontent.com/itxashancode/Pull-Shark-Automation/4788bc2b24050b3cc39f92aa661897eed240148c/proxies.txt",
        "https://raw.githubusercontent.com/Kiny-Kiny/ProxyChanger/0730c450c7a0c7813b49f8d3015f8f257362eff3/proxies.txt",
        "https://raw.githubusercontent.com/Yezz123-Archive/SpotifyGenerator/3b59554d9b3598ca049914684d22d84975dd2045/Proxies.txt",
        "https://raw.githubusercontent.com/odaysec/NewsCrap/918def37f3b0f447be5333fe4fb93fd090337780/proxies.txt",
        "https://raw.githubusercontent.com/im-hanzou/blockmesh-autobot/b2d19000d029acc8cba6f21517194db34df1abca/proxies.txt",
        "https://raw.githubusercontent.com/packetstream/proxysampler/8fedccabf342d890a9b37528075a02a4b9d1838a/proxies.txt",
        "https://raw.githubusercontent.com/Mohitkamboz/Thallium-Nuker/f5596845cd90791739807598e95e05a73f1fc58b/proxies.txt",
        "https://raw.githubusercontent.com/jonathanlin0/Linkvertise-Bypass-Bot/d0c07043df9a77b5f86cee450e6b7a562c2e9af4/proxies.txt",
        "https://raw.githubusercontent.com/ArvdSrh/free-agario-fb-bots/6e6b0e75796c42a8e186b4116f375b7e4438b613/proxies.txt",
        "https://raw.githubusercontent.com/DARKM00N1337/TelegramReferralBot/b0c4f9dc5ce4f112c155fbcd69bf9b085876a0e1/proxies.txt",
        "https://raw.githubusercontent.com/MalinovyjMakintosh/Blum_software/37709207f2d05526b19a32ed097943f2e448f8a4/proxies.txt",
        "https://raw.githubusercontent.com/bbambiku/promo-gen/5e6f1b103e0b05e8f54f1f52f69316bae23a25e6/proxies.txt",
        "https://raw.githubusercontent.com/Z3R003/Discord.Bot/b67a26e1d76558ca71f8fced9ecf107cbcd3cbc3/proxies.txt",
        "https://raw.githubusercontent.com/n3-v/Disocord-Token-Generator/315a3abcbaafa804e6005dc5ee4b71b3a0d847ce/proxies.txt",
        "https://raw.githubusercontent.com/Zlkcyber/expchain/8a1b6ca0f8e60fc248cbf245a73d399f2ab3f135/proxies.txt",
        "https://raw.githubusercontent.com/ed-biz23/Supreme-Bot/ae4174b8180a96ab5b01a1806ffa407839e1eaee/proxies.txt",
        "https://raw.githubusercontent.com/voroware/Voro-CLI/5dd0da85aefe9f5dec7ae993fcfe2c26ec575666/proxies.txt",
        "https://raw.githubusercontent.com/weird1337/Stanley/517ac62eab432af4e99b1dc98ae35b7fce07a7ea/proxies.txt",
        "https://raw.githubusercontent.com/Z3R003/Z3R0Raid/39f895d4f385ce909717600dd56303bc4fa2e17b/proxies.txt",
        "https://raw.githubusercontent.com/tacknuzz/debank-api-balance-checker/ae91de460765044a8a23a512d96731c1dcf582d9/proxies.txt",
        "https://raw.githubusercontent.com/im-hanzou/dawn-autoref/509b5bb1b004573a95bd4f6cb8063a4d3eac918d/proxies.txt",
        "https://raw.githubusercontent.com/gehaxelt/python-trafficgenerator/da40816fe5775a65c1ceff368710a52605d8d06c/proxies.txt",
        "https://raw.githubusercontent.com/Cyber-Dioxide/Prox-Scrapper/9134d1d052d73e446012913d7703aa260796d448/proxies.txt",
        "https://raw.githubusercontent.com/wezaxy/AI-Powered-Instagram-DM-Bot/67bd6a832a08e3916a6f0a11bf36bce73a044c4f/proxies.txt",
        "https://raw.githubusercontent.com/z6o/WalletHunter/c1db25c4868930c589b33a00ae1db167789e8f89/proxies.txt",
        "https://raw.githubusercontent.com/thog9/MegaETH-testnet/9b7e921cdc9aba9dad75beb18ad7951b9fe441c5/proxies.txt",
        "https://raw.githubusercontent.com/n1tr00-10/guns.lol-username-checker/2050f57645863f20594be3195c831028c79e485b/proxies.txt",
        "https://raw.githubusercontent.com/notspeezy/x444-Nuker/3914e94e198b77b0794ecf0dfb923e0ea3ae9c30/proxies.txt",
        "https://raw.githubusercontent.com/HexQuant-hub/MegaETH-Faucet/c85c16925455c27ea3b4f4ebbd32492c3fb613e1/proxies.txt",
        "https://raw.githubusercontent.com/im-hanzou/dawn-validator-bot/8f98c85ec61335d35b95a610e8f8e469512eeee7/proxies.txt",
        "https://raw.githubusercontent.com/9P9/Discord-Token-Brute/8612383a33cd09b3914fa38ef8a224f9cc849ba6/proxies.txt",
        "https://raw.githubusercontent.com/SylvanasSun/scrapy-picture-spider/f70407c9fa62ad073023a37712f1bb1bd33e69f0/proxies.txt",
        "https://raw.githubusercontent.com/FatBeeBHW/twitter-aio-tool/c866e32da19ac69677a3fc087f3659a53e9a63a6/proxies.txt",
        "https://raw.githubusercontent.com/5S6/Roblox-Ally-Bot/774482e0492cb0ef9aab9a749eb27d8929ecad2b/proxies.txt",
        "https://raw.githubusercontent.com/n0ctrn3/DoubleCounter-Bypass/7408a11099344a489ff8ef9c68685909cee2c7e8/proxies.txt",
        "https://raw.githubusercontent.com/Aniell4/DiscordHTTPGen/0aba2f165b5a1303bd976d46ad498624f54a9000/proxies.txt",
        "https://raw.githubusercontent.com/Skiddle-ID/proxylist/8efc6b80f45b351a7df4de691c587f2a65eda0fd/proxies.txt",
        "https://raw.githubusercontent.com/rameezusmani/pythonmassmailer/fd4a8acbcd05e3bfd62626aed736854cb1c4dcab/proxies.txt",
        "https://raw.githubusercontent.com/mmaxou/FckGPTManual/afb63d608bdfb7c4bd2fba5662390da8e465add0/proxies.txt",
        "https://raw.githubusercontent.com/Pr0t0ns/Pr0t0n-X-ADylan-Token-Creator-Joiner/2a837d8f26137cbeab76160133f6913530cd24ed/proxies.txt",
        "https://raw.githubusercontent.com/im-hanzou/kardpay-autoref/528fe22b943b7c6656dbce6db7b899422f73b9f9/proxies.txt",
        "https://raw.githubusercontent.com/NamBZ/diemthi-thpt-2026/4574753f5e84e44c5b7102b8d6bcb6eb90138e12/proxies.txt",
        "https://raw.githubusercontent.com/Timezero1/Anti-Cursed-Darkness-Squad-BETA/a86549a4f483234922c97de04e1fc6082f873742/proxies.txt"
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
        "https://raw.githubusercontent.com/AirdropFamilyIDN-V2-0/grass/90ada37640bcd6db42216ced5548b8d7989d2577/local_proxies.txt"
    ],
    "other": [
        "https://raw.githubusercontent.com/MikeMeliz/TorCrawl.py/2fb5d7842ab5f1bd3aae38e9d3bac21c30ae92f9/res/proxies.txt",
        "https://raw.githubusercontent.com/J3ldo/UGC-Sniper/c27d5db555768abeb89ffc52f24617f253c6a1db/proxies.txt",
        "https://raw.githubusercontent.com/engageub/InternetIncome/053690a750debcf37820b711e0fccb60ac3603f1/proxies.txt",
        "https://raw.githubusercontent.com/cubicbyte/reddit-account-generator/37d709dcf83628858ddc11b10d42ac630e00ca8a/proxies.txt",
        "https://raw.githubusercontent.com/cokice/List-of-genshin-University/93460ae65330fda386a7655e74f7929f796bbe5d/proxies.txt",
        "https://raw.githubusercontent.com/8ck/Instagram-Turbo/d6682142704a0dd24fbe2414ae6abf86e2b510df/proxies.txt",
        "https://raw.githubusercontent.com/KurimuzonAkuma/Kurimuzon-Userbot/ee03f279e7047b8cede5d3b57324e9ba7f26082e/proxies.txt"
    ]
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
    cleaned = {"http": set(), "socks4": set(), "socks5": set(), "other": set()}

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
        if proxies:
            working_proxies[proto] = await scan_protocol(proto, proxies)
        else:
            working_proxies[proto] = []

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
