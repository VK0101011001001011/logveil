package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"time"
)

// RedactedLine represents a processed log line
type RedactedLine struct {
	Line      string   `json:"line"`
	Timestamp string   `json:"timestamp,omitempty"`
	Errors    []string `json:"errors,omitempty"`
}

// ProcessResult represents the overall processing result
type ProcessResult struct {
	Success        bool     `json:"success"`
	LinesProcessed int      `json:"lines_processed"`
	Errors         []string `json:"errors,omitempty"`
	Duration       string   `json:"duration"`
}

func main() {
	if len(os.Args) < 3 {
		log.Fatalf("Usage: %s <input_file> <output_file>", os.Args[0])
	}

	inputFile := os.Args[1]
	outputFile := os.Args[2]

	// Validate input file exists
	if _, err := os.Stat(inputFile); os.IsNotExist(err) {
		log.Fatalf("Input file does not exist: %s", inputFile)
	}

	result, err := processLogFile(inputFile, outputFile)
	if err != nil {
		log.Fatalf("Processing failed: %v", err)
	}

	// Output result as JSON for structured logging
	if resultJSON, err := json.Marshal(result); err == nil {
		fmt.Println(string(resultJSON))
	}
}

func processLogFile(inputPath, outputPath string) (*ProcessResult, error) {
	startTime := time.Now()

	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Prepare command
	cmd := exec.CommandContext(ctx, "python3", "../cli/logveil_agent.py", inputPath, outputPath)

	// Capture both stdout and stderr
	output, err := cmd.CombinedOutput()

	result := &ProcessResult{
		Success:  err == nil,
		Duration: time.Since(startTime).String(),
	}

	if err != nil {
		if ctx.Err() == context.DeadlineExceeded {
			result.Errors = append(result.Errors, "Process timed out after 30 seconds")
		} else {
			result.Errors = append(result.Errors, fmt.Sprintf("Process failed: %v", err))
		}

		if len(output) > 0 {
			result.Errors = append(result.Errors, fmt.Sprintf("Output: %s", string(output)))
		}

		return result, fmt.Errorf("command failed: %v", err)
	}

	return result, nil
}
