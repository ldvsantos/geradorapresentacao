import os
import shutil
import subprocess
import sys
import tempfile
import time
import requests
import tarfile
from typing import Any
from pathlib import Path

def setup_quarto_linux():
    """Baixa e configura o Quarto CLI no Linux se não estiver presente."""
    if os.name != 'posix':
        return  # Apenas para Linux (Streamlit Cloud)

    if shutil.which('quarto'):
        return  # Já instalado ou no PATH

    # Configuração local
    QUARTO_VERSION = "1.6.40"
    # Instalar na home do usuário para ter permissão de escrita
    INSTALL_DIR = Path.home() / ".quarto_local"
    
    # A estrutura dentro do tar é quarto-{version}-linux-amd64/bin/quarto
    EXTRACTED_FOLDER_NAME = f"quarto-{QUARTO_VERSION}-linux-amd64"
    QUARTO_BIN_DIR = INSTALL_DIR / EXTRACTED_FOLDER_NAME / "bin"
    QUARTO_EXEC = QUARTO_BIN_DIR / "quarto"
    
    # Se já existir o executável no local esperado, apenas adiciona ao PATH e retorna
    if QUARTO_EXEC.exists():
        os.environ["PATH"] = str(QUARTO_BIN_DIR) + os.pathsep + os.environ["PATH"]
        return

    print(f"Instalando Quarto CLI v{QUARTO_VERSION} no Linux...")
    url = f"https://github.com/quarto-dev/quarto-cli/releases/download/v{QUARTO_VERSION}/quarto-{QUARTO_VERSION}-linux-amd64.tar.gz"
    
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            INSTALL_DIR.mkdir(parents=True, exist_ok=True)
            tar_path = INSTALL_DIR / "quarto.tar.gz"
            
            with open(tar_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=INSTALL_DIR)
            
            if QUARTO_EXEC.exists():
                os.environ["PATH"] = str(QUARTO_BIN_DIR) + os.pathsep + os.environ["PATH"]
                QUARTO_EXEC.chmod(0o755) # Garante permissão de execução
                print("Quarto configurado com sucesso.")
            else:
                print(f"Algo deu errado. executável não encontrado em {QUARTO_EXEC}")
            
            # Limpeza do tar
            if tar_path.exists():
                os.remove(tar_path)
        else:
            print(f"Erro ao baixar Quarto: Status {response.status_code}")
    except Exception as e:
        print(f"Erro na instalação do Quarto: {e}")

def copy_template(src: str, dst: str) -> None:
    ignore = shutil.ignore_patterns(
        ".quarto",
        "_site",
        "*.html",
        "*.pdf",
        "*.log",
    )
    shutil.copytree(src, dst, dirs_exist_ok=True, ignore=ignore)

def safe_rmtree(path: str, attempts: int = 6, delay_s: float = 0.25) -> None:
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
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        if last_exc:
            raise last_exc

def find_rendered_html(work_dir: str) -> str | None:
    candidates = [
        os.path.join(work_dir, "apresentacao.html"),
        os.path.join(work_dir, "_site", "apresentacao.html"),
        os.path.join(work_dir, "_site", "index.html"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    found_html: list[str] = []
    found_apresentacao: list[str] = []
    for root, dirs, files in os.walk(work_dir):
        dirs[:] = [d for d in dirs if d not in {".quarto", "node_modules"}]
        for filename in files:
            if filename.lower().endswith(".html"):
                full_path = os.path.join(root, filename)
                found_html.append(full_path)
                if filename.lower() == "apresentacao.html":
                    found_apresentacao.append(full_path)

    if found_apresentacao:
        found_apresentacao.sort(key=lambda p: p.count(os.sep))
        return found_apresentacao[0]

    if len(found_html) == 1:
        return found_html[0]

    for p in found_html:
        if p.lower().endswith(os.sep + "_site" + os.sep + "index.html"):
            return p

    return None

def build_qmd_content(titulo: str, subtitulo: str, instituto: str, conteudo: str) -> str:
    return f"""---
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

def render_quarto(
    *,
    titulo: str,
    subtitulo: str,
    instituto: str,
    conteudo: str,
    uploaded_files: list[Any] | None,
    output_dir: str | None = None
) -> tuple[bytes | None, str | None, dict[str, Any]]:
    # Se output_dir não for None, usamos ele como diretório de trabalho persistente (não temp)
    # Mas atenção: para streamlit usamos temp.
    # Vamos manter a lógica original: cria temp, renderiza, retorna bytes.
    # Mas se output_dir for fornecido (para build estático), copiamos o resultado para lá.
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_path, "template")

    if not os.path.isdir(template_path):
        return None, "Pasta 'template' não encontrada dentro do projeto.", {}

    tmpdirname = tempfile.mkdtemp(prefix="gerador_apresentacao_")
    try:
        work_dir = os.path.join(tmpdirname, "projeto")
        copy_template(template_path, work_dir)

        figuras_dir = os.path.join(work_dir, "Figuras")
        os.makedirs(figuras_dir, exist_ok=True)

        if uploaded_files:
            for uploaded_file in uploaded_files:
                # uploaded_file pode ser Streamlit UploadedFile ou arquivo normal se adaptarmos
                pass 
                # Nota: Na versao "util", uploaded_files pode ser quebrado se usarmos fora do Streamlit.
                # Para o script de build, vamos assumir que as imagens ja estao em template/Figuras se for o caso.

        qmd_content = build_qmd_content(titulo, subtitulo, instituto, conteudo)
        qmd_path = os.path.join(work_dir, "apresentacao.qmd")
        with open(qmd_path, "w", encoding="utf-8") as f:
            f.write(qmd_content)

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
        
        # Se for para salvar em output_dir, talvez não queiramos --embed-resources se for deployment com multiplos assets?
        # Mas o user pediu "como site". Single file é mais fácil. Vamos manter embed-resources.

        env = os.environ.copy()
        env["QUARTO_PYTHON"] = sys.executable

        try:
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                env=env,
            )
        except FileNotFoundError:
            return (
                None,
                "Comando 'quarto' não encontrado. Instale o Quarto CLI no servidor.",
                {"stdout": "", "stderr": "", "exit_code": None},
            )

        html_file = find_rendered_html(work_dir)
        debug: dict[str, Any] = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }

        if not html_file:
            return None, "Arquivo HTML não foi gerado.", debug
        
        if output_dir:
             # Para build script: copia o gerado para o destino
             os.makedirs(output_dir, exist_ok=True)
             shutil.copy(html_file, os.path.join(output_dir, "index.html"))
             
             # Copia ativos se necessário? Com embed-resources = true, não precisa.
             return None, None, debug

        with open(html_file, "rb") as f:
            html_bytes = f.read()

        return html_bytes, None, debug
    finally:
        safe_rmtree(tmpdirname)
