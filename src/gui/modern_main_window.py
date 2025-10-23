"""
Modern Main Window - Interfaz Moderna con Ventana Nativa
Diseño profesional, ancla a barra de tareas, notificaciones
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
from pathlib import Path


class ModernMainWindow(QMainWindow):
    """
    Ventana principal moderna con:
    - Diseño profesional
    - Barra de título personalizada
    - Sistema de pestañas
    - Notificaciones
    - Ancla a barra de tareas
    """
    
    def __init__(self, api_url: str = "http://127.0.0.1:8000"):
        super().__init__()
        self.api_url = api_url
        
        # Configuración de ventana
        self.setWindowTitle("Trading System Pro")
        self.setMinimumSize(1400, 900)
        
        # Icono de la aplicación
        self.setup_app_icon()
        
        # Estilo moderno
        self.setup_modern_style()
        
        # UI
        self.init_ui()
        
        # Centrar ventana
        self.center_window()
        
        # Configurar barra de tareas
        self.setup_taskbar()
    
    def setup_app_icon(self):
        """Configurar icono de la aplicación"""
        # Crear icono si no existe
        icon_path = Path("assets/icon.png")
        
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        else:
            # Crear icono por defecto
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("#1e88e5"))
            
            painter = QPainter(pixmap)
            painter.setPen(QPen(QColor("white"), 2))
            painter.setFont(QFont("Arial", 32, QFont.Weight.Bold))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "T")
            painter.end()
            
            self.setWindowIcon(QIcon(pixmap))
    
    def setup_modern_style(self):
        """Aplicar estilo moderno"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0e27;
            }
            
            /* Barra de título personalizada */
            QMenuBar {
                background-color: #151932;
                color: white;
                border-bottom: 2px solid #1e88e5;
                padding: 8px;
                font-size: 13px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 16px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #1e88e5;
            }
            
            QMenu {
                background-color: #151932;
                color: white;
                border: 1px solid #1e88e5;
                border-radius: 8px;
                padding: 8px;
            }
            
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #1e88e5;
            }
            
            /* Toolbar */
            QToolBar {
                background-color: #151932;
                border: none;
                padding: 8px;
                spacing: 8px;
            }
            
            QToolButton {
                background-color: #1e88e5;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            
            QToolButton:hover {
                background-color: #1976d2;
            }
            
            QToolButton:pressed {
                background-color: #1565c0;
            }
            
            QToolButton:disabled {
                background-color: #37474f;
                color: #78909c;
            }
            
            /* Tabs */
            QTabWidget::pane {
                border: 1px solid #1e88e5;
                border-radius: 8px;
                background-color: #0f1429;
                padding: 8px;
            }
            
            QTabBar::tab {
                background-color: #151932;
                color: #78909c;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 12px 24px;
                margin-right: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            
            QTabBar::tab:selected {
                background-color: #1e88e5;
                color: white;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #1a237e;
                color: white;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #151932;
                color: white;
                border-top: 2px solid #1e88e5;
                padding: 8px;
                font-size: 12px;
            }
            
            /* Scroll Bars */
            QScrollBar:vertical {
                background-color: #151932;
                width: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #1e88e5;
                border-radius: 6px;
                min-height: 30px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #1976d2;
            }
            
            QScrollBar:horizontal {
                background-color: #151932;
                height: 12px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #1e88e5;
                border-radius: 6px;
                min-width: 30px;
            }
            
            /* Tooltips */
            QToolTip {
                background-color: #151932;
                color: white;
                border: 1px solid #1e88e5;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
    
    def init_ui(self):
        """Inicializar interfaz"""
        
        # Menu Bar
        self.create_menu_bar()
        
        # Toolbar
        self.create_toolbar()
        
        # Central Widget con Tabs
        self.create_central_widget()
        
        # Status Bar
        self.create_status_bar()
        
        # System Tray
        self.create_system_tray()
    
    def create_menu_bar(self):
        """Crear barra de menú"""
        menubar = self.menuBar()
        
        # Archivo
        file_menu = menubar.addMenu("📁 Archivo")
        
        new_action = QAction("🆕 Nuevo Sistema", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("📂 Abrir Configuración", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("💾 Guardar", self)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Trading
        trading_menu = menubar.addMenu("📊 Trading")
        
        start_action = QAction("▶ Iniciar Sistema", self)
        start_action.setShortcut("F5")
        trading_menu.addAction(start_action)
        
        stop_action = QAction("⏹ Detener Sistema", self)
        stop_action.setShortcut("F6")
        trading_menu.addAction(stop_action)
        
        trading_menu.addSeparator()
        
        connect_action = QAction("🔌 Conectar Broker", self)
        connect_action.setShortcut("Ctrl+B")
        trading_menu.addAction(connect_action)
        
        # Análisis
        analysis_menu = menubar.addMenu("📈 Análisis")
        
        backtest_action = QAction("🔄 Backtesting", self)
        analysis_menu.addAction(backtest_action)
        
        optimize_action = QAction("⚙ Optimización", self)
        analysis_menu.addAction(optimize_action)
        
        # Herramientas
        tools_menu = menubar.addMenu("🛠 Herramientas")
        
        settings_action = QAction("⚙ Configuración", self)
        settings_action.setShortcut("Ctrl+,")
        tools_menu.addAction(settings_action)
        
        logs_action = QAction("📋 Ver Logs", self)
        tools_menu.addAction(logs_action)
        
        # Ayuda
        help_menu = menubar.addMenu("❓ Ayuda")
        
        docs_action = QAction("📚 Documentación", self)
        docs_action.setShortcut("F1")
        help_menu.addAction(docs_action)
        
        about_action = QAction("ℹ Acerca de", self)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Crear toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        
        # Botones principales
        start_btn = QToolButton()
        start_btn.setText("▶ Iniciar")
        start_btn.setToolTip("Iniciar sistema de trading (F5)")
        toolbar.addWidget(start_btn)
        
        stop_btn = QToolButton()
        stop_btn.setText("⏹ Detener")
        stop_btn.setToolTip("Detener sistema (F6)")
        stop_btn.setEnabled(False)
        toolbar.addWidget(stop_btn)
        
        toolbar.addSeparator()
        
        connect_btn = QToolButton()
        connect_btn.setText("🔌 Conectar Broker")
        connect_btn.setToolTip("Conectar con broker (Ctrl+B)")
        toolbar.addWidget(connect_btn)
        
        toolbar.addSeparator()
        
        config_btn = QToolButton()
        config_btn.setText("⚙ Configuración")
        config_btn.setToolTip("Configuración del sistema")
        toolbar.addWidget(config_btn)
        
        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Status
        self.status_label = QLabel("● Sistema Detenido")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #f44336;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 16px;
                background-color: #1a1a2e;
                border-radius: 6px;
            }
        """)
        toolbar.addWidget(self.status_label)
        
        # Broker status
        self.broker_label = QLabel("Broker: No conectado")
        self.broker_label.setStyleSheet("""
            QLabel {
                color: #78909c;
                font-size: 13px;
                padding: 8px 16px;
                background-color: #1a1a2e;
                border-radius: 6px;
                margin-left: 8px;
            }
        """)
        toolbar.addWidget(self.broker_label)
    
    def create_central_widget(self):
        """Crear widget central con tabs"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Tab 1: Dashboard
        dashboard_tab = self.create_dashboard_tab()
        tabs.addTab(dashboard_tab, "📊 Dashboard")
        
        # Tab 2: Trading
        trading_tab = self.create_trading_tab()
        tabs.addTab(trading_tab, "💹 Trading")
        
        # Tab 3: Análisis
        analysis_tab = self.create_analysis_tab()
        tabs.addTab(analysis_tab, "📈 Análisis")
        
        # Tab 4: Posiciones
        positions_tab = self.create_positions_tab()
        tabs.addTab(positions_tab, "📋 Posiciones")
        
        # Tab 5: Historial
        history_tab = self.create_history_tab()
        tabs.addTab(history_tab, "📜 Historial")
        
        # Tab 6: Configuración
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "⚙ Configuración")
        
        layout.addWidget(tabs)
    
    def create_dashboard_tab(self) -> QWidget:
        """Tab de Dashboard"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Aquí irá el dashboard actual
        label = QLabel("Dashboard - Métricas en tiempo real")
        label.setStyleSheet("color: white; font-size: 16px; padding: 20px;")
        layout.addWidget(label)
        
        return widget
    
    def create_trading_tab(self) -> QWidget:
        """Tab de Trading"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Panel de Trading - Ejecutar operaciones")
        label.setStyleSheet("color: white; font-size: 16px; padding: 20px;")
        layout.addWidget(label)
        
        return widget
    
    def create_analysis_tab(self) -> QWidget:
        """Tab de Análisis"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Análisis Técnico - Gráficos e indicadores")
        label.setStyleSheet("color: white; font-size: 16px; padding: 20px;")
        layout.addWidget(label)
        
        return widget
    
    def create_positions_tab(self) -> QWidget:
        """Tab de Posiciones"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Posiciones Abiertas - Gestión de trades")
        label.setStyleSheet("color: white; font-size: 16px; padding: 20px;")
        layout.addWidget(label)
        
        return widget
    
    def create_history_tab(self) -> QWidget:
        """Tab de Historial"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Historial de Trades - Performance histórica")
        label.setStyleSheet("color: white; font-size: 16px; padding: 20px;")
        layout.addWidget(label)
        
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Tab de Configuración"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Configuración del Sistema")
        label.setStyleSheet("color: white; font-size: 16px; padding: 20px;")
        layout.addWidget(label)
        
        return widget
    
    def create_status_bar(self):
        """Crear barra de estado"""
        statusbar = self.statusBar()
        
        # Información de conexión
        self.conn_status = QLabel("🔴 Desconectado")
        statusbar.addWidget(self.conn_status)
        
        statusbar.addWidget(QLabel("|"))
        
        # Balance
        self.balance_label = QLabel("Balance: $0.00")
        statusbar.addWidget(self.balance_label)
        
        statusbar.addWidget(QLabel("|"))
        
        # P&L
        self.pnl_label = QLabel("P&L: $0.00")
        statusbar.addWidget(self.pnl_label)
        
        statusbar.addWidget(QLabel("|"))
        
        # Win Rate
        self.winrate_label = QLabel("Win Rate: 0%")
        statusbar.addWidget(self.winrate_label)
        
        # Spacer
        statusbar.addPermanentWidget(QLabel(""))
        
        # Versión
        version_label = QLabel("v2.0.0")
        version_label.setStyleSheet("color: #78909c;")
        statusbar.addPermanentWidget(version_label)
    
    def create_system_tray(self):
        """Crear icono en system tray"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        
        # Menú del tray
        tray_menu = QMenu()
        
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Ocultar", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Salir", self)
        quit_action.triggered.connect(QApplication.quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Doble click para mostrar
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """Manejar click en tray icon"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()
    
    def setup_taskbar(self):
        """Configurar para barra de tareas de Windows"""
        try:
            # Windows: Configurar AppUserModelID para agrupar en taskbar
            import ctypes
            myappid = 'tradingsystem.pro.v2.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except:
            pass
    
    def center_window(self):
        """Centrar ventana en pantalla"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def closeEvent(self, event):
        """Manejar cierre de ventana"""
        reply = QMessageBox.question(
            self,
            'Confirmar Salida',
            '¿Estás seguro de que quieres salir?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Minimizar a tray en lugar de cerrar
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "Trading System Pro",
                "La aplicación sigue ejecutándose en segundo plano",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            event.ignore()
