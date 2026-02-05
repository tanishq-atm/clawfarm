# Make OpenClaw → Anthropic work from this VM

This VM cannot reach `api.anthropic.com:443` directly. Use an **SSH reverse tunnel** from a machine that has internet (your laptop, exe.dev host, etc.) so API traffic goes through that machine.

## One-time setup on the VM (already done or run once)

1. **Point api.anthropic.com to localhost** (so gateway uses the tunnel):
   ```bash
   sudo sed -i 's/160.79.104.10 api.anthropic.com/127.0.0.1 api.anthropic.com/' /etc/hosts
   grep api.anthropic.com /etc/hosts   # should show 127.0.0.1
   ```

2. **Start the local forwarder** (forwards VM port 443 → tunnel port 9443):
   ```bash
   sudo systemctl start anthropic-tunnel-forward
   sudo systemctl enable anthropic-tunnel-forward  # optional: start on boot
   ```

## Every time you want to use OpenClaw

1. **From a machine WITH internet** (your laptop, etc.), open an SSH session to this VM and create the reverse tunnel. Keep this terminal open:
   ```bash
   ssh -o ServerAliveInterval=60 -R 9443:api.anthropic.com:443 exedev@ITEM_COMPILE_IP
   ```
   Replace `ITEM_COMPILE_IP` with this VM’s IP or hostname (e.g. `10.42.0.87` or `item-compile`).

2. **On the VM**, restart the gateway so it uses the tunnel:
   ```bash
   systemctl --user restart openclaw-gateway
   ```

3. Send a message in OpenClaw; you should get a reply.

## To stop using the tunnel

- Close the SSH session (the one with `-R 9443:...`).
- To use direct IP again (if network is fixed later):
  ```bash
  sudo sed -i 's/127.0.0.1 api.anthropic.com/160.79.104.10 api.anthropic.com/' /etc/hosts
  sudo systemctl stop anthropic-tunnel-forward
  systemctl --user restart openclaw-gateway
  ```
