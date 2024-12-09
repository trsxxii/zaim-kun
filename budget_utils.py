import calendar
import textwrap
from datetime import datetime, timedelta
from constants import *
from dataclasses import dataclass

@dataclass
class AmountData:
    food: int
    leisure: int
    papa_free: int
    mama_free: int

"""Zaimで取得した使った金額をAmountDataに変換する"""
def amount_from_zaim_data(data):
    return AmountData(
        sum(item['amount'] for item in data if item['category'] == FOOD),
        sum(item['amount'] for item in data if item['category'] == LEISURE),
        sum(item['amount'] for item in data if item['category'] == PAPA_FREE),
        sum(item['amount'] for item in data if item['category'] == MAMA_FREE)
    )

"""Spreadsheetで取得した月間予算をAmountDataに変換する"""
def amount_from_budget_data(data):
    return AmountData(
        data[FOOD],
        data[LEISURE],
        data[PAPA_FREE],
        data[MAMA_FREE]
    )

"""現在日を起点に残りの年月の土曜日の数を計算する"""
def remaining_saturdays(year, month):
    now = datetime.combine(datetime.now().date(), datetime.min.time())
    _, last_day = calendar.monthrange(year, month)  # 月末日を取得
    
    # 現在日から月末までのdatetimeリストを生成
    remaining_days = [
        now + timedelta(days=i)
        for i in range((datetime(year, month, last_day) - now).days + 1)
    ]
    
    # 土曜日の数をカウント
    saturdays_count = sum(1 for day in remaining_days if day.weekday() == 5)
    
    return saturdays_count

"""年月の土曜日の数を計算する"""
def count_saturdays(year, month):
    weekdays = calendar.monthcalendar(year, month)
    return sum(1 for week in weekdays if week[calendar.SATURDAY] != 0)

"""intを金額表示に変換する"""
def format_currency(value):
    return f"¥{value:,.0f}"

"""金額表示をintに変換する"""
def convert_to_int(value):
    try:
        return int(value.replace('¥', '').replace(',', ''))
    except ValueError:
        return 0
    
"""月間予算と1週間毎の予算を比較して絵文字を返却する"""
def budget_comparison(saturday_count, monthly_budget_element, remaining_budget_element_per_week):
    if remaining_budget_element_per_week <= 0:
        return '⚡'
    
    weekly_budget_from_month = monthly_budget_element / saturday_count
    
    if weekly_budget_from_month == remaining_budget_element_per_week:
        return '🌤️'
    elif weekly_budget_from_month > remaining_budget_element_per_week:
        return '🌞'
    else:
        return '☔'

"""月間予算と使った金額から残りの予算を計算する"""
def remaining_budget(zaim, monthly_budget):
    return AmountData(
        monthly_budget.food - zaim.food,
        monthly_budget.leisure - zaim.leisure,
        monthly_budget.papa_free - zaim.papa_free,
        monthly_budget.mama_free - zaim.mama_free
    )

"""残りの予算と残りの土曜日から1週間毎に使える予算を計算する"""
def remaining_budget_per_week(remaining_budget, year, month):
    remaining_saturdays_count = remaining_saturdays(year, month)
    if remaining_saturdays_count == 0:
        return remaining_budget
    else:
        return AmountData(
            remaining_budget.food / remaining_saturdays_count,
            remaining_budget.leisure / remaining_saturdays_count,
            remaining_budget.papa_free / remaining_saturdays_count,
            remaining_budget.mama_free / remaining_saturdays_count
        )

"""1週間毎に使える予算から絵文字マップを作成する"""
def emoji_from_remaining_budget_per_week(monthly_budget, remaining_budget_per_week, year, month):
    saturdays_count = count_saturdays(year, month)
    return {
        FOOD: budget_comparison(saturdays_count, monthly_budget.food, remaining_budget_per_week.food),
        LEISURE: budget_comparison(saturdays_count, monthly_budget.leisure, remaining_budget_per_week.leisure),
        PAPA_FREE: budget_comparison(saturdays_count, monthly_budget.papa_free, remaining_budget_per_week.papa_free),
        MAMA_FREE: budget_comparison(saturdays_count, monthly_budget.mama_free, remaining_budget_per_week.mama_free)
    }

"""LINEのメッセージを作成する"""
def make_line_messages(remaining_budget, remaining_budget_per_week, emoji, now):
    day_of_week = ['月', '火', '水', '木', '金', '土', '日'][now.weekday()]
    remaining_budget_message = f"""
        {now.strftime(f"%Y年%m月%d日({day_of_week})")}
        残り予算をお知らせ

        🛒食日費: {format_currency(remaining_budget.food)}
        🚗娯楽費: {format_currency(remaining_budget.leisure)}
        👨パパお小遣い: {format_currency(remaining_budget.papa_free)}
        👩ママお小遣い: {format_currency(remaining_budget.mama_free)}
    """

    remaining_saturdays_count = remaining_saturdays(now.year, now.month)
    remaining_budget_per_week_message = ''
    if remaining_saturdays_count == 0:
        remaining_budget_per_week_message = """
            今月はもう週末がないよ。残りは慎重に使おうね
        """
    else:
        remaining_budget_per_week_message = f"""
            今月は残り{remaining_saturdays_count}回週末があるよ。
            1週間毎に使える予算はコチラ！

            🛒食日費: {format_currency(remaining_budget_per_week.food)} {emoji[FOOD]}
            🚗娯楽費: {format_currency(remaining_budget_per_week.leisure)} {emoji[LEISURE]}
            👨パパお小遣い: {format_currency(remaining_budget_per_week.papa_free)} {emoji[PAPA_FREE]}
            👩ママお小遣い: {format_currency(remaining_budget_per_week.mama_free)} {emoji[MAMA_FREE]}
        """
    
    return [textwrap.dedent(remaining_budget_message), textwrap.dedent(remaining_budget_per_week_message)]

    