from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

URL = "https://app.meteo.pl/meteogram/49.72,20.18"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

# dozwolone domeny (końcówki); wszystko inne jest blokowane
ALLOW = ("meteo.pl", "gstatic.com", "fonts.googleapis.com")

seen = {}

def route_handler(route):
    url = route.request.url
    if not url.startswith("http"):
        route.continue_()
        return
    host = urlparse(url).hostname or ""
    ok = any(host == d or host.endswith("." + d) for d in ALLOW)
    seen[host] = ok
    if ok:
        route.continue_()
    else:
        route.abort()

# działa w tle od początku ładowania strony
CLEANER = """
(() => {
  const KEEP = ['flutter-view', 'script', 'style', 'link', 'noscript', 'meta'];
  const kill = (root) => {
    root.querySelectorAll(
      'iframe, video, ins, [id^="google_ads"], [id^="aswift"], ' +
      '[class*="adsbygoogle"], [data-google-query-id], [data-anchor-status]'
    ).forEach(e => e.remove());
    root.querySelectorAll('*').forEach(e => { if (e.shadowRoot) kill(e.shadowRoot); });
  };
  const sweep = () => {
    if (!document.body) return;
    kill(document);
    [...document.body.children].forEach(e => {
      const t = e.tagName.toLowerCase();
      if (!KEEP.includes(t) && !t.startsWith('flt-')) {
        e.style.setProperty('display', 'none', 'important');
      }
    });
  };
  setInterval(sweep, 300);
})();
"""

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    page = b.new_page(viewport={"width": 1000, "height": 1000},
                      user_agent=UA, locale="pl-PL")
    page.route("**/*", route_handler)
    page.add_init_script(CLEANER)

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
    page.wait_for_timeout(3000)          # czas na ewentualne spóźnione reklamy i ich usunięcie

    # diagnostyka na wypadek, gdyby coś jeszcze przeciekało
    print("hosty (True = dozwolony):", seen)
    print("ramki:", [f.url for f in page.frames])

    page.screenshot(path="full.png")
    page.screenshot(path="meteogram.png",
                    clip={"x": 246, "y": 114, "width": 750, "height": 880})
    b.close()
