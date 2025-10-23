"""
API REST para control del sistema de trading
Permite comunicacion entre la GUI y el sistema
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from loguru import logger

from ..core.trading_system import TradingSystem
from ..config.settings import settings


# Modelos Pydantic
class BrokerConfig(BaseModel):
    broker_type: str
    credentials: Dict
    demo_mode: bool = True


class TradingConfig(BaseModel):
    symbol: str
    timeframe: str
    auto_trading: bool = False
    max_risk: float = 0.02
    max_positions: int = 3


class TradeRequest(BaseModel):
    symbol: str
    side: str  # 'buy' or 'sell'
    quantity: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None


class SystemCommand(BaseModel):
    command: str  # 'start', 'stop', 'pause', 'resume'
    params: Optional[Dict] = None


# API FastAPI
app = FastAPI(
    title="Trading System API",
    description="API para control del sistema de trading algoritmico",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estado global
trading_system: Optional[TradingSystem] = None
websocket_clients: List[WebSocket] = []


# ============================================
# ENDPOINTS DE SISTEMA
# ============================================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "name": "Trading System API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "system_initialized": trading_system is not None
    }


@app.get("/api/system/status")
async def get_system_status():
    """Obtiene estado del sistema"""
    if not trading_system:
        return {
            "initialized": False,
            "running": False,
            "message": "Sistema no inicializado"
        }
    
    status = trading_system.get_status()
    return status


@app.post("/api/system/initialize")
async def initialize_system(config: TradingConfig):
    """Inicializa el sistema de trading"""
    global trading_system
    
    try:
        trading_system = TradingSystem(config={
            'broker': 'quotex',  # Por defecto
            'symbol': config.symbol,
            'timeframe': config.timeframe,
            'auto_trading': config.auto_trading,
            'close_positions_on_stop': True
        })
        
        initialized = await trading_system.initialize()
        
        if initialized:
            await broadcast_message({
                'type': 'system_initialized',
                'data': {'status': 'success'}
            })
            return {"status": "success", "message": "Sistema inicializado"}
        else:
            raise HTTPException(status_code=500, detail="Error inicializando sistema")
            
    except Exception as e:
        logger.error(f"Error inicializando sistema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/system/start")
async def start_system():
    """Inicia el sistema de trading"""
    if not trading_system or not trading_system.is_initialized:
        raise HTTPException(status_code=400, detail="Sistema no inicializado")
    
    try:
        # Iniciar en background
        asyncio.create_task(trading_system.start())
        
        await broadcast_message({
            'type': 'system_started',
            'data': {'status': 'running'}
        })
        
        return {"status": "success", "message": "Sistema iniciado"}
    except Exception as e:
        logger.error(f"Error iniciando sistema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/system/stop")
async def stop_system():
    """Detiene el sistema de trading"""
    if not trading_system:
        raise HTTPException(status_code=400, detail="Sistema no inicializado")
    
    try:
        await trading_system.stop()
        
        await broadcast_message({
            'type': 'system_stopped',
            'data': {'status': 'stopped'}
        })
        
        return {"status": "success", "message": "Sistema detenido"}
    except Exception as e:
        logger.error(f"Error deteniendo sistema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS DE BROKER
# ============================================

@app.post("/api/broker/connect")
async def connect_broker(config: BrokerConfig):
    """Conecta con un broker"""
    try:
        logger.info(f"🔌 Intentando conectar a {config.broker_type}")
        logger.info(f"Credenciales: {list(config.credentials.keys())}")
        logger.info(f"Demo mode: {config.demo_mode}")
        
        # Importar brokers
        from ..brokers.binance_broker import BinanceBroker
        from ..brokers.binance_futures_broker import BinanceFuturesBroker
        
        # Crear instancia del broker
        if config.broker_type == 'binance':
            broker_config = {
                'api_key': config.credentials.get('api_key'),
                'api_secret': config.credentials.get('api_secret'),
                'testnet': config.credentials.get('testnet', False)
            }
            broker = BinanceBroker(broker_config)
        elif config.broker_type == 'binance_futures':
            broker_config = {
                'api_key': config.credentials.get('api_key'),
                'api_secret': config.credentials.get('api_secret'),
                'testnet': config.credentials.get('testnet', False)
            }
            broker = BinanceFuturesBroker(broker_config)
        else:
            raise HTTPException(status_code=400, detail=f"Broker '{config.broker_type}' no soportado")
        
        logger.info(f"Broker creado, intentando conectar...")
        
        # Conectar (método async)
        connected = await broker.connect()
        
        if connected:
            logger.success(f"✅ Conectado exitosamente a {config.broker_type}")
            
            # Si hay trading_system, asignar broker
            global trading_system
            if trading_system:
                trading_system.broker = broker
                logger.info("Broker asignado al trading system")
            
            return {
                "success": True,
                "status": "success",
                "message": f"Conectado a {config.broker_type}",
                "broker": config.broker_type
            }
        else:
            logger.error("❌ Broker retornó False al conectar")
            raise HTTPException(status_code=500, detail="El broker no pudo establecer conexión")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error conectando broker: {e}")
        logger.exception("Traceback completo:")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/broker/account")
async def get_account_info():
    """Obtiene informacion de la cuenta"""
    if not trading_system or not trading_system.broker:
        raise HTTPException(status_code=400, detail="Broker no conectado")
    
    try:
        account_info = await trading_system.broker.get_account_info()
        return {
            "balance": account_info.balance,
            "equity": account_info.equity,
            "margin": account_info.margin,
            "free_margin": account_info.free_margin,
            "margin_level": account_info.margin_level,
            "unrealized_pnl": account_info.unrealized_pnl
        }
    except Exception as e:
        logger.error(f"Error obteniendo info de cuenta: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/broker/positions")
async def get_positions():
    """Obtiene posiciones abiertas"""
    if not trading_system or not trading_system.broker:
        raise HTTPException(status_code=400, detail="Broker no conectado")
    
    try:
        positions = await trading_system.broker.get_open_positions()
        return {
            "positions": [
                {
                    "id": pos.id,
                    "symbol": pos.symbol,
                    "side": pos.side.value,
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": pos.current_price,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "unrealized_pnl_percent": pos.unrealized_pnl_percent,
                    "stop_loss": pos.stop_loss,
                    "take_profit": pos.take_profit,
                    "opened_at": pos.opened_at.isoformat()
                }
                for pos in positions
            ]
        }
    except Exception as e:
        logger.error(f"Error obteniendo posiciones: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS DE TRADING
# ============================================

@app.post("/api/trade/open")
async def open_trade(trade: TradeRequest):
    """Abre una nueva operacion"""
    if not trading_system or not trading_system.broker:
        raise HTTPException(status_code=400, detail="Sistema no listo")
    
    try:
        from ..brokers.base_broker import OrderSide
        
        side = OrderSide.BUY if trade.side.lower() == 'buy' else OrderSide.SELL
        
        order = await trading_system.broker.place_market_order(
            symbol=trade.symbol,
            side=side,
            quantity=trade.quantity,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit
        )
        
        await broadcast_message({
            'type': 'trade_opened',
            'data': {
                'order_id': order.id,
                'symbol': trade.symbol,
                'side': trade.side,
                'quantity': trade.quantity
            }
        })
        
        return {
            "status": "success",
            "order_id": order.id,
            "message": "Operacion abierta"
        }
    except Exception as e:
        logger.error(f"Error abriendo trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/trade/close/{position_id}")
async def close_trade(position_id: str):
    """Cierra una posicion"""
    if not trading_system or not trading_system.broker:
        raise HTTPException(status_code=400, detail="Sistema no listo")
    
    try:
        await trading_system.broker.close_position(position_id)
        
        await broadcast_message({
            'type': 'trade_closed',
            'data': {'position_id': position_id}
        })
        
        return {"status": "success", "message": "Posicion cerrada"}
    except Exception as e:
        logger.error(f"Error cerrando trade: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS DE METRICAS
# ============================================

@app.get("/api/metrics/performance")
async def get_performance_metrics():
    """Obtiene metricas de performance"""
    if not trading_system or not trading_system.performance_tracker:
        raise HTTPException(status_code=400, detail="Sistema no inicializado")
    
    try:
        metrics = trading_system.performance_tracker.calculate_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error obteniendo metricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/equity-curve")
async def get_equity_curve():
    """Obtiene curva de equity"""
    if not trading_system or not trading_system.performance_tracker:
        raise HTTPException(status_code=400, detail="Sistema no inicializado")
    
    try:
        df = trading_system.performance_tracker.get_equity_curve()
        return {
            "timestamps": df['timestamp'].dt.isoformat().tolist(),
            "equity": df['equity'].tolist(),
            "balance": df['balance'].tolist()
        }
    except Exception as e:
        logger.error(f"Error obteniendo equity curve: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/trades")
async def get_trades_history():
    """Obtiene historial de trades"""
    if not trading_system or not trading_system.performance_tracker:
        raise HTTPException(status_code=400, detail="Sistema no inicializado")
    
    try:
        df = trading_system.performance_tracker.get_trades_dataframe()
        
        if df.empty:
            return {"trades": []}
        
        trades = df.to_dict('records')
        
        # Convertir datetime a string
        for trade in trades:
            if 'opened_at' in trade:
                trade['opened_at'] = trade['opened_at'].isoformat()
            if 'closed_at' in trade:
                trade['closed_at'] = trade['closed_at'].isoformat()
        
        return {"trades": trades}
    except Exception as e:
        logger.error(f"Error obteniendo trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS DE DATOS DE MERCADO
# ============================================

@app.get("/api/market/data/{symbol}")
async def get_market_data(symbol: str, timeframe: str = "5m", bars: int = 200):
    """Obtiene datos de mercado"""
    if not trading_system or not trading_system.broker:
        raise HTTPException(status_code=400, detail="Broker no conectado")
    
    try:
        df = await trading_system.broker.get_live_data(symbol, timeframe, bars)
        
        if df.empty:
            return {"data": []}
        
        return {
            "data": df.to_dict('records')
        }
    except Exception as e:
        logger.error(f"Error obteniendo datos de mercado: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/price/{symbol}")
async def get_current_price(symbol: str):
    """Obtiene precio actual"""
    if not trading_system or not trading_system.broker:
        raise HTTPException(status_code=400, detail="Broker no conectado")
    
    try:
        bid, ask = await trading_system.broker.get_current_price(symbol)
        return {
            "symbol": symbol,
            "bid": bid,
            "ask": ask,
            "spread": ask - bid,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error obteniendo precio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# WEBSOCKET PARA ACTUALIZACIONES EN TIEMPO REAL
# ============================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para actualizaciones en tiempo real"""
    await websocket.accept()
    websocket_clients.append(websocket)
    
    logger.info(f"Cliente WebSocket conectado. Total: {len(websocket_clients)}")
    
    try:
        while True:
            # Mantener conexion viva
            data = await websocket.receive_text()
            
            # Procesar comandos si es necesario
            if data:
                message = json.loads(data)
                if message.get('type') == 'ping':
                    await websocket.send_json({'type': 'pong'})
                    
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)
        logger.info(f"Cliente WebSocket desconectado. Total: {len(websocket_clients)}")


async def broadcast_message(message: Dict):
    """Envia mensaje a todos los clientes WebSocket"""
    disconnected = []
    
    for client in websocket_clients:
        try:
            await client.send_json(message)
        except:
            disconnected.append(client)
    
    # Remover clientes desconectados
    for client in disconnected:
        websocket_clients.remove(client)


# ============================================
# STARTUP & SHUTDOWN
# ============================================

@app.on_event("startup")
async def startup_event():
    """Evento de inicio"""
    logger.info("API de Trading iniciada")


@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre"""
    global trading_system
    
    if trading_system and trading_system.is_running:
        await trading_system.stop()
    
    logger.info("API de Trading detenida")


# ============================================
# EJECUTAR API
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
