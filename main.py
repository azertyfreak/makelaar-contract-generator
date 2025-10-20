#!/usr/bin/env python3
"""
Makelaar Contract Generator - Main Entry Point
Entry point voor zowel lokale development als Render/Railway deployment

Author: Your Name
License: MIT
"""

import os
import sys
from pathlib import Path

# Ensure backend is in path
sys.path.insert(0, str(Path(__file__).parent))

from flask import send_from_directory, send_file
from backend.api import app, database
from backend.database import ensure_directories

# Create necessary directories
ensure_directories()

# Serve static frontend
@app.route('/')
def serve_frontend():
    """Serve the main frontend page"""
    frontend_path = os.path.join(os.path.dirname(__file__), 'frontend', 'index.html')
    if os.path.exists(frontend_path):
        return send_file(frontend_path)
    else:
        # Fallback: redirect naar API status
        return """
        <html>
        <head><title>Makelaar Contract Generator</title></head>
        <body style="font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1>🏠 Makelaar Contract Generator API</h1>
            <p>De API draait! Frontend niet gevonden.</p>
            <h2>API Endpoints:</h2>
            <ul>
                <li><a href="/health">GET /health</a> - Health check</li>
                <li><a href="/api/status">GET /api/status</a> - System status</li>
                <li><a href="/api/documents/types">GET /api/documents/types</a> - Document types</li>
                <li><a href="/api/contracts">GET /api/contracts</a> - List contracts</li>
                <li>POST /api/contract/create - Create contract</li>
                <li>POST /api/demo/populate - Create demo contract</li>
            </ul>
            <h3>Quick Test:</h3>
            <button onclick="testAPI()">Create Demo Contract</button>
            <pre id="result" style="background: #f5f5f5; padding: 15px; margin-top: 10px;"></pre>
            <script>
                async function testAPI() {
                    document.getElementById('result').textContent = 'Creating demo contract...';
                    try {
                        const res = await fetch('/api/demo/populate', { method: 'POST' });
                        const data = await res.json();
                        document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                    } catch(e) {
                        document.getElementById('result').textContent = 'Error: ' + e.message;
                    }
                }
            </script>
        </body>
        </html>
        """

@app.route('/assets/<path:path>')
def serve_assets(path):
    """Serve frontend assets"""
    return send_from_directory('frontend/assets', path)

