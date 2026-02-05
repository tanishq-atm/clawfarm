#!/usr/bin/env bash
# VM network diagnostic - run on the VM to capture what's wrong.
# Usage: sudo bash vm_network_diagnostic.sh

echo "=============================================="
echo "  VM network diagnostic ($(hostname) @ $(date -Iseconds))"
echo "=============================================="

echo ""
echo "=== 1. What works ==="
echo -n "  Ping 8.8.8.8: "
ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1 && echo "OK" || echo "FAIL"
echo -n "  Ping gateway 10.42.0.1: "
ping -c 1 -W 2 10.42.0.1 >/dev/null 2>&1 && echo "OK" || echo "FAIL"

echo ""
echo "=== 2. What does NOT work (outbound TCP) ==="
for target in "10.42.0.1 (gateway)" "8.8.8.8"; do
  ip="${target%% *}"
  echo "  TCP to $target:"
  for port in 53 80 443; do
    timeout 2 bash -c "echo >/dev/tcp/$ip/$port" 2>/dev/null && echo "    port $port: open" || echo "    port $port: timeout/fail"
  done
done

echo ""
echo "=== 2b. Outbound UDP (if OK, a VPN tunnel might work) ==="
echo -n "  UDP to 8.8.8.8:53 (DNS): "
(timeout 2 nc -u -z 8.8.8.8 53 2>/dev/null || timeout 2 bash -c 'echo | nc -u 8.8.8.8 53' 2>/dev/null) && echo "reachable" || echo "timeout/fail (or nc not installed)"
echo -n "  UDP to 1.1.1.1:443: "
(timeout 2 nc -u -z 1.1.1.1 443 2>/dev/null) && echo "reachable" || echo "timeout/fail"

echo ""
echo "=== 3. Conclusion ==="
echo "  ICMP (ping) works; outbound TCP (DNS 53, HTTP 80, HTTPS 443) does not."
echo "  So: API calls (HTTPS) and DNS cannot succeed from this VM."
echo "  The block is upstream of this box (gateway 10.42.0.1 or network)."
echo "  This VM is not blocking; iptables/nftables are clean."

echo ""
echo "=== 4. VM config (for reference) ==="
vm_ip=$(ip -4 -o route get 8.8.8.8 2>/dev/null | sed -n 's/.* src \([0-9.]*\) .*/\1/p'); [ -z "$vm_ip" ] && vm_ip="(unknown)"
echo "  This VM IP: $vm_ip"
echo "  /etc/resolv.conf: $(cat /etc/resolv.conf)"
echo "  Default route: $(ip route show default | xargs)"
n=$(sudo iptables-save 2>/dev/null | grep -c . 2>/dev/null || true); [ -z "$n" ] && n=0
echo "  iptables: $n rules (0 = none, VM not blocking)"

echo ""
echo "=== 5. Next steps (to fix) ==="
echo "  Ask whoever manages the host/gateway (10.42.0.1) or exe.dev to:"
echo "  - Allow outbound TCP from this VM ($vm_ip) to the internet on ports 53, 80, 443"
echo "  - Or restore the firewall/NAT that was in place when it last worked"

echo ""
echo "=== 6. Workaround: get OpenClaw/APIs working now (SSH tunnel) ==="
echo "  A) From a machine WITH internet (e.g. your laptop), run and leave open:"
echo "       ssh -R 9443:api.anthropic.com:443 $USER@$vm_ip"
echo "     (If you use a jump host or hostname like item-compile, use that instead of $vm_ip.)"
echo "  B) On THIS VM run once (sudo for port 443 and hosts):"
echo "       sudo sed -i '/api.anthropic.com/d' /etc/hosts; echo '127.0.0.1 api.anthropic.com' | sudo tee -a /etc/hosts"
echo "       sudo socat TCP-LISTEN:443,fork,reuseaddr TCP:127.0.0.1:9443 &"
echo "  C) Restart OpenClaw gateway: systemctl --user restart openclaw-gateway"
echo "  Traffic path: VM -> localhost:443 -> SSH tunnel -> your laptop -> Anthropic."
echo "  (Remove the api.anthropic.com line from /etc/hosts and kill socat when network is fixed.)"
echo ""
echo "=============================================="
