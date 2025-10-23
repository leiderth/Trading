"""
Notificador de Telegram
Envía alertas y notificaciones al usuario
"""

import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError
from loguru import logger


class TelegramNotifier:
    """
    Envía notificaciones a Telegram
    """
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot: Optional[Bot] = None
        self.enabled = True
        
        if bot_token and chat_id:
            self.bot = Bot(token=bot_token)
            logger.info("📱 TelegramNotifier inicializado")
        else:
            self.enabled = False
            logger.warning("⚠️  Telegram no configurado")
    
    async def send_message(self, message: str, parse_mode: str = 'HTML'):
        """
        Envía un mensaje a Telegram
        
        Args:
            message: Texto del mensaje
            parse_mode: Modo de parseo ('HTML' o 'Markdown')
        """
        if not self.enabled or not self.bot:
            return
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            logger.debug(f"📤 Mensaje enviado a Telegram")
        except TelegramError as e:
            logger.error(f"✗ Error enviando mensaje a Telegram: {e}")
        except Exception as e:
            logger.error(f"✗ Error inesperado en Telegram: {e}")
    
    async def send_trade_alert(
        self,
        action: str,
        symbol: str,
        side: str,
        price: float,
        quantity: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        pnl: Optional[float] = None
    ):
        """Envía alerta de trade"""
        if action == "open":
            emoji = "🟢" if side.lower() == "long" else "🔴"
            message = (
                f"{emoji} <b>TRADE ABIERTO</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📊 Símbolo: <b>{symbol}</b>\n"
                f"📈 Dirección: <b>{side.upper()}</b>\n"
                f"💰 Precio: <b>{price:.5f}</b>\n"
                f"📦 Cantidad: <b>{quantity:.4f}</b>\n"
            )
            if stop_loss:
                message += f"🛑 Stop Loss: <b>{stop_loss:.5f}</b>\n"
            if take_profit:
                message += f"🎯 Take Profit: <b>{take_profit:.5f}</b>\n"
        
        elif action == "close":
            emoji = "🟢" if pnl and pnl > 0 else "🔴"
            message = (
                f"{emoji} <b>TRADE CERRADO</b>\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📊 Símbolo: <b>{symbol}</b>\n"
                f"💰 Precio Cierre: <b>{price:.5f}</b>\n"
            )
            if pnl is not None:
                message += f"💵 P&L: <b>${pnl:+,.2f}</b>\n"
        
        else:
            message = f"ℹ️ {action}: {symbol}"
        
        await self.send_message(message)
    
    async def send_alert(self, alert_type: str, message: str):
        """Envía alerta general"""
        emoji_map = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '🚨',
            'success': '✅',
            'drawdown': '📉',
            'system': '🔧'
        }
        
        emoji = emoji_map.get(alert_type, 'ℹ️')
        formatted_message = f"{emoji} <b>{alert_type.upper()}</b>\n{message}"
        
        await self.send_message(formatted_message)
    
    async def send_daily_summary(self, metrics: dict):
        """Envía resumen diario"""
        message = (
            f"📊 <b>RESUMEN DIARIO</b>\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"💰 Equity: <b>${metrics.get('current_equity', 0):,.2f}</b>\n"
            f"📈 Retorno: <b>{metrics.get('total_return', 0):+.2f}%</b>\n"
            f"💵 P&L Diario: <b>${metrics.get('daily_pnl', 0):+,.2f}</b>\n"
            f"\n"
            f"📊 Trades Hoy: <b>{metrics.get('daily_trades', 0)}</b>\n"
            f"🟢 Win Rate: <b>{metrics.get('win_rate', 0):.1f}%</b>\n"
            f"📊 Profit Factor: <b>{metrics.get('profit_factor', 0):.2f}</b>\n"
            f"\n"
            f"📉 Max Drawdown: <b>{metrics.get('max_drawdown', 0):.2f}%</b>\n"
            f"📊 Sharpe Ratio: <b>{metrics.get('sharpe_ratio', 0):.2f}</b>\n"
        )
        
        await self.send_message(message)
