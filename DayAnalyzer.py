#%%
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta, time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import glob

st.title('Day Analyzer')

# # 履歴のファイルを読み込み
# his = pd.read_csv('./history/history.csv',
#                     parse_dates=['注文日時'], 
#                     index_col='注文日時'
#                     )

# # DLしたファイルの読み込み
# file_list = glob.glob('../../Downloads/stockorder(JP)_*')
# for file in file_list:
#     dft = pd.read_csv(file, encoding='cp932')
#     # '注文日時'カラムをdatetimeに変換
#     dft['注文日時'] = pd.to_datetime(dft['注文日時'], format='%m/%d %H:%M')
#     # 注文日時の年を2024年に変更
#     dft['注文日時'] = dft['注文日時'].apply(lambda dt: dt.replace(year=2024))
#     # '注文日時'カラムをインデックスに設定
#     dft.set_index('注文日時', inplace=True)
#     # 文字列のみの行を削除
#     dft = dft[dft['約定単価[円]'] != '-']
#     # 文字列を数値に変換
#     dft['約定単価[円]'] = dft['約定単価[円]'].str.replace(',', '').astype(float)
#     dft['現在値[円]'] = dft['現在値[円]'].str.replace(',', '').astype(float)
#     try:
#         dft['約定数量[株/口]'] = dft['約定数量[株/口]'].str.replace(',','').astype(float)
#     except AttributeError:
#         pass  # '約定数量[株/口]'列が文字列を含まない場合、何もせずにスキップします
#     his = pd.concat([his, dft])

# his = his.drop_duplicates().sort_index(ascending=False)
# his.to_csv('./history/history.csv')


# アップロード版のテスト
his = st.file_uploader('注文履歴のcsvファイルをアップロードしてください。', type='csv')
his = pd.read_csv(
    his, 
    encoding='cp932', 
    # parse_dates=['注文日時'], 
    # index_col='注文日時'
    ).sort_index(ascending=True)
try:
    his['約定数量[株/口]'] = his['約定数量[株/口]'].str.replace(',','').astype(float)
except AttributeError:
    pass  # '約定数量[株/口]'列が文字列を含まない場合、何もせずにスキップします

# '注文日時'カラムをdatetimeに変換
his['注文日時'] = pd.to_datetime(his['注文日時'], format='%m/%d %H:%M')
# 注文日時の年を2024年に変更
his['注文日時'] = his['注文日時'].apply(lambda dt: dt.replace(year=2024))
# '注文日時'カラムをインデックスに設定
his.set_index('注文日時', inplace=True)

#%%
# 直近1週間の日付のselect list
when = st.selectbox(
    '日付を選んでください',
    [str(date) for date in pd.unique(his.index.date).tolist()][0:5]
)


# 今日の日付に該当するデータを抽出
columns=['注文番号', '銘柄', '銘柄コード・市場', '取引', '売買', '約定数量[株/口]', '注文単価[円]', '約定単価[円]', '約定代金[円]']
his.sort_index(inplace=True)
his = his.loc[when][columns]

# enumerateを使用してインデックスと要素のペアを取得し、辞書に変換
# companies_dict = {i: company for i, company in enumerate(his['銘柄'].unique(), 1)}
companies_dict = {row['銘柄']:row['銘柄コード・市場'][:4] for index, row in his[['銘柄', '銘柄コード・市場']].drop_duplicates().iterrows()}


st.text('今日の売買回数は' + str(len(his)))
Ticker = st.selectbox('今日の売買銘柄', companies_dict.keys())

#%%
# パラメータを入力
# # tickerリストの読み込み
ticker_dict = pd.read_csv('tickers.csv', index_col=0).to_dict()['code']
tickers = str(ticker_dict.get(Ticker)) + '.T'
interval = st.selectbox('時間軸',
                    ['1m', '5m'])


