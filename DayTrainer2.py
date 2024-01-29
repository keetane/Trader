import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ticker_dict = {
    'アドバンテスト' : '6857',
    'ソシオネクスト' : '6526',
    'リクルート' : '6098',
    'ルネサス' : '6723',
    'レーザーテック' : '6920',
    'ディスコ' : '6146',
    '日経レバダブル' : '1579',
    'さくらインターネット' : '3778',
    '三菱UFJ' : '8306',
}


# サイドバーでパラメータを入力
tickers = st.sidebar.selectbox('Tickers',
             options=ticker_dict.keys())
tickers = str(ticker_dict.get(tickers)) + '.T'

# SMA_short = st.sidebar.number_input('SMA_short', value=5)
# SMA_middle = st.sidebar.number_input('SMA_middle', value=25)
# SMA_long = st.sidebar.number_input('SMA_long', value=75)

# 基本情報取得
info = yf.Ticker(tickers)
st.title('Day Trainer')
st.write(info.info['longName'])


# 1分足のデータを取得
yesterday = datetime.now() - timedelta(10)
yesterday_str = yesterday.strftime('%Y-%m-%d')
today_str = datetime.now().strftime('%Y-%m-%d')

data = yf.download(
    tickers = tickers,
    start = yesterday_str,
    )
data['delta'] = data['Close'].diff()
data['%'] = data['Close'].pct_change() * 100
data['Close_-1'] = data['Close'].shift()


df = yf.download(tickers=tickers,
                #  start=yesterday_str,
                #  end=today_str,
                 interval='1m',
                #  period = '5d'
                 )
df['time'] = [t.time() for t in df.index]
df['day'] = [t.date() for t in df.index]

# close間の差を計算
df['delta'] = df['Close'].diff()
df['%'] = df['Close'].pct_change() * 100

# 前日との差を計算
df['Close_-1'] = df['day'].map(lambda x : data['Close_-1'][str(x)])
df['delta_yd'] = df['Close'] - df['Close_-1']
df['pct_yd'] = df['delta_yd']/df['Close_-1']*100


# # 9時と12時30分の取引量をリセット
# morning = time(9,0)
# noon = time(12,30)
# df.loc[df['time'] == noon, 'Volume'] = 0
# df.loc[df['time'] == morning, 'Volume'] = 0


# # SMAを計算 
# df["SMA_short"] = df["Close"].rolling(window=SMA_short).mean() 
# df["SMA_middle"] = df["Close"].rolling(window=SMA_middle).mean()
# df["SMA_long"] = df["Close"].rolling(window=SMA_long).mean()

# def macd(df):
#     FastEMA_period = 12  # 短期EMAの期間
#     SlowEMA_period = 26  # 長期EMAの期間
#     SignalSMA_period = 9  # SMAを取る期間
#     df["MACD"] = df["Close"].ewm(span=FastEMA_period).mean() - df["Close"].ewm(span=SlowEMA_period).mean()
#     df["Signal"] = df["MACD"].rolling(SignalSMA_period).mean()
#     return df

# def rsi(df):
#     # 前日との差分を計算
#     df_diff = df["Close"].diff(1)
 
#     # 計算用のDataFrameを定義
#     df_up, df_down = df_diff.copy(), df_diff.copy()
    
#     # df_upはマイナス値を0に変換
#     # df_downはプラス値を0に変換して正負反転
#     df_up[df_up < 0] = 0
#     df_down[df_down > 0] = 0
#     df_down = df_down * -1
    
#     # 期間14でそれぞれの平均を算出
#     df_up_sma14 = df_up.rolling(window=14, center=False).mean()
#     df_down_sma14 = df_down.rolling(window=14, center=False).mean()
 
#     # RSIを算出
#     df["RSI"] = 100.0 * (df_up_sma14 / (df_up_sma14 + df_down_sma14))
 
#     return df
 
# # MACDを計算する
# df = macd(df)
 
# # RSIを算出
# df = rsi(df)

# st.write(df.head())

# 日付選択
when = st.selectbox(
    'Select date',
    df['day'].unique(),
    # index=None,
)

df = df[df['day']==when]
st.dataframe(df.tail(1))
# st.write('株価終値 ' + str(df['Close'].iloc[-1]))
# st.write('前日比 ' + str(df['delta_yd'].iloc[-1]) + '  ,  ' + str(df['%'].iloc[-1].round(2)) + ' %')

df = df.between_time('09:00', '10:00')

# My Art! we define some variables in order to make the code undertandable

play_button = {
    "args": [
        None, 
        {
            "frame": {"duration": 2000, "redraw": True},
            "fromcurrent": True, 
            "transition": {"duration": 1000000000,"easing": "quadratic-in-out"}
        }
    ],
    "label": "Play",
    "method": "animate"
}

pause_button = {
    "args": [
        [None], 
        {
            "frame": {"duration": 0, "redraw": False},
            "mode": "immediate",
            "transition": {"duration": 0}
        }
    ],
    "label": "Pause",
    "method": "animate"
}

sliders_steps = [
    {"args": [
        [0, i], # 0, in order to reset the image, i in order to plot frame i
        {"frame": {"duration": 300, "redraw": True},
         "mode": "immediate",
         "transition": {"duration": 300}}
    ],
    "label": i,
    "method": "animate"}
    for i in range(len(df))      
]

sliders_dict = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 20},
        "prefix": "candle:",
        "visible": True,
        "xanchor": "right"
    },
    "transition": {"duration": 300, "easing": "cubic-in-out"},
    "pad": {"b": 10, "t": 50},
    "len": 0.9,
    "x": 0.1,
    "y": 0,
    "steps": sliders_steps,
}

initial_plot = go.Candlestick(
    x=df.time, 
    open=df.Open, 
    high=df.High, 
    low=df.Low, 
    close=df.Close
)

first_i_candles = lambda i: go.Candlestick(
    x=df.time, 
    open=df.Open[:i], 
    high=df.High[:i], 
    low=df.Low[:i], 
    close=df.Close[:i]
)

fig = go.Figure(
    data=[initial_plot],
    layout=go.Layout(
        xaxis=dict(title='time', rangeslider=dict(visible=False)),
        title="Candles over time",
        updatemenus= [dict(type="buttons", buttons=[play_button, pause_button])],
        sliders= [sliders_dict]
    ),
    frames=[
        go.Frame(data=[first_i_candles(i)], name=f"{i}") # name, I imagine, is used to bind to frame i :) 
        for i in range(len(df))
    ],

)

# fig.show()

st.plotly_chart(fig)