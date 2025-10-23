"""
Binance Futures Broker
Trading de futuros con apalancamiento en Binance
Compatible con: https://demo.binance.com/en/futures/BTCUSDT
"""

from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException
import asyncio
from typing import Dict, List, Optional
from loguru import logger
from datetime import datetime
import numpy as np


class BinanceFuturesBroker:
    """
    Broker para Binance Futures (USDT-M)
    Soporta: Apalancamiento, Long/Short, Hedging
    """
    
    def __init__(self, credentials: Dict):
        """
        Inicializar Binance Futures
        
        Args:
            credentials: {
                'api_key': str,
                'api_secret': str,
                'testnet': bool (True para demo.binance.com)
            }
        """
        self.api_key = credentials.get('api_key')
        self.api_secret = credentials.get('api_secret')
        self.testnet = credentials.get('testnet', True)
        
        # URLs
        if self.testnet:
            self.base_url = 'https://testnet.binancefuture.com'
        else:
            self.base_url = 'https://fapi.binance.com'
        
        # Cliente
        self.client = None
        self.connected = False
        
        # Estado
        self.positions = {}
        self.orders = {}
        self.balance = 0.0
        self.leverage = 10  # Apalancamiento por defecto
        
        logger.info(f"Binance Futures inicializado (Testnet: {self.testnet})")
    
    async def connect(self) -> bool:
        """Conectar con Binance Futures"""
        try:
            logger.info("Conectando a Binance Futures...")
            
            # Crear cliente
            self.client = Client(
                self.api_key,
                self.api_secret,
                testnet=self.testnet
            )
            
            # Cambiar a Futures
            self.client.API_URL = self.base_url
            
            # Verificar conexión
            account_info = self.client.futures_account()
            
            if account_info:
                self.connected = True
                self.balance = float(account_info['totalWalletBalance'])
                
                logger.info(f"✅ Conectado a Binance Futures")
                logger.info(f"Balance: ${self.balance:.2f} USDT")
                
                # Configurar modo de posición (Hedge Mode)
                try:
                    self.client.futures_change_position_mode(dualSidePosition=True)
                    logger.info("Modo Hedge activado")
                except:
                    logger.warning("Modo Hedge ya estaba activado")
                
                return True
            else:
                logger.error("No se pudo obtener información de la cuenta")
                return False
                
        except BinanceAPIException as e:
            logger.error(f"Error de API Binance: {e}")
            return False
        except Exception as e:
            logger.error(f"Error conectando a Binance Futures: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Verificar si está conectado"""
        return self.connected
    
    async def get_account_info(self):
        """Obtener información de la cuenta"""
        try:
            if not self.connected:
                raise Exception("No conectado a Binance Futures")
            
            account = self.client.futures_account()
            
            return {
                'balance': float(account['totalWalletBalance']),
                'equity': float(account['totalMarginBalance']),
                'margin': float(account['totalInitialMargin']),
                'free_margin': float(account['availableBalance']),
                'margin_level': float(account['totalMarginBalance']) / float(account['totalInitialMargin']) * 100 if float(account['totalInitialMargin']) > 0 else 0,
                'unrealized_pnl': float(account['totalUnrealizedProfit'])
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo info de cuenta: {e}")
            return None
    
    async def get_price(self, symbol: str) -> Dict:
        """
        Obtener precio actual
        
        Args:
            symbol: Símbolo (ej: 'BTCUSDT', 'ETHUSDT')
        """
        try:
            if not self.connected:
                raise Exception("No conectado")
            
            # Asegurar formato correcto
            symbol = symbol.replace('/', '').upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            # Obtener ticker
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            
            # Obtener book
            book = self.client.futures_order_book(symbol=symbol, limit=5)
            
            bid = float(book['bids'][0][0]) if book['bids'] else float(ticker['price'])
            ask = float(book['asks'][0][0]) if book['asks'] else float(ticker['price'])
            
            return {
                'symbol': symbol,
                'bid': bid,
                'ask': ask,
                'last': float(ticker['price']),
                'spread': ask - bid,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo precio: {e}")
            return {'symbol': symbol, 'bid': 0, 'ask': 0, 'last': 0, 'spread': 0}
    
    async def set_leverage(self, symbol: str, leverage: int):
        """
        Configurar apalancamiento
        
        Args:
            symbol: Símbolo
            leverage: Apalancamiento (1-125)
        """
        try:
            symbol = symbol.replace('/', '').upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            # Validar apalancamiento
            leverage = max(1, min(125, leverage))
            
            result = self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
            
            self.leverage = leverage
            logger.info(f"Apalancamiento configurado: {leverage}x para {symbol}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error configurando apalancamiento: {e}")
            return False
    
    async def place_order(self, symbol: str, side: str, quantity: float,
                         order_type: str = 'MARKET', price: float = None,
                         stop_loss: float = None, take_profit: float = None,
                         leverage: int = None) -> Dict:
        """
        Ejecutar orden en Binance Futures
        
        Args:
            symbol: Símbolo (ej: 'BTCUSDT')
            side: 'BUY' o 'SELL'
            quantity: Cantidad en USDT (no en BTC)
            order_type: 'MARKET', 'LIMIT'
            price: Precio límite (para LIMIT)
            stop_loss: Precio de stop loss
            take_profit: Precio de take profit
            leverage: Apalancamiento (opcional)
        """
        try:
            if not self.connected:
                raise Exception("No conectado")
            
            # Formatear símbolo
            symbol = symbol.replace('/', '').upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            # Configurar apalancamiento
            if leverage:
                await self.set_leverage(symbol, leverage)
            
            # Obtener precio actual
            current_price = await self.get_price(symbol)
            price_value = current_price['last']
            
            # Calcular cantidad en contratos
            # Cantidad = USDT / Precio * Apalancamiento
            contracts = (quantity / price_value) * self.leverage
            
            # Obtener precisión del símbolo
            exchange_info = self.client.futures_exchange_info()
            symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == symbol), None)
            
            if symbol_info:
                quantity_precision = symbol_info['quantityPrecision']
                contracts = round(contracts, quantity_precision)
            
            # Crear orden principal
            order_params = {
                'symbol': symbol,
                'side': SIDE_BUY if side.upper() == 'BUY' else SIDE_SELL,
                'type': ORDER_TYPE_MARKET if order_type.upper() == 'MARKET' else ORDER_TYPE_LIMIT,
                'quantity': contracts,
                'positionSide': 'LONG' if side.upper() == 'BUY' else 'SHORT'
            }
            
            if order_type.upper() == 'LIMIT' and price:
                order_params['price'] = price
                order_params['timeInForce'] = TIME_IN_FORCE_GTC
            
            # Ejecutar orden
            order = self.client.futures_create_order(**order_params)
            
            logger.info(f"✅ Orden ejecutada: {side} {contracts} {symbol} @ {price_value}")
            
            # Crear órdenes de Stop Loss y Take Profit
            if stop_loss or take_profit:
                await self._create_sl_tp_orders(symbol, side, contracts, stop_loss, take_profit)
            
            return {
                'order_id': order['orderId'],
                'symbol': symbol,
                'side': side,
                'quantity': contracts,
                'price': float(order.get('avgPrice', price_value)),
                'status': order['status'],
                'leverage': self.leverage,
                'timestamp': datetime.now().isoformat()
            }
            
        except BinanceAPIException as e:
            logger.error(f"Error de API: {e}")
            return {'error': str(e)}
        except Exception as e:
            logger.error(f"Error ejecutando orden: {e}")
            return {'error': str(e)}
    
    async def _create_sl_tp_orders(self, symbol: str, side: str, quantity: float,
                                   stop_loss: float = None, take_profit: float = None):
        """Crear órdenes de Stop Loss y Take Profit"""
        try:
            position_side = 'LONG' if side.upper() == 'BUY' else 'SHORT'
            close_side = SIDE_SELL if side.upper() == 'BUY' else SIDE_BUY
            
            # Stop Loss
            if stop_loss:
                sl_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=close_side,
                    type=FUTURE_ORDER_TYPE_STOP_MARKET,
                    quantity=quantity,
                    stopPrice=stop_loss,
                    positionSide=position_side,
                    closePosition=True
                )
                logger.info(f"Stop Loss creado: {stop_loss}")
            
            # Take Profit
            if take_profit:
                tp_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=close_side,
                    type=FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET,
                    quantity=quantity,
                    stopPrice=take_profit,
                    positionSide=position_side,
                    closePosition=True
                )
                logger.info(f"Take Profit creado: {take_profit}")
                
        except Exception as e:
            logger.error(f"Error creando SL/TP: {e}")
    
    async def get_open_positions(self) -> List[Dict]:
        """Obtener posiciones abiertas"""
        try:
            if not self.connected:
                return []
            
            positions = self.client.futures_position_information()
            
            open_positions = []
            
            for pos in positions:
                position_amt = float(pos['positionAmt'])
                
                if position_amt != 0:
                    entry_price = float(pos['entryPrice'])
                    mark_price = float(pos['markPrice'])
                    unrealized_pnl = float(pos['unRealizedProfit'])
                    
                    open_positions.append({
                        'symbol': pos['symbol'],
                        'side': 'LONG' if position_amt > 0 else 'SHORT',
                        'quantity': abs(position_amt),
                        'entry_price': entry_price,
                        'current_price': mark_price,
                        'unrealized_pnl': unrealized_pnl,
                        'unrealized_pnl_percent': (unrealized_pnl / (entry_price * abs(position_amt)) * 100) if entry_price > 0 else 0,
                        'leverage': int(pos['leverage']),
                        'liquidation_price': float(pos['liquidationPrice'])
                    })
            
            return open_positions
            
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {e}")
            return []
    
    async def close_position(self, symbol: str, position_side: str = None) -> bool:
        """
        Cerrar posición
        
        Args:
            symbol: Símbolo
            position_side: 'LONG' o 'SHORT' (None para cerrar ambas)
        """
        try:
            if not self.connected:
                return False
            
            symbol = symbol.replace('/', '').upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            # Obtener posición actual
            positions = self.client.futures_position_information(symbol=symbol)
            
            for pos in positions:
                position_amt = float(pos['positionAmt'])
                
                if position_amt == 0:
                    continue
                
                pos_side = 'LONG' if position_amt > 0 else 'SHORT'
                
                # Filtrar por position_side si se especifica
                if position_side and pos_side != position_side.upper():
                    continue
                
                # Crear orden de cierre
                close_side = SIDE_SELL if position_amt > 0 else SIDE_BUY
                
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=close_side,
                    type=ORDER_TYPE_MARKET,
                    quantity=abs(position_amt),
                    positionSide=pos_side,
                    reduceOnly=True
                )
                
                logger.info(f"✅ Posición cerrada: {symbol} {pos_side}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cerrando posición: {e}")
            return False
    
    async def get_historical_data(self, symbol: str, interval: str = '1m', limit: int = 500) -> List[Dict]:
        """
        Obtener datos históricos
        
        Args:
            symbol: Símbolo
            interval: '1m', '5m', '15m', '1h', '4h', '1d'
            limit: Número de velas (max 1500)
        """
        try:
            symbol = symbol.replace('/', '').upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            klines = self.client.futures_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            historical = []
            
            for k in klines:
                historical.append({
                    'timestamp': datetime.fromtimestamp(k[0] / 1000).isoformat(),
                    'open': float(k[1]),
                    'high': float(k[2]),
                    'low': float(k[3]),
                    'close': float(k[4]),
                    'volume': float(k[5])
                })
            
            return historical
            
        except Exception as e:
            logger.error(f"Error obteniendo datos históricos: {e}")
            return []
    
    async def get_funding_rate(self, symbol: str) -> Dict:
        """Obtener funding rate actual"""
        try:
            symbol = symbol.replace('/', '').upper()
            if not symbol.endswith('USDT'):
                symbol += 'USDT'
            
            funding = self.client.futures_funding_rate(symbol=symbol, limit=1)
            
            if funding:
                return {
                    'symbol': symbol,
                    'funding_rate': float(funding[0]['fundingRate']),
                    'funding_time': datetime.fromtimestamp(int(funding[0]['fundingTime']) / 1000).isoformat()
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error obteniendo funding rate: {e}")
            return {}
    
    def __del__(self):
        """Destructor"""
        self.connected = False
