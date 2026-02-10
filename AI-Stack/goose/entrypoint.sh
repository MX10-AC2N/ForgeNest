#!/bin/bash
set -e

echo "🦆 Goose Agent IA - Prêt à travailler"
echo ""
echo "Configuration:"
echo "  Modèle: ${GOOSE_MODEL:-groq/llama-3.3-70b-versatile}"
echo "  Provider: ${GOOSE_PROVIDER:-openai}"
echo "  Workspace: ${WORKSPACE_DIR:-/workspace}"
echo ""
echo "Commandes disponibles:"
echo "  goose session           - Démarrer une session interactive"
echo "  goose \"votre tâche\"     - Exécuter une tâche"
echo "  goose --help            - Voir toutes les options"
echo ""
echo "Exemples:"
echo "  goose \"Create a Python hello world\""
echo "  goose --profile coding \"Write a FastAPI endpoint\""
echo ""

# Si pas de commande, lancer bash interactif
if [ "$#" -eq 0 ]; then
    exec bash
else
    exec "$@"
fi
