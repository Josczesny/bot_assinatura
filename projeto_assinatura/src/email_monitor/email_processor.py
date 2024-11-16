import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime
import logging

class EmailProcessor:
    def __init__(self, config):
        self.config = config
        self.mail = None
        self._configurar_logging()

    def _configurar_logging(self):
        logging.basicConfig(
            filename=f'logs/email_processor_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def conectar(self):
        """Conecta ao servidor de e-mail"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.config.EMAIL_SERVER)
            self.mail.login(self.config.EMAIL_USER, self.config.EMAIL_PASSWORD)
            logging.info("Conexão com servidor de e-mail estabelecida")
            return True
        except Exception as e:
            logging.error(f"Erro ao conectar ao e-mail: {str(e)}")
            return False

    def buscar_contratos_assinados(self):
        """Busca e-mails com contratos assinados anexados"""
        try:
            # Seleciona a caixa de entrada
            self.mail.select('INBOX')

            # Busca e-mails com as palavras-chave
            _, mensagens = self.mail.search(None, 
                'SUBJECT "contrato assinado" UNSEEN')

            contratos_encontrados = []

            for num in mensagens[0].split():
                try:
                    # Obtém os dados do e-mail
                    _, dados = self.mail.fetch(num, '(RFC822)')
                    email_body = dados[0][1]
                    email_msg = email.message_from_bytes(email_body)

                    # Processa anexos
                    contratos = self._processar_anexos(email_msg)
                    if contratos:
                        contratos_encontrados.extend(contratos)

                    # Marca e-mail como lido
                    self.mail.store(num, '+FLAGS', '\\Seen')

                except Exception as e:
                    logging.error(f"Erro ao processar e-mail {num}: {str(e)}")
                    continue

            return contratos_encontrados

        except Exception as e:
            logging.error(f"Erro ao buscar contratos assinados: {str(e)}")
            return []

    def _processar_anexos(self, email_msg):
        """Processa os anexos do e-mail"""
        contratos = []

        for part in email_msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            filename = part.get_filename()
            if filename:
                # Decodifica o nome do arquivo se necessário
                if decode_header(filename)[0][1] is not None:
                    filename = decode_header(filename)[0][0].decode(decode_header(filename)[0][1])

                if filename.lower().endswith('.pdf'):
                    # Salva o anexo
                    caminho_arquivo = os.path.join(
                        self.config.CONTRATOS_FINALIZADOS_PATH, 
                        filename
                    )
                    
                    with open(caminho_arquivo, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    
                    contratos.append({
                        'caminho': caminho_arquivo,
                        'nome_arquivo': filename,
                        'data_recebimento': datetime.now()
                    })

        return contratos
