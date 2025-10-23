# GUIA COMPLETA - APLICACION DE ESCRITORIO

## DESCRIPCION

Trading System Pro es una aplicacion de escritorio profesional con interfaz grafica moderna.

## CARACTERISTICAS

### 1. Dashboard Interactivo
- Metricas en tiempo real (Balance, Equity, P&L, Retorno)
- Estadisticas de trading (Win Rate, Profit Factor, Sharpe Ratio)
- Indicadores de riesgo (Max Drawdown, Posiciones abiertas)
- Actualizacion automatica cada 2 segundos

### 2. Panel de Trading Manual
- Ejecutar operaciones BUY/SELL con un click
- Configurar Stop Loss y Take Profit
- Ver precios Bid/Ask en tiempo real
- Seleccion de simbolos (Forex, Crypto, etc.)

### 3. Graficos de Precios
- Visualizacion de velas en tiempo real
- Indicadores tecnicos superpuestos
- Zoom y navegacion interactiva

### 4. Gestion de Posiciones
- Ver todas las posiciones abiertas
- P&L en tiempo real con colores
- Cerrar posiciones con un click

### 5. Historial de Trades
- Registro completo de operaciones
- Filtros y busqueda
- Analisis de performance

## INSTALACION

### Paso 1: Instalar Dependencias

```bash
cd c:\xampp\htdocs\Trading\Trading
venv\Scripts\activate
pip install PyQt6 PyQt6-WebEngine pyqtgraph qdarkstyle
pip install fastapi uvicorn pydantic
```

### Paso 2: Verificar Instalacion

```bash
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
```

## COMO USAR

### Terminal 1 - Iniciar API:

```bash
cd c:\xampp\htdocs\Trading\Trading
venv\Scripts\activate
python run_api.py
```

### Terminal 2 - Iniciar App:

```bash
cd c:\xampp\htdocs\Trading\Trading
venv\Scripts\activate
python desktop_app.py
```

## CONECTAR BROKERS

### QUOTEX (Simulacion)

1. Click en "Conectar Broker"
2. Seleccionar "Quotex (Simulacion)"
3. Ingresar credenciales
4. Marcar "Modo Demo"
5. Click "Conectar"

### BINANCE (Crypto Real)

1. Crear API Key en Binance:
   - Ir a: https://www.binance.com/
   - Login -> Perfil -> API Management
   - Click "Create API"
   - Habilitar: "Enable Spot & Margin Trading"
   - Deshabilitar: "Enable Withdrawals"
   - Copiar API Key y Secret

2. En la aplicacion:
   - Click "Conectar Broker"
   - Seleccionar "Binance (Crypto)"
   - Pegar API Key y Secret
   - Marcar "Usar Testnet" (para pruebas)
   - Click "Conectar"

3. Para trading real:
   - Desmarcar "Usar Testnet"
   - Depositar fondos en Binance (minimo $500)
   - Comenzar con operaciones pequenas

### OANDA (Forex Real)

1. Crear cuenta en OANDA:
   - Ir a: https://www.oanda.com/
   - Registrarse
   - Generar token de API

2. En la aplicacion:
   - Click "Conectar Broker"
   - Seleccionar "OANDA (Forex)"
   - Pegar token
   - Click "Conectar"

## EJECUTAR OPERACIONES

### Operacion Manual:

1. En Panel de Trading:
   - Seleccionar simbolo: EUR/USD o BTC/USDT
   - Click "Actualizar Precio"
   - Seleccionar direccion: BUY o SELL
   - Ingresar cantidad: 0.1
   - Configurar Stop Loss y Take Profit
   - Click "COMPRAR" o "VENDER"
   - Confirmar

2. Monitorear:
   - Ver posicion en "Posiciones Abiertas"
   - P&L en tiempo real
   - Click "Cerrar" para cerrar

## CONFIGURACION

### Menu -> Configuracion -> Preferencias

**Tab Trading:**
- Riesgo maximo por trade: 1-10%
- Posiciones maximas: 1-10
- Trading automatico: Si/No

**Tab IA:**
- Umbral de confianza: 50-100%
- Re-entrenamiento automatico: Si/No

## ADVERTENCIAS IMPORTANTES

### BINANCE:
- Comisiones: 0.1% por operacion
- Slippage: Puede haber diferencia de precio
- Volatilidad: Crypto es muy volatil
- Usar stop loss siempre

### OANDA:
- Apalancamiento: Maximo 50:1 (USA), 30:1 (EU)
- Spread: Variable segun par
- Horarios: Forex 24/5 (lunes a viernes)

### GENERAL:
- Comenzar siempre en DEMO
- Probar al menos 1 mes antes de real
- Depositar solo capital que puedas perder
- Monitorear el sistema constantemente
- Respetar limites de riesgo

## FUNCIONALIDADES AVANZADAS

### 1. Trading Automatico

En Configuracion:
- Activar "Trading Automatico"
- El sistema ejecutara senales de IA automaticamente
- Monitorear constantemente

### 2. Graficos Avanzados

- Click derecho en grafico para opciones
- Agregar indicadores
- Cambiar timeframe
- Exportar imagen

### 3. Exportar Datos

- Historial de Trades -> Exportar CSV
- Analizar en Excel
- Crear reportes personalizados

### 4. Alertas

- Configurar alertas de precio
- Notificaciones de Telegram
- Alertas de drawdown

## SOPORTE

- GitHub Issues: Reportar bugs
- Email: soporte@tradingsystem.com
- Telegram: @TradingSystemAI

## ACTUALIZACIONES

Para actualizar la aplicacion:

```bash
cd c:\xampp\htdocs\Trading\Trading
git pull
pip install --upgrade -r requirements.txt
```

---

Desarrollado con cuidado para traders algoritmicos
