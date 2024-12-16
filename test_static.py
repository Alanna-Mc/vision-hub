from flask import Flask, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return f"""
    <!doctype html>
    <html>
    <head>
        <link rel="stylesheet" href="{url_for('static', filename='css/styles.css')}">
    </head>
    <body>
        <h1>Test Page</h1>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(debug=True)

