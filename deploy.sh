#!/usr/bin/env bash
# =============================================================================
# ForgeNest — Déploiement
# =============================================================================
# Usage :
#   ./deploy.sh              → menu interactif
#   ./deploy.sh start full   → Stack Complète directement
#   ./deploy.sh start lite   → Stack Lite directement
#   ./deploy.sh stop         → arrêt propre
#   ./deploy.sh status       → état des services
#   ./deploy.sh logs [svc]   → logs temps réel
#   ./deploy.sh --help       → aide
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Couleurs
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}ℹ  $*${RESET}"; }
success() { echo -e "${GREEN}✅ $*${RESET}"; }
warning() { echo -e "${YELLOW}⚠️  $*${RESET}"; }
error()   { echo -e "${RED}❌ $*${RESET}"; exit 1; }
header()  { echo -e "\n${BOLD}${CYAN}━━━  $*  ━━━${RESET}\n"; }
sep()     { echo -e "${CYAN}──────────────────────────────────────────────────────${RESET}"; }

# =============================================================================
banner() {
  clear
  echo -e "${BOLD}${CYAN}"
  cat << 'BANNER'
  ___                 _  _        _
 | __| ___  _ _  __ _| \| | ___  __| |_
 | _| / _ \| '_|/ _` | .` |/ -_)(_-<  _|
 |_|  \___/|_|  \__, |_|\_|\___| /__/\__|
                |___/
BANNER
  echo -e "${RESET}"
  echo -e "${BOLD}Votre forge de développement privée, autonome et souveraine.${RESET}"
  echo ""
}

# =============================================================================
check_deps() {
  command -v docker &>/dev/null      || error "Docker non installé → https://docs.docker.com/get-docker/"
  docker info &>/dev/null            || error "Docker daemon non démarré (ou permissions insuffisantes)"
  docker compose version &>/dev/null || error "Docker Compose V2 requis"
}

detect_ram() { free -g 2>/dev/null | awk '/^Mem:/{print $2}' || echo "?"; }

# =============================================================================
# MENU
# =============================================================================
show_menu() {
  local ram
  ram=$(detect_ram)

  sep
  echo -e "${BOLD}Choisissez votre configuration :${RESET}"
  echo ""

  echo -e "  ${BOLD}${GREEN}[1] ForgeNest Full${RESET}"
  echo -e "      Forgejo · Woodpecker CI/CD"
  echo -e "      Ollama · LiteLLM · Langfuse · Open WebUI"
  echo -e "      AI Gateway · Tabby · Goose · Perplexica"
  echo -e "      ${YELLOW}RAM : ~20 GB${RESET} — Serveur dédié, workstation"
  echo ""

  echo -e "  ${BOLD}${GREEN}[2] ForgeNest Lite${RESET}  ⭐ recommandé homeserver"
  echo -e "      Forgejo · Woodpecker CI/CD"
  echo -e "      llama.cpp · LiteLLM · Open WebUI · AI Gateway"
  echo -e "      ${GREEN}RAM : 4–6 GB${RESET} — ZimaBoard, NAS, Mini-PC N100"
  echo ""

  echo -e "  ${BOLD}[q] Quitter${RESET}"
  sep

  # Recommandation automatique
  if [[ "$ram" =~ ^[0-9]+$ ]]; then
    if (( ram < 12 )); then
      echo -e "  ${CYAN}Votre machine : ${BOLD}${ram} GB RAM${RESET}${CYAN} → option ${BOLD}2 (Lite)${RESET}${CYAN} recommandée${RESET}"
    else
      echo -e "  ${CYAN}Votre machine : ${BOLD}${ram} GB RAM${RESET}${CYAN} → les deux options sont disponibles${RESET}"
    fi
    echo ""
  fi

  read -rp "Votre choix [1/2/q] : " choice
  echo ""
  echo "$choice"
}

# =============================================================================
# CONFIGURATION .env
# =============================================================================
setup_env() {
  local env_file="$SCRIPT_DIR/.env"
  local example_file="$SCRIPT_DIR/.env.example"

  if [[ ! -f "$env_file" ]]; then
    [[ -f "$example_file" ]] || error ".env.example introuvable dans $SCRIPT_DIR"
    info "Création de .env depuis .env.example…"
    cp "$example_file" "$env_file"
    echo ""
    warning "Configurez vos secrets avant de continuer :"
    echo -e "  ${CYAN}nano $env_file${RESET}"
    echo ""
    echo -e "${BOLD}Variables essentielles :${RESET}"
    echo -e "  FORGEJO_ADMIN_PASSWORD, WOODPECKER_SECRET"
    echo -e "  LITELLM_MASTER_KEY, POSTGRES_PASSWORD"
    echo ""
    read -rp "Appuyez sur Entrée une fois .env configuré (Ctrl+C pour annuler)…"
  else
    info ".env existant conservé."
  fi
}

