from flask import render_template, Flask, request

from Domasno4.Repository.Functions import issuers, generateGraph, df

app = Flask("")
@app.route('/page2', methods=['GET', 'POST'])
def show_graphs_history():
    if request.method == 'POST':
        issuer = request.form.get('issuer')

        if issuer not in issuers:
            return render_template('page2.html', issuers=issuers, error="Invalid issuer selected.")

        graph = generateGraph(issuer, df)

        return render_template('page2.html', issuers=issuers, graph=graph, selected_issuer=issuer)

    else:
        return render_template('page2.html', issuers=issuers)
