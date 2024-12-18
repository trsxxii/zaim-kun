import os
from datetime import datetime
from zaim_crawler import ZaimCrawler
from gs_fetcher import GSFetcher
from budget_utils import *
from line_notifier import send_line_notification
from constants import *
from dotenv import load_dotenv

# 初期化
# service_account_file = 'adept-bond-386013-ab92787a2f17.json'
# load_dotenv('.env')
service_account_file = '/etc/secrets/service-account/service-account.json'
load_dotenv('/etc/secrets/env/.env')

email = os.getenv('ZAIM_EMAIL')
password = os.getenv('ZAIM_PASSWORD')
spreadsheet_key = os.getenv('GOOGLE_SPREADSHEET_KEY')
access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

now = datetime.now()

# Zaim Crawler
print("Start Crawling Zaim")
crawler = ZaimCrawler(email, password)
zaim_data = amount_from_zaim_data(crawler.get_data(now.year, now.month))
print(zaim_data)
crawler.close()
print("Done Crawling Zaim")

# Google Spreadsheet Fetcher
print("Start Fetching Google Spreadsheet Data")
fetcher = GSFetcher(service_account_file=service_account_file, spreadsheet_key=spreadsheet_key)
monthly_budget = amount_from_budget_data(fetcher.get_budget(now.year, now.month))
print(monthly_budget)
print("Done Fetching Google Spreadsheet Data")

# 予算計算
print("Start Calculating Budget")
remaining_budget = remaining_budget(zaim_data, monthly_budget)
print(remaining_budget)
remaining_budget_per_week = remaining_budget_per_week(remaining_budget, now.year, now.month)
print(remaining_budget_per_week)
print("Done Calculating Budget")

# LINE通知
print("Start Notifying LINE")
emoji = emoji_from_remaining_budget_per_week(monthly_budget, remaining_budget_per_week, now.year, now.month)
print(emoji)
send_line_notification(make_line_message_data(remaining_budget, remaining_budget_per_week, emoji, now), access_token)
print("Done Notifying LINE")
