import pandas as pd
from transformers import pipeline, AutoTokenizer

df = pd.read_csv("../../DesignArchitecture-master/Domashno3/scraped_data_sentiment.csv")

df_copy = df.dropna(subset=['Content'])

result = df_copy.groupby('Issuer')['Content'].apply(lambda x: '. '.join(x)).reset_index()
result['Content'] = result['Content'] + '.'

issuers = result["Issuer"].tolist()
issuers = [issuer[:-1] for issuer in issuers]

sentimentModel = pipeline("sentiment-analysis")
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

sentForIssuer = {}


def split_into_chunks(text, max_length=512):
    tokens = tokenizer.encode(text, truncation=True, padding=False, max_length=max_length)

    chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]

    return [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]


for issuer in issuers:
    content_for_issuer = df[df['Issuer'] == issuer + "/"]['Content'].fillna('').astype(str).tolist()

    full_content = ' '.join(content_for_issuer)

    chunks = split_into_chunks(full_content)

    sentiment_scores = []
    for chunk in chunks:
        sentiment = sentimentModel(chunk)
        sentiment_scores.append(sentiment[0]['label'])

    sentForIssuer[issuer] = sentiment_scores

    print(f"Sentiment for {issuer}: {sentiment_scores}")

print(sentForIssuer)
