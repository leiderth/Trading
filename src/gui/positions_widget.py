"""
Widget de Posiciones Abiertas
"""

import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class PositionsWidget(QWidget):
    """Widget para mostrar posiciones abiertas"""
    
    def __init__(self, api_url: str):
        super().__init__()
        
        self.api_url = api_url
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        
        layout = QVBoxLayout(self)
        
        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID", "Simbolo", "Lado", "Cantidad", "Precio Entrada",
            "Precio Actual", "P&L", "P&L %", "Acciones"
        ])
        
        # Ajustar columnas
        header = self.table.horizontalHeader()
        for i in range(8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
        # Boton actualizar
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.clicked.connect(self.update_positions)
        layout.addWidget(refresh_btn)
    
    def update_positions(self):
        """Actualiza la tabla de posiciones"""
        try:
            response = requests.get(f"{self.api_url}/api/broker/positions", timeout=2)
            
            if response.status_code == 200:
                positions = response.json().get('positions', [])
                
                self.table.setRowCount(len(positions))
                
                for row, pos in enumerate(positions):
                    self.table.setItem(row, 0, QTableWidgetItem(pos['id']))
                    self.table.setItem(row, 1, QTableWidgetItem(pos['symbol']))
                    self.table.setItem(row, 2, QTableWidgetItem(pos['side']))
                    self.table.setItem(row, 3, QTableWidgetItem(f"{pos['quantity']:.4f}"))
                    self.table.setItem(row, 4, QTableWidgetItem(f"{pos['entry_price']:.5f}"))
                    self.table.setItem(row, 5, QTableWidgetItem(f"{pos['current_price']:.5f}"))
                    
                    # P&L con color
                    pnl_item = QTableWidgetItem(f"${pos['unrealized_pnl']:.2f}")
                    if pos['unrealized_pnl'] > 0:
                        pnl_item.setForeground(QColor(46, 204, 113))
                    else:
                        pnl_item.setForeground(QColor(231, 76, 60))
                    self.table.setItem(row, 6, pnl_item)
                    
                    pnl_pct_item = QTableWidgetItem(f"{pos['unrealized_pnl_percent']:+.2f}%")
                    if pos['unrealized_pnl_percent'] > 0:
                        pnl_pct_item.setForeground(QColor(46, 204, 113))
                    else:
                        pnl_pct_item.setForeground(QColor(231, 76, 60))
                    self.table.setItem(row, 7, pnl_pct_item)
                    
                    # Boton cerrar
                    close_btn = QPushButton("Cerrar")
                    close_btn.clicked.connect(lambda checked, pid=pos['id']: self.close_position(pid))
                    self.table.setCellWidget(row, 8, close_btn)
                    
        except Exception as e:
            pass
    
    def close_position(self, position_id: str):
        """Cierra una posicion"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Cerrar posicion {position_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                response = requests.post(
                    f"{self.api_url}/api/trade/close/{position_id}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    QMessageBox.information(self, "Exito", "Posicion cerrada")
                    self.update_positions()
                else:
                    raise Exception(response.json().get('detail'))
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
