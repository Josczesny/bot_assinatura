from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import logging

class MaxyconClient:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self._configurar_logging()

    def _configurar_logging(self):
        logging.basicConfig(
            filename=f'logs/maxycon_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def iniciar_navegador(self):
        """Inicia o navegador e faz login no Maxycon"""
        try:
            self.driver = webdriver.Chrome()
            self.driver.get(self.config.MAXYCON_URL)
            
            # Aguardar e preencher campos de login
            usuario = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "usuario"))
            )
            senha = self.driver.find_element(By.ID, "senha")
            
            usuario.send_keys(self.config.MAXYCON_USER)
            senha.send_keys(self.config.MAXYCON_PASSWORD)
            
            # Clicar no botão de login
            botao_login = self.driver.find_element(By.ID, "btn-login")
            botao_login.click()
            
            logging.info("Login no Maxycon realizado com sucesso")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao iniciar Maxycon: {str(e)}")
            return False

    def buscar_novos_contratos(self):
        """
        Busca contratos novos no sistema que ainda não passaram pelo processo de assinatura
        """
        try:
            # Navegar para a página de contratos
            self.driver.get(f"{self.config.MAXYCON_URL}/contratos")
            
            # Definir filtros de busca
            data_inicio = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
            data_fim = datetime.now().strftime("%d/%m/%Y")
            
            # Preencher filtros de data
            campo_data_inicio = self.driver.find_element(By.ID, "data_inicio")
            campo_data_fim = self.driver.find_element(By.ID, "data_fim")
            
            campo_data_inicio.clear()
            campo_data_inicio.send_keys(data_inicio)
            campo_data_fim.clear()
            campo_data_fim.send_keys(data_fim)
            
            # Filtrar por status "Pendente Assinatura"
            select_status = self.driver.find_element(By.ID, "status_contrato")
            select_status.click()
            opcao_pendente = self.driver.find_element(By.XPATH, "//option[text()='Pendente Assinatura']")
            opcao_pendente.click()
            
            # Buscar contratos
            botao_buscar = self.driver.find_element(By.ID, "buscar-contratos")
            botao_buscar.click()
            
            # Aguardar carregamento da tabela
            tabela = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "tabela-contratos"))
            )
            
            # Extrair dados dos contratos
            contratos = []
            linhas = tabela.find_elements(By.TAG_NAME, "tr")
            
            for linha in linhas[1:]:  # Pular cabeçalho
                colunas = linha.find_elements(By.TAG_NAME, "td")
                contrato = {
                    'id': colunas[0].text,
                    'numero': colunas[1].text,
                    'cliente': colunas[2].text,
                    'data_entrada': colunas[3].text,
                    'status': colunas[4].text
                }
                contratos.append(contrato)
            
            logging.info(f"Encontrados {len(contratos)} novos contratos")
            return contratos
            
        except Exception as e:
            logging.error(f"Erro ao buscar contratos: {str(e)}")
            return []

    def download_contrato(self, contrato_id):
        """
        Realiza o download do contrato em PDF
        """
        try:
            # Navegar para a página do contrato
            self.driver.get(f"{self.config.MAXYCON_URL}/contratos/{contrato_id}")
            
            # Clicar no botão de download
            botao_download = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "download-pdf"))
            )
            botao_download.click()
            
            # Aguardar download (ajuste o tempo conforme necessário)
            import time
            time.sleep(5)
            
            # Retornar caminho do arquivo baixado
            import os
            downloads_path = os.path.expanduser("~/Downloads")
            arquivo_pdf = f"{downloads_path}/contrato_{contrato_id}.pdf"
            
            if os.path.exists(arquivo_pdf):
                logging.info(f"Download do contrato {contrato_id} realizado com sucesso")
                return arquivo_pdf
            else:
                raise Exception("Arquivo PDF não encontrado após download")
            
        except Exception as e:
            logging.error(f"Erro ao fazer download do contrato {contrato_id}: {str(e)}")
            return None

    def atualizar_status_contrato(self, contrato_id, status):
        """Atualiza o status do contrato"""
        # Implementar atualização
        pass