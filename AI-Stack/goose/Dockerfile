FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    git \
    curl \
    jq \
    vim \
    nano \
    && rm -rf /var/lib/apt/lists/*

# Installation de Goose
RUN pip install --no-cache-dir goose-ai

# Installation d'outils supplémentaires pour Goose
RUN pip install --no-cache-dir \
    httpx \
    pyyaml \
    rich \
    click

# Créer les répertoires de travail
RUN mkdir -p /workspace /root/.config/goose

# Copier la configuration
COPY goose-config.yaml /root/.config/goose/config.yaml

# Script d'entrée
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exposer le workspace comme volume
VOLUME ["/workspace"]

WORKDIR /workspace

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
