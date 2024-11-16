from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import logging

class SignClient:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self._configurar_logging()

    def _configurar_logging(self):
        logging.basicConfig(
            filename=f'logs/sign_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def iniciar_navegador(self):
        """Inicia o navegador e faz login no sistema Sign"""
        try:
            self.driver = webdriver.Chrome()
            self.driver.get(self.config.SIGN_URL)
            
            # Login no sistema
            usuario = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "login"))
            )
            senha = self.driver.find_element(By.ID, "password")
            
            usuario.send_keys(self.config.SIGN_USER)
            senha.send_keys(self.config.SIGN_PASSWORD)
            
            botao_login = self.driver.find_element(By.ID, "btn-login")
            botao_login.click()
            
            logging.info("Login no Sign realizado com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao iniciar Sign: {str(e)}")
            return False

    def anexar_contrato(self, caminho_pdf, dados_contrato):
        """Anexa um novo contrato no sistema Sign"""
        try:
            # Navegar até a página de upload
            self.driver.get(f"{self.config.SIGN_URL}/novo-documento")
            
            # Upload do arquivo PDF
            input_arquivo = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "upload-file"))
            )
            input_arquivo.send_keys(caminho_pdf)
            
            # Preencher informações do contrato
            self._preencher_dados_contrato(dados_contrato)
            
            # Definir signatário padrão Royal
            self._definir_signatario_padrao()
            
            # Confirmar upload
            botao_confirmar = self.driver.find_element(By.ID, "confirmar-upload")
            botao_confirmar.click()
            
            logging.info(f"Contrato {dados_contrato['numero']} anexado com sucesso no Sign")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao anexar contrato no Sign: {str(e)}")
            return False

    def _preencher_dados_contrato(self, dados_contrato):
        """Preenche os campos obrigatórios do contrato"""
        try:
            campos = {
                "nome_cliente": dados_contrato['cliente'],
                "numero_contrato": dados_contrato['numero'],
                "data_inicio": dados_contrato['data_entrada']
            }
            
            for campo, valor in campos.items():
                elemento = self.driver.find_element(By.ID, campo)
                elemento.clear()
                elemento.send_keys(valor)
                
        except Exception as e:
            logging.error(f"Erro ao preencher dados do contrato: {str(e)}")
            raise

    def _definir_signatario_padrao(self):
        """Define o signatário padrão conforme regras da Royal"""
        try:
            select_signatario = self.driver.find_element(By.ID, "signatario")
            select_signatario.click()
            
            # Selecionar signatário padrão Royal
            opcao_signatario = self.driver.find_element(
                By.XPATH, 
                f"//option[text()='{self.config.SIGNATARIO_PADRAO_ROYAL}']"
            )
            opcao_signatario.click()
            
        except Exception as e:
            logging.error(f"Erro ao definir signatário padrão: {str(e)}")
            raise

    def verificar_status_contrato(self, numero_contrato):
        """Verifica o status atual do contrato no Sign"""
        try:
            self.driver.get(f"{self.config.SIGN_URL}/consulta-documentos")
            
            # Buscar contrato
            campo_busca = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "busca-documento"))
            )
            campo_busca.send_keys(numero_contrato)
            
            botao_buscar = self.driver.find_element(By.ID, "btn-buscar")
            botao_buscar.click()
            
            # Obter status
            status = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "status-documento"))
            ).text
            
            return status
            
        except Exception as e:
            logging.error(f"Erro ao verificar status do contrato {numero_contrato}: {str(e)}")
            return None