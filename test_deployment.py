#!/usr/bin/env python3
"""
Deployment Pre-flight Test

Tests all deployment components before actual GitHub deployment:
- File existence checks
- Module imports
- Environment variable handling
- API client initialization
- Graceful degradation

Run this before deploying to catch issues early.
"""

import os
import sys
import json
from pathlib import Path

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET}  {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET}  {msg}")

def print_section(title):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0
}

def test_file_existence():
    """Test 1: Check all required files exist"""
    print_section("TEST 1: File Existence Check")

    required_files = [
        # Frontend
        "index.html",
        "assets/styles.css",
        "assets/app.js",

        # Scripts
        "scripts/__init__.py",
        "scripts/update_news.py",
        "scripts/ai_relevance.py",

        # AI Filter modules (10 files)
        "scripts/ai_filter/__init__.py",
        "scripts/ai_filter/main_filter.py",
        "scripts/ai_filter/whitelist_router.py",
        "scripts/ai_filter/tier0_processor.py",
        "scripts/ai_filter/tier1_filter.py",
        "scripts/ai_filter/tier2_pipeline.py",
        "scripts/ai_filter/glm_client.py",
        "scripts/ai_filter/easyrouter_client.py",
        "scripts/ai_filter/language_detector.py",
        "scripts/ai_filter/prompts.py",

        # Config
        "config/source-whitelist.yaml",
        "requirements.txt",
    ]

    all_exist = True
    for file_path in required_files:
        full_path = Path(file_path)
        if full_path.exists():
            # Check if it's readable
            if full_path.stat().st_size == 0 and file_path.endswith('.py') and '__init__' not in file_path:
                print_warning(f"{file_path} exists but is empty")
                test_results["warnings"] += 1
            else:
                print_success(f"{file_path}")
                test_results["passed"] += 1
        else:
            print_error(f"{file_path} NOT FOUND")
            test_results["failed"] += 1
            all_exist = False

    return all_exist

def test_module_imports():
    """Test 2: Test Python module imports"""
    print_section("TEST 2: Module Import Test")

    # Add project root to path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))

    imports_to_test = [
        ("scripts.update_news", "main"),  # Script has main() function
        ("scripts.ai_relevance", "add_ai_relevance_fields"),  # Actual function name
        ("scripts.ai_filter.main_filter", "AIContentFilter"),
        ("scripts.ai_filter.glm_client", "GLMClient"),
        ("scripts.ai_filter.easyrouter_client", "EasyRouterClient"),
        ("scripts.ai_filter.tier0_processor", "Tier0Processor"),
        ("scripts.ai_filter.tier1_filter", "Tier1Filter"),
        ("scripts.ai_filter.tier2_pipeline", "Tier2Pipeline"),
        ("scripts.ai_filter.whitelist_router", "WhitelistRouter"),
        ("scripts.ai_filter.language_detector", "detect_language"),
        ("scripts.ai_filter.prompts", "build_classification_prompt"),
    ]

    all_imports_ok = True
    for module_path, item_name in imports_to_test:
        try:
            module = __import__(module_path, fromlist=[item_name])
            getattr(module, item_name)
            print_success(f"from {module_path} import {item_name}")
            test_results["passed"] += 1
        except ImportError as e:
            print_error(f"from {module_path} import {item_name} - {e}")
            test_results["failed"] += 1
            all_imports_ok = False
        except AttributeError as e:
            print_error(f"{item_name} not found in {module_path} - {e}")
            test_results["failed"] += 1
            all_imports_ok = False

    return all_imports_ok

def test_glm_client():
    """Test 3: Test GLM client initialization and API"""
    print_section("TEST 3: GLM Client Test")

    try:
        from scripts.ai_filter.glm_client import GLMClient

        # Test with default key
        print_info("Testing GLM client with default shared key...")
        client = GLMClient()

        print_success(f"Client initialized")
        print_info(f"  Using shared key: {client.using_shared_key}")
        print_info(f"  Using official SDK: {client.using_official_sdk}")
        print_info(f"  API Key: {client.api_key[:20]}...")

        # Test API call
        print_info("Testing GLM API call...")
        response = client.call_model(
            model="glm-4.7-flash",
            system_prompt="你是AI助手",
            user_prompt="说'测试成功'",
            temperature=0.1,
            max_tokens=50
        )

        if response['content'] and len(response['content']) > 0:
            print_success(f"GLM API call successful")
            print_info(f"  Response: {response['content'][:50]}...")
            print_info(f"  Tokens used: {response['usage']['total_tokens']}")
            test_results["passed"] += 2
            return True
        else:
            print_error("GLM API returned empty content")
            test_results["failed"] += 1
            return False

    except Exception as e:
        print_error(f"GLM client test failed: {e}")
        test_results["failed"] += 1
        return False

