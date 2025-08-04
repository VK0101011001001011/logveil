#!/usr/bin/env python3
"""
LogVeil Agent - Main CLI Entry Point
Advanced log sanitization with intelligent engine dispatch and modular processing.
"""

import sys
import time
import json
import platform
from pathlib import Path
from typing import Optional, Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text

# LogVeil core imports
from logveil.core.redactor import RedactionEngine
from logveil.core.profiles import ProfileManager
from logveil.cli.dispatcher import EngineDispatcher, EngineType
from logveil.cli.args import parse_args, validate_args
from logveil.utils.file_io import read_file_lines, write_file_lines


class LogVeilAgent:
    """Main LogVeil agent orchestrating the sanitization process."""
    
    def __init__(self, args):
        self.args = args
        # Configure console for Windows compatibility
        import platform
        if platform.system() == "Windows":
            # Force UTF-8 encoding for Windows and disable fancy spinners
            self.console = Console(
                color_system=None if args.no_color else "auto",
                force_terminal=True,
                legacy_windows=False
            )
        else:
            self.console = Console(color_system=None if args.no_color else "auto")
        
        # Initialize core components
        self.dispatcher = EngineDispatcher()
        self.profile_manager = ProfileManager(args.profiles_dir)
        self.redaction_engine = RedactionEngine()
        
        # Configure engine based on args
        self._configure_engine()
        
        # Load profile if specified
        if args.profile:
            self._load_profile(args.profile)
    
    def _configure_engine(self):
        """Configure the redaction engine based on CLI arguments."""
        config = {
            'entropy_threshold': self.args.entropy_threshold,
            'entropy_min_length': self.args.entropy_min_length,
            'enable_entropy_detection': not self.args.disable_entropy,
            'trace_enabled': bool(self.args.trace)
        }
        self.redaction_engine.configure(config)
    
    def _load_profile(self, profile_name: str):
        """Load and apply a redaction profile."""
        profile = self.profile_manager.get_profile(profile_name)
        if not profile:
            self.console.print(f"[red]Error:[/red] Profile '{profile_name}' not found.")
            self.console.print(f"Available profiles: {', '.join(self.profile_manager.list_profiles())}")
            sys.exit(1)
        
        # Apply profile patterns to engine
        for rule in profile.patterns:
            if rule.enabled:
                self.redaction_engine.pattern_registry.add_pattern(
                    f"profile_{rule.pattern}", 
                    rule.pattern
                )
        
        # Apply entropy config from profile
        if profile.entropy_config:
            self.redaction_engine.configure(profile.entropy_config)
        
        if not self.args.quiet:
            self.console.print(f"[green]LOADED[/green] Profile: {profile.name}")
    
    def run(self) -> int:
        """Main execution entry point."""
        try:
            # Handle special modes
            if self.args.list_profiles:
                return self._list_profiles()
            
            if self.args.list_engines:
                return self._list_engines()
            
            if self.args.benchmark:
                return self._run_benchmark()
            
            if self.args.serve:
                return self._start_server()
            
            # Main sanitization mode
            return self._sanitize_files()
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operation cancelled by user.[/yellow]")
            return 130
        except Exception as e:
            self.console.print(f"[red]Error:[/red] {str(e)}")
            if self.args.verbose >= 2:
                import traceback
                traceback.print_exc()
            return 1
    
    def _list_profiles(self) -> int:
        """List all available redaction profiles."""
        table = Table(title="Available Redaction Profiles")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="dim")
        table.add_column("Format", style="green")
        table.add_column("Patterns", justify="right")
        table.add_column("Key Paths", justify="right")
        
        for name in self.profile_manager.list_profiles():
            profile = self.profile_manager.get_profile(name)
            table.add_row(
                name,
                profile.description,
                profile.log_format.value,
                str(len(profile.patterns)),
                str(len(profile.key_paths))
            )
        
        self.console.print(table)
        return 0
    
    def _list_engines(self) -> int:
        """List all available execution engines."""
        table = Table(title="Available Execution Engines")
        table.add_column("Engine", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Version", style="dim")
        table.add_column("Performance", justify="right")
        table.add_column("Path", style="dim")
        
        status_info = self.dispatcher.get_engine_status()
        
        for engine_name, info in status_info.items():
            status = "Available" if info["available"] else "Not Available"
            version = info["version"] or "Unknown"
            score = str(info["performance_score"])
            path = info["binary_path"] or info["ffi_library"] or "Built-in"
            
            table.add_row(engine_name.upper(), status, version, score, path)
        
        # Show optimal selection
        optimal = self.dispatcher.select_optimal_engine()
        self.console.print(table)
        self.console.print(f"\nOptimal Engine: {optimal.engine_type.value.upper()}")
        return 0
    
    def _run_benchmark(self) -> int:
        """Run performance benchmark."""
        self.console.print("Running LogVeil Performance Benchmark...")
        
        # Generate sample data
        test_lines = [
            "2024-01-15 10:30:45 [INFO] User login: user@example.com from 192.168.1.100",
            "2024-01-15 10:31:12 [WARN] Failed authentication attempt from 10.0.0.45",
            "2024-01-15 10:31:20 [INFO] JWT issued: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature",
            "2024-01-15 10:32:01 [DEBUG] Database query: SELECT * FROM users WHERE id=12345",
            "2024-01-15 10:32:15 [ERROR] API key validation failed: sk-1234567890abcdef",
        ] * 1000  # 5000 lines total
        
        start_time = time.time()
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task("Benchmarking redaction...", total=len(test_lines))
            
            redacted_count = 0
            for line in test_lines:
                redacted_line, traces = self.redaction_engine.redact_line(line)
                redacted_count += len(traces)
                progress.update(task, advance=1)
        
        end_time = time.time()
        duration = end_time - start_time
        lines_per_second = len(test_lines) / duration
        
        # Display results
        results_table = Table(title="Benchmark Results")
        results_table.add_column("Metric", style="cyan")
        results_table.add_column("Value", style="green")
        
        results_table.add_row("Lines Processed", f"{len(test_lines):,}")
        results_table.add_row("Total Redactions", f"{redacted_count:,}")
        results_table.add_row("Processing Time", f"{duration:.2f} seconds")
        results_table.add_row("Lines per Second", f"{lines_per_second:.0f}")
        results_table.add_row("Engine Used", self.dispatcher.select_optimal_engine().engine_type.value.upper())
        
        self.console.print(results_table)
        return 0
    
    def _start_server(self) -> int:
        """Start the LogVeil API server."""
        try:
            from serve.api import create_app
            import uvicorn
            
            self.console.print(f"Starting LogVeil API server on {self.args.host}:{self.args.port}")
            self.console.print(f"API docs will be available at http://{self.args.host}:{self.args.port}/docs")
            
            app = create_app(self.redaction_engine, self.profile_manager)
            uvicorn.run(app, host=self.args.host, port=self.args.port)
            
        except ImportError:
            self.console.print("[red]Error:[/red] Server dependencies not installed. Install with: pip install 'logveil[server]'")
            return 1
        except Exception as e:
            self.console.print(f"[red]Server error:[/red] {str(e)}")
            return 1
    
    def _sanitize_files(self) -> int:
        """Main file sanitization process."""
        input_path = Path(self.args.input)
        
        # Determine files to process
        if input_path.is_file():
            files_to_process = [input_path]
        elif input_path.is_dir():
            if self.args.recursive:
                files_to_process = list(input_path.rglob("*"))
                files_to_process = [f for f in files_to_process if f.is_file()]
            else:
                files_to_process = [f for f in input_path.iterdir() if f.is_file()]
        else:
            self.console.print(f"[red]Error:[/red] Input path '{input_path}' is not a file or directory.")
            return 1
        
        # Filter log files (basic heuristic)
        log_extensions = {'.log', '.txt', '.out', '.err', '.json', '.yaml', '.yml'}
        files_to_process = [f for f in files_to_process if f.suffix.lower() in log_extensions or 'log' in f.name.lower()]
        
        if not files_to_process:
            self.console.print("[yellow]No log files found to process.[/yellow]")
            return 0
        
        # Preview mode
        if self.args.preview:
            return self._preview_redactions(files_to_process[:5])  # Limit to 5 files for preview
        
        # Process files
        return self._process_files(files_to_process)
    
    def _preview_redactions(self, files: List[Path]) -> int:
        """Show preview of redactions."""
        for file_path in files[:1]:  # Show preview for first file only
            self.console.print(f"\n[bold cyan]Preview for {file_path}:[/bold cyan]")
            
            table = Table(title=f"Redaction Preview: {file_path.name}")
            table.add_column("Line #", style="dim", width=6)
            table.add_column("Original", style="red", no_wrap=False)
            table.add_column("Redacted", style="green", no_wrap=False)
            table.add_column("Changes", style="yellow", width=8)
            
            try:
                lines = read_file_lines(str(file_path))
                for i, line in enumerate(lines[:10], 1):  # Show first 10 lines
                    redacted_line, traces = self.redaction_engine.redact_line(line, i, str(file_path))
                    changes = len(traces)
                    
                    table.add_row(
                        str(i),
                        line.strip()[:80] + ("..." if len(line.strip()) > 80 else ""),
                        redacted_line.strip()[:80] + ("..." if len(redacted_line.strip()) > 80 else ""),
                        str(changes) if changes > 0 else "-"
                    )
                
                self.console.print(table)
                
            except Exception as e:
                self.console.print(f"[red]Error reading {file_path}:[/red] {str(e)}")
        
        return 0
    
    def _process_files(self, files: List[Path]) -> int:
        """Process files for sanitization."""
        stats_summary = {"files_processed": 0, "total_redactions": 0, "errors": 0}
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=self.console,
            disable=self.args.quiet
        ) as progress:
            
            main_task = progress.add_task("Processing files...", total=len(files))
            
            for file_path in files:
                try:
                    file_task = progress.add_task(f"Processing {file_path.name}", total=None)
                    
                    # Read file
                    lines = read_file_lines(str(file_path))
                    
                    # Process lines
                    redacted_lines = []
                    all_traces = []
                    
                    for line_num, line in enumerate(lines, 1):
                        redacted_line, traces = self.redaction_engine.redact_line(line, line_num, str(file_path))
                        redacted_lines.append(redacted_line)
                        all_traces.extend(traces)
                    
                    # Write output
                    if not self.args.dry_run:
                        if self.args.inplace:
                            output_path = file_path
                        elif self.args.output:
                            output_path = Path(self.args.output)
                            if output_path.is_dir():
                                output_path = output_path / file_path.name
                        else:
                            output_path = file_path.with_suffix(f".redacted{file_path.suffix}")
                        
                        # Write output based on format
                        if self.args.format == "json":
                            # JSON format output
                            output_data = {
                                "file": str(file_path),
                                "sanitized_lines": redacted_lines,
                                "summary": {
                                    "lines_processed": len(redacted_lines),
                                    "redactions_made": len(all_traces),
                                    "profile_used": self.args.profile
                                },
                                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                            }
                            with open(output_path, 'w', encoding='utf-8') as f:
                                json.dump(output_data, f, indent=2, ensure_ascii=False)
                        else:
                            # Text format output (default)
                            write_file_lines(str(output_path), redacted_lines)
                    
                    # Save traces if requested
                    if self.args.trace and all_traces:
                        trace_file = Path(self.args.trace)
                        if len(files) > 1:
                            # Multiple files: create separate trace files
                            trace_file = trace_file.with_name(f"{trace_file.stem}_{file_path.stem}{trace_file.suffix}")
                        
                        self.redaction_engine.traces = all_traces
                        self.redaction_engine.export_traces_json(trace_file)
                    
                    stats_summary["files_processed"] += 1
                    stats_summary["total_redactions"] += len(all_traces)
                    
                    progress.remove_task(file_task)
                    progress.update(main_task, advance=1)
                    
                except Exception as e:
                    self.console.print(f"[red]Error processing {file_path}:[/red] {str(e)}")
                    stats_summary["errors"] += 1
                    progress.update(main_task, advance=1)
        
        # Show summary
        if self.args.stats and not self.args.quiet:
            self._show_stats_summary(stats_summary)
        
        return 0 if stats_summary["errors"] == 0 else 1
    
    def _show_stats_summary(self, stats: Dict[str, int]):
        """Display processing statistics summary."""
        panel_content = f"""
[green]Files Processed:[/green] {stats['files_processed']}
[yellow]Total Redactions:[/yellow] {stats['total_redactions']}
[red]Errors:[/red] {stats['errors']}

[bold]Redaction Engine Stats:[/bold]
{self._format_engine_stats()}
        """
        
        panel = Panel(
            panel_content.strip(),
            title="Processing Summary",
            border_style="green"
        )
        self.console.print(panel)
    
    def _format_engine_stats(self) -> str:
        """Format redaction engine statistics."""
        engine_stats = self.redaction_engine.get_stats()
        
        lines = [
            f"Lines Processed: {engine_stats.total_lines_processed:,}",
            f"Total Redactions: {engine_stats.total_redactions:,}",
            f"Entropy Detections: {engine_stats.entropy_detections:,}",
        ]
        
        if engine_stats.redactions_by_pattern:
            lines.append("Pattern Matches:")
            for pattern, count in engine_stats.redactions_by_pattern.items():
                lines.append(f"  {pattern}: {count:,}")
        
        return "\n".join(lines)


def main():
    """Main CLI entry point."""
    args = parse_args()
    
    # Validate arguments
    if not validate_args(args):
        return 1
    
    # Initialize and run agent
    agent = LogVeilAgent(args)
    return agent.run()


if __name__ == "__main__":
    sys.exit(main())


