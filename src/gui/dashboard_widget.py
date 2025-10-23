"""
Widget de Dashboard con Metricas
"""

import requests
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class MetricCard(QFrame):
    """Tarjeta para mostrar una metrica"""
    
    def __init__(self, title: str, value: str = "0", color: str = "#3498db"):
        super().__init__()
        
        self.setFrameStyle(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #34495e;
                border-left: 4px solid {color};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Titulo
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #95a5a6; font-size: 11px;")
        layout.addWidget(title_label)
        
        # Valor
        self.value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(18)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_label)
    
    def set_value(self, value: str):
        """Actualiza el valor"""
        self.value_label.setText(value)


class DashboardWidget(QWidget):
    """Widget principal del dashboard"""
    
    def __init__(self):
        super().__init__()
        
        self.api_url = "http://127.0.0.1:8000"
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Titulo
        title = QLabel("📊 DASHBOARD")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ecf0f1; padding: 10px;")
        layout.addWidget(title)
        
        # Seccion: Cuenta
        account_group = QGroupBox("Cuenta")
        account_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ecf0f1; }")
        account_layout = QGridLayout(account_group)
        
        self.balance_card = MetricCard("Balance", "$10,000", "#3498db")
        account_layout.addWidget(self.balance_card, 0, 0)
        
        self.equity_card = MetricCard("Equity", "$10,000", "#2ecc71")
        account_layout.addWidget(self.equity_card, 0, 1)
        
        self.pnl_card = MetricCard("P&L Total", "$0.00", "#95a5a6")
        account_layout.addWidget(self.pnl_card, 1, 0)
        
        self.return_card = MetricCard("Retorno", "0.00%", "#9b59b6")
        account_layout.addWidget(self.return_card, 1, 1)
        
        layout.addWidget(account_group)
        
        # Seccion: Trading
        trading_group = QGroupBox("Trading")
        trading_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ecf0f1; }")
        trading_layout = QGridLayout(trading_group)
        
        self.trades_card = MetricCard("Total Trades", "0", "#e67e22")
        trading_layout.addWidget(self.trades_card, 0, 0)
        
        self.winrate_card = MetricCard("Win Rate", "0%", "#2ecc71")
        trading_layout.addWidget(self.winrate_card, 0, 1)
        
        self.profit_factor_card = MetricCard("Profit Factor", "0.00", "#f39c12")
        trading_layout.addWidget(self.profit_factor_card, 1, 0)
        
        self.sharpe_card = MetricCard("Sharpe Ratio", "0.00", "#1abc9c")
        trading_layout.addWidget(self.sharpe_card, 1, 1)
        
        layout.addWidget(trading_group)
        
        # Seccion: Riesgo
        risk_group = QGroupBox("Riesgo")
        risk_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ecf0f1; }")
        risk_layout = QGridLayout(risk_group)
        
        self.drawdown_card = MetricCard("Max Drawdown", "0.00%", "#e74c3c")
        risk_layout.addWidget(self.drawdown_card, 0, 0)
        
        self.positions_card = MetricCard("Posiciones", "0", "#3498db")
        risk_layout.addWidget(self.positions_card, 0, 1)
        
        layout.addWidget(risk_group)
        
        layout.addStretch()
    
    def update_metrics(self):
        """Actualiza las metricas desde la API"""
        try:
            # Obtener metricas de performance
            response = requests.get(f"{self.api_url}/api/metrics/performance", timeout=2)
            
            if response.status_code == 200:
                metrics = response.json()
                
                # Actualizar tarjetas
                self.equity_card.set_value(f"${metrics.get('current_equity', 0):,.2f}")
                self.pnl_card.set_value(f"${metrics.get('total_pnl', 0):+,.2f}")
                self.return_card.set_value(f"{metrics.get('total_return', 0):+.2f}%")
                self.trades_card.set_value(str(metrics.get('total_trades', 0)))
                self.winrate_card.set_value(f"{metrics.get('win_rate', 0):.1f}%")
                self.profit_factor_card.set_value(f"{metrics.get('profit_factor', 0):.2f}")
                self.sharpe_card.set_value(f"{metrics.get('sharpe_ratio', 0):.2f}")
                self.drawdown_card.set_value(f"{metrics.get('max_drawdown', 0):.2f}%")
                
                # Cambiar color de P&L segun valor
                pnl = metrics.get('total_pnl', 0)
                if pnl > 0:
                    self.pnl_card.value_label.setStyleSheet("color: #2ecc71;")
                elif pnl < 0:
                    self.pnl_card.value_label.setStyleSheet("color: #e74c3c;")
                else:
                    self.pnl_card.value_label.setStyleSheet("color: #95a5a6;")
            
            # Obtener info de cuenta
            response = requests.get(f"{self.api_url}/api/broker/account", timeout=2)
            
            if response.status_code == 200:
                account = response.json()
                self.balance_card.set_value(f"${account.get('balance', 0):,.2f}")
            
            # Obtener posiciones
            response = requests.get(f"{self.api_url}/api/broker/positions", timeout=2)
            
            if response.status_code == 200:
                positions = response.json()
                self.positions_card.set_value(str(len(positions.get('positions', []))))
                
        except Exception as e:
            pass  # Silenciar errores de conexion
