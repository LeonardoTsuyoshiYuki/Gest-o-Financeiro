from django.test import TestCase
from decimal import Decimal
from datetime import date
from unittest.mock import patch
from .parsers.vivo import VivoParser

class VivoParserFallbackTests(TestCase):
    def setUp(self):
        self.parser = VivoParser()

    def test_layout_total_geral_pagar(self):
        """Layout que usa 'TOTAL GERAL A PAGAR' em vez do padrão 'Total a pagar'."""
        text = """
        VIVO EMPRESAS
        impressão Página 1 de 5
        Informações da Conta
        TOTAL GERAL A PAGAR R$ 2.895,14
        Vencimento 10/01/2026
        Fatura número 123456789
        """
        with patch.object(VivoParser, 'extract_text', return_value=text):
            data = self.parser.parse("fake.pdf")
            self.assertEqual(data['total_value'], Decimal('2895.14'))
            self.assertEqual(data['due_date'], date(2026, 1, 10))
            self.assertEqual(data['invoice_number'], '123456789')

    def test_layout_cards_visual(self):
        """Layout tipo cards onde o rótulo e o valor podem estar em linhas diferentes ou formatos distintos."""
        text = """
        VIVO
        Resumo da sua fatura
        
        VENCIMENTO
        15/02/2026
        
        VALOR TOTAL
        R$ 1.250,50
        
        Nº da fatura: 987654321
        """
        # Aqui o primary parser para multi-line pode falhar se não houver regex específico
        with patch.object(VivoParser, 'extract_text', return_value=text):
            data = self.parser.parse("fake.pdf")
            self.assertEqual(data['due_date'], date(2026, 2, 15))
            self.assertEqual(data['total_value'], Decimal('1250.50'))

    def test_no_regression_primary_layout(self):
        """Garante que layouts que já funcionavam continuam funcionando."""
        text = """
        CONTA VIVO
        Total a pagar R$ 350,00
        Vencimento 20/03/2026
        """
        with patch.object(VivoParser, 'extract_text', return_value=text):
            data = self.parser.parse("fake.pdf")
            self.assertEqual(data['total_value'], Decimal('350.00'))
            self.assertEqual(data['due_date'], date(2026, 3, 20))

    def test_mixed_layout_detection(self):
        """Testa se o fallback é ativado quando detecta palavras chave mesmo com dados parciais."""
        text = """
        VIVO EMPRESAS
        Resumo
        Valor Total desta fatura: R$ 500,00
        Sem a data de vencimento padrão aqui...
        Venc. 05/05/2026
        """
        with patch.object(VivoParser, 'extract_text', return_value=text):
            data = self.parser.parse("fake.pdf")
            # Primary pegaria o Total desta fatura (r'Total desta fatura\s*(?:R\$)?\s*(\d{1,3}(?:\.\d{3})*,\d{2})')
            # Mas não pegaria o Venc. (Primary tem 'Vencimento', 'Data de vencimento', 'Vence em', 'Pague até')
            self.assertEqual(data['total_value'], Decimal('500.00')) 
            self.assertEqual(data['due_date'], date(2026, 5, 5)) # Fallback pegou Venc.
