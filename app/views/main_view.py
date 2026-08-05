from __future__ import annotations
from models.activity_model import ActivityModel

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

STATE_IDLE = "idle"
STATE_RUNNING = "running"
STATE_PAUSED = "paused"

_STATUS_LABELS = {
    STATE_IDLE: "Idle",
    STATE_RUNNING: "Recording",
    STATE_PAUSED: "Paused",
}

_STATUS_COLORS = {
    STATE_IDLE: "#8a8a8a",
    STATE_RUNNING: "#0f9d58",
    STATE_PAUSED: "#f2a900",
}


class Card(QFrame):
    """Elevated container used to group related controls."""

    def __init__(self, title: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(12)
        if title:
            heading = QLabel(title)
            heading.setObjectName("cardTitle")
            self._layout.addWidget(heading)

    def body_layout(self) -> QVBoxLayout:
        return self._layout


class StatusDot(QLabel):
    """Small colored indicator reflecting the current tracking state."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(10, 10)
        self.set_state(STATE_IDLE)

    def set_state(self, state: str) -> None:
        color = _STATUS_COLORS.get(state, _STATUS_COLORS[STATE_IDLE])
        self.setStyleSheet(f"background-color: {color}; border-radius: 5px;")


class MainView(QMainWindow):
    """Main application window."""

    start_clicked = Signal()
    pause_clicked = Signal()
    stop_clicked = Signal()
    generate_summary_clicked = Signal()

    def __init__(self, model: ActivityModel, parent: QWidget | None = None, ) -> None:
        super().__init__(parent)
        self._model = model

        self.setWindowTitle("TrackBrain")
        self.resize(1080, 680)
        self.setMinimumSize(860, 560)
        self.setFont(QFont("Segoe UI", 10))

        self._state = STATE_IDLE
        self._next_log_entry_id = 0

        self._build_ui()
        self.setStyleSheet(_STYLE_SHEET)
        self.set_tracking_state(STATE_IDLE)

    # ---- construction ----------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        root.addWidget(self._build_header())
        root.addWidget(self._build_control_card())

        splitter = QSplitter(Qt.Horizontal)
        splitter.setObjectName("mainSplitter")
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_log_card())
        splitter.addWidget(self._build_summary_card())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        root.addWidget(splitter, stretch=1)

    def _build_header(self) -> QWidget:
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        text_box = QVBoxLayout()
        text_box.setSpacing(0)
        title = QLabel("TrackBrain")
        title.setObjectName("appTitle")
        subtitle = QLabel("Activity Tracker")
        subtitle.setObjectName("appSubtitle")
        text_box.addWidget(title)
        text_box.addWidget(subtitle)

        layout.addLayout(text_box)
        layout.addStretch(1)
        return header

    def _build_control_card(self) -> Card:
        card = Card()
        card.setObjectName("controlCard")
        row = QHBoxLayout()
        row.setSpacing(20)

        status_box = QVBoxLayout()
        status_box.setSpacing(6)
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        self._status_dot = StatusDot()
        self._status_label = QLabel()
        self._status_label.setObjectName("statusLabel")
        status_row.addWidget(self._status_dot)
        status_row.addWidget(self._status_label)
        status_row.addStretch(1)
        self._timer_label = QLabel("00:00:00")
        self._timer_label.setObjectName("timerLabel")
        status_box.addLayout(status_row)
        status_box.addWidget(self._timer_label)

        row.addLayout(status_box)
        row.addStretch(1)

        self._start_btn = QPushButton("Start")
        self._start_btn.setObjectName("startButton")
        self._pause_btn = QPushButton("Pause")
        self._pause_btn.setObjectName("pauseButton")
        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setObjectName("stopButton")

        for btn in (self._start_btn, self._pause_btn, self._stop_btn):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setMinimumHeight(40)
            btn.setMinimumWidth(110)
            row.addWidget(btn)

        self._start_btn.clicked.connect(self.start_clicked)
        self._pause_btn.clicked.connect(self.pause_clicked)
        self._stop_btn.clicked.connect(self.stop_clicked)

        card.body_layout().addLayout(row)
        return card

    def _build_log_card(self) -> Card:
        card = Card("Activity Log")
        self._log_table = QTableWidget(0, 2)
        self._log_table.setHorizontalHeaderLabels(["Time", "Activity"])
        header = self._log_table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self._log_table.verticalHeader().setVisible(False)
        self._log_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._log_table.setSelectionBehavior(QTableWidget.SelectRows)
        self._log_table.setAlternatingRowColors(True)
        self._log_table.setShowGrid(False)
        card.body_layout().addWidget(self._log_table)
        return card

    def _build_summary_card(self) -> Card:
        card = Card("AI Summary")

        self._summary_text = QTextEdit()
        self._summary_text.setObjectName("summaryText")
        self._summary_text.setReadOnly(True)
        self._summary_text.setPlaceholderText(
            "Generate a summary of your tracked activity..."
        )
        card.body_layout().addWidget(self._summary_text, stretch=1)

        self._generate_btn = QPushButton("Generate Summary")
        self._generate_btn.setObjectName("generateButton")
        self._generate_btn.setCursor(Qt.PointingHandCursor)
        self._generate_btn.setMinimumHeight(38)
        self._generate_btn.clicked.connect(self.generate_summary_clicked)
        card.body_layout().addWidget(self._generate_btn)

        return card

    # ---- public API for the controller -------------------------------

    def set_tracking_state(self, state: str) -> None:
        """Reflect the current tracking state (idle/running/paused)."""
        self._state = state
        self._status_dot.set_state(state)
        self._status_label.setText(_STATUS_LABELS.get(state, _STATUS_LABELS[STATE_IDLE]))
        self._pause_btn.setText("Resume" if state == STATE_PAUSED else "Pause")
        self._start_btn.setEnabled(state == STATE_IDLE)
        self._pause_btn.setEnabled(state in (STATE_RUNNING, STATE_PAUSED))
        self._stop_btn.setEnabled(state in (STATE_RUNNING, STATE_PAUSED))

    @Slot(str)
    def set_elapsed_time(self, text: str) -> None:
        self._timer_label.setText(text)

    @Slot(str, str)
    def add_log_entry(self, timestamp: str, activity: str) -> int:
        """Insert a new entry at the top of the activity log."""
        entry_id = self._next_log_entry_id
        self._next_log_entry_id += 1
        self._insert_log_row(0, entry_id, (timestamp, activity))
        return entry_id

    def set_log_entries(self, entries) -> None:
        """Replace the whole log, preserving the given order."""
        self._log_table.setRowCount(0)
        for timestamp, activity in entries:
            entry_id = self._next_log_entry_id
            self._next_log_entry_id += 1
            self._insert_log_row(self._log_table.rowCount(), entry_id, (timestamp, activity))

    def clear_log(self) -> None:
        self._log_table.setRowCount(0)

    def set_summary_text(self, text: str) -> None:
        self._summary_text.setMarkdown(text)

    def set_summary_generating(self, is_generating: bool) -> None:
        self._generate_btn.setDisabled(is_generating)
        self._generate_btn.setText("Generating…" if is_generating else "Generate Summary")

    # ---- helpers -------------------------------------------------------

    def _insert_log_row(self, row: int, entry_id: int, values: tuple[str, str]) -> None:
        self._log_table.insertRow(row)
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._log_table.setItem(row, column, item)
        self._log_table.item(row, 0).setData(Qt.UserRole, entry_id)


_STYLE_SHEET = """
QWidget#central {
    background-color: #f3f3f3;
}

