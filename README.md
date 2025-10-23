# 🚀 Sistema de Trading Algorítmico con IA + Aplicación de Escritorio

Sistema de trading autónomo 100% operacional que utiliza **Deep Learning (LSTM)** y **Reinforcement Learning (PPO)** para ejecutar operaciones automáticas en mercados financieros.

## ⭐ NUEVO: Aplicación de Escritorio con GUI

Ahora incluye una **aplicación de escritorio profesional** con interfaz gráfica moderna (PyQt6):
- 🖥️ **Dashboard interactivo** con métricas en tiempo real
- 📈 **Gráficos de precios** y equity
- 🎮 **Panel de trading manual** con clicks
- 🔌 **Gestión de brokers** visual (Quotex, Binance, OANDA)
- ⚙️ **Configuración sin código**
- 📊 **Monitoreo de posiciones** en vivo

**Inicio rápido:** Doble click en `start_trading_app.bat`

Ver: [INICIO_RAPIDO_APP.md](INICIO_RAPIDO_APP.md) | [DESKTOP_APP_GUIDE.md](DESKTOP_APP_GUIDE.md)

## 🎯 Características Principales

### 🧠 Inteligencia Artificial Dual
- **LSTM Predictor**: Predice movimientos de precios futuros con intervalos de confianza
- **Agente RL (PPO)**: Toma decisiones óptimas de trading basadas en el estado del mercado
- **Meta-Learning**: Combina ambos modelos para maximizar precisión

### 📊 Análisis Técnico Avanzado
- **60+ Indicadores Técnicos**: RSI, MACD, EMA, Bollinger Bands, ATR, ADX, Ichimoku, etc.
- **Detección de Patrones**: Candlestick patterns, chart patterns, swing points
- **Soporte/Resistencia Dinámico**: Clustering automático de niveles clave
- **Análisis Multi-Timeframe**: 1m, 5m, 15m, 1h, 4h, 1D

### 🛡️ Gestión de Riesgo Profesional
- **Position Sizing Inteligente**: Kelly Criterion modificado, ajustado por confianza
- **Stop Loss Dinámico**: Basado en ATR con trailing stop automático
- **Take Profit Optimizado**: Ratio Risk:Reward mínimo de 2:1
- **Límites de Seguridad**:
  - Máximo 2% de riesgo por operación
  - Drawdown máximo 15%
  - Máximo 3 posiciones simultáneas
  - Pausa automática en condiciones críticas

### 🔄 Aprendizaje Continuo
- Re-entrenamiento automático cada 50 operaciones
- A/B Testing de estrategias
- Adaptación a diferentes regímenes de mercado (trending/ranging)
- Backup automático de mejores modelos

### 🔌 Integración con Brokers
- **Quotex** (Simulación para desarrollo) ✅
- **Binance** (Crypto - API oficial) ✅

### 📱 Monitoreo y Alertas
- **Aplicación de Escritorio**: GUI profesional con PyQt6 ⭐ NUEVO
- **API REST**: FastAPI con WebSocket para comunicación ⭐ NUEVO
- **Telegram Bot**: Notificaciones en tiempo real
- **Logging Completo**: Registro detallado de todas las operaciones

## 📋 Requisitos del Sistema

### Software
- **Python 3.10+**
- **Windows/Linux/MacOS**
- **8GB RAM mínimo** (16GB recomendado)
- **GPU NVIDIA** (Opcional, acelera entrenamiento)

### Dependencias Principales
```
torch>=2.0.0
tensorflow>=2.13.0
stable-baselines3>=2.1.0
pandas>=2.0.0
numpy>=1.24.0
ta-lib>=0.4.28
PyQt6>=6.6.0          # GUI Desktop ⭐ NUEVO
fastapi>=0.104.0      # API REST ⭐ NUEVO
```

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
cd c:\xampp\htdocs\Trading\Trading
```

### 2. Crear entorno virtual
```bash
python -m venv venv
```

### 3. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Instalar TA-Lib (Indicadores Técnicos)

**Windows:**
```bash
# Descargar wheel desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl
```

**Linux:**
```bash
sudo apt-get install ta-lib
pip install TA-Lib
```

**Mac:**
```bash
brew install ta-lib
pip install TA-Lib
```

### 6. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
copy .env.example .env

# Editar .env con tus credenciales
notepad .env
```

## ⚙️ Configuración

### Archivo `.env`

```env
# Broker Principal (Quotex - Simulación)
QUOTEX_EMAIL=tu_email@ejemplo.com
QUOTEX_PASSWORD=tu_password
QUOTEX_DEMO_MODE=true

# Binance (Alternativa real)
BINANCE_API_KEY=tu_api_key
BINANCE_API_SECRET=tu_api_secret
BINANCE_TESTNET=true

# Telegram (Alertas)
TELEGRAM_BOT_TOKEN=tu_bot_token
TELEGRAM_CHAT_ID=tu_chat_id

# Configuración de Trading
MAX_RISK_PER_TRADE=0.02
MAX_DRAWDOWN=0.15
MAX_POSITIONS=3
INITIAL_CAPITAL=10000

# Modo de Operación
TRADING_MODE=demo
AUTO_TRADING=false
ENABLE_RL_TRAINING=true
```

### Archivo `config/config.yaml`

Personaliza indicadores técnicos, parámetros de IA, gestión de riesgo, etc.

## 🎮 Uso

### ⭐ NUEVO: Aplicación de Escritorio (Recomendado)

**Inicio Automático:**
```bash
# Doble click en:
start_trading_app.bat
```