setup_env_lite() {
  local lite_env="$SCRIPT_DIR/AI-Stack-Lite/.env.lite"
  local lite_example="$SCRIPT_DIR/AI-Stack-Lite/.env.lite.example"

  if [[ ! -f "$lite_env" ]]; then
    [[ -f "$lite_example" ]] || error ".env.lite.example introuvable"
    info "Création de AI-Stack-Lite/.env.lite depuis l'exemple…"
    cp "$lite_example" "$lite_env"
    echo ""
    warning "Configurez votre modèle IA et les paramètres :"
    echo -e "  ${CYAN}nano $lite_env${RESET}"
    echo ""
    echo -e "${BOLD}Variables essentielles :${RESET}"
    echo -e "  LLAMACPP_MODEL_REPO, LLAMACPP_MODEL_FILE"
    echo -e "  LITELLM_MASTER_KEY, WEBUI_SECRET_KEY"
    echo ""
    read -rp "Appuyez sur Entrée une fois .env.lite configuré…"
  else
    info "AI-Stack-Lite/.env.lite existant conservé."
  fi
}

# =============================================================================
# DÉPLOIEMENT
# =============================================================================
deploy_full() {
  header "ForgeNest Full"
  setup_env
  cd "$SCRIPT_DIR"

  info "Démarrage de la stack complète…"
  docker compose \
    -f "$SCRIPT_DIR/docker-compose.yml" \
    --env-file "$SCRIPT_DIR/.env" \
    up -d

  success "ForgeNest Full démarré !"
  _print_urls_full
}

deploy_lite() {
  header "ForgeNest Lite"
  setup_env
  setup_env_lite
  cd "$SCRIPT_DIR"

  # Le model-downloader peut prendre plusieurs minutes au premier démarrage
  info "Démarrage de la stack Lite…"
  info "(Le modèle IA sera téléchargé automatiquement au premier lancement)"
  docker compose \
    -f "$SCRIPT_DIR/docker-compose.lite.yaml" \
    --env-file "$SCRIPT_DIR/.env" \
    up -d

  success "ForgeNest Lite démarré !"
  echo ""
  info "Suivi du téléchargement du modèle :"
  echo -e "  ${CYAN}docker logs -f ai-lite-model-downloader${RESET}"
  _print_urls_lite
}

# =============================================================================
# OPÉRATIONS
# =============================================================================
cmd_stop() {
  header "Arrêt"
  local stopped=0

  # Tenter d'arrêter Full
  if docker compose -f "$SCRIPT_DIR/docker-compose.yml" \
      ps --quiet 2>/dev/null | grep -q .; then
    info "Arrêt ForgeNest Full…"
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" down
    (( stopped++ )) || true
  fi

  # Tenter d'arrêter Lite
  if docker compose -f "$SCRIPT_DIR/docker-compose.lite.yaml" \
      ps --quiet 2>/dev/null | grep -q .; then
    info "Arrêt ForgeNest Lite…"
    docker compose -f "$SCRIPT_DIR/docker-compose.lite.yaml" down
    (( stopped++ )) || true
  fi

  (( stopped > 0 )) && success "Arrêt terminé." || info "Aucune stack active."
}

cmd_status() {
  header "État — ForgeNest Full"
  if [[ -f "$SCRIPT_DIR/.env" ]]; then
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" \
      --env-file "$SCRIPT_DIR/.env" \
      ps 2>/dev/null || info "(non démarrée)"
  else
    info ".env non configuré"
  fi

  header "État — ForgeNest Lite"
  if [[ -f "$SCRIPT_DIR/AI-Stack-Lite/.env.lite" ]]; then
    docker compose -f "$SCRIPT_DIR/docker-compose.lite.yaml" \
      --env-file "$SCRIPT_DIR/.env" \
      ps 2>/dev/null || info "(non démarrée)"
  else
    info ".env.lite non configuré"
  fi
}

cmd_logs() {
  local svc="${2:-}"
  # Cherche dans laquelle des stacks le service tourne
  if docker compose -f "$SCRIPT_DIR/docker-compose.lite.yaml" \
      ps --quiet "$svc" 2>/dev/null | grep -q .; then
    docker compose -f "$SCRIPT_DIR/docker-compose.lite.yaml" logs -f $svc
  elif docker compose -f "$SCRIPT_DIR/docker-compose.yml" \
      ps --quiet "$svc" 2>/dev/null | grep -q .; then
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" logs -f $svc
  else
    # Logs de toutes les stacks actives
    docker compose -f "$SCRIPT_DIR/docker-compose.yml" logs -f $svc 2>/dev/null &
    docker compose -f "$SCRIPT_DIR/docker-compose.lite.yaml" logs -f $svc 2>/dev/null &
    wait
  fi
}

