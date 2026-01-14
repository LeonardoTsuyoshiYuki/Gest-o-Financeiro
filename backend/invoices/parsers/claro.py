from .base import BaseInvoiceParser
import re

class ClaroParser(BaseInvoiceParser):
    def parse(self, pdf_file):
        text = self.extract_text(pdf_file)
        
        data = {
            'invoice_number': None,
            'due_date': None,
            'total_value': None,
            'carrier': 'CLARO',
            'confidence': 100
        }

        if not text:
            data['confidence'] = 0
            return data

        # Exemplo Claro: "TOTAL A PAGAR R$ 89,90"
        val_match = re.search(r'TOTAL A PAGAR.*?(\d+,\d{2})', text, re.IGNORECASE)
        if val_match:
            data['total_value'] = self.clean_currency(val_match.group(1))
        
        # Exemplo Claro: "VENCIMENTO 15/12/2025"
        date_match = re.search(r'VENCIMENTO.*?(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
        if date_match:
            data['due_date'] = self.parse_date(date_match.group(1))
            
        if not data['total_value'] or not data['due_date']:
            data['confidence'] = 50

        return data
