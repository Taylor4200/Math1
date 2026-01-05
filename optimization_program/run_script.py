import json
import subprocess
import os
from src.config.paths import PATH_TO_GAMES, SETUP_PATH, OPTIMIZATION_PATH, PROJECT_PATH


class OptimizationExecution:
    """Handles execution of Rust optimization algorithm from python."""

    @staticmethod
    def load_math_config(filename: str) -> dict:
        """Load optimization parameter config file."""
        with open(filename, "r", encoding="UTF-8") as f:
            data = json.load(f)
        return data

    @staticmethod
    def run_opt_single_mode(game_config, mode, threads):
        """Create setup txt file for a single mode and run Rust executable binary."""
        import time
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"OPTIMIZATION STARTING: {mode}")
        print(f"{'='*80}")
        print(f"Game ID: {game_config.game_id}")
        print(f"Rust Threads: {threads}")
        
        os.chdir(PROJECT_PATH)
        filename = os.path.join(PATH_TO_GAMES, game_config.game_id, "library", "configs", "math_config.json")
        opt_config = OptimizationExecution.load_math_config(filename)

        opt_config = game_config.opt_params
        params = None
        for idx, obj in opt_config.items():
            if idx == mode:
                params = obj["parameters"]

        assert params is not None, "Could not load optimization parameters."

        print(f"\nOptimization Parameters:")
        print(f"  num_show_pigs: {params['num_show_pigs']}")
        print(f"  num_pigs_per_fence: {params['num_pigs_per_fence']}")
        print(f"  simulation_trials: {params['simulation_trials']}")
        print(f"  test_spins: {params['test_spins']}")
        print(f"  test_spins_weights: {params['test_spins_weights']}")
        print(f"  pmb_rtp: {params['pmb_rtp']}")
        print(f"  min_mean_to_median: {params['min_mean_to_median']}")
        print(f"  max_mean_to_median: {params['max_mean_to_median']}")
        
        setup_file = open(SETUP_PATH, "w", encoding="UTF-8")
        setup_file.write("game_name;" + game_config.game_id + "\n")
        setup_file.write("bet_type;" + mode + "\n")
        setup_file.write("num_show_pigs;" + str(params["num_show_pigs"]) + "\n")
        setup_file.write("num_pigs_per_fence;" + str(params["num_pigs_per_fence"]) + "\n")
        setup_file.write("threads_for_fence_construction;" + str(threads) + "\n")
        setup_file.write("threads_for_show_construction;" + str(threads) + "\n")
        setup_file.write("score_type;" + params["score_type"] + "\n")
        setup_file.write("test_spins;" + str(params["test_spins"]).replace(" ", "") + "\n")
        setup_file.write("test_spins_weights;" + str(params["test_spins_weights"]).replace(" ", "") + "\n")
        setup_file.write("simulation_trials;" + str(params["simulation_trials"]) + "\n")
        setup_file.write("graph_indexes;" + str(0) + "\n")
        setup_file.write("run_1000_batch;" + str(False) + "\n")
        setup_file.write("path_to_games;" + PATH_TO_GAMES + "\n")
        setup_file.write("pmb_rtp;" + str(params["pmb_rtp"]) + "\n")
        setup_file.write("min_mean_to_median;" + str(params["min_mean_to_median"]) + "\n")
        setup_file.write("max_mean_to_median;" + str(params["max_mean_to_median"]) + "\n")
        setup_file.close()
        
        print(f"\nSetup file written. Starting Rust optimization...")
        print(f"{'='*80}\n")
        
        OptimizationExecution.run_rust_script()
        
        elapsed = time.time() - start_time
        print(f"\n{'='*80}")
        print(f"OPTIMIZATION COMPLETED: {mode}")
        print(f"Total Time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
        print(f"{'='*80}\n")

    @staticmethod
    def run_all_modes(game_config, modes_to_run, rust_threads):
        """Loop through all game modes to run"""
        for mode in modes_to_run:
            OptimizationExecution.run_opt_single_mode(game_config, mode, rust_threads)

    @staticmethod
    def run_rust_script():
        """Run compiled binary and stream output to terminal in real-time."""
        import time
        import sys
        start_time = time.time()
        
        print("[PYTHON] Starting Rust optimization binary...")
        cargo_bin_path = os.path.join(os.path.expanduser("~"), ".cargo", "bin")
        updated_path = cargo_bin_path + os.pathsep + os.environ.get("PATH", "")
        
        print("[PYTHON] Executing: cargo run --release")
        print("[PYTHON] Working directory:", OPTIMIZATION_PATH)
        print("[PYTHON] Streaming output in real-time...\n")
        sys.stdout.flush()
        
        # Use Popen to stream output in real-time
        process = subprocess.Popen(
            ["cargo", "run", "--release"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Combine stderr into stdout
            text=True,
            bufsize=1,  # Line buffered
            cwd=OPTIMIZATION_PATH,
            env={**os.environ, "PATH": updated_path},
        )
        
        # Stream output line by line
        try:
            for line in process.stdout:
                print(line, end='')  # Print immediately
                sys.stdout.flush()
            
            process.wait()
            elapsed = time.time() - start_time
            
            if process.returncode == 0:
                print(f"\n[PYTHON] Rust binary completed successfully in {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
            else:
                print(f"\n[PYTHON] ERROR: Rust binary failed with exit code {process.returncode}")
                print(f"[PYTHON] Time elapsed: {elapsed:.2f} seconds")
        except KeyboardInterrupt:
            print("\n[PYTHON] Interrupted by user. Terminating Rust process...")
            process.terminate()
            process.wait()
            raise
