# 🔧 SOLUCIÓN - ERROR AL CONECTAR BROKER

## ❌ PROBLEMA ACTUAL

Veo en tu pantalla:
- ✅ API Key y Secret correctos (de Binance)
- ❌ Error: "No se pudo conectar el broker"
- ❌ Estado: "Desconectado"

**Causa:** La API REST no está corriendo o hay un problema de endpoints.

---

## ✅ SOLUCIÓN INMEDIATA

### **PASO 1: Cerrar Todo**
1. Cerrar la aplicación TradePro
2. Cerrar cualquier ventana de API que esté abierta
3. Cerrar todas las terminales

### **PASO 2: Iniciar Sistema Correctamente**

```powershell
.\start_binance_real.bat
```

**Deberías ver 2 ventanas:**
1. **Ventana 1:** API corriendo (fondo negro con logs)
2. **Ventana 2:** GUI de TradePro

**Espera 5 segundos** para que la API inicie completamente.

### **PASO 3: Verificar API**

Abre navegador y ve a: http://127.0.0.1:8001/health

**Deberías ver:**
```json
{
  "status": "ok",
  "timestamp": "2025-10-23T...",
  "system_initialized": false
}
```

Si ves esto, la API está corriendo ✅

### **PASO 4: Conectar Broker**

1. En TradePro, ir a **Settings**
2. Ingresar tus credenciales:
   - **API Key:** (la que tienes en Binance)
   - **API Secret:** (el que copiaste)
3. ⚠️ **IMPORTANTE:** 
   - Para **TRADING REAL**: DESMARCAR "Usar Testnet"
   - Para **PRUEBAS**: MARCAR "Usar Testnet"
4. Click **"Conectar Broker"**
5. Esperar 10-15 segundos
6. Debe cambiar a: **"● Conectado"** (verde)

---

## 🔍 DIAGNÓSTICO

### **Si la API NO inicia:**

**Error: "WinError 10013" (Puerto ocupado)**

**Solución:**
```powershell
# Matar proceso en puerto 8001
netstat -ano | findstr :8001
taskkill /PID [número_del_proceso] /F

# Luego reiniciar
.\start_binance_real.bat
```

### **Si API inicia pero no conecta:**

**Verificar logs de la API:**
- En la ventana negra de la API verás logs
- Busca errores en rojo
- Copia el error y léelo

**Errores comunes:**

1. **"Invalid API Key"**
   - API Key incorrecta
   - Verifica en Binance que esté activa
   - Copia de nuevo (sin espacios)

2. **"Signature invalid"**
   - API Secret incorrecta
   - Copia de nuevo el Secret
   - Asegúrate de no tener espacios

3. **"IP not whitelisted"**
   - Tu IP no está en la whitelist
   - Ve a Binance → API Management
   - Quita restricción de IP o agrega tu IP

4. **"Permission denied"**
   - API Key sin permisos de trading
   - Ve a Binance → API Management
   - Habilita "Enable Spot & Margin Trading"

---

## 📝 CHECKLIST

Antes de conectar, verifica:

- [ ] API corriendo (ventana negra con logs)
- [ ] http://127.0.0.1:8001/health responde
- [ ] API Key copiada correctamente (sin espacios)
- [ ] API Secret copiada correctamente
- [ ] API Key tiene permisos de trading en Binance
- [ ] "Usar Testnet" configurado correctamente:
  - ❌ Desmarcado = Trading REAL
  - ✅ Marcado = Trading DEMO (Testnet)

---

## 🚀 MÉTODO ALTERNATIVO (Manual)

Si el script automático falla:

### **Terminal 1 - API:**
```powershell
.\venv\Scripts\python.exe -m uvicorn src.api.trading_api:app --reload --port 8001
```

Espera ver:
```
INFO: Uvicorn running on http://127.0.0.1:8001
INFO: Application startup complete.
```

### **Terminal 2 - GUI:**
```powershell
.\venv\Scripts\python.exe launch_app.py
```

---

## ⚠️ TRADING REAL vs TESTNET

### **Para TRADING REAL (dinero real):**
1. API Key de Binance.com (cuenta real)
2. **DESMARCAR** "Usar Testnet"
3. Trades se ejecutan en tu cuenta real
4. Usa tu dinero real

### **Para PRUEBAS (dinero ficticio):**
1. API Key de https://testnet.binance.vision/
2. **MARCAR** "Usar Testnet"
3. Trades se ejecutan en testnet
4. Dinero ficticio (seguro para probar)

---

## 🎯 RESUMEN RÁPIDO

```powershell
# 1. Iniciar sistema
.\start_binance_real.bat

# 2. Esperar 5 segundos

# 3. Verificar API
# Abrir: http://127.0.0.1:8001/health

# 4. En TradePro:
#    - Settings
#    - Ingresar API Key/Secret
#    - Configurar Testnet (según necesites)
#    - Conectar

# 5. Debe decir: "● Conectado" (verde)
```

---

## 📞 SI SIGUE SIN FUNCIONAR

### **Prueba esto:**

```powershell
# Test de conexión
.\venv\Scripts\python.exe test_connection.py
```

Esto te dirá exactamente qué está fallando:
- ✅ API
- ✅ Database
- ✅ TradingController

### **Revisa logs:**

**Logs de la API:**
- En la ventana negra donde corre la API
- Busca líneas en rojo (errores)

**Logs de la aplicación:**
- `logs/trading.log`
- Últimas líneas tienen los errores

---

## ✅ CUANDO FUNCIONE

Verás:
- ✅ Estado: "● Conectado" (verde)
- ✅ Balance de Binance mostrado en Dashboard
- ✅ Puedes ejecutar trades
- ✅ Trades aparecen en Portfolio

---

## 🎉 LISTO

Una vez conectado:
1. Ve a **Dashboard** → Ver tu balance real
2. Ve a **Trading** → Ejecutar trades
3. Ve a **Portfolio** → Ver posiciones
4. Ve a **Analytics** → Ver historial

**¡Tu sistema estará funcionando con Binance!** 🚀
