import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from hashlib import sha256
from typing import Any

import streamlit as st
import streamlit.components.v1 as components


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


def _build_qmd_content(titulo: str, subtitulo: str, instituto: str, conteudo: str) -> str:
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


def _render_quarto(
    *,
    titulo: str,
    subtitulo: str,
    instituto: str,
    conteudo: str,
    uploaded_files: list[Any] | None,
) -> tuple[bytes | None, str | None, dict[str, Any]]:
    base_path = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_path, "template")

    if not os.path.isdir(template_path):
        return None, "Pasta 'template' não encontrada dentro do projeto.", {}

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

        qmd_content = _build_qmd_content(titulo, subtitulo, instituto, conteudo)
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

        output_file = _find_rendered_html(work_dir)
        debug: dict[str, Any] = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }

        if not output_file:
            return None, "Arquivo HTML não foi gerado.", debug

        with open(output_file, "rb") as f:
            html_bytes = f.read()

        return html_bytes, None, debug
    finally:
        _safe_rmtree(tmpdirname)


def _inject_file_uploader_pt_br_styles() -> None:
    st.markdown(
        """
<style>
    /*
        Streamlit não tem i18n nativo para o file_uploader.
        Então escondemos textos padrão e substituímos o label do botão por CSS.
        (Seletores duplicados para cobrir variações entre versões.)
    */

    /* Esconde instruções/limites (normalmente em inglês) */
    div[data-testid="stFileUploaderDropzoneInstructions"],
    div[data-testid="stFileUploader"] div[data-testid="stFileUploaderDropzoneInstructions"],
    .stFileUploader div[data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    div[data-testid="stFileUploaderDropzone"] small,
    div[data-testid="stFileUploader"] div[data-testid="stFileUploaderDropzone"] small,
    .stFileUploader div[data-testid="stFileUploaderDropzone"] small {
        display: none !important;
    }

    /* Troca o texto do botão (geralmente 'Browse files') */
    div[data-testid="stFileUploaderDropzone"] button,
    div[data-testid="stFileUploader"] div[data-testid="stFileUploaderDropzone"] button,
    .stFileUploader div[data-testid="stFileUploaderDropzone"] button {
        font-size: 0 !important;
        text-shadow: none !important;
    }

    div[data-testid="stFileUploaderDropzone"] button *,
    div[data-testid="stFileUploader"] div[data-testid="stFileUploaderDropzone"] button *,
    .stFileUploader div[data-testid="stFileUploaderDropzone"] button * {
        display: none !important;
    }

    div[data-testid="stFileUploaderDropzone"] button::after,
    div[data-testid="stFileUploader"] div[data-testid="stFileUploaderDropzone"] button::after,
    .stFileUploader div[data-testid="stFileUploaderDropzone"] button::after {
        content: "Selecionar arquivos";
        display: inline-block;
        color: inherit;
        font-size: 0.95rem;
        font-weight: 600;
    }
</style>
""",
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Gerador de Apresentação TCC", layout="wide")

st.markdown(
        """
<style>
    div[data-testid="stToolbar"] { visibility: hidden; height: 0; }
    div[data-testid="stDecoration"] { visibility: hidden; height: 0; }
</style>
""",
        unsafe_allow_html=True,
)

st.title("🎓 Gerador de Apresentação TCC")
st.caption("Crie sua apresentação baseada no template oficial do IFS. Código gratuito e controle total do projeto.")

with st.expander("📋 Slide de Título", expanded=True):
    col_titulo, col_instituto = st.columns([0.72, 0.28], gap="medium")
    with col_titulo:
        titulo = st.text_area(
            "Título",
            "DESENVOLVIMENTO DE UM PROTÓTIPO DE SISTEMA PARA APOIO ÀS ATIVIDADES PSICOPEDAGÓGICAS NO INSTITUTO FEDERAL DE SERGIPE",
            height=80,
            key="titulo",
        )
    with col_instituto:
        instituto = st.text_input(
            "Instituto",
            "Instituto Federal de Sergipe",
            key="instituto",
        )

    subtitulo = st.text_area(
        "Subtítulo (use <br> para quebra de linha)",
        "Discente: Seu Nome<br>Orientador: Nome do Orientador<br>Coorientadora: Nome da Coorientadora",
        height=80,
        key="subtitulo",
    )

st.subheader("📝 Conteúdo dos Slides")

with st.expander("💡 Dicas Rápidas de Formatação", expanded=False):
    st.markdown(
        """
        - **Novos Slides:** Use `## Título do Slide` para iniciar um slide.
        - **Listas:** Use `- Item` para marcadores ou `1. Item` para listas numeradas.
        - **Negrito/Itálico:** Use `**negrito**` ou `*itálico*`.
        - **Citações:** Use `> Texto citado` para criar um bloco de destaque.
        - **Código:** Use crases para `código inline` ou triplas crases para blocos de código.
        - **Imagens:** Envie abaixo e use `![](Figuras/arquivo.png)`.
        - **Colunas:** O Quarto permite colunas, mas o Markdown simples é sequencial.
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

conteudo = st.text_area("Editor (Markdown)", value=conteudo_default, height=600)

st.subheader("🖼️ Imagens")
_inject_file_uploader_pt_br_styles()
st.caption("Arraste e solte as imagens aqui ou clique em 'Selecionar arquivos'.")

uploaded_files = st.file_uploader(
    "Enviar imagens",
    accept_multiple_files=True,
    type=["png", "jpg", "jpeg", "gif"],
    label_visibility="collapsed",
)

if uploaded_files:
    st.write("Copie e cole no texto:")
    for up_file in uploaded_files:
        st.code(f"![](Figuras/{up_file.name})", language="markdown")

st.divider()

# --- Preview Section ---
st.subheader("👀 Pré-visualização")
st.caption("Veja como está ficando sua apresentação antes de baixar.")

auto = st.checkbox(
    "Atualizar automaticamente ao digitar",
    value=False,
    help="Atualiza o preview sempre que o conteúdo mudar (pode ser lento).",
)

chave = sha256(
    (titulo + "\n" + subtitulo + "\n" + instituto + "\n" + conteudo).encode("utf-8")
).hexdigest()

if "preview_quarto" not in st.session_state:
    st.session_state["preview_quarto"] = {"hash": "", "html": "", "error": "", "debug": {}}

preview_state: dict[str, Any] = st.session_state["preview_quarto"]

# Renderiza se clicou ou se está no modo auto e mudou
col_btn_preview, col_btn_download = st.columns([0.3, 0.7], gap="medium")

with col_btn_preview:
    clicked_preview = st.button("🔄 Atualizar Preview", type="secondary", use_container_width=True)

should_render = clicked_preview or (auto and preview_state.get("hash") != chave)

if should_render:
    with st.spinner("Gerando preview..."):
        html_bytes, err, preview_debug = _render_quarto(
            titulo=titulo,
            subtitulo=subtitulo,
            instituto=instituto,
            conteudo=conteudo,
            uploaded_files=uploaded_files,
        )

    preview_state["hash"] = chave
    preview_state["debug"] = preview_debug
    preview_state["error"] = err or ""
    preview_state["html"] = html_bytes.decode("utf-8", errors="replace") if html_bytes else ""

if preview_state.get("error"):
    st.error(preview_state.get("error", ""))
    with st.expander("Ver detalhes técnicos"):
        debug: dict[str, Any] = preview_state.get("debug") or {}
        st.code(
            f"STDOUT:\n{debug.get('stdout','')}\n\nSTDERR:\n{debug.get('stderr','')}\n\nExitCode: {debug.get('exit_code')}"
        )

# Mostra o preview se existir HTML
if preview_state.get("html"):
    st.markdown("---")
    components.html(str(preview_state.get("html", "")), height=720, scrolling=False)
    st.caption("Dica: Clique no slide e use as setas ← → ou Espaço para navegar.")
else:
    st.info("Clique em 'Atualizar Preview' para ver os slides.")


st.divider()

# --- Download Section ---
st.subheader("🚀 Finalizar e Baixar")

if st.button("💾 Gerar HTML Final para Download", type="primary"):
    with st.spinner("Gerando versão final..."):
        html_bytes, err, render_debug = _render_quarto(
            titulo=titulo,
            subtitulo=subtitulo,
            instituto=instituto,
            conteudo=conteudo,
            uploaded_files=uploaded_files,
        )

    if err:
        st.error(err)
        with st.expander("Ver detalhes técnicos"):
            st.code(
                f"STDOUT:\n{render_debug.get('stdout','')}\n\nSTDERR:\n{render_debug.get('stderr','')}\n\nExitCode: {render_debug.get('exit_code')}"
            )
    else:
        assert html_bytes is not None
        nome = f"apresentacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        st.success("Apresentação gerada com sucesso!")
        st.download_button(
            "⬇️ Baixar HTML",
            data=html_bytes,
            file_name=nome,
            mime="text/html",
        )
