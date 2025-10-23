# ⚡ INICIO RAPIDO - APLICACION DE ESCRITORIO

## 🚀 INICIAR EN 3 PASOS (5 MINUTOS)

### PASO 1: Instalar Dependencias GUI

```bash
cd c:\xampp\htdocs\Trading\Trading
venv\Scripts\activate
pip install PyQt6 PyQt6-WebEngine pyqtgraph qdarkstyle fastapi uvicorn
```

### PASO 2: Iniciar Aplicacion

**Opcion A - Automatico (Recomendado):**

Doble click en: `start_trading_app.bat`

**Opcion B - Manual:**

Terminal 1:
```bash
python run_api.py
```

Terminal 2:
```bash
python desktop_app.py
```

### PASO 3: Conectar y Operar

1. En la app: Click "Conectar Broker"
2. Seleccionar "Quotex (Simulacion)"
3. Ingresar email y password
4. Marcar "Modo Demo"
5. Click "Conectar"
6. Click "Iniciar" en la barra superior
7. Listo!

---

## 📊 PANTALLAS DE LA APLICACION

### PANTALLA PRINCIPAL

```
┌─────────────────────────────────────────────────────────────┐
│ 🚀 TRADING SYSTEM PRO                  ● Sistema Ejecutando │
│ [▶ Iniciar] [⏸ Detener] [🔌 Conectar] [⚙ Config]          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ┌─────────────┐  ┌──────────────────┐  ┌─────────────┐   │
│ │  DASHBOARD  │  │    GRAFICO       │  │   TRADING   │   │
│ │             │  │                  │  │    PANEL    │   │
│ │ Balance:    │  │    📈            │  │             │   │
│ │ $10,000     │  │                  │  │ Simbolo:    │   │
│ │             │  │                  │  │ EUR/USD     │   │
│ │ Equity:     │  │                  │  │             │   │
│ │ $10,500     │  │                  │  │ Direccion:  │   │
│ │             │  │                  │  │ [BUY/SELL]  │   │
│ │ P&L:        │  │                  │  │             │   │
│ │ +$500       │  │                  │  │ [🟢 COMPRAR]│   │
│ │             │  │                  │  │ [🔴 VENDER] │   │
│ └─────────────┘  └──────────────────┘  └─────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [Posiciones Abiertas] [Historial] [Logs]                   │
│                                                             │
│ ID    | Simbolo | Lado | P&L    | Acciones                │
│ 12345 | EUR/USD | BUY  | +$50   | [Cerrar]                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎮 CONTROLES PRINCIPALES

### BARRA DE HERRAMIENTAS

- **▶ Iniciar**: Inicia el sistema de trading
- **⏸ Detener**: Detiene el sistema
- **🔌 Conectar Broker**: Abre dialogo de conexion
- **⚙ Configuracion**: Abre preferencias

### DASHBOARD (Izquierda)

Muestra metricas en tiempo real:
- Balance y Equity
- P&L Total y Retorno
- Win Rate y Profit Factor
- Sharpe Ratio
- Max Drawdown
- Posiciones Abiertas

### GRAFICO (Centro)

- Visualizacion de precios
- Actualizacion automatica
- Zoom con scroll
- Click derecho para opciones

### PANEL DE TRADING (Derecha)

- Seleccionar simbolo
- Ver precio Bid/Ask
- Configurar cantidad
- Establecer SL/TP
- Ejecutar operaciones

### TABS INFERIORES

- **Posiciones Abiertas**: Ver y cerrar posiciones
- **Historial**: Ver trades cerrados
- **Logs**: Ver logs del sistema

---

## 🔌 CONECTAR BROKERS

### QUOTEX (Simulacion)

1. Click "Conectar Broker"
2. Seleccionar "Quotex (Simulacion)"
3. Email: cualquier email
4. Password: cualquier password
5. ✅ Modo Demo
6. Click "Conectar"

### BINANCE (Crypto Real)

**TESTNET (Pruebas):**

1. Ir a: https://testnet.binance.vision/
2. Crear cuenta de prueba
3. Generar API Key
4. En la app:
   - Seleccionar "Binance (Crypto)"
   - Pegar API Key y Secret
   - ✅ Usar Testnet
   - Click "Conectar"

**REAL (Dinero Real):**

1. Crear cuenta en Binance.com
2. Completar KYC
3. Generar API Key (sin Withdrawals)
4. Depositar fondos (min $500)
5. En la app:
   - Seleccionar "Binance (Crypto)"
   - Pegar API Key y Secret
   - ❌ Desmarcar Testnet
   - Click "Conectar"

---

## 📈 EJECUTAR PRIMERA OPERACION

### Operacion Manual:

1. **Conectar broker** (Quotex para empezar)
2. **Iniciar sistema** (Click "▶ Iniciar")
3. **En Panel de Trading:**
   - Simbolo: EUR/USD
   - Click "🔄 Actualizar Precio"
   - Direccion: BUY
   - Cantidad: 0.1
   - Stop Loss: 1.08320 (opcional)
   - Take Profit: 1.08860 (opcional)
4. **Click "🟢 COMPRAR"**
5. **Confirmar** en dialogo
6. **Ver posicion** en "Posiciones Abiertas"

### Cerrar Posicion:

1. Ir a tab "Posiciones Abiertas"
2. Encontrar tu posicion
3. Click "Cerrar"
4. Confirmar
5. Ver resultado en "Historial"

---

## ⚙️ CONFIGURACION BASICA

### Menu → Configuracion → Preferencias

**Tab Trading:**
- Riesgo maximo: 2% (conservador)
- Posiciones maximas: 3
- Trading automatico: ❌ (desactivado)

**Tab IA:**
- Umbral confianza: 65%
- Re-entrenamiento: ✅ (activado)

**Guardar cambios**

---

## 🐛 SOLUCION DE PROBLEMAS

### Error: "API no responde"

**Solucion:**
1. Verificar que `run_api.py` este ejecutando
2. Abrir: http://127.0.0.1:8000/docs
3. Si no abre, reiniciar API

### Error: "Broker no conecta"

**Solucion:**
1. Verificar credenciales
2. Para Quotex: usar cualquier email/password en demo
3. Para Binance: verificar API Key correcta

### Error: "ModuleNotFoundError: PyQt6"

**Solucion:**
```bash
pip install PyQt6 PyQt6-WebEngine pyqtgraph qdarkstyle
```

### Aplicacion se cierra sola

**Solucion:**
1. Ejecutar desde terminal para ver errores
2. Verificar que API este corriendo
3. Revisar logs en logs/

### Grafico no se actualiza

**Solucion:**
1. Click "🔄 Actualizar" manualmente
2. Verificar conexion a broker
3. Reiniciar aplicacion

---

## 📚 PROXIMOS PASOS

### Dia 1-7: Familiarizacion
- Explorar la interfaz
- Probar todos los botones
- Ver como funcionan las metricas
- NO ejecutar operaciones aun

### Semana 2-4: Trading Demo
- Ejecutar operaciones en Quotex (simulacion)
- Probar diferentes simbolos
- Experimentar con SL/TP
- Analizar resultados

### Mes 2: Entrenamiento
- Entrenar modelos de IA
- Optimizar parametros
- Backtesting

### Mes 3+: Trading Real
- Conectar Binance Testnet
- Probar con dinero virtual
- Validar estrategia
- Cuando estes listo: Trading real con capital minimo

---

## 🎯 TIPS Y TRUCOS

### Atajos de Teclado

- `Ctrl + S`: Guardar configuracion
- `Ctrl + Q`: Cerrar aplicacion
- `F5`: Actualizar datos
- `F11`: Pantalla completa

### Mejores Practicas

1. **Siempre usar Stop Loss**
2. **No arriesgar mas del 2% por trade**
3. **Monitorear constantemente**
4. **Revisar logs diariamente**
5. **Hacer backups de configuracion**

### Optimizacion

- Cerrar programas innecesarios
- Usar conexion estable
- Actualizar drivers de GPU (si tienes)
- Mantener sistema actualizado

---

## 📞 AYUDA RAPIDA

### Documentacion:
- `README.md` - Documentacion tecnica
- `DESKTOP_APP_GUIDE.md` - Guia completa de la app
- `RESUMEN_COMPLETO_APP.md` - Resumen de todo

### Soporte:
- GitHub Issues
- Email: soporte@tradingsystem.com
- Telegram: @TradingSystemAI

### API Docs:
- http://127.0.0.1:8000/docs (cuando API este corriendo)

---

## ✅ CHECKLIST INICIAL

Antes de trading real:

- [ ] Aplicacion instalada y funcionando
- [ ] API corriendo correctamente
- [ ] Broker conectado (Quotex demo)
- [ ] Sistema iniciado sin errores
- [ ] Primera operacion manual ejecutada
- [ ] Posicion cerrada exitosamente
- [ ] Metricas visualizadas correctamente
- [ ] Logs revisados
- [ ] Configuracion ajustada
- [ ] Documentacion leida

---

**🎉 LISTO PARA COMENZAR**

Doble click en `start_trading_app.bat` y empieza a operar!

Recuerda: SIEMPRE comenzar en modo DEMO
