import csv

from PySide6.QtCore import Slot

from models.activity_model import ActivityModel


class CSVSaver:
    def __init__(self, model: ActivityModel):
        self._model = model

    @Slot(str)
    def save_log(self, path: str) -> None:
        with open(path, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in self._model.log:
                writer.writerow(row)