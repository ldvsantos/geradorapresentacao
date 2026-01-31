import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime

import streamlit as st


def _copy_template(src: str, dst: str) -> None:
    ignore = shutil.ignore_patterns(
        ".quarto",
        "_site",
        "*.html",
        "*.pdf",
        "*.log",
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


st.set_page_config(page_title="Gerador de Apresentação TCC", layout="wide")

st.title("🎓 Gerador de Apresentação TCC")
st.caption("Crie sua apresentação baseada no template oficial do IFS. Código gratuito e controle total do projeto.")

with st.sidebar:
    st.header("📋 Slide de Título")
    titulo = st.text_area(
        "Título",
        "DESENVOLVIMENTO DE UM PROTÓTIPO DE SISTEMA PARA APOIO ÀS ATIVIDADES PSICOPEDAGÓGICAS NO INSTITUTO FEDERAL DE SERGIPE",
        height=120,
    )
    subtitulo = st.text_area(
        "Subtítulo (use <br> para quebra de linha)",
        "Discente: Seu Nome<br>Orientador: Nome do Orientador<br>Coorientadora: Nome da Coorientadora",
        height=100,
    )
    instituto = st.text_input("Instituto", "Instituto Federal de Sergipe")

st.subheader("📝 Conteúdo dos Slides")
st.markdown(
    """
**Dicas rápidas**
- Use `## Título do Slide` para criar um novo slide.
- Use `- Item` para listas.
- Para imagens enviadas aqui, use `![](Figuras/nome_arquivo.png)`.
"""
)

conteudo_default = """## Contextualização do Estudo

- Psicopedagogia nas instituições escolares
- Educação inclusiva 
- Atendimento psicopedagógico no IFS
- Necessidade de organização das informações

## Objetivos

### Objetivo Geral
Desenvolver um protótipo de sistema para...

### Objetivos Específicos
- Mapear processos
- Desenvolver sistema
- Validar protótipo

## Metodologia

Estudo de caso com abordagem qualitativa...

## Considerações Finais

- Principais resultados
- Contribuições do trabalho
- Trabalhos futuros
"""

conteudo = st.text_area("Editor (Markdown)", value=conteudo_default, height=360)

st.subheader("🖼️ Imagens")
uploaded_files = st.file_uploader(
    "Envie imagens (PNG/JPG/JPEG/GIF)",
    accept_multiple_files=True,
    type=["png", "jpg", "jpeg", "gif"],
)

if uploaded_files:
    st.write("Copie e cole no texto:")
    for up_file in uploaded_files:
        st.code(f"![](Figuras/{up_file.name})", language="markdown")

if st.button("🚀 Gerar Apresentação (HTML)", type="primary"):
    base_path = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_path, "template")

    if not os.path.isdir(template_path):
        st.error("Pasta 'template' não encontrada dentro do projeto.")
        st.stop()

    tmpdirname = tempfile.mkdtemp(prefix="gerador_apresentacao_")
    try:
        work_dir = os.path.join(tmpdirname, "projeto")
        _copy_template(template_path, work_dir)

        figuras_dir = os.path.join(work_dir, "Figuras")
        os.makedirs(figuras_dir, exist_ok=True)

        if uploaded_files:
            for uploaded_file in uploaded_files:
                out_path = os.path.join(figuras_dir, uploaded_file.name)
                with open(out_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

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

        cmd = [
            "quarto",
            "render",
            "apresentacao.qmd",
            "--to",
            "revealjs",
            "--embed-resources",
        ]

        with st.spinner("Renderizando com Quarto..."):
            try:
                result = subprocess.run(
                    cmd,
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                )
            except FileNotFoundError:
                st.error("Comando 'quarto' não encontrado. Instale o Quarto CLI ou configure no servidor.")
                st.stop()

        output_file = _find_rendered_html(work_dir)
        if not output_file:
            st.error("Arquivo HTML não foi gerado.")
            with st.expander("Ver detalhes técnicos"):
                st.code(f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n\nExitCode: {result.returncode}")
            st.stop()

        with open(output_file, "rb") as f:
            html_bytes = f.read()

        nome = f"minha_apresentacao_tcc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        st.success("Apresentação gerada com sucesso!")
        st.download_button(
            "⬇️ Baixar HTML",
            data=html_bytes,
            file_name=nome,
            mime="text/html",
        )

    finally:
        _safe_rmtree(tmpdirname)
