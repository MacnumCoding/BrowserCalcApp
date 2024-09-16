import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

class calculator(QMainWindow):
    def __init__(self):
        super(calculator, self).__init__()
        self.setGeometry(1200, 300, 700, 700)
        self.setWindowTitle("Calculator")
        self.setToolTip("Enter 2 numbers and press buttons")
        self.setWindowIcon(QIcon("kitten.jpeg"))
        self.initUI()

    def initUI(self):
        self.lbl_number1 = QtWidgets.QLabel(self)
        self.lbl_number1.setText("Number1")
        self.lbl_number1.move(50, 30)

        self.txt_number1 = QtWidgets.QLineEdit(self)
        self.txt_number1.move(150, 30)
        self.txt_number1.resize(200, 32)

        self.lbl_number2 = QtWidgets.QLabel(self)
        self.lbl_number2.setText("number2")
        self.lbl_number2.move(50, 80)

        self.txt_number2 = QtWidgets.QLineEdit(self)
        self.txt_number2.move(150, 80)
        self.txt_number2.resize(200, 32)

        self.btn_add = QtWidgets.QPushButton(self)
        self.btn_add.setText("Addition")
        self.btn_add.clicked.connect(self.calculate)
        self.btn_add.move(150, 130)

        self.btn_sub = QtWidgets.QPushButton(self)
        self.btn_sub.setText("Subtraction")
        self.btn_sub.clicked.connect(self.calculate)
        self.btn_sub.move(150, 180)

        self.btn_div = QtWidgets.QPushButton(self)
        self.btn_div.setText("Division")
        self.btn_div.clicked.connect(self.calculate)
        self.btn_div.move(150, 230)

        self.btn_mul = QtWidgets.QPushButton(self)
        self.btn_mul.setText("Multiplication")
        self.btn_mul.clicked.connect(self.calculate)
        self.btn_mul.move(150, 280)

        self.lbl_result = QtWidgets.QLabel(self)
        self.lbl_result.setText("Result: ")
        self.lbl_result.move(150, 330)
        self.lbl_result.resize(200, 32)

    def calculate(self):
        sender = self.sender()
        num1_text = self.txt_number1.text()
        num2_text = self.txt_number2.text()

        if not num1_text or not num2_text:
            result = "Invalid Input, Please Enter Numbers"
        else:
            num1 = int(num1_text)
            num2 = int(num2_text)
            match sender.text():
                case "Addition":
                    result = num1 + num2
                case "Subtraction":
                    result = num1 - num2
                case "Division":
                    if num2 == 0:
                        result = "Invalid Input, Cannot Divide By 0"
                    else:
                        result = num1 / num2
                case "Multiplication":
                    result = num1 * num2
                case _:
                    result = "Invalid Input"

        self.lbl_result.setText("Result: " + str(result))


def app():
    app = QApplication(sys.argv)
    win = calculator()
    win.show()
    sys.exit(app.exec_())

app()