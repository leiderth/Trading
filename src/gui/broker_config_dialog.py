"""Dialogo de Configuracion de Broker"""

import requests
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QCheckBox,
    QGroupBox, QFormLayout, QMessageBox
)

class BrokerConfigDialog(QDialog):
    def __init__(self, api_url: str, parent=None):
        super().__init__(parent)
        self.api_url = api_url
        self.selected_broker = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Configurar Broker")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Seleccion de broker
        broker_layout = QHBoxLayout()
        broker_layout.addWidget(QLabel("Broker:"))
        self.broker_combo = QComboBox()
        self.broker_combo.addItems(["Quotex (Simulacion)", "Binance (Crypto)"])
        self.broker_combo.currentIndexChanged.connect(self.on_broker_changed)
        broker_layout.addWidget(self.broker_combo)
        layout.addLayout(broker_layout)
        
        # Grupo Quotex
        self.quotex_group = QGroupBox("Configuracion Quotex")
        quotex_layout = QFormLayout(self.quotex_group)
        self.quotex_email = QLineEdit()
        self.quotex_password = QLineEdit()
        self.quotex_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.quotex_demo = QCheckBox("Modo Demo")
        self.quotex_demo.setChecked(True)
        quotex_layout.addRow("Email:", self.quotex_email)
        quotex_layout.addRow("Password:", self.quotex_password)
        quotex_layout.addRow("", self.quotex_demo)
        layout.addWidget(self.quotex_group)
        
        # Grupo Binance
        self.binance_group = QGroupBox("Configuracion Binance")
        binance_layout = QFormLayout(self.binance_group)
        self.binance_api_key = QLineEdit()
        self.binance_api_secret = QLineEdit()
        self.binance_api_secret.setEchoMode(QLineEdit.EchoMode.Password)
        self.binance_testnet = QCheckBox("Usar Testnet")
        self.binance_testnet.setChecked(True)
        binance_layout.addRow("API Key:", self.binance_api_key)
        binance_layout.addRow("API Secret:", self.binance_api_secret)
        binance_layout.addRow("", self.binance_testnet)
        layout.addWidget(self.binance_group)
        self.binance_group.hide()
        
        
        # Botones
        buttons_layout = QHBoxLayout()
        connect_btn = QPushButton("Conectar")
        connect_btn.clicked.connect(self.connect_broker)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(connect_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def on_broker_changed(self, index):
        # Ocultar todos
        self.quotex_group.hide()
        self.binance_group.hide()
        
        # Mostrar el seleccionado
        if index == 0:  # Quotex
            self.quotex_group.show()
        elif index == 1:  # Binance
            self.binance_group.show()
    
    def connect_broker(self):
        try:
            broker_index = self.broker_combo.currentIndex()
            
            if broker_index == 0:  # Quotex
                broker_type = "quotex"
                credentials = {
                    "email": self.quotex_email.text(),
                    "password": self.quotex_password.text(),
                    "demo_mode": self.quotex_demo.isChecked(),
                    "initial_balance": 10000
                }
                self.selected_broker = "Quotex"
            elif broker_index == 1:  # Binance
                broker_type = "binance"
                credentials = {
                    "api_key": self.binance_api_key.text(),
                    "api_secret": self.binance_api_secret.text(),
                    "testnet": self.binance_testnet.isChecked(),
                    "demo_mode": self.binance_testnet.isChecked()
                }
                self.selected_broker = "Binance"
            else:
                QMessageBox.warning(self, "Advertencia", "Broker no soportado")
                return
            
            response = requests.post(
                f"{self.api_url}/api/broker/connect",
                json={
                    "broker_type": broker_type,
                    "credentials": credentials,
                    "demo_mode": credentials.get("demo_mode", True)
                },
                timeout=10
            )
            
            if response.status_code == 200:
                QMessageBox.information(self, "Exito", f"Conectado a {self.selected_broker}")
                self.accept()
            else:
                raise Exception(response.json().get('detail', 'Error desconocido'))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error conectando: {e}")