**Inicio Manual:**
```bash
# Terminal 1 - API
python run_api.py

# Terminal 2 - App
python desktop_app.py
```

**Características:**
- 🖥️ Interfaz gráfica moderna
- 📊 Dashboard con métricas en tiempo real
- 🎮 Trading manual con clicks
- 📈 Gráficos interactivos
- ⚙️ Configuración visual

Ver: [INICIO_RAPIDO_APP.md](INICIO_RAPIDO_APP.md) para guía completa

---

### Modo 1: CLI - Trading Manual

```bash
python main.py
```

El sistema:
1. Se conecta al broker
2. Analiza el mercado en tiempo real
3. Genera señales de trading
4. **Espera tu aprobación** para ejecutar

### Modo 2: CLI - Trading Automático

```bash
# Editar .env
AUTO_TRADING=true

# Ejecutar
python main.py
```

⚠️ **ADVERTENCIA**: Solo activar después de backtesting exhaustivo.

### Modo 3: Entrenamiento de Modelos

```bash
# Entrenar LSTM
python scripts/train_lstm.py

# Entrenar RL Agent
python scripts/train_rl.py

# Backtesting
python scripts/backtest.py
```

## 📊 Métricas de Performance

El sistema calcula automáticamente:

- **Rentabilidad**: ROI, P&L total, Sharpe Ratio, Sortino Ratio
- **Precisión**: Win Rate, Profit Factor, Expectancy
- **Riesgo**: Max Drawdown, VAR, Calmar Ratio
- **Operativa**: Número de trades, duración promedio, comisiones

### Ejemplo de Salida

```
📊 RESUMEN DE PERFORMANCE
══════════════════════════════════════════════════════════════════
💰 Capital Inicial: $10,000.00
💰 Equity Actual: $11,870.00
📈 Retorno Total: +18.7%
💵 P&L Total: +$1,870.00

📊 Total Trades: 100
🟢 Ganadores: 63 (63.0%)
🔴 Perdedores: 37

📊 Profit Factor: 2.10
📊 Sharpe Ratio: 1.90
📊 Sortino Ratio: 2.45

📉 Max Drawdown: 3.2%
📉 Drawdown Actual: 0.5%
══════════════════════════════════════════════════════════════════
```

## 🔬 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA DE ADQUISICIÓN                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Broker API   │  │ Data Feed    │  │ News API     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────┴──────────────────┴──────────────────┴─────────────┐
│              PROCESAMIENTO DE DATOS                         │
│  • Feature Engineering (60+ features)                       │
│  • Normalización y limpieza                                 │
│  • Detección de régimen de mercado                          │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                 CEREBRO DE IA (DUAL BRAIN)                  │
│  ┌────────────────────┐    ┌─────────────────────┐         │
│  │  LSTM Predictor    │───▶│  Agente RL (PPO)    │         │
│  │  (Forecasting)     │    │  (Decisiones)       │         │
│  └────────────────────┘    └──────────┬──────────┘         │
└─────────────────────────────┬─────────┴─────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│             MÓDULO DE GESTIÓN DE RIESGO                     │
│  • Validación de señales                                    │
│  • Cálculo de position sizing                               │
│  • Stop Loss / Take Profit dinámicos                        │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│              CAPA DE EJECUCIÓN                              │
│  • Envío de órdenes                                         │
│  • Monitoreo en tiempo real                                 │
│  • Gestión de errores                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🧪 Testing

### Backtesting
```bash
python scripts/backtest.py --symbol EUR/USD --start 2022-01-01 --end 2024-12-31
```

### Paper Trading
```bash
# Editar .env
TRADING_MODE=paper

python main.py
```

### Unit Tests
```bash
pytest tests/
```

## 📈 Roadmap

### Fase 1: Desarrollo ✅
- [x] Arquitectura base
- [x] Integración con brokers
- [x] Feature engineering
- [x] Modelos de IA (LSTM + RL)
- [x] Risk management

### Fase 2: Testing 🔄
- [ ] Backtesting exhaustivo (2 años)
- [ ] Forward testing (1 mes demo)
- [ ] Optimización de hiperparámetros
- [ ] Validación en diferentes mercados

### Fase 3: Producción 📅
- [ ] Dashboard web interactivo
- [ ] Base de datos TimescaleDB
- [ ] API REST para control remoto
- [ ] Soporte para más brokers
- [ ] Análisis de sentimiento (NLP)

## ⚠️ Advertencias Importantes

### ⚡ RIESGO FINANCIERO
- **Este sistema opera con dinero real**
- **Puede generar pérdidas significativas**
- **Solo usar capital que puedas permitirte perder**
- **Comenzar siempre en modo DEMO**

### 🔒 Seguridad
- **Nunca compartir API keys**
- **Usar autenticación 2FA en brokers**
- **Mantener logs seguros**
- **Revisar operaciones regularmente**

### 📜 Legal
- **Cumplir regulaciones locales**
- **Declarar ganancias según legislación**
- **Usar brokers regulados**

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crear branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto es de código abierto bajo licencia MIT.

## 📞 Soporte

- **Issues**: GitHub Issues
- **Email**: soporte@tradingsystem.com
- **Telegram**: @TradingSystemAI

## 🙏 Agradecimientos

- **Stable-Baselines3**: Framework de RL
- **TA-Lib**: Indicadores técnicos
- **PyTorch**: Deep Learning
- **Comunidad Open Source**

---

**⚠️ DISCLAIMER**: Este software se proporciona "tal cual" sin garantías. El trading conlleva riesgos significativos. Los resultados pasados no garantizan resultados futuros.

**Desarrollado con ❤️ para la comunidad de trading algorítmico**
