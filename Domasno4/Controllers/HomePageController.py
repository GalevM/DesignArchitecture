from flask import render_template, Flask

app = Flask("")


@app.route('/')
def index():
    """Render the homepage."""
    return render_template('page1.html')


