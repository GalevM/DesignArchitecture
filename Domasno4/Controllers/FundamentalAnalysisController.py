from flask import render_template, Flask, request

from Domasno4.Repository.Functions import sentForIssuer

app = Flask("")
@app.route('/page4', methods=['GET', 'POST'])
def fundamental_analysis():
    selected_issuer = None
    sentiment = None

    issuers1 = sentForIssuer.keys()

    if request.method == 'POST':
        selected_issuer = request.form.get('issuer')
        sentiment = sentForIssuer[selected_issuer]

        return render_template(
            'page4.html',
            issuers=issuers1,
            sentiment=sentiment,
            selected_issuer=selected_issuer,
        )

    return render_template(
        'page4.html',
        issuers=issuers1,
        sentiment=sentiment,
        selected_issuer=selected_issuer,
    )