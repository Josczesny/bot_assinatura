import unittest
import sys
import os

def executar_testes():
    """Executa todos os testes do projeto"""
    # Adicionar diretório raiz ao path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Descobrir e executar todos os testes
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Executar testes
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    sucesso = executar_testes()
    sys.exit(0 if sucesso else 1)