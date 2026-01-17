#!/usr/bin/env python3
"""
Debug script to test version control functionality
Run this to diagnose issues with video generation
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.version_utils import (
    get_file_hash,
    check_for_updates,
    register_service_version,
    get_service_info,
    get_all_services,
    get_version_history,
    load_registry,
    initialize_registry
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def test_version_system():
    """Test the version control system"""
    
    print_section("Version Control System Debug")
    
    # 1. Check registry file
    print("\n[1] Checking Registry File...")
    registry_path = "version_registry.json"
    
    if os.path.exists(registry_path):
        print(f"✅ Registry file exists: {registry_path}")
        try:
            registry = load_registry()
            print(f"✅ Registry loaded successfully")
            print(f"   - Schema version: {registry.get('schema_version', 'N/A')}")
            print(f"   - Last updated: {registry.get('last_updated', 'N/A')}")
            print(f"   - Services count: {len(registry.get('services', {}))}")
        except Exception as e:
            print(f"❌ Error loading registry: {e}")
            print("   Attempting to initialize new registry...")
            registry = initialize_registry()
            print(f"✅ New registry initialized")
    else:
        print(f"⚠️  Registry file not found: {registry_path}")
        print("   Initializing new registry...")
        registry = initialize_registry()
        print(f"✅ New registry created")
    
    # 2. List all services
    print("\n[2] Listing All Services...")
    services = get_all_services()
    
    if services:
        print(f"✅ Found {len(services)} service(s):")
        for name, data in services.items():
            print(f"\n   📋 Service: {data.get('service_name', name)}")
            print(f"      - Normalized name: {name}")
            print(f"      - Current version: {data.get('current_version', 'N/A')}")
            print(f"      - Last updated: {data.get('last_updated', 'N/A')[:19]}")
            print(f"      - Video path: {data.get('video_path', 'N/A')}")
            print(f"      - Source type: {data.get('source_type', 'N/A')}")
            print(f"      - History count: {len(data.get('history', []))}")
    else:
        print("📭 No services registered yet")
    
    # 3. Check output directory
    print("\n[3] Checking Output Directory...")
    output_dir = "output_videos"
    
    if os.path.exists(output_dir):
        videos = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
        print(f"✅ Output directory exists")
        print(f"   - Total videos: {len(videos)}")
        
        if videos:
            print("\n   📹 Video files:")
            for video in sorted(videos):
                path = os.path.join(output_dir, video)
                size_mb = os.path.getsize(path) / (1024 * 1024)
                print(f"      - {video} ({size_mb:.2f} MB)")
    else:
        print(f"⚠️  Output directory not found: {output_dir}")
        print("   Creating directory...")
        os.makedirs(output_dir, exist_ok=True)
        print(f"✅ Directory created")
    
    # 4. Test hash generation
    print("\n[4] Testing Hash Generation...")
    test_content = b"Test content for hashing"
    test_hash = get_file_hash(test_content)
    print(f"✅ Hash generated successfully")
    print(f"   - Content: {test_content.decode()}")
    print(f"   - Hash: {test_hash[:16]}...")
    
    # 5. Test version check
    print("\n[5] Testing Version Check...")
    test_service_name = "Test Service"
    test_hash_new = get_file_hash(b"New content")
    
    status, existing = check_for_updates(test_service_name, test_hash_new)
    print(f"✅ Version check completed")
    print(f"   - Status: {status}")
    print(f"   - Existing data: {'Found' if existing else 'None'}")
    
    # 6. Check dependencies
    print("\n[6] Checking Dependencies...")
    
    dependencies = {
        "streamlit": "import streamlit",
        "moviepy": "import moviepy",
        "PIL": "from PIL import Image",
        "edge_tts": "import edge_tts",
        "google.generativeai": "import google.generativeai",
    }
    
    for name, import_stmt in dependencies.items():
        try:
            exec(import_stmt)
            print(f"✅ {name} - Available")
        except ImportError:
            print(f"❌ {name} - Missing")
    
    # 7. Summary
    print_section("Summary")
    
    if services:
        print(f"✅ System operational with {len(services)} registered service(s)")
    else:
        print(f"⚠️  System initialized but no services registered yet")
    
    print(f"\n📊 Registry Status:")
    print(f"   - File: {registry_path}")
    print(f"   - Services: {len(services)}")
    print(f"   - Output dir: {output_dir}")
    
    print("\n💡 Next Steps:")
    if not services:
        print("   1. Generate your first video using the Streamlit app")
        print("   2. Run 'py -m streamlit run app.py' to start")
    else:
        print("   1. System is working correctly")
        print("   2. Generate a new version to test version control")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        test_version_system()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
