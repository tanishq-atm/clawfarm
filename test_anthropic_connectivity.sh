#!/usr/bin/env bash
# Run this script **inside your VM terminal** to test Anthropic API connectivity.
# Usage: bash test_anthropic_connectivity.sh

set -e
echo "=============================================="
echo "  Anthropic connectivity test (run in VM)"
echo "=============================================="
echo ""
echo "=== 1. Where is this running? ==="
echo "  Hostname: $(hostname)"
echo "  User:     $(whoami)"
echo "  PWD:      $(pwd)"
echo "  (If this is your VM, you're in the right place.)"
echo ""

echo "=== 2. DNS: api.anthropic.com ==="
if getent hosts api.anthropic.com 2>/dev/null; then
  echo "  DNS: OK"
else
  echo "  DNS: FAIL (getent failed)"
  nslookup api.anthropic.com 2>&1 || true
fi
echo ""

echo "=== 3. Proxy environment ==="
for v in HTTP_PROXY HTTPS_PROXY NO_PROXY http_proxy https_proxy no_proxy; do
  eval "val=\$$v"
  [ -n "$val" ] && echo "  $v=$val"
done
[ -z "$HTTP_PROXY$HTTPS_PROXY$http_proxy$https_proxy" ] && echo "  (no proxy set)"
echo ""

echo "=== 4. HTTPS connection to api.anthropic.com (curl, 10s timeout) ==="
if curl -s -o /dev/null -w "  HTTP code: %{http_code}\n  Time: %{time_total}s\n" --connect-timeout 10 https://api.anthropic.com 2>&1; then
  echo "  Connection: OK (got response)"
else
  echo "  Connection: FAIL or timeout"
  echo "  Verbose try:"
  curl -v --connect-timeout 5 https://api.anthropic.com 2>&1 | head -30
fi
echo ""

echo "=== 5. Gateway process (OpenClaw) ==="
if pgrep -f openclaw-gateway >/dev/null 2>&1; then
  pid=$(pgrep -f openclaw-gateway | head -1)
  echo "  Gateway running, PID: $pid"
  echo "  Gateway proxy env:"
  tr '\0' '\n' < /proc/$pid/environ 2>/dev/null | grep -iE '^(HTTP_PROXY|HTTPS_PROXY|NO_PROXY)=' || echo "    (none)"
else
  echo "  Gateway not running"
fi
echo ""

echo "=============================================="
echo "  Done. Fix any FAILs above (DNS, proxy, firewall) then restart gateway."
echo "=============================================="
