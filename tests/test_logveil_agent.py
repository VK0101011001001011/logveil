import subprocess
import os
import json

def test_logveil_agent():
    input_file = "../sample_log.txt"
    output_file = "../cleaned_sample.log"

    # Run logveil-agent.py
    subprocess.run(["python3", "../cli/logveil-agent.py", input_file, output_file, "--profile", "auto"], check=True)

    # Assert output file exists
    assert os.path.exists(output_file), "Output file not created"

    # Validate JSON output
    with open(output_file, "r") as outfile:
        output_data = json.load(outfile)

    assert "file" in output_data, "Missing 'file' in output JSON"
    assert "sanitized_lines" in output_data, "Missing 'sanitized_lines' in output JSON"
    assert "summary" in output_data, "Missing 'summary' in output JSON"
    assert "timestamp" in output_data, "Missing 'timestamp' in output JSON"

    print("Functional test passed!")

if __name__ == "__main__":
    test_logveil_agent()
