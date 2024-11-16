from config.config import Config
from src.bot_assinatura import BotAssinatura
import schedule
import time
import logging
from datetime import datetime

def executar_bot():
    try:
        config = Config()
        bot = BotAssinatura(config)
        bot.executar_processamento()
    except Exception as e:
        logging.error(f"Erro na execução do bot: {str(e)}")

def main():
    # Configurar execuções diárias
    schedule.every().day.at("09:00").do(executar_bot)
    schedule.every().day.at("15:00").do(executar_bot)
    
    logging.info("Bot iniciado - aguardando horários programados")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    logging.basicConfig(
        filename=f'logs/main_{datetime.now().strftime("%Y%m%d")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()