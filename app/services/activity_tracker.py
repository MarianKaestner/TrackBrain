import pywinctl as pwc
from datetime import datetime
from PySide6.QtCore import QObject, Signal, Slot, QThread, QTimer


class _Worker(QObject):
    activity_changed = Signal(str)
    elapsed_time_changed = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._supposed_to_run = False
        self._current_activity = ""
        self._start_time = datetime.now()
        self._current_elapsed_time = ""
        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._run)

    def start(self):
        self._supposed_to_run = True
        self._timer.start()
        self._start_time = datetime.now()

    def stop(self):
        self._supposed_to_run = False

    def _run(self):
        if not self._supposed_to_run:
            self._timer.stop()
            self.finished.emit()
            return
        elapsed_time = self._get_elapsed_time()
        if elapsed_time != self._current_elapsed_time:
            self._current_time = elapsed_time
            self.elapsed_time_changed.emit(elapsed_time)
        activity = pwc.getActiveWindowTitle()
        if activity and activity != self._current_activity:
            self._current_activity = activity
            self.activity_changed.emit(activity)

    def _get_elapsed_time(self) -> str:
        elapsed = datetime.now() - self._start_time
        total_seconds = int(elapsed.total_seconds())
        h, rem = divmod(total_seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"


class ActivityTracker(QObject):
    activity_changed = Signal(str, str)
    time_changed = Signal(str)
    tracking_started = Signal()
    tracking_finished = Signal()

    def __init__(self):
        super().__init__()
        self.running = False
        self._thread: QThread | None = None
        self._worker: _Worker | None = None
        self.activity_change_timestamp = 0

    @Slot()
    def start(self):
        if self.running:
            return
        self._thread = QThread()
        self._worker = _Worker()
        self._worker.moveToThread(self._thread)
        self._worker.activity_changed.connect(self._handle_new_activity)
        self._worker.elapsed_time_changed.connect(self._handle_new_time)
        self._thread.started.connect(self._worker.start)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._thread.deleteLater)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.finished.connect(self.tracking_finished.emit)
        self._thread.start()
        self.tracking_started.emit()
        self.running = True

    @Slot()
    def stop(self):
        if self._worker and self._thread:
            self._worker.stop()
            self.running = False

    @Slot()
    def pause(self):
        pass    # TODO

    @Slot()
    def _handle_new_activity(self, activity: str) -> None:
        self.activity_changed.emit(datetime.now().strftime("%H:%M:%S"), activity)

    @Slot()
    def _handle_new_time(self, time: str) -> None:
        self.time_changed.emit(time)