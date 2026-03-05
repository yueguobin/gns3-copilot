# SPDX-License-Identifier: GPL-3.0-or-later
#
# GNS3-Copilot - AI-powered Network Lab Assistant for GNS3
#
# This file is part of GNS3-Copilot project.
#
# GNS3-Copilot is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# GNS3-Copilot is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNS3-Copilot. If not, see <https://www.gnu.org/licenses/>.
#
# Copyright (C) 2025 Guobin Yue
# Author: Guobin Yue
#
# Project Home: https://github.com/yueguobin/gns3-copilot
#

"""
Drawing tool prompt for GNS3 area annotation creation.

This module provides specialized prompts for guiding the AI in using GNS3 drawing tools
to create visual area annotations for network topology.
"""


def get_drawing_prompt() -> str:
    """
    Get the drawing tool usage prompt for the AI agent.

    Returns:
        str: A comprehensive prompt with examples and best practices for drawing tools.
    """
    return """
## GNS3 Drawing Tools

Use `create_gns3_area_drawing` to create visual area annotations for network devices.

### When to Use

Create annotations when configuring routing protocols or grouping devices:
- OSPF areas, EIGRP AS, BGP AS
- Logical isolation (VRF, VLAN, MSTP)
- High availability groups (VRRP, HSRP)
- Any 2 devices in the same logical domain

### Tool Parameters

- `project_id`: GNS3 project UUID
- `area_name`: Area/group name (e.g., "Area 0", "BGP AS 65001", "VRF A", "VLAN 10")
- `node_names`: Exactly 2 node names (e.g., ["R-1", "R-2"])

**Important**: Only supports exactly 2 nodes.

### Usage Examples

```
User: Configure OSPF area 0 on R-1 and R-2
→ create_gns3_area_drawing(project_id="xxx", area_name="Area 0", node_names=["R-1", "R-2"])

User: Create VLAN 10 for SW-1 and SW-2
→ create_gns3_area_drawing(project_id="xxx", area_name="VLAN 10", node_names=["SW-1", "SW-2"])

User: Configure VRRP group 1 on R-1 and R-2
→ create_gns3_area_drawing(project_id="xxx", area_name="VRRP Group 1", node_names=["R-1", "R-2"])
```

### Color Scheme (Business Professional)

The tool automatically selects colors based on keywords in area_name:

| Color | Semantics | Keywords | Examples |
|-------|-----------|----------|----------|
| `#2980B9` (Blue) | Core/Backbone | BGP, AS, AREA 0, BACKBONE | "BGP AS 65001", "Area 0" |
| `#5AA9DD` (Light Blue) | Normal Areas | AREA, LEVEL, OSPF, IS-IS, RIP, EIGRP | "Area 1", "Level-1" |
| `#9B59B6` (Purple) | Logical Isolation | VRF, VLAN, MSTP, VXLAN, MPLS | "VRF A", "VLAN 10" |
| `#E67E22` (Orange) | Management | MGMT, OOB, MANAGEMENT, INFRA | "MGMT", "OOB Network" |
| `#F39C12` (Bright Orange) | High Availability | VRRP, HSRP, HA, STACK, M-LAG, GLBP | "VRRP Group 1", "Core Stack" |
| `#E74C3C` (Bright Red) | External/Boundary | INET, OUT, EXTERNAL, INTERNET, DMZ | "Internet", "DMZ" |
| `#2ECC71` (Bright Green) | Security/Trusted | TRUST, SECURE, SAFE, DATA CENTER, SECURITY, VPN, IPSEC | "Trust Zone", "Data Center" |
| `#00CED1` (Cyan) | Cloud/Tunnel | GRE, IPSEC, VPN, TUNNEL, CLOUD, AWS, AZURE | "GRE Tunnel", "Cloud Provider" |

**Default**: Uses gray (`#808B96`) for labels without matching keywords.

### Best Practices

1. Complete configuration before creating annotations
2. Use concise names: "Area 0" not "OSPF Backbone Area Zero"
3. Verify configuration success with display commands first
4. Inform user when creating visual annotations

### Error Handling

If drawing fails:
- Verify node names are correct
- Ensure exactly 2 node names are provided
- Check project_id is valid
- Report error and continue with other tasks

"""
