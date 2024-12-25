import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from datetime import datetime


# Подготовка на податоците
def prepare_data(file_path):
    # Читање на податоците од CSV
    def parsePrice(price_str):
        price_str = price_str.replace('.', '')
        price_str = price_str.replace(',', '.')
        return float(price_str)

    df = pd.read_csv(file_path, parse_dates=["Datum"], dayfirst=True)

    df = df[df['Kolicina'] != 0]
    df['%prom'] = df['%prom'].ffill()
    df['Prosecna cena'] = df['Prosecna cena'].apply(parsePrice)
    df['Mak.'] = df['Mak.'].apply(parsePrice)
    df['Min.'] = df['Min.'].apply(parsePrice)
    df["Cena na posledna transakcija"] = df["Cena na posledna transakcija"].apply(parsePrice)

    df = df[["Datum", "Cena na posledna transakcija"]]  # Одбирање само на потребните колони
    df.columns = ["Date", "Close"]  # Променување на имињата на колоните
    df.dropna(inplace=True)  # Премахнување на редови со недостасувачки вредности
    df.set_index("Date", inplace=True)  # Поставување на датумот како индекс

    # Скалатор за нормализација на цените
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df["Close"].values.reshape(-1, 1))

    # Параметри за обработка на податоците
    sequence_length = 60  # Вземаме податоци од претходните 60 дена
    x_data, y_data = [], []

    # Подготовка на податоците за LSTM
    for i in range(sequence_length, len(scaled_data)):
        x_data.append(scaled_data[i - sequence_length:i, 0])
        y_data.append(scaled_data[i, 0])

    x_data, y_data = np.array(x_data), np.array(y_data)
    x_data = np.reshape(x_data, (x_data.shape[0], x_data.shape[1], 1))  # Потребно е за LSTM

    # Делиме на тренинг и тест сетови (70% за тренинг, 30% за тестирање)
    train_size = int(len(x_data) * 0.8)
    x_train, x_test = x_data[:train_size], x_data[train_size:]
    y_train, y_test = y_data[:train_size], y_data[train_size:]

    return x_train, x_test, y_train, y_test, scaler


# Тренинг на LSTM моделот
def train_lstm(x_train, y_train, x_test, y_test):
    model = Sequential([
        LSTM(50, return_sequences=False, input_shape=(x_train.shape[1], 1)),
        Dropout(0.2),
        Dense(1)
    ])

    model.compile(optimizer='adam', loss='mean_squared_error')

    # Тренинг на моделот
    model.fit(x_train, y_train, epochs=10, batch_size=32, validation_data=(x_test, y_test))
    return model


# Предвидување и процена на точноста на моделот
def predict_and_evaluate(model, x_test, y_test, scaler):
    predictions = model.predict(x_test)
    predictions = scaler.inverse_transform(predictions.reshape(-1, 1))  # Претворање на скалираните вредности

    y_test_scaled = scaler.inverse_transform(y_test.reshape(-1, 1))  # Претворање на тест податоците
    mse = mean_squared_error(y_test_scaled, predictions)  # Проценка на грешката

    rmse = np.sqrt(mse)  # Извлекување на корен од средна квадратна грешка (RMSE)

    return predictions, y_test_scaled, rmse


# Главна функција
# Главна функција
def main():
    file_path = "../Domasno1/dokss.csv"  # Патека до податоците (замени ако е потребно)

    # Подготовка на податоците
    x_train, x_test, y_train, y_test, scaler = prepare_data(file_path)

    # Тренинг на моделот
    model = train_lstm(x_train, y_train, x_test, y_test)

    # Предвидување и процена
    predictions, y_test_scaled, rmse = predict_and_evaluate(model, x_test, y_test, scaler)

    # Печатење на резултатите
    print("Првите 5 предвидувања:", predictions[:5])
    print("Реалните вредности:", y_test_scaled[:5])
    print(f"RMSE на моделот: {rmse}")

    # Зачувување на резултатите во CSV
    results_df = pd.DataFrame({
        "Real": y_test_scaled.flatten(),
        "Predicted": predictions.flatten()
    })
    results_df.to_csv("predictions.csv", index=False)
    print("Резултатите се зачувани во 'predictions.csv'.")

    # Визуелизација на резултатите
    plt.figure(figsize=(10, 6))
    plt.plot(y_test_scaled, label="Реални вредности")
    plt.plot(predictions, label="Предвидени вредности")
    plt.title("Предвидување на цените на акциите")
    plt.xlabel("Време")
    plt.ylabel("Цена")
    plt.legend()
    plt.show()
    graph_path = "static/lstm_predictions.png"
    plt.savefig(graph_path)
    plt.close()

if __name__ == "__main__":
    main()

