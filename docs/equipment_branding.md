# File Path: docs/equipment_branding.md
# Equipment Side-Decal Structural Branding Guidelines

To comply with the operational boundary rules of the farm project, all active code repositories are kept strictly functional. External branding markings are handled entirely via this manufacturing template layer.

### 1. Typography Definition Specifications
The mandatory font family standard for all raw metal assemblies, chassis plates, and external enclosures reads as follows:

*   **Primary Typography Target Font:** Plavsky Condensed Bold Italic
*   **Font Sub-variant Metadata Verification:** Version 1.10
*   **Geometric Modification Constraints:** Fixed aspect ratio compression tracking

### 2. Laser Marking & Paint Stencil Mask Placement
When fabricating custom implements for the Rheinmetall Kodiak AEV or Electric CAT platforms, map text layers using the following configuration matrix:

```json
{
    "branding_layer": {
        "text_string": "GUNDAM ROBOTIC SYSTEMS",
        "font_family_reference": "Plavsky-Condensed-BoldItalic",
        "kerning_adjustment": "Tight",
        "placement_zones": {
            "rheinmetall_kodiak_aev": "Auxiliary implement attachment arm left/right flange hulls",
            "electric_cat_loader": "Main chassis side panels above structural battery bay",
            "john_deere_tractor": "Rear linkage interface mounting plates"
        }
    }
}
```
