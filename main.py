import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# === 1. 設定投資組合 (已修正代碼格式) ===
# Yahoo Finance 格式修正：
# RDS.B -> SHEL
# BBL -> BHP
# BRK.B -> BRK-B (這是最常錯的，Python 裡要用減號)
portfolio = {
    "ETF (指數/股息/債券)": [
        'IVV', 'SPY', 'VTI', 'VIG', 'VYM', 'VDC', 
        'VCR', 'VTV', 'QQQ', 'FVD', 'VNQ', 'LQD'
    ],
    "核心個股 (壟斷/價值/農糧)": [
        'BHP', 'NOV', 'ADM'
    ],
    "石油巨獸與高股息個股": [
        'XOM', 'CVX', 'BP', 'SHEL', 
        'PFE', 'JNJ', 'PG', 'ABBV', 'BMY', 
        'MSFT', 'IBM', 'QCOM', 'CSCO', 
        'WFC', 'VLO', 'BRK-B'
    ]
}

tw = pytz.timezone('Asia/Taipei')
current_time = datetime.now(tw).strftime('%Y-%m-%d %H:%M:%S')

def get_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        # 抓取過去 10 年數據
        df = stock.history(period="10y")
        
        if df.empty:
            print(f"Warning: No data for {ticker}")
            return None, None

        # 轉成月線 (Month End)，並計算當月開盤、最高、最低、收盤
        monthly = df['Close'].resample('ME').last().to_frame()
        monthly['Open'] = df['Open'].resample('ME').first()
        monthly['High'] = df['High'].resample('ME').max()
        monthly['Low'] = df['Low'].resample('ME').min()
        
        # 計算單月漲跌幅
        monthly['Change(%)'] = ((monthly['Close'] - monthly['Open']) / monthly['Open'] * 100).round(2)
        
        # 格式整理
        monthly.index = monthly.index.strftime('%Y-%m')
        monthly = monthly.sort_index(ascending=False) # 最新月份在上面
        
        # 計算統計數據
        total_return = ((df['Close'].iloc[-1] - df['Open'].iloc[0]) / df['Open'].iloc[0] * 100)
        
        stats = {
            '目前股價': round(df['Close'].iloc[-1], 2),
            '10年最高價': round(df['High'].max(), 2),
            '10年最低價': round(df['Low'].min(), 2),
            '區間總報酬率(%)': round(total_return, 2)
        }
        return stats, monthly
        
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return None, None

# === 2. 生成 HTML 報告 ===
html_parts = []
html_header = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>價值投資月線報表</title>
<style>
    body {{ font-family: "Segoe UI", sans-serif; padding: 20px; background-color: #f4f4f9; color: #333; }}
    h1 {{ text-align: center; color: #2c3e50; }}
    .category-title {{ background-color: #2c3e50; color: white; padding: 10px; border-radius: 5px; margin-top: 40px; }}
    .stock-card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
    h3 {{ border-bottom: 2px solid #eee; padding-bottom: 5px; color: #2980b9; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
    th {{ background-color: #ecf0f1; }}
    .stats-row {{ display: flex; gap: 20px; margin-bottom: 10px; font-weight: bold; color: #555; }}
</style>
</head>
<body>
    <h1>核心資產 10年期月線報告</h1>
    <p style="text-align:center">更新時間: {current_time}</p>
    <p>說明：此表包含 ETF、核心壟斷股與高股息股的月度波動數據。</p>
"""
html_parts.append(html_header)

# 雙層迴圈：先跑分類，再跑個股
for category, ticker_list in portfolio.items():
    html_parts.append(f"<h2 class='category-title'>{category}</h2>")
    
    for t in ticker_list:
        print(f"Processing {t}...") # 讓您在 Action log 看到進度
        stats, df_table = get_data(t)
        
        if stats:
            # 統計數據顯示
            stats_html = f"""
            <div class="stats-row">
                <span>目前: {stats['目前股價']}</span>
                <span>最高: {stats['10年最高價']}</span>
                <span>最低: {stats['10年最低價']}</span>
                <span>總報酬: {stats['區間總報酬率(%)']}%</span>
            </div>
            """
            
            # 表格顯示 (限制顯示最近 120 個月，即 10 年)
            table_html = df_table.head(120).to_html(classes='table', border=0)
            
            card = f"""
            <div class="stock-card">
                <h3>{t}</h3>
                {stats_html}
                {table_html}
            </div>
            """
            html_parts.append(card)

html_parts.append("</body></html>")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write("\n".join(html_parts))

print("報表生成完畢！")
