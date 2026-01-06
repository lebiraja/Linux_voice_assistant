#!/usr/bin/env python3
"""
Test script for AI Script Generation feature
Tests the generate_and_run_script and execute_command tools
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.builtin.script_generator import GenerateAndRunScriptTool, ExecuteCommandTool
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_execute_command():
    """Test simple command execution"""
    print("\n" + "="*60)
    print("TEST 1: Execute Simple Command")
    print("="*60)
    
    tool = ExecuteCommandTool()
    
    # Test: List files
    print("\n📝 Test: List files in current directory")
    result = tool.execute(command="ls -la")
    
    if result['success']:
        print("✅ Success!")
        print(f"Output:\n{result['output'][:200]}...")
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    # Test: Show disk usage
    print("\n📝 Test: Show disk usage")
    result = tool.execute(command="df -h")
    
    if result['success']:
        print("✅ Success!")
        print(f"Output:\n{result['output'][:200]}...")
    else:
        print(f"❌ Failed: {result.get('error')}")


def test_script_generation_bash():
    """Test Bash script generation"""
    print("\n" + "="*60)
    print("TEST 2: Generate Bash Script")
    print("="*60)
    
    tool = GenerateAndRunScriptTool()
    
    # Check if aichat is installed
    print("\n🔍 Checking if aichat is installed...")
    if not tool._check_aichat_installed():
        print("❌ aichat is NOT installed!")
        print("   Please run: ./install-aichat.sh")
        return
    
    print("✅ aichat is installed")
    
    # Test: Generate a simple script (without execution)
    print("\n📝 Test: Generate a 'Hello World' bash script (no execution)")
    result = tool.execute(
        task_description="Create a simple hello world script that echoes 'Hello from JARVIS!' and shows current date",
        language="bash",
        auto_execute=False
    )
    
    if result['success']:
        print("✅ Script generated successfully!")
        print(f"\n📄 Generated Script:\n{'-'*60}")
        print(result['script_generated'])
        print('-'*60)
    else:
        print(f"❌ Failed: {result.get('error')}")


def test_script_generation_and_execution():
    """Test script generation with execution"""
    print("\n" + "="*60)
    print("TEST 3: Generate and Execute Script")
    print("="*60)
    
    tool = GenerateAndRunScriptTool()
    
    if not tool._check_aichat_installed():
        print("❌ Skipping test - aichat not installed")
        return
    
    # Test: Generate and execute
    print("\n📝 Test: Generate and execute a system info script")
    result = tool.execute(
        task_description="Create a script that shows: hostname, current user, and uptime. Format the output nicely.",
        language="bash",
        auto_execute=True
    )
    
    if result['success']:
        print("✅ Script generated and executed!")
        print(f"\n📄 Generated Script:\n{'-'*60}")
        print(result['script_generated'])
        print('-'*60)
        
        if result.get('executed'):
            if result.get('execution_success'):
                print(f"\n✅ Execution successful!")
                print(f"\n📤 Output:\n{'-'*60}")
                print(result.get('output', ''))
                print('-'*60)
            else:
                print(f"\n❌ Execution failed!")
                print(f"Errors: {result.get('errors', '')}")
    else:
        print(f"❌ Failed: {result.get('error')}")


def test_script_generation_python():
    """Test Python script generation"""
    print("\n" + "="*60)
    print("TEST 4: Generate Python Script")
    print("="*60)
    
    tool = GenerateAndRunScriptTool()
    
    if not tool._check_aichat_installed():
        print("❌ Skipping test - aichat not installed")
        return
    
    # Test: Generate Python script
    print("\n📝 Test: Generate Python script to calculate factorial")
    result = tool.execute(
        task_description="Create a Python script that calculates factorial of 5 and prints it nicely",
        language="python",
        auto_execute=True
    )
    
    if result['success']:
        print("✅ Script generated!")
        print(f"\n📄 Generated Script:\n{'-'*60}")
        print(result['script_generated'])
        print('-'*60)
        
        if result.get('executed') and result.get('execution_success'):
            print(f"\n✅ Execution successful!")
            print(f"\n📤 Output:\n{'-'*60}")
            print(result.get('output', ''))
            print('-'*60)
    else:
        print(f"❌ Failed: {result.get('error')}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 AI Script Generation Feature Tests")
    print("="*60)
    
    try:
        # Test 1: Simple command execution
        test_execute_command()
        
        # Test 2: Script generation (no execution)
        test_script_generation_bash()
        
        # Test 3: Script generation with execution
        test_script_generation_and_execution()
        
        # Test 4: Python script generation
        test_script_generation_python()
        
        print("\n" + "="*60)
        print("✅ All Tests Completed!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
