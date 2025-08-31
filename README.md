# Website Monitor

A lightweight Python-based monitor for websites and hosts. Supports
ICMP, TCP, and HTTP checks with simple syntax. Perfect for quick uptime
checks or monitoring multiple targets.

## Features

-   📡 **ICMP Ping** --- Simple host reachability check (requires
    `ping3`)
-   🔌 **TCP Connect** --- Check host with `host:port` syntax
-   🌐 **HTTP Check** --- Verify site availability with status codes
-   🖥️ **Multi-target Support** --- Pass multiple domains or IPs at once
-   ⚡ **Fast & Async** --- Runs checks concurrently for speed

## Installation

1.  Clone or download the project
2.  Install dependencies:

``` bash
pip install -r requirements.txt
```

## Quick Start

``` bash
# ICMP check (requires root on some systems), ICMP is the default, so you don't need --mode option
python main.py --targets example.com,1.1.1.1

# TCP check with ports inline
python main.py --mode tcp --targets github.com:443,google.com:21,1.1.1.1:22

# HTTP check
python main.py --mode http --targets example.com,https://example.org/health
```

## Command Line Options

### Required

-   `--targets TARGET/S` - Comma-separated list of hosts or URLs

### Optional

-   `--mode icmp|tcp|http` - Which check to perform (default: ICMP)
-   `--timeout N` - Timeout in seconds (default: 3.0)
-   `--delay N` - Time between requests in seconds (default: 1.0)

## Usage Examples

### Ping a single host

``` bash
python main.py --targets 1.1.1.1
```

### Ping two hosts with ICMP

``` bash
python main.py --targets 1.1.1.1,8.8.8.8
```

### Check multiple ports with TCP

``` bash
python main.py --mode tcp --targets github.com:22,github.com:443
```

### Verify web endpoints

``` bash
python main.py --mode http --targets https://example.com,api.example.org/health
```

Remember that the script will continue to send requests until you press CTRL+C

## Output

Console output shows:
- Target
- Mode
- Status (UP/DOWN)
- Latency
- Error details (if any)

Example:

    example.com                    ICMP  UP    9.5 ms
    example.net                    ICMP  UP    11.1 ms
    example.edu                    ICMP  DOWN  -
    ============================================================
    example.com                    ICMP  UP    9.2 ms
    example.net                    ICMP  UP    6.7 ms
    example.edu                    ICMP  DOWN  -
    ============================================================
    example.com                    ICMP  UP    7.9 ms
    example.net                    ICMP  UP    16.0 ms
    example.edu                    ICMP  DOWN  -
    ============================================================

## Dependencies

-   **ping3** - For ICMP checks
-   **aiohttp** - For HTTP checks

## Note
Code is fully written by me.\
Comments were generated with the help of AI (Claude 4 Sonnet).