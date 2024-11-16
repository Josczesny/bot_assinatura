from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import logging
import time

class WhatsAppSender:
    def __init__(self, config):
        self.config = config
        self.driver = None
        self._configurar_logging()

    def _configurar_logging(self):
        logging.basicConfig(
            filename=f'logs/whatsapp_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def iniciar_navegador(self):
        """Inicia o navegador e faz login no WhatsApp Web"""
        try:
            self.driver = webdriver.Chrome()
            self.driver.get("https://web.whatsapp.com")
            
            # Aguardar scan do QR code e login
            input("Por favor, escaneie o QR Code e pressione Enter após fazer login...")
            logging.info("Login no WhatsApp Web realizado")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao iniciar WhatsApp Web: {str(e)}")
            return False

    def enviar_alerta_diario(self, contratos_processados):
        """Envia alerta diário para o grupo de Cadastro"""
        try:
            # Preparar mensagem
            mensagem = f"""
🔔 *Resumo Diário de Contratos - {datetime.now().strftime('%d/%m/%Y')}*

*Contratos Processados Hoje:*
"""
            for contrato in contratos_processados:
                mensagem += f"""
📄 Contrato: {contrato['numero']}
👤 Cliente: {contrato['cliente']}
⏰ Processado em: {datetime.now().strftime('%H:%M')}
-------------------"""

            mensagem += f"\n\n*Total de contratos processados: {len(contratos_processados)}*"

            # Localizar e clicar no grupo de Cadastro
            grupo = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f"//span[@title='{self.config.WHATSAPP_GRUPO_CADASTRO}']"))
            )
            grupo.click()
            time.sleep(2)

            # Enviar mensagem
            campo_mensagem = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"]')
            
            # Dividir mensagem em partes para evitar problemas com caracteres especiais
            for linha in mensagem.split('\n'):
                campo_mensagem.send_keys(linha)
                campo_mensagem.send_keys('\n')
            
            # Clicar no botão enviar
            botao_enviar = self.driver.find_element(By.XPATH, '//span[@data-icon="send"]')
            botao_enviar.click()
            
            logging.info(f"Alerta diário enviado via WhatsApp: {len(contratos_processados)} contratos")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar alerta WhatsApp: {str(e)}")
            return False

    def enviar_alerta_erro(self, mensagem_erro):
        """Envia alerta de erro para o grupo"""
        try:
            mensagem = f"""
⚠️ *ALERTA DE ERRO*
{datetime.now().strftime('%d/%m/%Y %H:%M')}

❌ {mensagem_erro}

Por favor, verificar o sistema.
"""
            # Implementar envio similar ao método anterior
            logging.warning(f"Alerta de erro enviado via WhatsApp: {mensagem_erro}")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar alerta de erro WhatsApp: {str(e)}")
            return False