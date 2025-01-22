from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json


aniagotuje_links_filepath = "./backend/aniagotuje_scrapper/linki_do_przepisów.txt"
aniagotuje_results_filepath = "./backend/aniagotuje_scrapper/aniagotuje_scrapper_składniki.json"


def convert_fraction_to_decimal(quantity_str):
    """Zamienia ułamki na wartości dziesiętne."""
    if '/' in quantity_str:
        try:
            numerator, denominator = quantity_str.split('/')
            return str(float(numerator) / float(denominator))
        except ValueError:
            print(f"Nie udało się przetworzyć ułamka: {quantity_str}")
            return quantity_str  # Zwracamy oryginalny ciąg, jeśli konwersja się nie powiedzie
    return quantity_str


def split_quantity_and_unit(quantity_text):
    """Rozdziela ilość i jednostkę składnika, zakładając, że ilość jest przed jednostką."""
    
    # Najpierw znajdź część, która jest ułamkiem
    parts = quantity_text.split()
    
    if len(parts) > 1:
        # Rozdziel ułamek i jednostkę, jeśli to konieczne
        quantity_part = parts[0]  # Pierwsza część to ilość
        unit_part = " ".join(parts[1:])  # Reszta to jednostka
    else:
        quantity_part = parts[0]
        unit_part = ""

    # Jeśli ilość zawiera ułamek, konwertujemy go na liczbę dziesiętną
    quantity = convert_fraction_to_decimal(quantity_part)

    return quantity, unit_part


def get_recipe_ingredients(url):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(f"{url}")
        print(f"Załadowano stronę: {url}")

        # Czekamy na obecność sekcji składników
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "recipeIngredients"))
            )
            print(f"Znaleziono sekcję składników dla: {url}")
        except Exception as e:
            print(f"Nie udało się znaleźć sekcji składników dla {url}: {e}")
            driver.quit()
            return []

        # Sekcja składników
        ingredients_section = driver.find_element(By.ID, 'recipeIngredients')
        # print(f"HTML sekcji składników:\n{ingredients_section.get_attribute('outerHTML')}")

        ingredients = []

        # Znajdź wszystkie listy składników
        ingredient_lists = ingredients_section.find_elements(By.CLASS_NAME, 'recipe-ing-list')
        print(f"Liczba list składników znalezionych: {len(ingredient_lists)}")

        for idx, ingredient_list in enumerate(ingredient_lists):
            print(f"Przetwarzam listę składników {idx + 1}/{len(ingredient_lists)}")

            # Znajdź wszystkie elementy li w liście
            ingredient_items = ingredient_list.find_elements(By.TAG_NAME, 'li')
            print(f"Liczba składników w liście {idx + 1}: {len(ingredient_items)}")

            for item_idx, item in enumerate(ingredient_items):
                try:
                    # Przejdź głębiej do span z itemprop="recipeIngredient"
                    ingredient_span = item.find_element(By.CSS_SELECTOR, 'span[itemprop="recipeIngredient"]')

                    # Pobierz nazwę składnika
                    ingredient_name = ingredient_span.find_element(By.CLASS_NAME, 'ingredient')
                    ingredient_name_text = ingredient_name.text.strip() or ingredient_name.get_attribute("innerText").strip()

                    # Pobierz ilość składnika
                    ingredient_qty = ingredient_span.find_element(By.CLASS_NAME, 'qty')
                    ingredient_qty_text = ingredient_qty.text.strip() or ingredient_qty.get_attribute("innerText").strip()

                except Exception as e:
                    ingredient_name_text = ""
                    ingredient_qty_text = ""
                    print(f"Błąd podczas pobierania składnika (item {item_idx + 1}): {e}")

                # Dodaj składnik do listy
                if ingredient_name_text or ingredient_qty_text:
                    ingredients.append({
                        "product": ingredient_name_text,
                        "quantity": ingredient_qty_text
                    })

    except Exception as e:
        print(f"Wystąpił błąd podczas przetwarzania strony {url}: {e}")
    finally:
        driver.quit()

    # print(f"Znalezione składniki dla {url}: {ingredients}")
    return ingredients


def get_recipes(data):
    # Odczytanie linków do przepisów z przekazanej zmiennej (ciągu znaków)
    recipe_urls = [line.strip() for line in data.splitlines() if line.strip()]
    
    recipes = {}

    for url in recipe_urls:
        print(f"Scrapuję: {url}")
        recipe_name = url.split('/')[-1]  # Definiujemy nazwę przepisu niezależnie od wyniku
        ingredients = get_recipe_ingredients(url)
        if ingredients:
            recipes[recipe_name] = {"ingredients": ingredients}
        # print(f"Przepis: {recipe_name}, Składniki: {ingredients}")  # Debugowanie

    # print(f"Wszystkie przepisy: {recipes}")  # Debugowanie
    return recipes


def save_recipes_to_file(recipes, file_name=aniagotuje_results_filepath):
    print(f"Zapisuję dane: {recipes}")  # Debugowanie
    with open(file_name, "w", encoding="utf-8") as file:
        json.dump(recipes, file, ensure_ascii=False, indent=4)
    print(f"Zapisano przepisy do pliku {file_name}")


def aniagotuje_scrapper_main(data):
    recipes = get_recipes(data)
    save_recipes_to_file(recipes)

############### MAIN ###############
if __name__ == "__main__":
    # Uruchomienie scrapowania
    recipes = get_recipes()
    save_recipes_to_file(recipes)
