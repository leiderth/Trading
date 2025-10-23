"""
Script para ejecutar la API REST
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from src.api.trading_api import app

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 INICIANDO API DE TRADING")
    print("=" * 70)
    print("📡 URL: http://127.0.0.1:8000")
    print("📚 Docs: http://127.0.0.1:8000/docs")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
