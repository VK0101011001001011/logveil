import os
import subprocess
import sys
import json
from datetime import datetime
from core.sanitizer import SanitizerEngine
import argparse
import configparser

# Check backend availability
def rust_backend_available():
    return os.path.exists("/path/to/rust_binary")

def go_binary_available():
    return os.path.exists("/path/to/go_binary")

def call_rust(input_file, output_file):
    subprocess.run(["/path/to/rust_binary", input_file, output_file], check=True)

def call_go(input_file, output_file):
    subprocess.run(["/path/to/go_binary", input_file, output_file], check=True)

def use_python_engine(input_file, output_file, detect_entropy=False, trace_output=None, profile_dir="profiles"):
    engine = SanitizerEngine()
    engine.load_profiles(profile_dir)
    with open(input_file, "r") as infile:
        lines = infile.readlines()

    sanitized_lines = [engine.sanitize_line(line, detect_entropy=detect_entropy, trace=bool(trace_output), trace_file=trace_output) for line in lines]
    summary = engine.get_stats()

    output = {
        "file": input_file,
        "sanitized_lines": sanitized_lines,
        "summary": summary,
        "timestamp": datetime.now().isoformat()
    }

    with open(output_file, "w") as outfile:
        json.dump(output, outfile, indent=4)

# Define log profiles
def apply_profile(profile, lines):
    if profile == "apache":
        # Apply Apache log sanitization rules
        pass
    elif profile == "json":
        # Apply JSON log sanitization rules
        pass
    elif profile == "auto":
        # Use heuristics to guess log type
        pass
    return lines

# Load configuration from .logveilrc
def load_config():
    config = configparser.ConfigParser()
    config.read(".logveilrc")
    return config

def process_folder(input_folder, output_folder, detect_entropy, trace_output, profile_dir):
    engine = SanitizerEngine()
    engine.load_profiles(profile_dir)

    summary = {key: 0 for key in engine.stats.keys()}
    files_processed = 0

    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.startswith(".") or not file.endswith((".log", ".txt", ".json")):
                continue

            input_path = os.path.join(root, file)
            relative_path = os.path.relpath(root, input_folder)
            output_subfolder = os.path.join(output_folder, relative_path)
            os.makedirs(output_subfolder, exist_ok=True)

            output_path = os.path.join(output_subfolder, f"{file}.redacted.log")

            try:
                with open(input_path, "r") as infile:
                    lines = infile.readlines()

                sanitized_lines = [engine.sanitize_line(line, detect_entropy=detect_entropy, trace=bool(trace_output), trace_file=trace_output) for line in lines]
                file_summary = engine.get_stats()

                for key, value in file_summary.items():
                    summary[key] += value

                with open(output_path, "w") as outfile:
                    outfile.write("\n".join(sanitized_lines))

                files_processed += 1

            except Exception as e:
                print(f"Error processing {input_path}: {e}")

    final_summary = {
        "files_processed": files_processed,
        "total_redactions": summary
    }

    return final_summary

# Main CLI logic
def main():
    config = load_config()

    parser = argparse.ArgumentParser(description="Log sanitization tool")
    parser.add_argument("--input", help="Path to the input file or folder")
    parser.add_argument("--output-dir", type=str, help="Directory to save sanitized files")
    parser.add_argument("--profile", choices=["apache", "json", "auto"], default=config.get("DEFAULT", "profile", fallback="auto"), help="Log profile to apply")
    parser.add_argument("--profile-dir", type=str, default="profiles", help="Directory containing redaction profiles")
    parser.add_argument("--detect-entropy", action="store_true", help="Enable entropy-based secret detection")
    parser.add_argument("--trace-output", type=str, help="Path to trace log file")
    parser.add_argument("--policy", type=str, help="Path to the redaction policy file (YAML)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Input format (text or JSON)")
    parser.add_argument("--plugins-dir", type=str, help="Directory containing custom plugins")
    parser.add_argument("--html-report", type=str, help="Path to save the HTML diff report")
    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output_dir
    profile = args.profile
    detect_entropy = args.detect_entropy
    trace_output = args.trace_output
    profile_dir = args.profile_dir
    policy_path = args.policy
    input_format = args.format
    plugins_dir = args.plugins_dir
    html_report_path = args.html_report

    engine = SanitizerEngine()

    if plugins_dir:
        engine.load_plugins(plugins_dir)

    if input_format == "json":
        with open(input_path, "r", encoding="utf-8") as infile:
            json_data = json.load(infile)

        schema = {"redact": ["user.email", "user.token", "client.ip"]}  # Example schema
        redacted_data = engine.redact_json(json_data, schema)

        with open(output_dir, "w", encoding="utf-8") as outfile:
            json.dump(redacted_data, outfile, indent=4)

        if html_report_path:
            original_lines = json.dumps(json_data, indent=4).splitlines()
            sanitized_lines = json.dumps(redacted_data, indent=4).splitlines()
            from tools.html_diff_viewer import generate_html_diff
            generate_html_diff(original_lines, sanitized_lines, html_report_path)
    else:
        if os.path.isdir(input_path):
            final_summary = process_folder(input_path, output_dir, detect_entropy, trace_output, profile_dir)
            print(json.dumps(final_summary, indent=4))
        else:
            with open(input_path, "r") as infile:
                original_lines = infile.readlines()

            sanitized_lines = [engine.apply_plugins(line) for line in original_lines]
            sanitized_lines = [engine.apply_redaction_policy(line, file_name=input_path) for line in sanitized_lines]

            with open(output_dir, "w") as outfile:
                outfile.write("\n".join(sanitized_lines))

            if html_report_path:
                from tools.html_diff_viewer import generate_html_diff
                generate_html_diff(original_lines, sanitized_lines, html_report_path)

if __name__ == "__main__":
    main()
