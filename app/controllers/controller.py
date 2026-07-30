from PySide6.QtWidgets import QWidget

from services.activity_tracker import ActivityTracker
from views.main_view import MainView

class Controller:
    def __init__(self, view: MainView, tracker: ActivityTracker) -> None:
        self.view = view

    def _connectMainView(self):
        self.view.start_clicked.connect()