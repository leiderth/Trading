# 🚀 INSTRUCCIONES COMPLETAS - Sistema de Trading con IA

## 📋 RESUMEN DEL SISTEMA

Has recibido un **Sistema de Trading Algorítmico Profesional** con:

✅ **Inteligencia Artificial Dual**
- LSTM para predicción de precios
- Reinforcement Learning (PPO) para decisiones

✅ **60+ Indicadores Técnicos**
- RSI, MACD, Bollinger Bands, ATR, ADX, etc.

✅ **Gestión de Riesgo Profesional**
- Stop Loss dinámico
- Position sizing inteligente
- Límites de seguridad automáticos

✅ **Aprendizaje Continuo**
- Re-entrenamiento automático
- Adaptación al mercado

---

## 🔧 INSTALACIÓN (15 minutos)

### Paso 1: Verificar Python

Abrir terminal (CMD o PowerShell) y ejecutar:

```bash
python --version
```

**Debe mostrar Python 3.10 o superior**

Si no está instalado:
1. Descargar: https://www.python.org/downloads/
2. Instalar marcando "Add Python to PATH"

### Paso 2: Navegar al Proyecto

```bash
cd c:\xampp\htdocs\Trading\Trading
```

### Paso 3: Crear Entorno Virtual

```bash
python -m venv venv
```

### Paso 4: Activar Entorno Virtual

**Windows CMD:**
```bash
venv\Scripts\activate
```

**Windows PowerShell:**
```bash
venv\Scripts\Activate.ps1
```

Si hay error de permisos:
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Deberías ver `(venv)` al inicio de la línea.

### Paso 5: Actualizar pip

```bash
python -m pip install --upgrade pip
```

### Paso 6: Instalar TA-Lib (IMPORTANTE)

**Opción A - Wheel Pre-compilado (MÁS FÁCIL):**

1. Descargar desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib

2. Elegir según tu Python:
   - Python 3.10: `TA_Lib‑0.4.28‑cp310‑cp310‑win_amd64.whl`
   - Python 3.11: `TA_Lib‑0.4.28‑cp311‑cp311‑win_amd64.whl`
   - Python 3.12: `TA_Lib‑0.4.28‑cp312‑cp312‑win_amd64.whl`

3. Instalar (ajustar nombre del archivo):
```bash
pip install TA_Lib-0.4.28-cp310-cp310-win_amd64.whl
```

**Opción B - Si no funciona la Opción A:**

Instalar sin TA-Lib (el sistema usará pandas-ta como alternativa):
```bash
# Continuar sin TA-Lib
# El sistema funcionará con pandas-ta
```

### Paso 7: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Esto tomará 5-10 minutos**. Instalará:
- PyTorch (Deep Learning)
- TensorFlow (Neural Networks)
- Stable-Baselines3 (Reinforcement Learning)
- Pandas, NumPy (Data processing)
- Y muchas más...

### Paso 8: Configurar Variables de Entorno

```bash
copy .env.example .env
notepad .env
```

**Configuración mínima en `.env`:**

```env
# MODO DEMO (SIN RIESGO)
QUOTEX_EMAIL=tu_email@ejemplo.com
QUOTEX_PASSWORD=tu_password
QUOTEX_DEMO_MODE=true

# Capital inicial simulado
INITIAL_CAPITAL=10000

# Trading automático (DESACTIVADO por seguridad)
AUTO_TRADING=false

# Configuración de riesgo
MAX_RISK_PER_TRADE=0.02
MAX_DRAWDOWN=0.15
MAX_POSITIONS=3
```

### Paso 9: Verificar Instalación

```bash
python test_system.py
```

Debe mostrar:
```
✓ NumPy y Pandas
✓ PyTorch
✓ TensorFlow
✓ Stable-Baselines3
✓ Sistema listo para usar!
```

---

## ▶️ EJECUTAR EL SISTEMA

### Modo 1: Observación (RECOMENDADO PARA EMPEZAR)

```bash
python main.py
```

El sistema:
1. ✅ Se conecta al broker (modo simulación)
2. ✅ Analiza el mercado en tiempo real
3. ✅ Muestra predicciones y señales
4. ❌ NO ejecuta operaciones automáticamente

**Verás en pantalla:**

```
🚀 SISTEMA DE TRADING ALGORÍTMICO CON IA
══════════════════════════════════════════════════════════════════
✓ Conectado a QUOTEX (SIMULACIÓN)
✓ Feature Engineering inicializado
✓ LSTM Predictor cargado
✓ RL Agent cargado
✓ Risk Manager inicializado
══════════════════════════════════════════════════════════════════

▶️ SISTEMA DE TRADING INICIADO
📊 Símbolo: EUR/USD
⏱️ Timeframe: 5m
🤖 Trading Automático: ✗

📊 Datos actualizados: 200 velas
🧠 LSTM Predicción: UP | Cambio: +0.15% | Confianza: 72%
🤖 RL Acción: BUY_50% | Confianza: 68%
✓ SEÑAL VÁLIDA: UP | Confianza: 70.4%

⏸️ Modo observación - No se ejecutará automáticamente
```

