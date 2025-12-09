#!/usr/bin/env python3
"""
Test script to verify LiveKit server connection
Run this to ensure your environment is configured correctly
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
import urllib.request
import socket

console = Console()

def check_env_vars():
    """Check if required environment variables are set"""
    console.print("\n[bold blue]1. Checking Environment Variables[/bold blue]")
    
    load_dotenv()
    
    required_vars = {
        "LIVEKIT_URL": os.getenv("LIVEKIT_URL"),
        "LIVEKIT_API_KEY": os.getenv("LIVEKIT_API_KEY"),
        "LIVEKIT_API_SECRET": os.getenv("LIVEKIT_API_SECRET"),
    }
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Variable", style="yellow")
    table.add_column("Value", style="green")
    table.add_column("Status", style="white")
    
    all_set = True
    for var, value in required_vars.items():
        if value:
            # Mask secrets for display
            display_value = value if var == "LIVEKIT_URL" else f"{value[:8]}...{value[-4:]}"
            table.add_row(var, display_value, "✓ Set")
        else:
            table.add_row(var, "Not set", "✗ Missing")
            all_set = False
    
    console.print(table)
    
    if not all_set:
        console.print("\n[bold red]✗ Some environment variables are missing![/bold red]")
        console.print("Please check your .env file\n")
        return False
    
    console.print("[bold green]✓ All environment variables are set[/bold green]\n")
    return True

def check_server_reachable():
    """Check if LiveKit server is reachable"""
    console.print("[bold blue]2. Checking LiveKit Server Connectivity[/bold blue]")
    
    url = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
    
    # Extract host and port from URL
    if url.startswith("ws://"):
        host_port = url.replace("ws://", "")
    elif url.startswith("wss://"):
        host_port = url.replace("wss://", "")
    else:
        host_port = url
    
    parts = host_port.split(":")
    host = parts[0]
    port = int(parts[1].split("/")[0]) if len(parts) > 1 else 7880
    
    # Try HTTP endpoint first
    http_url = f"http://{host}:{port}"
    
    console.print(f"Testing connection to: [cyan]{http_url}[/cyan]")
    
    try:
        # Test TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            console.print(f"[green]✓ Port {port} is open[/green]")
        else:
            console.print(f"[red]✗ Port {port} is closed or unreachable[/red]")
            console.print("\n[yellow]Troubleshooting:[/yellow]")
            console.print("  1. Start LiveKit server: make livekit-start")
            console.print("  2. Check server status: make livekit-status")
            console.print("  3. View logs: make livekit-logs")
            return False
        
        # Try HTTP request
        try:
            req = urllib.request.Request(http_url, method='GET')
            with urllib.request.urlopen(req, timeout=3) as response:
                console.print(f"[green]✓ Server is responding (HTTP {response.status})[/green]")
        except urllib.error.HTTPError as e:
            # Some responses are expected (like 404)
            console.print(f"[green]✓ Server is responding (HTTP {e.code})[/green]")
        except Exception as e:
            console.print(f"[yellow]⚠ HTTP check inconclusive: {e}[/yellow]")
        
        console.print("[bold green]✓ LiveKit server is reachable[/bold green]\n")
        return True
        
    except socket.gaierror:
        console.print(f"[red]✗ Cannot resolve hostname: {host}[/red]")
        return False
    except socket.timeout:
        console.print(f"[red]✗ Connection timeout[/red]")
        return False
    except Exception as e:
        console.print(f"[red]✗ Connection error: {e}[/red]")
        return False

async def check_livekit_sdk():
    """Check if LiveKit SDK can connect"""
    console.print("[bold blue]3. Testing LiveKit SDK Connection[/bold blue]")
    
    try:
        from livekit import api
        
        # Create API client
        livekit_url = os.getenv("LIVEKIT_URL")
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        livekit_api = api.LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret,
        )
        
        # Try to list rooms (this will fail if credentials are wrong)
        console.print("Attempting to authenticate with LiveKit server...")
        
        try:
            rooms = await livekit_api.room.list_rooms(api.ListRoomsRequest())
            console.print(f"[green]✓ Successfully authenticated![/green]")
            console.print(f"[green]✓ Found {len(rooms.rooms)} active rooms[/green]")
            
            if len(rooms.rooms) > 0:
                console.print("\nActive rooms:")
                for room in rooms.rooms:
                    console.print(f"  • {room.name} ({room.num_participants} participants)")
            
            await livekit_api.aclose()
            
            console.print("[bold green]✓ LiveKit SDK connection successful[/bold green]\n")
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Authentication failed: {e}[/red]")
            console.print("\n[yellow]Troubleshooting:[/yellow]")
            console.print("  1. Check API key and secret in .env file")
            console.print("  2. Verify livekit.yaml has matching credentials")
            console.print("  3. Default dev credentials: devkey / secret")
            return False
        
    except ImportError:
        console.print("[red]✗ LiveKit SDK not installed[/red]")
        console.print("Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        console.print(f"[red]✗ SDK test failed: {e}[/red]")
        return False

def print_summary(env_ok, server_ok, sdk_ok):
    """Print final summary"""
    console.print("\n" + "="*60)
    console.print("[bold]Summary[/bold]")
    console.print("="*60)
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("Check", style="cyan")
    table.add_column("Status", style="white")
    
    table.add_row("Environment Variables", "✓ Pass" if env_ok else "✗ Fail")
    table.add_row("Server Connectivity", "✓ Pass" if server_ok else "✗ Fail")
    table.add_row("SDK Authentication", "✓ Pass" if sdk_ok else "✗ Fail")
    
    console.print(table)
    
    if env_ok and server_ok and sdk_ok:
        console.print("\n[bold green]🎉 All checks passed! You're ready to run the agent.[/bold green]")
        console.print("\nNext steps:")
        console.print("  1. Run the agent: [cyan]make dev[/cyan]")
        console.print("  2. Or console mode: [cyan]python agent.py console[/cyan]")
    else:
        console.print("\n[bold red]⚠ Some checks failed. Please fix the issues above.[/bold red]")
        console.print("\nQuick fixes:")
        console.print("  • Start server: [cyan]make livekit-start[/cyan]")
        console.print("  • Check status: [cyan]make livekit-status[/cyan]")
        console.print("  • View logs: [cyan]make livekit-logs[/cyan]")
        console.print("  • Check .env: [cyan]make check-env[/cyan]")

async def main():
    """Run all connection tests"""
    console.print("[bold]LiveKit Connection Test[/bold]")
    console.print("="*60 + "\n")
    
    # Run checks
    env_ok = check_env_vars()
    server_ok = check_server_reachable() if env_ok else False
    sdk_ok = await check_livekit_sdk() if (env_ok and server_ok) else False
    
    # Print summary
    print_summary(env_ok, server_ok, sdk_ok)
    
    # Exit with appropriate code
    sys.exit(0 if (env_ok and server_ok and sdk_ok) else 1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(1)

