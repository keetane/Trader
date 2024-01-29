import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, time
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# サイドバーでパラメータを入力
tickers = st.sidebar.text_input('Tickers', '6857') + '.T'
SMA_short = st.sidebar.number_input('SMA_short', value=5)
SMA_middle = st.sidebar.number_input('SMA_middle', value=25)
SMA_long = st.sidebar.number_input('SMA_long', value=75)
st.sidebar.write('6098 リクルート')
st.sidebar.write('1579 日経レバダブル')
st.sidebar.write('6723 ルネサス')
st.sidebar.write('6857 アドバンテス')

# 基本情報取得
info = yf.Ticker(tickers)
st.title('Trade Analizer')
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


# 9時と12時30分の取引量をリセット
morning = time(9,0)
noon = time(12,30)
df.loc[df['time'] == noon, 'Volume'] = 0
df.loc[df['time'] == morning, 'Volume'] = 0


# SMAを計算 
df["SMA_short"] = df["Close"].rolling(window=SMA_short).mean() 
df["SMA_middle"] = df["Close"].rolling(window=SMA_middle).mean()
df["SMA_long"] = df["Close"].rolling(window=SMA_long).mean()

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

# st.write(df.head())

# 日付選択
when = st.selectbox(
    'Select date',
    df['day'].unique(),
    index=None,
)

df = df[df['day']==when]
st.dataframe(df.tail(1))
# st.write('株価終値 ' + str(df['Close'].iloc[-1]))
# st.write('前日比 ' + str(df['delta_yd'].iloc[-1]) + '  ,  ' + str(df['%'].iloc[-1].round(2)) + ' %')



# figを定義
fig = make_subplots(
    rows=4, 
    cols=1, 
    shared_xaxes=True, 
    vertical_spacing=0.05, 
    row_width=[0.2, 0.2, 0.2, 0.7], 
# x_title="Time"
)
 
# Candlestick 
fig.add_trace(
    go.Candlestick(
        x=df.time, 
        open=df["Open"], 
        high=df["High"], 
        low=df["Low"], 
        close=df["Close"], 
        showlegend=False
        ),
    row=1, col=1
)

# 移動平均線
fig.add_trace(go.Scatter(x=df.time, y=df["SMA_short"], name="SMA_short", mode="lines"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.time, y=df["SMA_middle"], name="SMA_middle", mode="lines"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.time, y=df["SMA_long"], name="SMA_long", mode="lines"), row=1, col=1)

# MACD
fig.add_trace(go.Scatter(x=df.time, y=df["MACD"], mode="lines", showlegend=False), row=3, col=1)
fig.add_trace(go.Scatter(x=df.time, y=df["Signal"], mode="lines", showlegend=False), row=3, col=1)
 
# RSI
fig.add_trace(go.Scatter(x=df.time, y=df["RSI"], mode="lines", showlegend=False), row=4, col=1)

# Volume
fig.add_trace(
    go.Bar(x=df.time, y=df["Volume"], showlegend=False, marker_color='orange'),
    row=2, col=1
)

# ラベル名の設定とフォーマット変更（カンマ区切り）
fig.update_yaxes(separatethousands=True, title_text="株価", row=1, col=1) 
fig.update_yaxes(title_text="出来高", row=2, col=1)
fig.update_yaxes(title_text="MACD", row=3, col=1)
fig.update_yaxes(title_text="RSI", row=4, col=1)


fig.update(layout_xaxis_rangeslider_visible=False) #追加
fig.update_layout(
    width=1000,
    height=700,
    xaxis=dict(dtick=1000)
    ) # x軸の表示間隔を30ごとに設定
# fig.show()

st.plotly_chart(fig)