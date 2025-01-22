# ZakupoGenerator

ZakupoGenerator is a web application designed to scrape recipe data from **aniagotuje.pl** and convert it into a consolidated shopping basket. This tool takes multiple recipe URLs as input, processes the ingredient lists, and provides a combined shopping list with aggregated quantities.

---

## Features

### Core Features
- **Recipe Scraping**: Extract ingredient lists from recipe pages on **aniagotuje.pl**.
- **Ingredient Aggregation**: Sum up quantities of identical ingredients across all recipes.
- **Shopping Basket Generation**: Present a consolidated shopping list to streamline grocery shopping.

### Additional Features
- **User-Friendly Interface**: Input recipe URLs through an intuitive frontend.
- **Real-Time Processing**: Quickly processes input and generates a shopping list.
- **Clear Output Format**: Provides the shopping basket in an easy-to-read table format.

---

## Technologies Used

### Backend
The backend handles data scraping, processing, and aggregation. It is built using:

- **Python**: For data manipulation and aggregation of ingredient quantities. Version: 3.12.2
- **Selenium**: Library for web scraping and parsing HTML from **aniagotuje.pl**.

### Frontend
The frontend provides a simple and intuitive interface for users to interact with the application. It is built using:

- **Flask**: Lightweight web framework for building the API.
- **HTML/CSS/JavaScript**: For structuring and styling the user interface.
- **Bootstrap**: Framework for responsive and visually appealing design.

---

## Usage

1. Run Python file **run.py**.
2. Open the application in your browser (http://127.0.0.1:5000).
3. Paste URLs of recipes from **aniagotuje.pl** into the input field.
4. Click the "Generate Shopping List" button.
5. View and download the aggregated shopping list.


