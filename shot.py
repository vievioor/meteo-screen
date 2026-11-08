from playwright.sync_api import sync_playwright

URL = "https://app.meteo.pl/meteogram/49.72,20.18"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

with sync_playwright() as p:
    b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
    page = b.new_page(viewport={"width": 1000, "height": 1000},
                      user_agent=UA, locale="pl-PL")

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

    page.screenshot(path="full.png")
    page.screenshot(path="meteogram.png",
                    clip={"x": 246, "y": 114, "width": 750, "height": 880})
    b.close()
