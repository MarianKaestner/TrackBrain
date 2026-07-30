import sys

from views.main_view import MainView

from PySide6.QtWidgets import QApplication

app = QApplication()
view = MainView()
view.show()
sys.exit(app.exec_())