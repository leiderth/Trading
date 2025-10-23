"""Widget de Historial de Trades"""

import requests
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
from PyQt6.QtGui import QColor

class HistoryWidget(QWidget):
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Simbolo", "Lado", "Entrada", "Salida", "P&L", "P&L %", "Duracion", "Fecha"
        ])
        
        header = self.table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.update_history)
        layout.addWidget(refresh_btn)
    
    def update_history(self):
        try:
            response = requests.get(f"{self.api_url}/api/metrics/trades", timeout=2)
            if response.status_code == 200:
                trades = response.json().get('trades', [])
                self.table.setRowCount(len(trades))
                
                for row, trade in enumerate(trades):
                    self.table.setItem(row, 0, QTableWidgetItem(trade.get('symbol', '')))
                    self.table.setItem(row, 1, QTableWidgetItem(trade.get('side', '')))
                    self.table.setItem(row, 2, QTableWidgetItem(f"{trade.get('entry_price', 0):.5f}"))
                    self.table.setItem(row, 3, QTableWidgetItem(f"{trade.get('exit_price', 0):.5f}"))
                    
                    pnl_item = QTableWidgetItem(f"${trade.get('pnl', 0):.2f}")
                    if trade.get('pnl', 0) > 0:
                        pnl_item.setForeground(QColor(46, 204, 113))
                    else:
                        pnl_item.setForeground(QColor(231, 76, 60))
                    self.table.setItem(row, 4, pnl_item)
                    
                    self.table.setItem(row, 5, QTableWidgetItem(f"{trade.get('pnl_percent', 0):+.2f}%"))
                    self.table.setItem(row, 6, QTableWidgetItem(f"{trade.get('duration', 0)/60:.1f} min"))
                    self.table.setItem(row, 7, QTableWidgetItem(trade.get('closed_at', '')[:19]))
        except:
            pass
