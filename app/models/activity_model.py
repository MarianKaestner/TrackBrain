from PySide6.QtCore import Signal, Slot, QObject
from typing import List, Tuple

from services.sqlite_storage import Storage


class ActivityModel(QObject):
    log_added = Signal(str, str)
    log_cleared = Signal()
    log_loaded = Signal(list)

    def __init__(self, storage: Storage):
        super().__init__()
        self._storage = storage
        self._log: List[Tuple[str, str]] = []
        self._new_log: Tuple[str, str] | None = None

    # Properties
    @property
    def log(self) -> List[Tuple[str, str]]:
        return list(self._log)

    def load(self) -> None:
        """Restore the log mirrored on disk and notify listeners."""
        self._log = self._storage.get_log_entries()
        self.log_loaded.emit(list(reversed(self._log)))

    @Slot(str, str)
    def add_log(self, time: str, activity: str) -> None:
        self._new_log = (time, activity)
        self._log.append(self._new_log)
        self._storage.add_log_entry(time, activity)
        self.log_added.emit(self._new_log[0], self._new_log[1])

    @Slot()
    def clear_log(self) -> None:
        self._log.clear()
        self._storage.clear_log()
        self.log_cleared.emit()
