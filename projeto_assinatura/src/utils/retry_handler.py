import time
import logging
from functools import wraps

class RetryHandler:
    def __init__(self, max_tentativas=3, delay_inicial=1, max_delay=60):
        self.max_tentativas = max_tentativas
        self.delay_inicial = delay_inicial
        self.max_delay = max_delay

    def retry(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tentativa = 0
            delay = self.delay_inicial
            
            while tentativa < self.max_tentativas:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    tentativa += 1
                    if tentativa == self.max_tentativas:
                        logging.error(f"Todas as tentativas falharam para {func.__name__}: {str(e)}")
                        raise
                    
                    logging.warning(
                        f"Tentativa {tentativa} falhou para {func.__name__}. "
                        f"Aguardando {delay} segundos antes de tentar novamente."
                    )
                    
                    time.sleep(delay)
                    delay = min(delay * 2, self.max_delay)
            
            return None
        
        return wrapper