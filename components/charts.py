import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from utils.indicators import identify_momentum_trend

def plot_momentum_candlestick(symbol, df_can, days=20):
    """Plot candlestick chart with momentum indicators"""
    df = df_can[df_can['Ticker'] == symbol].copy()
    
    if df.empty:
        return None
    
    df['Date'] = pd.to_datetime(df['Date'])
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    df = df[df['Date'] >= start_date]
    df = df.sort_values('Date').reset_index(drop=True)
    df.columns = df.columns.str.lower()
    df = identify_momentum_trend(df)
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.55, 0.22, 0.23]
    )
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Price',
        hoverinfo='text',
        hovertext=[
            f"<b><u>Price</u></b><br>" +
            f"Open: ${o:.2f}<br>" +
            f"High: ${h:.2f}<br>" +
            f"Low: ${l:.2f}<br>" +
            f"Close: ${c:.2f}<br>"
            for d, o, h, l, c in zip(df['date'], df['open'], df['high'], df['low'], df['close'])
        ]
    ), row=1, col=1)
    
    # SMAs
    fig.add_trace(go.Scatter(x=df['date'], y=df['sma_20'], name='SMA 20', line=dict(color='orange', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['date'], y=df['sma_50'], name='SMA 50', line=dict(color='blue', width=1.5)), row=1, col=1)
    
    # Bullish/bearish markers
    bullish_points = df[df['bullish_momentum']]
    bearish_points = df[df['bearish_momentum']]
    
    if not bullish_points.empty:
        fig.add_trace(go.Scatter(x=bullish_points['date'], y=bullish_points['high'] * 1.02,
        mode='markers', marker=dict(symbol='triangle-up', size=8, color='green'),
        name='Bullish Momentum'), row=1, col=1)
    
    if not bearish_points.empty:
        fig.add_trace(go.Scatter(x=bearish_points['date'], y=bearish_points['low'] * 0.98,
        mode='markers', marker=dict(symbol='triangle-down', size=8, color='red'),
        name='Bearish Momentum'), row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=df['date'], y=df['rsi'], name='RSI', line=dict(color='purple', width=2)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=2, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", opacity=0.3, row=2, col=1)
    
    # Momentum
    fig.add_trace(go.Scatter(x=df['date'], y=df['momentum'], name='Momentum', line=dict(color='teal', width=2), fill='tozeroy'), row=3, col=1)
    fig.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.5, row=3, col=1)

    # Layout
    trend_text = "Bullish 📈" if df['bullish_momentum'].iloc[-1] else "Bearish 📉" if df['bearish_momentum'].iloc[-1] else "Neutral ➡️"
    fig.update_layout(
        height=800,
        title=f'<b>{symbol.upper()} Momentum Analysis</b><br><sub>RSI: {df["rsi"].iloc[-1]:.2f} | Momentum: ${df["momentum"].iloc[-1]:.2f} | Trend: {trend_text}</sub>',
        hovermode='x unified',
        showlegend=True,
        xaxis3_title='Date',
        margin=dict(t=100, b=80),
        xaxis_rangeslider_visible=False)

    fig.update_yaxes(title_text="<b>Price (USD)</b><br>w/ SMA 20 & 50", row=1, col=1)
    fig.update_yaxes(title_text="<b>RSI (14)</b><br><sub>>70 overbought, <30 oversold</sub>", row=2, col=1, range=[0, 100])
    fig.update_yaxes(title_text="<b>Momentum (10-day)</b><br><sub>Price change over 10 days</sub>", row=3, col=1)

    return fig