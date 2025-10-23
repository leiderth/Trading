# 🧪 GUÍA COMPLETA - BINANCE TESTNET

## 🎯 ¿QUÉ ES TESTNET?

**Binance Testnet** es un ambiente de prueba donde puedes:
- ✅ Operar con **dinero ficticio**
- ✅ Probar estrategias **sin riesgo**
- ✅ Aprender a usar la plataforma
- ✅ Obtener **miles de dólares** en criptomonedas de prueba
- ✅ Mismo funcionamiento que Binance real

**Perfecto para:** Aprender, probar, desarrollar estrategias.

---

## 🚀 PASO 1: OBTENER CREDENCIALES

### **1. Ir a Binance Testnet:**
```
https://testnet.binance.vision/
```

### **2. Login con GitHub:**
- Click **"Login with GitHub"**
- Si no tienes cuenta de GitHub, créala gratis en https://github.com
- Autoriza la aplicación

### **3. Dashboard:**
Verás una pantalla con:
- Tu balance (inicialmente en 0)
- Opciones para generar API Keys
- Opciones para obtener fondos de prueba

### **4. Generar API Key:**
- Busca el botón **"Generate HMAC_SHA256 Key"**
- Click en el botón
- Se generarán automáticamente:
  - **API Key** (64 caracteres)
  - **Secret Key** (64 caracteres)
- **⚠️ IMPORTANTE:** Copia ambas INMEDIATAMENTE
- El Secret Key solo se muestra UNA VEZ

**Ejemplo:**
```
API Key: abc123def456...xyz789
Secret Key: 123abc456def...789xyz
```

### **5. Obtener fondos de prueba:**
En el dashboard verás botones como:
- **"Get BNB"** - Recibe BNB de prueba
- **"Get BTC"** - Recibe BTC de prueba
- **"Get USDT"** - Recibe USDT de prueba
- **"Get ETH"** - Recibe ETH de prueba

**Click en cada uno** para recibir fondos ficticios.

**Recibirás algo como:**
- 10 BTC (~$1,000,000 USD)
- 100,000 USDT
- 1,000 BNB
- 100 ETH

---

## 📝 PASO 2: CONFIGURAR EN TRADEPRO

### **Opción A: Usar script automático (Recomendado)**

**1. Editar el archivo:**
```powershell
notepad configurar_testnet.py
```

**2. Pegar tus credenciales:**
Busca las líneas 11-12 y reemplaza:
```python
TESTNET_API_KEY = "PEGA_TU_API_KEY_DE_TESTNET_AQUI"
TESTNET_API_SECRET = "PEGA_TU_SECRET_KEY_DE_TESTNET_AQUI"
```

Por tus credenciales reales:
```python
TESTNET_API_KEY = "abc123def456...xyz789"
TESTNET_API_SECRET = "123abc456def...789xyz"
```

**3. Guardar y ejecutar:**
```powershell
python configurar_testnet.py
```

**Deberías ver:**
```
✅ Credenciales de testnet guardadas
✅ CONEXIÓN A TESTNET EXITOSA
💰 BALANCES DE TESTNET:
  BTC: 10.00000000
  USDT: 100000.00000000
  ...
🎉 TESTNET CONFIGURADO EXITOSAMENTE
```

### **Opción B: Configurar manualmente en la GUI**

**1. Abrir TradePro:**
```powershell
python launch_app.py
```

**2. Ir a Settings**

**3. Ingresar credenciales:**
- API Key: [Pega tu API Key de testnet]
- API Secret: [Pega tu Secret Key de testnet]
- **✅ MARCAR "Usar Testnet"** ← MUY IMPORTANTE

**4. Guardar configuración:**
- Click "💾 Guardar Configuración"

**5. Conectar:**
- Click "🔌 Conectar Broker"
- Espera 20-30 segundos
- Debe decir: **"● Conectado"** (verde)

---

## ✅ PASO 3: VERIFICAR CONEXIÓN

### **En Dashboard deberías ver:**
- Balance: Tu balance de testnet (ej: $100,000 USDT)
- Posiciones: 0 (inicialmente)
- P&L: $0.00

### **Puedes operar:**
1. Ve a **📊 Trading**
2. Selecciona par: BTCUSDT
3. Cantidad: 0.001 BTC
4. Click **"🟢 COMPRAR"**
5. ¡Trade ejecutado con dinero ficticio!

---

## 🔄 CAMBIAR ENTRE MAINNET Y TESTNET

### **Para usar TESTNET:**
1. Settings
2. **✅ MARCAR** "Usar Testnet"
3. Ingresar credenciales de testnet
4. Conectar

