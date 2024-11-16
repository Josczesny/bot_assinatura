import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import logging

class EmailSender:
    def __init__(self, config):
        self.config = config
        self.servidor = None
        self._configurar_logging()

    def _configurar_logging(self):
        logging.basicConfig(
            filename=f'logs/email_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def conectar(self):
        """Estabelece conexão com o servidor de e-mail"""
        try:
            self.servidor = smtplib.SMTP(self.config.EMAIL_SERVER, self.config.EMAIL_PORT)
            self.servidor.starttls()
            self.servidor.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
            logging.info("Conexão com servidor de e-mail estabelecida")
            return True
        except Exception as e:
            logging.error(f"Erro ao conectar ao servidor de e-mail: {str(e)}")
            return False

    def enviar_notificacao_novos_contratos(self, contratos):
        """Envia notificação de novos contratos para equipe de Cadastro"""
        try:
            assunto = f"Novos Contratos para Assinatura - {datetime.now().strftime('%d/%m/%Y')}"
            
            corpo = """
            <h2>Novos Contratos Incluídos no Sistema de Assinatura</h2>
            <p>Os seguintes contratos foram processados e aguardam revisão:</p>
            <table border="1">
                <tr>
                    <th>Número do Contrato</th>
                    <th>Cliente</th>
                    <th>Data de Processamento</th>
                </tr>
            """
            
            for contrato in contratos:
                corpo += f"""
                <tr>
                    <td>{contrato['numero']}</td>
                    <td>{contrato['cliente']}</td>
                    <td>{datetime.now().strftime('%d/%m/%Y %H:%M')}</td>
                </tr>
                """
            
            corpo += "</table>"
            
            msg = MIMEMultipart()
            msg['From'] = self.config.EMAIL_USER
            msg['To'] = self.config.EMAIL_CADASTRO
            msg['Subject'] = assunto
            msg.attach(MIMEText(corpo, 'html'))
            
            self.servidor.send_message(msg)
            logging.info(f"Notificação enviada para equipe de Cadastro: {len(contratos)} contratos")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao enviar notificação: {str(e)}")
            return False