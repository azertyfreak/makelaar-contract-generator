# backend/document_processor.py
"""
Document Processing Engine voor Makelaar Contract Generator
Mock versie voor Replit (zonder zware OCR libraries)
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
import json
import uuid


class DocumentParser:
    """Base class voor document parsing"""
    
    def __init__(self, text: str):
        self.text = text
        self.lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    def extract_date(self, pattern: str = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}') -> Optional[str]:
        """Extract datum in verschillende formaten"""
        match = re.search(pattern, self.text)
        if match:
            date_str = match.group()
            try:
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime('%Y-%m-%d')
                    except:
                        continue
            except:
                return date_str
        return None
    
    def find_field(self, keywords: List[str], after_keyword: bool = True) -> Optional[str]:
        """Zoek waarde na keyword"""
        for line in self.lines:
            for keyword in keywords:
                if keyword.lower() in line.lower():
                    if after_keyword:
                        parts = line.split(keyword, 1)
                        if len(parts) > 1:
                            return parts[1].strip().rstrip(':').strip()
                    else:
                        return line
        return None


class EPCParser(DocumentParser):
    """Parser voor Energieprestatiecertificaat"""
    
    def parse(self) -> Dict:
        data = {}
        
        # Mock data voor demo
        data['epc_code'] = f'EPC-2024-{uuid.uuid4().hex[:8].upper()}'
        data['epc_datum'] = datetime.now().strftime('%Y-%m-%d')
        data['epc_label'] = 'C'
        data['epc_score'] = '250 kWh/m²'
        
        return data


class BodemattestParser(DocumentParser):
    """Parser voor Bodemattest van OVAM"""
    
    def parse(self) -> Dict:
        data = {}
        
        # Mock data
        data['bodem_attest_referentie'] = f'OVAM-2024-{uuid.uuid4().hex[:6].upper()}'
        data['bodem_attest_datum'] = datetime.now().strftime('%Y-%m-%d')
        data['bodem_attest_inhoud'] = 'Geen bodemverontreiniging vastgesteld'
        data['bodem_activiteiten_geen'] = True
        
        return data


class KadasterParser(DocumentParser):
    """Parser voor Kadastrale documenten"""
    
    def parse(self) -> Dict:
        data = {}
        
        # Mock data
        data['goed_kadastrale_afdeling'] = '1'
        data['goed_kadastrale_sectie'] = 'A'
        data['goed_kadastrale_nummer'] = f'{uuid.uuid4().int % 1000}/02A'
        data['goed_kadastrale_oppervlakte'] = '450 m²'
        data['goed_kadastraal_inkomen_bedrag'] = '1250'
        data['goed_kadastraal_inkomen_bedraagt'] = True
        
        return data


class VIPParser(DocumentParser):
    """Parser voor VIP-dossier (Stedenbouw)"""
    
    def parse(self) -> Dict:
        data = {}
        
        # Mock data
        data['stedenbouw_meest_recente_bestemming'] = 'Woongebied'
        data['stedenbouw_vergunning_afgeleverd'] = True
        data['stedenbouw_plannenregister_goedgekeurd'] = True
        data['stedenbouw_uittreksel_datum'] = datetime.now().strftime('%Y-%m-%d')
        data['stedenbouw_in_verkaveling'] = False
        data['stedenbouw_inbreuken_geen'] = True
        
        return data


class ElektrischeKeuringParser(DocumentParser):
    """Parser voor Elektrische keuring"""
    
    def parse(self) -> Dict:
        data = {}
        
        # Mock data
        data['elektrische_keuring_datum'] = datetime.now().strftime('%Y-%m-%d')
        data['elektrische_keuring_a1'] = True
        data['elektrisch_conform'] = True
        
        return data


class StookolietankParser(DocumentParser):
    """Parser voor Stookolietank attest"""
    
    def parse(self) -> Dict:
        data = {}
        
        # Mock data
        data['stookolietank_geen'] = True
        
        return data


class EigendomstitelParser(DocumentParser):
    """Parser voor Eigendomstitel"""
    
    def parse(self) -> Dict:
        data = {}
        
        # Mock data
        data['erfdienstbaarheden_vermeld'] = 'Geen bijzondere erfdienstbaarheden'
        
        return data


class AsbestattestParser(DocumentParser):
    """Parser voor Asbestattest"""
    
    def parse(self) -> Dict:
        data = {}
        
        # Mock data
        data['asbestattest_aanwezig'] = True
        data['asbestattest_code'] = f'ASB-{uuid.uuid4().hex[:10].upper()}'
        data['asbestattest_datum'] = datetime.now().strftime('%Y-%m-%d')
        data['asbestattest_veilig'] = True
        data['asbestattest_identificatie'] = 'Geen asbest geïdentificeerd'
        
        return data


class DocumentProcessor:
    """Main processor voor alle document types"""
    
    PARSERS = {
        'epc': EPCParser,
        'bodemattest': BodemattestParser,
        'kadaster': KadasterParser,
        'vip': VIPParser,
        'elektrisch': ElektrischeKeuringParser,
        'stookolie': StookolietankParser,
        'eigendomstitel': EigendomstitelParser,
        'asbestattest': AsbestattestParser,
    }
    
    def __init__(self):
        # Mock mode - geen echte OCR voor Replit
        self.ocr_mode = 'mock'
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Mock text extraction
        In productie met EasyOCR:
        
        from pdf2image import convert_from_path
        images = convert_from_path(pdf_path)
        text = ""
        for image in images:
            result = self.reader.readtext(image, detail=0)
            text += " ".join(result) + "\n"
        return text
        """
        return f"Mock text extraction for {pdf_path}"
    
    def process_document(self, file_path: str, doc_type: str) -> Dict:
        """Process een document en extract structured data"""
        
        if doc_type not in self.PARSERS:
            return {'error': f'Onbekend document type: {doc_type}'}
        
        # Mock text (in productie: echte OCR)
        text = self.extract_text_from_pdf(file_path)
        
        # Parse met juiste parser
        parser_class = self.PARSERS[doc_type]
        parser = parser_class(text)
        data = parser.parse()
        
        # Add metadata
        data['_document_type'] = doc_type
        data['_processed_at'] = datetime.now().isoformat()
        
        return data
    
    def validate_extracted_data(self, data: Dict, doc_type: str) -> Dict:
        """Valideer geëxtraheerde data en geef confidence score"""
        validation = {
            'is_valid': True,
            'confidence': 0.95,  # Mock confidence
            'missing_fields': [],
            'warnings': []
        }
        
        # Document-specifieke validatie
        required_fields = {
            'epc': ['epc_code', 'epc_datum'],
            'bodemattest': ['bodem_attest_referentie', 'bodem_attest_datum'],
            'kadaster': ['goed_kadastrale_afdeling', 'goed_kadastrale_sectie'],
            'vip': ['stedenbouw_meest_recente_bestemming'],
            'elektrisch': ['elektrische_keuring_datum'],
        }
        
        if doc_type in required_fields:
            for field in required_fields[doc_type]:
                if field not in data or not data[field]:
                    validation['missing_fields'].append(field)
                    validation['is_valid'] = False
        
        # Bereken confidence
        if doc_type in required_fields:
            found = len([f for f in required_fields[doc_type] if f in data and data[f]])
            total = len(required_fields[doc_type])
            validation['confidence'] = found / total if total > 0 else 0
        
        return validation


# Test functie
if __name__ == "__main__":
    processor = DocumentProcessor()
    
    # Test met mock data
    mock_epc_text = """
    ENERGIEPRESTATIECERTIFICAAT
    EPC-2024-1234-5678
    Datum: 15/03/2024
    Label: C
    Primair energieverbruik: 250 kWh/m²
    """
    
    parser = EPCParser(mock_epc_text)
    result = parser.parse()
    print("EPC Test Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    validation = processor.validate_extracted_data(result, 'epc')
    print("\nValidation:")
    print(json.dumps(validation, indent=2, ensure_ascii=False))
