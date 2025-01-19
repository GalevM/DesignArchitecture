import numpy as np
import pandas as pd
from flask import request, render_template, Flask

from Domasno4.Repository.Functions import df, calculate_tma, calculate_ama, calculate_rsi, calculate_macd, \
    calculate_stochastic, calculate_cci, calculate_williams_r, majority_decision, issuers

app = Flask("")

@app.route('/page3', methods=['GET', 'POST'])
def technical_analysis():
    selected_issuer = None
    timeframe = None
    signals = None

    if request.method == 'POST':
        selected_issuer = request.form.get('issuer')
        timeframe = request.form.get('timeframe')

        if selected_issuer and timeframe:
            issuer_data = df[df['Ime na Kompanija'] == selected_issuer]
            issuer_data['Datum'] = pd.to_datetime(issuer_data['Datum'], errors='coerce')
            windoww = 0

            if timeframe == "1 day":
                issuer_data = issuer_data.tail(1)  # Last day's data
                windoww = 1
            elif timeframe == "1 week":
                issuer_data = issuer_data.tail(5)  # Last week's data (5 days)
                windoww = 5
            elif timeframe == "1 month":
                issuer_data = issuer_data.tail(20)  # Last month's data (20 days)
                windoww = 20

            if not issuer_data.empty:
                close = issuer_data['Prosecna cena']

                # Moving Averages
                sma = close.rolling(window=windoww).mean()
                ema = close.ewm(span=windoww, adjust=False).mean()
                wma = close.rolling(window=windoww).apply(
                    lambda x: np.dot(x, np.arange(1, windoww + 1)) / np.sum(np.arange(1, windoww + 1)), raw=True)
                tma = calculate_tma(close, windoww)
                ama = calculate_ama(close)

                # Oscillators
                rsi = calculate_rsi(close, windoww)
                macd, macd_signal = calculate_macd(close)
                stoch = calculate_stochastic(close, windoww)
                cci = calculate_cci(close, windoww)
                williams_r = calculate_williams_r(close, windoww)

                signals = {
                    "SMA": "Buy" if sma.iloc[-1] < close.iloc[-1] else "Sell",
                    "EMA": "Buy" if ema.iloc[-1] < close.iloc[-1] else "Sell",
                    "RSI": "Buy" if rsi.iloc[-1] < 30 else "Sell" if rsi.iloc[-1] > 70 else "Hold",
                    "MACD": "Buy" if macd.iloc[-1] > macd_signal.iloc[-1] else "Sell",
                    "WMA": "Buy" if wma.iloc[-1] < close.iloc[-1] else "Sell",
                    "TMA": "Buy" if tma.iloc[-1] < close.iloc[-1] else "Sell",
                    "AMA": "Buy" if ama.iloc[-1] < close.iloc[-1] else "Sell",
                    "Stochastic": "Buy" if stoch.iloc[-1] < 20 else "Sell" if stoch.iloc[-1] > 80 else "Hold",
                    "CCI": "Buy" if cci.iloc[-1] < -100 else "Sell" if cci.iloc[-1] > 100 else "Hold",
                    "Williams %R": "Buy" if williams_r.iloc[-1] < -80 else "Sell" if williams_r.iloc[
                                                                                         -1] > -20 else "Hold",
                }

                majority_signal = majority_decision(signals)
                signals['Majority Vote'] = majority_signal

                return render_template(
                    'page3.html',
                    issuers=issuers,
                    signals=signals,
                    selected_issuer=selected_issuer,
                    timeframe=timeframe,

                )

    return render_template(
        'page3.html',
        issuers=issuers,
        signals=signals,
        selected_issuer=selected_issuer,
        timeframe=timeframe,

    )