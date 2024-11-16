import os
import shutil
from datetime import datetime
import logging
from pathlib import Path

class FileHandler:
    def __init__(self, config):
        self.config = config
        self._criar_diretorios()
        self._configurar_logging()

    def _criar_diretorios(self):
        """Cria os diretórios necessários se não existirem"""
        diretorios = [
            self.config.CONTRATOS_NOVOS_PATH,
            self.config.CONTRATOS_FINALIZADOS_PATH,
            'logs'
        ]
        
        for diretorio in diretorios:
            Path(diretorio).mkdir(parents=True, exist_ok=True)

    def _configurar_logging(self):
        """Configura o sistema de logging"""
        logging.basicConfig(
            filename=f'logs/file_operations_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def salvar_contrato_novo(self, arquivo_pdf, numero_contrato):
        """Salva um novo contrato na pasta apropriada"""
        try:
            nome_arquivo = f"contrato_{numero_contrato}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            caminho_destino = os.path.join(self.config.CONTRATOS_NOVOS_PATH, nome_arquivo)
            
            shutil.copy2(arquivo_pdf, caminho_destino)
            logging.info(f"Contrato {numero_contrato} salvo com sucesso em {caminho_destino}")
            
            return caminho_destino
        except Exception as e:
            logging.error(f"Erro ao salvar contrato {numero_contrato}: {str(e)}")
            raise

    def mover_para_finalizados(self, caminho_arquivo):
        """Move um contrato para a pasta de finalizados"""
        try:
            nome_arquivo = os.path.basename(caminho_arquivo)
            destino = os.path.join(self.config.CONTRATOS_FINALIZADOS_PATH, nome_arquivo)
            
            shutil.move(caminho_arquivo, destino)
            logging.info(f"Contrato movido para finalizados: {destino}")
            
            return destino
        except Exception as e:
            logging.error(f"Erro ao mover contrato: {str(e)}")
            raise

    def listar_contratos_novos(self):
        """Lista todos os contratos na pasta de novos"""
        return [f for f in os.listdir(self.config.CONTRATOS_NOVOS_PATH) if f.endswith('.pdf')]

    def listar_contratos_finalizados(self):
        """Lista todos os contratos na pasta de finalizados"""
        return [f for f in os.listdir(self.config.CONTRATOS_FINALIZADOS_PATH) if f.endswith('.pdf')]

    def criar_relatorio_csv(self, dados, nome_arquivo):
        """Cria um arquivo CSV com os dados do relatório"""
        import csv
        try:
            caminho_arquivo = f"relatorios/{nome_arquivo}_{datetime.now().strftime('%Y%m%d')}.csv"
            
            with open(caminho_arquivo, 'w', newline='') as arquivo:
                writer = csv.DictWriter(arquivo, fieldnames=dados[0].keys())
                writer.writeheader()
                writer.writerows(dados)
            
            logging.info(f"Relatório CSV criado: {caminho_arquivo}")
            return caminho_arquivo
        except Exception as e:
            logging.error(f"Erro ao criar relatório CSV: {str(e)}")
            raise