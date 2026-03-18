"""
Clau-AI — Servicio de generación de propuestas PDF
Lut Parra Consultoría de Liderazgo

POST /generar
  Body JSON: { datos de propuesta }
  Respuesta: { "pdf_base64": "...", "pdf_url": "https://...", "filename": "Propuesta_...pdf" }

GET /files/<file_id>
  Descarga el PDF generado por su UUID (disponible ~30 min)

GET /ping
  Respuesta: { "ok": true }  — para verificar que el servicio está activo
"""

import os
import base64
import tempfile
import traceback
import uuid
import time
import threading
from flask import Flask, request, jsonify, send_file, abort
from io import BytesIO
from generar_propuesta_v2 import generar_pdf, CATALOGO

app = Flask(__name__)

# ── In-memory PDF store ──────────────────────────────────────────────────────
# { file_id: { 'data': bytes, 'filename': str, 'expires': float } }
_pdf_store: dict = {}
_store_lock = threading.Lock()
PDF_TTL_SECONDS = 1800  # 30 minutes


def _cleanup_expired():
    """Remove PDFs that have passed their TTL."""
    now = time.time()
    with _store_lock:
        expired = [fid for fid, v in _pdf_store.items() if v['expires'] < now]
        for fid in expired:
            del _pdf_store[fid]


def _store_pdf(pdf_bytes: bytes, filename: str) -> str:
    """Store PDF bytes and return the file_id."""
    _cleanup_expired()
    file_id = str(uuid.uuid4())
    with _store_lock:
        _pdf_store[file_id] = {
            'data':     pdf_bytes,
            'filename': filename,
            'expires':  time.time() + PDF_TTL_SECONDS,
        }
    return file_id


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'ok': True, 'programas': list(CATALOGO.keys())})


@app.route('/files/<file_id>', methods=['GET'])
def serve_file(file_id):
    """Serve a previously-generated PDF by its UUID."""
    _cleanup_expired()
    with _store_lock:
        entry = _pdf_store.get(file_id)
    if not entry:
        abort(404)
    return send_file(
        BytesIO(entry['data']),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=entry['filename'],
    )


@app.route('/generar', methods=['POST'])
def generar():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'error': 'No se recibieron datos JSON'}), 400

        # Validar campos obligatorios
        required = ['programa_key', 'empresa', 'contacto', 'participantes',
                    'formato', 'precio_total', 'forma_pago']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({'error': f'Faltan campos: {", ".join(missing)}'}), 400

        # Construir estructura de datos para generar_pdf()
        contacto_parts = data['contacto'].split(',', 1)
        contacto_nombre = contacto_parts[0].strip()
        contacto_puesto = contacto_parts[1].strip() if len(contacto_parts) > 1 else ''

        propuesta_data = {
            'programa_key':    data['programa_key'],
            'duracion':        data.get('duracion'),
            'formato':         data['formato'],
            'cliente': {
                'contacto': contacto_nombre,
                'area':     contacto_puesto or data.get('area', ''),
                'empresa':  data['empresa'],
            },
            'contexto_cliente': data.get('contexto_cliente', ''),
            'inversion': {
                'sesiones':       data.get('sesiones', '1 sesión'),
                'participantes':  f"{data['participantes']} participantes",
                'total':          data['precio_total'],
                'total_iva':      data['precio_total'] + ' + I.V.A.',
                'modalidad_pago': data['forma_pago'],
                'notas':          data.get('notas', ''),
            },
            'siguiente_paso': [
                'Confirmar fecha de impartición',
                'Firmar carta de acuerdo',
                'Agendar sesión de coordinación',
            ],
            'fecha': data.get('fecha', _fecha_hoy()),
        }

        # Generar PDF en archivo temporal
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name

        generar_pdf(propuesta_data, tmp_path)

        # Leer bytes del PDF
        with open(tmp_path, 'rb') as f:
            pdf_bytes = f.read()
        os.unlink(tmp_path)

        # Nombre del archivo
        empresa_slug = data['empresa'].replace(' ', '_')[:30]
        programa_slug = data['programa_key']
        filename = f'Propuesta_{programa_slug}_{empresa_slug}.pdf'

        # Codificar en base64
        pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Guardar en memoria y generar URL pública
        file_id = _store_pdf(pdf_bytes, filename)
        base_url = os.environ.get('BASE_URL', 'https://clau-propuestas.onrender.com')
        pdf_url = f'{base_url}/files/{file_id}'

        return jsonify({
            'ok':         True,
            'pdf_base64': pdf_b64,
            'pdf_url':    pdf_url,
            'filename':   filename,
            'size_kb':    round(len(pdf_bytes) / 1024, 1),
        })

    except KeyError as e:
        return jsonify({'error': f'Programa no encontrado en el catálogo: {e}'}), 400
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def _fecha_hoy():
    from datetime import date
    meses = ['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']
    d = date.today()
    return f'{d.day} de {meses[d.month - 1]} de {d.year}'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
