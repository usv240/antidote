#!/usr/bin/env bash
# Run Antidote's surveillance brief inside an NVIDIA OpenShell sandbox. The medico-legal register is sensitive, so
# the sandbox may reach exactly one service: the Nebius Token Factory model endpoint. No Tavily, no web, nothing else.
# The real API key never enters the sandbox; OpenShell substitutes it at the allowed host only.
# Requires: openshell + openshell-gateway 0.1.4 on PATH, Docker reachable, NEBIUS_API_KEY exported. Same gateway
# setup as Sieve (see sieve/infra/openshell/DEMONSTRATED.md for the WSL2 + Docker Desktop details).
set -euo pipefail
NAME=${SANDBOX_NAME:-antidote}
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
TLS_DIR=${OPENSHELL_LOCAL_TLS_DIR:-$HOME/.local/state/openshell/tls}
CFG=${OPENSHELL_GATEWAY_CONFIG:-$HOME/.config/openshell/gateway.toml}
PY=/workspace/.venv/bin/python   # venv interpreter; its resolved binary /usr/local/bin/python3.12 is what the policy matches

if ! openshell status >/dev/null 2>&1; then
  mkdir -p "$TLS_DIR" "$(dirname "$CFG")"
  [ -f "$TLS_DIR/ca.crt" ] || openshell-gateway generate-certs --output-dir "$TLS_DIR" --server-san host.openshell.internal --server-san host.docker.internal --server-san 127.0.0.1
  [ -f "$CFG" ] || cp "$HERE/gateway.toml" "$CFG"
  (OPENSHELL_LOCAL_TLS_DIR="$TLS_DIR" OPENSHELL_GATEWAY_CONFIG="$CFG" nohup openshell-gateway >"$HOME/.openshell-gateway.log" 2>&1 &)
  for _ in $(seq 1 30); do openshell status >/dev/null 2>&1 && break; sleep 2; done
  openshell status >/dev/null 2>&1 || openshell gateway add https://127.0.0.1:17670 --local --name openshell >/dev/null || true
fi
openshell status | grep -E "Status|Authentication"

docker build -q -t antidote-agent:latest -f "$HERE/Dockerfile.agent" "$REPO"

openshell profile lint -f "$HERE/profiles/nebius-token-factory.yaml" >/dev/null && openshell profile import -f "$HERE/profiles/nebius-token-factory.yaml" 2>/dev/null || true
openshell provider create --name nebius --type nebius-token-factory --credential NEBIUS_API_KEY 2>/dev/null || true

openshell sandbox delete "$NAME" >/dev/null 2>&1 || true; sleep 2
(openshell sandbox create --name "$NAME" --from antidote-agent:latest --no-auto-providers -- sleep infinity >/dev/null 2>&1 &)
for _ in $(seq 1 30); do openshell sandbox list 2>/dev/null | grep -q "^$NAME .*Ready" && break; sleep 2; done

probe() {
  openshell sandbox exec --name "$NAME" -- $PY -c "import httpx
for host in ['https://api.tavily.com', 'https://example.com', 'https://api.tokenfactory.nebius.com/v1/models']:
    try: print(host, '->', httpx.get(host, timeout=8).status_code)
    except Exception as e: print(host, '-> blocked:', type(e).__name__)"
}
echo "== before any provider (deny by default)"; probe
openshell sandbox provider attach "$NAME" nebius --wait --timeout 60
echo "== after attaching only the Token Factory provider"; probe
openshell sandbox exec --name "$NAME" -- sh -c 'env | grep -E "^NEBIUS_API_KEY=" | sed -E "s/=(.{6}).*/=\1... (placeholder)/"'

echo "== surveillance brief inside the sandbox"
openshell sandbox exec --name "$NAME" -- $PY -c "
import sys
sys.path[:0] = ['/workspace/packages/core','/workspace/packages/llm','/workspace/packages/retrieval','/workspace/packages/rules']
from pathlib import Path
from antidote_core import ChemRegistry
from antidote_core.surveillance import build_brief, load_rows
from antidote_llm import Ledger, TokenFactoryClient
from antidote_rules import load_rules
led = Ledger('/tmp/ledger.db')
rows = load_rows(Path('/workspace/data/mlc_register.jsonl'), Path('/workspace/data/samples/register_demo.jsonl'))
out = build_brief(TokenFactoryClient(ledger=led), rows, ChemRegistry(), load_rules('/workspace/packages/rules/antidote_rules/antidote.yaml'), trace_id='sandbox')
print('INSIDE OPENSHELL SANDBOX: alerts', [a['type'] for a in out['alerts']], '| case reports read', out['case_reports_read'], '| tokens', out['input_tokens_approx'])
print('headline:', out['brief']['headline'])
for row in led.trace('sandbox'): print('  trace', row['model'], row['purpose'], row['tokens_in'], f\"\${row['usd']:.4f}\")"
