#!/usr/bin/env python3
"""
CLI Integration Test - Tests kraang.py command routing without API calls
"""

import sys
import io
from contextlib import redirect_stdout, redirect_stderr

def test_help_command():
    """Test that help command shows extract-multi"""
    print("=== Test: Help Command ===")

    import kraang
    cli = kraang.KraangCLI()

    # Capture output
    f = io.StringIO()
    with redirect_stdout(f):
        cli.run(['--help'])

    output = f.getvalue()

    # Check for extract-multi in output
    if 'extract-multi' in output:
        print("✓ Help shows extract-multi command")
        return True
    else:
        # Try just running help
        f = io.StringIO()
        with redirect_stdout(f):
            cli.run([])
        output = f.getvalue()

        if 'extract-multi' in output:
            print("✓ Help shows extract-multi command")
            return True
        else:
            print("✗ extract-multi not found in help")
            return False

def test_extract_multi_validation():
    """Test that extract-multi validates artifact_id"""
    print("\n=== Test: Extract-Multi Validation ===")

    import kraang
    cli = kraang.KraangCLI()

    # Initialize store
    cli.store.init()

    # Try to extract from non-existent artifact
    f = io.StringIO()
    with redirect_stdout(f):
        cli.run(['extract-multi', 'artifact_999'])

    output = f.getvalue()

    if 'not found' in output.lower():
        print("✓ Correctly validates artifact existence")
        return True
    else:
        print("✗ Did not validate artifact")
        print(f"Output: {output}")
        return False

def test_extract_multi_availability():
    """Test that extract-multi checks for module availability"""
    print("\n=== Test: Extract-Multi Availability ===")

    import kraang

    if kraang.MULTI_PASS_AVAILABLE:
        print("✓ Multi-pass extraction available")

        # Test that cmd_extract_multi exists
        cli = kraang.KraangCLI()
        if hasattr(cli, 'cmd_extract_multi'):
            print("✓ cmd_extract_multi method exists")
            return True
        else:
            print("✗ cmd_extract_multi method missing")
            return False
    else:
        print("⚠ Multi-pass extraction not available (multi_pass_extraction.py not found)")
        print("  This is expected if the module isn't in the path")
        return True  # Not a failure

def test_command_routing():
    """Test that extract-multi command routes correctly"""
    print("\n=== Test: Command Routing ===")

    import kraang
    cli = kraang.KraangCLI()
    cli.store.init()

    # Test with missing artifact_id
    f = io.StringIO()
    with redirect_stdout(f):
        cli.run(['extract-multi'])

    output = f.getvalue()

    if 'Usage:' in output or 'usage:' in output.lower():
        print("✓ Shows usage when artifact_id missing")
        return True
    else:
        print("✗ Did not show usage")
        print(f"Output: {output}")
        return False

def test_option_parsing():
    """Test that options are parsed correctly"""
    print("\n=== Test: Option Parsing ===")

    import kraang

    # We can't fully test without making API calls, but we can check the method signature
    cli = kraang.KraangCLI()

    if hasattr(cli, 'cmd_extract_multi'):
        import inspect
        sig = inspect.signature(cli.cmd_extract_multi)
        params = list(sig.parameters.keys())

        expected = ['artifact_id', 'max_passes', 'budget', 'enable_diminishing_returns']

        if all(p in params for p in expected):
            print(f"✓ cmd_extract_multi has correct parameters: {params}")
            return True
        else:
            print(f"✗ Missing expected parameters")
            print(f"  Expected: {expected}")
            print(f"  Found: {params}")
            return False
    else:
        print("⚠ cmd_extract_multi not found")
        return False

def run_tests():
    """Run all CLI integration tests"""
    print("="*70)
    print("CLI Integration Tests (No API Calls)")
    print("="*70)
    print()

    tests = [
        test_help_command,
        test_extract_multi_validation,
        test_extract_multi_availability,
        test_command_routing,
        test_option_parsing,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed = sum(1 for r in results if r)
    total = len(results)

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All CLI integration tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
