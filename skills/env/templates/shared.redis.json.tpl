{
  "name": ${compose_project},
  "services": {
    "redis": {
      "image": ${image}, "container_name": ${hostname}, "restart": "unless-stopped",
      "env_file": [${admin_file}], "ports": [${port_mapping}],
      "volumes": ["data:/data", ${bootstrap_mount}], "networks": ["redis"],
      "command": ["sh", "-ec", "if [ ! -f /data/users.acl ]; then cp /envstack-bootstrap.acl /data/users.acl; fi; exec docker-entrypoint.sh redis-server --aclfile /data/users.acl --appendonly yes --databases \"$$1\"", "redis", ${databases}],
      "healthcheck": {
        "test": ["CMD-SHELL", "redis-cli --user envstack-admin ping | grep -qx PONG"],
        "interval": "3s", "timeout": "5s", "retries": 30
      }
    }
  },
  "volumes": {"data": {"name": ${volume}}},
  "networks": {"redis": {"name": ${network}}}
}
