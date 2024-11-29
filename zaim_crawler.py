import calendar
import time

from datetime import datetime
from tqdm import tqdm
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

# respect https://github.com/liebe-magi/pyzaim

class ZaimCrawler:
    def __init__(self, user_id, password):
        service = Service("/app/code/chromedriver")
        options = ChromeOptions()

        # メモリ消費を抑えるオプション
        options.add_argument("--disable-gpu")  # GPU ハードウェアアクセラレーションを無効化
        options.add_argument("--disable-software-rasterizer")  # ソフトウェアラスタライズを無効化
        options.add_argument("--no-sandbox")  # サンドボックス機能を無効化（Docker 環境で有効）
        options.add_argument("--disable-dev-shm-usage")  # /dev/shm を使わない
        options.add_argument("--disable-extensions")  # 拡張機能を無効化
        options.add_argument("--headless")  # ヘッドレスモード（UI を表示しない）
        options.add_argument("--disable-plugins")  # プラグインを無効化
        options.add_argument("--disable-translate")  # 翻訳機能を無効化
        options.add_argument("--disable-background-timer-throttling")  # 背景でのタイマー処理を無効化
        options.add_argument("--disable-backgrounding-occluded-windows")  # 非表示ウィンドウでのバックグラウンド処理を無効化

        # メモリ使用量を制限
        options.add_argument("--window-size=1280x1024")  # ウィンドウサイズを適切に設定
        options.add_argument("--disable-hardware-acceleration")  # ハードウェアアクセラレーションを無効化

        self.driver = Chrome(service=service, options=options)
        print("Start Chrome Driver.")

        print("Login to Zaim.")
        loginUrl = "https://zaim.net/user_session/new"

        self.driver.get(loginUrl)
        time.sleep(1)

        self.driver.find_element(value="email").send_keys(user_id)
        self.driver.find_element(value="password").send_keys(password, Keys.ENTER)

        wait = WebDriverWait(self.driver, 20)  # 最大20秒待機
        wait.until(lambda d: d.current_url != loginUrl)
        print("Redirected to:", self.driver.current_url)
        print("Login Success.")

        self.data = []
        self.current = 0

    def get_data(self, year, month):
        day_len = calendar.monthrange(int(year), int(month))[1]
        year = str(year)
        month = str(month).zfill(2)
        print("Get Data of {}/{}.".format(year, month))
        self.driver.get("https://zaim.net/money?month={}{}".format(year, month))
        time.sleep(10)

        # プログレスバーのゴールを対象月の日数にする
        print("Found {} days in {}/{}.".format(day_len, year, month))
        self.current = day_len
        self.pbar = tqdm(total=day_len)

        # データが一画面に収まらない場合には、スクロールして繰り返し読み込みする
        loop = True
        while loop:
            loop = self.crawler(year)

        self.pbar.update(self.current)
        self.pbar.close()

        return self.data[::-1]

    def close(self):
        self.driver.close()

    def crawler(self, year):
        table = self.driver.find_element(
            by=By.XPATH,
            value="//*[starts-with(@class, 'SearchResult-module__list___')]",
        )
        lines = table.find_elements(
            by=By.XPATH,
            value="//*[starts-with(@class, 'SearchResult-module__body___')]",
        )

        for line in lines:
            items = line.find_elements(by=By.TAG_NAME, value="div")

            item = {}
            item["id"] = items[0].find_element(by=By.TAG_NAME, value="i").get_attribute("data-url").split("/")[2]

            # 前ループの読み込み内容と重複がある場合はスキップする
            flg_duplicate = next((data["id"] for data in self.data if data["id"] == item["id"]), None)
            if flg_duplicate:
                continue

            item["count"] = items[1].find_element(by=By.TAG_NAME, value="i").get_attribute("title").split("（")[0]
            date = items[2].text.split("（")[0]
            item["date"] = datetime.strptime("{}年{}".format(year, date), "%Y年%m月%d日")
            item["category"] = items[3].find_element(by=By.TAG_NAME, value="span").get_attribute("data-title")
            item["genre"] = items[3].find_elements(by=By.TAG_NAME, value="span")[1].text
            item["amount"] = int(items[4].find_element(by=By.TAG_NAME, value="span").text.strip("¥").replace(",", ""))
            m_from = items[5].find_elements(by=By.TAG_NAME, value="img")
            if len(m_from) != 0:
                item["from_account"] = m_from[0].get_attribute("data-title")
            m_to = items[6].find_elements(by=By.TAG_NAME, value="img")
            if len(m_to) != 0:
                item["to_account"] = m_to[0].get_attribute("data-title")
            item["type"] = (
                "transfer"
                if "from_account" in item and "to_account" in item
                else ("payment" if "from_account" in item else "income" if "to_account" in item else None)
            )
            item["place"] = items[7].find_element(by=By.TAG_NAME, value="span").text
            item["name"] = items[8].find_element(by=By.TAG_NAME, value="span").text
            item["comment"] = items[9].find_element(by=By.TAG_NAME, value="span").text
            self.data.append(item)
            tmp_day = item["date"].day

            self.pbar.update(self.current - tmp_day)
            self.current = tmp_day

        # 画面をスクロールして、まだ新しい要素が残っている場合はループを繰り返す
        current_id = (
            lines[0]
            .find_elements(by=By.TAG_NAME, value="div")[0]
            .find_element(by=By.TAG_NAME, value="i")
            .get_attribute("data-url")
            .split("/")[2]
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", lines[len(lines) - 1])
        time.sleep(0.1)
        next_id = (
            self.driver.find_element(
                by=By.XPATH,
                value="//*[starts-with(@class, 'SearchResult-module__list___')]",
            )
            .find_elements(
                by=By.XPATH,
                value="//*[starts-with(@class, 'SearchResult-module__body___')]",
            )[0]
            .find_elements(by=By.TAG_NAME, value="div")[0]
            .find_element(by=By.TAG_NAME, value="i")
            .get_attribute("data-url")
            .split("/")[2]
        )

        if current_id == next_id:
            return False
        else:
            return True
