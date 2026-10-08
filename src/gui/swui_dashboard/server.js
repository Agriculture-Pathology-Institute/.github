const net = require('net');
const WebSocket = require('ws');

// Spawn WebSocket server for SWUI / HLS Camera overlays
const wss = new WebSocket.Server({ port: 8082 });
console.log('SWUI WebSocket Broadcaster online on port 8082');

// Connect natively to the active JSON network bridge
const telemetryClient = new net.Socket();

function connectToCoreBridge() {
    telemetryClient.connect(8080, '127.0.0.1', () => {
        console.log('Connected to rt_json_network_bridge on Port 8080');
    });

    telemetryClient.on('data', (data) => {
        try {
            const rawPackets = data.toString().split('\n');
            rawPackets.forEach(packet => {
                if (!packet.trim()) return;
                const telemetryJson = JSON.parse(packet);
                
                // Broadcast validated telemetry arrays out to the operator interface windows
                wss.clients.forEach(client => {
                    if (client.readyState === WebSocket.OPEN) {
                        client.send(JSON.stringify(telemetryJson));
                    }
                });
            });
        } catch (err) {
            // Rejects corrupt surges or structural framing errors silently
        }
    });

    telemetryClient.on('close', () => {
        setTimeout(connectToCoreBridge, 2000); // Autonomic reconnect loop
    });

    telemetryClient.on('error', () => {});
}

connectToCoreBridge();
