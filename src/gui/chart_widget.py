"""
Widget de Grafico de Precios
"""

import requests
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from datetime import datetime


class ChartWidget(QWidget):
    """Widget para mostrar grafico de precios"""
    
    def __init__(self):
        super().__init__()
        
        self.api_url = "http://127.0.0.1:8000"
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Titulo
        title = QLabel("📊 GRAFICO DE PRECIOS")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ecf0f1; padding: 10px;")
        layout.addWidget(title)
        
        # Grafico
        pg.setConfigOption('background', '#2c3e50')
        pg.setConfigOption('foreground', 'w')
        
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Precio')
        self.plot_widget.setLabel('bottom', 'Tiempo')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        layout.addWidget(self.plot_widget)
    
    def update_chart(self):
        """Actualiza el grafico"""
        try:
            response = requests.get(
                f"{self.api_url}/api/market/data/EUR/USD?timeframe=5m&bars=100",
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                
                if data:
                    closes = [d['close'] for d in data]
                    
                    self.plot_widget.clear()
                    self.plot_widget.plot(closes, pen=pg.mkPen(color='#3498db', width=2))
                    
        except Exception as e:
            pass
