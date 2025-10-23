"""Dialogo de Configuracion"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget,
    QFormLayout, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QHBoxLayout, QMessageBox
)

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Configuracion")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        tabs = QTabWidget()
        
        # Tab Trading
        trading_tab = QWidget()
        trading_layout = QFormLayout(trading_tab)
        
        self.max_risk_spin = QDoubleSpinBox()
        self.max_risk_spin.setRange(0.01, 0.10)
        self.max_risk_spin.setValue(0.02)
        self.max_risk_spin.setSingleStep(0.01)
        self.max_risk_spin.setSuffix(" %")
        trading_layout.addRow("Riesgo Maximo por Trade:", self.max_risk_spin)
        
        self.max_positions_spin = QSpinBox()
        self.max_positions_spin.setRange(1, 10)
        self.max_positions_spin.setValue(3)
        trading_layout.addRow("Posiciones Maximas:", self.max_positions_spin)
        
        self.auto_trading_check = QCheckBox()
        trading_layout.addRow("Trading Automatico:", self.auto_trading_check)
        
        tabs.addTab(trading_tab, "Trading")
        
        # Tab IA
        ia_tab = QWidget()
        ia_layout = QFormLayout(ia_tab)
        
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.5, 1.0)
        self.confidence_spin.setValue(0.65)
        self.confidence_spin.setSingleStep(0.05)
        ia_layout.addRow("Umbral de Confianza:", self.confidence_spin)
        
        self.retrain_check = QCheckBox()
        self.retrain_check.setChecked(True)
        ia_layout.addRow("Re-entrenamiento Automatico:", self.retrain_check)
        
        tabs.addTab(ia_tab, "Inteligencia Artificial")
        
        layout.addWidget(tabs)
        
        # Botones
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def save_settings(self):
        QMessageBox.information(self, "Exito", "Configuracion guardada")
        self.accept()
