from .test_base import TestBase
from unittest.mock import Mock, patch
from src.maxycon.maxycon_client import MaxyconClient
from config.config import Config

class TestMaxyconClient(TestBase):
    def setUp(self):
        self.config = Config()
        self.maxycon = MaxyconClient(self.config)

    def test_login_maxycon(self):
        """Testa o login no sistema Maxycon"""
        with patch('selenium.webdriver.Chrome') as mock_chrome:
            # Configurar o mock
            mock_driver = Mock()
            mock_chrome.return_value = mock_driver
            
            # Executar o teste
            resultado = self.maxycon.iniciar_navegador()
            
            # Verificar resultados
            self.assertTrue(resultado)
            mock_driver.get.assert_called_with(self.config.MAXYCON_URL)

    def test_buscar_novos_contratos(self):
        """Testa a busca de novos contratos"""
        self.maxycon.driver = Mock()
        
        # Simular encontrar contratos
        contratos = self.maxycon.buscar_novos_contratos()
        
        self.assertIsInstance(contratos, list)
