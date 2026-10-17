#!/usr/bin/env python3
"""Atualiza somente importações intocadas; adaptações nunca entram na seleção."""
import argparse
import copy
from pathlib import Path
import sys
import tempfile

from distribution import (DistributionError, files, fingerprints, git, git_files,
                          inside, json_bytes, read_json, replace_files)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = '.bezalel/upstream.json'


def synchronize(root, upstream, revision, apply=False):
    manifest_path = inside(root, MANIFEST)
    manifest = read_json(manifest_path)
    if manifest.get('schema_version') != 1:
        raise DistributionError('Versão de origem não suportada.')
    if set(manifest['skills']) & set(manifest.get('excluded_adaptations', ['pr-audit', 'iss-audit'])):
        raise DistributionError('Uma adaptação está indevidamente na seleção automática.')
    revision = git(upstream, 'rev-parse', '--verify', revision + '^{commit}').decode().strip()
    updated = copy.deepcopy(manifest)
    before, after = {}, {}
    report = {'revision': revision, 'updated': [], 'unchanged': [], 'protected': [], 'errors': []}
    for name, entry in manifest['skills'].items():
        directory = inside(root, 'skills/' + name)
        current = files(directory)
        if fingerprints(current) != entry['files']:
            report['protected'].append(name)
            continue
        try:
            incoming = git_files(upstream, revision, name)
            for path in entry.get('preserve', []):
                incoming[path] = current[path]
            for path, mode in entry.get('mode_overrides', {}).items():
                if path in incoming:
                    incoming[path] = (incoming[path][0], mode)
        except DistributionError:
            report['errors'].append(name)
            continue
        if incoming == current:
            report['unchanged'].append(name)
            continue
        report['updated'].append(name)
        updated['skills'][name]['revision'] = revision
        updated['skills'][name]['files'] = fingerprints(incoming)
        before.update({'skills/' + name + '/' + p: v for p, v in current.items()})
        after.update({'skills/' + name + '/' + p: v for p, v in incoming.items()})
    if report['errors']:
        raise DistributionError('Upstream incompatível em: ' + ', '.join(report['errors']) + '. Nada foi alterado.')
    if apply and report['updated']:
        before[MANIFEST] = (manifest_path.read_bytes(), 0o644)
        after[MANIFEST] = (json_bytes(updated), 0o644)
        replace_files(root, before, after)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, help='Clone local para testes ou revisão; sem fetch implícito.')
    parser.add_argument('--revision', default='HEAD')
    parser.add_argument('--apply', action='store_true', help='Gravar a proposta local, sem commit/push.')
    args = parser.parse_args()
    try:
        with tempfile.TemporaryDirectory(prefix='bezalel-upstream-') as temp:
            upstream = args.upstream
            if upstream is None:
                manifest = read_json(ROOT / MANIFEST)
                upstream = Path(temp) / 'source'
                git(temp, 'clone', '--quiet', '--no-checkout', '--depth=1',
                    '--branch', manifest['branch'], '--', manifest['repository'], str(upstream))
            report = synchronize(ROOT, upstream, args.revision, args.apply)
            print(json_bytes(report).decode(), end='')
        return 0
    except (DistributionError, OSError, ValueError, KeyError) as error:
        print('Atualização não concluída: ' + (str(error) if isinstance(error, DistributionError) else 'origem ou configuração inválida.'), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
