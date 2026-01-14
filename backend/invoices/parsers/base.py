from abc import ABC, abstractmethod
import pdfplumber
import re
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
from datetime import datetime
from decimal import Decimal
import io

class BaseInvoiceParser(ABC):
    @abstractmethod
    def parse(self, pdf_file):
        """
        Recebe um caminho de arquivo ou objeto de arquivo e retorna dados extraídos.
        """
        pass

    def extract_text(self, pdf_file):
        text = ""
        try:
            # Garante que o ponteiro está no início se for um objeto de arquivo
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
                
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Erro pdfplumber: {e}")

        # Se o texto for muito curto, pode ser um PDF escaneado
        if len(text.strip()) < 50:
            text = self.extract_text_via_ocr(pdf_file)
            
        return text

    def extract_text_via_ocr(self, pdf_file):
        text = ""
        try:
            if hasattr(pdf_file, 'seek'):
                pdf_file.seek(0)
            
            # Se for um caminho de arquivo
            if isinstance(pdf_file, str):
                images = convert_from_path(pdf_file, last_page=2)
            else:
                # Se for um objeto de arquivo (upload)
                content = pdf_file.read()
                images = convert_from_bytes(content, last_page=2)
                # Reset pointer again just in case
                if hasattr(pdf_file, 'seek'):
                    pdf_file.seek(0)

            for img in images:
                text += pytesseract.image_to_string(img, lang='por') + "\n"
        except Exception as e:
            print(f"Erro no OCR: {e}")
        return text

    def clean_currency(self, value_str):
        if not value_str:
            return None
        clean = re.sub(r'[^\d,]', '', value_str).replace(',', '.')
        try:
            return Decimal(clean)
        except:
            return None

    def parse_date(self, date_str, fmt='%d/%m/%Y'):
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except:
            return None
