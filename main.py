# import sys
#
# from PyQt6.QtCore import QSize, Qt
# from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
#
#
# # Subclass QMainWindow to customize your application's main window
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#
#         self.setWindowTitle("Done")
#         button = QPushButton("Press Me!")
#         self.setMinimumSize(QSize(1000, 600))
#         # Set the central widget of the Window.
#         self.setCentralWidget(button)
#
#
# app = QApplication(sys.argv)
#
# window = MainWindow()
# window.show()
#
# app.exec()
import func
# tm = func.TaskManager("./file.txt")
task = func.Task(tags=["@tag"], projects=[], priority="(A)")
