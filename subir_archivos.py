import os, urllib.parse, sys
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", 8500))
CLAVE = "Armada2026"

ESTILO = """<style>
body{font-family:'Segoe UI',sans-serif;margin:0;padding:20px;background:#f0f3f5;color:#1c2833;transition: background 0.5s;}
.container{max-width:650px;margin:20px auto;background:white;padding:30px;border-radius:12px;box-shadow:0 5px 20px rgba(0,26,51,0.15);border-top:8px solid #002147;position:relative;}
.header-zone{text-align:center;margin-bottom:25px}.logo-armada{max-width:140px;height:auto;margin-bottom:10px;border-radius:4px}
h2{color:#002147;margin:5px 0;text-transform:uppercase;font-size:22px}.sub-title{color:#7f8c8d;font-size:14px;margin-bottom:20px}
.path-box{background:#f4f6f7;padding:10px 15px;border-radius:6px;font-size:14px;border-left:4px solid #d4af37;margin-bottom:20px}
.upload-box{background:#f9fbfd;padding:20px;border-radius:8px;margin-bottom:25px;border:1px solid #d6e4f0}
.upload-box h3{margin-top:0;color:#002147;font-size:16px;border-bottom:2px solid #002147;padding-bottom:5px}
label{font-size:13px;font-weight:bold;color:#34495e;display:block;margin-top:10px}
select,input[type='file']{width:100%;margin:6px 0 15px 0;padding:10px;box-sizing:border-box;border-radius:6px;border:1px solid #ccc}
button[type='submit']{width:100%;background:#002147;color:white;border:2px solid #002147;padding:12px;font-size:15px;border-radius:6px;cursor:pointer;font-weight:bold;transition:all 0.3s}
button[type='submit']:hover{background:#d4af37;border-color:#d4af37;color:#002147}
.file-section-title{color:#002147;font-size:16px;margin-top:25px}
ul{list-style-type:none;padding:0}li{padding:12px 15px;border-bottom:1px solid #eef2f5;display:flex;align-items:center}li:hover{background:#f8f9fa}
a{text-decoration:none;color:#002147;font-weight:500}a:hover{text-decoration:underline;color:#d4af37}
.back-btn{display:inline-block;margin-bottom:15px;background:#7f8c8d;color:white;padding:6px 12px;border-radius:4px;font-size:13px;text-decoration:none}
.status-badge { display: block; text-align: center; font-weight: bold; padding: 10px; border-radius: 6px; margin-bottom: 20px; font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px; }
.online { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.offline { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; animation: parpadeo 1.5s infinite; }
.overlay-offline { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(240,243,245,0.7); border-radius: 12px; display: none; z-index: 999; }
@keyframes parpadeo { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>"""

SCRIPT_JS = """<script>
function pedirClave(e,a){e.preventDefault();var c=prompt('🔐 Introduzca la Clave de Autorizacion para descargar:');c&&(window.location.href=a.href+'?token='+encodeURIComponent(c))}

setInterval(function() {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/ping-status', true);
    xhr.timeout = 1800;
    xhr.onload = function() {
        if (xhr.status === 200) {
            document.getElementById('badge').className = 'status-badge online';
            document.getElementById('badge').innerHTML = '⚓ SERVIDOR EN LA NUBE ONLINE - TRANSFERENCIA LISTA';
            document.getElementById('blocker').style.display = 'none';
        } else { ponerOffline(); }
    };
    xhr.onerror = function() { ponerOffline(); };
    xhr.ontimeout = function() { ponerOffline(); };
    xhr.send();
}, 2000);

function ponerOffline() {
    document.getElementById('badge').className = 'status-badge offline';
    document.getElementById('badge').innerHTML = '⚠️ SERVIDOR DESCONECTADO';
    document.getElementById('blocker').style.display = 'block';
}
</script>"""

