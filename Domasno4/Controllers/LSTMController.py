import os

from flask import render_template, Flask

app = Flask("")

@app.route('/page5', methods=['GET'])
def LSTM():
    predictions = None
    real_values = None
    rmse = None
    graph_url = None

    results_file = 'data/predictions.csv'
    graph_path = 'static/lstm_predictions.png'

    if os.path.exists(results_file) and os.path.exists(graph_path):
        with open(results_file, 'r') as file:
            results = file.readlines()
            rmse = results[0].strip()
            predictions = results[1:]

        graph_url = graph_path
    else:
        return render_template('page5.html', error_message="No saved results found. Please ensure the model is trained and results are saved.")

    return render_template(
        'page5.html',
        rmse=rmse,
        predictions=predictions,
        graph_url=graph_url
    )