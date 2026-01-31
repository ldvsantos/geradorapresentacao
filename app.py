from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
import os
import tempfile
import subprocess
import shutil
import time
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB para upload

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _copy_template(src: str, dst: str) -> None:
    ignore = shutil.ignore_patterns(
        '.quarto',
        '_site',
        '*.html',
        '*.pdf',
        '*.log',
    )
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)


def _safe_rmtree(path: str, attempts: int = 6, delay_s: float = 0.25) -> None:
    if not os.path.exists(path):
        return
    last_exc: Exception | None = None
    for _ in range(attempts):
        try:
            shutil.rmtree(path)
            return
        except Exception as exc:
            last_exc = exc
            time.sleep(delay_s)
    # Em Windows, arquivos podem ficar em uso (lock). Não derrubar o servidor por isso.
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        if last_exc:
            raise last_exc


def _find_rendered_html(work_dir: str) -> str | None:
    candidates = [
        os.path.join(work_dir, "apresentacao.html"),
        os.path.join(work_dir, "_site", "apresentacao.html"),
        os.path.join(work_dir, "_site", "index.html"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    # Fallback: procurar recursivamente (Quarto pode colocar em subpastas dependendo do project/output-dir)
    found_html: list[str] = []
    found_apresentacao: list[str] = []
    for root, dirs, files in os.walk(work_dir):
        # evita passear por caches muito grandes se existirem
        dirs[:] = [d for d in dirs if d not in {".quarto", "node_modules"}]
        for filename in files:
            if filename.lower().endswith(".html"):
                full_path = os.path.join(root, filename)
                found_html.append(full_path)
                if filename.lower() == "apresentacao.html":
                    found_apresentacao.append(full_path)

    if found_apresentacao:
        # preferir o mais "raso" (mais próximo do work_dir)
        found_apresentacao.sort(key=lambda p: p.count(os.sep))
        return found_apresentacao[0]

    if len(found_html) == 1:
        return found_html[0]

    # Se houver vários, preferir index.html dentro de _site
    for p in found_html:
        if p.lower().endswith(os.sep + "_site" + os.sep + "index.html"):
            return p
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar', methods=['POST'])
def gerar_apresentacao():
    try:
        # Pegar dados do formulário
        titulo = request.form.get('titulo', 'Título da Apresentação')
        subtitulo = request.form.get('subtitulo', 'Autor')
        instituto = request.form.get('instituto', 'Instituto Federal de Sergipe')
        conteudo = request.form.get('conteudo', '')
        
        # Criar diretório temporário (não usar TemporaryDirectory aqui por causa de locks do Quarto no Windows)
        tmpdirname = tempfile.mkdtemp(prefix="gerador_apresentacao_")
        try:
            # Copiar template
            base_path = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(base_path, "template")
            work_dir = os.path.join(tmpdirname, "projeto")
            
            if os.path.exists(template_path):
                _copy_template(template_path, work_dir)
            else:
                return jsonify({'erro': 'Template não encontrado'}), 500
            
            # Criar pasta de imagens
            figuras_dir = os.path.join(work_dir, "Figuras")
            os.makedirs(figuras_dir, exist_ok=True)
            
            # Salvar imagens enviadas
            if 'imagens' in request.files:
                imagens = request.files.getlist('imagens')
                for imagem in imagens:
                    if imagem and allowed_file(imagem.filename):
                        filename = secure_filename(imagem.filename)
                        imagem.save(os.path.join(figuras_dir, filename))
            
            # Criar arquivo .qmd
            qmd_content = f"""---
title: "{titulo}"
subtitle: "{subtitulo}"
institute: "{instituto}"
date: today
date-format: "D [de] MMMM [de] YYYY"
lang: pt-BR
title-slide-attributes:
  class: title-slide
format:
  revealjs:
    theme: [simple, assets/ufs.scss]
    css: assets/custom.css
    logo: assets/logo_IFS.png
    footer: "IFS | Apresentação do TCC"
    slide-number: true
    controls: true
    width: 1280
    height: 720
    transition: slide
    background-transition: fade
    preview-links: auto
---

{conteudo}
"""
            
            qmd_path = os.path.join(work_dir, "apresentacao.qmd")
            with open(qmd_path, "w", encoding="utf-8") as f:
                f.write(qmd_content)
            
            # Executar Quarto
            # Observação: o template original é um projeto Quarto com output-dir: _site.
            # Tentamos sobrescrever para gerar na raiz, mas também tratamos o caso de sair em _site/.
            cmd = [
                "quarto",
                "render",
                "apresentacao.qmd",
                "--to",
                "revealjs",
                "--embed-resources",
                "--output-dir",
                ".",
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    check=False
                )
                
                # Verificar se o arquivo foi gerado (pode ir para _site/ dependendo do _quarto.yml)
                output_file = _find_rendered_html(work_dir)

                if not output_file:
                    erro_detalhado = (
                        f"Erro do Quarto:\n\nSTDOUT:\n{result.stdout}"
                        f"\n\nSTDERR:\n{result.stderr}"
                        f"\n\nCódigo de saída: {result.returncode}"
                    )
                    site_dir = os.path.join(work_dir, "_site")
                    arquivos_site = os.listdir(site_dir) if os.path.isdir(site_dir) else []
                    return jsonify({
                        'erro': 'Arquivo HTML não foi gerado',
                        'detalhes': erro_detalhado,
                        'arquivos_gerados': os.listdir(work_dir),
                        'arquivos_site': arquivos_site,
                    }), 500
                    
            except FileNotFoundError:
                return jsonify({
                    'erro': 'Comando "quarto" não encontrado',
                    'detalhes': 'Certifique-se de que o Quarto CLI está instalado e no PATH do sistema. Baixe em: https://quarto.org/docs/get-started/'
                }), 500
            
            # Copiar para pasta temporária para download
            download_path = os.path.join(
                tempfile.gettempdir(),
                f"apresentacao_{datetime.now().strftime('%Y%m%d%H%M%S')}.html",
            )
            shutil.copy2(output_file, download_path)
            
            return jsonify({'sucesso': True, 'arquivo': os.path.basename(download_path)})
        finally:
            _safe_rmtree(tmpdirname)
            
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    try:
        file_path = os.path.join(tempfile.gettempdir(), filename)
        if os.path.exists(file_path):
            response = send_file(file_path, as_attachment=True, download_name='minha_apresentacao_tcc.html')
            # Agendar remoção do arquivo após download
            @response.call_on_close
            def cleanup():
                try:
                    os.remove(file_path)
                except:
                    pass
            return response
        else:
            return "Arquivo não encontrado", 404
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # Evita reinícios automáticos que podem derrubar conexões no Windows.
    app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
