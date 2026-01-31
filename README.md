# Gerador de Apresentação Online (TCC/IFS)

Sistema para gerar e publicar apresentações (Reveal.js via Quarto) a partir de um editor simples. Ideal para TCC/defesas e apresentações institucionais seguindo identidade visual (IFS).

Repositório: https://github.com/ldvsantos/geradorapresentacao

## O que ele faz

- Editor (Markdown) para escrever os slides
- Upload de imagens e uso via `![](Figuras/arquivo.png)`
- Geração de um HTML único com recursos embutidos (`--embed-resources`), fácil de enviar/abrir
- Template Quarto/Revel.js com estilos do IFS

## Modos de execução

Você pode rodar de duas formas:

### 1) Streamlit (recomendado para “online”)

Interface pronta para publicar em servidores (Render/Railway/Fly) via Docker.

Pré-requisitos:
- Python 3.10+
- Quarto CLI (se for rodar sem Docker): https://quarto.org/docs/get-started/

Rodar local:

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Acesse: http://localhost:8501

### 2) Flask (interface HTML/CSS/JS)

Útil para usar a interface web clássica em `templates/`.

Pré-requisitos:
- Python 3.10+
- Quarto CLI: https://quarto.org/docs/get-started/

Rodar local:

```powershell
pip install -r requirements.txt
python app.py
```

Acesse: http://localhost:5000

## Deploy em nuvem (Docker)

Este projeto já tem um `Dockerfile` que instala o Quarto dentro da imagem e sobe o Streamlit na porta definida por `$PORT`.

Build e execução local via Docker:

```powershell
docker build -t geradorapresentacao .
docker run --rm -p 8501:8501 -e PORT=8501 geradorapresentacao
```

Depois publique em Render/Railway/Fly apontando para o `Dockerfile`.

## Estrutura

```
.
├── streamlit_app.py      # UI Streamlit (online)
├── app.py                # Backend Flask (alternativo)
├── template/             # Template Quarto (Reveal.js)
├── templates/            # UI HTML (Flask)
├── static/               # CSS/JS (Flask)
├── Dockerfile            # Deploy (Quarto + Streamlit)
└── requirements.txt
```

## Licença

Uso educacional e institucional.
