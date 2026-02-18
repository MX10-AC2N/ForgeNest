#!/usr/bin/env bash
# =============================================================================
# ForgeNest — Stack IA LITE
# Script de déploiement pour homeserver (ZimaBoard, NAS, Mini-PC…)
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STACK_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}ℹ  $*${RESET}"; }
success() { echo -e "${GREEN}✅ $*${RESET}"; }
warning() { echo -e "${YELLOW}⚠️  $*${RESET}"; }
error()   { echo -e "${RED}❌ $*${RESET}"; exit 1; }
header()  { echo -e "\n${BOLD}${CYAN}━━━  $*  ━━━${RESET}\n"; }

COMPOSE="docker compose -f $STACK_DIR/docker-compose.lite.yaml --env-file $STACK_DIR/.env.lite"

# =============================================================================
check_deps() {
  command -v docker &>/dev/null  || error "Docker non installé. Voir : https://docs.docker.com/get-docker/"
  docker info &>/dev/null        || error "Daemon Docker non démarré (ou permissions insuffisantes)."
  docker compose version &>/dev/null || error "Docker Compose V2 requis."
}

detect_ram() { free -g 2>/dev/null | awk '/^Mem:/ {print $2}' || echo "?"; }
detect_cpu() { nproc 2>/dev/null || echo "?"; }

# =============================================================================
configure() {
  header "Configuration"

  if [[ ! -f "$STACK_DIR/.env.lite" ]]; then
    info "Création de .env.lite depuis .env.lite.example..."
    cp "$STACK_DIR/.env.lite.example" "$STACK_DIR/.env.lite"
    success ".env.lite créé"
  else
    info ".env.lite existant détecté"
  fi

  local ram cpu
  ram=$(detect_ram); cpu=$(detect_cpu)
  echo -e "  Système détecté : ${BOLD}${ram} GB RAM${RESET} / ${BOLD}${cpu} CPU${RESET}"
  echo ""

  # Suggestion modèle selon RAM
  echo -e "${BOLD}Choisissez votre modèle GGUF :${RESET}"
  echo "  [1] Qwen2.5-1.5B  (1.0 GB) ← défaut, idéal ≤4 GB RAM"
  echo "  [2] Phi-3.5-mini   (2.2 GB) — excellent rapport qualité/taille"
  echo "  [3] Llama-3.2-3B   (2.0 GB) — très bon pour le chat"
  echo "  [4] Qwen2.5-7B     (4.4 GB) — meilleure qualité, ≥8 GB RAM"
  echo "  [5] Qwen2.5-Coder-1.5B (1.0 GB) — spécialisé code"
  echo "  [6] Modèle personnalisé"
  echo ""
  read -rp "Choix [1-6, Entrée = 1] : " c

  case "${c:-1}" in
    1) REPO="Qwen/Qwen2.5-1.5B-Instruct-GGUF";          FILE="qwen2.5-1.5b-instruct-q4_k_m.gguf" ;;
    2) REPO="bartowski/Phi-3.5-mini-instruct-GGUF";       FILE="Phi-3.5-mini-instruct-Q4_K_M.gguf" ;;
    3) REPO="bartowski/Llama-3.2-3B-Instruct-GGUF";       FILE="Llama-3.2-3B-Instruct-Q4_K_M.gguf" ;;
    4) REPO="Qwen/Qwen2.5-7B-Instruct-GGUF";              FILE="qwen2.5-7b-instruct-q4_k_m.gguf" ;;
    5) REPO="Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF";      FILE="qwen2.5-coder-1.5b-instruct-q4_k_m.gguf" ;;
    6) read -rp "Repo HuggingFace : " REPO; read -rp "Fichier GGUF : " FILE ;;
    *) error "Choix invalide" ;;
  esac

  # Calcul auto threads et contexte
  local threads=3 ctx=2048
  [[ "$cpu" =~ ^[0-9]+$ ]] && threads=$(( cpu > 1 ? cpu - 1 : 1 ))
  [[ "$ram" =~ ^[0-9]+$ ]] && (( ram >= 8 )) && ctx=4096
  [[ "$ram" =~ ^[0-9]+$ ]] && (( ram >= 16 )) && ctx=8192

  sed -i "s|^LLAMACPP_MODEL_REPO=.*|LLAMACPP_MODEL_REPO=${REPO}|"   "$STACK_DIR/.env.lite"
  sed -i "s|^LLAMACPP_MODEL_FILE=.*|LLAMACPP_MODEL_FILE=${FILE}|"   "$STACK_DIR/.env.lite"
  sed -i "s|^LLAMACPP_THREADS=.*|LLAMACPP_THREADS=${threads}|"      "$STACK_DIR/.env.lite"
  sed -i "s|^LLAMACPP_CTX=.*|LLAMACPP_CTX=${ctx}|"                  "$STACK_DIR/.env.lite"

  success "Modèle configuré : ${FILE} (threads=${threads}, ctx=${ctx})"

  echo ""
  echo -e "${BOLD}Clés API gratuites (optionnelles — fallback automatique) :${RESET}"
  read -rp "  Clé Groq (⭐ recommandé — gratuit) ? [y/N] : " yn
  if [[ "$yn" =~ ^[Yy]$ ]]; then
    read -rp "  GROQ_API_KEY : " key
    sed -i "s|^GROQ_API_KEY=.*|GROQ_API_KEY=${key}|" "$STACK_DIR/.env.lite"
    success "Groq configuré"
  fi

  read -rp "  Clé OpenRouter ? [y/N] : " yn
  if [[ "$yn" =~ ^[Yy]$ ]]; then
    read -rp "  OPENROUTER_API_KEY : " key
    sed -i "s|^OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=${key}|" "$STACK_DIR/.env.lite"
    success "OpenRouter configuré"
  fi
}

