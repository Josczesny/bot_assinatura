import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Configurações do Maxycon
    MAXYCON_URL = "https://sistema.maxycon.com"
    MAXYCON_USER = os.getenv('MAXYCON_USER')
    MAXYCON_PASSWORD = os.getenv('MAXYCON_PASSWORD')

    # Configurações do Sign
    SIGN_URL = "https://sistema.sign.com"
    SIGN_USER = os.getenv('SIGN_USER')
    SIGN_PASSWORD = os.getenv('SIGN_PASSWORD')
    SIGNATARIO_PADRAO_ROYAL = "NOME_DO_SIGNATARIO"

    # Configurações de pasta
    CONTRATOS_NOVOS_PATH = "contratos/novos/"
    CONTRATOS_FINALIZADOS_PATH = "contratos/finalizados/"
    RELATORIOS_PATH = "relatorios/"

    # Configurações de e-mail
    EMAIL_SERVER = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USER = "seu_email@gmail.com"
    EMAIL_PASSWORD = "sua_senha"
    EMAIL_CADASTRO = "cadastro@empresa.com"

    # Configurações do WhatsApp
    WHATSAPP_GRUPO_CADASTRO = "Nome do Grupo de Cadastro"