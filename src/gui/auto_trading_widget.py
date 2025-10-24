"""
Widget de interfaz para el AutoTrader
Control y monitoreo del bot de trading automático
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QGroupBox, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from loguru import logger
from datetime import datetime
import asyncio
import threading


class AutoTradingWidget(QWidget):
    """Widget para controlar el AutoTrader"""
    
    # Señales
    status_changed = pyqtSignal(dict)
    trade_executed = pyqtSignal(str, dict)
    signal_detected = pyqtSignal(str, dict)
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.auto_trader = None
        
        self.init_ui()
        
        # Timer para actualizar estado
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(1000)  # Cada segundo
    
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Título
        title = QLabel("🤖 Trading Automático con IA")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ff88;")
        layout.addWidget(title)
        
        # Estado del bot
        layout.addWidget(self.create_status_section())
        
        # Configuración
        layout.addWidget(self.create_config_section())
        
        # Controles
        layout.addWidget(self.create_controls_section())
        
        # Posiciones activas
        layout.addWidget(self.create_positions_section())
        
        # Señales recientes
        layout.addWidget(self.create_signals_section())
        
        # Log de actividad
        layout.addWidget(self.create_log_section())
        
        self.setLayout(layout)

    def _run_async(self, coro):
        """Ejecuta una corrutina en un hilo de fondo con su propio loop"""
        def runner():
            try:
                asyncio.run(coro)
            except Exception as e:
                self.log(f"❌ Error de ejecución async: {e}")
        t = threading.Thread(target=runner, daemon=True)
        t.start()
    
    def create_status_section(self):
        """Crea sección de estado"""
        group = QGroupBox("📊 Estado del Bot")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background: #1a1a1a;
            }
            QGroupBox::title {
                color: #00ff88;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Grid de métricas
        metrics_layout = QHBoxLayout()
        
        # Estado
        self.status_label = QLabel("● Detenido")
        self.status_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #ff4444;")
        metrics_layout.addWidget(self.status_label)
        
        metrics_layout.addStretch()
        
        # Balance
        balance_layout = QVBoxLayout()
        balance_layout.addWidget(QLabel("Balance:"))
        self.balance_label = QLabel("$0.00")
        self.balance_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.balance_label.setStyleSheet("color: #00ff88;")
        balance_layout.addWidget(self.balance_label)
        metrics_layout.addLayout(balance_layout)
        
        # P&L Diario
        pnl_layout = QVBoxLayout()
        pnl_layout.addWidget(QLabel("P&L Diario:"))
        self.pnl_label = QLabel("$0.00")
        self.pnl_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        pnl_layout.addWidget(self.pnl_label)
        metrics_layout.addLayout(pnl_layout)
        
        # Trades hoy
        trades_layout = QVBoxLayout()
        trades_layout.addWidget(QLabel("Trades Hoy:"))
        self.trades_label = QLabel("0")
        self.trades_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.trades_label.setStyleSheet("color: #00aaff;")
        trades_layout.addWidget(self.trades_label)
        metrics_layout.addLayout(trades_layout)
        
        # Posiciones activas
        positions_layout = QVBoxLayout()
        positions_layout.addWidget(QLabel("Posiciones:"))
        self.positions_label = QLabel("0")
        self.positions_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.positions_label.setStyleSheet("color: #ffaa00;")
        positions_layout.addWidget(self.positions_label)
        metrics_layout.addLayout(positions_layout)
        
        layout.addLayout(metrics_layout)
        
        # Barra de progreso (trades diarios)
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("Progreso diario:"))
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(20)  # Max trades diarios
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #333;
                border-radius: 5px;
                text-align: center;
                background: #0a0a0a;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff88, stop:1 #00aaff);
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        layout.addLayout(progress_layout)
        
        group.setLayout(layout)
        return group
    
    def create_config_section(self):
        """Crea sección de configuración"""
        group = QGroupBox("⚙️ Configuración")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background: #1a1a1a;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Símbolos
        symbols_layout = QVBoxLayout()
        symbols_layout.addWidget(QLabel("Símbolos:"))
        self.symbols_input = QComboBox()
        self.symbols_input.addItems(['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT'])
        self.symbols_input.setEditable(True)
        symbols_layout.addWidget(self.symbols_input)
        layout.addLayout(symbols_layout)
        
        # Timeframe
        timeframe_layout = QVBoxLayout()
        timeframe_layout.addWidget(QLabel("Timeframe:"))
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(['1m', '5m', '15m', '1h'])
        self.timeframe_combo.setCurrentText('5m')
        timeframe_layout.addWidget(self.timeframe_combo)
        layout.addLayout(timeframe_layout)
        
        # Max posiciones
        max_pos_layout = QVBoxLayout()
        max_pos_layout.addWidget(QLabel("Max Posiciones:"))
        self.max_positions_spin = QSpinBox()
        self.max_positions_spin.setRange(1, 10)
        self.max_positions_spin.setValue(3)
        max_pos_layout.addWidget(self.max_positions_spin)
        layout.addLayout(max_pos_layout)
        
        # Riesgo por trade
        risk_layout = QVBoxLayout()
        risk_layout.addWidget(QLabel("Riesgo/Trade (%):"))
        self.risk_spin = QDoubleSpinBox()
        self.risk_spin.setRange(0.5, 10.0)
        self.risk_spin.setValue(2.0)
        self.risk_spin.setSingleStep(0.5)
        risk_layout.addWidget(self.risk_spin)
        layout.addLayout(risk_layout)
        
        # Confianza mínima
        confidence_layout = QVBoxLayout()
        confidence_layout.addWidget(QLabel("Confianza Min (%):"))
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(50.0, 95.0)
        self.confidence_spin.setValue(65.0)
        self.confidence_spin.setSingleStep(5.0)
        confidence_layout.addWidget(self.confidence_spin)
        layout.addLayout(confidence_layout)
        
        # Trailing stop
        self.trailing_check = QCheckBox("Trailing Stop")
        self.trailing_check.setChecked(True)
        layout.addWidget(self.trailing_check)
        
        group.setLayout(layout)
        return group
    
    def create_controls_section(self):
        """Crea sección de controles"""
        group = QGroupBox("🎮 Controles")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background: #1a1a1a;
            }
        """)
        
        layout = QHBoxLayout()
        
        # Botón Iniciar
        self.start_btn = QPushButton("🚀 Iniciar Bot")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff88, stop:1 #00aaff);
                color: black;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffaa, stop:1 #00ccff);
            }
            QPushButton:disabled {
                background: #333;
                color: #666;
            }
        """)
        self.start_btn.clicked.connect(self.start_bot)
        layout.addWidget(self.start_btn)
        
        # Botón Pausar
        self.pause_btn = QPushButton("⏸️ Pausar")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background: #ffaa00;
                color: black;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: #ffcc00;
            }
            QPushButton:disabled {
                background: #333;
                color: #666;
            }
        """)
        self.pause_btn.clicked.connect(self.pause_bot)
        layout.addWidget(self.pause_btn)
        
        # Botón Detener
        self.stop_btn = QPushButton("🛑 Detener")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #ff4444;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: #ff6666;
            }
            QPushButton:disabled {
                background: #333;
                color: #666;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_bot)
        layout.addWidget(self.stop_btn)
        
        layout.addStretch()
        
        # Botón Cerrar Posiciones
        self.close_all_btn = QPushButton("🔒 Cerrar Todas")
        self.close_all_btn.setStyleSheet("""
            QPushButton {
                background: #aa00ff;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background: #cc00ff;
            }
        """)
        self.close_all_btn.clicked.connect(self.close_all_positions)
        layout.addWidget(self.close_all_btn)
        
        group.setLayout(layout)
        return group
    
    def create_positions_section(self):
        """Crea sección de posiciones activas"""
        group = QGroupBox("💼 Posiciones Activas")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background: #1a1a1a;
            }
        """)
        
        layout = QVBoxLayout()
        
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(7)
        self.positions_table.setHorizontalHeaderLabels([
            'Símbolo', 'Lado', 'Cantidad', 'Entrada', 'Actual', 'P&L', 'Tiempo'
        ])
        self.positions_table.setStyleSheet("""
            QTableWidget {
                background: #0a0a0a;
                color: white;
                gridline-color: #333;
                border: none;
            }
            QHeaderView::section {
                background: #1a1a1a;
                color: #00ff88;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.positions_table)
        group.setLayout(layout)
        return group
    
    def create_signals_section(self):
        """Crea sección de señales recientes"""
        group = QGroupBox("📡 Señales Recientes")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background: #1a1a1a;
            }
        """)
        
        layout = QVBoxLayout()
        
        self.signals_table = QTableWidget()
        self.signals_table.setColumnCount(5)
        self.signals_table.setHorizontalHeaderLabels([
            'Hora', 'Símbolo', 'Señal', 'Confianza', 'Razón'
        ])
        self.signals_table.setStyleSheet("""
            QTableWidget {
                background: #0a0a0a;
                color: white;
                gridline-color: #333;
                border: none;
            }
            QHeaderView::section {
                background: #1a1a1a;
                color: #00ff88;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.signals_table)
        group.setLayout(layout)
        return group
    
    def create_log_section(self):
        """Crea sección de log"""
        group = QGroupBox("📝 Log de Actividad")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #333;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background: #1a1a1a;
            }
        """)
        
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background: #0a0a0a;
                color: #00ff88;
                border: none;
                font-family: 'Courier New';
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.log_text)
        group.setLayout(layout)
        return group
    
    def start_bot(self):
        """Inicia el bot"""
        try:
            self.log("🚀 Iniciando AutoTrader...")
            
            # Obtener configuración
            config = {
                'symbols': [self.symbols_input.currentText()],
                'timeframe': self.timeframe_combo.currentText(),
                'max_positions': self.max_positions_spin.value(),
                'risk_per_trade': self.risk_spin.value() / 100,
                'min_confidence': self.confidence_spin.value() / 100,
                'use_trailing_stop': self.trailing_check.isChecked(),
                'max_daily_trades': 20,
                'max_daily_loss': 0.05
            }
            
            # Crear AutoTrader
            from ..auto_trading import AutoTrader
            
            # Validar conexión del controlador (REST)
            if self.controller and self.controller.is_connected:
                # Pasar el controller al AutoTrader para usar la API REST
                self.auto_trader = AutoTrader(self.controller, config)
                
                # Configurar callbacks
                self.auto_trader.on_trade_callback = self.on_trade
                self.auto_trader.on_signal_callback = self.on_signal
                self.auto_trader.on_error_callback = self.on_error
                
                # Iniciar en hilo separado con su propio event loop
                self._run_async(self.auto_trader.start())
                
                # Actualizar UI
                self.start_btn.setEnabled(False)
                self.pause_btn.setEnabled(True)
                self.stop_btn.setEnabled(True)
                
                self.status_label.setText("● Corriendo")
                self.status_label.setStyleSheet("color: #00ff88;")
                
                self.log("✅ AutoTrader iniciado exitosamente")
            else:
                self.log("❌ Error: API/Controller no conectado. Conecta el broker en Settings primero.")
                
        except Exception as e:
            self.log(f"❌ Error iniciando bot: {e}")
            logger.exception("Error:")
    
    def pause_bot(self):
        """Pausa el bot"""
        if self.auto_trader:
            if self.auto_trader.is_paused:
                self._run_async(self.auto_trader.resume())
                self.pause_btn.setText("⏸️ Pausar")
                self.log("▶️ Bot reanudado")
            else:
                self._run_async(self.auto_trader.pause())
                self.pause_btn.setText("▶️ Reanudar")
                self.log("⏸️ Bot pausado")
    
    def stop_bot(self):
        """Detiene el bot"""
        if self.auto_trader:
            self._run_async(self.auto_trader.stop())
            
            # Actualizar UI
            self.start_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            
            self.status_label.setText("● Detenido")
            self.status_label.setStyleSheet("color: #ff4444;")
            
            self.log("🛑 Bot detenido")
    
    def close_all_positions(self):
        """Cierra todas las posiciones"""
        if self.auto_trader:
            self._run_async(self.auto_trader._close_all_positions())
            self.log("🔒 Cerrando todas las posiciones...")
    
    def update_status(self):
        """Actualiza el estado del bot"""
        if self.auto_trader:
            status = self.auto_trader.get_status()
            
            # Actualizar labels
            self.balance_label.setText(f"${status['balance']:,.2f}")
            
            pnl = status['daily_pnl']
            pnl_color = "#00ff88" if pnl >= 0 else "#ff4444"
            self.pnl_label.setText(f"${pnl:+,.2f}")
            self.pnl_label.setStyleSheet(f"color: {pnl_color}; font-size: 16px; font-weight: bold;")
            
            self.trades_label.setText(str(status['daily_trades']))
            self.positions_label.setText(str(status['active_positions']))
            
            self.progress_bar.setValue(status['daily_trades'])
            
            # Actualizar tabla de posiciones
            self.update_positions_table()
    
    def update_positions_table(self):
        """Actualiza la tabla de posiciones"""
        if not self.auto_trader:
            return
        
        positions = self.auto_trader.active_positions
        self.positions_table.setRowCount(len(positions))
        
        for row, (symbol, pos) in enumerate(positions.items()):
            self.positions_table.setItem(row, 0, QTableWidgetItem(symbol))
            self.positions_table.setItem(row, 1, QTableWidgetItem(pos['signal']['action']))
            self.positions_table.setItem(row, 2, QTableWidgetItem(f"{pos['quantity']:.4f}"))
            self.positions_table.setItem(row, 3, QTableWidgetItem(f"${pos['entry_price']:.2f}"))
            # Actual y P&L se actualizarían con precio en tiempo real
            self.positions_table.setItem(row, 4, QTableWidgetItem("--"))
            self.positions_table.setItem(row, 5, QTableWidgetItem("--"))
            
            elapsed = datetime.now() - pos['entry_time']
            self.positions_table.setItem(row, 6, QTableWidgetItem(str(elapsed).split('.')[0]))
    
    def on_trade(self, symbol: str, order, signal):
        """Callback cuando se ejecuta un trade"""
        self.log(f"✅ Trade ejecutado: {signal['action']} {symbol}")
        self.trade_executed.emit(symbol, {'order': order, 'signal': signal})
    
    def on_signal(self, symbol: str, signal):
        """Callback cuando se detecta una señal"""
        self.log(f"📡 Señal: {signal['action']} {symbol} ({signal['confidence']:.0%})")
        self.signal_detected.emit(symbol, signal)
        
        # Agregar a tabla de señales
        row = self.signals_table.rowCount()
        self.signals_table.insertRow(row)
        
        self.signals_table.setItem(row, 0, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
        self.signals_table.setItem(row, 1, QTableWidgetItem(symbol))
        self.signals_table.setItem(row, 2, QTableWidgetItem(signal['action']))
        self.signals_table.setItem(row, 3, QTableWidgetItem(f"{signal['confidence']:.0%}"))
        self.signals_table.setItem(row, 4, QTableWidgetItem(signal['reason'][:50]))
        
        # Limitar a 10 señales
        if self.signals_table.rowCount() > 10:
            self.signals_table.removeRow(0)
    
    def on_error(self, symbol: str, error: str):
        """Callback cuando hay un error"""
        self.log(f"❌ Error en {symbol}: {error}")
    
    def log(self, message: str):
        """Agrega mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
