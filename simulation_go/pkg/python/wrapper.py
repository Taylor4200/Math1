"""
Python wrapper for Go simulation engine.

This module provides a Python interface to call Go simulations,
similar to how OptimizationExecution calls Rust optimizer.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Path to Go binary (adjust based on your build location)
GO_BIN_DIR = Path(__file__).parent.parent.parent / "cmd" / "simulator"
GO_BINARY = GO_BIN_DIR / "sim_engine.exe"  # Windows
if not GO_BINARY.exists():
    GO_BINARY = GO_BIN_DIR / "sim_engine"  # Linux/macOS

PROJECT_PATH = Path(__file__).parent.parent.parent.parent


class GoSimulationExecution:
    """Handles execution of Go simulation engine from Python."""

    @staticmethod
    def run_sims_single_mode(
        game_config,
        mode: str,
        num_sims: int = 100000,
        threads: int = 10,
        batch_size: int = 50000,
        compress: bool = True,
    ):
        """
        Run simulations for a single mode using Go engine.
        
        Args:
            game_config: GameConfig object
            mode: Bet mode name (e.g., "base")
            num_sims: Number of simulations to run
            threads: Number of threads
            batch_size: Batch size for processing
            compress: Enable compression
        """
        start_time = time.time()

        print("\n" + "=" * 80)
        print(f"GO SIMULATIONS STARTING: {mode}")
        print("=" * 80)
        print(f"Game ID: {game_config.game_id}")
        print(f"Mode: {mode}")
        print(f"Simulations: {num_sims:,}")
        print(f"Threads: {threads}")
        print(f"Batch Size: {batch_size:,}")
        print(f"Compression: {compress}")
        print("=" * 80 + "\n")

        # Build command
        cmd = [
            str(GO_BINARY),
            "--game", game_config.game_id,
            "--mode", mode,
            "--sims", str(num_sims),
            "--threads", str(threads),
            "--batch", str(batch_size),
        ]

        if compress:
            cmd.append("--compress")

        # Change to project directory
        os.chdir(PROJECT_PATH)

        # Check if binary exists
        if not GO_BINARY.exists():
            raise FileNotFoundError(
                f"Go binary not found at {GO_BINARY}.\n"
                f"Please build it first: cd simulation_go && go build -o cmd/simulator/sim_engine.exe ./cmd/simulator"
            )

        print(f"[PYTHON] Starting Go simulation binary...")
        print(f"[PYTHON] Executing: {' '.join(cmd)}")
        print(f"[PYTHON] Working directory: {PROJECT_PATH}")
        print(f"[PYTHON] Streaming output in real-time...\n")
        sys.stdout.flush()

        # Run Go binary and stream output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=str(PROJECT_PATH),
        )

        # Stream output line by line
        try:
            for line in process.stdout:
                print(line, end="")
                sys.stdout.flush()
        except KeyboardInterrupt:
            process.terminate()
            raise

        # Wait for completion
        return_code = process.wait()
        if return_code != 0:
            raise RuntimeError(f"Go simulation failed with exit code {return_code}")

        elapsed = time.time() - start_time
        print(f"\n{'=' * 80}")
        print(f"GO SIMULATIONS COMPLETED: {mode}")
        print(f"Total Time: {elapsed:.2f} seconds ({elapsed / 60:.2f} minutes)")
        print(f"{'=' * 80}\n")

    @staticmethod
    def run_sims_all_modes(game_config, modes_to_run: list, num_sims: dict, threads: int, batch_size: int, compress: bool = True):
        """
        Run simulations for all specified modes.
        
        Args:
            game_config: GameConfig object
            modes_to_run: List of mode names
            num_sims: Dict mapping mode names to simulation counts
            threads: Number of threads
            batch_size: Batch size
            compress: Enable compression
        """
        for mode in modes_to_run:
            if mode in num_sims and num_sims[mode] > 0:
                GoSimulationExecution.run_sims_single_mode(
                    game_config=game_config,
                    mode=mode,
                    num_sims=num_sims[mode],
                    threads=threads,
                    batch_size=batch_size,
                    compress=compress,
                )


# Example usage (for testing)
if __name__ == "__main__":
    # This would be called from run.py like:
    # from simulation_go.pkg.python.wrapper import GoSimulationExecution
    # execution = GoSimulationExecution()
    # execution.run_sims_single_mode(config, "base", 100000, 10, 50000, True)
    pass


















