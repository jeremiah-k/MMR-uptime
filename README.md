# MMR-uptime

Config usage:

```
community-plugins:
  uptime_plugin:
    active: true
    repository: https://github.com/leow149/MMR-uptime.git
    tag: main
    tracked_nodes:
      - "!1234abcd"
    offline_threshold: 1800
    alert_room_id: "!my_alert_room_id:example.org"
```
