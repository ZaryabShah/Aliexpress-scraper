# pip install selenium webdriver-manager

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

URL = "https://pl.aliexpress.com/item/1005006722922099.html"
OUTPUT = "aliexpress_full.html"

# ── 1. Chrome options ───────────────────────────────────────────────
opts = Options()
opts.add_argument("--headless=new")        # Chrome 109+ headless mode
opts.add_argument("--disable-gpu")
opts.add_argument("--window-size=1920,1080")

# (optional) run through a proxy
# opts.add_argument("--proxy-server=http://37.48.118.4:13151")

# (optional) import your own cookies so price & currency match the browser
# driver.add_cookie({"name": "_m_h5_tk", "value": "…", "domain": ".aliexpress.com"})

# ── 2. Start browser ────────────────────────────────────────────────
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=opts,
)

try:
    # ── 3. Open the page and wait for a key element ────────────────
    driver.get(URL)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "span.product-price-value")
        )
    )

    # ── 4. Scroll once to trigger lazy-load images / modules ────────
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)             # short pause so images/text can load

    # ── 5. Dump the final HTML ──────────────────────────────────────
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    print(f"✔ Done – full HTML saved to {OUTPUT}")

finally:
    driver.quit()