# Demo data endpoint for testing
@app.route('/api/demo/populate', methods=['POST'])
def populate_demo_data():
    """Populate demo data for testing without real documents"""
    from flask import jsonify
    import uuid
    from datetime import datetime
    
    contract_id = str(uuid.uuid4())
    
    demo_data = {
        # Verkoper
        'verkoper_naam': 'Janssens',
        'verkoper_voornaam': 'Jan',
        'verkoper_adres': 'Hoogstraat 12, 2000 Antwerpen',
        'verkoper_email': 'jan.janssens@example.com',
        'verkoper_telefoonnummer': '+32 3 123 45 67',
        'verkoper_natuurlijk_persoon': True,
        
        # Koper
        'koper_naam': 'Peeters',
        'koper_voornaam': 'Marie',
        'koper_adres': 'Kerkstraat 45, 9000 Gent',
        'koper_email': 'marie.peeters@example.com',
        'koper_telefoonnummer': '+32 9 987 65 43',
        'koper_natuurlijk_persoon': True,
        'koper_voor_zichzelf': True,
        
        # Het Goed
        'goed_straat': 'Marktplein',
        'goed_nummer': '7',
        'goed_postcode': '3000',
        'goed_gemeente': 'Leuven',
        'goed_land': 'België',
        'goed_aard': 'Woonhuis',
        
        # Kadaster
        'goed_kadastrale_afdeling': '1',
        'goed_kadastrale_sectie': 'A',
        'goed_kadastrale_nummer': '123/02A',
        'goed_kadastrale_oppervlakte': '450 m²',
        'goed_kadastraal_inkomen_bedrag': '1250',
        'goed_kadastraal_inkomen_bedraagt': True,
        
        # Financieel
        'prijs_totaal': '350000',
        'voorschot_bedrag': '35000',
        'btw_geen': True,
        
        # EPC
        'epc_code': 'EPC-2024-1234-5678',
        'epc_label': 'C',
        'epc_score': '250 kWh/m²',
        'epc_datum': '2024-03-15',
        
        # Bodemattest
        'bodem_attest_referentie': 'OVAM-2024-001234',
        'bodem_attest_datum': '2024-02-10',
        'bodem_attest_inhoud': 'Geen bodemverontreiniging vastgesteld',
        'bodem_activiteiten_geen': True,
        
        # Stedenbouw
        'stedenbouw_meest_recente_bestemming': 'Woongebied',
        'stedenbouw_vergunning_afgeleverd': True,
        'stedenbouw_plannenregister_goedgekeurd': True,
        'stedenbouw_inbreuken_geen': True,
        'stedenbouw_in_verkaveling': False,
        
        # Elektrische keuring
        'elektrische_keuring_datum': '2023-11-20',
        'elektrische_keuring_a1': True,
        
        # Andere
        'stookolietank_geen': True,
        'water_p_score': 'A',
        'water_g_score': 'A',
        'water_overstromingsgebied': False,
        'water_risicozone': False,
        'rookmelders_aanwezig': True,
        'goed_verhuurd': False,
        'goed_niet_verhuurd': True,
        'roerende_goederen_geen': True,
        
        # Notaris
        'notaris_verkoper': 'Notaris De Vries',
        'notaris_koper': 'Notaris Vermeulen',
        'akte_uiterste_datum': '2024-12-31',
        
        # Makelaar
        'makelaar_naam': 'Vastgoed Partners',
        'makelaar_biv_nummer': 'BIV123456',
        'makelaar_kantoor': 'Antwerpen Centrum',
        'aantal_exemplaren': '3',
    }
    
    # Simuleer geüploade documenten
    demo_documents = {
        'epc': {
            'filename': 'demo_epc.pdf',
            'filepath': '/demo/epc.pdf',
            'uploaded_at': datetime.now().isoformat(),
            'extracted_data': {
                'epc_code': demo_data['epc_code'],
                'epc_label': demo_data['epc_label'],
                'epc_score': demo_data['epc_score'],
                'epc_datum': demo_data['epc_datum']
            },
            'validation': {'is_valid': True, 'confidence': 0.95}
        },
        'bodemattest': {
            'filename': 'demo_bodemattest.pdf',
            'filepath': '/demo/bodemattest.pdf',
            'uploaded_at': datetime.now().isoformat(),
            'extracted_data': {
                'bodem_attest_referentie': demo_data['bodem_attest_referentie'],
                'bodem_attest_datum': demo_data['bodem_attest_datum'],
                'bodem_attest_inhoud': demo_data['bodem_attest_inhoud']
            },
            'validation': {'is_valid': True, 'confidence': 0.92}
        },
        'kadaster': {
            'filename': 'demo_kadaster.pdf',
            'filepath': '/demo/kadaster.pdf',
            'uploaded_at': datetime.now().isoformat(),
            'extracted_data': {
                'goed_kadastrale_afdeling': demo_data['goed_kadastrale_afdeling'],
                'goed_kadastrale_sectie': demo_data['goed_kadastrale_sectie'],
                'goed_kadastrale_nummer': demo_data['goed_kadastrale_nummer']
            },
            'validation': {'is_valid': True, 'confidence': 0.98}
        },
        'vip': {
            'filename': 'demo_vip.pdf',
            'filepath': '/demo/vip.pdf',
            'uploaded_at': datetime.now().isoformat(),
            'extracted_data': {
                'stedenbouw_meest_recente_bestemming': demo_data['stedenbouw_meest_recente_bestemming']
            },
            'validation': {'is_valid': True, 'confidence': 0.88}
        },
        'elektrisch': {
            'filename': 'demo_elektrisch.pdf',
            'filepath': '/demo/elektrisch.pdf',
            'uploaded_at': datetime.now().isoformat(),
            'extracted_data': {
                'elektrische_keuring_datum': demo_data['elektrische_keuring_datum']
            },
            'validation': {'is_valid': True, 'confidence': 0.91}
        },
        'eigendomstitel': {
            'filename': 'demo_eigendomstitel.pdf',
            'filepath': '/demo/eigendomstitel.pdf',
            'uploaded_at': datetime.now().isoformat(),
            'extracted_data': {},
            'validation': {'is_valid': True, 'confidence': 0.85}
        }
    }
    
    database['contracts'][contract_id] = {
        'id': contract_id,
        'created_at': datetime.now().isoformat(),
        'status': 'draft',
        'form_data': demo_data,
        'documents': demo_documents,
        'validation': {}
    }
    
    return jsonify({
        'success': True,
        'contract_id': contract_id,
        'message': 'Demo contract aangemaakt met voorbeelddata'
    })

@app.route('/api/status')
def status():
    """System status endpoint"""
    from flask import jsonify
    return jsonify({
        'status': 'online',
        'environment': os.getenv('RENDER', 'local'),
        'contracts_count': len(database['contracts']),
        'documents_count': sum(len(c.get('documents', {})) for c in database['contracts'].values()),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Render/Railway compatibility - gebruik PORT env variable
    port = int(os.getenv('PORT', 5000))
    host = '0.0.0.0'  # Moet 0.0.0.0 zijn voor deployment
    debug = False  # Altijd False in productie
    
    print("=" * 70)
    print("🏠 MAKELAAR CONTRACT GENERATOR")
    print("=" * 70)
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📊 Status: http://{host}:{port}/api/status")
    print(f"🧪 Demo: POST http://{host}:{port}/api/demo/populate")
    print(f"🔧 Environment: {os.getenv('RENDER_SERVICE_NAME', 'Local')}")
    print("=" * 70)
    
    # CRITICAL: Gebruik threads voor deployment compatibility
    app.run(host=host, port=port, debug=debug, threaded=True)
