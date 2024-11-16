import unittest
import os
from pathlib import Path

class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para todos os testes"""
        # Criar diretórios necessários
        dirs = ['logs', 'contratos/novos', 'contratos/finalizados', 'relatorios']
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)