#%%
# 1分足のデータを取得
yesterday = datetime.now() - timedelta(10)
yesterday_str = yesterday.strftime('%Y-%m-%d')
today_str = datetime.now().strftime('%Y-%m-%d')
#%%
data = yf.download(
    tickers = tickers,
    start = yesterday_str,
    )
data['delta'] = data['Close'].diff()
data['%'] = data['Close'].pct_change() * 100
data['Close_-1'] = data['Close'].shift()

#%%
df = yf.download(tickers=tickers,
                #  start=yesterday_str,
                #  end=today_str,
                #  interval='1m',
                 interval=interval,
                 period = '5d'
                 )
df['time'] = [t.time() for t in df.index]
df['day'] = [t.date() for t in df.index]

# close間の差を計算
df['delta'] = df['Close'].diff()
df['%'] = df['Close'].pct_change() * 100

# # 前日との差を計算
# df['Close_-1'] = df['day'].map(lambda x : data['Close_-1'][str(x)])
# df['delta_yd'] = df['Close'] - df['Close_-1']
# df['pct_yd'] = df['delta_yd']/df['Close_-1']*100


df = df.loc[when]

# 分足の選択
if interval == '1m':
    df = df.between_time('09:00', '10:00')
    length = 61
else:
    df = df.between_time('09:00', '11:30')
    length = 31

# scatter plot用のデータフレーム
df_scatter = his[his['銘柄']==Ticker]

# マーカーの色と形を設定する関数
def set_color(row):
    if row['売買'] == '買建':
        return 'green'
    elif row['売買'] == '売埋':
        return 'green'
    elif row['売買'] == '売建':
        return 'red'
    elif row['売買'] == '買埋':
        return 'red'
    else:
        return ''  # デフォルトのマーカー

def set_marker(row):
    if row['売買'] == '買建':
        return 'triangle-up'
    elif row['売買'] == '売埋':
        return 'circle'
    elif row['売買'] == '売建':
        return 'triangle-down'
    elif row['売買'] == '買埋':
        return 'circle'
    else:
        return ''  # デフォルトのマーカー

# DataFrameの各行に対してマーカーの設定を適用
df_scatter['color'] = df_scatter.apply(set_color, axis=1)
df_scatter['marker'] = df_scatter.apply(set_marker, axis=1)


# サブプロットを作成
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                    vertical_spacing=0.03, subplot_titles=('ローソク足', '取引量'), 
                    row_width=[0.2, 0.7])

# ローソク足チャートを追加
fig.add_trace(go.Candlestick(x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                ), row=1, col=1)

# scatter plotを追加
fig.add_trace(go.Scatter(x=df_scatter.index, y=df_scatter['約定単価[円]'], 
                         mode='markers',
                         marker=dict(size=df_scatter['約定数量[株/口]'],
                                     sizemode='area',  # サイズを面積として解釈
                                     sizeref=2.*max(df_scatter['約定数量[株/口]'])/(20.**2),  # サイズスケーリングのための参照値
                                     sizemin=1,  # マーカーの最小サイズ
                                     color=df_scatter['color'],  # マーカーの色
                                     symbol=df_scatter['marker']  # マーカーの形
                                     )),
                                      row=1, col=1
                                      )

# histgramを追加
fig.add_trace(go.Bar(
    x=df.index,
    y=df['Volume'],
),
    row=2,col=1
)

# グラフのレイアウトを更新
fig.update_layout(height=600, width=800, title_text=Ticker + ' ' + interval + "ローソク足チャートと取引データのScatter Plot")
fig.update_xaxes(title_text="時間", row=2, col=1)
fig.update_yaxes(title_text="価格", row=1, col=1)
fig.update_yaxes(title_text="出来高", row=2, col=1)
fig.update_layout(xaxis_rangeslider_visible=False)

# レイアウトの設定
layout = go.Layout(
    hovermode='closest',  # カーソルが最も近いデータポイントにホバーするように設定
)
# グラフを表示
st.plotly_chart(fig)