# Port Scanner

A couple of port scanners I built to understand how scanning actually works under
the hood, instead of just firing `nmap` and trusting the output. There are two
versions that attack the same problem from different angles:

- **`portscan.py`** — a TCP *connect* scanner built on plain Python sockets. It
  opens a full connection to each port with `connect_ex()` and reports the ones
  that answer. Runs the ports concurrently with a `ThreadPoolExecutor`.
- **`stealth_portscan.py`** — a half-open *SYN* scanner built with Scapy. It
  sends a raw SYN packet and, if the port replies with SYN/ACK, marks it open and
  immediately sends an RST to tear the connection down before the handshake
  completes. Needs root because it crafts raw packets.

It's a learning project, not an nmap replacement — the goal was to really
understand the TCP handshake, socket timeouts and threading.

## Requirements

- Python 3.9+
- `portscan.py` uses **only the standard library** — nothing to install.
- `stealth_portscan.py` needs **Scapy** and **root** privileges (raw sockets).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### TCP connect scanner

```bash
python portscan.py <ip> [options]
```

| Option | Description |
| --- | --- |
| `ip` | Target IP address (required) |
| `-ap`, `--all_port` | Scan the full range, ports 1–65535 |
| `-tp`, `--top_ports` | Scan a short list of common ports |
| `-t`, `--time` | Socket timeout in seconds (default: `0.5`) |

With no flags it scans ports 1–1024.

```bash
# Common ports, with a slightly longer timeout
python portscan.py 192.168.1.10 -tp -t 1.0
```

```
=======Iniciando escaneo=======
[+] Puerto 22 ABIERTO
[+] Puerto 80 ABIERTO
[+] Puerto 443 ABIERTO

Tiempo total: 0.42
=========Fin del escaneo=========
```

### SYN (half-open) scanner

```bash
sudo python stealth_portscan.py <ip> [-tp]
```

| Option | Description |
| --- | --- |
| `ip` | Target IP address (required) |
| `-tp`, `--top_ports` | Scan common ports instead of the full range |

Without `-tp` it sweeps the full 1–65535 range. Scapy opens a sniffer per packet,
so the worker count is kept low on purpose to avoid flooding the host.

## How the SYN scan works

A normal TCP connection is a three-way handshake: SYN → SYN/ACK → ACK. This
scanner stops after the second step: it sends the SYN, reads the reply, and if
the port is open (SYN/ACK) it answers with an RST instead of an ACK, so the
connection is never fully established. That's why it's called "half-open" or
"stealth" — it leaves a lighter trace than a full connect.

## Notes and limitations

- Scans one target host at a time.
- Timing depends on the timeout you pass and your network.
- Error handling is intentionally minimal — this is a study tool.

## Disclaimer

Only scan machines you own or have explicit, written permission to test.
Unauthorized port scanning can be illegal in many jurisdictions.
