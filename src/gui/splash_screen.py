"""
Splash Screen Profesional
Pantalla de carga al iniciar la app
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys


class SplashScreen(QWidget):
    """Splash screen moderno con animación"""
    
    def __init__(self):
        super().__init__()
        
        # Sin borde
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Tamaño
        self.setFixedSize(500, 350)
        
        # Centrar en pantalla
        self.center()
        
        # Setup UI
        self.setup_ui()
        
        # Progress
        self.progress = 0
        
        # Timer para animación
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)
    
    def center(self):
        """Centrar ventana"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container con bordes redondeados
        container = QWidget()
        container.setObjectName("splashContainer")
        
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(40, 40, 40, 40)
        container_layout.setSpacing(20)
        
        # Logo
        logo_label = QLabel("💎")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 80px;")
        
        # Título
        title_label = QLabel("TradePro")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #ffffff;
            font-family: 'Segoe UI', Arial;
        """)
        
        # Subtítulo
        subtitle_label = QLabel("Professional Trading Platform")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: #888888;
            margin-bottom: 20px;
        """)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("modernProgress")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setRange(0, 100)
        
        # Loading text
        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            font-size: 13px;
            color: #00a8ff;
            margin-top: 10px;
        """)
        
        # Version
        version_label = QLabel("v4.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("""
            font-size: 11px;
            color: #555555;
            margin-top: 10px;
        """)
        
        container_layout.addWidget(logo_label)
        container_layout.addWidget(title_label)
        container_layout.addWidget(subtitle_label)
        container_layout.addStretch()
        container_layout.addWidget(self.progress_bar)
        container_layout.addWidget(self.loading_label)
        container_layout.addWidget(version_label)
        
        layout.addWidget(container)
        
        # Estilo
        self.setStyleSheet("""
            #splashContainer {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a,
                    stop:1 #1a1a2e
                );
                border-radius: 20px;
                border: 2px solid rgba(0, 168, 255, 0.3);
            }
            
            #modernProgress {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 3px;
                border: none;
            }
            
            #modernProgress::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00a8ff,
                    stop:1 #00ff88
                );
                border-radius: 3px;
            }
        """)
    
    def update_progress(self):
        """Actualizar progreso"""
        self.progress += 1
        self.progress_bar.setValue(self.progress)
        
        # Mensajes de carga
        if self.progress < 20:
            self.loading_label.setText("Initializing system...")
        elif self.progress < 40:
            self.loading_label.setText("Loading AI models...")
        elif self.progress < 60:
            self.loading_label.setText("Connecting to markets...")
        elif self.progress < 80:
            self.loading_label.setText("Setting up dashboard...")
        elif self.progress < 100:
            self.loading_label.setText("Almost ready...")
        else:
            self.loading_label.setText("Ready!")
            self.timer.stop()
            QTimer.singleShot(500, self.finish_loading)
    
    def finish_loading(self):
        """Terminar carga"""
        self.close()
    
    def paintEvent(self, event):
        """Pintar sombra"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Sombra
        shadow_rect = self.rect().adjusted(5, 5, -5, -5)
        painter.setBrush(QColor(0, 0, 0, 100))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, 20, 20)


def show_splash():
    """Mostrar splash screen"""
    app = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    return app, splash


if __name__ == "__main__":
    app, splash = show_splash()
    sys.exit(app.exec())
