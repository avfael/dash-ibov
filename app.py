import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(layout="wide")

st.title('Dashboard Financeiro - Código Quant')
periodo_box = st.sidebar.selectbox(
    "Variação",
    ("Diária", "Semanal", "Mensal")
)

st.header("Variação "+periodo_box)

@st.cache
def get_prices(tickers):
    prices = pd.DataFrame(columns=tickers)
    df = yf.download(tickers,  period="3mo")['Adj Close']
    prices.loc['dia_anterior']    = df.iloc[-2].copy()
    prices.loc['semana_anterior'] = df.resample("W").last().iloc[-2].copy()
    prices.loc['mes_anterior']    = df.resample("M").last().iloc[-2].copy()
    return prices

def get_lastest_price(tickers):
    return yf.download(tickers, period="1d")['Adj Close'].iloc[-1]
    
def get_retornos(periodo, prices):
    atual = get_lastest_price(tickers)    
    if periodo == 'Diária':
        return (atual / prices.loc['dia_anterior']) - 1
    elif periodo == "Semanal":
        return (atual / prices.loc['semana_anterior']) - 1
    elif periodo == "Mensal":
        return (atual / prices.loc['mes_anterior']) - 1
    else:
        st.write("Período inválido")

ibov_setor = pd.read_csv("data/ibov_setores.csv", index_col=0)
ibov_setor.set_index('Código', inplace=True)
ibov_setor.sort_index(inplace=True)
ibov_setor['ret'] = 0.0
ibov_setor['indice'] = "Índice Bovespa"
tickers = (ibov_setor.index + ".SA").to_list()

try:
    prices = get_prices(tickers)
except:
    st.error('ERRO: Não foi possível carregar a base de preços')

try:
    ret = get_retornos(periodo_box, prices)
except:
    st.error('ERRO: Não foi possível calcular os retornos.')

for t in tickers:
    ibov_setor.at[t.rstrip(".SA"), "ret"] = ret[t]

fig = px.treemap(ibov_setor.reset_index(), 
                 path=["indice",'Setor', 'SubSetor', 'Código'], 
                 values='Part. (%)', 
                 height=800,
                 width=1600,               
                 color="ret", 
                 color_continuous_scale='rdylgn',
                 range_color = [-.01, 0.01],
                 color_continuous_midpoint=0.0                
                 )

fig.update_traces(#textfont_color='white',
                  textfont_size=18,
                  textposition="middle center",
                  text=ibov_setor['ret'].apply(lambda r: f"{r:.2%}"),
                  hovertemplate='<b>%{label}:</b> Part. (IBOV): %{value:.2f}%',                                   
                  )
fig.update_layout(coloraxis_showscale=False)

st.plotly_chart(fig)