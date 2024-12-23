# MMR-uptime

## Uptime Plugin for Meshtastic-Matrix Relay

This plugin is designed to work with the [Meshtastic-Matrix Relay](https://github.com/geoffwhittington/meshtastic-matrix-relay) project. It monitors specific nodes in a Meshtastic network and provides:

1. **Automatic Alerts**: Sends alerts to a Matrix room when a node exceeds a specified downtime threshold.
2. **Manual Status Checks**: Responds to the `!uptime` command in Matrix rooms to provide the current status of tracked nodes.

## Features
- Tracks the uptime of specific nodes in a Meshtastic network.
- Sends alerts when a node is offline beyond a configured threshold.
- Reports the uptime or downtime status of all tracked nodes on command.

## Requirements
- The [Meshtastic-Matrix Relay](https://github.com/geoffwhittington/meshtastic-matrix-relay) core program.

## Configuration

Add the following configuration to your config.yaml for the uptime plugin:

```yaml
...
community-plugins:
  uptime:
    active: true
    repository: https://github.com/leow149/MMR-uptime.git
    tag: main
    tracked_nodes:
      - "!node_id_1"
      - "!node_id_2"
    offline_threshold: 1800
    alert_room_id: "!my_alert_room_id:example.org"
...
```
  - Replace `!node_id_1` and `!node_id_2` with the IDs of the nodes you want to track
  - Set `offline_threshold` to the desired amount of seconds before alerting about downtime
  - Replace `!my_alert_room_id:example.org` with the Matrix Room ID that the alert should go to

## Usage

### Automatic Alerts
- The plugin will automatically monitor the configured nodes and send alerts to the Matrix room if any node exceeds the downtime threshold.

### Manual Status Check
- Send the `!uptime` command in a Matrix room to get the current status of all tracked nodes. The plugin will respond with:
  - **ONLINE**: The node's last seen time is within the threshold.
  - **OFFLINE**: The node has been offline for a duration exceeding the threshold.
  - **Never Seen**: The node has never reported uptime to the relay.

Example:
```plaintext
!uptime
```
Response:
```plaintext
Node !node_id_1: ONLINE, last seen 20.35 seconds ago
Node !node_id_2: OFFLINE for 310.25 seconds
```

## Acknowledgments
This plugin is designed to integrate seamlessly with the [Meshtastic-Matrix Relay](https://github.com/geoffwhittington/meshtastic-matrix-relay) project. Special thanks to the community for their support and contributions.
