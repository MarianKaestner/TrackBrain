import pywinctl as pwc
from datetime import datetime, timedelta
from PySide6.QtCore import QObject, Signal, Slot, QThread, QTimer


STATE_IDLE = "idle"
STATE_RUNNING = "running"
STATE_PAUSED = "paused"


class _Worker(QObject):
    activity_changed = Signal(str)
    elapsed_time_changed = Signal(str)
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._supposed_to_run = False
        self._current_activity = ""
        self.start_time = datetime.now()
        self._current_elapsed_time = ""
        self._timer = QTimer(self)
        self._timer.setInterval(100)
        self._timer.timeout.connect(self._run)

    def start(self) -> None:
        self._supposed_to_run = True
        self._timer.start()

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
        elapsed = datetime.now() - self.start_time
        total_seconds = int(elapsed.total_seconds())
        h, rem = divmod(total_seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"


class ActivityTracker(QObject):
    activity_changed = Signal(str, str)
    time_changed = Signal(str)
    tracking_started = Signal()
    tracking_paused = Signal()
    tracking_resumed = Signal()
    tracking_finished = Signal()

    def __init__(self):
        super().__init__()
        self.status = STATE_IDLE
        self._thread: QThread | None = None
        self._worker: _Worker | None = None
        self._start_time = datetime.now()
        self._accumulated_elapsed = timedelta()

    @Slot()
    def start(self):
        if self.status == STATE_RUNNING:
            return
        if self.status == STATE_IDLE:
            self._accumulated_elapsed = timedelta()
            self._start_time = datetime.now()
        elif self.status == STATE_PAUSED:
            self._start_time = datetime.now() - self._accumulated_elapsed
        self._thread = QThread()
        self._worker = _Worker()
        self._worker.start_time = self._start_time
        self._worker.moveToThread(self._thread)
        self._worker.activity_changed.connect(self._handle_new_activity)
        self._worker.elapsed_time_changed.connect(self._handle_new_time)
        self._thread.started.connect(self._worker.start)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._thread.deleteLater)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.start()
        if self.status == STATE_IDLE:
            self.tracking_started.emit()
        elif self.status == STATE_PAUSED:
            self.tracking_resumed.emit()
        else:
            raise ValueError(f"status is not supposed to be {self.status}")
        self.status = STATE_RUNNING

    @Slot()
    def stop(self):
        if self.status != STATE_IDLE and self._worker and self._thread:
            self._worker.stop()
            self._thread.quit()
            self.tracking_finished.emit()
            self.status = STATE_IDLE

    @Slot()
    def pause(self):
        if self.status == STATE_RUNNING and self._worker and self._thread:
            self._accumulated_elapsed = datetime.now() - self._start_time
            self._worker.stop()
            self._thread.quit()
            self._handle_new_activity("Pause")
            self.tracking_paused.emit()
            self.status = STATE_PAUSED
        elif self.status == STATE_PAUSED:
            self.start()

    @Slot()
    def _handle_new_activity(self, activity: str) -> None:
        self.activity_changed.emit(datetime.now().strftime("%H:%M:%S"), activity)

    @Slot()
    def _handle_new_time(self, time: str) -> None:
        self.time_changed.emit(time)