package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"time"

	"simulation_engine/internal/config"
	"simulation_engine/internal/simulation"
)

func main() {
	// Command-line flags
	gameID := flag.String("game", "", "Game ID (e.g., 0_0_lines_v6)")
	mode := flag.String("mode", "", "Bet mode (e.g., base)")
	numSims := flag.Int("sims", 100000, "Number of simulations")
	threads := flag.Int("threads", 10, "Number of threads")
	batchSize := flag.Int("batch", 50000, "Batch size")
	compress := flag.Bool("compress", true, "Enable compression")
	configPath := flag.String("config", "", "Path to config file (optional)")
	flag.Parse()

	// Validate required flags
	if *gameID == "" || *mode == "" {
		fmt.Fprintf(os.Stderr, "Error: --game and --mode are required\n")
		flag.Usage()
		os.Exit(1)
	}

	startTime := time.Now()

	// Load configuration
	cfg, err := config.Load(*gameID, *mode, *configPath)
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Create simulation runner
	runner := simulation.NewRunner(cfg)

	// Run simulations
	fmt.Printf("Starting simulations for game: %s, mode: %s\n", *gameID, *mode)
	fmt.Printf("Simulations: %d, Threads: %d, Batch: %d\n", *numSims, *threads, *batchSize)

	err = runner.Run(*numSims, *threads, *batchSize, *compress)
	if err != nil {
		log.Fatalf("Simulation failed: %v", err)
	}

	elapsed := time.Since(startTime)
	fmt.Printf("\nSimulations completed in %.2f seconds (%.2f minutes)\n",
		elapsed.Seconds(), elapsed.Minutes())
}




