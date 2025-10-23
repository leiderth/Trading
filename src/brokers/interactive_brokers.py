"""
Interactive Brokers Broker Implementation
Conecta con Interactive Brokers TWS/Gateway usando ib_insync
"""

from ib_insync import IB, Stock, Forex, Future, Option, MarketOrder, LimitOrder, StopOrder, util
from src.brokers.base_broker import BaseBroker
from loguru import logger
import asyncio
from datetime import datetime
from typing import Dict, List, Optional


class InteractiveBrokersBroker(BaseBroker):
    """
    Broker para Interactive Brokers
    Soporta: Acciones, Forex, Futuros, Opciones
    """
    
    def __init__(self, host: str = '127.0.0.1', port: int = 7497, client_id: int = 1):
        """
        Inicializar Interactive Brokers
        
        Args:
            host: IP del TWS/Gateway (default: localhost)
            port: Puerto (7497 para TWS paper, 7496 para TWS live, 4002 para Gateway paper, 4001 para Gateway live)
            client_id: ID del cliente (único por conexión)
        """
        super().__init__()
        self.host = host
        self.port = port
        self.client_id = client_id
        self.ib = IB()
        self.connected = False
        self.positions_cache = {}
        self.account_info = {}
        
        logger.info(f"Interactive Brokers inicializado: {host}:{port}")
    
    def connect(self) -> bool:
        """Conectar con TWS/Gateway"""
        try:
            logger.info(f"Conectando a IB TWS/Gateway en {self.host}:{self.port}...")
            
            # Conectar
            self.ib.connect(self.host, self.port, clientId=self.client_id)
            
            # Verificar conexión
            if self.ib.isConnected():
                self.connected = True
                
                # Obtener información de la cuenta
                accounts = self.ib.managedAccounts()
                if accounts:
                    self.account = accounts[0]
                    logger.info(f"Conectado a IB. Cuenta: {self.account}")
                    
                    # Suscribirse a actualizaciones de cuenta
                    self.ib.accountSummary()
                    
                    return True
                else:
                    logger.error("No se encontraron cuentas")
                    return False
            else:
                logger.error("No se pudo conectar a IB")
                return False
                
        except Exception as e:
            logger.error(f"Error conectando a IB: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Desconectar de TWS/Gateway"""
        try:
            if self.ib.isConnected():
                self.ib.disconnect()
                self.connected = False
                logger.info("Desconectado de IB")
        except Exception as e:
            logger.error(f"Error desconectando de IB: {e}")
    
    def is_connected(self) -> bool:
        """Verificar si está conectado"""
        return self.connected and self.ib.isConnected()
    
    def get_balance(self) -> Dict:
        """Obtener balance de la cuenta"""
        try:
            if not self.is_connected():
                raise Exception("No conectado a IB")
            
            # Obtener resumen de cuenta
            account_values = self.ib.accountSummary()
            
            balance_info = {
                'balance': 0.0,
                'equity': 0.0,
                'margin_available': 0.0,
                'margin_used': 0.0
            }
            
            for item in account_values:
                if item.tag == 'TotalCashValue':
                    balance_info['balance'] = float(item.value)
                elif item.tag == 'NetLiquidation':
                    balance_info['equity'] = float(item.value)
                elif item.tag == 'AvailableFunds':
                    balance_info['margin_available'] = float(item.value)
                elif item.tag == 'MaintMarginReq':
                    balance_info['margin_used'] = float(item.value)
            
            logger.info(f"Balance IB: {balance_info}")
            return balance_info
            
        except Exception as e:
            logger.error(f"Error obteniendo balance de IB: {e}")
            return {'balance': 0.0, 'equity': 0.0, 'margin_available': 0.0, 'margin_used': 0.0}
    
    def get_price(self, symbol: str) -> Dict:
        """
        Obtener precio actual de un símbolo
        
        Args:
            symbol: Símbolo (ej: 'AAPL', 'EUR.USD', 'ES')
        """
        try:
            if not self.is_connected():
                raise Exception("No conectado a IB")
            
            # Crear contrato según el tipo de símbolo
            contract = self._create_contract(symbol)
            
            # Solicitar datos de mercado
            self.ib.qualifyContracts(contract)
            ticker = self.ib.reqMktData(contract, '', False, False)
            
            # Esperar datos
            self.ib.sleep(1)
            
            # Obtener precios
            bid = ticker.bid if ticker.bid and ticker.bid > 0 else 0.0
            ask = ticker.ask if ticker.ask and ticker.ask > 0 else 0.0
            last = ticker.last if ticker.last and ticker.last > 0 else 0.0
            
            # Si no hay bid/ask, usar last
            if bid == 0 and ask == 0 and last > 0:
                bid = last
                ask = last
            
            price_info = {
                'symbol': symbol,
                'bid': bid,
                'ask': ask,
                'last': last,
                'spread': ask - bid if ask > bid else 0.0,
                'timestamp': datetime.now().isoformat()
            }
            
            # Cancelar suscripción
            self.ib.cancelMktData(contract)
            
            logger.info(f"Precio IB {symbol}: Bid={bid}, Ask={ask}")
            return price_info
            
        except Exception as e:
            logger.error(f"Error obteniendo precio de IB: {e}")
            return {'symbol': symbol, 'bid': 0.0, 'ask': 0.0, 'last': 0.0, 'spread': 0.0}
    
    def place_order(self, symbol: str, side: str, quantity: float, 
                   order_type: str = 'market', price: float = None,
                   stop_loss: float = None, take_profit: float = None) -> Dict:
        """
        Ejecutar orden en IB
        
        Args:
            symbol: Símbolo (ej: 'AAPL', 'EUR.USD')
            side: 'BUY' o 'SELL'
            quantity: Cantidad (acciones, contratos, lotes)
            order_type: 'market', 'limit', 'stop'
            price: Precio límite (para limit orders)
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
        """
        try:
            if not self.is_connected():
                raise Exception("No conectado a IB")
            
            # Crear contrato
            contract = self._create_contract(symbol)
            self.ib.qualifyContracts(contract)
            
            # Crear orden
            action = 'BUY' if side.upper() == 'BUY' else 'SELL'
            
            if order_type.lower() == 'market':
                order = MarketOrder(action, quantity)
            elif order_type.lower() == 'limit':
                if not price:
                    raise ValueError("Precio requerido para limit order")
                order = LimitOrder(action, quantity, price)
            elif order_type.lower() == 'stop':
                if not price:
                    raise ValueError("Precio requerido para stop order")
                order = StopOrder(action, quantity, price)
            else:
                raise ValueError(f"Tipo de orden no soportado: {order_type}")
            
            # Ejecutar orden
            trade = self.ib.placeOrder(contract, order)
            
            # Esperar confirmación
            self.ib.sleep(2)
            
            # Información de la orden
            order_info = {
                'order_id': trade.order.orderId,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'order_type': order_type,
                'status': trade.orderStatus.status,
                'filled': trade.orderStatus.filled,
                'remaining': trade.orderStatus.remaining,
                'avg_fill_price': trade.orderStatus.avgFillPrice,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Orden IB ejecutada: {order_info}")
            
            # Si hay stop loss o take profit, crear órdenes bracket
            if stop_loss or take_profit:
                self._place_bracket_orders(contract, trade.order.orderId, side, quantity, stop_loss, take_profit)
            
            return order_info
            
        except Exception as e:
            logger.error(f"Error ejecutando orden en IB: {e}")
            return {'error': str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Obtener posiciones abiertas"""
        try:
            if not self.is_connected():
                raise Exception("No conectado a IB")
            
            positions = []
            ib_positions = self.ib.positions()
            
            for pos in ib_positions:
                # Obtener precio actual
                ticker = self.ib.reqMktData(pos.contract, '', False, False)
                self.ib.sleep(0.5)
                
                current_price = ticker.last if ticker.last > 0 else ticker.close
                entry_price = pos.avgCost / abs(pos.position) if pos.position != 0 else 0
                
                # Calcular P&L
                if pos.position > 0:  # Long
                    pnl = (current_price - entry_price) * pos.position
                else:  # Short
                    pnl = (entry_price - current_price) * abs(pos.position)
                
                position_info = {
                    'symbol': pos.contract.symbol,
                    'side': 'LONG' if pos.position > 0 else 'SHORT',
                    'quantity': abs(pos.position),
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'pnl': pnl,
                    'pnl_percent': (pnl / (entry_price * abs(pos.position)) * 100) if entry_price > 0 else 0,
                    'account': pos.account
                }
                
                positions.append(position_info)
                
                # Cancelar suscripción
                self.ib.cancelMktData(pos.contract)
            
            logger.info(f"Posiciones IB: {len(positions)}")
            return positions
            
        except Exception as e:
            logger.error(f"Error obteniendo posiciones de IB: {e}")
            return []
    
    def close_position(self, symbol: str) -> bool:
        """Cerrar posición"""
        try:
            if not self.is_connected():
                raise Exception("No conectado a IB")
            
            # Buscar posición
            ib_positions = self.ib.positions()
            
            for pos in ib_positions:
                if pos.contract.symbol == symbol:
                    # Crear orden opuesta
                    action = 'SELL' if pos.position > 0 else 'BUY'
                    quantity = abs(pos.position)
                    
                    order = MarketOrder(action, quantity)
                    trade = self.ib.placeOrder(pos.contract, order)
                    
                    self.ib.sleep(2)
                    
                    logger.info(f"Posición cerrada: {symbol}")
                    return True
            
            logger.warning(f"No se encontró posición para {symbol}")
            return False
            
        except Exception as e:
            logger.error(f"Error cerrando posición en IB: {e}")
            return False
    
    def _create_contract(self, symbol: str):
        """
        Crear contrato IB según el símbolo
        
        Formatos soportados:
        - Acciones: 'AAPL', 'TSLA', 'MSFT'
        - Forex: 'EUR.USD', 'GBP.USD'
        - Futuros: 'ES', 'NQ', 'CL'
        """
        # Forex (contiene punto)
        if '.' in symbol:
            base, quote = symbol.split('.')
            return Forex(base + quote)
        
        # Futuros (símbolos cortos conocidos)
        futures_symbols = ['ES', 'NQ', 'YM', 'RTY', 'CL', 'GC', 'SI', 'NG']
        if symbol.upper() in futures_symbols:
            return Future(symbol.upper(), exchange='GLOBEX')
        
        # Por defecto: Acción
        return Stock(symbol.upper(), 'SMART', 'USD')
    
    def _place_bracket_orders(self, contract, parent_order_id: int, side: str, 
                             quantity: float, stop_loss: float = None, take_profit: float = None):
        """Crear órdenes bracket (SL/TP)"""
        try:
            # Stop Loss
            if stop_loss:
                sl_action = 'SELL' if side.upper() == 'BUY' else 'BUY'
                sl_order = StopOrder(sl_action, quantity, stop_loss)
                sl_order.parentId = parent_order_id
                sl_order.transmit = False if take_profit else True
                self.ib.placeOrder(contract, sl_order)
                logger.info(f"Stop Loss colocado: {stop_loss}")
            
            # Take Profit
            if take_profit:
                tp_action = 'SELL' if side.upper() == 'BUY' else 'BUY'
                tp_order = LimitOrder(tp_action, quantity, take_profit)
                tp_order.parentId = parent_order_id
                tp_order.transmit = True
                self.ib.placeOrder(contract, tp_order)
                logger.info(f"Take Profit colocado: {take_profit}")
                
        except Exception as e:
            logger.error(f"Error colocando bracket orders: {e}")
    
    def get_historical_data(self, symbol: str, timeframe: str = '1D', bars: int = 100) -> List[Dict]:
        """Obtener datos históricos"""
        try:
            if not self.is_connected():
                raise Exception("No conectado a IB")
            
            contract = self._create_contract(symbol)
            self.ib.qualifyContracts(contract)
            
            # Solicitar datos históricos
            bars_data = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=f'{bars} D',
                barSizeSetting=timeframe,
                whatToShow='TRADES',
                useRTH=True
            )
            
            historical = []
            for bar in bars_data:
                historical.append({
                    'timestamp': bar.date.isoformat(),
                    'open': bar.open,
                    'high': bar.high,
                    'low': bar.low,
                    'close': bar.close,
                    'volume': bar.volume
                })
            
            logger.info(f"Datos históricos IB: {len(historical)} barras")
            return historical
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos de IB: {e}")
            return []
    
    def __del__(self):
        """Destructor: desconectar al eliminar objeto"""
        self.disconnect()
