"""
Trading Controller - Conecta GUI con API Backend
"""

import requests
from typing import Dict, List, Optional
from loguru import logger
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class TradingController(QObject):
    """
    Controlador entre GUI y Sistema de Trading
    Maneja todas las comunicaciones con la API REST
    """
    
    # Señales para actualizar GUI
    balance_updated = pyqtSignal(dict)
    positions_updated = pyqtSignal(list)
    trade_executed = pyqtSignal(dict)
    agents_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, api_url="http://127.0.0.1:8001"):
        super().__init__()
        self.api_url = api_url
        self.is_connected = False
        self.auto_trading = False
        self.current_broker = None
        
        # Timer para actualizar datos
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_all_data)
        
        logger.info("TradingController inicializado")
    
    def check_api_connection(self) -> bool:
        """Verificar si API está disponible"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def connect_broker(self, broker: str, credentials: Dict) -> Dict:
        """
        Conectar broker
        
        Args:
            broker: 'quotex', 'binance', 'binance_futures'
            credentials: dict con api_key, api_secret, etc.
        """
        try:
            logger.info(f"Conectando broker: {broker}")
            logger.info(f"Credenciales: api_key={credentials.get('api_key', '')[:10]}..., testnet={credentials.get('testnet')}")
            
            # Preparar configuración para la API
            config = {
                "broker_type": broker,
                "credentials": credentials,
                "demo_mode": credentials.get('testnet', False)
            }
            
            logger.info(f"Enviando POST a {self.api_url}/api/broker/connect")
            
            response = requests.post(
                f"{self.api_url}/api/broker/connect",
                json=config,
                timeout=30
            )
            
            logger.info(f"Status code: {response.status_code}")
            logger.info(f"Respuesta: {response.text}")
            
            # Verificar status code primero
            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"JSON parseado: {result}")
                    
                    # Verificar success en el resultado
                    if result.get('success') or result.get('status') == 'success':
                        self.is_connected = True
                        self.current_broker = broker
                        logger.success(f"✅ Broker {broker} conectado exitosamente")
                        
                        # Iniciar actualizaciones automáticas
                        self.update_timer.start(2000)  # Cada 2 segundos
                        
                        return {"success": True, "message": result.get('message', 'Conectado')}
                    else:
                        error = result.get('error') or result.get('detail') or 'Error desconocido'
                        logger.error(f"❌ API retornó error: {error}")
                        self.error_occurred.emit(error)
                        return {"success": False, "error": error}
                        
                except ValueError as e:
                    logger.error(f"❌ Error parseando JSON: {e}")
                    logger.error(f"Respuesta raw: {response.text}")
                    return {"success": False, "error": f"Respuesta inválida de la API: {response.text}"}
            else:
                # Status code != 200
                try:
                    error_data = response.json()
                    error = error_data.get('detail') or error_data.get('error') or response.text
                except:
                    error = response.text
                
                logger.error(f"❌ Error HTTP {response.status_code}: {error}")
                self.error_occurred.emit(error)
                return {"success": False, "error": error}
            
        except requests.exceptions.Timeout:
            error_msg = "Timeout: La API no respondió en 30 segundos"
            logger.error(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            return {"success": False, "error": error_msg}
        except requests.exceptions.ConnectionError:
            error_msg = "No se pudo conectar a la API. Verifica que esté corriendo en http://127.0.0.1:8001"
            logger.error(f"❌ {error_msg}")
            self.error_occurred.emit(error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            logger.error(f"❌ {error_msg}")
            logger.exception("Traceback completo:")
            self.error_occurred.emit(error_msg)
            return {"success": False, "error": error_msg}
    
    def disconnect_broker(self) -> Dict:
        """Desconectar broker"""
        try:
            response = requests.post(f"{self.api_url}/broker/disconnect")
            result = response.json()
            
            if result.get('success'):
                self.is_connected = False
                self.current_broker = None
                self.update_timer.stop()
                logger.info("Broker desconectado")
            
            return result
        except Exception as e:
            logger.error(f"Error desconectando: {e}")
            return {"success": False, "error": str(e)}
    
    def get_balance(self) -> Dict:
        """Obtener balance de la cuenta"""
        try:
            response = requests.get(f"{self.api_url}/account/balance", timeout=5)
            balance_data = response.json()
            
            # Emitir señal para actualizar GUI
            self.balance_updated.emit(balance_data)
            
            return balance_data
        except Exception as e:
            logger.error(f"Error obteniendo balance: {e}")
            return {"balance": 0, "currency": "USD", "error": str(e)}
    
    def get_positions(self) -> List[Dict]:
        """Obtener posiciones abiertas"""
        try:
            response = requests.get(f"{self.api_url}/positions", timeout=5)
            data = response.json()
            positions = data.get('positions', [])
            
            # Emitir señal
            self.positions_updated.emit(positions)
            
            return positions
        except Exception as e:
            logger.error(f"Error obteniendo posiciones: {e}")
            return []
    
    def execute_trade(
        self,
        symbol: str,
        side: str,
        amount: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None
    ) -> Dict:
        """
        Ejecutar trade manual
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
            side: 'buy' o 'sell'
            amount: Cantidad a operar
            stop_loss: Precio de stop loss (opcional)
            take_profit: Precio de take profit (opcional)
        """
        try:
            logger.info(f"Ejecutando trade: {side.upper()} {amount} {symbol}")
            
            payload = {
                "symbol": symbol,
                "side": side,
                "amount": amount
            }
            
            if stop_loss:
                payload["stop_loss"] = stop_loss
            if take_profit:
                payload["take_profit"] = take_profit
            
            response = requests.post(
                f"{self.api_url}/trade/execute",
                json=payload,
                timeout=10
            )
            
            result = response.json()
            
            if result.get('success'):
                logger.info(f"✅ Trade ejecutado: {result}")
                self.trade_executed.emit(result)
            else:
                logger.error(f"❌ Error en trade: {result.get('error')}")
                self.error_occurred.emit(result.get('error', 'Error ejecutando trade'))
            
            return result
            
        except Exception as e:
            error_msg = f"Error ejecutando trade: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return {"success": False, "error": str(e)}
    
    def close_position(self, position_id: str) -> Dict:
        """Cerrar posición específica"""
        try:
            response = requests.post(
                f"{self.api_url}/position/close/{position_id}",
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error cerrando posición: {e}")
            return {"success": False, "error": str(e)}
    
    def start_auto_trading(self, config: Dict) -> Dict:
        """
        Iniciar trading automático con IA
        
        Args:
            config: {
                'use_multi_agent': bool,
                'use_ppo': bool,
                'use_sentiment': bool,
                'symbols': list,
                'max_positions': int,
                'risk_per_trade': float
            }
        """
        try:
            logger.info("🤖 Iniciando trading automático")
            
            response = requests.post(
                f"{self.api_url}/trading/auto/start",
                json=config,
                timeout=10
            )
            
            result = response.json()
            
            if result.get('success'):
                self.auto_trading = True
                logger.info("✅ Trading automático iniciado")
            else:
                logger.error(f"❌ Error iniciando auto trading: {result.get('error')}")
                self.error_occurred.emit(result.get('error', 'Error iniciando auto trading'))
            
            return result
            
        except Exception as e:
            error_msg = f"Error iniciando auto trading: {str(e)}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return {"success": False, "error": str(e)}
    
    def stop_auto_trading(self) -> Dict:
        """Detener trading automático"""
        try:
            logger.info("Deteniendo trading automático")
            
            response = requests.post(
                f"{self.api_url}/trading/auto/stop",
                timeout=10
            )
            
            result = response.json()
            
            if result.get('success'):
                self.auto_trading = False
                logger.info("✅ Trading automático detenido")
            
            return result
            
        except Exception as e:
            logger.error(f"Error deteniendo auto trading: {e}")
            return {"success": False, "error": str(e)}
    
    def get_ai_agents_status(self) -> Dict:
        """Obtener estado de los 6 agentes de IA"""
        try:
            response = requests.get(f"{self.api_url}/ai/agents/status", timeout=5)
            agents_data = response.json()
            
            # Emitir señal
            self.agents_updated.emit(agents_data)
            
            return agents_data
        except Exception as e:
            logger.error(f"Error obteniendo estado de agentes: {e}")
            return {"agents": []}
    
    def get_market_data(self, symbol: str) -> Dict:
        """Obtener datos de mercado en tiempo real"""
        try:
            response = requests.get(
                f"{self.api_url}/market/data/{symbol}",
                timeout=5
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo datos de mercado: {e}")
            return {}
    
    def get_sentiment_analysis(self, symbol: str) -> Dict:
        """Obtener análisis de sentimiento"""
        try:
            response = requests.get(
                f"{self.api_url}/sentiment/{symbol}",
                timeout=5
            )
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo sentimiento: {e}")
            return {"sentiment": 0, "classification": "NEUTRAL"}
    
    def get_trading_history(self, limit: int = 50) -> List[Dict]:
        """Obtener historial de trades"""
        try:
            response = requests.get(
                f"{self.api_url}/trades/history?limit={limit}",
                timeout=5
            )
            data = response.json()
            return data.get('trades', [])
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []
    
    def get_performance_metrics(self) -> Dict:
        """Obtener métricas de performance"""
        try:
            response = requests.get(f"{self.api_url}/analytics/performance", timeout=5)
            return response.json()
        except Exception as e:
            logger.error(f"Error obteniendo métricas: {e}")
            return {}
    
    def update_all_data(self):
        """Actualizar todos los datos (llamado por timer)"""
        if not self.is_connected:
            return
        
        try:
            # Actualizar balance
            self.get_balance()
            
            # Actualizar posiciones
            self.get_positions()
            
            # Actualizar agentes si auto trading está activo
            if self.auto_trading:
                self.get_ai_agents_status()
                
        except Exception as e:
            logger.error(f"Error actualizando datos: {e}")
