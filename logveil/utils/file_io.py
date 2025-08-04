import os
from pathlib import Path
from typing import Generator

def read_file_lines(file_path: str, show_progress: bool = False) -> Generator[str, None, None]:
    """
    Read a file line by line, optionally showing a progress bar.

    Args:
        file_path (str): Path to the file to read.
        show_progress (bool): Whether to show a progress bar.

    Yields:
        str: Lines from the file.
    """
    file_size = os.path.getsize(file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        if show_progress:
            # Simple progress simulation without external dependencies
            lines_processed = 0
            print(f"Reading file: {file_path} ({file_size} bytes)")
            for line in file:
                yield line
                lines_processed += 1
                if lines_processed % 1000 == 0:
                    print(f"Processed {lines_processed} lines...")
        else:
            for line in file:
                yield line

def write_file_lines(file_path: str, lines: Generator[str, None, None]):
    """
    Write lines to a file.

    Args:
        file_path (str): Path to the file to write.
        lines (Generator[str, None, None]): Lines to write.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        for line in lines:
            file.write(line)

def safe_overwrite(file_path: str, lines: Generator[str, None, None]):
    """
    Safely overwrite a file by writing to a temporary file first.

    Args:
        file_path (str): Path to the file to overwrite.
        lines (Generator[str, None, None]): Lines to write.
    """
    temp_file = Path(file_path).with_suffix(".tmp")
    write_file_lines(temp_file, lines)
    temp_file.replace(file_path)
