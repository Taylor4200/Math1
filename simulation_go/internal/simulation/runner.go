package simulation

import (
	"fmt"
	"log"
	"sync"

	"simulation_engine/internal/config"
)

// Runner manages simulation execution
type Runner struct {
	config *config.Config
}

// NewRunner creates a new simulation runner
func NewRunner(cfg *config.Config) *Runner {
	return &Runner{
		config: cfg,
	}
}

// Run executes simulations with the specified parameters
func (r *Runner) Run(numSims, threads, batchSize int, compress bool) error {
	fmt.Printf("Running %d simulations with %d threads (batch size: %d)\n",
		numSims, threads, batchSize)

	// Calculate work distribution
	simsPerThread := numSims / threads
	if numSims%threads != 0 {
		return fmt.Errorf("numSims (%d) must be divisible by threads (%d)", numSims, threads)
	}

	batchesPerThread := simsPerThread / batchSize
	if simsPerThread%batchSize != 0 {
		return fmt.Errorf("simsPerThread (%d) must be divisible by batchSize (%d)",
			simsPerThread, batchSize)
	}

	// Channel for results
	resultChan := make(chan error, threads)
	var wg sync.WaitGroup

	// Start worker goroutines
	for threadID := 0; threadID < threads; threadID++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()

			startSim := id * simsPerThread
			err := r.runThread(id, startSim, batchesPerThread, batchSize, compress)
			resultChan <- err
		}(threadID)
	}

	// Wait for all threads to complete
	wg.Wait()
	close(resultChan)

	// Check for errors
	for err := range resultChan {
		if err != nil {
			return fmt.Errorf("thread error: %w", err)
		}
	}

	fmt.Println("All threads completed successfully")
	return nil
}

// runThread runs simulations for a single thread
func (r *Runner) runThread(threadID, startSim, numBatches, batchSize int, compress bool) error {
	log.Printf("Thread %d: Starting simulations %d-%d",
		threadID, startSim, startSim+(numBatches*batchSize)-1)

	for batch := 0; batch < numBatches; batch++ {
		batchStart := startSim + (batch * batchSize)
		batchEnd := batchStart + batchSize

		// TODO: Implement actual simulation logic
		// For now, just log progress
		if batch%10 == 0 {
			log.Printf("Thread %d: Batch %d/%d (sims %d-%d)",
				threadID, batch+1, numBatches, batchStart, batchEnd-1)
		}

		// Placeholder: Run batch of simulations
		if err := r.runBatch(threadID, batchStart, batchSize, compress); err != nil {
			return fmt.Errorf("batch %d failed: %w", batch, err)
		}
	}

	return nil
}

// runBatch runs a single batch of simulations
func (r *Runner) runBatch(threadID, startSim, batchSize int, compress bool) error {
	// TODO: Implement actual game simulation
	// This is where you'd:
	// 1. Create GameState for this batch
	// 2. Run simulations (call RunSpin for each sim)
	// 3. Collect books/results
	// 4. Write to file (with compression if enabled)

	// Placeholder implementation
	_ = threadID
	_ = startSim
	_ = batchSize
	_ = compress

	return nil
}




