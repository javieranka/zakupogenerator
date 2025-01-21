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



# def merge_ingredients(all_ingredients):
#     """Łączy wszystkie składniki i sumuje ilości dla tych samych produktów."""
#     merged_ingredients = defaultdict(lambda: {"quantity": 0, "unit": ""})
    
#     for ingredient in all_ingredients:
#         product = ingredient["product"]
#         quantity = ingredient["quantity"]
#         unit = ingredient["unit"]
        
#         # Sumowanie ilości (zwykłe i ułamkowe wartości)
#         if quantity:
#             try:
#                 merged_ingredients[product]["quantity"] += float(quantity)
#             except ValueError:
#                 print(f"Nie udało się przetworzyć ilości: {quantity} dla produktu: {product}")
#         else:
#             merged_ingredients[product]["quantity"] += 1  # domyślnie traktujemy brak ilości jako "1"
        
#         # Ustalamy jednostkę (przyjmujemy pierwszą jednostkę, która się pojawi)
#         if merged_ingredients[product]["unit"] == "":
#             merged_ingredients[product]["unit"] = unit
    
#     # Zmieniamy strukturę na listę
#     merged_ingredients_list = []
#     for product, data in merged_ingredients.items():
#         merged_ingredients_list.append({
#             "product": product,
#             "quantity": str(data["quantity"]),
#             "unit": data["unit"]
#         })
    
#     return merged_ingredients_list

# def merge_ingredients(all_ingredients):
#     """Łączy wszystkie składniki, sumuje ilości dla tych samych produktów i dopasowuje jednostki."""
#     merged_ingredients = defaultdict(lambda: {"quantity": 0, "unit": ""})

#     for ingredient in all_ingredients:
#         product = ingredient["product"]
#         quantity = ingredient["quantity"]
#         unit = ingredient["unit"]

#         # Dopasowanie jednostki do wartości z jednostki.json
#         for key in unit_mappings:
#             if key in unit:  # Sprawdź, czy klucz (np. "g", "łyżk") występuje w jednostce
#                 unit = unit_mappings[key]
#                 break

#         # Sumowanie ilości (zwykłe i ułamkowe wartości)
#         if quantity:
#             try:
#                 merged_ingredients[product]["quantity"] += float(quantity)
#             except ValueError:
#                 print(f"Nie udało się przetworzyć ilości: {quantity} dla produktu: {product}")
#         else:
#             merged_ingredients[product]["quantity"] += 1  # Domyślnie traktujemy brak ilości jako "1"

#         # Ustalamy jednostkę (przyjmujemy pierwszą jednostkę, która się pojawi)
#         if merged_ingredients[product]["unit"] == "":
#             merged_ingredients[product]["unit"] = unit

#     # Zmieniamy strukturę na listę
#     merged_ingredients_list = []
#     for product, data in merged_ingredients.items():
#         merged_ingredients_list.append({
#             "product": product,
#             "quantity": str(data["quantity"]),
#             "unit": data["unit"]
#         })

#     return merged_ingredients_list

# def merge_ingredients(all_ingredients):
    """Łączy wszystkie składniki, sumuje ilości dla tych samych produktów i dopasowuje jednostki."""
    merged_ingredients = defaultdict(lambda: {"quantity": 0, "unit": ""})

    for ingredient in all_ingredients:
        product = ingredient["product"]
        quantity = ingredient["quantity"]
        unit = ingredient["unit"]

        # Dopasowanie jednostki do wartości z jednostki.json
        for key in unit_mappings:
            if key in unit:  # Sprawdź, czy klucz (np. "g", "łyżk") występuje w jednostce
                unit = unit_mappings[key]
                break

        # Konwersja ilości na liczbę
        try:
            quantity = float(quantity) if quantity else 1
        except ValueError:
            print(f"Nie udało się przetworzyć ilości: {quantity} dla produktu: {product}")
            quantity = 1

        # Jeśli jednostka produktu już istnieje w `merged_ingredients`, konwertuj do wspólnej jednostki
        if merged_ingredients[product]["unit"] and merged_ingredients[product]["unit"] != unit:
            existing_unit = merged_ingredients[product]["unit"]

            # Sprawdź, czy można dokonać konwersji między jednostkami
            if unit in unit_conversion_factors and existing_unit in unit_conversion_factors[unit]:
                conversion_factor = unit_conversion_factors[unit][existing_unit]
                quantity *= conversion_factor  # Konwertuj ilość na istniejącą jednostkę
                unit = existing_unit  # Ustaw jednostkę na istniejącą jednostkę w merged_ingredients
            elif existing_unit in unit_conversion_factors and unit in unit_conversion_factors[existing_unit]:
                conversion_factor = unit_conversion_factors[existing_unit][unit]
                merged_ingredients[product]["quantity"] *= conversion_factor  # Konwertuj już zsumowaną ilość
                merged_ingredients[product]["unit"] = unit  # Ustaw nową jednostkę
            else:
                print(f"Nie udało się dopasować jednostek: {existing_unit} i {unit} dla produktu: {product}")

        # Sumowanie ilości w tej samej jednostce
        merged_ingredients[product]["quantity"] += quantity

        # Ustalamy jednostkę (przyjmujemy pierwszą jednostkę, która się pojawi)
        if not merged_ingredients[product]["unit"]:
            merged_ingredients[product]["unit"] = unit

    # Zmieniamy strukturę na listę
    merged_ingredients_list = []
    for product, data in merged_ingredients.items():
        merged_ingredients_list.append({
            "product": product,
            "quantity": str(data["quantity"]),
            "unit": data["unit"]
        })

    return merged_ingredients_list
