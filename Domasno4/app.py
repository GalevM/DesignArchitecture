from flask import Flask
from Controllers.HomePageController import index
from Controllers.FundamentalAnalysisController import fundamental_analysis
from Controllers.HistoryController import show_graphs_history
from Controllers.LSTMController import LSTM
from Controllers.TechnicalAnalysisController import technical_analysis

import sys
sys.path.append('/app')

app = Flask(__name__)

app.add_url_rule('/', 'index', index, methods=['GET'])
app.add_url_rule('/page2', 'page2', show_graphs_history, methods=['GET', 'POST'])
app.add_url_rule('/page3', 'page3', technical_analysis, methods=['GET', 'POST'])
app.add_url_rule('/page4', 'page4', fundamental_analysis, methods=['GET', 'POST'])
app.add_url_rule('/page5', 'page5', LSTM, methods=['GET'])

if __name__ == '__main__':
    app.run(debug=True)