cmd_help() {
  echo ""
  echo -e "${BOLD}ForgeNest — Déploiement${RESET}"
  echo ""
  echo -e "${BOLD}Usage :${RESET}"
  echo "  ./deploy.sh                → menu interactif"
  echo "  ./deploy.sh start full     → ForgeNest Full directement"
  echo "  ./deploy.sh start lite     → ForgeNest Lite directement"
  echo "  ./deploy.sh stop           → arrêt propre de toutes les stacks"
  echo "  ./deploy.sh status         → état des services"
  echo "  ./deploy.sh logs [service] → logs temps réel"
  echo "  ./deploy.sh --help         → cet écran"
  echo ""
  echo -e "${BOLD}Exemples :${RESET}"
  echo "  ./deploy.sh start lite"
  echo "  ./deploy.sh logs ai-gateway"
  echo "  ./deploy.sh logs llama-cpp"
  echo ""
}

# =============================================================================
# URLs
# =============================================================================
_read_env()      { grep "^${1}=" "${2:-$SCRIPT_DIR/.env}" 2>/dev/null | cut -d= -f2 | tr -d '"' || echo "${3:-}"; }

_print_urls_full() {
  echo ""
  sep
  echo -e "${BOLD}🌐 Services :${RESET}"
  echo -e "   🦊 Forgejo     → ${CYAN}http://localhost:$(_read_env FORGEJO_HTTP_PORT "" 5333)${RESET}"
  echo -e "   🪵 Woodpecker  → ${CYAN}http://localhost:$(_read_env WOODPECKER_PORT "" 5444)${RESET}"
  echo -e "   🎨 Open WebUI  → ${CYAN}http://localhost:$(_read_env WEBUI_PORT "" 3001)${RESET}"
  echo -e "   ⚡ LiteLLM     → ${CYAN}http://localhost:$(_read_env LITELLM_PORT "" 4000)${RESET}"
  echo -e "   📊 Langfuse    → ${CYAN}http://localhost:$(_read_env LANGFUSE_PORT "" 3002)${RESET}"
  echo -e "   🌐 AI Gateway  → ${CYAN}http://localhost:$(_read_env AI_GATEWAY_PORT "" 8000)${RESET}"
  sep
  echo ""
}

_print_urls_lite() {
  local lite_env="$SCRIPT_DIR/AI-Stack-Lite/.env.lite"
  echo ""
  sep
  echo -e "${BOLD}🌐 Services :${RESET}"
  echo -e "   🦊 Forgejo     → ${CYAN}http://localhost:$(_read_env FORGEJO_HTTP_PORT "" 5333)${RESET}"
  echo -e "   🪵 Woodpecker  → ${CYAN}http://localhost:$(_read_env WOODPECKER_PORT "" 5444)${RESET}"
  echo -e "   🎨 Open WebUI  → ${CYAN}http://localhost:$(_read_env WEBUI_PORT "$lite_env" 3000)${RESET}"
  echo -e "   ⚡ LiteLLM     → ${CYAN}http://localhost:$(_read_env LITELLM_PORT "$lite_env" 4000)${RESET}"
  echo -e "   🌐 AI Gateway  → ${CYAN}http://localhost:$(_read_env AI_GATEWAY_PORT "$lite_env" 8000)${RESET}"
  echo -e "   ⚙️  llama.cpp   → ${CYAN}http://localhost:$(_read_env LLAMACPP_PORT "$lite_env" 8081)${RESET}"
  sep
  echo ""
}

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================
check_deps

case "${1:-}" in
  start)
    banner
    target="${2:-}"
    if [[ -z "$target" ]]; then
      target=$(show_menu)
    fi
    case "$target" in
      1|full)  deploy_full ;;
      2|lite)  deploy_lite ;;
      q|Q)     echo "Au revoir !"; exit 0 ;;
      *)       error "Choix invalide : '$target'  (full ou lite attendu)" ;;
    esac
    ;;
  stop)        cmd_stop ;;
  status)      cmd_status ;;
  logs)        cmd_logs "$@" ;;
  --help|-h)   cmd_help ;;
  "")
    banner
    choice=$(show_menu)
    case "$choice" in
      1|full)  deploy_full ;;
      2|lite)  deploy_lite ;;
      q|Q)     echo "Au revoir !"; exit 0 ;;
      *)       error "Choix invalide : '$choice'" ;;
    esac
    ;;
  *)
    error "Commande inconnue : '$1'  (--help pour l'aide)"
    ;;
esac