### Modo 2: Trading Automático (SOLO DESPUÉS DE TESTING)

**⚠️ ADVERTENCIA: Solo activar después de:**
- Observar el sistema al menos 1 semana
- Entrenar modelos con datos históricos
- Hacer backtesting exhaustivo
- Estar cómodo con el riesgo

En `.env`:
```env
AUTO_TRADING=true
```

Luego:
```bash
python main.py
```

### Detener el Sistema

Presionar `Ctrl + C` en la terminal

---

## 🎓 ENTRENAR MODELOS DE IA

### Entrenar LSTM (Predictor de Precios)

```bash
python scripts/train_lstm.py
```

**Tiempo:** 10-30 minutos
**Resultado:** `models/best_lstm_model.pth`

El modelo aprenderá a predecir movimientos de precios basándose en datos históricos.

### Entrenar RL Agent (Toma de Decisiones)

```bash
python scripts/train_rl.py
```

**Tiempo:** 30-60 minutos
**Resultado:** `models/best_rl_model.zip`

El agente aprenderá qué acciones tomar en diferentes situaciones del mercado.

---

## 📊 MONITOREO Y MÉTRICAS

### Ver Logs en Tiempo Real

**Windows CMD:**
```bash
type logs\trading_2024-XX-XX.log
```

**Windows PowerShell:**
```bash
Get-Content logs\trading_2024-XX-XX.log -Wait
```

### Métricas Automáticas

El sistema muestra automáticamente:

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
══════════════════════════════════════════════════════════════════
```

---

## 🔔 CONFIGURAR ALERTAS DE TELEGRAM (OPCIONAL)

### 1. Crear Bot de Telegram

1. Abrir Telegram
2. Buscar: `@BotFather`
3. Enviar: `/newbot`
4. Seguir instrucciones
5. Copiar el **token** que te da

### 2. Obtener tu Chat ID

1. Buscar: `@userinfobot`
2. Enviar: `/start`
3. Copiar tu **chat ID**

### 3. Configurar en .env

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

Ahora recibirás notificaciones de:
- ✅ Trades abiertos/cerrados
- ⚠️ Alertas de riesgo
- 📊 Resumen diario

---

## 🔄 USAR BINANCE (CRYPTO REAL)

### Por qué Binance en lugar de Quotex:

❌ **Quotex:**
- No tiene API pública oficial
- Limitado a opciones binarias
- Regulación limitada

✅ **Binance:**
- API oficial completa
- Alta liquidez
- Comisiones bajas (0.1%)
- Testnet para pruebas

### Configurar Binance:

1. **Crear cuenta en Binance:**
   - https://www.binance.com/

2. **Generar API Key:**
   - Ir a: Perfil → API Management
   - Crear nueva API key
   - ✅ Habilitar: Spot Trading
   - ❌ Deshabilitar: Withdrawals
   - Guardar API Key y Secret

3. **Configurar en .env:**

```env
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_API_SECRET=tu_api_secret_aqui
BINANCE_TESTNET=true  # USAR TESTNET PRIMERO!
```

4. **Modificar main.py:**

```python
trading_system = TradingSystem(config={
    'broker': 'binance',  # Cambiar de 'quotex' a 'binance'
    'symbol': 'BTC/USDT',
    'timeframe': '5m',
    'auto_trading': False
})
```

5. **Probar en Testnet:**

```bash
python main.py
```

6. **Cuando estés listo para real:**

```env
BINANCE_TESTNET=false
```

---

## ⚙️ CONFIGURACIÓN AVANZADA

### Cambiar Símbolo

En `main.py`:

```python
'symbol': 'EUR/USD',  # Forex
'symbol': 'BTC/USDT', # Crypto
'symbol': 'ETH/USDT', # Crypto
```

### Cambiar Timeframe

```python
'timeframe': '1m',   # 1 minuto
'timeframe': '5m',   # 5 minutos (recomendado)
'timeframe': '15m',  # 15 minutos
'timeframe': '1h',   # 1 hora
```

### Ajustar Riesgo

En `.env`:

```env
# Más conservador
MAX_RISK_PER_TRADE=0.01  # 1% por trade
MAX_DRAWDOWN=0.10        # 10% drawdown máximo
MAX_POSITIONS=2          # Máximo 2 posiciones

# Más agresivo (NO RECOMENDADO)
MAX_RISK_PER_TRADE=0.03  # 3% por trade
MAX_DRAWDOWN=0.20        # 20% drawdown máximo
MAX_POSITIONS=5          # Máximo 5 posiciones
```

### Personalizar Indicadores

Editar `config/config.yaml`:

```yaml
technical_indicators:
  trend:
    - name: "EMA"
      periods: [20, 50, 200]  # Cambiar períodos
  
  momentum:
    - name: "RSI"
      period: 14  # Cambiar período
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "ModuleNotFoundError"

