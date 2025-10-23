# ⚡ INICIO RÁPIDO - TRADING REAL CON TU API KEY

## 🚀 EN 5 PASOS

### **PASO 1: Obtener API Key de Binance** (5 min)

1. Login en https://www.binance.com
2. Perfil → **API Management**
3. **Create API** → System Generated
4. Nombre: `TradePro`
5. Habilitar permisos:
   - ✅ **Enable Reading**
   - ✅ **Enable Spot & Margin Trading**
   - ❌ **NO habilitar Withdrawals**
6. Copiar **API Key** y **Secret Key**
7. Guardar en lugar seguro

---

### **PASO 2: Iniciar Sistema** (30 seg)

```powershell
.\start_binance_real.bat
```

Esto abre:
- API en puerto 8001
- GUI de la aplicación

---

### **PASO 3: Conectar Broker** (1 min)

1. En la app, ir a **"⚙️ Settings"**
2. Sección "Conexión a Broker"
3. **Broker:** Binance
4. **API Key:** *pegar tu key*
5. **API Secret:** *pegar tu secret*
6. ⚠️ **DESMARCAR "Usar Testnet"** (IMPORTANTE)
7. Click **"🔌 Conectar Broker"**
8. Esperar: **"✅ Broker binance conectado exitosamente"**
9. Estado: **"● Conectado"** (verde, sin "Demo")

---

### **PASO 4: Verificar Balance** (10 seg)

1. Ir a **"🏠 Dashboard"**
2. Verificar que el balance sea tu balance REAL de Binance
3. Debe coincidir con Binance.com

---

### **PASO 5: Ejecutar Primer Trade** (1 min)

1. Ir a **"📊 Trading"**
2. Configurar:
   - **Símbolo:** BTCUSDT
   - **Cantidad:** 0.0001 (pequeño para probar)
   - **Lado:** BUY
3. Click **"🟢 COMPRAR"**
4. Confirmar
5. ✅ Trade ejecutado en tu cuenta REAL

---

## ✅ VERIFICAR QUE FUNCIONA

### **En la App:**
1. Ir a **"💼 Portfolio"**
2. Ver tu posición abierta
3. P&L en tiempo real

### **En Binance.com:**
1. Login en Binance
2. **Orders** → **Trade History**
3. Ver tu trade ejecutado desde TradePro

---

## 🔴 CERRAR POSICIÓN

1. En **Portfolio**, click **"Cerrar"**
2. Confirmar
3. Ver P&L final
4. Balance actualizado

---

## ⚠️ IMPORTANTE

### **Antes de Empezar:**
- ✅ Solo usa dinero que puedes perder
- ✅ Comienza con cantidades pequeñas ($10-50)
- ✅ Usa Stop Loss siempre
- ✅ Verifica que "Testnet" esté DESMARCADO
- ❌ NO habilites Withdrawals en API Key

### **Verificar Modo Real:**
- ✅ Estado: "● Conectado" (verde)
- ❌ NO debe decir "(Demo)"
- ❌ NO debe decir "Testnet"
- ✅ Balance coincide con Binance.com

---

## 🛡️ SEGURIDAD

### **API Key:**
- ✅ Solo permisos de lectura y trading
- ❌ NO habilitar withdrawals
- ✅ Restricción por IP (opcional)
- ⚠️ Nunca compartir

### **Trading:**
- 💰 Empieza pequeño
- 🛡️ Usa Stop Loss
- 📊 Monitorea tus trades
- 📈 Aprende y mejora

---

## 🚀 COMANDOS

### **Iniciar:**
```powershell
.\start_binance_real.bat
```

### **Verificar:**
```powershell
.\venv\Scripts\python.exe test_connection.py
```

---

## 📊 EJEMPLO RÁPIDO

```
1. Conectar broker (sin Testnet)
2. Ir a Trading
3. BTCUSDT, 0.0001, BUY
4. Click COMPRAR
5. Ver en Portfolio
6. Cerrar cuando quieras
7. Ver P&L
```

---

## ✅ LISTO

**Tu sistema está configurado para trading REAL.**

**Los trades usarán tu dinero real de Binance.**

**Lee `TRADING_REAL_BINANCE.md` para guía completa.**

**¡Buena suerte!** 🚀📈
