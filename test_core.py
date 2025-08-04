#!/usr/bin/env python3
"""
Quick test of the LogVeil 2.0 core components
"""

import sys
from pathlib import Path

# Add the sanilog directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_redaction_engine():
    """Test the new redaction engine."""
    print("🧪 Testing RedactionEngine...")
    
    from core.redactor import RedactionEngine, sanitize_line
    
    # Test legacy compatibility
    line = "User admin@company.com logged in from 192.168.1.100"
    redacted, counts = sanitize_line(line)
    print(f"Legacy API: {line}")
    print(f"Redacted:   {redacted}")
    print(f"Counts:     {counts}")
    print()
    
    # Test new engine
    engine = RedactionEngine()
    engine.trace_enabled = True
    
    redacted_line, traces = engine.redact_line(line, 1, "test.log")
    print(f"New API: {line}")
    print(f"Redacted: {redacted_line}")
    print(f"Traces: {len(traces)} redactions")
    for trace in traces:
        print(f"  - {trace.original_value} -> {trace.redacted_value} ({trace.reason.value})")
    print()

def test_profile_system():
    """Test the profile system."""
    print("🔧 Testing ProfileManager...")
    
    try:
        from core.profiles import ProfileManager
        
        manager = ProfileManager()
        profiles = manager.list_profiles()
        print(f"Available profiles: {profiles}")
        
        # Test nginx profile
        nginx = manager.get_profile("nginx")
        if nginx:
            print(f"Nginx profile: {nginx.description}")
            print(f"  Patterns: {len(nginx.patterns)}")
            print(f"  Filename patterns: {nginx.filename_patterns}")
        print()
        
    except ImportError as e:
        print(f"Profile system requires YAML: {e}")
        print("Skipping profile tests...")
        print()

def test_dispatcher():
    """Test the engine dispatcher."""
    print("🚀 Testing EngineDispatcher...")
    
    from cli.dispatcher import EngineDispatcher
    
    dispatcher = EngineDispatcher()
    status = dispatcher.get_engine_status()
    
    for engine, info in status.items():
        available = "✅" if info["available"] else "❌"
        print(f"  {engine.upper()}: {available} (score: {info['performance_score']})")
    
    optimal = dispatcher.select_optimal_engine()
    print(f"Optimal engine: {optimal.engine_type.value.upper()}")
    print()

def test_structured_data():
    """Test structured data processing."""
    print("📊 Testing StructuredDataProcessor...")
    
    try:
        from core.structured import StructuredDataProcessor
        from core.redactor import RedactionEngine
        
        # Sample JSON data
        test_data = {
            "user": {
                "email": "user@example.com",
                "ip": "192.168.1.100"
            },
            "auth": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature"
            }
        }
        
        engine = RedactionEngine()
        processor = StructuredDataProcessor(engine)
        
        # Add key path rules
        processor.add_key_path_rule("user.email", "redact")
        processor.add_key_path_rule("auth.token", "redact")
        
        redacted_data, traces = processor.process_json(test_data)
        
        print(f"Original: {test_data}")
        print(f"Redacted: {redacted_data}")
        print(f"Traces: {len(traces)} redactions")
        print()
        
    except Exception as e:
        print(f"Structured data test failed: {e}")
        print()

def main():
    """Run all tests."""
    print("🔥 LogVeil 2.0 Core Component Tests")
    print("=" * 50)
    
    try:
        test_redaction_engine()
        test_profile_system()
        test_dispatcher()
        test_structured_data()
        
        print("✅ All core tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
