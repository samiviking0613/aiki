#!/bin/bash
# AIKI-HOME Transparent Proxy Setup
# Intercepterer all HTTP/HTTPS trafikk fra WireGuard clients
# uten at de trenger å konfigurere proxy-innstillinger
#
# Fungerer selv med apps som bruker certificate pinning (TikTok etc)
# fordi appen tror den snakker direkte med serveren

set -e

# Konfigurasjon
WG_INTERFACE="wg0"
WG_SUBNET="10.8.0.0/24"
PROXY_PORT=8080
PROXY_PORT_HTTPS=8443
LOCAL_IP="10.8.0.1"

# Farger
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

show_help() {
    cat << EOF
AIKI-HOME Transparent Proxy

Bruk:
  $0 start     - Start transparent proxy + iptables redirect
  $0 stop      - Stopp proxy og fjern iptables regler
  $0 status    - Vis status
  $0 passthrough - Bytt til passthrough mode (ingen inspeksjon)
  $0 inspect   - Bytt til inspect mode (full MITM)

Arkitektur:
  iPhone → WireGuard VPN → iptables REDIRECT → mitmproxy → Internett

Merk:
  - Krever at mitmproxy CA-sert er installert på enheten
  - Certificate pinning apps (TikTok) vil fungere i passthrough mode
  - Inspect mode gir full HTTPS dekryptering for ikke-pinnede apps
EOF
}

setup_iptables() {
    print_status "Setter opp iptables regler..."

    # Fjern gamle regler først
    teardown_iptables 2>/dev/null || true

    # Redirect HTTP (80) fra WG clients til lokal proxy
    sudo iptables -t nat -A PREROUTING -i $WG_INTERFACE -p tcp --dport 80 \
        -j REDIRECT --to-port $PROXY_PORT

    # Redirect HTTPS (443) fra WG clients til lokal proxy
    sudo iptables -t nat -A PREROUTING -i $WG_INTERFACE -p tcp --dport 443 \
        -j REDIRECT --to-port $PROXY_PORT_HTTPS

    # Marker pakker for mitmproxy transparent mode
    sudo iptables -t mangle -A PREROUTING -i $WG_INTERFACE -p tcp --dport 80 \
        -j MARK --set-mark 1
    sudo iptables -t mangle -A PREROUTING -i $WG_INTERFACE -p tcp --dport 443 \
        -j MARK --set-mark 1

    print_status "iptables konfigurert"
}

teardown_iptables() {
    print_status "Fjerner iptables regler..."

    # Fjern NAT regler
    sudo iptables -t nat -D PREROUTING -i $WG_INTERFACE -p tcp --dport 80 \
        -j REDIRECT --to-port $PROXY_PORT 2>/dev/null || true
    sudo iptables -t nat -D PREROUTING -i $WG_INTERFACE -p tcp --dport 443 \
        -j REDIRECT --to-port $PROXY_PORT_HTTPS 2>/dev/null || true

    # Fjern mangle regler
    sudo iptables -t mangle -D PREROUTING -i $WG_INTERFACE -p tcp --dport 80 \
        -j MARK --set-mark 1 2>/dev/null || true
    sudo iptables -t mangle -D PREROUTING -i $WG_INTERFACE -p tcp --dport 443 \
        -j MARK --set-mark 1 2>/dev/null || true

    print_status "iptables regler fjernet"
}

start_proxy() {
    local mode=${1:-"passthrough"}

    print_status "Starter mitmproxy i transparent mode ($mode)..."

    # Sjekk om mitmproxy er installert
    if ! command -v mitmproxy &> /dev/null; then
        print_error "mitmproxy er ikke installert!"
        echo "Installer med: pip install mitmproxy"
        exit 1
    fi

    # Opprett log dir
    mkdir -p ~/aiki/logs/proxy

    # Start mitmproxy
    if [ "$mode" == "passthrough" ]; then
        # Passthrough mode - ingen HTTPS dekryptering
        # Fungerer med certificate pinning apps
        print_warning "Passthrough mode: HTTPS trafikk blir IKKE dekryptert"

        mitmdump \
            --mode transparent \
            --listen-host $LOCAL_IP \
            --listen-port $PROXY_PORT \
            --ssl-insecure \
            --ignore-hosts '.*' \
            -s ~/aiki/src/proxy/aiki_addon.py \
            > ~/aiki/logs/proxy/mitm.log 2>&1 &
    else
        # Inspect mode - full MITM
        print_warning "Inspect mode: HTTPS trafikk blir dekryptert (krever CA-sert)"

        mitmdump \
            --mode transparent \
            --listen-host $LOCAL_IP \
            --listen-port $PROXY_PORT \
            --ssl-insecure \
            -s ~/aiki/src/proxy/aiki_addon.py \
            > ~/aiki/logs/proxy/mitm.log 2>&1 &
    fi

    echo $! > /tmp/aiki_proxy.pid
    sleep 2

    if pgrep -f "mitmdump.*transparent" > /dev/null; then
        print_status "mitmproxy startet (PID: $(cat /tmp/aiki_proxy.pid))"
    else
        print_error "Feil ved start av mitmproxy"
        cat ~/aiki/logs/proxy/mitm.log
        exit 1
    fi
}

stop_proxy() {
    print_status "Stopper mitmproxy..."

    if [ -f /tmp/aiki_proxy.pid ]; then
        kill $(cat /tmp/aiki_proxy.pid) 2>/dev/null || true
        rm /tmp/aiki_proxy.pid
    fi

    pkill -f "mitmdump.*transparent" 2>/dev/null || true

    print_status "mitmproxy stoppet"
}

show_status() {
    echo "═══════════════════════════════════════════════════════════"
    echo "AIKI-HOME TRANSPARENT PROXY STATUS"
    echo "═══════════════════════════════════════════════════════════"

    # WireGuard status
    echo -e "\n${YELLOW}WireGuard:${NC}"
    if ip link show wg0 &>/dev/null; then
        echo -e "  Interface: ${GREEN}UP${NC}"
        wg show wg0 | grep -E "peer|latest handshake" | head -4
    else
        echo -e "  Interface: ${RED}DOWN${NC}"
    fi

    # Proxy status
    echo -e "\n${YELLOW}Proxy:${NC}"
    if pgrep -f "mitmdump.*transparent" > /dev/null; then
        echo -e "  mitmproxy: ${GREEN}RUNNING${NC}"
        pgrep -f "mitmdump" | head -1
    else
        echo -e "  mitmproxy: ${RED}STOPPED${NC}"
    fi

    # iptables status
    echo -e "\n${YELLOW}iptables redirect regler:${NC}"
    sudo iptables -t nat -L PREROUTING -n | grep -E "REDIRECT|dpt:(80|443)" || echo "  Ingen redirect regler"

    # Aktive connections
    echo -e "\n${YELLOW}Aktive connections fra WG:${NC}"
    ss -tn | grep "10.8.0" | head -5 || echo "  Ingen aktive connections"

    echo ""
    echo "═══════════════════════════════════════════════════════════"
}

# Main
case "${1:-help}" in
    start)
        setup_iptables
        start_proxy "${2:-passthrough}"
        show_status
        ;;
    stop)
        stop_proxy
        teardown_iptables
        show_status
        ;;
    status)
        show_status
        ;;
    passthrough)
        stop_proxy
        start_proxy "passthrough"
        ;;
    inspect)
        stop_proxy
        start_proxy "inspect"
        ;;
    *)
        show_help
        ;;
esac
