# Mapa ułamków w Unicode na wartości dziesiętne
fraction_map = {
    "½": 0.5,
    "⅓": 1/3,
    "⅔": 2/3,
    "¼": 0.25,
    "¾": 0.75,
    "⅕": 0.2,
    "⅖": 0.4,
    "⅗": 0.6,
    "⅘": 0.8,
    "⅙": 1/6,
    "⅚": 5/6,
    "⅛": 0.125,
    "⅜": 0.375,
    "⅝": 0.625,
    "⅞": 0.875,
    "1 ½": 1.5,
    "1 ⅓": 1 + 1/3, 
    "1 ¼": 1 + 0.25,  
    "1 ¾": 1 + 0.75,  
    "2 ½": 2 + 0.5,  
    "2 ⅓": 2 + 1/3,  
}



def convert_fraction_to_decimal(quantity_str):
    """Zamienia ułamki na wartości dziesiętne."""
    # Sprawdzamy, czy ilość jest ułamkiem zapisanym jako "numerator/denominator"
    if '/' in quantity_str:
        try:
            numerator, denominator = quantity_str.split('/')
            return str(float(numerator) / float(denominator))
        except ValueError:
            print(f"Nie udało się przetworzyć ułamka: {quantity_str}")
            return quantity_str  # Zwracamy oryginalny ciąg, jeśli konwersja się nie powiedzie
    
    # Sprawdzamy, czy ilość zawiera Unicode fraction (np. ½, ⅓)
    for fraction, decimal in fraction_map.items():
        if fraction in quantity_str:
            return str(decimal)
    
    # Jeżeli ilość nie jest ułamkiem, po prostu zwróć ją w oryginalnej formie
    return quantity_str

def parse_quantity_and_unit(quantity_str):
    """Rozdziela ilość i jednostkę w składniku."""
    quantity_str = convert_fraction_to_decimal(quantity_str)
    
    # Dopasowanie ilości i jednostki (zwykła ilość lub z ułamkiem)
    match = re.match(r"([0-9,/.½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞\-\s]+)\s*([a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]*)", quantity_str.strip())
    if match:
        quantity = match.group(1).strip() if match.group(1) else ""
        unit = match.group(2).strip() if match.group(2) else ""
        
        # Obsługuje przypadek "1 ½", "1 ¼" itp.
        if " " in quantity:
            parts = quantity.split()
            quantity = sum(float(part) if "/" not in part else float(convert_fraction_to_decimal(part)) for part in parts)
        
        return str(quantity), unit
    
    return "", ""


# aniagotuje

                    # Tutaj sprawdz czy pierwsze slowo z wartosci unit 
                    # znajduje sie w któryms z kluczy pliku../jednostki.json
                    # {
                    #     "units": {
                    #         "g": "g",
                    #         "dkg": "dkg",
                    #         "kg": "kg",
                    #         "sztuk": "sztuka",
                    #         "ml": "ml",
                    #         "l": "l"
                    #     }
                    # }
                    # jelsi tak to przetlumacz unit na wartosc klucza
                    # chodzi glownie o sztuk
                    # sztuk znajduje sie w sztuki, sztuka, ... a tlumaczymy na sztuka w lb poj