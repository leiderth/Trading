"""
Trading Database - SQLite para datos persistentes
Gestiona: usuarios, trades, posiciones, configuración, analytics
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from loguru import logger
import json
from pathlib import Path


class TradingDatabase:
    """Base de datos SQLite para el sistema de trading"""
    
    def __init__(self, db_path: str = "data/trading.db"):
        """Inicializar base de datos"""
        self.db_path = db_path
        
        # Crear directorio si no existe
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Conectar y crear tablas
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        self.create_tables()
        logger.info(f"✅ Base de datos inicializada: {db_path}")
    
    def create_tables(self):
        """Crear todas las tablas necesarias"""
        
        # Tabla de usuarios
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                avatar_url TEXT,
                bio TEXT,
                initial_balance REAL DEFAULT 10000.0,
                current_balance REAL DEFAULT 10000.0
            )
        """)
        
        # Tabla de configuración de usuario
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                broker TEXT,
                api_key TEXT,
                api_secret TEXT,
                testnet BOOLEAN DEFAULT 1,
                theme TEXT DEFAULT 'dark',
                notifications_enabled BOOLEAN DEFAULT 1,
                sound_enabled BOOLEAN DEFAULT 1,
                max_positions INTEGER DEFAULT 3,
                risk_per_trade REAL DEFAULT 0.02,
                auto_trading_enabled BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Tabla de trades
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                stop_loss REAL,
                take_profit REAL,
                pnl REAL DEFAULT 0,
                pnl_percent REAL DEFAULT 0,
                status TEXT DEFAULT 'open',
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                closed_at TIMESTAMP,
                broker TEXT,
                order_id TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Tabla de posiciones actuales
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                trade_id INTEGER,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                stop_loss REAL,
                take_profit REAL,
                pnl REAL DEFAULT 0,
                pnl_percent REAL DEFAULT 0,
                opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
        """)
        
        # Tabla de balance histórico
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                balance REAL NOT NULL,
                equity REAL NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Tabla de analytics
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date DATE NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                win_rate REAL DEFAULT 0,
                profit_factor REAL DEFAULT 0,
                sharpe_ratio REAL DEFAULT 0,
                max_drawdown REAL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id),
                UNIQUE(user_id, date)
            )
        """)
        
        # Tabla de agentes IA
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_agents_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                agent_name TEXT NOT NULL,
                decision TEXT NOT NULL,
                confidence REAL NOT NULL,
                accuracy REAL DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        self.conn.commit()
        logger.info("✅ Tablas creadas/verificadas")
    
    # ==================== USUARIOS ====================
    
    def create_user(self, username: str, email: str = None, initial_balance: float = 10000.0) -> int:
        """Crear nuevo usuario"""
        try:
            self.cursor.execute("""
                INSERT INTO users (username, email, initial_balance, current_balance)
                VALUES (?, ?, ?, ?)
            """, (username, email, initial_balance, initial_balance))
            self.conn.commit()
            
            user_id = self.cursor.lastrowid
            
            # Crear settings por defecto
            self.cursor.execute("""
                INSERT INTO user_settings (user_id) VALUES (?)
            """, (user_id,))
            self.conn.commit()
            
            logger.info(f"✅ Usuario creado: {username} (ID: {user_id})")
            return user_id
        except sqlite3.IntegrityError:
            logger.warning(f"Usuario {username} ya existe")
            return self.get_user_by_username(username)['id']
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Obtener usuario por nombre"""
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Obtener usuario por ID"""
        self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_user_balance(self, user_id: int, new_balance: float):
        """Actualizar balance del usuario"""
        self.cursor.execute("""
            UPDATE users SET current_balance = ? WHERE id = ?
        """, (new_balance, user_id))
        self.conn.commit()
        
        # Guardar en historial
        self.cursor.execute("""
            INSERT INTO balance_history (user_id, balance, equity)
            VALUES (?, ?, ?)
        """, (user_id, new_balance, new_balance))
        self.conn.commit()
    
    def update_last_login(self, user_id: int):
        """Actualizar último login"""
        self.cursor.execute("""
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
        """, (user_id,))
        self.conn.commit()
    
    # ==================== SETTINGS ====================
    
    def get_user_settings(self, user_id: int) -> Optional[Dict]:
        """Obtener configuración del usuario"""
        self.cursor.execute("SELECT * FROM user_settings WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_user_settings(self, user_id: int, settings: Dict):
        """Actualizar configuración del usuario"""
        fields = ', '.join([f"{k} = ?" for k in settings.keys()])
        values = list(settings.values()) + [user_id]
        
        self.cursor.execute(f"""
            UPDATE user_settings SET {fields} WHERE user_id = ?
        """, values)
        self.conn.commit()
    
    # ==================== TRADES ====================
    
    def create_trade(self, user_id: int, symbol: str, side: str, amount: float,
                     entry_price: float, stop_loss: float = None, 
                     take_profit: float = None, broker: str = None) -> int:
        """Crear nuevo trade"""
        self.cursor.execute("""
            INSERT INTO trades (user_id, symbol, side, amount, entry_price, 
                              stop_loss, take_profit, broker)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, symbol, side, amount, entry_price, stop_loss, take_profit, broker))
        self.conn.commit()
        
        trade_id = self.cursor.lastrowid
        
        # Crear posición
        self.cursor.execute("""
            INSERT INTO positions (user_id, trade_id, symbol, side, amount, 
                                 entry_price, current_price, stop_loss, take_profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, trade_id, symbol, side, amount, entry_price, 
              entry_price, stop_loss, take_profit))
        self.conn.commit()
        
        logger.info(f"✅ Trade creado: {side} {amount} {symbol} @ {entry_price}")
        return trade_id
    
    def close_trade(self, trade_id: int, exit_price: float):
        """Cerrar trade"""
        # Obtener trade
        self.cursor.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
        trade = dict(self.cursor.fetchone())
        
        # Calcular P&L
        if trade['side'] == 'buy':
            pnl = (exit_price - trade['entry_price']) * trade['amount']
        else:
            pnl = (trade['entry_price'] - exit_price) * trade['amount']
        
        pnl_percent = (pnl / (trade['entry_price'] * trade['amount'])) * 100
        
        # Actualizar trade
        self.cursor.execute("""
            UPDATE trades 
            SET exit_price = ?, pnl = ?, pnl_percent = ?, 
                status = 'closed', closed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (exit_price, pnl, pnl_percent, trade_id))
        
        # Eliminar posición
        self.cursor.execute("DELETE FROM positions WHERE trade_id = ?", (trade_id,))
        
        # Actualizar balance
        user = self.get_user(trade['user_id'])
        new_balance = user['current_balance'] + pnl
        self.update_user_balance(trade['user_id'], new_balance)
        
        self.conn.commit()
        
        logger.info(f"✅ Trade cerrado: P&L = ${pnl:.2f} ({pnl_percent:.2f}%)")
        return pnl
    
    def get_open_trades(self, user_id: int) -> List[Dict]:
        """Obtener trades abiertos"""
        self.cursor.execute("""
            SELECT * FROM trades 
            WHERE user_id = ? AND status = 'open'
            ORDER BY opened_at DESC
        """, (user_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_trade_history(self, user_id: int, limit: int = 100) -> List[Dict]:
        """Obtener historial de trades"""
        self.cursor.execute("""
            SELECT * FROM trades 
            WHERE user_id = ?
            ORDER BY opened_at DESC
            LIMIT ?
        """, (user_id, limit))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== POSICIONES ====================
    
    def get_open_positions(self, user_id: int) -> List[Dict]:
        """Obtener posiciones abiertas"""
        self.cursor.execute("""
            SELECT * FROM positions 
            WHERE user_id = ?
            ORDER BY opened_at DESC
        """, (user_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_position_price(self, position_id: int, current_price: float):
        """Actualizar precio actual de posición"""
        # Obtener posición
        self.cursor.execute("SELECT * FROM positions WHERE id = ?", (position_id,))
        pos = dict(self.cursor.fetchone())
        
        # Calcular P&L
        if pos['side'] == 'buy':
            pnl = (current_price - pos['entry_price']) * pos['amount']
        else:
            pnl = (pos['entry_price'] - current_price) * pos['amount']
        
        pnl_percent = (pnl / (pos['entry_price'] * pos['amount'])) * 100
        
        # Actualizar
        self.cursor.execute("""
            UPDATE positions 
            SET current_price = ?, pnl = ?, pnl_percent = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (current_price, pnl, pnl_percent, position_id))
        self.conn.commit()
    
    # ==================== ANALYTICS ====================
    
    def get_daily_analytics(self, user_id: int, date: str = None) -> Optional[Dict]:
        """Obtener analytics del día"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute("""
            SELECT * FROM analytics WHERE user_id = ? AND date = ?
        """, (user_id, date))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def update_daily_analytics(self, user_id: int):
        """Actualizar analytics del día"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Calcular métricas
        self.cursor.execute("""
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(pnl) as total_pnl
            FROM trades
            WHERE user_id = ? AND DATE(opened_at) = ?
        """, (user_id, today))
        
        stats = dict(self.cursor.fetchone())
        
        win_rate = (stats['winning_trades'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0
        
        # Insertar o actualizar
        self.cursor.execute("""
            INSERT INTO analytics (user_id, date, total_trades, winning_trades, 
                                 losing_trades, total_pnl, win_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, date) DO UPDATE SET
                total_trades = excluded.total_trades,
                winning_trades = excluded.winning_trades,
                losing_trades = excluded.losing_trades,
                total_pnl = excluded.total_pnl,
                win_rate = excluded.win_rate
        """, (user_id, today, stats['total_trades'], stats['winning_trades'],
              stats['losing_trades'], stats['total_pnl'], win_rate))
        self.conn.commit()
    
    def get_balance_history(self, user_id: int, days: int = 30) -> List[Dict]:
        """Obtener historial de balance"""
        self.cursor.execute("""
            SELECT * FROM balance_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, days * 24))
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ==================== AI AGENTS ====================
    
    def save_agent_decision(self, user_id: int, agent_name: str, 
                           decision: str, confidence: float, accuracy: float = 0):
        """Guardar decisión de agente"""
        self.cursor.execute("""
            INSERT INTO ai_agents_history (user_id, agent_name, decision, confidence, accuracy)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, agent_name, decision, confidence, accuracy))
        self.conn.commit()
    
    def get_agent_history(self, user_id: int, agent_name: str = None, limit: int = 100) -> List[Dict]:
        """Obtener historial de agente"""
        if agent_name:
            self.cursor.execute("""
                SELECT * FROM ai_agents_history
                WHERE user_id = ? AND agent_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, agent_name, limit))
        else:
            self.cursor.execute("""
                SELECT * FROM ai_agents_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_user_settings(self, user_id: int) -> Dict:
        """Obtener configuración del usuario"""
        self.cursor.execute("""
            SELECT * FROM user_settings WHERE user_id = ?
        """, (user_id,))
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    # ==================== UTILIDADES ====================
    
    def close(self):
        """Cerrar conexión"""
        self.conn.close()
        logger.info("Base de datos cerrada")
    
    def __del__(self):
        """Destructor"""
        if hasattr(self, 'conn'):
            self.conn.close()


# Instancia global
_db_instance = None

def get_database() -> TradingDatabase:
    """Obtener instancia de base de datos (singleton)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = TradingDatabase()
    return _db_instance