# =============================================================================
start() {
  header "Démarrage de la Stack Lite"

  mkdir -p "$STACK_DIR/volumes/lite/models"
  $COMPOSE up -d

  success "Stack démarrée !"
  echo ""
  echo -e "${BOLD}📥 Téléchargement du modèle en cours...${RESET}"
  echo -e "   Suivi : ${CYAN}docker logs -f ai-lite-model-downloader${RESET}"
  echo ""
  echo -e "${BOLD}🌐 Services :${RESET}"
  echo -e "   Open WebUI  → ${CYAN}http://localhost:3000${RESET}"
  echo -e "   LiteLLM     → ${CYAN}http://localhost:4000${RESET}  (cache + routing)"
  echo -e "   AI Gateway  → ${CYAN}http://localhost:8000${RESET}  (API unifiée)"
  echo -e "     ↳ Modèles   ${CYAN}http://localhost:8000/v1/models${RESET}"
  echo -e "     ↳ Providers ${CYAN}http://localhost:8000/v1/providers${RESET}"
  echo -e "   llama.cpp   → ${CYAN}http://localhost:8081${RESET}  (debug)"
  echo ""
  echo -e "${BOLD}📊 Logs :${RESET}"
  echo -e "   ${CYAN}$COMPOSE logs -f${RESET}"
}

# =============================================================================
cmd_stop()   { header "Arrêt"; cd "$STACK_DIR"; $COMPOSE down; success "Stack arrêtée"; }
cmd_status() { header "Statut"; $COMPOSE ps; }
cmd_logs()   { $COMPOSE logs -f "${2:-}"; }
cmd_help() {
  echo ""
  echo -e "${BOLD}Usage :${RESET}"
  echo "  $0              # Configuration interactive + démarrage"
  echo "  $0 start        # Démarrage direct (utilise .env.lite existant)"
  echo "  $0 stop         # Arrêt propre"
  echo "  $0 status       # Statut des services"
  echo "  $0 logs [svc]   # Logs en temps réel (optionnel : nom du service)"
  echo ""
}

# =============================================================================
main() {
  check_deps
  case "${1:-}" in
    start)        start ;;
    stop)         cmd_stop ;;
    status)       cmd_status ;;
    logs)         cmd_logs "$@" ;;
    --help|-h)    cmd_help ;;
    "")           configure; start ;;
    *)            error "Commande inconnue : $1  (--help pour l'aide)" ;;
  esac
}

main "$@"
