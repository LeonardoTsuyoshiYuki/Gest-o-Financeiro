import os
import re

class DirectoryScanner:
    def __init__(self, base_path):
        self.base_path = base_path

    def scan(self):
        """
        Estrutura esperada: Ano / Cidade / Operadora / Mês / *.pdf
        Retorna lista de dicionários com metadados extraídos do path.
        """
        results = []
        
        # Walk através da estrutura de pastas
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    full_path = os.path.join(root, file)
                    
                    # Tenta extrair metadados via path relativo
                    rel_path = os.path.relpath(full_path, self.base_path)
                    parts = rel_path.split(os.sep)
                    
                    #parts: [Ano, Cidade, Operadora, Mês, Arquivo]
                    if len(parts) >= 5:
                        results.append({
                            'path': full_path,
                            'year': parts[0],
                            'city': parts[1],
                            'carrier': parts[2],
                            'month': parts[3],
                            'filename': parts[4]
                        })
        return results
