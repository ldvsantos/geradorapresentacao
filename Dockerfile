# Deploy em nuvem (Linux) com Quarto + Streamlit
FROM python:3.12-slim

ARG QUARTO_VERSION=1.6.40

# Dependências do sistema
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl ca-certificates tar \
  && rm -rf /var/lib/apt/lists/*

# Instala Quarto CLI
RUN curl -L -o /tmp/quarto.tar.gz \
    "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz" \
  && tar -xzf /tmp/quarto.tar.gz -C /opt \
  && ln -s "/opt/quarto-${QUARTO_VERSION}/bin/quarto" /usr/local/bin/quarto \
  && rm /tmp/quarto.tar.gz

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8501

# Render/Fly/Railway costumam fornecer $PORT
CMD ["sh", "-c", "streamlit run streamlit_app.py --server.address=0.0.0.0 --server.port=${PORT:-8501}"]
