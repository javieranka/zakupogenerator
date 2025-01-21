from flask import render_template, request, redirect, url_for
from app import app

from datetime import datetime

@app.route('/')
def index():
    return render_template('index.html', 
            now=datetime.now()
        )

@app.route('/results', methods=['POST'])
def results():
    data = request.form.get('input_field')  # Pobranie danych z formularza
    return render_template('results.html', 
            data=data,               
            now=datetime.now()
        )
