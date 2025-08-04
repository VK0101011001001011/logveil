#!/usr/bin/env python3
"""
LogVeil 2.0 Demo - Showcasing the new architecture
"""

import sys
from pathlib import Path

# Add the sanilog directory to path
sys.path.insert(0, str(Path(__file__).parent))

def demo_basic_redaction():
    """Demonstrate basic redaction capabilities."""
    print("🔥 LogVeil 2.0 - Basic Redaction Demo")
    print("=" * 50)
    
    from core.redactor import RedactionEngine
    
    # Sample log lines with various sensitive data
    sample_logs = [
        "2024-01-15 10:30:45 [INFO] User login: admin@company.com from 192.168.1.100",
        "2024-01-15 10:31:12 [WARN] Failed authentication attempt from 10.0.0.45",
        "2024-01-15 10:31:20 [INFO] JWT issued: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature",
        "2024-01-15 10:32:01 [DEBUG] Database query: SELECT * FROM users WHERE id=12345",
        "2024-01-15 10:32:15 [ERROR] API key validation failed: sk-1234567890abcdefghijklmnop",
        "2024-01-15 10:33:00 [INFO] Session created: session_abc123def456ghi789",
        "2024-01-15 10:33:30 [WARN] Credit card number detected: 4532-1234-5678-9012",
        "2024-01-15 10:34:00 [ERROR] AWS key leaked: AKIAIOSFODNN7EXAMPLE",
    ]
    
    # Create redaction engine with tracing enabled
    engine = RedactionEngine()
    engine.configure({
        'trace_enabled': True,
        'entropy_threshold': 4.2,
        'enable_entropy_detection': True
    })
    
    print("📝 Processing sample log entries:")
    print()
    
    total_redactions = 0
    
    for i, log_line in enumerate(sample_logs, 1):
        redacted_line, traces = engine.redact_line(log_line, i, "demo.log")
        
        print(f"Line {i}:")
        print(f"  Original:  {log_line}")
        print(f"  Redacted:  {redacted_line}")
        
        if traces:
            print(f"  Changes:   {len(traces)} redactions")
            for trace in traces:
                reason = trace.reason.value.replace('_', ' ').title()
                pattern = f" ({trace.pattern_name})" if trace.pattern_name else ""
                print(f"    - {trace.original_value} -> {trace.redacted_value} [{reason}{pattern}]")
        else:
            print(f"  Changes:   No sensitive data detected")
        
        print()
        total_redactions += len(traces)
    
    # Show statistics
    stats = engine.get_stats()
    print("📊 Processing Summary:")
    print(f"  Lines processed: {stats.total_lines_processed}")
    print(f"  Total redactions: {stats.total_redactions}")
    print(f"  Entropy detections: {stats.entropy_detections}")
    print(f"  Pattern matches: {len(stats.redactions_by_pattern)} types")
    
    if stats.redactions_by_pattern:
        print("\n🎯 Redaction Breakdown:")
        for pattern, count in stats.redactions_by_pattern.items():
            print(f"  {pattern}: {count} matches")

def demo_performance_comparison():
    """Demonstrate performance aspects."""
    print("\n🚀 Performance Comparison Demo")
    print("=" * 50)
    
    from cli.dispatcher import EngineDispatcher
    
    dispatcher = EngineDispatcher()
    
    print("Available execution engines:")
    
    for engine_type, info in dispatcher.available_engines.items():
        status = "✅ Available" if info.available else "❌ Not Available"
        version = info.version or "Unknown"
        
        print(f"  {engine_type.value.upper()}: {status}")
        print(f"    Version: {version}")
        print(f"    Performance Score: {info.performance_score}")
        
        if info.binary_path:
            print(f"    Binary: {info.binary_path}")
        if info.ffi_library:
            print(f"    FFI Library: {info.ffi_library}")
        print()
    
    optimal = dispatcher.select_optimal_engine()
    print(f"🎯 Optimal engine for this system: {optimal.engine_type.value.upper()}")

def demo_pattern_showcase():
    """Showcase built-in pattern detection."""
    print("\n🎭 Pattern Detection Showcase")
    print("=" * 50)
    
    from core.redactor import PatternRegistry
    
    registry = PatternRegistry()
    
    # Test patterns with sample data
    test_cases = {
        "ip_address": "Server responded from 192.168.1.100",
        "email": "Contact support at help@example.com",
        "uuid": "Request ID: 550e8400-e29b-41d4-a716-446655440000",
        "jwt": "Auth token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.test",
        "sha256": "File hash: 2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae",
        "aws_access_key": "AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE",
        "credit_card": "Payment with card 4532-1234-5678-9012",
        "ssn": "SSN: 123-45-6789",
        "phone": "Call us at +1-555-123-4567",
    }
    
    print(f"Built-in patterns: {len(registry.patterns)} types")
    print()
    
    for pattern_name, test_text in test_cases.items():
        if pattern_name in registry.patterns:
            pattern = registry.patterns[pattern_name]
            matches = pattern.findall(test_text)
            
            print(f"🔍 {pattern_name.upper().replace('_', ' ')}")
            print(f"  Test: {test_text}")
            
            if matches:
                redacted = pattern.sub(f"[REDACTED_{pattern_name.upper()}]", test_text)
                print(f"  Result: {redacted}")
                print(f"  Matches: {matches}")
            else:
                print(f"  Result: No matches")
            print()

def main():
    """Run the complete demo."""
    try:
        demo_basic_redaction()
        demo_performance_comparison()
        demo_pattern_showcase()
        
        print("\n🎉 Demo completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install pyyaml rich fastapi")
        print("2. Try the full CLI: python cli/logveil-agent.py --help")
        print("3. Start API server: python cli/logveil-agent.py --serve")
        print("4. Explore profiles: python cli/logveil-agent.py --list-profiles")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
