import difflib

def generate_html_diff(original_lines, sanitized_lines, output_path):
    """
    Generate an HTML diff report showing side-by-side comparison of original and sanitized logs.

    Args:
        original_lines (list): List of original log lines.
        sanitized_lines (list): List of sanitized log lines.
        output_path (str): Path to save the HTML report.
    """
    diff = difflib.HtmlDiff().make_file(original_lines, sanitized_lines, fromdesc="Original", todesc="Sanitized")

    with open(output_path, "w", encoding="utf-8") as html_file:
        html_file.write(diff)

if __name__ == "__main__":
    # Example usage
    original = ["User john.doe@company.com logged in from 192.168.1.100"]
    sanitized = ["User [REDACTED_EMAIL] logged in from [REDACTED_IP]"]
    generate_html_diff(original, sanitized, "report.html")
