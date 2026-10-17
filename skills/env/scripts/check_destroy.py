"""Read-only ownership checks before Compose may remove an environment's volumes."""
import json
import subprocess
import sys


def docker_output(*arguments):
    return subprocess.check_output(["docker", *arguments], text=True, stderr=subprocess.DEVNULL)


def check(compose_file, expected_project):
    config = json.loads(docker_output("compose", "-f", compose_file, "config", "--format", "json"))
    if config.get("name") != expected_project:
        raise ValueError("Projeto Compose difere do ambiente confirmado.")
    volumes = {
        spec["name"] for spec in config.get("volumes", {}).values()
        if not spec.get("external")
    }
    existing = set(docker_output("volume", "ls", "--format", "{{.Name}}").splitlines())
    for volume in sorted(volumes & existing):
        labels = json.loads(docker_output("volume", "inspect", volume, "--format", "{{json .Labels}}")) or {}
        if labels.get("com.docker.compose.project") != expected_project:
            raise ValueError("Volume sem propriedade exclusiva comprovada; preservado.")
    projection = '{"project":{{json (index .Config.Labels "com.docker.compose.project")}},"mounts":{{json .Mounts}}}'
    for container in docker_output("ps", "-aq").splitlines():
        details = json.loads(docker_output("inspect", "--format", projection, container))
        if details.get("project") != expected_project:
            if any(mount.get("Name") in volumes for mount in details.get("mounts", [])):
                raise ValueError("Volume usado por outro container; nenhuma remocao autorizada.")


if __name__ == "__main__":
    try:
        check(*sys.argv[1:])
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError):
        print("Nao foi possivel comprovar a propriedade exclusiva dos volumes/Compose. Remocao cancelada.", file=sys.stderr)
        sys.exit(1)
