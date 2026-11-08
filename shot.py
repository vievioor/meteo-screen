from playwright.sync_api import sync_playwright

URL = "https://app.meteo.pl/meteogram/49.72,20.18"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

# fragmenty adresów sieci reklamowych, które blokujemy
BLOCK = (
    "googlesyndication.com", "doubleclick.net", "googleadservices.com",
    "googletagservices.com", "googletagmanager.com", "adservice.google",
    "amazon-adsystem.com", "adnxs.com", "criteo", "taboola", "outbrain",
    "rubiconproject", "pubmatic", "openx.net", "smartadserver", "adform",
    "gemius", "adsrvr.org", "casalemedia", "moatads", "2mdn.net",
)

HIDE_ADS_CSS = """
ins.adsbygoogle, .adsbygoogle, [class*="adsbygoogle"],
[id^="google_ads"], [id^="aswift"], [id^="google_vignette"],
[id^="div-gpt-ad"], [data-google-query-id], [data-anchor-status],
iframe[src*="googlesyndication"], iframe[src*="doubleclick"],
iframe[id^="google_ads"] {
    display: none !important;
    visibility: hidden !important;
}
"""

def block_ads(route):
    if any(d in route.request.url for d in BLOCK):
        route.abort()
    else:
        route.continue_()

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    page = b.new_page(viewport={"width": 1000, "height": 1000},
                      user_agent=UA, locale="pl-PL")
    page.route("**/*", block_ads)

    # 3 próby wejścia na stronę, bo ICM bywa wolny
    for attempt in range(3):
        try:
            page.goto(URL, wait_until="domcontentloaded", timeout=60000)
            break
        except Exception as e:
            print(f"próba {attempt + 1} nieudana: {e}")
            if attempt == 2:
                raise

    page.wait_for_timeout(12000)         # Flutter potrzebuje chwili na narysowanie wykresu

    # zamknięcie okna "Co nowego?"
    page.keyboard.press("Escape")
    page.wait_for_timeout(2000)

    # schowanie ewentualnych reklam, które mimo blokady trafiły na stronę
    page.add_style_tag(content=HIDE_ADS_CSS)
    page.wait_for_timeout(500)

    # diagnostyka: jakie ramki są na stronie (przyda się, jeśli reklama przejdzie)
    print("ramki:", [f.url for f in page.frames])

    page.screenshot(path="full.png")
    page.screenshot(path="meteogram.png",
                    clip={"x": 246, "y": 114, "width": 750, "height": 880})
    b.close()
