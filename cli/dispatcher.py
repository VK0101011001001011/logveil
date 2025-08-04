#!/usr/bin/env python3
"""
LogVeil Engine Dispatcher
Selects the optimal execution engine based on available runtimes and workload characteristics.
"""
import os
import sys
import shutil
import platform
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class EngineType(Enum):
    """Available execution engines in order of preference."""
    RUST = "rust"
    GO = "go" 
    PYTHON = "python"
    WASM = "wasm"

@dataclass
class EngineInfo:
    """Information about an available engine."""
    engine_type: EngineType
    binary_path: Optional[str]
    ffi_library: Optional[str]
    version: Optional[str]
    available: bool
    performance_score: int  # Higher is better

class EngineDispatcher:
    """
    Detects available engines and selects the optimal one for the workload.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.available_engines: Dict[EngineType, EngineInfo] = {}
        self._detect_engines()

    def _detect_engines(self) -> None:
        """Detect all available execution engines."""
        # Detect Rust engine (compiled library or binary)
        rust_info = self._detect_rust_engine()
        if rust_info:
            self.available_engines[EngineType.RUST] = rust_info
            self.logger.info(f"Detected Rust engine: {rust_info}")

        # Detect Go engine
        go_info = self._detect_go_engine()
        if go_info:
            self.available_engines[EngineType.GO] = go_info
            self.logger.info(f"Detected Go engine: {go_info}")

        # Python is always available as fallback
        python_info = self._detect_python_engine()
        self.available_engines[EngineType.PYTHON] = python_info
        self.logger.info(f"Using Python engine as fallback: {python_info}")

        # Detect WASM runtime
        wasm_info = self._detect_wasm_engine()
        if wasm_info:
            self.available_engines[EngineType.WASM] = wasm_info
            self.logger.info(f"Detected WASM engine: {wasm_info}")

    def _detect_rust_engine(self) -> Optional[EngineInfo]:
        """Detect Rust-based sanitizer engine."""
        # Look for compiled FFI library
        lib_extensions = {
            "Windows": ".dll",
            "Linux": ".so",
            "Darwin": ".dylib"
        }

        system = platform.system()
        lib_ext = lib_extensions.get(system, ".so")

        # Check for FFI library in core directory
        core_dir = Path(__file__).parent.parent / "core"
        rust_lib = core_dir / f"liblogveil_sanitizer{lib_ext}"

        if rust_lib.exists():
            return EngineInfo(
                engine_type=EngineType.RUST,
                binary_path=None,
                ffi_library=str(rust_lib),
                version=self._get_rust_version(),
                available=True,
                performance_score=100
            )

        # Check for standalone Rust binary
        rust_binary = shutil.which("logveil-rust")
        if rust_binary:
            return EngineInfo(
                engine_type=EngineType.RUST,
                binary_path=rust_binary,
                ffi_library=None,
                version=self._get_rust_version(),
                available=True,
                performance_score=95
            )

        return None
    
    def _detect_go_engine(self) -> Optional[EngineInfo]:
        """Detect Go-based streaming processor."""
        go_binary = shutil.which("logveil-go")
        if not go_binary:
            # Check local bridge directory
            bridge_dir = Path(__file__).parent.parent / "bridge" / "go-wrapper"
            local_go = bridge_dir / "logveil-go"
            if local_go.exists():
                go_binary = str(local_go)
        
        if go_binary:
            return EngineInfo(
                engine_type=EngineType.GO,
                binary_path=go_binary,
                ffi_library=None,
                version=self._get_go_version(go_binary),
                available=True,
                performance_score=85
            )
        
        return None
    
    def _detect_python_engine(self) -> EngineInfo:
        """Python engine is always available as fallback."""
        return EngineInfo(
            engine_type=EngineType.PYTHON,
            binary_path=sys.executable,
            ffi_library=None,
            version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            available=True,
            performance_score=50
        )
    
    def _detect_wasm_engine(self) -> Optional[EngineInfo]:
        """Detect WASM runtime for plugins."""
        try:
            import wasmtime
            return EngineInfo(
                engine_type=EngineType.WASM,
                binary_path=None,
                ffi_library=None,
                version=wasmtime.__version__,
                available=True,
                performance_score=70
            )
        except ImportError:
            return None
    
    def _get_rust_version(self) -> Optional[str]:
        """Get Rust engine version if available."""
        # This would query the Rust library/binary for version
        return "1.0.0"  # Placeholder
    
    def _get_go_version(self, binary_path: str) -> Optional[str]:
        """Get Go engine version."""
        try:
            import subprocess
            result = subprocess.run([binary_path, "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return "unknown"
    
    def select_optimal_engine(self, workload_hints: Optional[Dict[str, Any]] = None) -> EngineInfo:
        """
        Select the optimal engine based on available engines and workload characteristics.

        Args:
            workload_hints: Optional hints about the workload (file_size, file_count, etc.)

        Returns:
            EngineInfo for the selected engine
        """
        if not self.available_engines:
            self.logger.error("No execution engines available")
            raise RuntimeError("No execution engines available")

        # Apply workload-specific logic
        if workload_hints:
            file_size = workload_hints.get("file_size_mb", 0)
            file_count = workload_hints.get("file_count", 1)
            is_streaming = workload_hints.get("streaming", False)

            # For large files or streaming, prefer Go for I/O performance
            if (file_size > 100 or file_count > 1000 or is_streaming) and EngineType.GO in self.available_engines:
                self.logger.info("Selecting Go engine for large or streaming workload")
                return self.available_engines[EngineType.GO]

            # For intensive redaction, prefer Rust
            if file_size > 10 and EngineType.RUST in self.available_engines:
                self.logger.info("Selecting Rust engine for intensive redaction")
                return self.available_engines[EngineType.RUST]

        # Default selection: highest performance score
        best_engine = max(
            self.available_engines.values(),
            key=lambda e: e.performance_score if e.available else 0
        )

        self.logger.info(f"Selecting default engine: {best_engine.engine_type.value}")
        return best_engine
    
    def get_engine_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all detected engines."""
        status = {}
        for engine_type, info in self.available_engines.items():
            status[engine_type.value] = {
                "available": info.available,
                "version": info.version,
                "binary_path": info.binary_path,
                "ffi_library": info.ffi_library,
                "performance_score": info.performance_score
            }
        return status


def create_dispatcher() -> EngineDispatcher:
    """Factory function to create and initialize engine dispatcher."""
    return EngineDispatcher()


if __name__ == "__main__":
    # CLI for testing dispatcher
    dispatcher = create_dispatcher()
    
    print("🔥 LogVeil Engine Dispatcher Status")
    print("=" * 40)
    
    for engine_type, info in dispatcher.available_engines.items():
        status = "✅ Available" if info.available else "❌ Not Available"
        print(f"{engine_type.value.upper()}: {status}")
        if info.available:
            print(f"  Version: {info.version}")
            print(f"  Performance Score: {info.performance_score}")
            if info.binary_path:
                print(f"  Binary: {info.binary_path}")
            if info.ffi_library:
                print(f"  FFI Library: {info.ffi_library}")
        print()
    
    # Test optimal selection
    optimal = dispatcher.select_optimal_engine()
    print(f"🚀 Optimal Engine: {optimal.engine_type.value.upper()}")
