# 🚀 GUÍA DE INICIO RÁPIDO - TRADEPRO CON BINANCE

## ✅ TUS CREDENCIALES YA ESTÁN CONFIGURADAS

Las credenciales de Binance ya están guardadas en la base de datos:
- ✅ API Key: `AsJ3UTzFTu...FMTC`
- ✅ API Secret: Guardada
- ✅ Permisos de trading: Habilitados
- ✅ Conexión probada: Exitosa

---

## 🎯 INICIAR EL SISTEMA (3 PASOS)

### **PASO 1: Ejecutar el script de inicio**

```powershell
.\iniciar_sistema_completo.bat
```

**Se abrirán 2 ventanas:**
1. **Ventana API** (fondo negro) - **NO LA CIERRES**
2. **Ventana TradePro** (aplicación)

**Espera 10 segundos** para que la API inicie completamente.

---

### **PASO 2: Conectar el broker en la app**

1. En TradePro, ve a **⚙️ Settings**
2. Verás que tus credenciales **ya están cargadas**:
   - API Key: `AsJ3UTzFTu...`
   - API Secret: `***********`
3. **MUY IMPORTANTE:** 
   - ✅ **DESMARCA** "Usar Testnet" (para usar tu cuenta real)
   - ❌ Si lo dejas marcado, intentará conectar a testnet
4. Click **"🔌 Conectar Broker"**
5. **Espera 20-30 segundos**
6. Debe cambiar a: **"● Conectado"** (verde)

---

### **PASO 3: Verificar conexión**

1. Ve a **🏠 Dashboard**
2. Deberías ver:
   - Balance: Tu balance real de Binance
   - Stats actualizadas
3. Si ves datos, ¡está funcionando! ✅

---

## 🔍 VERIFICAR QUE TODO FUNCIONA

### **Test 1: API corriendo**
Abre navegador: http://127.0.0.1:8001/health

Deberías ver:
```json
{"status":"ok","timestamp":"..."}
```

### **Test 2: Documentación API**
Abre: http://127.0.0.1:8001/docs

Deberías ver la interfaz de FastAPI con todos los endpoints.

### **Test 3: Conexión a Binance**
En la ventana de la API (negra) deberías ver logs como:
```
INFO: Conectando broker: binance
INFO: ✅ Broker binance conectado
```

---

## ❌ SI NO FUNCIONA

### **Problema 1: "No se pudo conectar al broker"**

**Causa:** La API no está corriendo o no responde.

**Solución:**
1. Verifica que la ventana de la API esté abierta
2. En la ventana API, busca errores en rojo
3. Abre: http://127.0.0.1:8001/health
4. Si no responde, cierra todo y ejecuta de nuevo

### **Problema 2: "Error desconocido"**

**Causa:** Timeout o problema de red.

**Solución:**
1. Espera más tiempo (hasta 30 segundos)
2. Verifica tu conexión a internet
3. Intenta conectar de nuevo

### **Problema 3: Credenciales no aparecen**

**Causa:** No se cargaron de la base de datos.

**Solución:**
1. Cierra la app
2. Ejecuta: `python test_binance_auto.py`
3. Esto guardará las credenciales de nuevo
4. Abre la app de nuevo

### **Problema 4: Balance no se muestra**

**Causa:** No está conectado al broker o no hay fondos.

**Solución:**
1. Verifica que diga "● Conectado" (verde)
2. Tu cuenta tiene muy poco balance ($0.00 USDT)
3. Deposita fondos en Binance o usa Testnet

---

## 💰 SOBRE TU BALANCE

**Tu cuenta actual:**
- Balance: 0.00963125 COP (~$0.00 USDT)
- Muy poco para operar

**Opciones:**

### **Opción A: Depositar fondos (Real)**
1. Ve a Binance.com
2. Wallet → Deposit
3. Deposita USDT, BTC, etc.
4. Espera confirmación
5. Opera desde TradePro

### **Opción B: Usar Testnet (Demo)**
1. Ve a: https://testnet.binance.vision/
2. Login con GitHub
3. Generate API Key
4. Obtienes $100,000 USDT ficticios
5. Actualiza credenciales en la app
6. Marca "Usar Testnet"
7. Perfecto para probar sin riesgo

---

## 📊 CÓMO USAR LA APP

### **1. Dashboard**
- Ver balance en tiempo real
- Ver P&L del día
- Ver estadísticas

### **2. Trading**
- Ejecutar trades manuales
- Configurar Stop Loss y Take Profit
- Ver confirmación de trades

### **3. Portfolio**
- Ver posiciones abiertas
- Cerrar posiciones
- Ver P&L en tiempo real

### **4. Analytics**
- Ver historial de trades
- Ver métricas de performance
- Analizar resultados

### **5. AI Agents**
- Activar trading automático
- 6 agentes de IA trabajando
- Configurar parámetros

### **6. Settings**
- Conectar/desconectar broker
- Configurar parámetros
- Ver perfil

---

## 🎯 EJEMPLO DE USO

### **Ejecutar un trade:**

1. Ve a **📊 Trading**
2. Configura:
   - Símbolo: BTCUSDT
   - Cantidad: 0.0001 BTC
   - Lado: BUY
3. Click **"🟢 COMPRAR"**
4. Confirmar
5. Ver trade en **💼 Portfolio**
6. Cerrar cuando quieras

**Nota:** Necesitas fondos suficientes en tu cuenta.

---

## ⚠️ IMPORTANTE

### **Trading Real:**
- ✅ Desmarca "Usar Testnet"
- ✅ Usa tu dinero real
- ✅ Ganancias y pérdidas reales
- ⚠️ Comienza con cantidades pequeñas

### **Testnet (Demo):**
- ✅ Marca "Usar Testnet"
- ✅ Dinero ficticio
- ✅ Sin riesgo
- ✅ Perfecto para aprender

---

## 🚀 COMANDOS RÁPIDOS

### **Iniciar sistema:**
```powershell
.\iniciar_sistema_completo.bat
```

### **Probar conexión:**
```powershell
python test_binance_auto.py
```

### **Solo API:**
```powershell
.\venv\Scripts\python.exe -m uvicorn src.api.trading_api:app --reload --port 8001
```

### **Solo GUI:**
```powershell
.\venv\Scripts\python.exe launch_app.py
```

---

## ✅ CHECKLIST

Antes de operar:

- [ ] API corriendo (ventana negra abierta)
- [ ] http://127.0.0.1:8001/health responde
- [ ] TradePro abierto
- [ ] Settings → Credenciales cargadas
- [ ] "Usar Testnet" configurado correctamente
- [ ] Click "Conectar Broker"
- [ ] Estado: "● Conectado" (verde)
- [ ] Dashboard muestra balance
- [ ] Tienes fondos suficientes

---

## 🎉 ¡LISTO!

**Tu sistema está configurado y listo para usar.**

**Ejecuta:**
```powershell
.\iniciar_sistema_completo.bat
```

**Y sigue los 3 pasos de arriba.** 🚀📈💰