### **Para usar MAINNET (Real):**
1. Settings
2. **❌ DESMARCAR** "Usar Testnet"
3. Ingresar credenciales reales
4. Conectar

---

## 📊 DIFERENCIAS TESTNET vs MAINNET

| Característica | TESTNET | MAINNET |
|----------------|---------|---------|
| Dinero | Ficticio | Real |
| Riesgo | Ninguno | Alto |
| Ganancias | Ficticias | Reales |
| Pérdidas | Ficticias | Reales |
| Fondos iniciales | Gratis | Debes depositar |
| Precio BTC | Real | Real |
| API | testnet.binance.vision | api.binance.com |
| Perfecto para | Aprender/Probar | Trading real |

---

## 🎯 CASOS DE USO

### **Usa TESTNET para:**
- ✅ Aprender a usar TradePro
- ✅ Probar estrategias nuevas
- ✅ Testear los AI Agents
- ✅ Practicar sin riesgo
- ✅ Desarrollar y debuggear

### **Usa MAINNET para:**
- ✅ Trading real
- ✅ Ganancias reales
- ✅ Cuando ya dominas la plataforma

---

## ⚠️ IMPORTANTE

### **Sobre TESTNET:**
- ✅ Dinero 100% ficticio
- ✅ Sin riesgo alguno
- ✅ Mismo funcionamiento que real
- ✅ Precios reales de mercado
- ⚠️ Las ganancias NO son reales
- ⚠️ No puedes retirar fondos

### **Sobre MAINNET:**
- ⚠️ Dinero 100% real
- ⚠️ Riesgo de pérdidas reales
- ⚠️ Comienza con cantidades pequeñas
- ⚠️ Usa Stop Loss siempre
- ⚠️ No inviertas más de lo que puedes perder

---

## 🧪 EJEMPLO DE USO

### **1. Configurar testnet:**
```powershell
# Editar archivo
notepad configurar_testnet.py

# Pegar credenciales
# Guardar

# Ejecutar
python configurar_testnet.py
```

### **2. Abrir TradePro:**
```powershell
python launch_app.py
```

### **3. Verificar en Settings:**
- API Key: [Tu key de testnet]
- API Secret: [Tu secret de testnet]
- ✅ "Usar Testnet" MARCADO

### **4. Conectar:**
- Click "Conectar Broker"
- Espera 30 segundos
- ✅ "Conectado"

### **5. Ver balance:**
- Dashboard → Balance: $100,000+ USDT

### **6. Ejecutar trade de prueba:**
- Trading → BTCUSDT
- Cantidad: 0.001 BTC
- Click "COMPRAR"
- ✅ Trade ejecutado

### **7. Ver resultado:**
- Portfolio → Ver posición abierta
- Analytics → Ver historial

---

## 🔍 TROUBLESHOOTING

### **Problema: "Invalid API Key"**
**Solución:**
- Verifica que copiaste la API Key completa
- Asegúrate de usar credenciales de TESTNET
- Genera nuevas credenciales si es necesario

### **Problema: "Signature invalid"**
**Solución:**
- Verifica que copiaste el Secret completo
- No debe tener espacios al inicio/final
- Genera nuevas credenciales

### **Problema: "No se puede conectar"**
**Solución:**
- Verifica que "Usar Testnet" esté MARCADO
- Verifica tu conexión a internet
- Prueba con: `python configurar_testnet.py`

### **Problema: Balance en $0**
**Solución:**
- Ve a https://testnet.binance.vision/
- Click en los botones "Get BTC", "Get USDT", etc.
- Espera unos segundos
- Refresca TradePro

---

## 📚 RECURSOS

### **Links útiles:**
- Testnet: https://testnet.binance.vision/
- Documentación: https://testnet.binance.vision/docs
- GitHub: https://github.com (para login)

### **Scripts útiles:**
- `configurar_testnet.py` - Configurar credenciales
- `test_api_connection.py` - Probar conexión
- `ver_credenciales.py` - Ver credenciales guardadas

---

## 🎉 RESUMEN

**Para usar TESTNET:**

1. ✅ Ir a https://testnet.binance.vision/
2. ✅ Login con GitHub
3. ✅ Generate API Key
4. ✅ Get fondos de prueba (BTC, USDT, etc.)
5. ✅ Ejecutar: `python configurar_testnet.py`
6. ✅ Pegar credenciales en el archivo
7. ✅ Ejecutar de nuevo
8. ✅ Abrir TradePro
9. ✅ Settings → Verificar "Usar Testnet" MARCADO
10. ✅ Conectar → ¡Listo!

**¡Ahora puedes operar sin riesgo!** 🚀📈💰
