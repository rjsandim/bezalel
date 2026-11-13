#!/usr/bin/env bash
# Atalho nesta árvore para skills/issue-bot/scripts/issue_session.sh (a skill é autocontida).
exec bash "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/skills/issue-bot/scripts/issue_session.sh" "$@"
