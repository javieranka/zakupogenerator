import os
import json
import csv
import subprocess
import re
from collections import defaultdict

import backend.config_file as cfg
from backend.aniagotuje_scrapper.aniagotuje_scrapper import aniagotuje_scrapper_main


# Wczytanie pliku jednostki.json
with open(cfg.units_filepath, 'r', encoding='utf-8') as units_file:
    unit_mappings = json.load(units_file)["units"]

# Wczytanie pliku jednostki_przelicznie.json
with open(cfg.units_calc_filepath, 'r', encoding='utf-8') as units_calc_file:
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
    Zwraca pierwsze dopasowanie (ilość i jednostkę) lub domyślnie (quantity_text, "").
    """

    # Usuwamy przymiotniki, takie jak "płaska" czy "czubata", pozostawiając jednostki
    quantity_text = re.sub(r'\b(po)\b', '', quantity_text).strip()
    quantity_text = re.sub(r'\b(płaska|płaskie|płaskiej|czubata|czubate|czubatej)\b', '', quantity_text).strip()

    # Definiujemy wzorce w kolejności priorytetu
    quantity_patterns = [
        # Najpierw wzorce dla jednostek wagowych i objętościowych (kg przed g, bez zbędnych spacji)
        r'(?P<quantity>\d+/\d+|\d+)\s*(?P<unit>\bkg\b|\bg\b|\bl\b|\bml\b|\błyżeczka\b|\błyżka\b|\błyżeczki\b|\błyżki\b)',  # np. 1 kg, 1/2 łyżeczki
        # Następnie sztuki
        r'(?P<quantity>\d+)\s*(?P<unit>\bsztuk(?:a|i)?\b)',  # np. 3 sztuki
        # Inne frazy typu "po 1 łyżeczce"
        r'po\s+(?P<quantity>\d+)\s*(?P<unit>\błyżeczki\b|\błyżki\b)',  # np. po 1 łyżeczce
    ]

    # Przechowujemy wszystkie dopasowania w formie (pozycja, ilość, jednostka)
    matches = []
    for pattern in quantity_patterns:
        for match in re.finditer(pattern, quantity_text):
            matches.append((match.start(), match.group('quantity'), match.group('unit')))

    # Jeśli znaleziono dopasowania, wybierz pierwsze w tekście (najmniejsza pozycja startowa)
    if matches:
        first_match = min(matches, key=lambda x: x[0])
        # print(f"First match: {first_match}")
        return first_match[1], first_match[2]

    # Domyślny zwrot: ilość = cały tekst, jednostka = ""
    return quantity_text, ""


def map_unit(unit):
    """
    Dopasowuje jednostkę do wartości z `unit_mappings`, uwzględniając regex.
    """
    for pattern, normalized_unit in unit_mappings.items():
        if re.search(pattern, unit):
            return normalized_unit
    return unit  # Jeśli nie znaleziono, zwróć oryginalną jednostkę


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
        
        # Usuwamy słowo "małe" z nazwy produktu
        clean_product = re.sub(r"\b(małe|mała|mały|mało|duża|duże|dużo|duży)\b", "", product).strip()

        ingredient_data = {
            "product": clean_product,
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
    with open(cfg.shopping_list_json, "w", encoding="utf-8") as json_file:
        json.dump(sorted_shopping_list, json_file, ensure_ascii=False, indent=4)

    print(f"Zapisano listę zakupów w pliku: {cfg.shopping_list_json}")

    # Zwrócenie danych JSON wcześniej załadowanych do pliku
    return sorted_shopping_list


# Funkcja wywołująca podskrypt aniagotuje_scrapper.py
def run_scraper(data):
    """Uruchamia podskrypt scrapera."""
    try:
        # Wywołanie skryptu aniagotuje_scrapper.py
        # result = subprocess.run(["python", cfg.aniagotuje_scrapper_script_filepath, data], 
        #                         check=True, capture_output=True, text=True)
        aniagotuje_scrapper_main(data)
        print("Podskrypt scrapera zakończył się sukcesem.")
    except subprocess.CalledProcessError as e:
        print(f"Błąd przy uruchamianiu scrapera: {e}")
        exit()


# Funckja dla wywołania przez inny program
# Zwraca wynik w postaci JSON
def return_result_shopping_list_json(data):
        # Uruchamiamy podskrypt scrapera
    run_scraper(data)

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
    sorted_json_data = generate_shopping_list(merged_ingredients)

    return sorted_json_data


# Główna część skryptu
if __name__ == "__main__":
    final_data = return_result_shopping_list_json()
    print(final_data)
