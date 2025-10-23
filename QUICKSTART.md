# Guia Rapida de Inicio

## Instalacion (5 minutos)

### 1. Instalar Dependencias

```bash
# Activar entorno virtual
venv\Scripts\activate

# Instalar paquetes
pip install -r requirements.txt
```

### 2. Configurar Credenciales

```bash
# Copiar archivo de configuracion
copy .env.example .env

# Editar con tus datos
notepad .env
```

Configuracion minima en `.env`:

```env
# Modo DEMO (sin riesgo)
QUOTEX_EMAIL=tu_email@ejemplo.com
QUOTEX_PASSWORD=tu_password
QUOTEX_DEMO_MODE=true

# Capital inicial simulado
INITIAL_CAPITAL=10000

# Trading automatico (desactivado por defecto)
AUTO_TRADING=false
```

### 3. Ejecutar Sistema

```bash
python main.py
```

## Primeros Pasos

### Modo 1: Observacion (Recomendado)

El sistema analiza el mercado y muestra senales SIN ejecutar:

```bash
# En .env
AUTO_TRADING=false

# Ejecutar
python main.py
```

Veras:
- Analisis de mercado en tiempo real
- Predicciones del LSTM
- Decisiones del agente RL
- Senales de trading (sin ejecutar)

### Modo 2: Trading Manual

Aprueba cada operacion manualmente:

1. El sistema genera senal
2. Te muestra detalles (precio, SL, TP)
3. Tu decides si ejecutar

### Modo 3: Trading Automatico (CUIDADO)

Solo despues de backtesting exhaustivo:

```bash
# En .env
AUTO_TRADING=true
```

## Entrenar Modelos de IA

### Entrenar LSTM (Predictor de Precios)

```bash
python scripts/train_lstm.py
```

Tiempo: 10-30 minutos
Resultado: `models/best_lstm_model.pth`

### Entrenar RL Agent (Decisiones)

```bash
python scripts/train_rl.py
```

Tiempo: 30-60 minutos
Resultado: `models/best_rl_model.zip`

## Configuracion Avanzada

### Cambiar Simbolo

En `main.py`:

```python
trading_system = TradingSystem(config={
    'symbol': 'BTC/USD',  # Cambiar aqui
    'timeframe': '5m',
    # ...
})
```

### Ajustar Riesgo

En `.env`:

```env
MAX_RISK_PER_TRADE=0.01  # 1% (mas conservador)
MAX_DRAWDOWN=0.10        # 10% drawdown maximo
MAX_POSITIONS=2          # Maximo 2 posiciones
```

### Usar Binance (Crypto Real)

1. Crear cuenta en Binance
2. Generar API Key (con permisos de trading)
3. Configurar en `.env`:

```env
BINANCE_API_KEY=tu_api_key
BINANCE_API_SECRET=tu_api_secret
BINANCE_TESTNET=true  # Usar testnet primero
```

4. En `main.py`:

```python
trading_system = TradingSystem(config={
    'broker': 'binance',  # Cambiar de quotex a binance
    # ...
})
```

## Alertas de Telegram

### 1. Crear Bot

1. Hablar con @BotFather en Telegram
2. Enviar `/newbot`
3. Copiar token

### 2. Obtener Chat ID

1. Hablar con @userinfobot
2. Copiar tu chat ID

### 3. Configurar

En `.env`:

```env
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
TELEGRAM_CHAT_ID=123456789
```

Recibiras notificaciones de:
- Trades abiertos/cerrados
- Alertas de riesgo
- Resumen diario

## Monitoreo

### Ver Logs

```bash
# Logs en tiempo real
tail -f logs/trading_YYYY-MM-DD.log

# Windows
Get-Content logs\trading_YYYY-MM-DD.log -Wait
```

### Metricas de Performance

El sistema muestra automaticamente:

```
RESUMEN DE PERFORMANCE
Capital Inicial: $10,000.00
Equity Actual: $11,870.00
Retorno Total: +18.7%

Total Trades: 100
Win Rate: 63.0%
Profit Factor: 2.10
Sharpe Ratio: 1.90
Max Drawdown: 3.2%
```

## Comandos Utiles

### Detener Sistema

`Ctrl + C` en la terminal

### Limpiar Logs

```bash
del logs\*.log
```

### Resetear Modelos

```bash
del models\*.pth
del models\*.zip
```

### Actualizar Dependencias

```bash
pip install --upgrade -r requirements.txt
```

## Solucionar Problemas

### Error: ModuleNotFoundError

```bash
# Verificar que el entorno virtual este activo
venv\Scripts\activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: Broker no conecta

- Verificar credenciales en `.env`
- Verificar conexion a internet
- Revisar logs en `logs/`

### Sistema muy lento

- Reducir `LSTM_LOOKBACK` en `.env`
- Usar GPU si esta disponible
- Reducir numero de indicadores en `config/config.yaml`

## Proximos Pasos

1. **Observar** el sistema en modo demo (1 semana)
2. **Entrenar** modelos con datos historicos
3. **Backtesting** exhaustivo (minimo 2 anos)
4. **Paper trading** (1 mes)
5. **Trading real** con capital minimo
6. **Escalar** gradualmente

## Recursos

- **README.md**: Documentacion completa
- **INSTALL.md**: Instalacion detallada
- **config/config.yaml**: Configuracion avanzada
- **GitHub Issues**: Reportar problemas

## Advertencias

- Comenzar SIEMPRE en modo DEMO
- No invertir mas de lo que puedes perder
- Monitorear el sistema regularmente
- Respetar limites de riesgo
- Usar brokers regulados

## Soporte

- Email: soporte@tradingsystem.com
- Telegram: @TradingSystemAI
- GitHub: Issues

---

Desarrollado con cuidado para la comunidad de trading algoritmico
