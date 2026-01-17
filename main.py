import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# === 投資組合清單 (已修正代號) ===
portfolio = {
    "ETF": ['IVV', 'SPY', 'VTI', 'VIG', 'VYM', 'VDC', 'VCR', 'VTV', 'QQQ', 'FVD', 'VNQ', 'LQD'],
    "Core": ['BHP', 'NOV', 'ADM'],
    "Oil_HighDiv": ['XOM', 'CVX', 'BP', 'SHEL', 'PFE', 'JNJ', 'PG', 'ABBV', 'BMY', 'MSFT', 'IBM', 'QCOM', 'CSCO', 'WFC', 'VLO', 'BRK-B']
}

tw = pytz.timezone('Asia/Taipei')
current_time = datetime.now(tw).strftime('%Y-%m-%d %H:%M:%S')

def get_data_for_csv(ticker, category):
    try:
        stock = yf.Ticker(ticker)
        # 抓取 10 年數據
        df = stock.history(period="10y")
        
        if df.empty:
            print(f"警告：{ticker} 抓不到數據")
            return None

        # 轉成月線 (Month End)
        monthly = df['Close'].resample('ME').last().to_frame()
        monthly['High'] = df['High'].resample('ME').max()
        monthly['Low'] = df['Low'].resample('ME').min()
        monthly['Open'] = df['Open'].resample('ME').first()
        
        # 整理欄位 (Flatten)
        monthly['Ticker'] = ticker
        monthly['Category'] = category
        monthly['Date'] = monthly.index.strftime('%Y-%m-%d')
        
        # 計算當月漲跌幅
        monthly['Change_Pct'] = ((monthly['Close'] - monthly['Open']) / monthly['Open'] * 100).round(2)
        
        # 只保留需要的欄位，順序排好
        return monthly[['Date', 'Category', 'Ticker', 'Close', 'High', 'Low', 'Change_Pct']]
    except Exception as e:
        print(f"錯誤：處理 {ticker} 時發生異常: {e}")
        return None

# === 主程式 ===
all_dfs = []
print("開始抓取數據...")

for category, tickers in portfolio.items():
    print(f"正在處理分類：{category}...")
    for t in tickers:
        df = get_data_for_csv(t, category)
        if df is not None:
            all_dfs.append(df)

# 合併並輸出
if all_dfs:
    final_df = pd.concat(all_dfs)
    
    # 1. 輸出 CSV (這是給 Google Sheet 吃的關鍵檔案)
    final_df.to_csv('stock_data.csv', index=False)
    print(f"成功生成 stock_data.csv，共 {len(final_df)} 筆數據")

    # 2. 輸出簡易 HTML (讓您確認 Action 有在跑)
    html = f"""
    <html>
    <head><meta charset='utf-8'></head>
    <body>
    <h1>更新完成</h1>
    <p>時間: {current_time}</p>
    <p>CSV 數據已生成，請去 Google Sheets 使用 IMPORTDATA 讀取。</p>
    </body>
    </html>
    """
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

print("程式執行完畢")
