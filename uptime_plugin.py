import time
import asyncio
from plugins.base_plugin import BasePlugin

class Plugin(BasePlugin):
    plugin_name = "uptime"

    @property
    def description(self):
        return "Tracks uptime of specific nodes, sends alerts when they exceed the downtime threshold, and responds to the !uptime command."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_last_seen = {}
        self.tracked_nodes = self.config.get("tracked_nodes", [])
        self.offline_threshold = self.config.get("offline_threshold", 1800)
        self.alert_sent = set()

        # New setting for which Matrix room to send OFFLINE alerts to
        self.alert_room_id = self.config.get("alert_room_id", None)
        if not self.alert_room_id:
            self.logger.warning(f"No alert_room_id specified in config for plugin '{self.plugin_name}'. "
                                "Offline alerts will not be sent to Matrix.")

    async def handle_meshtastic_message(self, packet, formatted_message, longname, meshnet_name):
        """
        Records last-seen time for any tracked node that sends a packet.
        Clears 'alert_sent' if the node is back online after being offline.
        """
        try:
            node_id = packet.get("fromId")
            if not isinstance(node_id, str):
                return False

            if node_id in self.tracked_nodes:
                self.node_last_seen[node_id] = time.time()
                if node_id in self.alert_sent:
                    self.alert_sent.discard(node_id)
            return True
        except Exception:
            return False

    async def monitor_nodes(self):
        """
        Periodically checks tracked nodes for downtime. If a node
        exceeds 'offline_threshold' seconds, an alert is sent to Matrix.
        """
        while True:
            current_time = time.time()

            # Only proceed if alert_room_id is configured
            if not self.alert_room_id:
                await asyncio.sleep(10)
                continue

            for node_id in self.tracked_nodes:
                last_seen = self.node_last_seen.get(node_id, None)
                if last_seen is None:
                    continue

                downtime = current_time - last_seen
                if downtime > self.offline_threshold and node_id not in self.alert_sent:
                    self.alert_sent.add(node_id)
                    try:
                        await self.send_matrix_message(
                            self.alert_room_id,
                            f"Alert: Node {node_id} is OFFLINE for {downtime:.2f} seconds!",
                            formatted=False
                        )
                    except Exception as e:
                        self.logger.error(f"Failed sending offline alert for node {node_id} to Matrix: {e}")

            await asyncio.sleep(10)

    async def handle_room_message(self, room, event, full_message):
        """
        Responds with a current uptime report if "!uptime" is in the message.
        """
        if "!uptime" in full_message:
            report = self.generate_uptime_report()
            try:
                await self.send_matrix_message(
                    room.room_id,
                    report,
                    formatted=False
                )
            except Exception as e:
                self.logger.error(f"Failed sending uptime report to Matrix: {e}")
            return True
        return False

    def generate_uptime_report(self):
        """
        Builds a multiline report of each tracked node's status
        (ONLINE vs. OFFLINE).
        """
        current_time = time.time()
        report_lines = []

        for node_id in self.tracked_nodes:
            last_seen = self.node_last_seen.get(node_id, None)
            if last_seen is None:
                report_lines.append(f"Node {node_id}: Never seen")
            else:
                downtime = current_time - last_seen
                if downtime > self.offline_threshold:
                    report_lines.append(f"Node {node_id}: OFFLINE for {downtime:.2f} seconds")
                else:
                    report_lines.append(f"Node {node_id}: ONLINE, last seen {downtime:.2f} seconds ago")

        return "\n".join(report_lines)

    def start(self):
        """
        If 'tracked_nodes' is non-empty, spins up an async task to check
        node downtime every 10 seconds. 
        """
        if not self.tracked_nodes:
            return
        asyncio.create_task(self.monitor_nodes())

    def stop(self):
        """
        Cleanup or teardown logic if needed. 
        """
        pass
