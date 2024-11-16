from .test_base import TestBase
from unittest.mock import Mock, patch, call
from src.bot_assinatura import BotAssinatura
from config.config import Config
from datetime import datetime

class TestBotAssinatura(TestBase):
    def setUp(self):
        self.config = Config()
        self.bot = BotAssinatura(self.config)
        
    def test_inicializar_sistemas(self):
        """Testa a inicialização de todos os sistemas"""
        # Mock de todos os clientes
        self.bot.maxycon = Mock()
        self.bot.sign = Mock()
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        
        # Executar teste
        self.bot._inicializar_sistemas()
        
        # Verificar se todos os métodos foram chamados
        self.bot.maxycon.iniciar_navegador.assert_called_once()
        self.bot.sign.iniciar_navegador.assert_called_once()
        self.bot.email.conectar.assert_called_once()
        self.bot.whatsapp.iniciar_navegador.assert_called_once()
        
    def test_inicializar_sistemas_erro(self):
        """Testa erro na inicialização dos sistemas"""
        # Mock dos componentes
        self.bot.maxycon = Mock()
        self.bot.sign = Mock()
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        
        # Simular erro no Maxycon
        self.bot.maxycon.iniciar_navegador.side_effect = Exception("Erro ao iniciar Maxycon")
        
        # Executar teste e verificar exceção
        with self.assertRaises(Exception) as context:
            self.bot._inicializar_sistemas()
        
        # Verificar mensagem de erro
        self.assertIn('Erro ao iniciar Maxycon', str(context.exception))
        
    def test_processar_contrato(self):
        """Testa o processamento de um contrato"""
        # Mock dos componentes
        self.bot.maxycon = Mock()
        self.bot.sign = Mock()
        self.bot.file_handler = Mock()
        
        # Configurar retornos
        self.bot.maxycon.download_contrato.return_value = "temp/contrato.pdf"
        self.bot.file_handler.salvar_contrato_novo.return_value = "contratos/novos/contrato.pdf"
        self.bot.sign.anexar_contrato.return_value = True
        
        # Dados de teste
        contrato = {
            'id': '123',
            'numero': '12345',
            'cliente': 'Cliente Teste'
        }
        
        # Executar teste
        self.bot._processar_contrato(contrato)
        
        # Verificações
        self.bot.maxycon.download_contrato.assert_called_with('123')
        self.bot.file_handler.salvar_contrato_novo.assert_called()
        self.bot.sign.anexar_contrato.assert_called()
        self.assertIn(contrato, self.bot.contratos_processados)

    def test_processar_contratos_finalizados(self):
        """Testa o processamento de contratos finalizados"""
        # Mock dos componentes
        self.bot.email_processor = Mock()
        self.bot.maxycon = Mock()
        
        # Configurar retornos
        self.bot.email_processor.conectar.return_value = True
        self.bot.email_processor.buscar_contratos_assinados.return_value = [
            {
                'nome_arquivo': 'contrato_123.pdf',
                'caminho': 'contratos/finalizados/contrato_123.pdf'
            }
        ]
        
        # Executar teste
        self.bot._processar_contratos_finalizados()
        
        # Verificações
        self.bot.email_processor.conectar.assert_called_once()
        self.bot.email_processor.buscar_contratos_assinados.assert_called_once()
        self.bot.maxycon.atualizar_status_contrato.assert_called_with(
            'contrato_123.pdf',
            'Finalizado'
        )
        self.bot.maxycon.upload_contrato_assinado.assert_called_with(
            'contratos/finalizados/contrato_123.pdf',
            'contrato_123.pdf'
        )
        self.assertEqual(len(self.bot.contratos_finalizados), 1)

    def test_processar_contratos_finalizados_erro_conexao(self):
        """Testa erro de conexão ao processar contratos finalizados"""
        self.bot.email_processor = Mock()
        self.bot.email_processor.conectar.return_value = False
        
        with self.assertRaises(Exception) as context:
            self.bot._processar_contratos_finalizados()
        
        self.assertIn('Não foi possível conectar', str(context.exception))

    def test_processar_contratos_finalizados_erro_upload(self):
        """Testa erro no upload de contrato finalizado"""
        # Mock dos componentes
        self.bot.email_processor = Mock()
        self.bot.maxycon = Mock()
        
        # Configurar retornos
        self.bot.email_processor.conectar.return_value = True
        self.bot.email_processor.buscar_contratos_assinados.return_value = [
            {
                'nome_arquivo': 'contrato_123.pdf',
                'caminho': 'contratos/finalizados/contrato_123.pdf'
            }
        ]
        
        # Simular erro no upload
        self.bot.maxycon.upload_contrato_assinado.side_effect = Exception("Erro no upload")
        
        # Executar teste
        self.bot._processar_contratos_finalizados()
        
        # Verificações
        self.bot.maxycon.atualizar_status_contrato.assert_called_with(
            'contrato_123.pdf',
            'Finalizado'
        )
        self.assertEqual(len(self.bot.contratos_finalizados), 0)

    def test_enviar_notificacoes(self):
        """Testa o envio de notificações"""
        # Mock dos componentes
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        
        # Dados de teste
        self.bot.contratos_processados = [
            {'numero': '123', 'cliente': 'Cliente A'},
            {'numero': '456', 'cliente': 'Cliente B'}
        ]
        
        # Executar teste
        self.bot._enviar_notificacoes()
        
        # Verificações
        self.bot.email.enviar_notificacao_novos_contratos.assert_called_with(
            self.bot.contratos_processados
        )
        self.bot.whatsapp.enviar_alerta_diario.assert_called_with(
            self.bot.contratos_processados
        )

    def test_gerar_relatorio_diario(self):
        """Testa a geração do relatório diário"""
        # Mock dos componentes
        self.bot.file_handler = Mock()
        self.bot.email = Mock()
        
        # Dados de teste
        self.bot.contratos_processados = [{'numero': '123'}]
        self.bot.contratos_finalizados = [{'numero': '456'}]
        
        # Executar teste
        self.bot._gerar_relatorio_diario()
        
        # Verificações
        relatorio_esperado = {
            'data': datetime.now().strftime("%d/%m/%Y"),
            'novos_contratos': self.bot.contratos_processados,
            'contratos_finalizados': self.bot.contratos_finalizados,
            'total_novos': 1,
            'total_finalizados': 1
        }
        
        self.bot.file_handler.salvar_relatorio.assert_called_with(relatorio_esperado)
        self.bot.email.enviar_relatorio_diario.assert_called_with(relatorio_esperado)

    def test_executar_processamento(self):
        """Testa o fluxo completo de processamento"""
        # Mock de todos os componentes
        self.bot.maxycon = Mock()
        self.bot.sign = Mock()
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        self.bot.file_handler = Mock()
        self.bot.email_processor = Mock()
        
        # Configurar retornos
        self.bot.maxycon.buscar_novos_contratos.return_value = [
            {'id': '123', 'numero': '12345', 'cliente': 'Cliente Teste'}
        ]
        self.bot.maxycon.download_contrato.return_value = "temp/contrato.pdf"
        self.bot.file_handler.salvar_contrato_novo.return_value = "contratos/novos/contrato.pdf"
        self.bot.sign.anexar_contrato.return_value = True
        self.bot.email_processor.conectar.return_value = True
        self.bot.email_processor.buscar_contratos_assinados.return_value = [
            {
                'nome_arquivo': 'contrato_123.pdf',
                'caminho': 'contratos/finalizados/contrato_123.pdf'
            }
        ]
        
        # Executar teste
        self.bot.executar_processamento()
        
        # Verificações
        self.bot.maxycon.iniciar_navegador.assert_called_once()
        self.bot.sign.iniciar_navegador.assert_called_once()
        self.bot.email.conectar.assert_called_once()
        self.bot.whatsapp.iniciar_navegador.assert_called_once()
        self.bot.maxycon.buscar_novos_contratos.assert_called_once()
        
        # Verificar processamento de novos contratos
        self.bot.maxycon.download_contrato.assert_called_with('123')
        self.bot.file_handler.salvar_contrato_novo.assert_called()
        self.bot.sign.anexar_contrato.assert_called()
        
        # Verificar processamento de contratos finalizados
        self.bot.email_processor.buscar_contratos_assinados.assert_called_once()
        self.bot.maxycon.atualizar_status_contrato.assert_called()
        self.bot.maxycon.upload_contrato_assinado.assert_called()
        
        # Verificar notificações e relatório
        self.bot.email.enviar_notificacao_novos_contratos.assert_called_once()
        self.bot.whatsapp.enviar_alerta_diario.assert_called_once()
        self.bot.file_handler.salvar_relatorio.assert_called_once()

    def test_processar_contrato_erro(self):
        """Testa erro no processamento de um contrato"""
        # Mock dos componentes
        self.bot.maxycon = Mock()
        self.bot.sign = Mock()
        self.bot.file_handler = Mock()
        
        # Configurar erro no download
        self.bot.maxycon.download_contrato.side_effect = Exception("Erro ao baixar contrato")
        
        # Dados de teste
        contrato = {
            'id': '123',
            'numero': '12345',
            'cliente': 'Cliente Teste'
        }
        
        # Executar teste e verificar exceção
        with self.assertRaises(Exception) as context:
            self.bot._processar_contrato(contrato)
        
        # Verificar mensagem de erro
        self.assertIn('Erro ao baixar contrato', str(context.exception))
        
        # Verificar que o contrato não foi processado
        self.assertNotIn(contrato, self.bot.contratos_processados)

    def test_executar_processamento_erro(self):
        """Testa erro no fluxo completo de processamento"""
        # Mock dos componentes
        self.bot.maxycon = Mock()
        self.bot.sign = Mock()
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        self.bot.file_handler = Mock()
        
        # Simular erro
        self.bot.maxycon.buscar_novos_contratos.side_effect = Exception("Erro ao buscar contratos")
        
        # Executar teste
        self.bot.executar_processamento()
        
        # Verificar que o alerta de erro foi enviado
        self.bot.whatsapp.enviar_alerta_erro.assert_called_once()
        erro_enviado = self.bot.whatsapp.enviar_alerta_erro.call_args[0][0]
        self.assertIn('Erro ao buscar contratos', erro_enviado)

    def test_enviar_notificacoes_erro(self):
        """Testa erro no envio de notificações"""
        # Mock dos componentes
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        
        # Simular erro no envio de e-mail
        self.bot.email.enviar_notificacao_novos_contratos.side_effect = Exception("Erro ao enviar e-mail")
        
        # Dados de teste
        self.bot.contratos_processados = [{'numero': '123', 'cliente': 'Cliente A'}]
        
        # Executar teste - não deve lançar exceção
        self.bot._enviar_notificacoes()
        
        # Verificar que o WhatsApp ainda foi chamado mesmo com erro no e-mail
        self.bot.whatsapp.enviar_alerta_diario.assert_called_with(self.bot.contratos_processados)

    def test_gerar_relatorio_diario_erro_email(self):
        """Testa erro no envio do relatório por e-mail"""
        # Mock dos componentes
        self.bot.file_handler = Mock()
        self.bot.email = Mock()
        
        # Simular erro no envio do relatório
        self.bot.email.enviar_relatorio_diario.side_effect = Exception("Erro ao enviar relatório")
        
        # Dados de teste
        self.bot.contratos_processados = [{'numero': '123'}]
        self.bot.contratos_finalizados = [{'numero': '456'}]
        
        # Executar teste e verificar exceção
        with self.assertRaises(Exception) as context:
            self.bot._gerar_relatorio_diario()
        
        # Verificar que o arquivo foi salvo mesmo com erro no e-mail
        self.bot.file_handler.salvar_relatorio.assert_called_once()
        self.assertIn('Erro ao enviar relatório', str(context.exception))

    def test_executar_processamento_erro_whatsapp(self):
        """Testa erro no envio de alerta de erro via WhatsApp"""
        # Mock dos componentes
        self.bot.maxycon = Mock()
        self.bot.sign = Mock()
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        self.bot.file_handler = Mock()
        
        # Simular erro no processamento e no WhatsApp
        erro_busca = Exception("Erro ao buscar contratos")
        self.bot.maxycon.buscar_novos_contratos.side_effect = erro_busca
        self.bot.whatsapp.enviar_alerta_erro.side_effect = Exception("Erro no WhatsApp")
        
        # Executar teste - não deve lançar exceção
        self.bot.executar_processamento()
        
        # Verificar que tentou enviar alerta e registrou erro
        self.bot.whatsapp.enviar_alerta_erro.assert_called_once_with(
            f"Erro no processamento: {str(erro_busca)}"
        )

    def test_gerar_relatorio_diario_erro_completo(self):
        """Testa erro total na geração do relatório diário"""
        # Mock dos componentes
        self.bot.file_handler = Mock()
        self.bot.email = Mock()
        
        # Simular erros em ambos os canais
        self.bot.file_handler.salvar_relatorio.side_effect = Exception("Erro ao salvar arquivo")
        self.bot.email.enviar_relatorio_diario.side_effect = Exception("Erro ao enviar e-mail")
        
        # Dados de teste
        self.bot.contratos_processados = [{'numero': '123'}]
        self.bot.contratos_finalizados = [{'numero': '456'}]
        
        # Executar teste e verificar exceção
        with self.assertRaises(Exception) as context:
            self.bot._gerar_relatorio_diario()
        
        # Verificar mensagem de erro
        self.assertIn('Erro ao salvar arquivo', str(context.exception))

    def test_processar_multiplos_contratos_com_erro(self):
        """Testa processamento de múltiplos contratos com erro em um deles"""
        # Mock dos componentes
        self.bot.maxycon = Mock()
        self.bot.sign = Mock()
        self.bot.file_handler = Mock()
        
        # Configurar retornos para o primeiro contrato (sucesso)
        self.bot.maxycon.download_contrato.side_effect = [
            "temp/contrato1.pdf",  # Primeiro contrato OK
            Exception("Erro ao baixar segundo contrato")  # Segundo contrato falha
        ]
        self.bot.file_handler.salvar_contrato_novo.return_value = "contratos/novos/contrato.pdf"
        self.bot.sign.anexar_contrato.return_value = True
        
        # Dados de teste
        contratos = [
            {'id': '123', 'numero': '12345', 'cliente': 'Cliente A'},
            {'id': '456', 'numero': '67890', 'cliente': 'Cliente B'}
        ]
        
        # Executar processamento para cada contrato
        for contrato in contratos:
            try:
                self.bot._processar_contrato(contrato)
            except Exception:
                continue
        
        # Verificações
        self.assertEqual(len(self.bot.contratos_processados), 1)
        self.assertEqual(self.bot.contratos_processados[0]['numero'], '12345')
        self.bot.maxycon.download_contrato.assert_has_calls([
            call('123'),
            call('456')
        ])

    def test_enviar_notificacoes_erro_whatsapp(self):
        """Testa erro no envio de notificações via WhatsApp"""
        # Mock dos componentes
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        
        # Simular erro no WhatsApp
        self.bot.whatsapp.enviar_alerta_diario.side_effect = Exception("Erro no envio WhatsApp")
        
        # Dados de teste
        self.bot.contratos_processados = [
            {'numero': '123', 'cliente': 'Cliente A'},
            {'numero': '456', 'cliente': 'Cliente B'}
        ]
        
        # Executar teste - não deve lançar exceção
        self.bot._enviar_notificacoes()
        
        # Verificar que o e-mail foi enviado mesmo com erro no WhatsApp
        self.bot.email.enviar_notificacao_novos_contratos.assert_called_with(
            self.bot.contratos_processados
        )

    def test_gerar_relatorio_diario_erro_whatsapp(self):
        """Testa erro no envio do relatório diário via WhatsApp"""
        # Mock dos componentes
        self.bot.file_handler = Mock()
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        
        # Simular erro no WhatsApp
        self.bot.whatsapp.enviar_alerta_diario.side_effect = Exception("Erro no envio WhatsApp")
        
        # Dados de teste
        self.bot.contratos_processados = [{'numero': '123'}]
        self.bot.contratos_finalizados = [{'numero': '456'}]
        
        # Executar teste
        self.bot._gerar_relatorio_diario()
        
        # Verificar que arquivo foi salvo e e-mail foi enviado
        relatorio_esperado = {
            'data': datetime.now().strftime("%d/%m/%Y"),
            'novos_contratos': self.bot.contratos_processados,
            'contratos_finalizados': self.bot.contratos_finalizados,
            'total_novos': 1,
            'total_finalizados': 1
        }
        
        self.bot.file_handler.salvar_relatorio.assert_called_with(relatorio_esperado)
        self.bot.email.enviar_relatorio_diario.assert_called_with(relatorio_esperado)

    def test_gerar_relatorio_diario_erro_whatsapp_apos_email(self):
        """Testa erro no envio do relatório via WhatsApp após sucesso no e-mail"""
        # Mock dos componentes
        self.bot.file_handler = Mock()
        self.bot.email = Mock()
        self.bot.whatsapp = Mock()
        
        # Simular erro apenas no WhatsApp
        self.bot.whatsapp.enviar_alerta_diario.side_effect = Exception("Erro no envio WhatsApp")
        
        # Dados de teste
        self.bot.contratos_processados = [
            {'numero': '123', 'cliente': 'Cliente A'},
            {'numero': '456', 'cliente': 'Cliente B'}
        ]
        
        # Executar teste - não deve lançar exceção
        self.bot._gerar_relatorio_diario()
        
        # Verificar que arquivo foi salvo e e-mail foi enviado
        relatorio_esperado = {
            'data': datetime.now().strftime("%d/%m/%Y"),
            'novos_contratos': self.bot.contratos_processados,
            'contratos_finalizados': self.bot.contratos_finalizados,
            'total_novos': 2,
            'total_finalizados': 0
        }
        
        # Verificar chamadas
        self.bot.file_handler.salvar_relatorio.assert_called_with(relatorio_esperado)
        self.bot.email.enviar_relatorio_diario.assert_called_with(relatorio_esperado)
        self.bot.whatsapp.enviar_alerta_diario.assert_called_with(self.bot.contratos_processados)