#!/usr/bin/env bash
# Forward localhost TCP/88 to the research DC's explicit recovery NIC mapping.
set -euo pipefail
action="${1:-status}"
name="goad-lineage-kerberos-proxy"
case "$action" in
  start)
    if docker container inspect "$name" >/dev/null 2>&1; then
      echo "$name already exists" >&2
      exit 1
    fi
    if ! docker exec goad-lineage-dc03 netstat -ltn | rg -q ':18888 '; then
      docker exec goad-lineage-dc03 sh -c "printf 'hostfwd_add recovery tcp::18888-10.20.0.15:88\n' | nc -w 1 127.0.0.1 4444" >/dev/null
    fi
    dc_address="$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' goad-lineage-dc03)"
    docker run -d --name "$name" --network host --read-only --memory 128m \
      node:24.22.1-alpine node -e '
      const net = require("net");
      net.createServer(client => {
        const target = net.connect(18888, process.argv[1]);
        client.on("error", () => target.destroy());
        target.on("error", () => client.destroy());
        client.setTimeout(30000, () => client.destroy());
        client.pipe(target); target.pipe(client);
      }).listen(88, "127.0.0.2");
      ' "$dc_address"
    ;;
  stop)
    if docker container inspect "$name" >/dev/null 2>&1; then
      docker stop "$name"
      docker rm "$name"
    fi
    ;;
  status) docker ps -a --filter name="$name" --format '{{.Names}} {{.Status}}' ;;
  *) echo "Usage: $0 start|stop|status" >&2; exit 2 ;;
esac
