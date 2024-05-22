#%%
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, time

# tickerリストの読み込み
df = pd.read_csv('tickers.csv', index_col=0)
df['code'] = df['code'].astype(str)
ticker_dict = df.to_dict()['code']


# 日付の取得
past = datetime.now() - timedelta(10)
past_str = past.strftime('%Y-%m-%d')

for ticker in list(ticker_dict.values()):

    # データの取得
    data = yf.download(
        tickers = ticker + '.T',
        start = past_str,
        )
    data['delta'] = data['Close'].diff()
    data['%'] = data['Close'].pct_change() * 100
    data['Close_-1'] = data['Close'].shift()

    df = yf.download(tickers=ticker + '.T',
                    interval='1m',
                    )

    # 時間を追加
    df['time'] = [t.time() for t in df.index]
    df['day'] = [t.date() for t in df.index]

    # close間の差を計算
    df['delta'] = df['Close'].diff()
    df['%'] = df['Close'].pct_change() * 100

    # 前日との差を計算
    df['Close_-1'] = df['day'].map(lambda x : data['Close_-1'][str(x)])
    df['delta_yd'] = df['Close'] - df['Close_-1']
    df['pct_yd'] = df['delta_yd']/df['Close_-1']*100

    # SMAを計算 
    df["SMA_short"] = df["Close"].rolling(window=10).mean() 
    df["SMA_middle"] = df["Close"].rolling(window=25).mean()
    df["SMA_long"] = df["Close"].rolling(window=75).mean()

    def macd(df):
        FastEMA_period = 12  # 短期EMAの期間
        SlowEMA_period = 26  # 長期EMAの期間
        SignalSMA_period = 9  # SMAを取る期間
        df["MACD"] = df["Close"].ewm(span=FastEMA_period).mean() - df["Close"].ewm(span=SlowEMA_period).mean()
        df["Signal"] = df["MACD"].rolling(SignalSMA_period).mean()
        return df
    

    def rsi(df):
        # 前日との差分を計算
        df_diff = df["Close"].diff(1)
    
        # 計算用のDataFrameを定義
        df_up, df_down = df_diff.copy(), df_diff.copy()
        
        # df_upはマイナス値を0に変換
        # df_downはプラス値を0に変換して正負反転
        df_up[df_up < 0] = 0
        df_down[df_down > 0] = 0
        df_down = df_down * -1
        
        # 期間14でそれぞれの平均を算出
        df_up_sma14 = df_up.rolling(window=14, center=False).mean()
        df_down_sma14 = df_down.rolling(window=14, center=False).mean()
    
        # RSIを算出
        df["RSI"] = 100.0 * (df_up_sma14 / (df_up_sma14 + df_down_sma14))
    
        return df
    
    # MACDを計算する
    df = macd(df)
    
    # RSIを算出
    df = rsi(df)

    # tickerをdfに追加
    df['ticker'] = ticker

    # 保存データとの結合
    try:
        df = pd.concat(
            [pd.read_csv(
                '~/Documents/trader/1min/' + ticker + '.csv',
                parse_dates=['Datetime'], 
                index_col='Datetime'
                ), 
            df])
    except:
        pass

    # データを保存
    df.drop_duplicates().to_csv('~/Documents/trader/1min/' + ticker + '.csv')


for ticker in list(ticker_dict.values()):

    # データの取得
    df = yf.download(
        tickers = ticker + '.T',
        # start = past_str,
        interval='1d'
        )
    df['delta'] = df['Close'].diff().fillna(0)
    df['%'] = df['Close'].pct_change().fillna(0) * 100
    df['Close_-1'] = df['Close'].shift().fillna(0)

    # SMAを計算 
    df["SMA_short"] = df["Close"].rolling(window=10).mean() 
    df["SMA_middle"] = df["Close"].rolling(window=25).mean()
    df["SMA_long"] = df["Close"].rolling(window=75).mean()

    def macd(df):
        FastEMA_period = 12  # 短期EMAの期間
        SlowEMA_period = 26  # 長期EMAの期間
        SignalSMA_period = 9  # SMAを取る期間
        df["MACD"] = df["Close"].ewm(span=FastEMA_period).mean() - df["Close"].ewm(span=SlowEMA_period).mean()
        df["Signal"] = df["MACD"].rolling(SignalSMA_period).mean()
        return df
    

    def rsi(df):
        # 前日との差分を計算
        df_diff = df["Close"].diff(1)
    
        # 計算用のDataFrameを定義
        df_up, df_down = df_diff.copy(), df_diff.copy()
        
        # df_upはマイナス値を0に変換
        # df_downはプラス値を0に変換して正負反転
        df_up[df_up < 0] = 0
        df_down[df_down > 0] = 0
        df_down = df_down * -1
        
        # 期間14でそれぞれの平均を算出
        df_up_sma14 = df_up.rolling(window=14, center=False).mean()
        df_down_sma14 = df_down.rolling(window=14, center=False).mean()
    
        # RSIを算出
        df["RSI"] = 100.0 * (df_up_sma14 / (df_up_sma14 + df_down_sma14))
    
        return df
    
    # MACDを計算する
    df = macd(df)
    
    # RSIを算出
    df = rsi(df)

    # tickerをdfに追加
    df['ticker'] = ticker

    # 保存データとの結合
    try:
        df = pd.concat(
            [pd.read_csv(
                './1day/' + ticker + '.csv',
                parse_dates=['Datetime'], 
                index_col='Datetime'
                ), 
            df])
    except:
        pass

    # データを保存
    df.drop_duplicates().to_csv('./1day/' + ticker + '.csv')
# %%
