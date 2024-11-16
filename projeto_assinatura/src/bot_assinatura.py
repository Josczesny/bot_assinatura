from datetime import datetime
import logging
from .maxycon.maxycon_client import MaxyconClient
from .sign.sign_client import SignClient
from .notifications.email_sender import EmailSender
from .notifications.whatsapp_sender import WhatsAppSender
from .utils.file_handler import FileHandler
from .email_monitor.email_processor import EmailProcessor
from .utils.retry_handler import RetryHandler

# Criar uma única instância do RetryHandler
retry_handler = RetryHandler()

class BotAssinatura:
    def __init__(self, config):
        self.config = config
        self.maxycon = MaxyconClient(config)
        self.sign = SignClient(config)
        self.email = EmailSender(config)
        self.whatsapp = WhatsAppSender(config)
        self.file_handler = FileHandler(config)
        self.email_processor = EmailProcessor(config)
        
        self.contratos_processados = []
        self.contratos_finalizados = []
        self._configurar_logging()

    def _configurar_logging(self):
        logging.basicConfig(
            filename=f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def executar_processamento(self):
        """Executa o fluxo completo de processamento"""
        try:
            logging.info("Iniciando processamento de contratos")
            
            # 1. Inicializar sistemas
            self._inicializar_sistemas()
            
            # 2. Buscar e processar novos contratos
            contratos = self.maxycon.buscar_novos_contratos()
            
            for contrato in contratos:
                self._processar_contrato(contrato)
            
            # 3. Processar contratos finalizados
            self._processar_contratos_finalizados()
            
            # 4. Enviar notificações
            if self.contratos_processados:
                self._enviar_notificacoes()
            
            # 5. Gerar relatório diário
            self._gerar_relatorio_diario()
            
            logging.info("Processamento finalizado com sucesso")
            
        except Exception as e:
            erro = f"Erro no processamento: {str(e)}"
            logging.error(erro)
            try:
                self.whatsapp.enviar_alerta_erro(erro)
            except Exception as whatsapp_error:
                logging.error(f"Erro ao enviar alerta WhatsApp: {str(whatsapp_error)}")

    def _inicializar_sistemas(self):
        """Inicializa todos os sistemas necessários"""
        self.maxycon.iniciar_navegador()
        self.sign.iniciar_navegador()
        self.email.conectar()
        self.whatsapp.iniciar_navegador()

    @retry_handler.retry
    def _processar_contrato(self, contrato):
        """Processa um único contrato com retry automático"""
        try:
            # Download do PDF
            pdf_path = self.maxycon.download_contrato(contrato['id'])
            
            if pdf_path:
                # Salvar localmente
                pdf_salvo = self.file_handler.salvar_contrato_novo(pdf_path, contrato['numero'])
                
                # Anexar no Sign
                if self.sign.anexar_contrato(pdf_salvo, contrato):
                    self.contratos_processados.append(contrato)
                    logging.info(f"Contrato {contrato['numero']} processado com sucesso")
                
        except Exception as e:
            logging.error(f"Erro ao processar contrato {contrato['numero']}: {str(e)}")
            raise

    @retry_handler.retry
    def _processar_contratos_finalizados(self):
        """Processa contratos finalizados com retry automático"""
        try:
            # Conectar ao e-mail
            if not self.email_processor.conectar():
                raise Exception("Não foi possível conectar ao servidor de e-mail")

            # Buscar contratos assinados
            contratos = self.email_processor.buscar_contratos_assinados()

            for contrato in contratos:
                try:
                    # Atualizar status no Maxycon
                    self.maxycon.atualizar_status_contrato(
                        contrato['nome_arquivo'],
                        "Finalizado"
                    )

                    # Fazer upload do contrato assinado
                    self.maxycon.upload_contrato_assinado(
                        contrato['caminho'],
                        contrato['nome_arquivo']
                    )

                    self.contratos_finalizados.append(contrato)
                    logging.info(f"Contrato finalizado processado: {contrato['nome_arquivo']}")

                except Exception as e:
                    logging.error(f"Erro ao processar contrato finalizado {contrato['nome_arquivo']}: {str(e)}")

        except Exception as e:
            logging.error(f"Erro no processamento de contratos finalizados: {str(e)}")
            raise

    def _enviar_notificacoes(self):
        """Envia notificações sobre contratos processados"""
        try:
            self.email.enviar_notificacao_novos_contratos(self.contratos_processados)
        except Exception as e:
            logging.error(f"Erro ao enviar notificação por e-mail: {str(e)}")
        
        try:
            self.whatsapp.enviar_alerta_diario(self.contratos_processados)
        except Exception as e:
            logging.error(f"Erro ao enviar notificação por WhatsApp: {str(e)}")

    def _gerar_relatorio_diario(self):
        """Gera relatório diário atualizado incluindo contratos finalizados"""
        relatorio = {
            'data': datetime.now().strftime("%d/%m/%Y"),
            'novos_contratos': self.contratos_processados,
            'contratos_finalizados': self.contratos_finalizados,
            'total_novos': len(self.contratos_processados),
            'total_finalizados': len(self.contratos_finalizados)
        }
        
        # Salvar arquivo
        try:
            self.file_handler.salvar_relatorio(relatorio)
        except Exception as e:
            logging.error(f"Erro ao salvar relatório: {str(e)}")
            raise
        
        # Enviar por e-mail
        try:
            self._enviar_relatorio_completo(relatorio)
        except Exception as e:
            logging.error(f"Erro ao enviar relatório por e-mail: {str(e)}")
            raise

    def _enviar_relatorio_completo(self, relatorio):
        """Envia relatório completo por e-mail"""
        self.email.enviar_relatorio_diario(relatorio)