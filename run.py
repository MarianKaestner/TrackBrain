import sys

from controllers.controller import Controller
from services.activity_tracker import ActivityTracker
from views.main_view import MainView
from models.activity_model import ActivityModel

from PySide6.QtWidgets import QApplication

app = QApplication()
model = ActivityModel()
view = MainView(model)
tracker = ActivityTracker()
controller = Controller(model, view, tracker)
view.show()
sys.exit(app.exec())