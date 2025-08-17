#!/usr/bin/env python3
"""
Simple validation script to test that requirements.txt is working properly.
This can be run to verify dependencies are correctly specified.
"""

import sys

def test_core_imports():
    """Test that all core dependencies can be imported"""
    print("Testing core dependency imports...")
    
    try:
        import requests
        print("✓ requests imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import requests: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4 imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import beautifulsoup4: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import pandas: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import numpy: {e}")
        return False
    
    return True

def test_package_imports():
    """Test that the package imports work with dependencies"""
    print("\nTesting nflprojections package imports...")
    
    try:
        import nflprojections
        print("✓ nflprojections basic import works")
    except ImportError as e:
        print(f"✗ Failed to import nflprojections: {e}")
        return False
    
    try:
        from nflprojections import NFLComProjections, ProjectionCombiner, ProjectionSource
        print("✓ Main high-level APIs import successfully")
    except ImportError as e:
        print(f"✗ Failed to import main APIs: {e}")
        return False
    
    try:
        from nflprojections.fetch import NFLComFetcher
        from nflprojections.parse import NFLComParser
        from nflprojections.combine import ProjectionCombiner
        print("✓ Functional components import successfully")
    except ImportError as e:
        print(f"✗ Failed to import functional components: {e}")
        return False
    
    return True

def test_class_instantiation():
    """Test that classes can be instantiated (basic functionality)"""
    print("\nTesting class instantiation...")
    
    try:
        from nflprojections.fetch import NFLComFetcher
        fetcher = NFLComFetcher()
        print("✓ NFLComFetcher can be instantiated")
    except Exception as e:
        print(f"✗ Failed to instantiate NFLComFetcher: {e}")
        return False
    
    try:
        from nflprojections.parse import NFLComParser
        parser = NFLComParser()
        print("✓ NFLComParser can be instantiated")  
    except Exception as e:
        print(f"✗ Failed to instantiate NFLComParser: {e}")
        return False
    
    try:
        from nflprojections.combine import ProjectionCombiner
        combiner = ProjectionCombiner()
        print("✓ ProjectionCombiner can be instantiated")
    except Exception as e:
        print(f"✗ Failed to instantiate ProjectionCombiner: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("NFLPROJECTIONS REQUIREMENTS VALIDATION")
    print("=" * 60)
    
    success = True
    
    success &= test_core_imports()
    success &= test_package_imports() 
    success &= test_class_instantiation()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED! Requirements.txt is working correctly.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED! Check requirements.txt and dependencies.")
        sys.exit(1)