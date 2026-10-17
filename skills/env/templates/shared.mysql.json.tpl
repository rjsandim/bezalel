{
  "name": ${compose_project},
  "services": {
    "mysql": {
      "image": ${image}, "container_name": ${hostname}, "restart": "unless-stopped",
      "env_file": [${admin_file}],
      "ports": [${port_mapping}],
      "volumes": ["data:/var/lib/mysql"],
      "networks": ["database"],
      "healthcheck": {
        "test": ["CMD-SHELL", "MYSQL_PWD=$$MYSQL_ROOT_PASSWORD mysql -uroot -e 'SELECT 1' >/dev/null 2>&1"],
        "interval": "3s", "timeout": "5s", "retries": 60
      }
    }
  },
  "volumes": {"data": {"name": ${volume}}},
  "networks": {"database": {"name": ${network}}}
}
