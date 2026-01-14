from .base import BaseInvoiceParser
import re
from decimal import Decimal

class VivoParser(BaseInvoiceParser):
    def parse(self, pdf_file):
        text = self.extract_text(pdf_file)
        
        data = {
            'invoice_number': None,
            'due_date': None,
            'total_value': None,
            'carrier': 'VIVO',
            'confidence': 100 # Default to perfect parsing (PDF Digital)
        }

        if not text:
            data['confidence'] = 0
            return data

        # --- PRIMARY PARSING (DO NOT ALTER) ---
        # 1. Extração do Valor Total
        total_patterns = [
            r'Total a pagar\s*(?:R\$)?\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'VALOR TOTAL\s*(?:R\$)?\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'Total desta fatura\s*(?:R\$)?\s*(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'Valor a pagar\s*(?:R\$)?\s*(\d{1,3}(?:\.\d{3})*,\d{2})'
        ]
        
        found_values = []
        for pattern in total_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                val = self.clean_currency(m)
                if val:
                    found_values.append(val)
        
        if found_values:
            data['total_value'] = max(found_values)
        
        # 2. Extração da Data de Vencimento
        date_patterns = [
            r'Vencimento\s*(\d{2}/\d{2}/\d{4})',
            r'Data de vencimento\s*(\d{2}/\d{2}/\d{4})',
            r'Vence em\s*(\d{2}/\d{2}/\d{4})',
            r'Pague até\s*(\d{2}/\d{2}/\d{4})'
        ]
        
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                data['due_date'] = self.parse_date(date_match.group(1))
                if data['due_date']:
                    break
            
        # 3. Número da Fatura
        inv_match = re.search(r'(?:Fatura número|Nº da fatura|Conta No\.)\s*(\d+)', text, re.IGNORECASE)
        if inv_match:
            data['invoice_number'] = inv_match.group(1)

        # --- FALLBACK PARSING (TRIGGERED ONLY IF DATA IS MISSING OR LAYOUT DETECTED) ---
        if not data['total_value'] or not data['due_date'] or not data['invoice_number']:
            # Downgrade confidence because primary method failed
            data['confidence'] = 80 # Validated heurística fallback
            self._parse_fallback(text, data)
            
            # If still missing info after fallback, downgrade further
            if not data['total_value'] or not data['due_date']:
                data['confidence'] = 50 # Partial extraction
                
        return data

    def _parse_fallback(self, text, data):
        """
        Fallback logic for specific problematic layouts (cards, summary sidebars, fatura fixa, etc.)
        Activated if primary parsing fails.
        """
        print(f"[VivoParser] Fallback específico para fatura fixa ativado. Texto detectado: {text[:50]}...")

        # Fallback Total Value Patterns
        fallback_total_patterns = [
            r'TOTAL GERAL A PAGAR[\s\S]{0,50}?(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'TOTAL A PAGAR[\s\S]{0,50}?(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'Total Geral[\s\S]{0,50}?(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'(?:Resumo|VALOR \(R\$\))[\s\S]{0,50}?(\d{1,3}(?:\.\d{3})*,\d{2})',
            r'valor.*?(\d{1,3}(?:\.\d{3})*,\d{2})',
        ]

        if not data['total_value']:
            f_found_values = []
            for pattern in fallback_total_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for m in matches:
                    val = self.clean_currency(m)
                    if val:
                        f_found_values.append(val)
            if f_found_values:
                data['total_value'] = max(f_found_values)

        # Fallback Date Patterns
        fallback_date_patterns = [
            r'VENCIMENTO[\s\S]{0,50}?(\d{2}/\d{2}/\d{4})',
            r'Venc\.[\s\S]{0,50}?(\d{2}/\d{2}/\d{4})',
            r'(?:Pagamento até|Data limite|Pague até)[\s\S]{0,50}?(\d{2}/\d{2}/\d{4})',
            r'(\d{2}/\d{2}/\d{4})', # any date
        ]

        if not data['due_date']:
            f_found_dates = []
            for pattern in fallback_date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for m in matches:
                    parsed_date = self.parse_date(m)
                    if parsed_date:
                        f_found_dates.append(parsed_date)
            if f_found_dates:
                # O vencimento costuma ser a data solitária ou a última do header
                data['due_date'] = max(f_found_dates)
        
        # Fallback Invoice Number
        if not data['invoice_number']:
            inv_match = re.search(r'Fatura\D*(\d{7,15})', text, re.IGNORECASE)
            if inv_match:
                data['invoice_number'] = inv_match.group(1)
