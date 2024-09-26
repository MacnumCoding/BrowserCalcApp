import sys
import os
import requests
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QStackedWidget, QMessageBox, QListWidget

# Replace these with your actual app ID and app key
app_id = os.getenv('NUTRITIONIX_APP_ID')
app_key = os.getenv('NUTRITIONIX_APP_KEY')

if app_id is None or app_key is None:
    print("Error: API credentials are not set.")

# Database setup
db_name = "calories.db"

# Initialize or connect to the database
def init_db():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS calorie_intake (
            date TEXT PRIMARY KEY,
            total_calories INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Fetch the calorie intake for the current date from the database
def get_today_calories():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    today_date = datetime.now().strftime("%Y-%m-%d")
    c.execute('SELECT total_calories FROM calorie_intake WHERE date = ?', (today_date,))
    result = c.fetchone()
    conn.close()
    if result:
        return result[0]
    else:
        return 0

# Update or insert the calorie intake for the current date in the database
def update_today_calories(calories):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    today_date = datetime.now().strftime("%Y-%m-%d")
    c.execute('''
        INSERT INTO calorie_intake (date, total_calories) 
        VALUES (?, ?)
        ON CONFLICT(date) 
        DO UPDATE SET total_calories = ?
    ''', (today_date, calories, calories))
    conn.commit()
    conn.close()

# Fetch all calorie intake history from the database
def fetch_calorie_history():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('SELECT date, total_calories FROM calorie_intake ORDER BY date DESC')
    history = c.fetchall()
    conn.close()
    return history

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Create a QStackedWidget to hold different pages
        self.stacked_widget = QStackedWidget()

        # Initialize daily calorie intake from the database
        self.daily_calories = get_today_calories()
        self.searched_item_calories = 0  # To hold calories from the searched food item

        # Create the first page with input field and calorie display
        self.page1 = QWidget()
        self.page1_layout = QVBoxLayout()

        # Display current date
        self.current_date_label = QLabel(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        self.page1_layout.addWidget(self.current_date_label)

        # Label to display the daily calorie intake
        self.calorie_label = QLabel(f"Total Calories Today: {self.daily_calories}")
        self.page1_layout.addWidget(self.calorie_label)

        # Input field for adding calories manually
        self.calorie_input = QLineEdit()
        self.calorie_input.setPlaceholderText("Enter calorie amount...")
        self.page1_layout.addWidget(self.calorie_input)

        # Button to add the manually entered calories
        self.add_button = QPushButton("Add Calories")
        self.add_button.clicked.connect(self.add_calories)
        self.page1_layout.addWidget(self.add_button)

        # ---- Search Bar for Food Item ----
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter a food item to search...")
        self.page1_layout.addWidget(self.search_input)

        # Search button to trigger API request
        self.search_button = QPushButton("Search Food")
        self.search_button.clicked.connect(self.search_food)
        self.page1_layout.addWidget(self.search_button)

        # Label to display search result
        self.search_result_label = QLabel("")
        self.page1_layout.addWidget(self.search_result_label)

        # Button to add the searched food item's calories to the daily total
        self.add_searched_calories_button = QPushButton("Add Searched Item's Calories")
        self.add_searched_calories_button.clicked.connect(self.add_searched_item_calories)
        self.page1_layout.addWidget(self.add_searched_calories_button)
        self.add_searched_calories_button.setEnabled(False)  # Disable until a search is made

        # Button to go to calorie history page
        self.history_button = QPushButton("View Calorie History")
        self.history_button.clicked.connect(self.show_history_page)
        self.page1_layout.addWidget(self.history_button)

        # Setting the layout for page 1
        self.page1.setLayout(self.page1_layout)

        # Create the calorie history page
        self.page2 = QWidget()
        self.page2_layout = QVBoxLayout()
        self.history_list = QListWidget()
        self.page2_layout.addWidget(self.history_list)

        # Back button to return to the main page
        self.back_button = QPushButton("Back to Main Page")
        self.back_button.clicked.connect(self.show_main_page)
        self.page2_layout.addWidget(self.back_button)

        # Setting the layout for page 2
        self.page2.setLayout(self.page2_layout)

        # Add pages to the stacked widget
        self.stacked_widget.addWidget(self.page1)  # index 0
        self.stacked_widget.addWidget(self.page2)  # index 1

        # Set the layout of the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        # Set the window title
        self.setWindowTitle("Calorie Tracker")
        self.resize(400, 300)

        # Load calorie history into the list on page 2
        self.load_calorie_history()

    def load_calorie_history(self):
        """
        Loads calorie history from the database into the history list widget.
        """
        self.history_list.clear()  # Clear the list before loading
        history = fetch_calorie_history()
        for date, calories in history:
            self.history_list.addItem(f"{date}: {calories} calories")

    def show_history_page(self):
        """
        Switches to the calorie history page.
        """
        self.load_calorie_history()  # Load history before showing the page
        self.stacked_widget.setCurrentIndex(1)

    def show_main_page(self):
        """
        Switches back to the main page.
        """
        self.stacked_widget.setCurrentIndex(0)

    def add_calories(self):
        """
        Adds the entered calorie amount to the daily calorie total and updates the label.
        """
        try:
            calorie_value = int(self.calorie_input.text())
            self.daily_calories += calorie_value
            self.calorie_label.setText(f"Total Calories Today: {self.daily_calories}")
            self.calorie_input.clear()
            update_today_calories(self.daily_calories)  # Update the database
        except ValueError:
            self.calorie_label.setText("Please enter a valid number.")

    def search_food(self):
        """
        Searches for the given food item using the Nutritionix API and displays the result.
        """
        food_item = self.search_input.text()
        if not food_item:
            QMessageBox.warning(self, "Input Error", "Please enter a food item.")
            return

        headers = {
            'x-app-id': app_id,
            'x-app-key': app_key,
        }

        params = {
            'query': food_item,
            'num_servings': 1,
            'locale': 'en_US',
        }

        try:
            response = requests.post('https://trackapi.nutritionix.com/v2/natural/nutrients', headers=headers, json=params)

            if response.status_code == 200:
                data = response.json()
                food_name = data['foods'][0]['food_name']
                calories = data['foods'][0]['nf_calories']
                total_fat = data['foods'][0]['nf_total_fat']
                total_protein = data['foods'][0]['nf_protein']
                total_sugar = data['foods'][0]['nf_sugars']
                serving_size = data['foods'][0]['serving_weight_grams']

                # Store the calories of the searched food item for adding later
                self.searched_item_calories = calories

                # Enable the button to add the calories
                self.add_searched_calories_button.setEnabled(True)

                # Display search result with serving size and other nutritional info
                result_text = (f"{food_name} ({serving_size}g):\n"
                               f"Calories: {calories} kcal\n"
                               f"Total Fat: {total_fat}g\n"
                               f"Protein: {total_protein}g\n"
                               f"Sugar: {total_sugar}g")
                self.search_result_label.setText(result_text)
            else:
                error_message = f"Error: {response.status_code}, {response.text}"
                QMessageBox.critical(self, "API Error", error_message)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def add_searched_item_calories(self):
        """
        Adds the calories from the searched food item to the daily calorie total.
        """
        self.daily_calories += self.searched_item_calories
        self.calorie_label.setText(f"Total Calories Today: {self.daily_calories}")
        update_today_calories(self.daily_calories)  # Update the database

if __name__ == '__main__':
    app = QApplication(sys.argv)
    init_db()
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
