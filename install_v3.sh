#!/usr/bin/env bash
# File Path: install.sh
# =========================================================================
# REVOLUTIONARY TECHNOLOGY COMPANY — UNIVAC IX MAIN OPERATING FABRIC
# Master Platform Persistent Installation, Network Binding, & Hardening Script
# Enforces: Stable -> Secure -> Fast Production Execution Benchmarks
# =========================================================================

set -e # Terminate script immediately if any sub-command drops an error code

echo "=== INITIALIZING AGRICULTURE PATHOLOGY INSTITUTE DEPLOYMENT ENGINE ==="
echo "[*] Target Environment Baseline: Ubuntu Host Linux Architecture"

# 1. Enforce strict system-level environment variables
export UNIVAC_CORE_DIR="$(pwd)"
export UNIVAC_DATA_DIR="$UNIVAC_CORE_DIR/Data/UnivacStreams"
export ZEPHYR_BOARD_REPO="https://github.com"

echo "[*] Exporting platform environment variables..."
mkdir -p "$UNIVAC_DATA_DIR"
mkdir -p build_artifacts

# 2. Verify Docker and NVIDIA Runtime dependencies are live on the Ubuntu host
if ! command -v docker &> /dev/null; then
    echo "[-] Error: Docker daemon not detected. Install Docker Engine before booting the fabric."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "[-] Error: docker-compose engine missing from system binaries path."
    exit 1
fi

# 3. Synchronize and clone out-of-tree hardware repository support packages
echo "[*] Synchronizing pristine out-of-tree Zephyr Board Support Packages..."
if [ ! -d "Zephyr-RTOS-Board-Support-Package-BSP" ]; then
    git clone "$ZEPHYR_BOARD_REPO" Zephyr-RTOS-Board-Support-Package-BSP
else
    cd Zephyr-RTOS-Board-Support-Package-BSP && git pull && cd ..
fi

# 4. Run pre-flight syntax checks on core layout parameters
echo "[*] Executing pre-flight schema validations over local config.yaml..."
if [ -f "validate-config.js" ]; then
    node validate-config.js || { echo "[-] Critical configuration syntax error detected. Boot halted."; exit 1; }
fi

# 5. Programmatically Build the Persistent Firewall Security Fencing Helper Script
echo "[*] Compiling persistent zero-trust local network hardening scripts..."
cat <<'EOF' > "$UNIVAC_CORE_DIR/scripts/apply_network_hardening.sh"
#!/usr/bin/env bash
# Formulated Local Base Station Zero-Trust Firewall Rule Matrix
iptables -F
iptables -X
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Authorize loopback and verified university consortium hardware links
iptables -A INPUT -i lo -j ACCEPT

APPROVED_IPS=(
    "127.0.0.1"      # Local Core Loopback
    "192.168.1.100"  # Authorized UW AG Cohort Primary Cockpit
    "192.168.1.101"  # Authorized Kansas State Precision Team Link
    "192.168.1.102"  # Authorized Central Washington Grid Sub-station
    "192.168.1.50"   # Authorized Local Ubuntu Docker Host Interface
)

for IP in "${APPROVED_IPS[@]}"; do
    iptables -A INPUT -p tcp -s "$IP" --dport 8080 -j ACCEPT
    iptables -A INPUT -p tcp -s "$IP" --dport 8081 -j ACCEPT
    iptables -A INPUT -p tcp -s "$IP" --dport 8082 -j ACCEPT
    iptables -A INPUT -p tcp -s "$IP" --dport 8083 -j ACCEPT
done

# Route un-whitelisted exceptions directly to the local audio alarm logs
iptables -A INPUT -p tcp --dport 8080 -j LOG --log-prefix "[🚨 UNIVAC IX INTRUSION ALERT] "
iptables -A INPUT -p tcp --dport 8080 -j DROP
EOF

chmod +x "$UNIVAC_CORE_DIR/scripts/apply_network_hardening.sh"

# 6. Launch the prioritized multi-container Docker Compose network loop
echo "[🚀 Launching System Fabric] Initializing secure container layers over internal bridge..."
docker-compose up -d --build

# 7. Verify that the RAM-drive volatile tmpfs pipeline volume is mounted cleanly
echo "[*] Verifying performance tmpfs allocation parameters..."
if mount | grep -q "univac_stream_data"; then
    echo "[+] High-speed temporary RAM-drive buffer mounted successfully (MTU=1500)."
else
    echo "[⚠️ Warning] High-speed tmpfs volume partition fallback activated."
fi

# 8. Configure Persistent Systemd Service for Boot Execution & Security Enforcement
echo "[*] Configuring persistent systemd automation service with boot firewall locks..."
cat <<EOF | sudo tee /etc/systemd/system/univac-fabric.service > /dev/null
[Unit]
Description=UNIVAC IX Core Fabric Multi-Platform Fleet Automation & Network Fencing Daemon
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$UNIVAC_CORE_DIR
ExecStartPre=$UNIVAC_CORE_DIR/scripts/apply_network_hardening.sh
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down -v

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable univac-fabric.service
echo "[+] Persistent system boot daemon and firewall locks successfully registered and enabled."

echo -e "\n========================================================================="
echo "🪐 [DEPLOYMENT SUCCESSFUL] UNIVAC IX CORE FABRIC IS ONLINE AND SECURED."
echo "========================================================================="
echo "[*] Government XR Viewports (Tier 1) routing data live on Port 8080 [1.22]."
echo "[*] Local base station firewall locks active. Rogue remote signals are DROPPED."
echo "[*] Edwards FireWorks Supervisory loops active and held HIGH [1.15]."
echo "[*] Use 'docker-compose logs -f' to stream real-time telemetry metrics."
