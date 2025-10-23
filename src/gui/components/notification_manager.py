"""
Notification Manager - Sistema de notificaciones
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from typing import Optional
from datetime import datetime


class NotificationWidget(QWidget):
    """Widget de notificación individual"""
    
    closed = pyqtSignal()
    
    def __init__(self, title: str, message: str, notification_type: str = "info"):
        super().__init__()
        
        self.setFixedSize(350, 100)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Container
        container = QWidget()
        container.setObjectName("notificationContainer")
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(15, 10, 15, 10)
        
        # Icono según tipo
        icons = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "trade": "💰"
        }
        
        icon_label = QLabel(icons.get(notification_type, "ℹ️"))
        icon_label.setStyleSheet("font-size: 32px;")
        
        # Texto
        text_layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ffffff;")
        
        message_label = QLabel(message)
        message_label.setStyleSheet("font-size: 12px; color: #cccccc;")
        message_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(message_label)
        
        # Botón cerrar
        close_btn = QPushButton("✖")
        close_btn.setFixedSize(25, 25)
        close_btn.setObjectName("notificationClose")
        close_btn.clicked.connect(self.close_notification)
        
        container_layout.addWidget(icon_label)
        container_layout.addLayout(text_layout)
        container_layout.addStretch()
        container_layout.addWidget(close_btn)
        
        layout.addWidget(container)
        
        # Estilo
        colors = {
            "success": "#00ff88",
            "error": "#ff4444",
            "warning": "#ffaa00",
            "info": "#00a8ff",
            "trade": "#00ff88"
        }
        
        color = colors.get(notification_type, "#00a8ff")
        
        self.setStyleSheet(f"""
            #notificationContainer {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(26, 26, 46, 0.95),
                    stop:1 rgba(26, 26, 46, 0.95)
                );
                border-left: 4px solid {color};
                border-radius: 10px;
            }}
            
            #notificationClose {{
                background: transparent;
                border: none;
                color: #888888;
                font-size: 14px;
            }}
            
            #notificationClose:hover {{
                color: #ffffff;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }}
        """)
        
        # Auto-cerrar después de 5 segundos
        QTimer.singleShot(5000, self.close_notification)
    
    def close_notification(self):
        """Cerrar notificación con animación"""
        self.closed.emit()
        self.close()


class NotificationManager(QObject):
    """
    Gestor de notificaciones del sistema
    Muestra notificaciones en la esquina de la pantalla
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.notifications = []
        self.max_notifications = 5
        self.spacing = 10
    
    def show_notification(
        self,
        title: str,
        message: str,
        notification_type: str = "info"
    ):
        """
        Mostrar notificación
        
        Args:
            title: Título de la notificación
            message: Mensaje
            notification_type: 'success', 'error', 'warning', 'info', 'trade'
        """
        # Limitar número de notificaciones
        if len(self.notifications) >= self.max_notifications:
            oldest = self.notifications.pop(0)
            oldest.close()
        
        # Crear notificación
        notification = NotificationWidget(title, message, notification_type)
        notification.closed.connect(lambda: self.remove_notification(notification))
        
        # Posicionar en pantalla
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - notification.width() - 20
        y = screen.height() - notification.height() - 20
        
        # Ajustar por notificaciones existentes
        for existing in self.notifications:
            y -= (existing.height() + self.spacing)
        
        notification.move(x, y)
        notification.show()
        
        self.notifications.append(notification)
    
    def remove_notification(self, notification):
        """Remover notificación de la lista"""
        if notification in self.notifications:
            self.notifications.remove(notification)
            self.reposition_notifications()
    
    def reposition_notifications(self):
        """Reposicionar notificaciones después de cerrar una"""
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - 370
        y = screen.height() - 120
        
        for notification in reversed(self.notifications):
            notification.move(x, y)
            y -= (notification.height() + self.spacing)
    
    def show_trade_executed(self, symbol: str, side: str, amount: float, price: float):
        """Notificación de trade ejecutado"""
        self.show_notification(
            "Trade Ejecutado",
            f"{side.upper()} {amount} {symbol} @ ${price:,.2f}",
            "trade"
        )
    
    def show_position_closed(self, symbol: str, pnl: float):
        """Notificación de posición cerrada"""
        notification_type = "success" if pnl > 0 else "error"
        sign = "+" if pnl > 0 else ""
        
        self.show_notification(
            "Posición Cerrada",
            f"{symbol}: {sign}${pnl:,.2f}",
            notification_type
        )
    
    def show_error(self, error_message: str):
        """Notificación de error"""
        self.show_notification(
            "Error",
            error_message,
            "error"
        )
    
    def show_success(self, message: str):
        """Notificación de éxito"""
        self.show_notification(
            "Éxito",
            message,
            "success"
        )
    
    def show_warning(self, message: str):
        """Notificación de advertencia"""
        self.show_notification(
            "Advertencia",
            message,
            "warning"
        )
    
    def show_broker_connected(self, broker: str):
        """Notificación de broker conectado"""
        self.show_notification(
            "Broker Conectado",
            f"Conectado exitosamente a {broker}",
            "success"
        )
    
    def show_auto_trading_started(self):
        """Notificación de trading automático iniciado"""
        self.show_notification(
            "Trading Automático",
            "Sistema de trading automático iniciado",
            "success"
        )
    
    def show_auto_trading_stopped(self):
        """Notificación de trading automático detenido"""
        self.show_notification(
            "Trading Automático",
            "Sistema de trading automático detenido",
            "warning"
        )
