# from time import sleep
from datetime import datetime
from flask import render_template, request, redirect, url_for
from front.app import app

# from backend.zakupogenerator import return_result_shopping_list_json


@app.route('/')
def index():
    return render_template('index.html', 
            now=datetime.now()
        )

@app.route('/results', methods=['POST'])
def results():
    input_text = request.form.get('input_field')  # Pobranie danych z formularza
    # sleep(1)
    return render_template('results.html', 
            # data=data,
            input_text = input_text,
            # data = return_result_shopping_list_json(),               
            data = test_lista_zakupow(),               
            now=datetime.now(),
            enumerate=enumerate,
        )



def test_lista_zakupow():
    data = [
        {
            "product": "cukier",
            "quantity": "200.0",
            "unit": "g"
        },
        {
            "product": "cukier drobny",
            "quantity": "290.0",
            "unit": "g"
        },
        {
            "product": "cukier wanilinowy",
            "quantity": "32.0",
            "unit": "g"
        },
        {
            "product": "cynamon",
            "quantity": "1.0",
            "unit": "łyżeczka"
        },
        {
            "product": "proszek do pieczenia i soda",
            "quantity": "1.0",
            "unit": "",
            "original_quantity": "po płaskiej łyżeczce"
        },
    ]
    return data