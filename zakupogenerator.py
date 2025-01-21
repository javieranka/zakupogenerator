import os
import json
import csv
import subprocess
import re
from collections import defaultdict

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


def merge_ingredients(all_ingredients):
    """Łączy wszystkie składniki i sumuje ilości dla tych samych produktów."""
    merged_ingredients = defaultdict(lambda: {"quantity": 0, "unit": ""})
    
    for ingredient in all_ingredients:
        product = ingredient["product"]
        quantity, unit = parse_quantity_and_unit(ingredient["quantity"])
        
        # Sumowanie ilości (zwykłe i ułamkowe wartości)
        if quantity:
            try:
                merged_ingredients[product]["quantity"] += float(quantity)
            except ValueError:
                print(f"Nie udało się przetworzyć ilości: {quantity} dla produktu: {product}")
        else:
            merged_ingredients[product]["quantity"] += 1  # domyślnie traktujemy brak ilości jako "1"
        
        # Ustalamy jednostkę (przyjmujemy pierwszą jednostkę, która się pojawi)
        if merged_ingredients[product]["unit"] == "":
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
            quantity, unit = parse_quantity_and_unit(item["quantity"])
            writer.writerow([item["product"], quantity, unit])

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
