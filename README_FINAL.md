# 🚀 TRADEPRO - GUÍA DEFINITIVA

## ✅ ESTADO ACTUAL

### **Lo que funciona:**
- ✅ Credenciales guardadas en base de datos
- ✅ Credenciales se cargan automáticamente en Settings
- ✅ Conexión a Binance probada y funcionando
- ✅ Permisos de trading habilitados
- ✅ Base de datos funcionando
- ✅ GUI funcionando

### **Lo que falta:**
- ❌ Iniciar la API REST antes de usar la app

---

## 🎯 SOLUCIÓN DEFINITIVA (SIMPLE)

### **Ejecuta este comando:**

```powershell
.\start.bat
```

**Eso es todo.** El script hará todo automáticamente.

---

## 📋 QUÉ HACE EL SCRIPT

1. ✅ Inicia la API en puerto 8001
2. ✅ Espera 10 segundos
3. ✅ Inicia TradePro GUI
4. ✅ Todo listo para conectar

**Se abrirán 2 ventanas:**
- **Ventana 1:** API Backend (fondo negro) - **NO CERRAR**
- **Ventana 2:** TradePro GUI (aplicación)

---

## 🔌 CÓMO CONECTAR

### **Después de ejecutar `.\start.bat`:**

1. **Espera 10 segundos** (la API necesita iniciar)
2. En TradePro, ve a **⚙️ Settings**
3. Verás tus credenciales **ya cargadas**:
   - API Key: `AsJ3UTzFTu...` ✅
   - API Secret: `***********` ✅
   - Testnet: Desmarcado ✅
4. Click **"🔌 Conectar Broker"**
5. **Espera 30 segundos** (importante)
6. Debe cambiar a: **"● Conectado"** (verde)

---

## ✅ VERIFICAR QUE TODO FUNCIONA

### **Test 1: API corriendo**
Abre navegador: http://127.0.0.1:8001/health

Deberías ver:
```json
{"status":"ok","timestamp":"...","system_initialized":false}
```

### **Test 2: Credenciales guardadas**
```powershell
python ver_credenciales.py
```

Deberías ver:
```
✅ API Key correcta
✅ API Secret correcta
```

### **Test 3: Conexión a Binance**
```powershell
python test_binance_auto.py
```

Deberías ver:
```
✅ TODAS LAS PRUEBAS EXITOSAS
```

---

## 🔧 SOLUCIÓN MANUAL (SI EL SCRIPT FALLA)

### **Terminal 1 - API:**
```powershell
cd c:\xampp\htdocs\Trading\Trading
.\venv\Scripts\python.exe -m uvicorn src.api.trading_api:app --reload --port 8001
```

**Espera ver:**
```
INFO: Uvicorn running on http://127.0.0.1:8001
INFO: Application startup complete.
```

**NO CIERRES ESTA VENTANA**

### **Terminal 2 - GUI:**
```powershell
cd c:\xampp\htdocs\Trading\Trading
.\venv\Scripts\python.exe launch_app.py
```

---

## ❌ SOLUCIÓN DE PROBLEMAS

### **Problema 1: "Error desconocido" al conectar**

**Causa:** La API no está corriendo.

**Solución:**
1. Verifica que la ventana de la API esté abierta
2. Abre: http://127.0.0.1:8001/health
3. Si no responde, reinicia la API

### **Problema 2: Puerto 8001 ocupado**

**Error:** `WinError 10013`

**Solución:**
```powershell
# Encontrar proceso
netstat -ano | findstr :8001

# Matar proceso (reemplaza 12345 con el PID)
taskkill /PID 12345 /F

# Reiniciar
.\start.bat
```

### **Problema 3: Credenciales no aparecen**

**Solución:**
```powershell
# Verificar credenciales
python ver_credenciales.py

# Si no están, guardarlas
python test_binance_auto.py
```

### **Problema 4: "No se pudo conectar al broker"**

**Causas posibles:**
1. API no está corriendo
2. Timeout (espera más tiempo)
3. Problema de red

**Solución:**
1. Verifica que la API esté corriendo
2. Espera 30-60 segundos al conectar
3. Revisa logs de la API (ventana negra)
4. Intenta de nuevo

---

## 💰 SOBRE TU BALANCE

**Tu cuenta actual:**
- Balance: ~$0.00 USDT
- No puedes operar sin fondos

**Opciones:**

