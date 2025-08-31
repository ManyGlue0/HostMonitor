import sys
import time
import ping3
import asyncio
import aiohttp
import argparse

from urllib.parse import urlparse
from typing import Optional, Tuple


separator = "="*60


async def icmp_ping(host: str, timeout: float) -> Tuple[Optional[float], Optional[str]]:
    """Perform ICMP ping using ping3 library"""
    try:
        ping3.EXCEPTIONS = True
        rtt = await asyncio.to_thread(ping3.ping, host, timeout=timeout, unit='ms')
        if rtt is None:
            return None, "timeout"
        return float(rtt), None
    except Exception as e:
        return None, str(e)


async def tcp_ping(host: str, port: int, timeout: float) -> Tuple[Optional[float], Optional[str]]:
    """Test TCP connectivity by opening a connection"""
    start = time.perf_counter()
    try:
        conn = asyncio.open_connection(host=host, port=port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        rtt = (time.perf_counter() - start) * 1000.0  # Convert to ms
        
        # Clean connection close
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass  # Ignore close errors
        
        return rtt, None
    except Exception as e:
        return None, str(e)


async def http_check(session: aiohttp.ClientSession, url: str, timeout: float) -> Tuple[Optional[float], Optional[str]]:
    """Perform HTTP request and measure response time"""
    try:
        start = time.perf_counter()
        async with session.get(url, timeout=timeout) as resp:
            await resp.read()  # Ensure full response is received
            rtt = (time.perf_counter() - start) * 1000.0  # Convert to ms
            
            # Consider 2xx and 3xx as successful
            if 200 <= resp.status < 400:
                return rtt, None
            return None, f"HTTP {resp.status}"
    except Exception as e:
        return None, str(e)


def fmt_ms(v: Optional[float]) -> str:
    """Format latency value for display"""
    return f"{v:.1f} ms" if v is not None else "—"


def parse_target(target: str, mode: str):
    """Parse target string based on check mode"""
    if mode == 'tcp':
        if ':' not in target:
            raise ValueError(f"TCP target must include port (host:port): {target}")
        host, port_str = target.split(':', 1)
        return host, int(port_str), None
    elif mode == 'http':
        # Add https:// if no protocol specified
        url = target if '://' in target else f"https://{target}"
        return None, None, url
    else:  # icmp mode
        return target, None, None


async def main_async(args: argparse.Namespace) -> int:
    """Main async execution logic"""
    # Parse comma-separated targets
    targets = []
    if args.targets:
        for part in args.targets.split(','):
            if part.strip():
                targets.append(part.strip())
    
    if not targets:
        print("No targets specified.")
        return 1

    # Setup HTTP session for HTTP mode
    session = None
    if args.mode == 'http':
        session = aiohttp.ClientSession(headers={'User-Agent': 'Mozilla/5.0 (compatible; HostMonitor/1.0; +http://example.com/bot)'})

    while True:
        try:
            # Process each target
            for t in targets:
                if args.mode == 'icmp':
                    host, _, _ = parse_target(t, 'icmp')
                    latency, err = await icmp_ping(host, args.timeout)
                    label = host
                elif args.mode == 'tcp':
                    host, port, _ = parse_target(t, 'tcp')
                    latency, err = await tcp_ping(host, port, args.timeout)
                    label = f"{host}:{port}"
                elif args.mode == 'http':
                    _, _, url = parse_target(t, 'http')
                    latency, err = await http_check(session, url, args.timeout)
                    label = url
                else:
                    print("Invalid mode")
                    return 1

                # Format and display results
                status = 'UP' if err is None else 'DOWN'
                print(f"{label:30} {args.mode.upper():5} {status:5} {fmt_ms(latency)} {err or ''}")

        finally:
            # Clean up HTTP session
            if session is not None:
                await session.close()
        
        print(separator)
        time.sleep(args.delay)


def main(argv):
    """CLI entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Host Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--mode', choices=['icmp', 'tcp', 'http'], default="icmp",
                        help='Check mode')
    parser.add_argument('--targets', required=True,
                        help='Comma-separated list of targets (host, host:port, or URL)')
    parser.add_argument('--timeout', type=float, default=3.0, 
                        help='Timeout seconds (default: 3)')
    parser.add_argument('--delay', type=float, default=1.0,
                        help='Delay between requests')

    args = parser.parse_args(argv)

    try:
        return asyncio.run(main_async(args))
    except KeyboardInterrupt:
            print("Interrupting...")
            exit()


if __name__ == '__main__':
    main(sys.argv[1:])