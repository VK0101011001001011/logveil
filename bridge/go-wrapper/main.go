package main

import (
	"os/exec"
	"fmt"
	"encoding/json"
)

type RedactedLine struct {
	Line string `json:"line"`
}

func main() {
	cmd := exec.Command("python3", "../cli/logveil-agent.py", "--input", "sample.log", "--format", "json", "--dry-run")
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
