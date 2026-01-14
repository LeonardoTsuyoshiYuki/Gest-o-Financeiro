from django.test import TestCase
from decimal import Decimal
from datetime import date
from unittest.mock import patch
from .parsers.vivo import VivoParser

class VivoFaturaFixaTests(TestCase):
    def setUp(self):
        self.parser = VivoParser()

    def test_vivo_fatura_fixa_layout(self):
        """
        Testa o layout específico de fatura fixa da Vivo Empresa (conforme imagem).
        """
        text = """
        VIVO EMPRESAS
        MATRA MAQUINAS E TRATORES AGRICOLAS COMERCIO LTDA
        CNPJ: 03.682.747/0001-65
        Número da Conta: 699991956555
        Número da Fatura: 2008843401
        Período de Utilização: 09/11/2025 a 08/12/2025
        
        MÊS DE REFERÊNCIA
        12/2025
        
        VENCIMENTO
        03/01/2026
        
        TOTAL A PAGAR
        R$ 929,30
        
        RESUMO                                    VALOR (R$)
        Telefone + Serviços Digitais e Técnicos
        Consumo Mínimo                            900,00
        TOTAL GERAL A PAGAR                       929,30
        """
        
        with patch.object(self.parser, 'extract_text', return_value=text):
            data = self.parser.parse("fatura_fixa_fake.pdf")
            
            # Validações baseadas na imagem fornecida
            self.assertEqual(data['total_value'], Decimal('929.30'))
            self.assertEqual(data['due_date'], date(2026, 1, 3))
            self.assertEqual(data['invoice_number'], '2008843401')

    def test_no_regression_previous_layouts(self):
        """Garante que faturas que já funcionavam continuam funcionando perfeitamente."""
        # Exemplo de layout já funcional
        text = """
        VIVO EMPRESAS
        TOTAL GERAL A PAGAR R$ 2.895,14
        Vencimento 10/01/2026
        Fatura número 123456789
        """
        with patch.object(self.parser, 'extract_text', return_value=text):
            data = self.parser.parse("fake_anterior.pdf")
            self.assertEqual(data['total_value'], Decimal('2895.14'))
            self.assertEqual(data['due_date'], date(2026, 1, 10))
            self.assertEqual(data['invoice_number'], '123456789')

    def test_vivo_fallback_triggered_log(self):
        """Verifica se o log de ativação do fallback é impresso (via stdout)."""
        import sys
        from io import StringIO
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        text = "Fatura Fixa Vivo\nTOTAL A PAGAR R$ 100,00\nVENCIMENTO 01/01/2026"
        
        try:
            with patch.object(self.parser, 'extract_text', return_value=text):
                self.parser.parse("test_log.pdf")
            
            output = captured_output.getvalue()
            self.assertIn("[VivoParser] Fallback específico para fatura fixa ativado", output)
        finally:
            sys.stdout = sys.__stdout__
