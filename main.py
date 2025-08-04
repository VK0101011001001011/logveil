import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from core.sanitizer import sanitize_line
from cli.args import parse_args
from utils.file_io import read_file_lines, write_file_lines, safe_overwrite

console = Console()

def main():
    args = parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        console.print(f"[red]Error:[/red] File '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if args.inplace and args.output:
        console.print("[red]Error:[/red] Cannot use --inplace and --output together.", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else None

    if args.preview:
        table = Table(title="Preview Sanitization", show_lines=True)
        table.add_column("Original Line", style="dim")
        table.add_column("Sanitized Line", style="bold")

        for line in read_file_lines(str(input_path)):
            sanitized_line, _ = sanitize_line(line)
            table.add_row(line.strip(), sanitized_line.strip())

        console.print(table)
        sys.exit(0)

    if args.dry_run:
        console.print("[yellow]Dry-run mode enabled. No changes will be written to files.[/yellow]")

    sanitized_lines = []
    match_counts = {}

    with Progress() as progress:
        task = progress.add_task("Sanitizing", total=input_path.stat().st_size) if args.progress else None

        for line in read_file_lines(str(input_path)):
            sanitized_line, counts = sanitize_line(line)
            sanitized_lines.append(sanitized_line)

            for key, count in counts.items():
                match_counts[key] = match_counts.get(key, 0) + count

            if args.progress:
                progress.update(task, advance=len(line))

    if not args.dry_run:
        if args.inplace:
            safe_overwrite(str(input_path), iter(sanitized_lines))
        elif output_path:
            write_file_lines(str(output_path), iter(sanitized_lines))
        else:
            for line in sanitized_lines:
                console.print(line, end="")

    if args.format == "json":
        import json
        metadata = {
            "redaction_counts": match_counts,
            "timestamp": str(input_path.stat().st_mtime),
            "original_file": str(input_path)
        }
        output = {
            "sanitized_lines": sanitized_lines,
            "metadata": metadata
        }
        console.print(json.dumps(output, indent=4))
        sys.exit(0)

    if args.summary:
        console.print("\n[bold]Sanitization Summary:[/bold]")
        for key, count in match_counts.items():
            console.print(f"[green]{key}:[/green] {count}")

if __name__ == "__main__":
    main()
