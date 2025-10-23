# 🏦 GUÍA COMPLETA: INTERACTIVE BROKERS

## 📋 TABLA DE CONTENIDOS

1. [Qué es Interactive Brokers](#qué-es-interactive-brokers)
2. [Requisitos](#requisitos)
3. [Instalación TWS/Gateway](#instalación-twsgateway)
4. [Configuración](#configuración)
5. [Conectar con la App](#conectar-con-la-app)
6. [Trading](#trading)
7. [Símbolos Soportados](#símbolos-soportados)
8. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 QUÉ ES INTERACTIVE BROKERS

**Interactive Brokers (IB)** es un broker profesional que ofrece:

- ✅ **Acciones** (NYSE, NASDAQ, etc.)
- ✅ **Forex** (EUR/USD, GBP/USD, etc.)
- ✅ **Futuros** (ES, NQ, CL, GC, etc.)
- ✅ **Opciones** (Calls, Puts)
- ✅ **Bonos, CFDs, Criptomonedas**

### **Ventajas:**
- 🌍 Acceso a 150+ mercados globales
- 💰 Comisiones muy bajas
- 🔒 Regulado (SEC, FCA, etc.)
- 📊 API profesional (TWS API)
- 💵 Paper Trading gratuito

### **Desventajas:**
- 📚 Curva de aprendizaje alta
- 💰 Mínimo de $10,000 (cuenta real)
- 🔧 Requiere TWS/Gateway instalado

---

## 📋 REQUISITOS

### **Software:**
1. **TWS (Trader Workstation)** o **IB Gateway**
2. **Cuenta de Interactive Brokers** (real o paper)
3. **Trading System Pro** (tu aplicación)

### **Cuenta:**
- **Paper Trading:** Gratis, sin depósito
- **Cuenta Real:** Mínimo $10,000 USD

---

## 🚀 INSTALACIÓN TWS/GATEWAY

### **OPCIÓN 1: TWS (Trader Workstation)** - Recomendado para principiantes

1. **Descargar TWS:**
   - Ir a: https://www.interactivebrokers.com/en/trading/tws.php
   - Descargar versión para tu sistema operativo
   - Instalar

2. **Crear cuenta Paper Trading:**
   - Ir a: https://www.interactivebrokers.com/en/index.php?f=1286
   - Click "Open Paper Trading Account"
   - Completar formulario
   - Recibirás credenciales por email

3. **Iniciar TWS:**
   - Abrir TWS
   - Ingresar usuario y contraseña (paper)
   - Click "Login"

---

### **OPCIÓN 2: IB Gateway** - Recomendado para trading automatizado

1. **Descargar Gateway:**
   - Ir a: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
   - Descargar e instalar

2. **Iniciar Gateway:**
   - Abrir IB Gateway
   - Ingresar credenciales
   - Click "Login"

**Ventajas del Gateway:**
- Más ligero que TWS
- Menos recursos
- Ideal para bots

---

## ⚙️ CONFIGURACIÓN

### **PASO 1: Habilitar API en TWS/Gateway**

1. **Abrir TWS o Gateway**
2. **Ir a configuración:**
   - TWS: File → Global Configuration → API → Settings
   - Gateway: Configure → Settings → API → Settings

3. **Habilitar API:**
   - ✅ **Enable ActiveX and Socket Clients**
   - ✅ **Allow connections from localhost only** (por seguridad)
   - ✅ **Read-Only API** (desmarcar si quieres ejecutar órdenes)
   - **Socket Port:** 
     - Paper: 7497 (TWS) o 4002 (Gateway)
     - Live: 7496 (TWS) o 4001 (Gateway)

4. **Click "OK"**

5. **Reiniciar TWS/Gateway**

---

### **PASO 2: Verificar Conexión**

1. **TWS/Gateway debe estar corriendo**
2. **Verificar que el puerto esté abierto:**
   ```powershell
   netstat -an | findstr "7497"
   ```
   Debe mostrar: `TCP 0.0.0.0:7497 LISTENING`

---

## 🖥️ CONECTAR CON LA APP

### **PASO 1: Iniciar TWS/Gateway**

1. Abrir TWS o IB Gateway
2. Iniciar sesión (paper o live)
3. Esperar a que esté completamente cargado

---

### **PASO 2: Iniciar Trading System Pro**

```powershell
.\start_trading_app.bat
```

---

### **PASO 3: Iniciar Sistema**

1. Click **"▶ Iniciar"**
2. Esperar 10 segundos
3. Verificar "● Sistema Ejecutando"

---

### **PASO 4: Conectar Interactive Brokers**

1. Click **"🔌 Conectar Broker"**
2. Seleccionar **"Interactive Brokers"**
3. Configurar:
   - **Host:** `127.0.0.1` (localhost)
   - **Puerto:**
     - TWS Paper: `7497`
     - TWS Live: `7496`
     - Gateway Paper: `4002`
     - Gateway Live: `4001`
   - **Client ID:** `1` (único por conexión)
   - ✅ **Paper Trading** (marcar si usas paper)
4. Click **"Conectar"**
5. Esperar 5 segundos
6. Verificar: **"Broker: Interactive Brokers"**

---

## 📊 TRADING

### **PASO 1: Seleccionar Símbolo**

En el **Panel de Trading:**

**Acciones:**
- `AAPL` (Apple)
- `TSLA` (Tesla)
- `MSFT` (Microsoft)
- `GOOGL` (Google)

**Forex:**
- `EUR.USD` (Euro/Dólar)
- `GBP.USD` (Libra/Dólar)
- `USD.JPY` (Dólar/Yen)

**Futuros:**
- `ES` (E-mini S&P 500)
- `NQ` (E-mini NASDAQ)
- `CL` (Crude Oil)
- `GC` (Gold)

---

### **PASO 2: Actualizar Precio**

1. Click **"🔄 Actualizar Precio"**
2. Verás:
   - **Bid:** Precio de venta
   - **Ask:** Precio de compra
   - **Spread:** Diferencia

---

### **PASO 3: Configurar Operación**

**Ejemplo: Comprar Apple (AAPL)**

- **Símbolo:** `AAPL`
- **Cantidad:** `10` (10 acciones)
- **Stop Loss:** `150.00` (precio de stop)
- **Take Profit:** `160.00` (precio objetivo)

---

### **PASO 4: Ejecutar Orden**

1. Click **"🟢 COMPRAR"** o **"🔴 VENDER"**
2. Confirmar
3. La orden se ejecuta en IB
4. Aparece en **"Posiciones Abiertas"**

---

### **PASO 5: Monitorear Posición**

En **"Posiciones Abiertas":**
- Ver P&L en tiempo real
- Ver precio actual
- Cerrar manualmente si quieres

**Stop Loss/Take Profit:**
- Se ejecutan automáticamente
- Cuando el precio llega a SL → Cierra
- Cuando el precio llega a TP → Cierra

---

## 📈 SÍMBOLOS SOPORTADOS

### **ACCIONES (Stocks)**

Formato: `SÍMBOLO`

Ejemplos:
- `AAPL` - Apple
- `TSLA` - Tesla
- `MSFT` - Microsoft
- `GOOGL` - Google
- `AMZN` - Amazon
- `META` - Meta (Facebook)
- `NVDA` - NVIDIA
- `AMD` - AMD

**Cantidades mínimas:** 1 acción

---

### **FOREX**

Formato: `BASE.QUOTE`

Ejemplos:
- `EUR.USD` - Euro/Dólar
- `GBP.USD` - Libra/Dólar
- `USD.JPY` - Dólar/Yen
- `AUD.USD` - Dólar Australiano/Dólar
- `USD.CAD` - Dólar/Dólar Canadiense

**Cantidades mínimas:** 20,000 unidades (0.2 lotes)

---

### **FUTUROS**

Formato: `SÍMBOLO`

Ejemplos:
- `ES` - E-mini S&P 500
- `NQ` - E-mini NASDAQ
- `YM` - E-mini Dow Jones
- `RTY` - E-mini Russell 2000
- `CL` - Crude Oil
- `GC` - Gold
- `SI` - Silver
- `NG` - Natural Gas

**Cantidades mínimas:** 1 contrato

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### **Error: "No se pudo conectar a IB"**

**Causas:**
1. TWS/Gateway no está corriendo
2. Puerto incorrecto
3. API no habilitada

**Solución:**
1. Verificar que TWS/Gateway esté abierto
2. Verificar puerto en configuración de API
3. Habilitar API en TWS/Gateway
4. Reiniciar TWS/Gateway

---

### **Error: "Connection refused"**

**Causa:** Puerto bloqueado o incorrecto

**Solución:**
1. Verificar puerto:
   ```powershell
   netstat -an | findstr "7497"
   ```
2. Si no aparece, TWS no está escuchando
3. Verificar configuración de API en TWS
4. Reiniciar TWS

---

### **Error: "Read-Only API"**

**Causa:** API configurada en modo solo lectura

**Solución:**
1. TWS: File → Global Configuration → API → Settings
2. **Desmarcar** "Read-Only API"
3. Click "OK"
4. Reiniciar TWS

---

### **Error: "Invalid symbol"**

**Causa:** Símbolo no existe o formato incorrecto

**Solución:**
1. Verificar símbolo en IB
2. Usar formato correcto:
   - Acciones: `AAPL`
   - Forex: `EUR.USD`
   - Futuros: `ES`

---

### **Error: "Insufficient margin"**

**Causa:** No hay suficiente margen para la operación

**Solución:**
1. Reducir cantidad
2. Depositar más fondos
3. Cerrar otras posiciones

---

### **Órdenes no se ejecutan**

**Causas:**
1. Mercado cerrado
2. Precio fuera de rango
3. Cuenta sin permisos

**Solución:**
1. Verificar horario de mercado
2. Usar precio de mercado actual
3. Verificar permisos de cuenta

---

## 📊 HORARIOS DE MERCADO

### **Acciones USA:**
- **Pre-market:** 4:00 AM - 9:30 AM EST
- **Regular:** 9:30 AM - 4:00 PM EST
- **After-hours:** 4:00 PM - 8:00 PM EST

### **Forex:**
- **24 horas** (Lunes a Viernes)
- Cierra: Viernes 5:00 PM EST
- Abre: Domingo 5:00 PM EST

### **Futuros:**
- **Casi 24 horas** (depende del contrato)
- ES/NQ: Domingo 6:00 PM - Viernes 5:00 PM EST

---

## 💰 COMISIONES

### **Acciones:**
- **IB Pro:** $0.005 por acción (mínimo $1)
- **IB Lite:** $0 (pero peor ejecución)

### **Forex:**
- **Spread:** Variable según par
- **Comisión:** $0.20 por 1,000 unidades

### **Futuros:**
- **ES/NQ:** $0.85 por contrato
- **CL/GC:** $1.50 por contrato

---

## 🔒 SEGURIDAD

### **Recomendaciones:**

1. ✅ **Usar Paper Trading** primero
2. ✅ **Habilitar 2FA** en IB
3. ✅ **Restringir API a localhost**
4. ✅ **No compartir credenciales**
5. ✅ **Monitorear constantemente**
6. ✅ **Usar Stop Loss siempre**

---

## 📚 RECURSOS

### **Documentación:**
- **IB API:** https://interactivebrokers.github.io/tws-api/
- **ib_insync:** https://ib-insync.readthedocs.io/
- **TWS Guide:** https://www.interactivebrokers.com/en/software/tws/usersguidebook.htm

### **Soporte:**
- **IB Support:** https://www.interactivebrokers.com/en/support/contact.php
- **Chat:** 24/7 en IB website

---

## ✅ CHECKLIST

Antes de operar con dinero real:

- [ ] Cuenta IB creada y verificada
- [ ] TWS/Gateway instalado
- [ ] API habilitada en TWS
- [ ] Probado en Paper Trading (50+ trades)
- [ ] Win Rate > 55% en paper
- [ ] Stop Loss configurado siempre
- [ ] Entendido comisiones y márgenes
- [ ] Horarios de mercado conocidos
- [ ] Capital que puedo perder

---

## 🎯 RESUMEN RÁPIDO

```
1. Crear cuenta Paper Trading en IB
2. Descargar e instalar TWS
3. Habilitar API en TWS (puerto 7497)
4. Iniciar TWS
5. Iniciar Trading System Pro
6. Click "Iniciar"
7. Click "Conectar Broker" → Interactive Brokers
8. Host: 127.0.0.1, Puerto: 7497, Client ID: 1
9. Conectar
10. Seleccionar símbolo (ej: AAPL)
11. Actualizar precio
12. Configurar cantidad, SL, TP
13. COMPRAR o VENDER
14. Monitorear en "Posiciones Abiertas"
```

---

**¡Listo para operar con Interactive Brokers!** 🚀📈

**Recuerda:** Siempre comenzar en Paper Trading y probar exhaustivamente antes de usar dinero real.
