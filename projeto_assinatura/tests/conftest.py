import pytest
import sys
import os
from pathlib import Path

# Adiciona o diretório raiz do projeto ao PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.fixture
def config():
    from config.config import Config
    return Config()

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configura o ambiente de teste"""
    # Criar diretórios necessários
    dirs = ['logs', 'contratos/novos', 'contratos/finalizados', 'relatorios']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)