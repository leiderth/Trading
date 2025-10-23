@echo off
echo ========================================
echo  INSTALACION FASE 2 - SISTEMA INSTITUCIONAL
echo  Trading System Pro v4.0
echo ========================================
echo.

echo [1/3] Instalando dependencias de FASE 2...
.\venv\Scripts\python.exe -m pip install pyqtgraph scipy --quiet
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar dependencias
    pause
    exit /b 1
)
echo OK - pyqtgraph y scipy instalados

echo.
echo [2/3] Verificando instalacion...
.\venv\Scripts\python.exe -c "import pyqtgraph; import scipy; print('OK - Todas las dependencias instaladas')"
if %errorlevel% neq 0 (
    echo ERROR: Verificacion fallida
    pause
    exit /b 1
)

echo.
echo [3/3] Creando directorios adicionales...
if not exist "backtests" mkdir backtests
if not exist "portfolios" mkdir portfolios
echo OK - Directorios creados

echo.
echo ========================================
echo  FASE 2 INSTALADA CORRECTAMENTE
echo ========================================
echo.
echo Componentes instalados:
echo  - Multi-Agent System (6 agentes)
echo  - Advanced Backtesting Framework
echo  - Portfolio Optimization
echo  - Bloomberg-Style Dashboard
echo.
echo Para usar:
echo   python examples/run_multi_agent.py
echo   python examples/run_backtesting.py
echo   python examples/run_portfolio_optimizer.py
echo   python examples/run_bloomberg_dashboard.py
echo.
echo Documentacion:
echo   FASE2_COMPLETADA.md
echo.
pause
