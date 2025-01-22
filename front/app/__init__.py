from flask import Flask

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your_secret_key'  # Wymagane dla Flask-WTF, jeśli użyjesz formularzy

from front.app import routes
