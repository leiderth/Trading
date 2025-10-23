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
        """Página de Trading"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        label = QLabel("🚀 Trading Page - En construcción")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #888888;")
        
        layout.addWidget(label)
        
        return page
    
    def create_portfolio_page(self) -> QWidget:
        """Página de Portfolio"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        label = QLabel("💼 Portfolio Page - En construcción")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #888888;")
        
        layout.addWidget(label)
        
        return page
    
    def create_analytics_page(self) -> QWidget:
        """Página de Analytics"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        label = QLabel("📈 Analytics Page - En construcción")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #888888;")
        
        layout.addWidget(label)
        
        return page
    
    def create_agents_page(self) -> QWidget:
        """Página de AI Agents"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        label = QLabel("🤖 AI Agents Page - En construcción")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #888888;")
        
        layout.addWidget(label)
        
        return page
    
    def create_settings_page(self) -> QWidget:
        """Página de Settings"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        label = QLabel("⚙️ Settings Page - En construcción")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; color: #888888;")
        
        layout.addWidget(label)
        
        return page
    
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
            
            # Highlight botón activo
            for i, btn in enumerate(self.nav_buttons):
                if i == index:
                    btn.setProperty("active", True)
                else:
                    btn.setProperty("active", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)
    
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
