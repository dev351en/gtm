# Geyser Bedrock Resource Packs Directory (`plugins/Geyser-Spigot/packs`)

## How Server-Side Auto-Send Works for PE & Bedrock:
1. Any `.mcpack` or `.zip` file placed in this folder is **automatically downloaded and applied** by Bedrock and Pocket Edition (PE) clients when they connect to the server!
2. In `plugins/Geyser-Spigot/config.yml`, `force-resource-packs: true` is configured so the pack is **mandatory for all PE/Bedrock players**.

## Where to get the Fresh Animations Bedrock `.mcpack`:
- **Fresh Animations Bedrock (Mob Animations)**:
  Download the `.mcpack` from: https://mcpedl.com/fresh-animations-bedrock/ or https://modbay.org/textures/
- **Fresh Moves Bedrock (Player Animations)**:
  Download the `.mcpack` from: https://mcpedl.com/fresh-player-animations-bedrock/

Drop the downloaded `.mcpack` file directly into this `packs/` folder, restart the server, and Geyser will auto-send it to every mobile player on join!
