import sys
import os
import sqlite3
import requests
from PyQt5.QtWidgets import (QApplication, QLabel, QLineEdit, QVBoxLayout, 
                             QWidget, QPushButton, QStackedWidget, QHBoxLayout)
from PyQt5.QtCore import QDate

app_id = os.getenv('NUTRITIONIX_APP_ID')
app_key = os.getenv('NUTRITIONIX_APP_KEY')

class CalorieTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Calorie Tracker")
        self.setGeometry(100, 100, 400, 300)
        self.setToolTip("Every measure is in grams")

        self.stacked_widget = QStackedWidget()
        self.initUI()

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.conn = sqlite3.connect('calories.db')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calorie_intake (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                calories REAL,
                protein REAL,
                sugar REAL
            )
        ''')
        self.conn.commit()

    def initUI(self):
        page1 = QWidget()
        page1_layout = QVBoxLayout()

        self.date_label = QLabel(f"Date: {QDate.currentDate().toString('yyyy-MM-dd')}")
        page1_layout.addWidget(self.date_label)

        self.total_calories_label = QLabel("Total Calories Today: 0")
        page1_layout.addWidget(self.total_calories_label)

        self.total_protein_label = QLabel("Total Protein Today: 0g")
        page1_layout.addWidget(self.total_protein_label)

        self.total_sugar_label = QLabel("Total Sugar Today: 0g")
        page1_layout.addWidget(self.total_sugar_label)

        self.calorie_input = QLineEdit()
        self.calorie_input.setPlaceholderText("Enter calories")
        page1_layout.addWidget(self.calorie_input)

        self.protein_input = QLineEdit()
        self.protein_input.setPlaceholderText("Enter protein in grams")
        page1_layout.addWidget(self.protein_input)

        self.sugar_input = QLineEdit()
        self.sugar_input.setPlaceholderText("Enter sugar in grams")
        page1_layout.addWidget(self.sugar_input)

        add_calories_btn = QPushButton("Add Calories")
        add_calories_btn.clicked.connect(self.add_calories)
        page1_layout.addWidget(add_calories_btn)

        add_protein_btn = QPushButton("Add Protein")
        add_protein_btn.clicked.connect(self.add_protein)
        page1_layout.addWidget(add_protein_btn)

        add_sugar_btn = QPushButton("Add Sugar")
        add_sugar_btn.clicked.connect(self.add_sugar)
        page1_layout.addWidget(add_sugar_btn)

        self.food_input = QLineEdit()
        self.food_input.setPlaceholderText("Search for a food item")
        page1_layout.addWidget(self.food_input)

        search_btn = QPushButton("Search Food Item")
        search_btn.clicked.connect(self.search_food)
        page1_layout.addWidget(search_btn)

        page1.setLayout(page1_layout)
        self.stacked_widget.addWidget(page1)

        page2 = QWidget()
        page2_layout = QVBoxLayout()

        self.history_label = QLabel("Calorie Intake History")
        page2_layout.addWidget(self.history_label)

        self.history_data_label = QLabel("")
        page2_layout.addWidget(self.history_data_label)

        back_to_main_btn = QPushButton("Back to Main Page")
        back_to_main_btn.clicked.connect(self.show_main_page)
        page2_layout.addWidget(back_to_main_btn)

        page2.setLayout(page2_layout)
        self.stacked_widget.addWidget(page2)

        history_btn = QPushButton("View History")
        history_btn.clicked.connect(self.show_history)
        page1_layout.addWidget(history_btn)
    
    def show_main_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def add_calories(self):
        calories = float(self.calorie_input.text())
        current_date = QDate.currentDate().toString('yyyy-MM-dd')
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO calorie_intake (date, calories, protein, sugar)
            VALUES (?, ?, ?, ?)
        ''', (current_date, calories, 0, 0))
        self.conn.commit()
        self.update_calories_display()

    def add_protein(self):
        protein = float(self.protein_input.text())
        current_date = QDate.currentDate().toString('yyyy-MM-dd')
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE calorie_intake
            SET protein = protein + ?
            WHERE date = ?
        ''', (protein, current_date))
        self.conn.commit()
        self.update_calories_display()

    def add_sugar(self):
        sugar = float(self.sugar_input.text())
        current_date = QDate.currentDate().toString('yyyy-MM-dd')
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE calorie_intake
            SET sugar = sugar + ?
            WHERE date = ?
        ''', (sugar, current_date))
        self.conn.commit()
        self.update_calories_display()

    def update_calories_display(self):
        current_date = QDate.currentDate().toString('yyyy-MM-dd')
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT SUM(calories), SUM(protein), SUM(sugar) FROM calorie_intake WHERE date = ?
        ''', (current_date,))
        data = cursor.fetchone()

        total_calories = data[0] if data[0] else 0
        total_protein = data[1] if data[1] else 0
        total_sugar = data[2] if data[2] else 0

        self.total_calories_label.setText(f"Total Calories Today: {total_calories}")
        self.total_protein_label.setText(f"Total Protein Today: {total_protein}g")
        self.total_sugar_label.setText(f"Total Sugar Today: {total_sugar}g")

    def search_food(self):
        food_item = self.food_input.text()
        
        headers = {
            'x-app-id': app_id,
            'x-app-key': app_key,
        }

        params = {
            'query': food_item,
            'num_servings': 1,
            'locale': 'en_US',
        }

        response = requests.post('https://trackapi.nutritionix.com/v2/natural/nutrients', headers=headers, json=params)

        if response.status_code == 200:
            data = response.json()
            food_name = data['foods'][0]['food_name']
            calories = data['foods'][0]['nf_calories']
            protein = data['foods'][0]['nf_protein']
            sugar = data['foods'][0]['nf_sugars']
            serving_size = data['foods'][0]['serving_weight_grams']
            
            self.calorie_input.setText(str(calories))
            self.protein_input.setText(str(protein))
            self.sugar_input.setText(str(sugar))
            
            print(f"{food_name} (Serving Size: {serving_size}g) contains {calories} calories, {protein}g protein, {sugar}g sugar.")
        else:
            print(f"Error: {response.status_code}, {response.text}")

    def show_history(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT date, SUM(calories), SUM(protein), SUM(sugar) 
            FROM calorie_intake
            GROUP BY date
            ORDER BY date DESC
        ''')
        data = cursor.fetchall()

        history_text = ""
        for entry in data:
            history_text += f"Date: {entry[0]}, Calories: {entry[1]}, Protein: {entry[2]}g, Sugar: {entry[3]}g\n"
        
        self.history_data_label.setText(history_text)
        self.stacked_widget.setCurrentIndex(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalorieTrackerApp()
    window.show()
    sys.exit(app.exec_())
