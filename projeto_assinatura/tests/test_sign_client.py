from .test_base import TestBase
from unittest.mock import Mock, patch
from src.sign.sign_client import SignClient
from config.config import Config

class TestSignClient(TestBase):
    def setUp(self):
        self.config = Config()
        self.sign = SignClient(self.config)

    def test_anexar_contrato(self):
        """Testa a anexação de contrato no Sign"""
        self.sign.driver = Mock()
        
        dados_contrato = {
            'numero': '12345',
            'cliente': 'Cliente Teste',
            'data_entrada': '2024-03-20'
        }
        
        resultado = self.sign.anexar_contrato(
            'caminho/teste.pdf',
            dados_contrato
        )
        
        self.assertTrue(resultado)
