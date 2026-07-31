from PySide6.QtCore import Signal, Slot, QObject
from typing import List, Tuple
from datetime import datetime


class ActivityModel(QObject):
    log_added = Signal(str, str)

    def __init__(self):
        super().__init__()
        self._log: List[Tuple[str, str]] = []
        self._new_log: Tuple[str, str] | None = None

    @Slot(str, str)
    def add_log(self, time: str, activity: str) -> None:
        self._new_log = (time, activity)
        self._log.append(self._new_log)
        print("Added log for", activity)
        self.log_added.emit(self._new_log[0], self._new_log[1])