**Solución:**
```bash
# Verificar que el entorno virtual esté activo
venv\Scripts\activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "TA-Lib no se puede instalar"

**Solución:**
```bash
# Descargar wheel pre-compilado
# Desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
# Instalar: pip install TA_Lib-xxx.whl

# O continuar sin TA-Lib (usará pandas-ta)
```

### Error: "CUDA not available"

**No es un error crítico**. El sistema funcionará en CPU.

Para usar GPU:
```bash
# Instalar PyTorch con CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Sistema muy lento

**Soluciones:**
1. Reducir `LSTM_LOOKBACK` en `.env`
2. Usar menos indicadores en `config.yaml`
3. Aumentar timeframe (5m → 15m)
4. Usar GPU si está disponible

### Broker no conecta

**Verificar:**
1. Credenciales en `.env` correctas
2. Conexión a internet activa
3. Logs en `logs/` para más detalles

---

## 📚 RECURSOS Y DOCUMENTACIÓN

### Archivos Importantes:

- **README.md**: Documentación completa del sistema
- **QUICKSTART.md**: Guía rápida de inicio
- **INSTALL.md**: Instalación detallada
- **QUOTEX_INFO.md**: Info sobre Quotex y brokers alternativos
- **config/config.yaml**: Configuración avanzada

### Estructura del Proyecto:

```
Trading/
├── main.py                 # Punto de entrada
├── test_system.py          # Verificar instalación
├── requirements.txt        # Dependencias
├── .env                    # Configuración (CREAR)
├── config/
│   └── config.yaml        # Configuración avanzada
├── src/
│   ├── brokers/           # Conectores de brokers
│   ├── models/            # Modelos de IA
│   ├── data/              # Procesamiento de datos
│   ├── risk/              # Gestión de riesgo
│   ├── core/              # Sistema principal
│   └── utils/             # Utilidades
├── scripts/
│   ├── train_lstm.py      # Entrenar LSTM
│   └── train_rl.py        # Entrenar RL
├── models/                # Modelos guardados
└── logs/                  # Logs del sistema
```

---

## ⚠️ ADVERTENCIAS IMPORTANTES

### 🚨 RIESGO FINANCIERO

- Este sistema opera con dinero real
- Puede generar pérdidas significativas
- Solo usar capital que puedas permitirte perder
- **SIEMPRE comenzar en modo DEMO**

### 🔒 SEGURIDAD

- Nunca compartir tus API keys
- Usar autenticación 2FA en brokers
- No habilitar "Withdrawals" en API keys
- Mantener logs seguros

### 📜 LEGAL

- Cumplir regulaciones locales
- Declarar ganancias según legislación
- Usar brokers regulados

---

## 🎯 PLAN RECOMENDADO

### Semana 1-2: Observación
- ✅ Ejecutar en modo observación
- ✅ Entender cómo funciona
- ✅ Ver señales generadas
- ❌ No activar auto-trading

### Semana 3-4: Entrenamiento
- ✅ Entrenar modelos LSTM y RL
- ✅ Ajustar configuración
- ✅ Optimizar parámetros

### Mes 2: Backtesting
- ✅ Probar con datos históricos
- ✅ Validar en diferentes condiciones
- ✅ Calcular métricas

### Mes 3: Paper Trading
- ✅ Usar testnet de Binance
- ✅ Simular operaciones reales
- ✅ Monitorear 24/7

### Mes 4+: Trading Real
- ✅ Comenzar con capital mínimo ($500)
- ✅ Monitorear constantemente
- ✅ Escalar gradualmente

---

## 📞 SOPORTE

### Preguntas Frecuentes:

**P: ¿Puedo usar Quotex para trading real?**
R: No recomendado. Quotex no tiene API oficial. Usar Binance, OANDA, o Interactive Brokers.

**P: ¿Cuánto capital necesito?**
R: Mínimo $500 para trading real. Comenzar con $10,000 es ideal.

**P: ¿El sistema garantiza ganancias?**
R: NO. El trading conlleva riesgos. Resultados pasados no garantizan resultados futuros.

**P: ¿Necesito conocimientos de programación?**
R: No para uso básico. Sí para personalización avanzada.

**P: ¿Funciona en Mac/Linux?**
R: Sí, con ajustes menores en la instalación.

### Contacto:

- **GitHub Issues**: Para bugs y mejoras
- **Email**: soporte@tradingsystem.com
- **Telegram**: @TradingSystemAI

---

## ✅ CHECKLIST FINAL

Antes de usar el sistema, verificar:

- [ ] Python 3.10+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Todas las dependencias instaladas
- [ ] Archivo `.env` configurado
- [ ] `test_system.py` ejecutado exitosamente
- [ ] Sistema ejecutado en modo observación
- [ ] Logs revisados sin errores críticos
- [ ] Entendimiento de riesgos financieros
- [ ] Plan de trading definido

---

**🎉 ¡SISTEMA LISTO PARA USAR!**

**Recuerda:**
- Comenzar siempre en DEMO
- Monitorear constantemente
- Respetar límites de riesgo
- Aprender continuamente

**¡Buena suerte en tu trading algorítmico! 🚀📈**
