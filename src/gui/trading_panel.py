"""
Panel de Control de Trading
"""

import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QDoubleSpinBox, QGroupBox,
    QMessageBox, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class TradingPanel(QWidget):
    """Panel para ejecutar operaciones manuales"""
    
    def __init__(self, api_url: str):
        super().__init__()
        
        self.api_url = api_url
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Titulo
        title = QLabel("📈 PANEL DE TRADING")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ecf0f1; padding: 10px;")
        layout.addWidget(title)
        
        # Grupo: Nueva Operacion
        trade_group = QGroupBox("Nueva Operacion")
        trade_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ecf0f1; }")
        trade_layout = QVBoxLayout(trade_group)
        
        # Simbolo
        symbol_layout = QHBoxLayout()
        symbol_layout.addWidget(QLabel("Simbolo:"))
        self.symbol_combo = QComboBox()
        self.symbol_combo.addItems([
            "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD",
            "BTC/USDT", "ETH/USDT", "BNB/USDT"
        ])
        symbol_layout.addWidget(self.symbol_combo)
        trade_layout.addLayout(symbol_layout)
        
        # Direccion
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(QLabel("Direccion:"))
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["BUY (Long)", "SELL (Short)"])
        direction_layout.addWidget(self.direction_combo)
        trade_layout.addLayout(direction_layout)
        
        # Cantidad
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Cantidad:"))
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 100.0)
        self.quantity_spin.setValue(0.1)
        self.quantity_spin.setSingleStep(0.01)
        self.quantity_spin.setDecimals(2)
        quantity_layout.addWidget(self.quantity_spin)
        trade_layout.addLayout(quantity_layout)
        
        # Stop Loss
        sl_layout = QHBoxLayout()
        sl_layout.addWidget(QLabel("Stop Loss:"))
        self.sl_spin = QDoubleSpinBox()
        self.sl_spin.setRange(0.0, 100000.0)
        self.sl_spin.setValue(0.0)
        self.sl_spin.setSingleStep(0.0001)
        self.sl_spin.setDecimals(5)
        sl_layout.addWidget(self.sl_spin)
        trade_layout.addLayout(sl_layout)
        
        # Take Profit
        tp_layout = QHBoxLayout()
        tp_layout.addWidget(QLabel("Take Profit:"))
        self.tp_spin = QDoubleSpinBox()
        self.tp_spin.setRange(0.0, 100000.0)
        self.tp_spin.setValue(0.0)
        self.tp_spin.setSingleStep(0.0001)
        self.tp_spin.setDecimals(5)
        tp_layout.addWidget(self.tp_spin)
        trade_layout.addLayout(tp_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.buy_btn = QPushButton("🟢 COMPRAR")
        self.buy_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.buy_btn.clicked.connect(lambda: self.open_trade('buy'))
        buttons_layout.addWidget(self.buy_btn)
        
        self.sell_btn = QPushButton("🔴 VENDER")
        self.sell_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.sell_btn.clicked.connect(lambda: self.open_trade('sell'))
        buttons_layout.addWidget(self.sell_btn)
        
        trade_layout.addLayout(buttons_layout)
        
        layout.addWidget(trade_group)
        
        # Grupo: Precio Actual
        price_group = QGroupBox("Precio Actual")
        price_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ecf0f1; }")
        price_layout = QVBoxLayout(price_group)
        
        self.bid_label = QLabel("Bid: --")
        self.bid_label.setStyleSheet("color: #e74c3c; font-size: 16px; font-weight: bold;")
        price_layout.addWidget(self.bid_label)
        
        self.ask_label = QLabel("Ask: --")
        self.ask_label.setStyleSheet("color: #2ecc71; font-size: 16px; font-weight: bold;")
        price_layout.addWidget(self.ask_label)
        
        self.spread_label = QLabel("Spread: --")
        self.spread_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        price_layout.addWidget(self.spread_label)
        
        refresh_btn = QPushButton("🔄 Actualizar Precio")
        refresh_btn.clicked.connect(self.update_price)
        price_layout.addWidget(refresh_btn)
        
        layout.addWidget(price_group)
        
        layout.addStretch()
    
    def open_trade(self, side: str):
        """Abre una nueva operacion"""
        try:
            symbol = self.symbol_combo.currentText()
            quantity = self.quantity_spin.value()
            sl = self.sl_spin.value() if self.sl_spin.value() > 0 else None
            tp = self.tp_spin.value() if self.tp_spin.value() > 0 else None
            
            # Confirmar
            reply = QMessageBox.question(
                self,
                "Confirmar Operacion",
                f"¿Abrir operacion {side.upper()}?\n\n"
                f"Simbolo: {symbol}\n"
                f"Cantidad: {quantity}\n"
                f"Stop Loss: {sl if sl else 'No'}\n"
                f"Take Profit: {tp if tp else 'No'}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                response = requests.post(
                    f"{self.api_url}/api/trade/open",
                    json={
                        "symbol": symbol,
                        "side": side,
                        "quantity": quantity,
                        "stop_loss": sl,
                        "take_profit": tp
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    QMessageBox.information(
                        self,
                        "Exito",
                        f"Operacion abierta exitosamente\nID: {data.get('order_id')}"
                    )
                else:
                    raise Exception(response.json().get('detail', 'Error desconocido'))
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo operacion: {e}")
    
    def update_price(self):
        """Actualiza el precio actual"""
        try:
            symbol = self.symbol_combo.currentText()
            
            response = requests.get(
                f"{self.api_url}/api/market/price/{symbol}",
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                self.bid_label.setText(f"Bid: {data['bid']:.5f}")
                self.ask_label.setText(f"Ask: {data['ask']:.5f}")
                self.spread_label.setText(f"Spread: {data['spread']:.5f}")
            
        except Exception as e:
            pass
