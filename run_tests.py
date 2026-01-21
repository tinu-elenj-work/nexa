#!/usr/bin/env python3
"""
Nexa Test Runner
================

Comprehensive test runner for the Nexa project with coverage reporting.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --coverage         # Run with coverage report
    python run_tests.py --verbose          # Run with verbose output
    python run_tests.py --specific test_file.py  # Run specific test file
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_tests(coverage=False, verbose=False, specific_test=None):
    """Run the test suite with optional coverage reporting"""
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Build pytest command
    cmd = ['python', '-m', 'pytest']
    
    # Add test directory
    cmd.append('tests/')
    
    # Add specific test if provided
    if specific_test:
        cmd.append(f'tests/{specific_test}')
    
    # Add verbose flag
    if verbose:
        cmd.append('-v')
    
    # Add coverage if requested
    if coverage:
        cmd.extend([
            '--cov=src',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-report=xml'
        ])
    
    # Add other useful options
    cmd.extend([
        '--tb=short',  # Short traceback format
        '--strict-markers',  # Strict marker handling
        '--disable-warnings',  # Disable warnings for cleaner output
        '--color=yes'  # Colored output
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 60)
    
    # Run the tests
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        
        if coverage:
            print("\n📊 Coverage report generated:")
            print("   - HTML report: htmlcov/index.html")
            print("   - XML report: coverage.xml")
            print("   - Terminal report: See above output")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 60)
        print(f"❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install it with: pip install pytest")
        return False

def check_dependencies():
    """Check if required testing dependencies are installed"""
    required_packages = [
        'pytest',
        'pytest-cov',
        'pandas',
        'openpyxl',
        'xlsxwriter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run Nexa test suite')
    parser.add_argument('--coverage', action='store_true', 
                       help='Generate coverage report')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--specific', '-s', type=str,
                       help='Run specific test file (e.g., test_api_clients.py)')
    
    args = parser.parse_args()
    
    print("🧪 Nexa Test Suite Runner")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Run tests
    success = run_tests(
        coverage=args.coverage,
        verbose=args.verbose,
        specific_test=args.specific
    )
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test suite failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