class HandlerArmada(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        path = self.translate_path(parsed.path)
        
        if parsed.path == '/ping-status':
            try:
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.send_header('Content-Length', '2')
                self.end_headers()
                self.wfile.write(b"OK")
            except Exception:
                pass
            return
            
        if os.path.isfile(path):
            if parsed.path.endswith('dn5.jpg'):
                super().do_GET()
                return
            if params.get('token', [''])[0] != CLAVE:
                self.send_response(403)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write("<h3>⚠️ ACCESO RESTRINGIDO - Clave incorrecta</h3><br><a href='/'>Volver</a>".encode('utf-8'))
                return
            super().do_GET()
            return
            
        if os.path.isdir(path):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            try: items_dir = os.listdir(path)
            except: items_dir = []
            items_dir.sort(key=lambda a: a.lower())
            
            IGNORAR = ['venv', '.venv', '.git', 'subir_archivos.py', 'arrancar.bat', 'diagnostico.bat', 'liberar.bat', 'requirements.txt']
            
            options = '<option value=".">[Carpeta Actual]</option>'
            for n in items_dir:
                if os.path.isdir(os.path.join(path, n)) and n not in IGNORAR and not n.startswith('.'):
                    options += f'<option value="{n}">{n}/</option>'
            files_html = ""
            for n in items_dir:
                if n in IGNORAR or n.startswith('.'): continue
                link = urllib.parse.quote(n)
                if os.path.isdir(os.path.join(path, n)):
                    files_html += f"<li>📁 <a href='{link}/'>{n}/</a></li>"
                else:
                    files_html += f"<li>📄 <a href='{link}' onclick='pedirClave(event, this)'>{n}</a></li>"
            back = f"<a class='back-btn' href='../'>⬅ Directorio Superior</a>" if parsed.path != '/' else ''
            
            html = f"""<html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>QUINTO DISTRITO NAVAL SANTA CRUZ</title>{ESTILO}{SCRIPT_JS}</head><body><div class='container'><div id='blocker' class='overlay-offline'></div><div class='header-zone'><img src='/dn5.jpg' alt='Insignia' class='logo-armada' onerror='this.style.display="none";'><h2>QUINTO DISTRITO NAVAL SANTA CRUZ</h2><div class='sub-title'>Sistema de Transferencia de Archivos</div></div><div id='badge' class='status-badge online'>⚓ SERVIDOR EN LA NUBE ONLINE - TRANSFERENCIA LISTA</div><div class='path-box'><strong>Directorio:</strong> <code>{parsed.path}</code></div>{back}<div class='upload-box'><h3>⚓ Cargar Documento</h3><form method='POST' action='/upload-target' enctype='multipart/form-data'><input type='hidden' name='current_dir' value='{parsed.path}'><label>Destino:</label><select name='dest_folder'>{options}</select><label>Archivo:</label><input type='file' name='file' required><br><button type='submit'>CARGAR DOCUMENTO</button></form></div><div class='file-section-title'>Contenido de la Carpeta</div><ul>{files_html if files_html else '<li><i>Vacio</i></li>'}</ul></div></body></html>"""
            self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        print("\n" + "="*40)
        print("📥 RECIBIENDO PETICION POST (SUBIDA DE ARCHIVO)...")
        print("="*40)
        
        if self.path != '/upload-target': 
            print(f"⚠️ Ruta no reconocida en POST: {self.path}")
            return
            
        try:
            content_type = self.headers.get('Content-Type', '')
            if 'boundary=' not in content_type:
                print("❌ ERROR: El formulario no envió el formato multipart correcto.")
                self.send_response(400); self.end_headers(); return
                
            boundary = b'--' + content_type.split('boundary=')[-1].encode()
            content_length = int(self.headers.get('Content-Length', 0))
            body_data = self.rfile.read(content_length)
            parts = body_data.split(boundary)
            
            cd, dest, fname, fdata = '/', '.', '', b''
            for p in parts:
                if b'Content-Disposition' in p:
                    h, data = p.split(b'\r\n\r\n', 1)
                    if data.endswith(b'\r\n'): data = data[:-2]
                    if data.endswith(b'--\r\n'): data = data[:-4]
                    h_str = h.decode('utf-8', errors='ignore')
                    if 'name="current_dir"' in h_str: cd = data.decode('utf-8').strip()
                    elif 'name="dest_folder"' in h_str: dest = data.decode('utf-8').strip()
                    elif 'name="file"' in h_str and 'filename=' in h_str:
                        fdata = data
                        for line in h_str.split('\r\n'):
                            if 'filename=' in line: fname = os.path.basename(line.split('filename=')[-1].strip('"'))
            
            if fname:
                file_dest_path = os.path.join(os.path.normpath(os.path.join(self.translate_path(cd), dest)), fname)
                with open(file_dest_path, 'wb') as f:
                    f.write(fdata)
                
                print(f"📁 Archivo guardado localmente en el servidor: {fname}")
                
                # Intentar subida a MEGA
                email = os.environ.get("MEGA_EMAIL")
                password = os.environ.get("MEGA_PASSWORD")
                
                print(f"EMAIL DETECTADO: {email if email else '❌ NO CONFIGURADO'}")
                print(f"PASSWORD DETECTADA: {'YES (*****)' if password else '❌ NO CONFIGURADA'}")
                
                if email and password:
                    try:
                        from mega import Mega
                        print("Iniciando sesión en MEGA...")
                        mega_api = Mega()
                        m_instance = mega_api.login(email.strip(), password.strip())
                        print(f"Subiendo {fname} a la nube de MEGA...")
                        m_instance.upload(file_dest_path)
                        print(f"✅ ¡{fname} SUBIDO EXITOSAMENTE A MEGA!")
                    except Exception as err:
                        print(f"❌ ERROR AL CONECTAR/SUBIR A MEGA: {err}")
                else:
                    print("⚠️ ALERTA: Faltan variables de entorno MEGA_EMAIL o MEGA_PASSWORD.")
            else:
                print("⚠️ No se detectó ningún nombre de archivo en los datos enviados.")
                
            print("="*40 + "\n")
            self.send_response(303); self.send_header('Location', cd); self.end_headers()
        except Exception as e:
            print(f"❌ Error crítico en procesar POST: {e}")
            self.send_response(400); self.end_headers()

if __name__ == '__main__':
    print(f"Iniciando Servidor del DN-5 en el puerto {PORT}...")
    server = HTTPServer(('0.0.0.0', PORT), HandlerArmada)
    server.serve_forever()