def test_easyrouter_optional():
    """Test 4: Test EasyRouter is optional"""
    print_section("TEST 4: EasyRouter Optional Test")

    # Save and clear EasyRouter env vars
    saved_key = os.environ.get('EASYROUTER_API_KEY')
    saved_url = os.environ.get('EASYROUTER_BASE_URL')

    if 'EASYROUTER_API_KEY' in os.environ:
        del os.environ['EASYROUTER_API_KEY']
    if 'EASYROUTER_BASE_URL' in os.environ:
        del os.environ['EASYROUTER_BASE_URL']

    try:
        from scripts.ai_filter.easyrouter_client import EasyRouterClient
        from scripts.ai_filter.tier1_filter import Tier1Filter
        from scripts.ai_filter.tier2_pipeline import Tier2Pipeline

        # Test 4.1: EasyRouter client should initialize without error
        print_info("Testing EasyRouter client initialization without API key...")
        client = EasyRouterClient()
        print_success("EasyRouter client initialized (lazy validation)")
        test_results["passed"] += 1

        # Test 4.2: call_model should raise ValueError
        print_info("Testing EasyRouter call should fail gracefully...")
        try:
            client.call_model(
                model="test",
                system_prompt="test",
                user_prompt="test"
            )
            print_error("EasyRouter should have raised ValueError")
            test_results["failed"] += 1
        except ValueError as e:
            if "EASYROUTER_API_KEY" in str(e):
                print_success(f"EasyRouter correctly raises ValueError: {e}")
                test_results["passed"] += 1
            else:
                print_error(f"Unexpected ValueError: {e}")
                test_results["failed"] += 1

        # Test 4.3: Tier1Filter should initialize
        print_info("Testing Tier1Filter initialization without EasyRouter...")
        tier1 = Tier1Filter()
        print_success("Tier1Filter initialized")
        test_results["passed"] += 1

        # Test 4.4: Tier2Pipeline should initialize
        print_info("Testing Tier2Pipeline initialization without EasyRouter...")
        tier2 = Tier2Pipeline()
        print_success("Tier2Pipeline initialized")
        test_results["passed"] += 1

        return True

    except Exception as e:
        print_error(f"EasyRouter optional test failed: {e}")
        test_results["failed"] += 1
        return False
    finally:
        # Restore env vars
        if saved_key:
            os.environ['EASYROUTER_API_KEY'] = saved_key
        if saved_url:
            os.environ['EASYROUTER_BASE_URL'] = saved_url

def test_ai_content_filter():
    """Test 5: Test AIContentFilter initialization"""
    print_section("TEST 5: AIContentFilter Integration Test")

    try:
        from scripts.ai_filter.main_filter import AIContentFilter

        print_info("Initializing AIContentFilter...")
        filter_system = AIContentFilter()
        print_success("AIContentFilter initialized successfully")
        test_results["passed"] += 1

        # Test that filter components are accessible
        print_info("Testing filter components...")
        if filter_system.router:
            print_success("Router component available")
            test_results["passed"] += 1
        else:
            print_error("Router component missing")
            test_results["failed"] += 1

        # Skip actual filtering test (requires full whitelist setup)
        print_info("Skipping live filter test (requires whitelist config)")

        return True

    except Exception as e:
        print_error(f"AIContentFilter test failed: {e}")
        import traceback
        traceback.print_exc()
        test_results["failed"] += 1
        return False

def test_update_news_script():
    """Test 6: Test update_news.py can be imported"""
    print_section("TEST 6: update_news.py Import Test")

    try:
        # Just test import, don't run it
        import scripts.update_news
        print_success("update_news.py imported successfully")
        test_results["passed"] += 1
        return True
    except Exception as e:
        print_error(f"update_news.py import failed: {e}")
        import traceback
        traceback.print_exc()
        test_results["failed"] += 1
        return False

def test_pythonpath_simulation():
    """Test 7: Simulate GitHub Actions PYTHONPATH"""
    print_section("TEST 7: PYTHONPATH Simulation")

    project_root = Path(__file__).parent

    # Simulate GitHub Actions environment
    print_info(f"Simulating: export PYTHONPATH=\"${{PYTHONPATH}}:{project_root}\"")

    # Check if project root is in sys.path
    if str(project_root) in sys.path:
        print_success(f"Project root in sys.path")
        test_results["passed"] += 1
    else:
        print_warning(f"Project root not in sys.path (added by test)")
        sys.path.insert(0, str(project_root))
        test_results["warnings"] += 1

    # Test that modules can be imported with this setup
    try:
        from scripts.ai_filter.main_filter import AIContentFilter
        print_success("Module imports work with PYTHONPATH setup")
        test_results["passed"] += 1
        return True
    except ImportError as e:
        print_error(f"Module import failed with PYTHONPATH: {e}")
        test_results["failed"] += 1
        return False

def print_summary():
    """Print test summary"""
    print_section("TEST SUMMARY")

    total = test_results["passed"] + test_results["failed"]

    print(f"Total tests: {total}")
    print(f"{Colors.GREEN}Passed: {test_results['passed']}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {test_results['failed']}{Colors.RESET}")
    print(f"{Colors.YELLOW}Warnings: {test_results['warnings']}{Colors.RESET}")

    if test_results["failed"] == 0:
        print(f"\n{Colors.GREEN}{'='*60}")
        print("✓ ALL TESTS PASSED - SAFE TO DEPLOY")
        print(f"{'='*60}{Colors.RESET}\n")
        return True
    else:
        print(f"\n{Colors.RED}{'='*60}")
        print("✗ TESTS FAILED - DO NOT DEPLOY YET")
        print("Fix the errors above before deploying")
        print(f"{'='*60}{Colors.RESET}\n")
        return False

def main():
    print(f"\n{Colors.BLUE}{'='*60}")
    print("AI Daily News - Deployment Pre-flight Test")
    print(f"{'='*60}{Colors.RESET}\n")

    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Run all tests
    test_file_existence()
    test_module_imports()
    test_glm_client()
    test_easyrouter_optional()
    test_ai_content_filter()
    test_update_news_script()
    test_pythonpath_simulation()

    # Print summary
    success = print_summary()

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
