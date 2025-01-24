import streamlit as st
import pandas as pd
import ccxt
import matplotlib.pyplot as plt
from finta import TA

# Função para obter a lista de todas as moedas de futuros
def listar_moedas_futures(exchange):
    markets = exchange.load_markets()
    moedas_futures = [market for market in markets if exchange.markets[market]['type'] == 'swap']
    return moedas_futures

# Coleta de dados da API da Bitget usando ccxt
def coleta_dados(exchange, symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=168)  # 7 dias (24*7=168 horas)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# Análise técnica com Fibonacci e Expansão
def analise_tecnica(df):
    high = df['high'].max()
    low = df['low'].min()
    diff = high - low
    
    # Níveis de Fibonacci
    fib_levels = {
        'Fib 23.6%': high - 0.236 * diff,
        'Fib 38.2%': high - 0.382 * diff,
        'Fib 50.0%': high - 0.5 * diff,
        'Fib 61.8%': high - 0.618 * diff,
        'Fib 78.6%': high - 0.786 * diff,
    }
    
    for level_name, level_value in fib_levels.items():
        df[level_name] = level_value
    
    # Expansão de Fibonacci
    expansions = {
        'Exp 100%': high + diff,
        'Exp 161.8%': high + 1.618 * diff,
    }
    
    for exp_name, exp_value in expansions.items():
        df[exp_name] = exp_value

    # Implementação de indicadores adicionais
    df['SMA'] = df['close'].rolling(window=14).mean()  # Média Móvel Simples (SMA)
    df['EMA'] = df['close'].ewm(span=14).mean()  # Média Móvel Exponencial (EMA)
    
    return df

# Exibição dos dados e gráficos
def exibir_grafico(df, symbol):
    high = df['high'].max()
    low = df['low'].min()
    diff = high - low

    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Plotando Preço
    ax.plot(df.index, df['close'], label='Preço', color='black', linewidth=1.5)
    
    # Plotando Indicadores
    ax.plot(df.index, df['SMA'], label='SMA', color='blue', linestyle='dotted')
    ax.plot(df.index, df['EMA'], label='EMA', color='orange', linestyle='dotted')
    
    # Plotando Níveis de Fibonacci
    for level_name in ['Fib 23.6%', 'Fib 38.2%', 'Fib 50.0%', 'Fib 61.8%', 'Fib 78.6%']:
        ax.axhline(y=df[level_name].iloc[0], linestyle='--', label=level_name, color='purple')
    
    # Plotando Expansões de Fibonacci
    for exp_name in ['Exp 100%', 'Exp 161.8%']:
        ax.axhline(y=df[exp_name].iloc[0], linestyle='-.', label=exp_name, color='green')
    
    # Anotações para Expansões de Fibonacci
    ax.annotate('Target 1.618 (Up)', xy=(df.index[-1], df['Exp 161.8%'].iloc[0]), xytext=(df.index[-1], df['Exp 161.8%'].iloc[0] + diff * 0.1),
                arrowprops=dict(facecolor='green', shrink=0.05), fontsize=10, color='green')
    ax.annotate('Target 1.618 (Down)', xy=(df.index[-1], df['Exp 100%'].iloc[0] - 1.618 * diff), xytext=(df.index[-1], df['Exp 100%'].iloc[0] - 1.618 * diff - diff * 0.1),
                arrowprops=dict(facecolor='red', shrink=0.05), fontsize=10, color='red')
    
    ax.set_title(f'Análise Técnica de {symbol} (H1)', fontsize=16)
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Preço', fontsize=12)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True)
    
    st.pyplot(fig)

# Aplicação principal
def main():
    st.title("Análise de Trading com Fibonacci e Expansão")
    
    # Solicitação das credenciais de API
    api_key = st.text_input("Digite sua chave pública de API da Bitget:", type="password")
    api_secret = st.text_input("Digite sua chave privada de API da Bitget:", type="password")
    passphrase = st.text_input("Digite sua senha de API da Bitget:", type="password")
    
    if api_key and api_secret and passphrase:
        # Conectando com a API da Bitget usando ccxt
        exchange = ccxt.bitget({
            'apiKey': api_key,
            'secret': api_secret,
            'password': passphrase,
        })
        
        # Buscar todas as moedas de futuros
        moedas_futures = listar_moedas_futures(exchange)
        st.write("Moedas de futuros disponíveis:")
        st.write(moedas_futures)
        
        # Permitir ao usuário selecionar moedas para analisar
        moedas_selecionadas = st.multiselect("Selecione as moedas para análise:", moedas_futures)
        
        for symbol in moedas_selecionadas:
            st.write(f"Analisando {symbol}...")
            
            # Coleta de dados
            df = coleta_dados(exchange, symbol)
            
            # Análise técnica
            df_analise = analise_tecnica(df)
            
            # Exibição dos dados e gráficos
            exibir_grafico(df_analise, symbol)
    
if __name__ == "__main__":
    main()