### **A) Depositar en Binance (Real)**
1. Binance.com → Wallet → Deposit
2. Deposita USDT, BTC, etc.
3. Espera confirmación
4. Opera desde TradePro

### **B) Usar Testnet (Recomendado para probar)**
1. Ve a: https://testnet.binance.vision/
2. Login con GitHub
3. Click "Generate HMAC_SHA256 Key"
4. Copia API Key y Secret
5. En TradePro → Settings:
   - Pega nuevas credenciales
   - **MARCAR** "Usar Testnet"
   - Conectar
6. Obtienes $100,000 USDT ficticios
7. ¡Prueba sin riesgo!

---

## 📊 CÓMO USAR LA APP

### **1. Dashboard**
- Ver balance en tiempo real
- Ver P&L del día
- Ver estadísticas

### **2. Trading**
- Ejecutar trades manuales
- Configurar Stop Loss y Take Profit
- Ver confirmación

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
- 6 agentes de IA
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

**Nota:** Necesitas fondos suficientes.

---

## 📁 ARCHIVOS ÚTILES

### **Scripts de inicio:**
- `start.bat` - Inicia todo automáticamente ⭐
- `iniciar_sistema_completo.bat` - Alternativa
- `start_binance_real.bat` - Otra alternativa

### **Scripts de verificación:**
- `ver_credenciales.py` - Ver credenciales guardadas
- `test_binance_auto.py` - Probar conexión a Binance
- `test_connection.py` - Test general

### **Documentación:**
- `README_FINAL.md` - Esta guía ⭐
- `SOLUCION_FINAL.md` - Solución de credenciales
- `GUIA_INICIO_RAPIDO.md` - Guía rápida
- `TRADING_REAL_BINANCE.md` - Trading real
- `SOLUCION_CONEXION_BROKER.md` - Solución de conexión

---

## ⚠️ IMPORTANTE

### **Trading Real:**
- ✅ Desmarca "Usar Testnet"
- ✅ Usa tu dinero real
- ✅ Ganancias y pérdidas reales
- ⚠️ Comienza con cantidades pequeñas
- ⚠️ Usa Stop Loss siempre

### **Testnet (Demo):**
- ✅ Marca "Usar Testnet"
- ✅ Dinero ficticio
- ✅ Sin riesgo
- ✅ Perfecto para aprender

---

## 🚀 INICIO RÁPIDO

### **1. Ejecutar:**
```powershell
.\start.bat
```

### **2. Esperar:**
- 10 segundos para que la API inicie

### **3. Conectar:**
- Settings → Conectar Broker → Esperar 30 seg

### **4. Operar:**
- Dashboard → Trading → Portfolio

---

## ✅ CHECKLIST FINAL

Antes de operar:

- [ ] Ejecutado `.\start.bat`
- [ ] Ventana API abierta (fondo negro)
- [ ] Ventana TradePro abierta
- [ ] http://127.0.0.1:8001/health responde
- [ ] Settings → Credenciales cargadas
- [ ] "Usar Testnet" configurado correctamente
- [ ] Click "Conectar Broker"
- [ ] Esperado 30 segundos
- [ ] Estado: "● Conectado" (verde)
- [ ] Dashboard muestra balance
- [ ] Tienes fondos suficientes (o usas testnet)

---

## 🎉 ¡LISTO!

**Tu sistema está 100% configurado.**

**Ejecuta:**
```powershell
.\start.bat
```

**Y sigue los pasos de arriba.** 🚀📈💰

---

## 📞 SOPORTE

Si tienes problemas:

1. **Revisa los logs:**
   - Ventana de la API (fondo negro)
   - Busca errores en rojo

2. **Verifica credenciales:**
   ```powershell
   python ver_credenciales.py
   ```

3. **Prueba conexión:**
   ```powershell
   python test_binance_auto.py
   ```

4. **Reinicia todo:**
   - Cierra ambas ventanas
   - Ejecuta `.\start.bat` de nuevo

---

## 🔑 TUS CREDENCIALES

**API Key:** `AsJ3UTzFTux4wnzWQiMvYuThjgo05FlZpd6sYRKdihHZtAC4pAy1gL7O3QyiFMTC`
**API Secret:** `tbFovnluEo5BBSG8l91hXbC7hF72bSxcnbiud0xoCrQS1pOjqvTrBsScznNjNJ8N`
**Testnet:** Desactivado (MAINNET - Real)

**⚠️ Estas credenciales son para tu cuenta REAL de Binance.**

---

**¡Buena suerte con tu trading!** 🚀📈💰
