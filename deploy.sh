#!/usr/bin/env bash
# =============================================================================
# ForgeNest — Déploiement interactif
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info()    { echo -e "${BLUE}ℹ  $*${RESET}"; }
success() { echo -e "${GREEN}✅ $*${RESET}"; }
warning() { echo -e "${YELLOW}⚠️  $*${RESET}"; }
error()   { echo -e "${RED}❌ $*${RESET}"; exit 1; }

# =============================================================================
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

# =============================================================================
check_deps() {
  command -v docker &>/dev/null  || error "Docker non installé."
  docker info &>/dev/null        || error "Docker daemon non démarré."
  docker compose version &>/dev/null || error "Docker Compose V2 requis."
}

detect_ram() { free -g 2>/dev/null | awk '/^Mem:/{print $2}' || echo "?"; }

show_menu() {
  local ram
  ram=$(detect_ram)

  echo -e "${BOLD}Quelle stack souhaitez-vous déployer ?${RESET}"
  echo ""
  echo -e "  ${BOLD}[1] Stack Complète${RESET}  (Full)"
  echo -e "      Forgejo · Woodpecker · Ollama · LiteLLM · Langfuse"
  echo -e "      Open WebUI · Tabby · Goose · Perplexica · AI Gateway"
  echo -e "      ${YELLOW}RAM requise : ~20 GB${RESET} — Serveur dédié / workstation"
  echo ""
  echo -e "  ${BOLD}[2] Stack Légère${RESET}    (Lite) ⭐ recommandée homeserver"
  echo -e "      llama.cpp · LiteLLM · AI Gateway · Open WebUI"
  echo -e "      ${GREEN}RAM requise : 2.5–5.6 GB${RESET} — ZimaBoard, NAS, Mini-PC N100"
  echo ""
  echo -e "  ${BOLD}[3] Les deux${RESET}        (Forgejo+Woodpecker + Stack Lite)"
  echo -e "      CI/CD complet + IA légère sur la même machine"
  echo -e "      ${YELLOW}RAM requise : ~6 GB${RESET}"
  echo ""
  echo -e "  ${BOLD}[q] Quitter${RESET}"
  echo ""

  if [[ "$ram" =~ ^[0-9]+$ ]]; then
    if   (( ram < 6  )); then echo -e "  ${CYAN}Votre machine : ${ram} GB RAM → Option 2 recommandée${RESET}"
    elif (( ram < 16 )); then echo -e "  ${CYAN}Votre machine : ${ram} GB RAM → Options 2 ou 3 recommandées${RESET}"
    else                       echo -e "  ${CYAN}Votre machine : ${ram} GB RAM → Toutes les options disponibles${RESET}"
    fi
    echo ""
  fi

  read -rp "Votre choix [1/2/3/q] : " choice
  echo ""
}

# =============================================================================
deploy_full() {
  header "Stack Complète"

  if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
    info "Création de .env depuis .env.example..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    warning "Éditez .env avant de continuer (secrets, mots de passe)"
    read -rp "Appuyez sur Entrée une fois .env configuré..."
  fi

  docker compose -f "$SCRIPT_DIR/docker-compose.yml" --env-file "$SCRIPT_DIR/.env" up -d

  success "Stack Complète démarrée !"
  echo ""
  echo -e "${BOLD}🌐 Services :${RESET}"
  echo -e "   Forgejo     → ${CYAN}http://localhost:5333${RESET}"
  echo -e "   Woodpecker  → ${CYAN}http://localhost:5444${RESET}"
  echo -e "   Open WebUI  → ${CYAN}http://localhost:3001${RESET}"
  echo -e "   LiteLLM     → ${CYAN}http://localhost:4000${RESET}"
  echo -e "   Langfuse    → ${CYAN}http://localhost:3002${RESET}"
  echo -e "   AI Gateway  → ${CYAN}http://localhost:8000${RESET}"
}

deploy_lite() {
  header "Stack Légère (Lite)"
  bash "$SCRIPT_DIR/AI-Stack-Lite/scripts/deploy.sh"
}

deploy_ci_plus_lite() {
  header "Forgejo + Woodpecker + Stack Lite"

  if [[ ! -f "$SCRIPT_DIR/.env" ]]; then
    info "Création de .env depuis .env.example..."
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    warning "Éditez .env avant de continuer"
    read -rp "Appuyez sur Entrée une fois .env configuré..."
  fi

  # CI/CD stack seule (sans AI-Stack Full)
  docker compose \
    -f "$SCRIPT_DIR/Forgejo-Woodpecker_CI-Stack/docker-compose.yml" \
    --env-file "$SCRIPT_DIR/.env" \
    up -d

  success "Forgejo + Woodpecker démarrés !"
  echo ""

  # Stack Lite
  bash "$SCRIPT_DIR/AI-Stack-Lite/scripts/deploy.sh" start

  echo ""
  echo -e "${BOLD}🌐 Services :${RESET}"
  echo -e "   Forgejo     → ${CYAN}http://localhost:5333${RESET}"
  echo -e "   Woodpecker  → ${CYAN}http://localhost:5444${RESET}"
  echo -e "   Open WebUI  → ${CYAN}http://localhost:3000${RESET}"
  echo -e "   LiteLLM     → ${CYAN}http://localhost:4000${RESET}"
  echo -e "   AI Gateway  → ${CYAN}http://localhost:8000${RESET}"
}

header() { echo -e "\n${BOLD}${CYAN}━━━  $*  ━━━${RESET}\n"; }

# =============================================================================
check_deps
show_menu

case "${choice:-}" in
  1)   deploy_full ;;
  2)   deploy_lite ;;
  3)   deploy_ci_plus_lite ;;
  q|Q) echo "Au revoir !"; exit 0 ;;
  *)   error "Choix invalide : '$choice'" ;;
esac
