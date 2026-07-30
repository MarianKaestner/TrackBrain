from sys import platform

import pywinctl as pwc
from PySide6.QtCore import QObject, Signal, QThread

class _Worker(QObject):
    activity_changed = Signal(str)

    def __init__(self) -> None:
        self.running = False
        self._current_activity = ""

    def run(self):
        self.running = True
        while self.running:
            activity = pwc.getActiveWindowTitle()
            if activity != self.current_activity:
                self.current_activity = activity
                self.activity_changed.emit(self.current_activity)


class ActivityTracker(QObject):
    activity_changed = Signal(object)

    def __init__(self) -> None:
        self._thread = QThread()
        self._worker = _Worker()

    def start(self):
        pass    # TODO

    def stop(self):
        pass    # TODO

    def pause(self):
        pass    # TODO