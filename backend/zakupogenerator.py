import os
import json
import csv
import subprocess
import re
from collections import defaultdict

units_filepath = './backend/jednostki/jednostki.json'
units_calc_filepath = './backend/jednostki/jednostki_przeliczanie.json'
shopping_list_json = './backend/lista_zakupów.json'

aniagotuje_scrapper_filepath = "./backend/aniagotuje_scrapper/"
aniagotuje_scrapper_script_filepath = "./backend/aniagotuje_scrapper/aniagotuje_scrapper.py"


# Wczytanie pliku jednostki.json
with open(units_filepath, 'r', encoding='utf-8') as units_file:
    unit_mappings = json.load(units_file)["units"]

# Wczytanie pliku jednostki_przelicznie.json
with open(units_calc_filepath, 'r', encoding='utf-8') as units_calc_file:
    unit_conversion_factors = json.load(units_calc_file)

def load_ingredients_from_files(scraper_folders):
    """Ładuje składniki z plików JSON w folderach *_scrapper."""
    all_ingredients = []
    
    for folder in scraper_folders:
        json_file_path = os.path.join('./backend/', folder, f"{folder}_składniki.json")
        
        # Sprawdzamy, czy plik istnieje
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as file:
                try:
                    recipe_data = json.load(file)
                    # Dodaj składniki z każdego przepisu
                    for recipe in recipe_data.values():
                        all_ingredients.extend(recipe.get("ingredients", []))
                except json.JSONDecodeError as e:
                    print(f"Błąd podczas odczytu pliku {json_file_path}: {e}")
        else:
            print(f"Plik {json_file_path} nie istnieje.")
    
    return all_ingredients

def extract_quantity_and_unit(quantity_text):
    """
    Rozdziela ilość i jednostkę na podstawie regexów.
    Normalizuje jednostki, np. "płaska łyżeczka" -> "łyżeczka".
    Zwraca pierwsze dopasowanie (ilość i jednostkę) lub domyślnie (quantity_text, "").
    """

    # Normalizacja jednostek z przymiotnikami
    quantity_text = re.sub(r'płaska\s+(łyżeczka|łyżka)', r'\1', quantity_text)
    quantity_text = re.sub(r'płaskie\s+(łyżeczki|łyżki)', r'\1', quantity_text)

    quantity_patterns = [
        r'(?P<quantity>\d+)\s*(?P<unit>sztuk(?:a|i)?)',  # np. 4 sztuki
        r'(?P<quantity>\d+/\d+|\d+)\s*(?P<unit>łyżeczka|łyżka|łyżeczki|g|kg|ml|l)',  # np. 1 łyżeczka, 1/3 łyżeczki
        r'po\s+(?P<quantity>\d+)\s*(?P<unit>łyżeczki|łyżki)',  # np. po 1 łyżeczce
    ]

    for pattern in quantity_patterns:
        match = re.search(pattern, quantity_text)
        if match:
            return match.group('quantity'), match.group('unit')

    return quantity_text, ""  # Domyślnie ilość = quantity_text, jednostka pusta

def merge_ingredients(all_ingredients):
    """
    Łączy wszystkie składniki, sumuje ilości dla tych samych produktów i dopasowuje jednostki.
    """
    merged_ingredients = defaultdict(lambda: {"quantity": 0, "unit": "", "original_quantity": None})

    for ingredient in all_ingredients:
        product = ingredient["product"]
        quantity_text = ingredient["quantity"]

        # Wyodrębnij ilość i jednostkę przy użyciu regexów
        quantity, unit = extract_quantity_and_unit(quantity_text)

        # Dopasowanie jednostki do wartości z `unit_mappings`
        for key in unit_mappings:
            if key in unit:  # Sprawdź, czy klucz (np. "g", "łyżk") występuje w jednostce
                unit = unit_mappings[key]
                break

        # Konwersja ilości na liczbę
        try:
            quantity = float(quantity) if quantity else 1.0
            original_quantity = None  # Ilość została poprawnie przetworzona, brak oryginalnego tekstu
        except ValueError:
            print(f"Nie udało się przetworzyć ilości: {quantity_text} dla produktu: {product}")
            original_quantity = quantity_text  # Zapisujemy oryginalny tekst
            quantity = 1.0  # Domyślna ilość
            unit = ""       # Domyślna jednostka

        # Sumowanie ilości w tej samej jednostce
        merged_ingredients[product]["quantity"] += quantity

        # Ustalamy jednostkę (przyjmujemy pierwszą jednostkę, która się pojawi)
        if not merged_ingredients[product]["unit"]:
            merged_ingredients[product]["unit"] = unit

        # Zapisujemy oryginalną ilość, jeśli istnieje
        if original_quantity:
            merged_ingredients[product]["original_quantity"] = original_quantity

    # Zmieniamy strukturę na listę
    merged_ingredients_list = []
    for product, data in merged_ingredients.items():
        ingredient_data = {
            "product": product,
            "quantity": str(data["quantity"]),
            "unit": data["unit"],
        }
        # Dodajemy oryginalną ilość do wyniku, jeśli istnieje
        if data["original_quantity"]:
            ingredient_data["original_quantity"] = data["original_quantity"]

        merged_ingredients_list.append(ingredient_data)

    return merged_ingredients_list


def generate_shopping_list(shopping_list):
    """Generuje listę zakupów w formacie JSON, posortowaną alfabetycznie według produktu."""

    # Sortowanie listy zakupów alfabetycznie według pola 'product'
    sorted_shopping_list = sorted(shopping_list, key=lambda item: item["product"])
    # print(sorted_shopping_list)

    # Zapis do pliku JSON
    with open(shopping_list_json, "w", encoding="utf-8") as json_file:
        json.dump(sorted_shopping_list, json_file, ensure_ascii=False, indent=4)

    print(f"Zapisano listę zakupów w pliku: {shopping_list_json}")


# Funkcja wywołująca podskrypt aniagotuje_scrapper.py
def run_scraper():
    """Uruchamia podskrypt scrapera."""
    try:
        # Wywołanie skryptu aniagotuje_scrapper.py
        result = subprocess.run(["python", aniagotuje_scrapper_script_filepath], 
                                check=True, capture_output=True, text=True)
        print("Podskrypt scrapera zakończył się sukcesem.")
    except subprocess.CalledProcessError as e:
        print(f"Błąd przy uruchamianiu scrapera: {e}")
        exit()


# Główna część skryptu
if __name__ == "__main__":
    # Uruchamiamy podskrypt scrapera
    run_scraper()

    # Zakładając, że foldery *_scrapper są w bieżącym katalogu
    # scraper_folders = [folder for folder in os.listdir() if folder.endswith('_scrapper')]
    scraper_folders = [
        folder for folder in os.listdir('./backend/') 
        if os.path.isdir(os.path.join('./backend/', folder)) and folder.endswith('_scrapper')
    ]

    # Załaduj składniki z plików *_składniki.json
    all_ingredients = load_ingredients_from_files(scraper_folders)
    
    # Wygeneruj złączoną listę składników
    merged_ingredients = merge_ingredients(all_ingredients)
    
    # Wygeneruj listę zakupów (posortowany JSON)
    generate_shopping_list(merged_ingredients)
