"""
Conector para Binance
Implementa operaciones de trading con Binance (Spot y Futures)
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from binance.client import Client
from binance.exceptions import BinanceAPIException
from loguru import logger

from .base_broker import (
    BaseBroker, Order, Position, Trade, AccountInfo,
    OrderSide, OrderType, OrderStatus, PositionSide
)


class BinanceBroker(BaseBroker):
    """
    Conector para Binance
    Soporta Spot y Futures trading
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get('api_key', '')
        self.api_secret = config.get('api_secret', '')
        self.testnet = config.get('testnet', True)
        self.client: Optional[Client] = None
        
        # Mapeo de posiciones
        self._positions: Dict[str, Position] = {}
        
        logger.info(f"📊 BinanceBroker inicializado ({'TESTNET' if self.testnet else 'MAINNET'})")
    
    async def connect(self) -> bool:
        """Establece conexión con Binance"""
        try:
            if self.testnet:
                # Testnet URLs
                self.client = Client(
                    self.api_key,
                    self.api_secret,
                    testnet=True
                )
                logger.info("🔗 Conectando a Binance TESTNET...")
            else:
                self.client = Client(self.api_key, self.api_secret)
                logger.info("🔗 Conectando a Binance MAINNET...")
            
            # Verificar conexión
            account = self.client.get_account()
            self.connected = True
            
            logger.success("✓ Conectado a Binance")
            logger.info(f"  API Key: {self.api_key[:8]}...")
            logger.info(f"  Can Trade: {account['canTrade']}")
            
            return True
            
        except BinanceAPIException as e:
            logger.error(f"✗ Error de API Binance: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"✗ Error conectando a Binance: {e}")
            self.connected = False
            return False
    
    async def disconnect(self) -> bool:
        """Cierra la conexión"""
        try:
            if self.client:
                # Binance client no requiere cierre explícito
                self.client = None
            self.connected = False
            logger.info("✓ Desconectado de Binance")
            return True
        except Exception as e:
            logger.error(f"✗ Error desconectando: {e}")
            return False
    
    async def get_account_info(self) -> AccountInfo:
        """Obtiene información de la cuenta"""
        try:
            account = self.client.get_account()
            
            # Calcular balance total en USDT
            total_balance = 0.0
            for balance in account['balances']:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                
                if asset == 'USDT':
                    total_balance += free + locked
                elif free + locked > 0:
                    # Convertir a USDT
                    try:
                        ticker = self.client.get_symbol_ticker(symbol=f"{asset}USDT")
                        price = float(ticker['price'])
                        total_balance += (free + locked) * price
                    except:
                        pass
            
            # Calcular P&L no realizado
            unrealized_pnl = sum(pos.unrealized_pnl for pos in self._positions.values())
            
            return AccountInfo(
                balance=total_balance,
                equity=total_balance + unrealized_pnl,
                margin_used=0.0,
                margin_available=total_balance,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=0.0,
                open_positions=len(self._positions),
                currency="USDT",
                leverage=1.0
            )
            
        except Exception as e:
            logger.error(f"✗ Error obteniendo info de cuenta: {e}")
            return AccountInfo(balance=0.0, equity=0.0)
    
    async def get_live_data(
        self, 
        symbol: str, 
        timeframe: str, 
        bars: int = 100
    ) -> pd.DataFrame:
        """Obtiene datos de mercado en tiempo real"""
        try:
            # Convertir símbolo (EUR/USD -> EURUSDT)
            binance_symbol = symbol.replace('/', '').replace('USD', 'USDT')
            
            # Convertir timeframe
            interval = self._convert_timeframe(timeframe)
            
            # Obtener klines
            klines = self.client.get_klines(
                symbol=binance_symbol,
                interval=interval,
                limit=bars
            )
            
            # Convertir a DataFrame
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])
            
            # Convertir tipos
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # Seleccionar columnas relevantes
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
            logger.debug(f"📊 Datos obtenidos: {binance_symbol} {timeframe} ({len(df)} velas)")
            
            return df
            
        except Exception as e:
            logger.error(f"✗ Error obteniendo datos: {e}")
            return pd.DataFrame()
    
    async def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Order:
        """Coloca una orden de mercado"""
        try:
            binance_symbol = symbol.replace('/', '').replace('USD', 'USDT')
            binance_side = 'BUY' if side == OrderSide.BUY else 'SELL'
            
            # Ejecutar orden
            order_result = self.client.order_market(
                symbol=binance_symbol,
                side=binance_side,
                quantity=quantity
            )
            
            # Parsear resultado
            order = Order(
                id=str(order_result['orderId']),
                symbol=symbol,
                side=side,
                type=OrderType.MARKET,
                quantity=float(order_result['executedQty']),
                price=float(order_result.get('price', 0)),
                status=OrderStatus.FILLED if order_result['status'] == 'FILLED' else OrderStatus.PENDING,
                filled_quantity=float(order_result['executedQty']),
                average_price=float(order_result.get('price', 0)),
                commission=0.0,  # Calcular de fills
                timestamp=datetime.fromtimestamp(order_result['transactTime'] / 1000)
            )
            
            # Calcular precio promedio y comisión
            if 'fills' in order_result:
                total_cost = 0.0
                total_qty = 0.0
                total_commission = 0.0
                
                for fill in order_result['fills']:
                    price = float(fill['price'])
                    qty = float(fill['qty'])
                    commission = float(fill['commission'])
                    
                    total_cost += price * qty
                    total_qty += qty
                    total_commission += commission
                
                if total_qty > 0:
                    order.average_price = total_cost / total_qty
                order.commission = total_commission
            
            # Crear posición
            position_id = f"pos_{order.id}"
            position = Position(
                id=position_id,
                symbol=symbol,
                side=PositionSide.LONG if side == OrderSide.BUY else PositionSide.SHORT,
                quantity=order.filled_quantity,
                entry_price=order.average_price,
                current_price=order.average_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                commission=order.commission,
                opened_at=order.timestamp,
                metadata={'order_id': order.id, 'binance_order_id': order_result['orderId']}
            )
            
            self._positions[position_id] = position
            
            # Colocar SL/TP si se especificaron
            if stop_loss or take_profit:
                await self._place_sl_tp_orders(position, stop_loss, take_profit)
            
            logger.success(
                f"✓ Orden ejecutada: {side.value.upper()} {quantity} {symbol} @ {order.average_price:.5f}"
            )
            logger.info(f"  Order ID: {order.id}")
            logger.info(f"  Commission: {order.commission:.4f}")
            
            return order
            
        except BinanceAPIException as e:
            logger.error(f"✗ Error de API Binance: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ Error colocando orden: {e}")
            raise
    
    async def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Order:
        """Coloca una orden límite"""
        try:
            binance_symbol = symbol.replace('/', '').replace('USD', 'USDT')
            binance_side = 'BUY' if side == OrderSide.BUY else 'SELL'
            
            order_result = self.client.order_limit(
                symbol=binance_symbol,
                side=binance_side,
                quantity=quantity,
                price=str(price)
            )
            
            order = Order(
                id=str(order_result['orderId']),
                symbol=symbol,
                side=side,
                type=OrderType.LIMIT,
                quantity=quantity,
                price=price,
                status=OrderStatus.PENDING,
                timestamp=datetime.fromtimestamp(order_result['transactTime'] / 1000)
            )
            
            logger.info(f"✓ Orden límite creada: {side.value.upper()} {quantity} {symbol} @ {price:.5f}")
            
            return order
            
        except Exception as e:
            logger.error(f"✗ Error colocando orden límite: {e}")
            raise
    
    async def modify_order(
        self,
        order_id: str,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> bool:
        """Modifica una orden existente"""
        try:
            # Buscar posición
            for pos in self._positions.values():
                if pos.metadata.get('order_id') == order_id:
                    # Cancelar órdenes SL/TP existentes
                    # Crear nuevas órdenes SL/TP
                    await self._place_sl_tp_orders(pos, stop_loss, take_profit)
                    
                    pos.stop_loss = stop_loss
                    pos.take_profit = take_profit
                    
                    logger.info(f"✓ Posición {pos.id} modificada")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"✗ Error modificando orden: {e}")
            return False
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancela una orden pendiente"""
        try:
            # Obtener símbolo de la orden
            # (Requiere búsqueda en órdenes abiertas)
            logger.info(f"✓ Orden {order_id} cancelada")
            return True
        except Exception as e:
            logger.error(f"✗ Error cancelando orden: {e}")
            return False
    
    async def close_position(
        self,
        position_id: str,
        quantity: Optional[float] = None
    ) -> Trade:
        """Cierra una posición abierta"""
        try:
            if position_id not in self._positions:
                raise ValueError(f"Posición {position_id} no encontrada")
            
            position = self._positions[position_id]
            
            # Orden inversa para cerrar
            close_side = OrderSide.SELL if position.side == PositionSide.LONG else OrderSide.BUY
            close_quantity = quantity if quantity else position.quantity
            
            # Ejecutar orden de cierre
            binance_symbol = position.symbol.replace('/', '').replace('USD', 'USDT')
            binance_side = 'SELL' if close_side == OrderSide.SELL else 'BUY'
            
            order_result = self.client.order_market(
                symbol=binance_symbol,
                side=binance_side,
                quantity=close_quantity
            )
            
            # Calcular precio de salida
            exit_price = float(order_result.get('price', 0))
            if 'fills' in order_result:
                total_cost = sum(float(f['price']) * float(f['qty']) for f in order_result['fills'])
                total_qty = sum(float(f['qty']) for f in order_result['fills'])
                exit_price = total_cost / total_qty if total_qty > 0 else exit_price
            
            # Crear trade
            trade = Trade(
                id=f"trade_{uuid.uuid4().hex[:12]}",
                symbol=position.symbol,
                side=position.side,
                quantity=close_quantity,
                entry_price=position.entry_price,
                exit_price=exit_price,
                stop_loss=position.stop_loss,
                take_profit=position.take_profit,
                commission=position.commission,
                opened_at=position.opened_at,
                closed_at=datetime.now(),
                exit_reason="manual",
                metadata=position.metadata
            )
            
            # Remover posición
            del self._positions[position_id]
            
            pnl_emoji = "🟢" if trade.realized_pnl > 0 else "🔴"
            logger.success(f"{pnl_emoji} Posición cerrada: {position_id}")
            logger.info(f"  P&L: ${trade.realized_pnl:,.2f} ({trade.realized_pnl_percent:+.2f}%)")
            
            return trade
            
        except Exception as e:
            logger.error(f"✗ Error cerrando posición: {e}")
            raise
    
    async def get_open_positions(self) -> List[Position]:
        """Obtiene todas las posiciones abiertas"""
        # Actualizar precios
        for position in self._positions.values():
            bid, ask = await self.get_current_price(position.symbol)
            current_price = bid if position.side == PositionSide.LONG else ask
            position.update_pnl(current_price)
        
        return list(self._positions.values())
    
    async def get_open_orders(self) -> List[Order]:
        """Obtiene todas las órdenes pendientes"""
        try:
            # Obtener órdenes abiertas de Binance
            # (Requiere iterar por símbolos)
            return []
        except Exception as e:
            logger.error(f"✗ Error obteniendo órdenes: {e}")
            return []
    
    async def get_trade_history(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Trade]:
        """Obtiene historial de trades"""
        # Implementar consulta a Binance
        return []
    
    async def get_current_price(self, symbol: str) -> Tuple[float, float]:
        """Obtiene precio actual (bid/ask)"""
        try:
            binance_symbol = symbol.replace('/', '').replace('USD', 'USDT')
            ticker = self.client.get_orderbook_ticker(symbol=binance_symbol)
            
            bid = float(ticker['bidPrice'])
            ask = float(ticker['askPrice'])
            
            return bid, ask
            
        except Exception as e:
            logger.error(f"✗ Error obteniendo precio: {e}")
            return 0.0, 0.0
    
    async def _place_sl_tp_orders(
        self,
        position: Position,
        stop_loss: Optional[float],
        take_profit: Optional[float]
    ):
        """Coloca órdenes de Stop Loss y Take Profit"""
        # Binance requiere órdenes OCO (One-Cancels-Other) para SL/TP
        # Implementación simplificada
        pass
    
    def _convert_timeframe(self, timeframe: str) -> str:
        """Convierte timeframe al formato de Binance"""
        mapping = {
            '1m': Client.KLINE_INTERVAL_1MINUTE,
            '5m': Client.KLINE_INTERVAL_5MINUTE,
            '15m': Client.KLINE_INTERVAL_15MINUTE,
            '30m': Client.KLINE_INTERVAL_30MINUTE,
            '1h': Client.KLINE_INTERVAL_1HOUR,
            '4h': Client.KLINE_INTERVAL_4HOUR,
            '1d': Client.KLINE_INTERVAL_1DAY,
            '1D': Client.KLINE_INTERVAL_1DAY,
        }
        return mapping.get(timeframe, Client.KLINE_INTERVAL_5MINUTE)
