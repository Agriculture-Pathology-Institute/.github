#!/usr/bin/env bash
# File Path: scripts/apply_network_hardening.sh
# =========================================================================
# REVOLUTIONARY TECHNOLOGY COMPANY — UNIVAC IX MAIN OPERATING FABRIC
# Local Base Station Firewall Hardening & Network Security Fencing
# Objective: Defend against unauthorized remote connections or script interference
# =========================================================================

set -e

echo "=== INITIALIZING HARDENED NETWORK SECURITY FENCING ACT ==="
echo "[*] Base Station Target: UW Medicine Ballard Machinery Room Servers"

# 1. Enforce strict non-privileged execution bounds check
if [ "$EUID" -ne 0 ]; then
  echo "[-] Error: This network hardening script must be executed with root/sudo privileges."
  exit 1
fi

# 2. Reset local firewall rules to a clean, zero-trust default DROP policy
echo "[*] Purging active firewall rules... Transitioning to Zero-Trust Baseline..."
iptables -F
iptables -X
iptables -P INPUT DROP   # Dropping all un-vetted incoming packets by default
iptables -P FORWARD DROP # Blocking cross-network packet jumping
iptables -P OUTPUT ACCEPT # Authorizing outbound telemetry streaming

# 3. Always authorize the local loopback interface (Internal system communication)
iptables -A INPUT -i lo -j ACCEPT

# 4. EXPLICIT PEER WHITELISTING MATRIX
# Only allow connections from verified, designated industrial network nodes
# Add your local terminal and cockpit hardware IP paths exactly here:
APPROVED_IPS=(
    "127.0.0.1"      # Local Core Loopback
    "192.168.1.100"  # Authorized UW AG Cohort Primary Cockpit
    "192.168.1.101"  # Authorized Kansas State Precision Team Link
    "192.168.1.102"  # Authorized Central Washington Grid Sub-station
    "192.168.1.50"   # Authorized Local Ubuntu Docker Host Interface
)

echo "[*] Mapping explicit cryptographic perimeter clear zones for approved peers..."
for IP in "${APPROVED_IPS[@]}"; do
    echo "[+] Authorizing Secure Gateway Access Path for Approved Peer: $IP"
    # Lock down Port 8080 (RtJsonNetworkBridge) to verified hardware nodes only
    iptables -A INPUT -p tcp -s "$IP" --dport 8080 -j ACCEPT
    # Lock down Port 8081 (LiveNetworkAudioAlarm) to verified hardware nodes only
    iptables -A INPUT -p tcp -s "$IP" --dport 8081 -j ACCEPT
    # Lock down Port 8082 (Edwards FireWorks Interface) to verified hardware nodes only
    iptables -A INPUT -p tcp -s "$IP" --dport 8082 -j ACCEPT
done

# 5. Log and Drop all unauthorized connection attempts from local outside devices
iptables -A INPUT -p tcp --dport 8080 -j LOG --log-prefix "[🚨 UNIVAC IX INTRUSION ALERT] "
iptables -A INPUT -p tcp --dport 8080 -j DROP

echo -e "\n========================================================================="
echo "🔒 [SECURITY PERIMETER ACTIVE] BALLARD BASE STATION NETWORK IS FULLY HARDENED."
echo "========================================================================="
echo "[+] All un-vetted outside signals attempting connection to Port 8080 are DROPPED."
echo "[+] Unauthorized remote controllers or local wireless devices are blocked."
echo "[+] Use 'sudo iptables -L -v' to audit current network defensive blocks."