QLabel#appTitle {
    font-size: 22px;
    font-weight: 600;
    color: #1a1a1a;
}

QLabel#appSubtitle {
    font-size: 12px;
    color: #6b6b6b;
}

QFrame#card {
    background-color: #ffffff;
    border: 1px solid #e3e3e3;
    border-radius: 8px;
}

QLabel#cardTitle {
    font-size: 13px;
    font-weight: 600;
    color: #3a3a3a;
    padding-bottom: 4px;
}

QLabel#statusLabel {
    font-size: 13px;
    font-weight: 500;
    color: #3a3a3a;
}

QLabel#timerLabel {
    font-size: 28px;
    font-weight: 600;
    color: #1a1a1a;
    font-family: "Consolas", "Segoe UI";
}

QPushButton {
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: 500;
    border: 1px solid #d6d6d6;
    background-color: #fafafa;
    color: #1a1a1a;
}

QPushButton:hover {
    background-color: #f0f0f0;
}

QPushButton:pressed {
    background-color: #e6e6e6;
}

QPushButton:disabled {
    color: #a3a3a3;
    background-color: #f5f5f5;
    border-color: #ececec;
}

QPushButton#startButton, QPushButton#generateButton {
    background-color: #0067c0;
    border: 1px solid #0067c0;
    color: #ffffff;
}

QPushButton#startButton:hover, QPushButton#generateButton:hover {
    background-color: #1975c8;
}

QPushButton#startButton:disabled, QPushButton#generateButton:disabled {
    background-color: #b9d7ee;
    border-color: #b9d7ee;
    color: #ffffff;
}

QPushButton#stopButton:hover {
    background-color: #fdecea;
    border-color: #e5484d;
    color: #c62828;
}

QTableWidget {
    background-color: #ffffff;
    border: none;
    gridline-color: #eeeeee;
    selection-background-color: #e5f1fb;
    selection-color: #1a1a1a;
    font-size: 12px;
}

QTableWidget::item {
    padding: 6px;
}

QHeaderView::section {
    background-color: #fafafa;
    color: #6b6b6b;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #e3e3e3;
    font-weight: 600;
    font-size: 11px;
}

QTextEdit#summaryText {
    background-color: #fbfbfb;
    border: 1px solid #ececec;
    border-radius: 6px;
    padding: 10px;
    font-size: 13px;
}

QSplitter#mainSplitter::handle {
    background-color: transparent;
    width: 16px;
}
"""


if __name__ == "__main__":
    # Manual preview only; the real entry point wires this view to a
    # controller elsewhere.
    import sys

    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    view = MainView()
    view.set_log_entries(
        [
            ("09:02", "PyCharm - TrackBrain"),
            ("08:55", "Outlook"),
            ("08:30", "Microsoft Teams - Standup"),
        ]
    )
    view.set_summary_text(
        "**Today so far:** mostly focused work in PyCharm, with a short "
        "standup meeting and a quick check of Outlook."
    )
    view.show()
    sys.exit(app.exec())
