# backend/api.py
"""
Flask API voor Makelaar Contract Generator
Production-ready version voor Replit deployment
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
from pathlib import Path
import uuid

app = Flask(__name__)
CORS(app)

# Configuratie
UPLOAD_FOLDER = 'backend/uploads'
CONTRACTS_FOLDER = 'backend/generated_contracts'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))

# Simple in-memory database
database = {
    'contracts': {},
    'documents': {}
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/contract/create', methods=['POST'])
def create_contract():
    """Maak een nieuw contract aan"""
    contract_id = str(uuid.uuid4())
    database['contracts'][contract_id] = {
        'id': contract_id,
        'created_at': datetime.now().isoformat(),
        'status': 'draft',
        'form_data': {},
        'documents': {},
        'validation': {}
    }
    
    return jsonify({
        'success': True,
        'contract_id': contract_id
    })


@app.route('/api/contract/<contract_id>/upload', methods=['POST'])
def upload_document(contract_id):
    """Upload en process een document"""
    
    if contract_id not in database['contracts']:
        return jsonify({'error': 'Contract niet gevonden'}), 404
    
    if 'file' not in request.files:
        return jsonify({'error': 'Geen file gevonden'}), 400
    
    file = request.files['file']
    doc_type = request.form.get('doc_type')
    
    if not doc_type:
        return jsonify({'error': 'doc_type is verplicht'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'Geen file geselecteerd'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Save file
            filename = secure_filename(f"{contract_id}_{doc_type}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process document
            from backend.document_processor import DocumentProcessor
            processor = DocumentProcessor()
            extracted_data = processor.process_document(filepath, doc_type)
            validation = processor.validate_extracted_data(extracted_data, doc_type)
            
            # Store in database
            database['contracts'][contract_id]['documents'][doc_type] = {
                'filename': filename,
                'filepath': filepath,
                'uploaded_at': datetime.now().isoformat(),
                'extracted_data': extracted_data,
                'validation': validation
            }
            
            # Merge extracted data into form_data
            database['contracts'][contract_id]['form_data'].update(extracted_data)
            
            return jsonify({
                'success': True,
                'extracted_data': extracted_data,
                'validation': validation,
                'message': f'Document {doc_type} verwerkt'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/api/contract/<contract_id>/data', methods=['GET', 'POST'])
def contract_data(contract_id):
    """Get of update contract data"""
    
    if contract_id not in database['contracts']:
        return jsonify({'error': 'Contract niet gevonden'}), 404
    
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': database['contracts'][contract_id]
        })
    
    if request.method == 'POST':
        new_data = request.json
        database['contracts'][contract_id]['form_data'].update(new_data)
        database['contracts'][contract_id]['updated_at'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'message': 'Data bijgewerkt'
        })


@app.route('/api/contract/<contract_id>/validate', methods=['POST'])
def validate_contract(contract_id):
    """Valideer alle contract data"""
    
    if contract_id not in database['contracts']:
        return jsonify({'error': 'Contract niet gevonden'}), 404
    
    contract = database['contracts'][contract_id]
    form_data = contract['form_data']
    
    errors = []
    warnings = []
    
    # Verplichte documenten
    required_docs = ['epc', 'bodemattest', 'vip', 'kadaster', 'eigendomstitel', 'elektrisch']
    for doc in required_docs:
        if doc not in contract['documents']:
            errors.append(f'Document {doc} is verplicht')
    
    # Verplichte velden
    required_fields = {
        'verkoper_naam': 'Naam verkoper',
        'verkoper_voornaam': 'Voornaam verkoper',
        'verkoper_adres': 'Adres verkoper',
        'koper_naam': 'Naam koper',
        'koper_voornaam': 'Voornaam koper',
        'koper_adres': 'Adres koper',
        'goed_straat': 'Straat van het goed',
        'goed_nummer': 'Huisnummer',
        'goed_postcode': 'Postcode',
        'goed_gemeente': 'Gemeente',
        'prijs_totaal': 'Totale koopprijs',
        'voorschot_bedrag': 'Voorschot/Waarborg bedrag'
    }
    
    for field, label in required_fields.items():
        if not form_data.get(field):
            errors.append(f'{label} is verplicht')
    
    # Business logic validaties
    if form_data.get('prijs_totaal') and form_data.get('voorschot_bedrag'):
        try:
            prijs = float(form_data['prijs_totaal'])
            voorschot = float(form_data['voorschot_bedrag'])
            
            if voorschot > prijs:
                errors.append('Voorschot kan niet hoger zijn dan de koopprijs')
            
            if voorschot < 2500:
                warnings.append('Voorschot is lager dan gebruikelijk minimum (€2.500)')
            
            if voorschot > prijs * 0.3:
                warnings.append('Voorschot is hoger dan 30% van de koopprijs')
                
        except ValueError:
            errors.append('Prijs en voorschot moeten numerieke waarden zijn')
    
    # Email validatie
    for field in ['verkoper_email', 'koper_email']:
        if form_data.get(field):
            if '@' not in form_data[field]:
                errors.append(f'{field} is geen geldig email adres')
    
    validation_result = {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'validated_at': datetime.now().isoformat()
    }
    
    database['contracts'][contract_id]['validation'] = validation_result
    
    return jsonify({
        'success': True,
        'validation': validation_result
    })


@app.route('/api/contract/<contract_id>/generate', methods=['POST'])
def generate_contract(contract_id):
    """Genereer het Word contract"""
    
    if contract_id not in database['contracts']:
        return jsonify({'error': 'Contract niet gevonden'}), 404
    
    contract = database['contracts'][contract_id]
    
    # Valideer eerst
    validation = contract.get('validation', {})
    if not validation.get('is_valid'):
        return jsonify({
            'success': False,
            'error': 'Contract is niet valide. Valideer eerst.',
            'errors': validation.get('errors', [])
        }), 400
    
    try:
        from backend.word_generator import ContractGenerator
        generator = ContractGenerator()
        
        output_filename = f"contract_{contract_id}.docx"
        output_path = os.path.join(CONTRACTS_FOLDER, output_filename)
        
        # Genereer contract
        generator.generate_simple_contract(contract['form_data'], output_path)
        
        database['contracts'][contract_id]['status'] = 'generated'
        database['contracts'][contract_id]['generated_at'] = datetime.now().isoformat()
        database['contracts'][contract_id]['output_file'] = output_filename
        
        return jsonify({
            'success': True,
            'message': 'Contract gegenereerd',
            'download_url': f'/api/contract/{contract_id}/download'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/contract/<contract_id>/download', methods=['GET'])
def download_contract(contract_id):
    """Download het gegenereerde contract"""
    
    if contract_id not in database['contracts']:
        return jsonify({'error': 'Contract niet gevonden'}), 404
    
    contract = database['contracts'][contract_id]
    
    if 'output_file' not in contract:
        return jsonify({'error': 'Contract nog niet gegenereerd'}), 400
    
    output_path = os.path.join(CONTRACTS_FOLDER, contract['output_file'])
    
    if not os.path.exists(output_path):
        return jsonify({'error': 'Bestand niet gevonden'}), 404
    
    return send_file(
        output_path,
        as_attachment=True,
        download_name=f"verkoopovereenkomst_{datetime.now().strftime('%Y%m%d')}.docx",
        mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )


@app.route('/api/contracts', methods=['GET'])
def list_contracts():
    """List alle contracts"""
    contracts = []
    for contract_id, contract in database['contracts'].items():
        contracts.append({
            'id': contract_id,
            'created_at': contract.get('created_at'),
            'status': contract.get('status'),
            'has_validation': 'validation' in contract,
            'document_count': len(contract.get('documents', {}))
        })
    
    contracts.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'success': True,
        'contracts': contracts
    })


@app.route('/api/documents/types', methods=['GET'])
def get_document_types():
    """Geef lijst van ondersteunde document types"""
    return jsonify({
        'success': True,
        'document_types': [
            {
                'id': 'epc',
                'name': 'EPC (Energieprestatiecertificaat)',
                'required': True,
                'description': 'Energieprestatiecertificaat met label en score'
            },
            {
                'id': 'bodemattest',
                'name': 'Bodemattest',
                'required': True,
                'description': 'OVAM bodemattest voor bodemverontreiniging'
            },
            {
                'id': 'vip',
                'name': 'VIP-dossier (Stedenbouw)',
                'required': True,
                'description': 'Stedenbouwkundige informatie en vergunningen'
            },
            {
                'id': 'kadaster',
                'name': 'Kadastrale legger en plan',
                'required': True,
                'description': 'Kadastrale gegevens, sectie, nummer, oppervlakte'
            },
            {
                'id': 'eigendomstitel',
                'name': 'Eigendomstitel',
                'required': True,
                'description': 'Notariële akte met eigendomsgegevens'
            },
            {
                'id': 'elektrisch',
                'name': 'Elektrische keuring',
                'required': True,
                'description': 'Keuringsattest elektrische installatie'
            },
            {
                'id': 'stookolie',
                'name': 'Keuringattest stookolietank',
                'required': False,
                'description': 'Attest voor stookolietank indien aanwezig'
            },
            {
                'id': 'asbestattest',
                'name': 'Asbestattest',
                'required': False,
                'description': 'Asbestattest voor gebouwen van voor 2001'
            }
        ]
    })


@app.route('/api/contract/<contract_id>/summary', methods=['GET'])
def get_contract_summary(contract_id):
    """Geef een samenvatting van het contract voor preview"""
    
    if contract_id not in database['contracts']:
        return jsonify({'error': 'Contract niet gevonden'}), 404
    
    contract = database['contracts'][contract_id]
    form_data = contract['form_data']
    
    def calculate_completion():
        total_items = 18
        completed_items = 0
        
        required_docs = ['epc', 'bodemattest', 'vip', 'kadaster', 'eigendomstitel', 'elektrisch']
        completed_items += len([d for d in required_docs if d in contract['documents']])
        
        required_fields = [
            'verkoper_naam', 'verkoper_voornaam', 'verkoper_adres',
            'koper_naam', 'koper_voornaam', 'koper_adres',
            'goed_straat', 'goed_nummer', 'goed_postcode', 'goed_gemeente',
            'prijs_totaal', 'voorschot_bedrag'
        ]
        completed_items += len([f for f in required_fields if form_data.get(f)])
        
        return round((completed_items / total_items) * 100) if total_items > 0 else 0
    
    summary = {
        'contract_id': contract_id,
        'status': contract['status'],
        'created_at': contract['created_at'],
        
        'parties': {
            'verkoper': {
                'naam': form_data.get('verkoper_naam', ''),
                'voornaam': form_data.get('verkoper_voornaam', ''),
                'adres': form_data.get('verkoper_adres', ''),
                'email': form_data.get('verkoper_email', ''),
                'telefoon': form_data.get('verkoper_telefoonnummer', '')
            },
            'koper': {
                'naam': form_data.get('koper_naam', ''),
                'voornaam': form_data.get('koper_voornaam', ''),
                'adres': form_data.get('koper_adres', ''),
                'email': form_data.get('koper_email', ''),
                'telefoon': form_data.get('koper_telefoonnummer', '')
            }
        },
        
        'property': {
            'adres': f"{form_data.get('goed_straat', '')} {form_data.get('goed_nummer', '')}",
            'postcode': form_data.get('goed_postcode', ''),
            'gemeente': form_data.get('goed_gemeente', ''),
            'kadaster': {
                'afdeling': form_data.get('goed_kadastrale_afdeling', ''),
                'sectie': form_data.get('goed_kadastrale_sectie', ''),
                'nummer': form_data.get('goed_kadastrale_nummer', ''),
                'oppervlakte': form_data.get('goed_kadastrale_oppervlakte', '')
            }
        },
        
        'financieel': {
            'prijs_totaal': form_data.get('prijs_totaal', 0),
            'voorschot': form_data.get('voorschot_bedrag', 0),
            'saldo': float(form_data.get('prijs_totaal', 0) or 0) - float(form_data.get('voorschot_bedrag', 0) or 0)
        },
        
        'documents': {
            doc_type: {
                'uploaded': True,
                'filename': doc_data['filename'],
                'validation': doc_data['validation']
            }
            for doc_type, doc_data in contract['documents'].items()
        },
        
        'certificates': {
            'epc': {
                'code': form_data.get('epc_code', ''),
                'label': form_data.get('epc_label', ''),
                'datum': form_data.get('epc_datum', '')
            },
            'bodemattest': {
                'referentie': form_data.get('bodem_attest_referentie', ''),
                'datum': form_data.get('bodem_attest_datum', '')
            }
        },
        
        'completion_percentage': calculate_completion()
    }
    
    return jsonify({
        'success': True,
        'summary': summary
    })


# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Bestand is te groot (max 16MB)'}), 413


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Niet gevonden'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Server fout', 'message': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting Makelaar Contract Generator API")
    print("📄 API Documentation: http://localhost:5000/health")
    app.run(debug=True, host='0.0.0.0', port=5000)
