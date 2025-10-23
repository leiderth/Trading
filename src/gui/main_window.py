"""
Ventana Principal de la Aplicacion de Trading
"""

import asyncio
import json
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QToolBar, QPushButton,
    QLabel, QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QAction, QIcon, QFont
import requests

from .dashboard_widget import DashboardWidget
from .trading_panel import TradingPanel
from .chart_widget import ChartWidget
from .broker_config_dialog import BrokerConfigDialog
from .settings_dialog import SettingsDialog
from ..config.settings import settings


class APIWorker(QThread):
    """Worker thread para comunicacion con API"""
    
    status_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_url: str):
        super().__init__()
        self.api_url = api_url
        self.running = True
    
    def run(self):
        """Loop principal del worker"""
        while self.running:
            try:
                # Obtener estado del sistema
                response = requests.get(f"{self.api_url}/api/system/status", timeout=2)
                if response.status_code == 200:
                    data = response.json()
                    self.status_updated.emit(data)
            except Exception as e:
                self.error_occurred.emit(str(e))
            
            # Esperar 1 segundo
            self.msleep(1000)
    
    def stop(self):
        """Detener worker"""
        self.running = False


class MainWindow(QMainWindow):
    """Ventana principal de la aplicacion"""
    
    def __init__(self):
        super().__init__()
        
        self.api_url = "http://127.0.0.1:8000"
        self.api_worker: Optional[APIWorker] = None
        self.system_running = False
        
        self.init_ui()
        self.start_api_worker()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        
        # Configuracion de ventana
        self.setWindowTitle("Trading System Pro - AI Algorithmic Trading")
        self.setGeometry(100, 100, 1600, 900)
        
        # Crear menu bar
        self.create_menu_bar()
        
        # Crear toolbar
        self.create_toolbar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Header con informacion del sistema
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Splitter principal (vertical)
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Splitter superior (horizontal)
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Dashboard
        self.dashboard = DashboardWidget()
        top_splitter.addWidget(self.dashboard)
        
        # Panel central: Grafico
        self.chart = ChartWidget()
        top_splitter.addWidget(self.chart)
        
        # Panel derecho: Trading Panel
        self.trading_panel = TradingPanel(self.api_url)
        top_splitter.addWidget(self.trading_panel)
        
        # Proporciones del splitter superior
        top_splitter.setSizes([400, 800, 400])
        
        main_splitter.addWidget(top_splitter)
        
        # Tabs inferiores
        bottom_tabs = QTabWidget()
        
        # Tab de posiciones
        from .positions_widget import PositionsWidget
        self.positions_widget = PositionsWidget(self.api_url)
        bottom_tabs.addTab(self.positions_widget, "Posiciones Abiertas")
        
        # Tab de historial
        from .history_widget import HistoryWidget
        self.history_widget = HistoryWidget(self.api_url)
        bottom_tabs.addTab(self.history_widget, "Historial de Trades")
        
        # Tab de logs
        from .logs_widget import LogsWidget
        self.logs_widget = LogsWidget()
        bottom_tabs.addTab(self.logs_widget, "Logs del Sistema")
        
        main_splitter.addWidget(bottom_tabs)
        
        # Proporciones del splitter principal
        main_splitter.setSizes([600, 300])
        
        main_layout.addWidget(main_splitter)
        
        # Status bar
        self.create_status_bar()
        
        # Timer para actualizaciones
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(2000)  # Actualizar cada 2 segundos
    
    def create_menu_bar(self):
        """Crea la barra de menu"""
        menubar = self.menuBar()
        
        # Menu Sistema
        system_menu = menubar.addMenu("Sistema")
        
        start_action = QAction("Iniciar Sistema", self)
        start_action.triggered.connect(self.start_system)
        system_menu.addAction(start_action)
        
        stop_action = QAction("Detener Sistema", self)
        stop_action.triggered.connect(self.stop_system)
        system_menu.addAction(stop_action)
        
        system_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        system_menu.addAction(exit_action)
        
        # Menu Broker
        broker_menu = menubar.addMenu("Broker")
        
        connect_broker_action = QAction("Conectar Broker", self)
        connect_broker_action.triggered.connect(self.show_broker_config)
        broker_menu.addAction(connect_broker_action)
        
        # Menu Configuracion
        config_menu = menubar.addMenu("Configuracion")
        
        settings_action = QAction("Preferencias", self)
        settings_action.triggered.connect(self.show_settings)
        config_menu.addAction(settings_action)
        
        # Menu Ayuda
        help_menu = menubar.addMenu("Ayuda")
        
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Crea la barra de herramientas"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Boton Start
        self.start_btn = QPushButton("▶ Iniciar")
        self.start_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 8px 16px;")
        self.start_btn.clicked.connect(self.start_system)
        toolbar.addWidget(self.start_btn)
        
        # Boton Stop
        self.stop_btn = QPushButton("⏸ Detener")
        self.stop_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 8px 16px;")
        self.stop_btn.clicked.connect(self.stop_system)
        self.stop_btn.setEnabled(False)
        toolbar.addWidget(self.stop_btn)
        
        toolbar.addSeparator()
        
        # Boton Conectar Broker
        connect_btn = QPushButton("🔌 Conectar Broker")
        connect_btn.clicked.connect(self.show_broker_config)
        toolbar.addWidget(connect_btn)
        
        toolbar.addSeparator()
        
        # Boton Configuracion
        settings_btn = QPushButton("⚙ Configuracion")
        settings_btn.clicked.connect(self.show_settings)
        toolbar.addWidget(settings_btn)
    
    def create_header(self) -> QWidget:
        """Crea el header con informacion del sistema"""
        header = QWidget()
        header.setStyleSheet("background-color: #2c3e50; padding: 10px; border-radius: 5px;")
        
        layout = QHBoxLayout(header)
        
        # Titulo
        title = QLabel("🚀 TRADING SYSTEM PRO")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("color: #ecf0f1;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Estado del sistema
        self.status_label = QLabel("● Sistema Detenido")
        self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Broker conectado
        self.broker_label = QLabel("Broker: No conectado")
        self.broker_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        layout.addWidget(self.broker_label)
        
        return header
    
    def create_status_bar(self):
        """Crea la barra de estado"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        self.statusBar.showMessage("Listo")
    
    def start_api_worker(self):
        """Inicia el worker de API"""
        self.api_worker = APIWorker(self.api_url)
        self.api_worker.status_updated.connect(self.on_status_updated)
        self.api_worker.error_occurred.connect(self.on_api_error)
        self.api_worker.start()
    
    def on_status_updated(self, status: dict):
        """Callback cuando se actualiza el estado"""
        if status.get('is_running'):
            self.status_label.setText("● Sistema Ejecutando")
            self.status_label.setStyleSheet("color: #2ecc71; font-size: 14px; font-weight: bold;")
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.system_running = True
        else:
            self.status_label.setText("● Sistema Detenido")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px; font-weight: bold;")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.system_running = False
    
    def on_api_error(self, error: str):
        """Callback cuando hay error en API"""
        # Solo mostrar si es un error critico
        pass
    
    def update_data(self):
        """Actualiza datos de la interfaz"""
        if self.system_running:
            # Actualizar dashboard
            self.dashboard.update_metrics()
            
            # Actualizar posiciones
            self.positions_widget.update_positions()
            
            # Actualizar grafico
            self.chart.update_chart()
    
    def start_system(self):
        """Inicia el sistema de trading"""
        try:
            # Primero inicializar
            response = requests.post(
                f"{self.api_url}/api/system/initialize",
                json={
                    "symbol": "EUR/USD",
                    "timeframe": "5m",
                    "auto_trading": False,
                    "max_risk": 0.02,
                    "max_positions": 3
                },
                timeout=10
            )
            
            if response.status_code == 200:
                # Luego iniciar
                response = requests.post(f"{self.api_url}/api/system/start", timeout=5)
                
                if response.status_code == 200:
                    self.statusBar.showMessage("Sistema iniciado correctamente")
                    QMessageBox.information(self, "Exito", "Sistema de trading iniciado")
                else:
                    raise Exception(response.json().get('detail', 'Error desconocido'))
            else:
                raise Exception(response.json().get('detail', 'Error inicializando'))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error iniciando sistema: {e}")
            self.statusBar.showMessage(f"Error: {e}")
    
    def stop_system(self):
        """Detiene el sistema de trading"""
        try:
            response = requests.post(f"{self.api_url}/api/system/stop", timeout=5)
            
            if response.status_code == 200:
                self.statusBar.showMessage("Sistema detenido")
                QMessageBox.information(self, "Exito", "Sistema detenido correctamente")
            else:
                raise Exception(response.json().get('detail', 'Error desconocido'))
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error deteniendo sistema: {e}")
    
    def show_broker_config(self):
        """Muestra dialogo de configuracion de broker"""
        dialog = BrokerConfigDialog(self.api_url, self)
        if dialog.exec():
            self.statusBar.showMessage("Broker conectado")
            self.broker_label.setText(f"Broker: {dialog.selected_broker}")
    
    def show_settings(self):
        """Muestra dialogo de configuracion"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_about(self):
        """Muestra dialogo Acerca de"""
        QMessageBox.about(
            self,
            "Acerca de Trading System Pro",
            "<h2>Trading System Pro</h2>"
            "<p>Sistema de Trading Algoritmico con Inteligencia Artificial</p>"
            "<p><b>Version:</b> 1.0.0</p>"
            "<p><b>Caracteristicas:</b></p>"
            "<ul>"
            "<li>Prediccion con LSTM</li>"
            "<li>Agente RL (PPO)</li>"
            "<li>60+ Indicadores Tecnicos</li>"
            "<li>Gestion de Riesgo Profesional</li>"
            "<li>Soporte Multi-Broker</li>"
            "</ul>"
            "<p><b>Desarrollado con:</b> Python, PyQt6, PyTorch, TensorFlow</p>"
        )
    
    def closeEvent(self, event):
        """Evento al cerrar la ventana"""
        reply = QMessageBox.question(
            self,
            "Confirmar Salida",
            "¿Estas seguro de que quieres salir?\n\nSi el sistema esta ejecutando, se detendra.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Detener API worker
            if self.api_worker:
                self.api_worker.stop()
                self.api_worker.wait()
            
            # Detener sistema si esta ejecutando
            if self.system_running:
                try:
                    requests.post(f"{self.api_url}/api/system/stop", timeout=2)
                except:
                    pass
            
            event.accept()
        else:
            event.ignore()
