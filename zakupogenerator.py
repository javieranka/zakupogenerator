import os
import json
import csv
import subprocess
import re
from collections import defaultdict


# Wczytanie pliku jednostki.json
with open('jednostki.json', 'r', encoding='utf-8') as units_file:
    unit_mappings = json.load(units_file)["units"]

# Wczytanie pliku jednostki_przelicznie.json
with open('jednostki_przeliczanie.json', 'r', encoding='utf-8') as units_calc_file:
    unit_conversion_factors = json.load(units_calc_file)["units"]


def load_ingredients_from_files(scraper_folders):
    """Ładuje składniki z plików JSON w folderach *_scrapper."""
    all_ingredients = []
    
    for folder in scraper_folders:
        json_file_path = os.path.join(folder, f"{folder}_składniki.json")
        
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
    Zwraca pierwsze dopasowanie (ilość i jednostkę) lub domyślnie (1, "").
    """
    quantity_patterns = [
        r'(?P<quantity>\d+)\s*(?P<unit>sztuk(?:a|i)?)',  # np. 4 sztuki
        r'(?P<quantity>\d+)\s*(?P<unit>g|kg|ml|l)',       # np. 250 g
    ]

    for pattern in quantity_patterns:
        match = re.search(pattern, quantity_text)
        if match:
            return match.group('quantity'), match.group('unit')

    return "1", ""  # Domyślnie ilość = 1, jednostka pusta


def merge_ingredients(all_ingredients):
    """
    Łączy wszystkie składniki, sumuje ilości dla tych samych produktów i dopasowuje jednostki.
    """
    merged_ingredients = defaultdict(lambda: {"quantity": 0, "unit": ""})

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

def generate_shopping_list(shopping_list):
    """Generuje listę zakupów w formacie JSON i CSV."""
    shopping_list_json = "lista_zakupów_oryginalne_jednostki.json"
    shopping_list_csv = "lista_zakupów.csv"

    # Zapis do pliku JSON
    with open(shopping_list_json, "w", encoding="utf-8") as json_file:
        json.dump(shopping_list, json_file, ensure_ascii=False, indent=4)

    # Zapis do pliku CSV
    with open(shopping_list_csv, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Produkt", "Ilość", "Jednostka"])
        for item in shopping_list:
            writer.writerow([item["product"], item['quantity'], item['unit']])

    print(f"Zapisano listę zakupów w plikach: {shopping_list_json} i {shopping_list_csv}")


# Funkcja wywołująca podskrypt aniagotuje_scrapper.py
def run_scraper():
    """Uruchamia podskrypt scrapera."""
    try:
        # Wywołanie skryptu aniagotuje_scrapper.py
        result = subprocess.run(["python", "./aniagotuje_scrapper/aniagotuje_scrapper.py"], 
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
    scraper_folders = [folder for folder in os.listdir() if folder.endswith('_scrapper')]

    # Załaduj składniki z plików *_składniki.json
    all_ingredients = load_ingredients_from_files(scraper_folders)
    
    # Wygeneruj złączoną listę składników
    merged_ingredients = merge_ingredients(all_ingredients)
    
    # Wygeneruj listę zakupów
    generate_shopping_list(merged_ingredients)
