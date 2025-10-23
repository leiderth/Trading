"""Widget de Logs del Sistema"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton
from pathlib import Path
from datetime import datetime

class LogsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: Consolas;")
        layout.addWidget(self.text_edit)
        
        refresh_btn = QPushButton("🔄 Actualizar Logs")
        refresh_btn.clicked.connect(self.load_logs)
        layout.addWidget(refresh_btn)
        
        self.load_logs()
    
    def load_logs(self):
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                today = datetime.now().strftime("%Y-%m-%d")
                log_file = log_dir / f"trading_{today}.log"
                
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        logs = f.readlines()
                        self.text_edit.setPlainText(''.join(logs[-100:]))  # Ultimas 100 lineas
                else:
                    self.text_edit.setPlainText("No hay logs para hoy")
        except Exception as e:
            self.text_edit.setPlainText(f"Error cargando logs: {e}")
