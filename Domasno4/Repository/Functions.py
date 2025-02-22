import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import io
import base64
from collections import Counter
from transformers import pipeline, AutoTokenizer

matplotlib.use('Agg')

dataFile = pd.read_csv("../Domasno1/dokss.csv")

issuers = [row for row in dataFile['Ime na Kompanija']]
issuers = set(issuers)
issuers = sorted(issuers)


def parsePrice(price_str):
    price_str = price_str.replace('.', '')
    price_str = price_str.replace(',', '.')
    return float(price_str)


df = dataFile[dataFile['Kolicina'] != 0]
df['%prom'] = df['%prom'].ffill()
df['Prosecna cena'] = df['Prosecna cena'].apply(parsePrice)


def generateGraph(issuer, df):
    issuer_data = df[df['Ime na Kompanija'] == issuer].copy()

    if issuer_data.empty:
        return None

    issuer_data['Datum'] = pd.to_datetime(issuer_data['Datum'], errors='coerce')
    issuer_data.loc[:, 'Prosecna cena'] = pd.to_numeric(issuer_data['Prosecna cena'], errors='coerce')

    issuer_data.dropna(subset=['Datum', 'Prosecna cena'], inplace=True)

    issuer_data.set_index('Datum', inplace=True)
    issuer_data.sort_index(inplace=True)

    issuer_data['Prosecna cena'] = issuer_data['Prosecna cena'].interpolate()

    plt.figure(figsize=(10, 6))
    plt.plot(
        issuer_data.index, issuer_data['Prosecna cena'],
        label=f'{issuer} Prosecna cena', color='blue', linestyle='-', linewidth=2
    )
    plt.title(f'{issuer} Просечна Цена Низ Времето')
    plt.xlabel('Datum')
    plt.ylabel('Prosecna cena')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return img_base64


def sentimentAnalysis():
    df1 = pd.read_csv("../../DizajnArhitektura/Domasno4/data/scraped_data_sentiment.csv")

    df_copy = df1.dropna(subset=['Content'])

    result = df_copy.groupby('Issuer')['Content'].apply(lambda x: '. '.join(x)).reset_index()
    result['Content'] = result['Content'] + '.'

    issuers1 = result["Issuer"].tolist()
    issuers1 = [issuer1[:-1] for issuer1 in issuers1]

    sentimentModel = pipeline("sentiment-analysis")
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

    sentForIssuer = {}

    def split_into_chunks(text, max_length=512):
        tokens = tokenizer.encode(text, truncation=True, padding=False, max_length=max_length)

        chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]

        return [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]

    for issuer in issuers1:
        content_for_issuer = result[result['Issuer'] == issuer + "/"]['Content'].fillna('').astype(str).tolist()

        full_content = ' '.join(content_for_issuer)

        chunks = split_into_chunks(full_content)

        sentiment_scores = []
        for chunk in chunks:
            sentiment = sentimentModel(chunk)
            sentiment_scores.append(sentiment[0]['label'])

        sentForIssuer[issuer] = sentiment_scores

    return sentForIssuer


sentForIssuer = sentimentAnalysis()


def calculate_stochastic(close, windoww):
    highest_high = close.rolling(window=windoww).max()
    lowest_low = close.rolling(window=windoww).min()

    stoch = 100 * (close - lowest_low) / (highest_high - lowest_low)
    return stoch


def calculate_cci(close, windoww):
    typical_price = (close + close + close) / 3
    moving_average = typical_price.rolling(window=windoww).mean()
    mean_deviation = typical_price.rolling(window=windoww).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)

    cci = (typical_price - moving_average) / (0.015 * mean_deviation)
    return cci


def calculate_tma(close, windoww):
    sma = close.rolling(window=windoww).mean()
    return sma.rolling(window=windoww).mean()


def calculate_williams_r(close, windoww):
    highest_high = close.rolling(window=windoww).max()
    lowest_low = close.rolling(window=windoww).min()

    williams_r = -100 * (highest_high - close) / (highest_high - lowest_low)
    return williams_r


def calculate_ama(close):
    fast = close.ewm(span=2, adjust=False).mean()
    slow = close.ewm(span=30, adjust=False).mean()
    ama = fast - (fast - slow) * (0.2)
    return ama


def majority_decision(signals):
    signal_counts = Counter(signals.values())

    most_common_signal, count = signal_counts.most_common(1)[0]

    return most_common_signal


def calculate_rsi(close, period):
    delta = close.diff(1)
    gain = np.where(delta > 0, delta, 0)
    loss = -np.where(delta < 0, delta, 0)

    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return pd.Series(rsi, index=close.index)


def calculate_macd(close, short_period=12, long_period=26, signal_period=9):
    short_ema = close.ewm(span=short_period, adjust=False).mean()
    long_ema = close.ewm(span=long_period, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    return macd_line, signal_line
