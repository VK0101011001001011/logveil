package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"time"
)

type RedactedLine struct {
	Line string `json:"line"`
}

func main() {
	if len(os.Args) < 3 {
		log.Fatalf("Usage: go-wrapper <input_file> <output_file>")
	}

	inputFile := os.Args[1]
	outputFile := os.Args[2]

	cmd := exec.Command("python3", "../cli/logveil-agent.py", inputFile, outputFile)

	// Capture stderr
	stderr, err := cmd.StderrPipe()
	if err != nil {
		log.Fatalf("Failed to capture stderr: %v", err)
	}

	// Set timeout
	timeout := time.AfterFunc(30*time.Second, func() {
		cmd.Process.Kill()
		log.Fatalf("Process timed out")
	})
	defer timeout.Stop()

	// Start the process
	if err := cmd.Start(); err != nil {
		log.Fatalf("Failed to start process: %v", err)
	}

	// Read stderr
	go func() {
		buf := make([]byte, 1024)
		for {
			n, err := stderr.Read(buf)
			if n > 0 {
				log.Printf("stderr: %s", string(buf[:n]))
			}
			if err != nil {
				break
			}
		}
	}()

	// Wait for the process to finish
	if err := cmd.Wait(); err != nil {
		log.Fatalf("Process failed: %v", err)
	}

	log.Println("Process completed successfully")

	out, err := cmd.Output()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}

	var lines []RedactedLine
	err = json.Unmarshal(out, &lines)
	if err != nil {
		panic(err)
	}

	for _, l := range lines {
		fmt.Println(l.Line)
	}
}
