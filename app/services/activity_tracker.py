from sys import platform

import pywinctl as pwc
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QThread


class _Worker(QObject):
    activity_changed = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.running = False
        self._current_activity = ""

    def run(self):
        self.running = True
        while self.running:
            activity = pwc.getActiveWindowTitle()
            if activity and activity != self._current_activity:
                self._current_activity = activity
                self.activity_changed.emit(activity)
        self.finished.emit()


class ActivityTracker(QObject):
    activity_changed = Signal(str, str)
    tracking_started = Signal()
    tracking_finished = Signal()

    def __init__(self):
        super().__init__()
        self._thread: QThread | None = None
        self._worker: _Worker | None = None
        self.activity_change_timestamp = 0

    @Slot()
    def start(self):
        if self._thread is not None and self._thread.isRunning():
            return
        self._thread = QThread()
        self._worker = _Worker()
        self._worker.moveToThread(self._thread)
        self._worker.activity_changed.connect(self._handle_new_activity)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.deleteLater)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.finished.connect(self.tracking_finished)
        self._thread.start()
        self.tracking_started.emit()

    @Slot()
    def stop(self):
        if self._worker:
            self._worker.running = False

    @Slot()
    def pause(self):
        pass    # TODO

    @Slot()
    def _handle_new_activity(self, activity: str) -> None:
        self.activity_changed.emit(datetime.now().strftime("%H:%M:%S"), activity)