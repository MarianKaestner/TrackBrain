import sys

from controllers.controller import Controller
from services.activity_tracker import ActivityTracker
from services.sqlite_storage import Storage
from views.main_view import MainView
from models.activity_model import ActivityModel

from PySide6.QtWidgets import QApplication

app = QApplication()
storage = Storage()
model = ActivityModel(storage)
view = MainView(model)
tracker = ActivityTracker(storage)
controller = Controller(model, view, tracker)
view.show()
exit_code = app.exec()
storage.close()
sys.exit(exit_code)