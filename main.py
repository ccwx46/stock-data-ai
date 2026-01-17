import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# === 1. 設定投資組合 ===
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
        df = stock.history(period="10y")
        if df.empty: return None, None

        # 月線處理
        monthly = df['Close'].resample('ME').last().to_frame()
        monthly['Open'] = df['Open'].resample('ME').first()
        monthly['High'] = df['High'].resample('ME').max()
        monthly['Low'] = df['Low'].resample('ME').min()
        monthly['Change(%)'] = ((monthly['Close'] - monthly['Open']) / monthly['Open'] * 100).round(2)
        
        # 格式整理
        monthly.index = monthly.index.strftime('%Y-%m-%d')
        monthly = monthly.sort_index(ascending=False)
        
        # 統計數據
        stats = {
            '目前股價': round(df['Close'].iloc[-1], 2),
            '10年最高': round(df['High'].max(), 2),
            '10年最低': round(df['Low'].min(), 2)
        }
        return stats, monthly
    except:
        return None, None

# === 2. 生成 HTML 與 CSV ===
html_parts = []
csv_data = []

html_header = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>價值投資日報</title>
<style>
    body {{ font-family: sans-serif; padding: 20px; color: #333; }}
    h1 {{ text-align: center; color: #2c3e50; }}
    .category {{ background: #2c3e50; color: white; padding: 10px; margin-top: 30px; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }}
    th, td {{ border: 1px solid #ddd; padding: 6px; text-align: center; }}
    th {{ background-color: #f2f2f2; }}
</style>
</head>
<body>
    <h1>投資組合報告 ({current_time})</h1>
"""
html_parts.append(html_header)

print("開始抓取數據...")

for category, ticker_list in portfolio.items():
    html_parts.append(f"<h2 class='category'>{category}</h2>")
    
    for t in ticker_list:
        print(f"Processing {t}...")
        stats, df_table = get_data(t)
        
        if stats:
            # 1. 加入 HTML
            # 限制顯示最近 60 個月 (5年) 避免網頁太長，AI 讀最近的就夠了
            table_html = df_table.head(60).to_html(classes='table')
            
            card = f"""
            <div class='stock'>
                <h3>{t} (現價: {stats['目前股價']} | 高: {stats['10年最高']} | 低: {stats['10年最低']})</h3>
                {table_html}
            </div>
            """
            html_parts.append(card)
            
            # 2. 加入 CSV (備份用)
            df_table['Ticker'] = t
            df_table['Category'] = category
            df_table['Date'] = df_table.index
            csv_data.append(df_table)

# 結束 HTML
html_parts.append("</body></html>")

# 輸出檔案
with open('index.html', 'w', encoding='utf-8') as f:
    f.write("\n".join(html_parts))

if csv_data:
    final_df = pd.concat(csv_data)
    final_df.to_csv('stock_data.csv', index=False)

print("報表生成完畢！")
