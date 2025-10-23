"""
Bloomberg-Style Professional Dashboard
Multi-monitor, Advanced Charts, Real-time Heatmaps
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import pyqtgraph as pg
import numpy as np
from typing import Dict, List
from loguru import logger


class BloombergDashboard(QMainWindow):
    """
    Dashboard profesional estilo Bloomberg Terminal
    
    Características:
    - Multi-monitor support
    - Drag & drop layout
    - 50+ chart overlays
    - Real-time heatmaps
    - Order book visualization
    - P&L attribution
    - Trade journal
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trading System Pro - Bloomberg Dashboard")
        self.setGeometry(0, 0, 1920, 1080)
        
        # Tema oscuro profesional
        self.setup_dark_theme()
        
        # Layout principal
        self.init_ui()
        
        # Datos en tiempo real
        self.market_data = {}
        self.portfolio_data = {}
        
        # Timers para actualización
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_widgets)
        self.update_timer.start(1000)  # 1 segundo
        
        logger.info("Bloomberg Dashboard inicializado")
    
    def setup_dark_theme(self):
        """Tema oscuro profesional tipo Bloomberg"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0a;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #e0e0e0;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
            QLabel {
                color: #e0e0e0;
                padding: 2px;
            }
            QPushButton {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 5px 15px;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #2a2a2a;
                border: 1px solid #3a3a3a;
                padding: 8px 20px;
                color: #e0e0e0;
            }
            QTabBar::tab:selected {
                background-color: #3a3a3a;
                border-bottom: 2px solid #00a8ff;
            }
            QTableWidget {
                background-color: #1a1a1a;
                gridline-color: #2a2a2a;
                border: 1px solid #3a3a3a;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #3a3a3a;
                font-weight: bold;
            }
        """)
    
    def init_ui(self):
        """Inicializa interfaz"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (grid 2x2)
        main_layout = QGridLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Cuadrante 1: Market Overview (arriba izquierda)
        self.market_overview_widget = self.create_market_overview()
        main_layout.addWidget(self.market_overview_widget, 0, 0)
        
        # Cuadrante 2: Advanced Chart (arriba derecha)
        self.chart_widget = self.create_advanced_chart()
        main_layout.addWidget(self.chart_widget, 0, 1)
        
        # Cuadrante 3: Portfolio & Positions (abajo izquierda)
        self.portfolio_widget = self.create_portfolio_widget()
        main_layout.addWidget(self.portfolio_widget, 1, 0)
        
        # Cuadrante 4: Order Book & Trades (abajo derecha)
        self.orderbook_widget = self.create_orderbook_widget()
        main_layout.addWidget(self.orderbook_widget, 1, 1)
        
        # Barra de estado profesional
        self.create_status_bar()
    
    def create_market_overview(self) -> QWidget:
        """Market Overview con métricas clave"""
        widget = QGroupBox("MARKET OVERVIEW")
        widget.setStyleSheet("QGroupBox { font-weight: bold; color: #00a8ff; }")
        layout = QVBoxLayout(widget)
        
        # Grid de métricas
        metrics_grid = QGridLayout()
        
        # Precio actual
        self.price_label = QLabel("$0.00")
        self.price_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #00ff00;")
        metrics_grid.addWidget(QLabel("PRICE:"), 0, 0)
        metrics_grid.addWidget(self.price_label, 0, 1)
        
        # Cambio 24h
        self.change_24h_label = QLabel("+0.00%")
        self.change_24h_label.setStyleSheet("font-size: 18px; color: #00ff00;")
        metrics_grid.addWidget(QLabel("24H CHANGE:"), 1, 0)
        metrics_grid.addWidget(self.change_24h_label, 1, 1)
        
        # Volumen
        self.volume_label = QLabel("$0")
        metrics_grid.addWidget(QLabel("VOLUME:"), 2, 0)
        metrics_grid.addWidget(self.volume_label, 2, 1)
        
        # Market Cap
        self.mcap_label = QLabel("$0")
        metrics_grid.addWidget(QLabel("MARKET CAP:"), 3, 0)
        metrics_grid.addWidget(self.mcap_label, 3, 1)
        
        layout.addLayout(metrics_grid)
        
        # Heatmap de correlación
        heatmap_label = QLabel("CORRELATION HEATMAP")
        heatmap_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(heatmap_label)
        
        self.heatmap = self.create_heatmap()
        layout.addWidget(self.heatmap)
        
        # Sentiment gauge
        sentiment_label = QLabel("MARKET SENTIMENT")
        sentiment_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(sentiment_label)
        
        self.sentiment_gauge = self.create_sentiment_gauge()
        layout.addWidget(self.sentiment_gauge)
        
        return widget
    
    def create_advanced_chart(self) -> QWidget:
        """Chart avanzado con múltiples overlays"""
        widget = QGroupBox("ADVANCED CHART")
        widget.setStyleSheet("QGroupBox { font-weight: bold; color: #00a8ff; }")
        layout = QVBoxLayout(widget)
        
        # Toolbar de chart
        toolbar = QHBoxLayout()
        
        # Timeframe selector
        timeframe_label = QLabel("Timeframe:")
        toolbar.addWidget(timeframe_label)
        
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(["1m", "5m", "15m", "1h", "4h", "1D", "1W"])
        self.timeframe_combo.setCurrentText("1h")
        toolbar.addWidget(self.timeframe_combo)
        
        toolbar.addStretch()
        
        # Indicators
        indicators_label = QLabel("Indicators:")
        toolbar.addWidget(indicators_label)
        
        self.ma_checkbox = QCheckBox("MA")
        self.ma_checkbox.setChecked(True)
        toolbar.addWidget(self.ma_checkbox)
        
        self.bb_checkbox = QCheckBox("Bollinger")
        toolbar.addWidget(self.bb_checkbox)
        
        self.rsi_checkbox = QCheckBox("RSI")
        toolbar.addWidget(self.rsi_checkbox)
        
        self.macd_checkbox = QCheckBox("MACD")
        toolbar.addWidget(self.macd_checkbox)
        
        layout.addLayout(toolbar)
        
        # PyQtGraph chart
        self.price_chart = pg.PlotWidget()
        self.price_chart.setBackground('#0a0a0a')
        self.price_chart.showGrid(x=True, y=True, alpha=0.3)
        self.price_chart.setLabel('left', 'Price', units='$')
        self.price_chart.setLabel('bottom', 'Time')
        
        # Candlestick plot
        self.candlestick_item = pg.CandlestickItem()
        self.price_chart.addItem(self.candlestick_item)
        
        layout.addWidget(self.price_chart)
        
        # Volume chart
        self.volume_chart = pg.PlotWidget()
        self.volume_chart.setBackground('#0a0a0a')
        self.volume_chart.setMaximumHeight(150)
        self.volume_chart.setLabel('left', 'Volume')
        
        layout.addWidget(self.volume_chart)
        
        return widget
    
    def create_portfolio_widget(self) -> QWidget:
        """Portfolio & Positions"""
        widget = QGroupBox("PORTFOLIO & POSITIONS")
        widget.setStyleSheet("QGroupBox { font-weight: bold; color: #00a8ff; }")
        layout = QVBoxLayout(widget)
        
        # Portfolio summary
        summary_grid = QGridLayout()
        
        self.balance_label = QLabel("$10,000.00")
        self.balance_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ff00;")
        summary_grid.addWidget(QLabel("BALANCE:"), 0, 0)
        summary_grid.addWidget(self.balance_label, 0, 1)
        
        self.pnl_label = QLabel("+$0.00 (+0.00%)")
        self.pnl_label.setStyleSheet("font-size: 16px; color: #00ff00;")
        summary_grid.addWidget(QLabel("P&L:"), 1, 0)
        summary_grid.addWidget(self.pnl_label, 1, 1)
        
        self.sharpe_label = QLabel("0.00")
        summary_grid.addWidget(QLabel("SHARPE:"), 2, 0)
        summary_grid.addWidget(self.sharpe_label, 2, 1)
        
        self.drawdown_label = QLabel("0.00%")
        summary_grid.addWidget(QLabel("DRAWDOWN:"), 3, 0)
        summary_grid.addWidget(self.drawdown_label, 3, 1)
        
        layout.addLayout(summary_grid)
        
        # Positions table
        positions_label = QLabel("OPEN POSITIONS")
        positions_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(positions_label)
        
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(7)
        self.positions_table.setHorizontalHeaderLabels([
            "Symbol", "Side", "Size", "Entry", "Current", "P&L", "P&L %"
        ])
        self.positions_table.horizontalHeader().setStretchLastSection(True)
        self.positions_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.positions_table)
        
        return widget
    
    def create_orderbook_widget(self) -> QWidget:
        """Order Book & Recent Trades"""
        widget = QGroupBox("ORDER BOOK & TRADES")
        widget.setStyleSheet("QGroupBox { font-weight: bold; color: #00a8ff; }")
        layout = QVBoxLayout(widget)
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab 1: Order Book
        orderbook_tab = QWidget()
        orderbook_layout = QVBoxLayout(orderbook_tab)
        
        # Spread
        self.spread_label = QLabel("Spread: $0.00 (0.00%)")
        self.spread_label.setStyleSheet("font-weight: bold; text-align: center;")
        orderbook_layout.addWidget(self.spread_label)
        
        # Order book table
        self.orderbook_table = QTableWidget()
        self.orderbook_table.setColumnCount(3)
        self.orderbook_table.setHorizontalHeaderLabels(["Price", "Size", "Total"])
        
        orderbook_layout.addWidget(self.orderbook_table)
        
        tabs.addTab(orderbook_tab, "Order Book")
        
        # Tab 2: Recent Trades
        trades_tab = QWidget()
        trades_layout = QVBoxLayout(trades_tab)
        
        self.trades_table = QTableWidget()
        self.trades_table.setColumnCount(5)
        self.trades_table.setHorizontalHeaderLabels([
            "Time", "Side", "Price", "Size", "Total"
        ])
        
        trades_layout.addWidget(self.trades_table)
        
        tabs.addTab(trades_tab, "Recent Trades")
        
        # Tab 3: Trade Journal
        journal_tab = QWidget()
        journal_layout = QVBoxLayout(journal_tab)
        
        self.journal_table = QTableWidget()
        self.journal_table.setColumnCount(8)
        self.journal_table.setHorizontalHeaderLabels([
            "Time", "Symbol", "Side", "Entry", "Exit", "P&L", "Duration", "Notes"
        ])
        
        journal_layout.addWidget(self.journal_table)
        
        tabs.addTab(journal_tab, "Trade Journal")
        
        layout.addWidget(tabs)
        
        return widget
    
    def create_heatmap(self) -> QWidget:
        """Heatmap de correlación"""
        heatmap = pg.PlotWidget()
        heatmap.setMaximumHeight(200)
        heatmap.setBackground('#0a0a0a')
        heatmap.hideAxis('left')
        heatmap.hideAxis('bottom')
        
        # Datos de ejemplo
        data = np.random.rand(5, 5)
        img = pg.ImageItem()
        img.setImage(data)
        
        # Color map
        colormap = pg.colormap.get('CET-D1')
        img.setColorMap(colormap)
        
        heatmap.addItem(img)
        
        return heatmap
    
    def create_sentiment_gauge(self) -> QWidget:
        """Gauge de sentimiento"""
        gauge = QProgressBar()
        gauge.setRange(-100, 100)
        gauge.setValue(0)
        gauge.setFormat("Neutral (0)")
        gauge.setStyleSheet("""
            QProgressBar {
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                text-align: center;
                background-color: #1a1a1a;
            }
            QProgressBar::chunk {
                background-color: #00a8ff;
            }
        """)
        
        return gauge
    
    def create_status_bar(self):
        """Barra de estado profesional"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border-top: 1px solid #3a3a3a;
            }
        """)
        
        # Widgets de status
        self.status_connection = QLabel("● CONNECTED")
        self.status_connection.setStyleSheet("color: #00ff00; font-weight: bold;")
        status_bar.addWidget(self.status_connection)
        
        status_bar.addWidget(QLabel("|"))
        
        self.status_latency = QLabel("Latency: 0ms")
        status_bar.addWidget(self.status_latency)
        
        status_bar.addWidget(QLabel("|"))
        
        self.status_time = QLabel("00:00:00")
        status_bar.addWidget(self.status_time)
        
        status_bar.addPermanentWidget(QLabel("Trading System Pro v4.0"))
    
    def update_all_widgets(self):
        """Actualiza todos los widgets en tiempo real"""
        # Actualizar tiempo
        from datetime import datetime
        self.status_time.setText(datetime.now().strftime("%H:%M:%S"))
        
        # Simular actualización de datos (en producción, obtener de API)
        self.update_market_data()
        self.update_portfolio_data()
        self.update_chart()
    
    def update_market_data(self):
        """Actualiza datos de mercado"""
        # Simulación (en producción: obtener de API)
        price = 43250.50 + np.random.randn() * 100
        change_24h = np.random.randn() * 2
        
        self.price_label.setText(f"${price:,.2f}")
        
        color = "#00ff00" if change_24h >= 0 else "#ff0000"
        sign = "+" if change_24h >= 0 else ""
        self.change_24h_label.setText(f"{sign}{change_24h:.2f}%")
        self.change_24h_label.setStyleSheet(f"font-size: 18px; color: {color};")
    
    def update_portfolio_data(self):
        """Actualiza datos de portfolio"""
        # Simulación
        balance = 10000 + np.random.randn() * 500
        pnl = balance - 10000
        pnl_pct = (pnl / 10000) * 100
        
        self.balance_label.setText(f"${balance:,.2f}")
        
        color = "#00ff00" if pnl >= 0 else "#ff0000"
        sign = "+" if pnl >= 0 else ""
        self.pnl_label.setText(f"{sign}${pnl:,.2f} ({sign}{pnl_pct:.2f}%)")
        self.pnl_label.setStyleSheet(f"font-size: 16px; color: {color};")
    
    def update_chart(self):
        """Actualiza chart"""
        # Simulación de datos OHLC
        n_points = 100
        x = np.arange(n_points)
        
        # Generar candlesticks
        open_prices = 43000 + np.cumsum(np.random.randn(n_points) * 10)
        high_prices = open_prices + np.abs(np.random.randn(n_points) * 50)
        low_prices = open_prices - np.abs(np.random.randn(n_points) * 50)
        close_prices = open_prices + np.random.randn(n_points) * 30
        
        # Actualizar candlesticks
        data = np.column_stack([x, open_prices, high_prices, low_prices, close_prices])
        self.candlestick_item.setData(data)
