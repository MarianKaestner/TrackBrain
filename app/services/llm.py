from ollama import chat, ChatResponse
from PySide6.QtCore import QThread, Signal

from models.activity_model import ActivityModel


class LLM:
    def __init__(self, activity_model: ActivityModel):
        self._activity_model = activity_model

    def get_summary(self) -> str:
        response: ChatResponse = chat(model="gemma4:e2b", messages=[
            {
                "role": "user",
                "content": f"Do a short summary of the work activities from the log below in natural language. "
                           f"Only output the summary."
                           f"\n{self._activity_model.log}"
            }
        ])
        return str(response.message.content)


class SummaryWorker(QThread):
    """Runs LLM.get_summary() off the UI thread."""

    summary_ready = Signal(str)

    def __init__(self, llm: LLM, parent=None):
        super().__init__(parent)
        self._llm = llm

    def run(self) -> None:
        summary = self._llm.get_summary()
        self.summary_ready.emit(summary)