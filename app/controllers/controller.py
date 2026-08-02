from PySide6.QtWidgets import QWidget

from services.activity_tracker import ActivityTracker
from views.main_view import MainView
from models.activity_model import ActivityModel

class Controller:
    def __init__(self, model: ActivityModel, view: MainView, tracker: ActivityTracker):
        self.model = model
        self.view = view
        self.tracker = tracker

        self._connect_main_view_to_tracker()
        self._connect_tracker_to_main_view()
        self._connect_tracker_to_model()
        self._connect_model_to_view()

    def _connect_main_view_to_tracker(self):
        self.view.start_clicked.connect(self.tracker.start)

    def _connect_tracker_to_main_view(self):
        self.tracker.tracking_started.connect(lambda: self.view.set_tracking_state("running"))
        self.tracker.tracking_started.connect(lambda: self.view.set_tracking_state("idle"))

    def _connect_model_to_view(self):
        self.model.log_added.connect(self.view.add_log_entry)

    def _connect_tracker_to_model(self):
        self.tracker.activity_changed.connect(self.model.add_log)