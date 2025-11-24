#!/bin/bash
# Setup iptables for transparent proxy
iptables -t nat -A PREROUTING -i wg0 -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -i wg0 -p tcp --dport 443 -j REDIRECT --to-port 8080
echo "iptables setup complete"
