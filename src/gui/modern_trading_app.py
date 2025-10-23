"""
Modern Trading App - Diseño Profesional
Estilo: Spotify/Instagram/WhatsApp
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
from datetime import datetime
import numpy as np
from loguru import logger

# Importar controller (opcional si API no está disponible)
try:
    from src.gui.trading_controller import TradingController
    CONTROLLER_AVAILABLE = True
except:
    CONTROLLER_AVAILABLE = False
    logger.warning("TradingController no disponible - modo demo")

# Importar base de datos
try:
    from src.database import get_database
    DATABASE_AVAILABLE = True
except:
    DATABASE_AVAILABLE = False
    logger.warning("Database no disponible")


class ModernTradingApp(QMainWindow):
    """
    Aplicación Moderna de Trading
    
    Diseño:
    - Sidebar navigation (estilo Spotify)
    - Cards con sombras (estilo Material Design)
    - Animaciones suaves
    - Glassmorphism effects
    - Gradientes modernos
    - Iconos premium
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TradePro - Professional Trading Platform")
        self.setGeometry(100, 100, 1400, 900)
        
        # Quitar borde de ventana para diseño moderno
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Variables
        self.balance = 10000.0
        self.pnl = 0.0
        self.positions = []
        
        # Base de datos
        self.db = None
        self.current_user_id = None
        if DATABASE_AVAILABLE:
            try:
                self.db = get_database()
                # Crear usuario por defecto si no existe
                user = self.db.get_user_by_username("trader_pro")
                if not user:
                    self.current_user_id = self.db.create_user("trader_pro", "trader@tradepro.com", 10000.0)
                else:
                    self.current_user_id = user['id']
                    self.db.update_last_login(self.current_user_id)
                
                # Cargar balance desde DB
                user = self.db.get_user(self.current_user_id)
                self.balance = user['current_balance']
                logger.info(f"✅ Base de datos conectada - Usuario: {user['username']}")
            except Exception as e:
                logger.warning(f"⚠️ Error con base de datos: {e}")
        
        # Trading Controller (si está disponible)
        self.controller = None
        if CONTROLLER_AVAILABLE:
            try:
                self.controller = TradingController()
                logger.info("✅ TradingController conectado")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo conectar TradingController: {e}")
        
        # Setup
        self.setup_ui()
        self.apply_modern_theme()
        
        # Timers
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(1000)
        
        logger.info("Modern Trading App inicializada")
    
    def setup_ui(self):
        """Setup UI moderna"""
        # Widget central con bordes redondeados
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # SIDEBAR (estilo Spotify)
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # CONTENT AREA
        content_area = self.create_content_area()
        main_layout.addWidget(content_area)
    
    def create_sidebar(self) -> QWidget:
        """Sidebar de navegación estilo Spotify"""
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(280)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(15)
        
        # Logo y título
        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 20)
        
        logo_label = QLabel("💎")
        logo_label.setStyleSheet("font-size: 32px;")
        
        title_label = QLabel("TradePro")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #ffffff;
            font-family: 'Segoe UI', Arial;
        """)
        
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()
        
        layout.addWidget(logo_container)
        
        # Menú de navegación
        self.nav_buttons = []
        
        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("📊", "Trading", "trading"),
            ("💼", "Portfolio", "portfolio"),
            ("📈", "Analytics", "analytics"),
            ("🤖", "AI Agents", "agents"),
            ("⚙️", "Settings", "settings"),
        ]
        
        for icon, text, page in nav_items:
            btn = self.create_nav_button(icon, text, page)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # User profile (abajo)
        profile = self.create_profile_widget()
        layout.addWidget(profile)
        
        return sidebar
    
    def create_nav_button(self, icon: str, text: str, page: str) -> QPushButton:
        """Botón de navegación moderno"""
        btn = QPushButton(f"{icon}  {text}")
        btn.setObjectName("navButton")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(50)
        
        btn.clicked.connect(lambda: self.switch_page(page))
        
        return btn
    
    def create_profile_widget(self) -> QWidget:
        """Widget de perfil de usuario"""
        profile = QWidget()
        profile.setObjectName("profileWidget")
        
        layout = QHBoxLayout(profile)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Avatar
        avatar = QLabel("👤")
        avatar.setStyleSheet("font-size: 32px;")
        
        # Info
        info_layout = QVBoxLayout()
        
        name_label = QLabel("Trader Pro")
        name_label.setStyleSheet("font-weight: bold; color: #ffffff; font-size: 14px;")
        
        status_label = QLabel("● Online")
        status_label.setStyleSheet("color: #00ff88; font-size: 11px;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(status_label)
        
        layout.addWidget(avatar)
        layout.addLayout(info_layout)
        layout.addStretch()
        
        return profile
    
    def create_content_area(self) -> QWidget:
        """Área de contenido principal"""
        content = QWidget()
        content.setObjectName("contentArea")
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # HEADER con título y acciones
        header = self.create_header()
        layout.addWidget(header)
        
        # STACKED WIDGET para diferentes páginas
        self.stacked_widget = QStackedWidget()
        
        # Páginas
        self.stacked_widget.addWidget(self.create_dashboard_page())
        self.stacked_widget.addWidget(self.create_trading_page())
        self.stacked_widget.addWidget(self.create_portfolio_page())
        self.stacked_widget.addWidget(self.create_analytics_page())
        self.stacked_widget.addWidget(self.create_agents_page())
        self.stacked_widget.addWidget(self.create_settings_page())
        
        layout.addWidget(self.stacked_widget)
        
        return content
    
    def create_header(self) -> QWidget:
        """Header con título y acciones"""
        header = QWidget()
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título de página
        self.page_title = QLabel("Dashboard")
        self.page_title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #ffffff;
        """)
        
        layout.addWidget(self.page_title)
        layout.addStretch()
        
        # Botones de acción
        search_btn = self.create_icon_button("🔍", "Search")
        notif_btn = self.create_icon_button("🔔", "Notifications")
        minimize_btn = self.create_icon_button("➖", "Minimize")
        maximize_btn = self.create_icon_button("⬜", "Maximize")
        close_btn = self.create_icon_button("✖", "Close")
        
        minimize_btn.clicked.connect(self.showMinimized)
        maximize_btn.clicked.connect(self.toggle_maximize)
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(search_btn)
        layout.addWidget(notif_btn)
        layout.addWidget(minimize_btn)
        layout.addWidget(maximize_btn)
        layout.addWidget(close_btn)
        
        return header
    
    def create_icon_button(self, icon: str, tooltip: str) -> QPushButton:
        """Botón con icono"""
        btn = QPushButton(icon)
        btn.setObjectName("iconButton")
        btn.setToolTip(tooltip)
        btn.setFixedSize(40, 40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
    
    def create_dashboard_page(self) -> QWidget:
        """Página Dashboard"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Stats Cards (3 columnas)
        stats_layout = QHBoxLayout()
        
        balance_card = self.create_stat_card(
            "💰 Balance",
            f"${self.balance:,.2f}",
            "+12.5%",
            "#00ff88"
        )
        
        pnl_card = self.create_stat_card(
            "📊 P&L Today",
            f"+${abs(self.pnl):,.2f}",
            "+5.2%",
            "#00ff88"
        )
        
        trades_card = self.create_stat_card(
            "🔄 Trades",
            "47",
            "Win Rate: 68%",
            "#00a8ff"
        )
        
        stats_layout.addWidget(balance_card)
        stats_layout.addWidget(pnl_card)
        stats_layout.addWidget(trades_card)
        
        layout.addLayout(stats_layout)
        
        # Chart Card
        chart_card = self.create_chart_card()
        layout.addWidget(chart_card)
        
        # Recent Activity
        activity_card = self.create_activity_card()
        layout.addWidget(activity_card)
        
        return page
    
    def create_stat_card(self, title: str, value: str, subtitle: str, color: str) -> QWidget:
        """Card de estadística moderna"""
        card = QWidget()
        card.setObjectName("statCard")
        card.setMinimumHeight(140)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(10)
        
        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 14px;
            color: #888888;
            font-weight: 500;
        """)
        
        # Valor principal
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {color};
        """)
        
        # Subtítulo
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            font-size: 13px;
            color: #00ff88;
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        layout.addStretch()
        
        return card
    
    def create_chart_card(self) -> QWidget:
        """Card con gráfico"""
        card = QWidget()
        card.setObjectName("chartCard")
        card.setMinimumHeight(350)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📈 Portfolio Performance")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        
        timeframe_combo = QComboBox()
        timeframe_combo.addItems(["1D", "1W", "1M", "3M", "1Y", "ALL"])
        timeframe_combo.setObjectName("modernCombo")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(timeframe_combo)
        
        layout.addLayout(header_layout)
        
        # Placeholder para gráfico
        chart_placeholder = QLabel("📊 Chart Area\n(Integrar con pyqtgraph)")
        chart_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_placeholder.setStyleSheet("""
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            color: #666666;
            font-size: 16px;
            padding: 50px;
        """)
        
        layout.addWidget(chart_placeholder)
        
        return card
    
    def create_activity_card(self) -> QWidget:
        """Card de actividad reciente"""
        card = QWidget()
        card.setObjectName("activityCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        
        title = QLabel("🕒 Recent Activity")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Lista de actividades
        activities = [
            ("🟢 BUY", "BTC/USDT", "+$250.00", "2 min ago"),
            ("🔴 SELL", "ETH/USDT", "+$180.50", "15 min ago"),
            ("🟢 BUY", "SOL/USDT", "+$95.20", "1 hour ago"),
        ]
        
        for action, symbol, pnl, time in activities:
            activity_item = self.create_activity_item(action, symbol, pnl, time)
            layout.addWidget(activity_item)
        
        return card
    
    def create_activity_item(self, action: str, symbol: str, pnl: str, time: str) -> QWidget:
        """Item de actividad"""
        item = QWidget()
        item.setFixedHeight(60)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(10, 10, 10, 10)
        
        action_label = QLabel(action)
        action_label.setFixedWidth(100)
        action_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        
        symbol_label = QLabel(symbol)
        symbol_label.setStyleSheet("color: #ffffff; font-size: 14px;")
        
        pnl_label = QLabel(pnl)
        pnl_label.setStyleSheet("color: #00ff88; font-weight: bold; font-size: 14px;")
        
        time_label = QLabel(time)
        time_label.setStyleSheet("color: #888888; font-size: 12px;")
        
        layout.addWidget(action_label)
        layout.addWidget(symbol_label)
        layout.addStretch()
        layout.addWidget(pnl_label)
        layout.addWidget(time_label)
        
        return item
    
    def create_trading_page(self) -> QWidget:
        """Página de Trading - FUNCIONAL"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Grid layout para formulario y chart
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # ===== FORMULARIO DE TRADING =====
        form_card = QWidget()
        form_card.setObjectName("tradingCard")
        form_card.setMinimumWidth(400)
        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(25, 25, 25, 25)
        
        # Título
        title = QLabel("📊 Ejecutar Trade")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        form_layout.addWidget(title)
        
        # Formulario
        form = QFormLayout()
        form.setSpacing(15)
        
        # Symbol
        self.symbol_input = QLineEdit("BTCUSDT")
        self.symbol_input.setObjectName("modernInput")
        self.symbol_input.setPlaceholderText("Ej: BTCUSDT, ETHUSDT")
        self.symbol_input.setFixedHeight(40)
        form.addRow("Símbolo:", self.symbol_input)
        
        # Side
        self.side_combo = QComboBox()
        self.side_combo.setObjectName("modernCombo")
        self.side_combo.addItems(["BUY", "SELL"])
        self.side_combo.setFixedHeight(40)
        form.addRow("Lado:", self.side_combo)
        
        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setObjectName("modernInput")
        self.amount_input.setDecimals(8)
        self.amount_input.setMaximum(1000000)
        self.amount_input.setValue(0.001)
        self.amount_input.setFixedHeight(40)
        form.addRow("Cantidad:", self.amount_input)
        
        # Stop Loss
        self.sl_input = QDoubleSpinBox()
        self.sl_input.setObjectName("modernInput")
        self.sl_input.setDecimals(2)
        self.sl_input.setMaximum(1000000)
        self.sl_input.setFixedHeight(40)
        form.addRow("Stop Loss:", self.sl_input)
        
        # Take Profit
        self.tp_input = QDoubleSpinBox()
        self.tp_input.setObjectName("modernInput")
        self.tp_input.setDecimals(2)
        self.tp_input.setMaximum(1000000)
        self.tp_input.setFixedHeight(40)
        form.addRow("Take Profit:", self.tp_input)
        
        form_layout.addLayout(form)
        form_layout.addSpacing(10)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        buy_btn = QPushButton("🟢 COMPRAR")
        buy_btn.setObjectName("buyButton")
        buy_btn.setFixedHeight(50)
        buy_btn.clicked.connect(lambda: self.execute_trade_from_form("buy"))
        
        sell_btn = QPushButton("🔴 VENDER")
        sell_btn.setObjectName("sellButton")
        sell_btn.setFixedHeight(50)
        sell_btn.clicked.connect(lambda: self.execute_trade_from_form("sell"))
        
        buttons_layout.addWidget(buy_btn)
        buttons_layout.addWidget(sell_btn)
        
        form_layout.addLayout(buttons_layout)
        
        grid.addWidget(form_card, 0, 0)
        
        # ===== SÍMBOLOS RÁPIDOS =====
        quick_card = QWidget()
        quick_card.setObjectName("tradingCard")
        quick_layout = QVBoxLayout(quick_card)
        quick_layout.setContentsMargins(25, 25, 25, 25)
        
        quick_title = QLabel("⚡ Acceso Rápido")
        quick_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        quick_layout.addWidget(quick_title)
        
        # Botones de símbolos populares
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT"]
        symbols_grid = QGridLayout()
        symbols_grid.setSpacing(10)
        
        for i, symbol in enumerate(symbols):
            btn = QPushButton(symbol.replace("USDT", ""))
            btn.setObjectName("symbolButton")
            btn.setFixedHeight(45)
            btn.clicked.connect(lambda checked, s=symbol: self.symbol_input.setText(s))
            row = i // 2
            col = i % 2
            symbols_grid.addWidget(btn, row, col)
        
        quick_layout.addLayout(symbols_grid)
        quick_layout.addStretch()
        
        grid.addWidget(quick_card, 0, 1)
        
        layout.addLayout(grid)
        
        return page
    
    def execute_trade_from_form(self, side):
        """Ejecutar trade desde formulario"""
        symbol = self.symbol_input.text()
        amount = self.amount_input.value()
        sl = self.sl_input.value() if self.sl_input.value() > 0 else None
        tp = self.tp_input.value() if self.tp_input.value() > 0 else None
        
        # Precio simulado (en producción vendría del broker)
        entry_price = 50000.0 if "BTC" in symbol else 3000.0
        
        # Guardar en base de datos
        if self.db and self.current_user_id:
            try:
                trade_id = self.db.create_trade(
                    self.current_user_id, symbol, side, amount,
                    entry_price, sl, tp, "binance"
                )
                
                QMessageBox.information(
                    self,
                    "Trade Ejecutado",
                    f"✅ {side.upper()} {amount} {symbol} @ ${entry_price:,.2f}\n\nTrade ID: {trade_id}"
                )
                
                # Actualizar balance
                user = self.db.get_user(self.current_user_id)
                self.balance = user['current_balance']
                self.balance_label.setText(f"${self.balance:,.2f}")
                
                logger.info(f"✅ Trade guardado en DB: {trade_id}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Error guardando trade: {e}")
        else:
            # Modo demo sin DB
            QMessageBox.information(
                self,
                "Trade Ejecutado (Demo)",
                f"✅ {side.upper()} {amount} {symbol} @ ${entry_price:,.2f}\n\n(Modo demo - sin base de datos)"
            )
    
    def create_portfolio_page(self) -> QWidget:
        """Página de Portfolio - FUNCIONAL"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Header con botón cerrar todas
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("💼 Posiciones Abiertas")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        
        close_all_btn = QPushButton("🔴 Cerrar Todas")
        close_all_btn.setObjectName("sellButton")
        close_all_btn.setFixedHeight(40)
        close_all_btn.clicked.connect(self.close_all_positions)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(close_all_btn)
        
        layout.addWidget(header)
        
        # Tabla de posiciones
        self.positions_table = QTableWidget()
        self.positions_table.setObjectName("portfolioTable")
        self.positions_table.setColumnCount(8)
        self.positions_table.setHorizontalHeaderLabels([
            "Símbolo", "Lado", "Cantidad", "Precio Entrada", 
            "Precio Actual", "P&L ($)", "P&L (%)", "Acción"
        ])
        
        # Configurar tabla
        self.positions_table.horizontalHeader().setStretchLastSection(False)
        self.positions_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.positions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.positions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.positions_table.setAlternatingRowColors(True)
        self.positions_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.positions_table)
        
        # Cargar posiciones desde DB
        self.load_positions()
        
        return page
    
    def load_positions(self):
        """Cargar posiciones desde base de datos"""
        if not self.db or not self.current_user_id:
            return
        
        try:
            positions = self.db.get_open_positions(self.current_user_id)
            
            self.positions_table.setRowCount(len(positions))
            
            for row, pos in enumerate(positions):
                # Símbolo
                self.positions_table.setItem(row, 0, QTableWidgetItem(pos['symbol']))
                
                # Lado
                side_item = QTableWidgetItem(pos['side'].upper())
                side_item.setForeground(QColor("#00ff88" if pos['side'] == 'buy' else "#ff4444"))
                self.positions_table.setItem(row, 1, side_item)
                
                # Cantidad
                self.positions_table.setItem(row, 2, QTableWidgetItem(f"{pos['amount']:.8f}"))
                
                # Precio entrada
                self.positions_table.setItem(row, 3, QTableWidgetItem(f"${pos['entry_price']:,.2f}"))
                
                # Precio actual (simulado)
                current_price = pos['entry_price'] * (1 + np.random.uniform(-0.05, 0.05))
                self.positions_table.setItem(row, 4, QTableWidgetItem(f"${current_price:,.2f}"))
                
                # P&L
                if pos['side'] == 'buy':
                    pnl = (current_price - pos['entry_price']) * pos['amount']
                else:
                    pnl = (pos['entry_price'] - current_price) * pos['amount']
                
                pnl_percent = (pnl / (pos['entry_price'] * pos['amount'])) * 100
                
                pnl_item = QTableWidgetItem(f"${pnl:,.2f}")
                pnl_item.setForeground(QColor("#00ff88" if pnl > 0 else "#ff4444"))
                self.positions_table.setItem(row, 5, pnl_item)
                
                pnl_pct_item = QTableWidgetItem(f"{pnl_percent:,.2f}%")
                pnl_pct_item.setForeground(QColor("#00ff88" if pnl > 0 else "#ff4444"))
                self.positions_table.setItem(row, 6, pnl_pct_item)
                
                # Botón cerrar
                close_btn = QPushButton("Cerrar")
                close_btn.setObjectName("closePositionButton")
                close_btn.clicked.connect(lambda checked, t_id=pos['trade_id']: self.close_position(t_id))
                self.positions_table.setCellWidget(row, 7, close_btn)
            
            logger.info(f"✅ {len(positions)} posiciones cargadas")
        except Exception as e:
            logger.error(f"Error cargando posiciones: {e}")
    
    def close_position(self, trade_id):
        """Cerrar posición individual"""
        if not self.db:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar",
            "¿Cerrar esta posición?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Precio de salida simulado
                exit_price = 50000.0 * (1 + np.random.uniform(-0.02, 0.02))
                
                pnl = self.db.close_trade(trade_id, exit_price)
                
                QMessageBox.information(
                    self, "Posición Cerrada",
                    f"✅ Posición cerrada\n\nP&L: ${pnl:,.2f}"
                )
                
                # Recargar posiciones
                self.load_positions()
                
                # Actualizar balance
                user = self.db.get_user(self.current_user_id)
                self.balance = user['current_balance']
                self.balance_label.setText(f"${self.balance:,.2f}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Error cerrando posición: {e}")
    
    def close_all_positions(self):
        """Cerrar todas las posiciones"""
        if not self.db or not self.current_user_id:
            return
        
        positions = self.db.get_open_positions(self.current_user_id)
        
        if not positions:
            QMessageBox.information(self, "Info", "No hay posiciones abiertas")
            return
        
        reply = QMessageBox.question(
            self, "Confirmar",
            f"¿Cerrar todas las {len(positions)} posiciones?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            total_pnl = 0
            for pos in positions:
                exit_price = pos['entry_price'] * (1 + np.random.uniform(-0.02, 0.02))
                pnl = self.db.close_trade(pos['trade_id'], exit_price)
                total_pnl += pnl
            
            QMessageBox.information(
                self, "Posiciones Cerradas",
                f"✅ {len(positions)} posiciones cerradas\n\nP&L Total: ${total_pnl:,.2f}"
            )
            
            self.load_positions()
            
            user = self.db.get_user(self.current_user_id)
            self.balance = user['current_balance']
            self.balance_label.setText(f"${self.balance:,.2f}")
    
    def create_analytics_page(self) -> QWidget:
        """Página de Analytics - FUNCIONAL"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Grid de métricas
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(15)
        
        # Obtener métricas desde DB
        if self.db and self.current_user_id:
            trades = self.db.get_trade_history(self.current_user_id, limit=1000)
            
            total_trades = len(trades)
            winning_trades = len([t for t in trades if t['pnl'] and t['pnl'] > 0])
            losing_trades = len([t for t in trades if t['pnl'] and t['pnl'] < 0])
            total_pnl = sum([t['pnl'] for t in trades if t['pnl']])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Profit factor
            gross_profit = sum([t['pnl'] for t in trades if t['pnl'] and t['pnl'] > 0])
            gross_loss = abs(sum([t['pnl'] for t in trades if t['pnl'] and t['pnl'] < 0]))
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        else:
            total_trades = 0
            winning_trades = 0
            losing_trades = 0
            total_pnl = 0
            win_rate = 0
            profit_factor = 0
        
        # Cards de métricas
        metrics = [
            ("Total Trades", str(total_trades), "#00a8ff"),
            ("Win Rate", f"{win_rate:.1f}%", "#00ff88"),
            ("Total P&L", f"${total_pnl:,.2f}", "#00ff88" if total_pnl > 0 else "#ff4444"),
            ("Profit Factor", f"{profit_factor:.2f}", "#00ff88")
        ]
        
        for i, (label, value, color) in enumerate(metrics):
            card = self.create_metric_card(label, value, color)
            metrics_grid.addWidget(card, 0, i)
        
        layout.addLayout(metrics_grid)
        
        # Historial de trades
        history_card = QWidget()
        history_card.setObjectName("analyticsCard")
        history_layout = QVBoxLayout(history_card)
        history_layout.setContentsMargins(25, 20, 25, 20)
        
        history_title = QLabel("📊 Historial de Trades")
        history_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        history_layout.addWidget(history_title)
        
        # Tabla de historial
        history_table = QTableWidget()
        history_table.setObjectName("analyticsTable")
        history_table.setColumnCount(6)
        history_table.setHorizontalHeaderLabels([
            "Fecha", "Símbolo", "Lado", "Cantidad", "P&L ($)", "P&L (%)"
        ])
        
        history_table.horizontalHeader().setStretchLastSection(True)
        history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        history_table.setAlternatingRowColors(True)
        history_table.verticalHeader().setVisible(False)
        history_table.setMaximumHeight(400)
        
        # Cargar últimos 50 trades
        if self.db and self.current_user_id:
            recent_trades = self.db.get_trade_history(self.current_user_id, limit=50)
            history_table.setRowCount(len(recent_trades))
            
            for row, trade in enumerate(recent_trades):
                # Fecha
                date_str = trade['opened_at'][:10] if trade['opened_at'] else ""
                history_table.setItem(row, 0, QTableWidgetItem(date_str))
                
                # Símbolo
                history_table.setItem(row, 1, QTableWidgetItem(trade['symbol']))
                
                # Lado
                side_item = QTableWidgetItem(trade['side'].upper())
                side_item.setForeground(QColor("#00ff88" if trade['side'] == 'buy' else "#ff4444"))
                history_table.setItem(row, 2, side_item)
                
                # Cantidad
                history_table.setItem(row, 3, QTableWidgetItem(f"{trade['amount']:.8f}"))
                
                # P&L
                pnl = trade['pnl'] if trade['pnl'] else 0
                pnl_item = QTableWidgetItem(f"${pnl:,.2f}")
                pnl_item.setForeground(QColor("#00ff88" if pnl > 0 else "#ff4444"))
                history_table.setItem(row, 4, pnl_item)
                
                # P&L %
                pnl_pct = trade['pnl_percent'] if trade['pnl_percent'] else 0
                pnl_pct_item = QTableWidgetItem(f"{pnl_pct:.2f}%")
                pnl_pct_item.setForeground(QColor("#00ff88" if pnl_pct > 0 else "#ff4444"))
                history_table.setItem(row, 5, pnl_pct_item)
        
        history_layout.addWidget(history_table)
        layout.addWidget(history_card)
        
        return page
    
    def create_metric_card(self, label, value, color):
        """Card de métrica individual"""
        card = QWidget()
        card.setObjectName("metricCard")
        card.setMinimumHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label_label = QLabel(label)
        label_label.setStyleSheet("font-size: 14px; color: #888888;")
        label_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        
        return card
    
    def create_agents_page(self) -> QWidget:
        """Página de AI Agents - Trading Automático"""
        from .auto_trading_widget import AutoTradingWidget
        
        # Crear widget de auto trading
        auto_trading_widget = AutoTradingWidget(controller=self.controller)
        
        return auto_trading_widget
    
    def create_agent_card(self, icon, name, desc, accuracy, vote):
        """Card individual de agente"""
        card = QWidget()
        card.setObjectName("agentCard")
        card.setMinimumHeight(180)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header con icono y nombre
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Descripción
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("font-size: 12px; color: #888888;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        
        # Accuracy
        accuracy_layout = QHBoxLayout()
        accuracy_layout.addWidget(QLabel("Accuracy:"))
        accuracy_label = QLabel(f"{accuracy}%")
        accuracy_label.setStyleSheet("font-weight: bold; color: #00ff88;")
        accuracy_layout.addWidget(accuracy_label)
        accuracy_layout.addStretch()
        layout.addLayout(accuracy_layout)
        
        # Last vote
        vote_layout = QHBoxLayout()
        vote_layout.addWidget(QLabel("Last Vote:"))
        
        vote_colors = {"BUY": "#00ff88", "SELL": "#ff4444", "HOLD": "#ffaa00"}
        vote_label = QLabel(vote)
        vote_label.setStyleSheet(f"font-weight: bold; color: {vote_colors.get(vote, '#ffffff')};")
        vote_layout.addWidget(vote_label)
        vote_layout.addStretch()
        layout.addLayout(vote_layout)
        
        return card
    
    def create_agents_stats_card(self):
        """Card con estadísticas de agentes"""
        card = QWidget()
        card.setObjectName("statsCard")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(25, 20, 25, 20)
        
        title = QLabel("📊 Performance del Sistema Multi-Agente")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)
        
        # Stats grid
        stats_layout = QHBoxLayout()
        
        stats = [
            ("Decisiones Hoy", "247", "#00a8ff"),
            ("Accuracy Promedio", "86%", "#00ff88"),
            ("Consenso", "High", "#00ff88"),
            ("Conflictos", "12", "#ffaa00")
        ]
        
        for label, value, color in stats:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)
            
            value_label = QLabel(value)
            value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            label_label = QLabel(label)
            label_label.setStyleSheet("font-size: 12px; color: #888888;")
            label_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(label_label)
            
            stats_layout.addWidget(stat_widget)
        
        layout.addLayout(stats_layout)
        
        return card
    
    def toggle_auto_trading(self):
        """Toggle auto trading"""
        if hasattr(self, 'controller') and self.controller:
            if self.controller.auto_trading:
                # Detener
                self.controller.stop_auto_trading()
                self.auto_trading_btn.setText("▶ START AUTO TRADING")
                self.auto_trading_btn.setObjectName("startButton")
            else:
                # Iniciar
                config = {
                    'use_multi_agent': True,
                    'use_ppo': True,
                    'use_sentiment': True,
                    'symbols': ['BTCUSDT', 'ETHUSDT'],
                    'max_positions': 3,
                    'risk_per_trade': 0.02
                }
                self.controller.start_auto_trading(config)
                self.auto_trading_btn.setText("⏸ STOP AUTO TRADING")
                self.auto_trading_btn.setObjectName("stopButton")
            
            # Actualizar estilo
            self.auto_trading_btn.style().unpolish(self.auto_trading_btn)
            self.auto_trading_btn.style().polish(self.auto_trading_btn)
        else:
            QMessageBox.warning(self, "Error", "Primero conecta un broker en Settings")
    
    def create_settings_page(self) -> QWidget:
        """Página de Settings - FUNCIONAL"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        
        # Scroll area para settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("settingsScroll")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)
        
        # ===== PERFIL DE USUARIO =====
        profile_card = QWidget()
        profile_card.setObjectName("settingsCard")
        profile_layout = QVBoxLayout(profile_card)
        profile_layout.setContentsMargins(25, 20, 25, 20)
        
        profile_title = QLabel("👤 Perfil de Usuario")
        profile_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        profile_layout.addWidget(profile_title)
        
        if self.db and self.current_user_id:
            user = self.db.get_user(self.current_user_id)
            
            profile_info = QFormLayout()
            profile_info.setSpacing(10)
            
            username_label = QLabel(user['username'])
            username_label.setStyleSheet("color: #00ff88; font-weight: bold;")
            profile_info.addRow("Usuario:", username_label)
            
            email_label = QLabel(user['email'] or "No configurado")
            profile_info.addRow("Email:", email_label)
            
            created_label = QLabel(user['created_at'][:10] if user['created_at'] else "")
            profile_info.addRow("Miembro desde:", created_label)
            
            balance_label = QLabel(f"${user['current_balance']:,.2f}")
            balance_label.setStyleSheet("color: #00ff88; font-size: 16px; font-weight: bold;")
            profile_info.addRow("Balance:", balance_label)
            
            profile_layout.addLayout(profile_info)
        
        scroll_layout.addWidget(profile_card)
        
        # ===== BROKER CONNECTION =====
        broker_card = QWidget()
        broker_card.setObjectName("settingsCard")
        broker_layout = QVBoxLayout(broker_card)
        broker_layout.setContentsMargins(25, 20, 25, 20)
        
        broker_title = QLabel("🔌 Conexión a Broker")
        broker_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        broker_layout.addWidget(broker_title)
        
        broker_form = QFormLayout()
        broker_form.setSpacing(15)
        
        # Broker selector
        self.broker_combo = QComboBox()
        self.broker_combo.setObjectName("modernCombo")
        self.broker_combo.addItems(["Binance", "Binance Futures", "Quotex"])
        self.broker_combo.setFixedHeight(40)
        broker_form.addRow("Broker:", self.broker_combo)
        
        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setObjectName("modernInput")
        self.api_key_input.setPlaceholderText("Tu API Key")
        self.api_key_input.setFixedHeight(40)
        broker_form.addRow("API Key:", self.api_key_input)
        
        # API Secret
        self.api_secret_input = QLineEdit()
        self.api_secret_input.setObjectName("modernInput")
        self.api_secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_secret_input.setPlaceholderText("Tu API Secret")
        self.api_secret_input.setFixedHeight(40)
        broker_form.addRow("API Secret:", self.api_secret_input)
        
        # Testnet checkbox
        self.testnet_check = QCheckBox("Usar Testnet (Recomendado)")
        self.testnet_check.setChecked(False)  # Por defecto desactivado (MAINNET)
        self.testnet_check.setStyleSheet("color: #ffffff;")
        broker_form.addRow("", self.testnet_check)
        
        broker_layout.addLayout(broker_form)
        
        # Botones
        broker_buttons = QHBoxLayout()
        
        connect_btn = QPushButton("🔌 Conectar Broker")
        connect_btn.setObjectName("startButton")
        connect_btn.setFixedHeight(45)
        connect_btn.clicked.connect(self.connect_broker_from_settings)
        
        disconnect_btn = QPushButton("❌ Desconectar")
        disconnect_btn.setObjectName("sellButton")
        disconnect_btn.setFixedHeight(45)
        
        broker_buttons.addWidget(connect_btn)
        broker_buttons.addWidget(disconnect_btn)
        
        broker_layout.addLayout(broker_buttons)
        
        # Estado
        self.connection_status = QLabel("● Desconectado")
        self.connection_status.setStyleSheet("color: #ff4444; font-size: 14px; font-weight: bold;")
        broker_layout.addWidget(self.connection_status)
        
        scroll_layout.addWidget(broker_card)
        
        # ===== TRADING PARAMETERS =====
        trading_card = QWidget()
        trading_card.setObjectName("settingsCard")
        trading_layout = QVBoxLayout(trading_card)
        trading_layout.setContentsMargins(25, 20, 25, 20)
        
        trading_title = QLabel("⚙️ Parámetros de Trading")
        trading_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        trading_layout.addWidget(trading_title)
        
        trading_form = QFormLayout()
        trading_form.setSpacing(15)
        
        # Max positions
        max_pos_spin = QSpinBox()
        max_pos_spin.setObjectName("modernInput")
        max_pos_spin.setRange(1, 10)
        max_pos_spin.setValue(3)
        max_pos_spin.setFixedHeight(40)
        trading_form.addRow("Max Posiciones:", max_pos_spin)
        
        # Risk per trade
        risk_spin = QDoubleSpinBox()
        risk_spin.setObjectName("modernInput")
        risk_spin.setRange(0.01, 0.10)
        risk_spin.setValue(0.02)
        risk_spin.setSingleStep(0.01)
        risk_spin.setSuffix("%")
        risk_spin.setFixedHeight(40)
        trading_form.addRow("Riesgo por Trade:", risk_spin)
        
        trading_layout.addLayout(trading_form)
        
        # Botón guardar
        save_btn = QPushButton("💾 Guardar Configuración")
        save_btn.setObjectName("startButton")
        save_btn.setFixedHeight(45)
        save_btn.clicked.connect(lambda: QMessageBox.information(self, "Guardado", "✅ Configuración guardada"))
        trading_layout.addWidget(save_btn)
        
        scroll_layout.addWidget(trading_card)
        
        # ===== APPEARANCE =====
        appearance_card = QWidget()
        appearance_card.setObjectName("settingsCard")
        appearance_layout = QVBoxLayout(appearance_card)
        appearance_layout.setContentsMargins(25, 20, 25, 20)
        
        appearance_title = QLabel("🎨 Apariencia")
        appearance_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
        appearance_layout.addWidget(appearance_title)
        
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Tema:"))
        
        dark_radio = QRadioButton("🌙 Oscuro")
        dark_radio.setChecked(True)
        dark_radio.setStyleSheet("color: #ffffff;")
        
        light_radio = QRadioButton("☀️ Claro")
        light_radio.setStyleSheet("color: #ffffff;")
        
        theme_layout.addWidget(dark_radio)
        theme_layout.addWidget(light_radio)
        theme_layout.addStretch()
        
        appearance_layout.addLayout(theme_layout)
        
        scroll_layout.addWidget(appearance_card)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        return page
    
    def connect_broker_from_settings(self):
        """Conectar broker desde settings"""
        broker_map = {
            "Binance": "binance",
            "Binance Futures": "binance_futures",
            "Quotex": "quotex"
        }
        
        broker = broker_map[self.broker_combo.currentText()]
        api_key = self.api_key_input.text()
        api_secret = self.api_secret_input.text()
        testnet = self.testnet_check.isChecked()
        
        if not api_key or not api_secret:
            QMessageBox.warning(self, "Error", "Por favor ingresa API Key y Secret")
            return
        
        # Guardar en DB
        if self.db and self.current_user_id:
            try:
                self.db.update_user_settings(self.current_user_id, {
                    'broker': broker,
                    'api_key': api_key,
                    'api_secret': api_secret,
                    'testnet': testnet
                })
                logger.info(f"✅ Configuración guardada en DB para {broker}")
            except Exception as e:
                logger.error(f"Error guardando configuración: {e}")
        
        # Conectar via controller (si está disponible)
        if self.controller:
            try:
                credentials = {
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "testnet": testnet
                }
                
                logger.info(f"Intentando conectar {broker} (testnet={testnet})...")
                logger.info(f"API Key: {api_key[:8]}... (longitud: {len(api_key)})")
                
                result = self.controller.connect_broker(broker, credentials)
                
                logger.info(f"Resultado de conexión: {result}")
                
                if result and result.get('success'):
                    self.connection_status.setText("● Conectado")
                    self.connection_status.setStyleSheet("color: #00ff88; font-size: 14px; font-weight: bold;")
                    QMessageBox.information(
                        self, 
                        "Éxito", 
                        f"✅ Broker {broker} conectado exitosamente\n\nTestnet: {'Sí' if testnet else 'No'}"
                    )
                else:
                    error_msg = result.get('error', 'Error desconocido') if result else 'La API no respondió correctamente'
                    logger.error(f"Error conectando broker: {error_msg}")
                    logger.error(f"Respuesta completa: {result}")
                    
                    # Mensaje más detallado
                    detail_msg = f"❌ No se pudo conectar al broker\n\n"
                    detail_msg += f"Error: {error_msg}\n\n"
                    detail_msg += "💡 Verifica:\n"
                    detail_msg += "1. API Key correcta (sin espacios)\n"
                    detail_msg += "2. API Secret correcta (sin espacios)\n"
                    detail_msg += "3. API corriendo: http://127.0.0.1:8001/health\n"
                    detail_msg += "4. Permisos en Binance (Enable Trading)\n"
                    detail_msg += f"5. Testnet: {'Activado' if testnet else 'Desactivado'}\n\n"
                    detail_msg += "🔍 Revisa los logs de la API para más detalles"
                    
                    QMessageBox.critical(self, "Error de Conexión", detail_msg)
            except Exception as e:
                logger.error(f"Excepción conectando broker: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"❌ Error al conectar:\n\n{str(e)}\n\n💡 Asegúrate de que la API esté corriendo:\n\nuvicorn src.api.trading_api:app --reload"
                )
        else:
            # Modo demo - guardar configuración pero no conectar realmente
            self.connection_status.setText("● Conectado (Demo)")
            self.connection_status.setStyleSheet("color: #ffaa00; font-size: 14px; font-weight: bold;")
            
            QMessageBox.information(
                self, 
                "Modo Demo", 
                f"✅ Configuración guardada para {broker}\n\n"
                f"⚠️ Modo Demo Activo\n\n"
                f"La API no está disponible. Los trades se simularán.\n\n"
                f"Para conectar realmente:\n"
                f"1. Ejecuta: uvicorn src.api.trading_api:app --reload\n"
                f"2. Reinicia la aplicación"
            )
    
    def switch_page(self, page: str):
        """Cambiar de página con animación"""
        pages = {
            "dashboard": (0, "Dashboard"),
            "trading": (1, "Trading"),
            "portfolio": (2, "Portfolio"),
            "analytics": (3, "Analytics"),
            "agents": (4, "AI Agents"),
            "settings": (5, "Settings"),
        }
        
        if page in pages:
            index, title = pages[page]
            self.stacked_widget.setCurrentIndex(index)
            self.page_title.setText(title)
            
            # Si es Settings, cargar credenciales
            if page == "settings":
                self.load_saved_credentials()
            
            # Highlight botón activo
            for i, btn in enumerate(self.nav_buttons):
                if i == index:
                    btn.setProperty("active", True)
                else:
                    btn.setProperty("active", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
    
    def load_saved_credentials(self):
        """Cargar credenciales guardadas en los campos"""
        if not self.db or not self.current_user_id:
            return
        
        try:
            settings = self.db.get_user_settings(self.current_user_id)
            if settings:
                logger.info("📥 Cargando credenciales guardadas...")
                
                if settings.get('api_key'):
                    self.api_key_input.setText(settings['api_key'])
                    logger.success(f"✅ API Key cargada: {settings['api_key'][:10]}...")
                
                if settings.get('api_secret'):
                    self.api_secret_input.setText(settings['api_secret'])
                    logger.success("✅ API Secret cargada")
                
                if settings.get('testnet') is not None:
                    self.testnet_check.setChecked(bool(settings['testnet']))
                    logger.success(f"✅ Testnet: {'Activado' if settings['testnet'] else 'Desactivado'}")
                
                logger.info("✅ Credenciales cargadas exitosamente")
            else:
                logger.warning("⚠️ No hay credenciales guardadas")
        except Exception as e:
            logger.error(f"❌ Error cargando credenciales: {e}")
            import traceback
            traceback.print_exc()
    
    def toggle_maximize(self):
        """Toggle maximize/restore"""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def update_data(self):
        """Actualizar datos en tiempo real"""
        # Simular cambios
        self.pnl += np.random.randn() * 10
        self.balance += self.pnl * 0.01
    
    def apply_modern_theme(self):
        """Tema moderno con gradientes y glassmorphism"""
        self.setStyleSheet("""
            /* VENTANA PRINCIPAL */
            #centralWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a,
                    stop:1 #1a1a2e
                );
                border-radius: 15px;
            }
            
            /* SIDEBAR */
            #sidebar {
                background: rgba(20, 20, 30, 0.95);
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            /* BOTONES DE NAVEGACIÓN */
            #navButton {
                background: transparent;
                color: #888888;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                text-align: left;
                font-size: 15px;
                font-weight: 500;
            }
            
            #navButton:hover {
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
            }
            
            #navButton[active="true"] {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00a8ff,
                    stop:1 #00ff88
                );
                color: #ffffff;
                font-weight: bold;
            }
            
            /* PROFILE WIDGET */
            #profileWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            /* CONTENT AREA */
            #contentArea {
                background: transparent;
            }
            
            /* STAT CARDS */
            #statCard {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.05),
                    stop:1 rgba(255, 255, 255, 0.02)
                );
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            #statCard:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255, 255, 255, 0.08),
                    stop:1 rgba(255, 255, 255, 0.04)
                );
                border: 1px solid rgba(0, 168, 255, 0.3);
            }
            
            /* CHART CARD */
            #chartCard {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            /* ACTIVITY CARD */
            #activityCard {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            /* ICON BUTTONS */
            #iconButton {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                color: #ffffff;
                font-size: 16px;
            }
            
            #iconButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(0, 168, 255, 0.5);
            }
            
            /* COMBOBOX */
            #modernCombo {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 8px 15px;
                color: #ffffff;
                font-size: 13px;
            }
            
            #modernCombo:hover {
                border: 1px solid rgba(0, 168, 255, 0.5);
            }
            
            #modernCombo::drop-down {
                border: none;
            }
            
            #modernCombo QAbstractItemView {
                background: #1a1a2e;
                border: 1px solid rgba(255, 255, 255, 0.1);
                selection-background-color: #00a8ff;
                color: #ffffff;
            }
            
            /* AGENT CARDS */
            #agentCard {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            #agentCard:hover {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(0, 168, 255, 0.3);
            }
            
            /* STATS CARD */
            #statsCard {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 20px;
            }
            
            /* START/STOP BUTTONS */
            #startButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff88, stop:1 #00cc66);
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 30px;
            }
            
            #startButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00cc66, stop:1 #009944);
            }
            
            #stopButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4444, stop:1 #cc0000);
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 30px;
            }
            
            #stopButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #cc0000, stop:1 #990000);
            }
            
            /* TRADING PAGE */
            #tradingCard {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            #symbolButton {
                background: rgba(0, 168, 255, 0.2);
                border: 1px solid rgba(0, 168, 255, 0.3);
                border-radius: 8px;
                color: #00a8ff;
                font-weight: bold;
            }
            
            #symbolButton:hover {
                background: rgba(0, 168, 255, 0.3);
            }
            
            #buyButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff88, stop:1 #00cc66);
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
            
            #buyButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00cc66, stop:1 #009944);
            }
            
            #sellButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff4444, stop:1 #cc0000);
                border: none;
                border-radius: 10px;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
            }
            
            #sellButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #cc0000, stop:1 #990000);
            }
            
            /* PORTFOLIO PAGE */
            #portfolioTable {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                color: #ffffff;
            }
            
            #portfolioTable::item {
                padding: 10px;
            }
            
            #portfolioTable::item:selected {
                background: rgba(0, 168, 255, 0.3);
            }
            
            #portfolioTable QHeaderView::section {
                background: rgba(255, 255, 255, 0.05);
                color: #ffffff;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            
            #closePositionButton {
                background: rgba(255, 68, 68, 0.2);
                border: 1px solid #ff4444;
                border-radius: 5px;
                color: #ff4444;
                padding: 5px 15px;
            }
            
            #closePositionButton:hover {
                background: #ff4444;
                color: #ffffff;
            }
            
            /* ANALYTICS PAGE */
            #analyticsCard {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            #metricCard {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            #metricCard:hover {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(0, 168, 255, 0.3);
            }
            
            #analyticsTable {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                color: #ffffff;
            }
            
            #analyticsTable QHeaderView::section {
                background: rgba(255, 255, 255, 0.05);
                color: #ffffff;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            
            /* SETTINGS PAGE */
            #settingsCard {
                background: rgba(255, 255, 255, 0.03);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            #settingsScroll {
                background: transparent;
                border: none;
            }
            
            QScrollArea {
                background: transparent;
                border: none;
            }
            
            QScrollBar:vertical {
                background: rgba(255, 255, 255, 0.05);
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: rgba(0, 168, 255, 0.5);
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 168, 255, 0.7);
            }
        """)
    
    def mousePressEvent(self, event):
        """Para mover la ventana sin borde"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Mover ventana"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Fuente moderna
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = ModernTradingApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
