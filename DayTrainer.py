#%%
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, time
import plotly.graph_objects as go
from random import random

st.title('Day Trainer')

# tickerリストの読み込み
ticker_dict = pd.read_csv('tickers.csv', index_col=0).to_dict()['code']

# 銘柄を選択
tickers = st.selectbox('Tickers',
             options=ticker_dict.keys(),
             index=9)

csv = '1min/' + str(ticker_dict[tickers]) + '.csv'

df = pd.read_csv(csv, index_col=0, parse_dates=True)

# 日付を選択
day = st.selectbox('day',
             options=df['day'].unique(),
             index=len(df['day'].unique())-1
             )

# 前日終値の表示
df = df[df['day']==day]
st.write('前日株価終値 ' + str(df['Close'].iloc[-1]))

# 分足の選択
interval = st.selectbox('時間軸',
                    ['1m', '5m'])
if interval == '1m':
    df = df.between_time('09:00', '10:00')
    length = 61
else:
    df = df.between_time('09:00', '11:30')
    length = 31

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

# initial_plot = go.Candlestick(
#     x=df.time, 
#     open=df.Open, 
#     high=df.High, 
#     low=df.Low, 
#     close=df.Close
# )

first_i_candles = lambda i: go.Candlestick(
    x=df.time, 
    open=df.Open[:i], 
    high=df.High[:i], 
    low=df.Low[:i], 
    close=df.Close[:i]
)

fig = go.Figure(
    # data=[initial_plot],
    data=[first_i_candles(0)],
    layout=go.Layout(
        xaxis=dict(title='time', rangeslider=dict(visible=False)),
        title="Candles over time",
                updatemenus= [
            dict(
                type="buttons", 
                buttons=[play_button, pause_button],
                direction = 'right',
                y=1.1,
                x=0.1,
                xanchor='right',
                yanchor='top',
                )],
        sliders= [sliders_dict]
    ),

    frames=[
        go.Frame(data=[first_i_candles(i)], name=f"{i}") # name, I imagine, is used to bind to frame i :) 
        for i in range(len(df))

    ],

)
# 開始値を取得
start_value = df['Open'].iloc[0]
# 最大値と最小値の差を計算
max_diff = df['High'].max() - df['Low'].min()
# 開始値から+-最大値幅を計算
lower_bound = start_value - max_diff
upper_bound = start_value + max_diff

# lower_bound = lower_bound / 1.007
# upper_bound = upper_bound * 1.007

# y軸の範囲を設定
fig.update_yaxes(range=[lower_bound, upper_bound])
fig.update_xaxes(range=[-1,length])
fig.update_layout(width=500)

# fig.show()

st.plotly_chart(fig)
