from .test_base import TestBase
from unittest.mock import Mock, patch
from src.email_monitor.email_processor import EmailProcessor
from config.config import Config

class TestEmailProcessor(TestBase):
    def setUp(self):
        self.config = Config()
        self.email_processor = EmailProcessor(self.config)

    def test_buscar_contratos_assinados(self):
        """Testa a busca de contratos assinados no e-mail"""
        with patch('imaplib.IMAP4_SSL') as mock_imap:
            # Configurar o mock
            mock_connection = Mock()
            mock_imap.return_value = mock_connection
            
            # Simular e-mails encontrados
            mock_connection.search.return_value = (
                'OK', 
                [b'1 2 3']
            )
            
            # Executar teste
            self.email_processor.conectar()
            contratos = self.email_processor.buscar_contratos_assinados()
            
            self.assertIsInstance(contratos, list)
