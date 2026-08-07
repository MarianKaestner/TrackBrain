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
        self._restore_state()

    def _connect_main_view_to_tracker(self):
        self.view.start_clicked.connect(self.tracker.start)
        self.view.stop_clicked.connect(self.tracker.stop)
        self.view.pause_clicked.connect(self.tracker.pause)

    def _connect_tracker_to_main_view(self):
        self.tracker.tracking_started.connect(lambda: self.view.set_tracking_state("running"))
        self.tracker.tracking_resumed.connect(lambda: self.view.set_tracking_state("running"))
        self.tracker.tracking_paused.connect(lambda: self.view.set_tracking_state("paused"))
        self.tracker.tracking_finished.connect(lambda: self.view.set_tracking_state("idle"))

        self.tracker.time_changed.connect(self.view.set_elapsed_time)

    def _connect_model_to_view(self):
        self.model.log_added.connect(self.view.add_log_entry)
        self.model.log_cleared.connect(self.view.clear_log)
        self.model.log_loaded.connect(self.view.set_log_entries)

    def _connect_tracker_to_model(self):
        self.tracker.activity_changed.connect(self.model.add_log)
        self.tracker.tracking_started.connect(self.model.clear_log)

    def _restore_state(self):
        self.model.load()
        self.view.set_tracking_state(self.tracker.status)
        self.view.set_elapsed_time(self.tracker.initial_elapsed_display)