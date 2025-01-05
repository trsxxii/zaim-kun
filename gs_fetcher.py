import gspread
from google.oauth2.service_account import Credentials
from constants import *
from budget_utils import *

class GSFetcher:
    def __init__(self, service_account_info, spreadsheet_key):
        self.credentials = Credentials.from_service_account_info(
            service_account_info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        self.client = gspread.authorize(self.credentials)
        self.spreadsheet = self.client.open_by_key(spreadsheet_key)

    def __init__(self, service_account_file, spreadsheet_key):
        self.credentials = Credentials.from_service_account_file(
            service_account_file, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        self.client = gspread.authorize(self.credentials)
        self.spreadsheet = self.client.open_by_key(spreadsheet_key)

    def get_budget(self, year, month):
        # 指定年のシートを取得
        sheet = self.spreadsheet.worksheet(f"{year}年")

        # 月が記載された行のデータを取得
        header_row = sheet.row_values(2)

        # 指定月の文字列
        search_string = f"{month}月"

        # 最初に一致する文字列で検索して列を特定する
        column_index = None
        for idx, value in enumerate(header_row):
            if search_string in value:
                column_index = idx + 1  # gspreadは1-indexedなので +1
                break

        # 一致する列が見つかった場合
        if column_index:                
            # シート内の全データを取得
            rows = sheet.get_all_values()
            
            # 各条件に基づく行データを格納する辞書
            result = {}

            
            for row_num, row in enumerate(rows, start=1):
                category_column = row[3] # カテゴリ
                badget_column = row[column_index - 1] # 予算
                badget_int = convert_to_int(badget_column)
                if category_column == FOOD:
                    result[FOOD] = badget_int
                elif category_column == LEISURE:
                    result[LEISURE] = badget_int
                elif category_column == PAPA_FREE:
                    result[PAPA_FREE] = badget_int
                elif category_column == MAMA_FREE:
                    result[MAMA_FREE] = badget_int
        else:
            print(f"'{search_string}' 見つかりませんでした。")
        
        return result
