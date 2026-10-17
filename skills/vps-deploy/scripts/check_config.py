#!/usr/bin/env python3
"""Validate one project's local configuration without network or write access."""

import argparse
import ipaddress
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


class ConfigError(ValueError):
    """A safe, user-facing configuration error without input values."""


def validate_url(value):
    if not isinstance(value, str) or not value or re.search(r"\s", value):
        raise ConfigError("Informe uma URL válida para a instância no arquivo local.")
    try:
        url = urlsplit(value)
        host = url.hostname
        port = url.port
        if not host or url.username is not None or url.password is not None:
            raise ValueError
        if url.query or url.fragment or (port is not None and port == 0):
            raise ValueError
        if any(ord(char) < 32 or char in "\\<>" for char in value):
            raise ValueError
        host = host.lower().rstrip(".")
        if host == "example.invalid" or host.endswith(".invalid") or host in {
            "example.com", "example.org", "example.net"
        } or any(host.endswith("." + domain) for domain in ["example.com", "example.org", "example.net"]):
            raise ValueError
        try:
            loopback = ipaddress.ip_address(host).is_loopback
        except ValueError:
            loopback = host == "localhost"
            if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?", host):
                raise ValueError
        if url.scheme != "https" and not (url.scheme == "http" and loopback):
            raise ValueError
    except ValueError:
        raise ConfigError("A URL precisa usar HTTPS (ou HTTP em loopback), sem credenciais, placeholders, query ou fragmento.") from None


def validate_project(project, environment):
    project = Path(project)
    if not project.is_dir():
        raise ConfigError("O diretório do projeto não existe.")
    directory = project / ".bezalel"
    config_path = directory / "vps-deploy.local.json"
    if directory.is_symlink() or config_path.is_symlink():
        raise ConfigError("Use um arquivo local próprio deste projeto, sem symlink.")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError("Falta .bezalel/vps-deploy.local.json neste projeto. Configure localmente a partir do modelo, sem inserir token no JSON.") from None
    except (OSError, UnicodeError, ValueError):
        raise ConfigError("Não foi possível ler uma configuração JSON válida neste projeto.") from None
    if not isinstance(config, dict) or set(config) - {"coolify_base_url", "ssh_target"}:
        raise ConfigError("A configuração aceita somente coolify_base_url e ssh_target; não armazene credenciais no JSON.")
    validate_url(config.get("coolify_base_url"))
    ssh_target = config.get("ssh_target", "")
    if not isinstance(ssh_target, str) or (ssh_target and not re.fullmatch(
        r"(?:[A-Za-z_][A-Za-z0-9_.-]*@)?[A-Za-z0-9][A-Za-z0-9_.-]*", ssh_target
    )):
        raise ConfigError("ssh_target deve ser um alias ou usuario@host, sem opções ou comandos; pode ficar vazio.")
    token = environment.get("COOLIFY_API_TOKEN", "")
    if not token or not token.strip():
        raise ConfigError("COOLIFY_API_TOKEN está ausente. Configure-o no processo pelo seu gerenciador de segredos; não envie o valor no chat.")
    if any(ord(char) < 32 or ord(char) == 127 for char in token):
        raise ConfigError("COOLIFY_API_TOKEN contém caracteres de controle e não pode ser usado como cabeçalho.")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path, help="Projeto alvo explícito; não usa configuração global.")
    args = parser.parse_args(argv)
    try:
        validate_project(args.project, os.environ)
    except ConfigError as error:
        print(str(error), file=sys.stderr)
        return 1
    print("Configuração local e presença de COOLIFY_API_TOKEN verificadas; autenticação não testada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
