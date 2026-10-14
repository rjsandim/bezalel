{
  "name": ${compose_project},
  "services": {
    "postgres": {
      "image": ${image}, "container_name": ${hostname}, "restart": "unless-stopped",
      "env_file": [${admin_file}],
      "ports": [${port_mapping}],
      "volumes": [${data_mount}],
      "networks": ["database"],
      "healthcheck": {
        "test": ["CMD-SHELL", "pg_isready -U postgres -d postgres"],
        "interval": "3s", "timeout": "5s", "retries": 60
      }
    }
  },
  "volumes": {"data": {"name": ${volume}}},
  "networks": {"database": {"name": ${network}}}
}
