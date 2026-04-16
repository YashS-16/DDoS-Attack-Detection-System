from flask import Flask, render_template, jsonify
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOG_FILE = os.path.join(BASE_DIR, 'logs.json')
print("Reading logs from:", LOG_FILE)

print("STATIC PATH:", os.path.join(BASE_DIR, '../Frontend/static'))
print("EXISTS:", os.path.exists(os.path.join(BASE_DIR, '../Frontend/static')))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, '../Frontend/template'),
    static_folder=os.path.join(BASE_DIR, '../Frontend/static')
)

# ------------------- PAGES -------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/precautions')
def precautions():
    return render_template('precautions.html')


# ------------------- APIs -------------------
@app.route('/api/data')
def get_data():
    if not os.path.exists(LOG_FILE):
        return jsonify({"logs": []})

    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    except:
        logs = []

    return jsonify({
        "logs": logs[-20:]  # last 20 entries
    })


if __name__ == '__main__':
    app.run(debug=True)