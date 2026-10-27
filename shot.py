from playwright.sync_api import sync_playwright

URL = "https://app.meteo.pl/meteogram/49.72,20.18"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    page = b.new_page(viewport={"width": 1000, "height": 1000},
                      user_agent=UA, locale="pl-PL")
    page.goto(URL, wait_until="networkidle")
    page.wait_for_timeout(8000)          # Flutter potrzebuje chwili na narysowanie wykresu

    # zamknięcie okna "Co nowego?"
    page.keyboard.press("Escape")
    page.wait_for_timeout(2000)          # animacja zamykania

    page.screenshot(path="full.png")
    page.screenshot(path="meteogram.png",
                    clip={"x": 244, "y": 70, "width": 756, "height": 930})
    b.close()
