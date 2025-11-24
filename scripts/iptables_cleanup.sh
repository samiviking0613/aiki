#!/bin/bash
# Cleanup iptables for transparent proxy
iptables -t nat -D PREROUTING -i wg0 -p tcp --dport 80 -j REDIRECT --to-port 8080 2>/dev/null
iptables -t nat -D PREROUTING -i wg0 -p tcp --dport 443 -j REDIRECT --to-port 8080 2>/dev/null
echo "iptables cleanup complete"
