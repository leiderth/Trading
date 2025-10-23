"""
Clase base abstracta para todos los conectores de brokers
Define la interfaz común que deben implementar todos los brokers
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import pandas as pd


class OrderSide(Enum):
    """Tipo de orden"""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Tipo de ejecución"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(Enum):
    """Estado de la orden"""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PositionSide(Enum):
    """Lado de la posición"""
    LONG = "long"
    SHORT = "short"
    NEUTRAL = "neutral"


@dataclass
class Order:
    """Estructura de una orden"""
    id: str
    symbol: str
    side: OrderSide
    type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_price: float = 0.0
    commission: float = 0.0
    timestamp: datetime = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Position:
    """Estructura de una posición abierta"""
    id: str
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    current_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0
    commission: float = 0.0
    opened_at: datetime = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.opened_at is None:
            self.opened_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        self.update_pnl(self.current_price)
    
    def update_pnl(self, current_price: float):
        """Actualiza el P&L de la posición"""
        self.current_price = current_price
        
        if self.side == PositionSide.LONG:
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        elif self.side == PositionSide.SHORT:
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity
        
        if self.entry_price > 0:
            self.unrealized_pnl_percent = (self.unrealized_pnl / (self.entry_price * self.quantity)) * 100


@dataclass
class Trade:
    """Estructura de un trade cerrado"""
    id: str
    symbol: str
    side: PositionSide
    quantity: float
    entry_price: float
    exit_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    realized_pnl: float = 0.0
    realized_pnl_percent: float = 0.0
    commission: float = 0.0
    opened_at: datetime = None
    closed_at: datetime = None
    duration_seconds: float = 0.0
    exit_reason: str = "manual"  # manual, stop_loss, take_profit, trailing_stop
    metadata: Dict = None
    
    def __post_init__(self):
        if self.opened_at is None:
            self.opened_at = datetime.now()
        if self.closed_at is None:
            self.closed_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}
        
        # Calcular P&L
        if self.side == PositionSide.LONG:
            self.realized_pnl = (self.exit_price - self.entry_price) * self.quantity
        elif self.side == PositionSide.SHORT:
            self.realized_pnl = (self.entry_price - self.exit_price) * self.quantity
        
        self.realized_pnl -= self.commission
        
        if self.entry_price > 0:
            self.realized_pnl_percent = (self.realized_pnl / (self.entry_price * self.quantity)) * 100
        
        # Calcular duración
        if self.opened_at and self.closed_at:
            self.duration_seconds = (self.closed_at - self.opened_at).total_seconds()


@dataclass
class AccountInfo:
    """Información de la cuenta"""
    balance: float
    equity: float
    margin_used: float = 0.0
    margin_available: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    total_pnl: float = 0.0
    open_positions: int = 0
    currency: str = "USD"
    leverage: float = 1.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        self.total_pnl = self.realized_pnl + self.unrealized_pnl
        self.equity = self.balance + self.unrealized_pnl


class BaseBroker(ABC):
    """
    Clase base abstracta para conectores de brokers
    Todos los brokers deben heredar de esta clase e implementar sus métodos
    """
    
    def __init__(self, config: Dict):
        """
        Inicializa el conector del broker
        
        Args:
            config: Diccionario con configuración del broker
        """
        self.config = config
        self.connected = False
        self.demo_mode = config.get('demo_mode', True)
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establece conexión con el broker
        
        Returns:
            True si la conexión fue exitosa
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Cierra la conexión con el broker
        
        Returns:
            True si se desconectó correctamente
        """
        pass
    
    @abstractmethod
    async def get_account_info(self) -> AccountInfo:
        """
        Obtiene información de la cuenta
        
        Returns:
            Objeto AccountInfo con datos de la cuenta
        """
        pass
    
    @abstractmethod
    async def get_live_data(
        self, 
        symbol: str, 
        timeframe: str, 
        bars: int = 100
    ) -> pd.DataFrame:
        """
        Obtiene datos de mercado en tiempo real
        
        Args:
            symbol: Símbolo del activo (ej: "EUR/USD")
            timeframe: Timeframe (ej: "5m", "1h")
            bars: Número de velas a obtener
            
        Returns:
            DataFrame con columnas: timestamp, open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    async def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Order:
        """
        Coloca una orden de mercado
        
        Args:
            symbol: Símbolo del activo
            side: BUY o SELL
            quantity: Cantidad a operar
            stop_loss: Precio de stop loss (opcional)
            take_profit: Precio de take profit (opcional)
            
        Returns:
            Objeto Order con información de la orden
        """
        pass
    
    @abstractmethod
    async def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Order:
        """
        Coloca una orden límite
        
        Args:
            symbol: Símbolo del activo
            side: BUY o SELL
            quantity: Cantidad a operar
            price: Precio límite
            stop_loss: Precio de stop loss (opcional)
            take_profit: Precio de take profit (opcional)
            
        Returns:
            Objeto Order con información de la orden
        """
        pass
    
    @abstractmethod
    async def modify_order(
        self,
        order_id: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """
        Modifica una orden existente
        
        Args:
            order_id: ID de la orden
            stop_loss: Nuevo stop loss (opcional)
            take_profit: Nuevo take profit (opcional)
            
        Returns:
            True si se modificó correctamente
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """
        Cancela una orden pendiente
        
        Args:
            order_id: ID de la orden
            
        Returns:
            True si se canceló correctamente
        """
        pass
    
    @abstractmethod
    async def close_position(
        self,
        position_id: str,
        quantity: Optional[float] = None
    ) -> Trade:
        """
        Cierra una posición abierta
        
        Args:
            position_id: ID de la posición
            quantity: Cantidad a cerrar (None = cerrar todo)
            
        Returns:
            Objeto Trade con información del trade cerrado
        """
        pass
    
    @abstractmethod
    async def get_open_positions(self) -> List[Position]:
        """
        Obtiene todas las posiciones abiertas
        
        Returns:
            Lista de objetos Position
        """
        pass
    
    @abstractmethod
    async def get_open_orders(self) -> List[Order]:
        """
        Obtiene todas las órdenes pendientes
        
        Returns:
            Lista de objetos Order
        """
        pass
    
    @abstractmethod
    async def get_trade_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Trade]:
        """
        Obtiene historial de trades cerrados
        
        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            limit: Número máximo de trades
            
        Returns:
            Lista de objetos Trade
        """
        pass
    
    @abstractmethod
    async def get_current_price(self, symbol: str) -> Tuple[float, float]:
        """
        Obtiene precio actual (bid/ask)
        
        Args:
            symbol: Símbolo del activo
            
        Returns:
            Tupla (bid, ask)
        """
        pass
    
    def is_connected(self) -> bool:
        """Verifica si está conectado al broker"""
        return self.connected
    
    def is_demo_mode(self) -> bool:
        """Verifica si está en modo demo"""
        return self.demo_mode
    
    def __repr__(self) -> str:
        mode = "DEMO" if self.demo_mode else "LIVE"
        status = "Connected" if self.connected else "Disconnected"
        return f"<{self.__class__.__name__}({mode}, {status})>"
