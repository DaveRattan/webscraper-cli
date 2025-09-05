#!/usr/bin/env python3
"""
Test script to debug async issues in different environments
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import asyncio
from rich.console import Console

console = Console()

async def simple_async_task():
    """Simple async task for testing"""
    await asyncio.sleep(0.1)
    return "Task completed successfully"

def test_asyncio_environments():
    """Test different asyncio scenarios"""
    console.print("🧪 [bold blue]Testing Asyncio Environments[/bold blue]")
    
    # Test 1: Check if we're in an async context
    console.print("\n1. Checking for existing event loop...")
    try:
        loop = asyncio.get_running_loop()
        console.print(f"   ⚠️  Found running loop: {loop}")
        console.print(f"   Loop is running: {loop.is_running()}")
    except RuntimeError:
        console.print("   ✅ No running event loop detected")
    
    # Test 2: Try asyncio.run()
    console.print("\n2. Testing asyncio.run()...")
    try:
        result = asyncio.run(simple_async_task())
        console.print(f"   ✅ asyncio.run() worked: {result}")
    except RuntimeError as e:
        console.print(f"   ❌ asyncio.run() failed: {e}")
        
        # Test 3: Try manual loop creation
        console.print("\n3. Testing manual loop creation...")
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(simple_async_task())
            console.print(f"   ✅ Manual loop worked: {result}")
            loop.close()
        except Exception as e:
            console.print(f"   ❌ Manual loop failed: {e}")
        
        # Test 4: Try thread-based approach
        console.print("\n4. Testing thread-based approach...")
        try:
            import concurrent.futures
            
            def run_in_thread():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    return new_loop.run_until_complete(simple_async_task())
                finally:
                    new_loop.close()
                    asyncio.set_event_loop(None)
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_in_thread)
                result = future.result()
                console.print(f"   ✅ Thread-based approach worked: {result}")
                
        except Exception as e:
            console.print(f"   ❌ Thread-based approach failed: {e}")

def test_webscraper_import():
    """Test importing webscraper components"""
    console.print("\n🕷️ [bold blue]Testing WebScraper Imports[/bold blue]")
    
    try:
        from cli.commands import run_async_safe
        console.print("   ✅ Successfully imported run_async_safe")
        
        # Test the safe runner
        result = run_async_safe(simple_async_task())
        console.print(f"   ✅ run_async_safe worked: {result}")
        
    except Exception as e:
        console.print(f"   ❌ WebScraper import/test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    console.print("🔬 [bold green]Async Environment Diagnostics[/bold green]")
    console.print(f"Python version: {sys.version}")
    console.print(f"Platform: {sys.platform}")
    
    test_asyncio_environments()
    test_webscraper_import()
    
    console.print("\n🎉 [bold green]Diagnostics complete![/bold green]")
