#include "imgui.h"
#include <map>
#include <string>

// Structure mirroring raw telemetry for heavy machinery and structures
struct HeavyAsset {
    std::string AssetName;
    uint8_t HexState;       // 16-State Hexadecimal (0x0 to 0xF)
    float CoreVoltage;      // 0.0V to 1.0V mapping
    bool SafeguardLoop;     // Edwards FireWorks loop status (NC)
};

void RenderSovereignTelemetryConsole(std::map<std::string, HeavyAsset>& ActiveFleet) {
    ImGui::Begin("UNIVAC IX - Core Telemetry Register Grid");
    
    ImGui::Text("System Framework Origin Status: NOMINAL OPERATIONS (±2mV Window)");
    ImGui::Separator();

    if (ImGui::BeginTable("FleetTable", 5, ImGuiTableFlags_Borders | ImGuiTableFlags_RowBg)) {
        ImGui::TableSetupColumn("Asset Identifier / ID");
        ImGui::TableSetupColumn("Hex State");
        ImGui::TableSetupColumn("Bus Voltage");
        ImGui::TableSetupColumn("Edwards Safety NC Loop");
        ImGui::TableSetupColumn("Emergency Command");
        ImGui::TableHeadersRow();

        for (auto& [id, asset] : ActiveFleet) {
            ImGui::TableNextRow();
            
            // Asset ID
            ImGui::TableSetColumnIndex(0);
            ImGui::Text("%s", asset.AssetName.c_str());

            // Hex State Engine
            ImGui::TableSetColumnIndex(1);
            if (asset.HexState == 0x0) {
                ImGui::TextColored(ImVec4(1.0f, 0.0f, 0.0f, 1.0f), "0x0 [HARD SHUTDOWN]");
            } else {
                ImGui::Text("0x%X", asset.HexState);
            }

            // Analog Voltage Readout
            ImGui::TableSetColumnIndex(2);
            ImGui::Text("%.4f V", asset.CoreVoltage);

            // Edwards Safety Loop State
            ImGui::TableSetColumnIndex(3);
            if (asset.SafeguardLoop) {
                ImGui::TextColored(ImVec4(0.0f, 1.0f, 0.0f, 1.0f), "CLOSED [SAFE]");
            } else {
                ImGui::TextColored(ImVec4(1.0f, 0.0f, 0.0f, 1.0f), "OPEN [BREACHED]");
            }

            // Direct Manual Hardware Overrides
            ImGui::TableSetColumnIndex(4);
            std::string buttonLabel = "FORCE NC DROP##" + id;
            if (ImGui::Button(buttonLabel.c_str())) {
                asset.HexState = 0x0;
                asset.SafeguardLoop = false; // Mechanically pop loop OPEN instantly
            }
        }
        ImGui::EndTable();
    }
    ImGui::End();
}
