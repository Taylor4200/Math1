Comprehensive Math‑SDK Reference

This document consolidates every relevant detail and nuance from the Math‑SDK documentation available at https://stakeengine.github.io/math-sdk
. It is organised top‑down to guide a new developer through the SDK’s capabilities, installation, architecture, game‑development workflow, optimisation tools, and integration with the Stake RGS platform. Citations accompany factual statements so you can quickly locate the source in the original docs.

1. Introduction & Purpose

Stake Development Kit overview – The Stake Development Kit simplifies creation, simulation and optimisation of slot games. It contains two components: a Math framework for defining game rules, simulating outcomes and creating backend files, and a frontend framework (PixiJS/Svelte) for rendering games that integrates seamlessly with the math outputs
stakeengine.github.io
. Both components leverage the Carrot Remote Gaming Server (RGS) to host and run games on Stake.com
stakeengine.github.io
.

Why use the Math‑SDK? Traditional slot‑development can be slow because each game must be created from scratch. The Math‑SDK provides ready‑made frameworks that allow developers to focus on game design while the SDK handles simulation, optimisation and file generation. It ensures high mathematical precision by using static files (CSV and JSON) that describe every possible outcome and their probabilities
stakeengine.github.io
. The SDK integrates directly with Carrot RGS, enabling easy upload and deployment of games
stakeengine.github.io
.

Target users – Developers or studios aiming to create custom slot games, experiment with mechanics, generate accurate Return‑to‑Player (RTP) tables, and optimise win distributions. Non‑technical product owners can use the provided prototypes for configuration or collaborate with mathematicians for custom games
stakeengine.github.io
.

Static outputs – The SDK outputs game logic files (compressed JSON lines) and lookup tables summarising simulation results. Each simulation result is assigned an ID, probability and final payout multiplier. When the game is played through RGS, a simulation ID is randomly selected proportional to its weight and the corresponding events are returned
stakeengine.github.io
.

2. Engine Setup & Quick Start
2.1 Prerequisites and Installation

Software requirements – Python 3 and pip are required to run the math‑sdk. Rust and Cargo are needed if you plan to use the optimisation algorithm
stakeengine.github.io
. On Linux you can install Rust using the provided curl command; see the docs for details
stakeengine.github.io
.

Repository setup – Clone the math-sdk repository and run the Makefile: make setup. This creates a virtual environment and installs dependencies. To run a game, call make run GAME=<game_id>
stakeengine.github.io
.

Manual installation – Create a virtual environment manually, install dependencies via pip install -r requirements.txt, install the SDK in editable mode (python3 -m pip install -e .), and verify by running a test game
stakeengine.github.io
.

Deactivation – After running, deactivate the virtual environment to clean up
stakeengine.github.io
.

2.2 Running Example Games (Quickstart)

Use the Quickstart guide to run sample games. Navigate into the repo and execute make run GAME=0_0_lines to simulate the “lines” example game
stakeengine.github.io
. The run.py script accepts arguments like number of threads, compression type, simulation counts, etc. These can be adjusted by editing the num_threads, compression, num_sim_args and run_conditions variables in run.py
stakeengine.github.io
.

Simulation parameters – You can run large batches of simulations (e.g., 100 k) across multiple threads (e.g., 20). For long runs set batching_size and scaling_mode. The Quickstart page explains how to adjust variables for debugging or performance and shows how to generate PAR sheets using run_analysis.py
stakeengine.github.io
.

Output analysis – After running simulations, review the generated books and lookup tables:

Books: contain per‑simulation results with events and win breakdowns; used for debugging and front‑end testing
stakeengine.github.io
.

Lookup tables: CSV files summarising simulation ID, probability and final payout; used by optimisation and RGS
stakeengine.github.io
.

Config files: three JSON files (config_math.json, config_fe.json, config.json) hold optimisation parameters, front‑end symbol info and file hashes
stakeengine.github.io
.

3. Required Math File Format

To upload a game to RGS, three file types must be generated
stakeengine.github.io
:

index.json – top‑level descriptor listing each game mode and pointing to the corresponding compressed JSON‑lines file and weight/probability file. Example for a single mode:

[
  {
    "mode": "BASE",
    "cost": 1,
    "eventFile": "0_0_lines_base.jsonl.zst",
    "weightsFile": "lookUpTable_base.csv"
  }
]


For multi‑mode games (e.g., basegame and bonus), list each mode separately with its cost multiplier
stakeengine.github.io
.

Lookup table CSV – Each row contains simulation number, probability, payout multiplier. The simulation number must be sequential starting at 0. Probabilities must sum to 1 and payouts are integers or decimals representing multipliers
stakeengine.github.io
.

Game logic file – Compressed .jsonl.zst file where each line describes the result of a simulation. Each JSON object must contain an id, a list of events (used by the frontend), and a payoutMultiplier
stakeengine.github.io
.

4. SDK Directory Structure

The repository is organised into several top‑level directories
stakeengine.github.io
:

Directory	Description
games/	Sample games showing different win types (lines, ways, cluster, scatter, expanding wilds)
stakeengine.github.io
. Each game folder has its own library of configurations and simulation outputs.
src/	Core SDK functions and classes divided into submodules for calculations, config, events, executables, state management, win evaluation, and data writing
stakeengine.github.io
.
utils/	Helper functions for analysis, file hashing, swapping lookup tables and generating hit‑rate reports
stakeengine.github.io
.
tests/	PyTest functions for validating behaviour.
uploads/	Handles temporary S3 upload tasks
stakeengine.github.io
.
optimization_program/	Contains the Rust optimisation algorithm and configuration classes
stakeengine.github.io
.
5. High‑Level Structure
5.1 State Machine (GameState)

The heart of every game is the GameState class. It manages simulation parameters, game modes, configuration values, RNG seeds, simulation criteria and results
stakeengine.github.io
. It also handles output file creation and interactions with GameExecutables and GameCalculations. Games derive from GameStateOverride to override core functions such as win evaluation or free‑spin logic
stakeengine.github.io
.

Books and lookup tables – A book is a JSON‑line object representing one simulation. Each book entry contains the id, events, payout, basegame/freegame wins and simulation criteria (e.g., win cap, base win, freegame)
stakeengine.github.io
. Books are stored in game/library/books/ and can be compressed. The lookup table summarises final payout multipliers and is used for optimisation and by the RGS for random selection
stakeengine.github.io
.

5.2 Game Structure (Recommended Layout)

Each game folder (games/<game_id>/) follows a structured layout
stakeengine.github.io
:

Library folder: contains subdirectories books/, configs/, forces/, lookup_tables/ for storing outputs.

run.py: entry script defining simulation parameters such as threads, compression, batching, profiling and seeding
stakeengine.github.io
. It calls functions like create_books() and generate_configs() from game_executables.py
stakeengine.github.io
.

game_config.py: defines game parameters such as number of reels and rows, paytable, symbol definitions, trigger conditions, bet modes, etc.

game_executables.py: defines simulation functions like run_spin() and run_freespin() which call underlying logic to draw boards, evaluate wins, handle tumbling, trigger free spins and compute final wins
stakeengine.github.io
.

game_state.py / game_override.py: custom classes that extend GameState to implement game‑specific logic (e.g., multipliers, feature triggers). They override functions such as assign_special_sym_function, run_spin, run_freespin, etc.
stakeengine.github.io
.

Additional helpers: such as payout_override.py for cluster/ways pay group generation, game_calculations.py for miscellaneous calculations like lines or scatter pay evaluation
stakeengine.github.io
.

5.3 Game Format and Configurations

GameConfig – This class defines all static parameters of a game: game ID, provider number, win cap, win type (lines/ways/cluster/scatter), RTP, number of reels/rows, paytable values, special symbols, free‑spin triggers, reel strips and distribution of bet modes
stakeengine.github.io
. Each bet mode sets a cost multiplier and may change reel strips or triggers (see BetMode below).

Run functions – run_spin() seeds the RNG with the simulation number, resets the state, draws the board from reels, evaluates wins, updates the win manager, emits events and checks for free spins; this loop continues until a terminating condition (e.g., no tumble or no free spins) is met
stakeengine.github.io
. run_freespin() replicates the procedure for free spins; both functions must be overridden for each game to implement unique mechanics
stakeengine.github.io
.

Outputs – After simulations, four output categories are generated: books (JSON‑line files), lookup tables, force files, and config files
stakeengine.github.io
. File names are constructed using the OutputFiles class in src/config/output_filenames
stakeengine.github.io
.

6. Gamestate Structure
6.1 Simulation Acceptance & Distribution Criteria

Simulations are pre‑allocated to criteria categories: 0‑win, basegame win, freegame entry, or max win. Each category has a quota defined in Distribution and BetMode classes
stakeengine.github.io
. Quotas ensure enough samples for rare events (e.g., max win) by forcing acceptance of simulations meeting specific criteria.
stakeengine.github.io
.

A Distribution entry defines:

criteria (shorthand name for the event, e.g., fg for freegame or wc for wincap).

quota (fraction of simulations to accept from this criteria).

conditions – optional dictionary controlling the random draw (e.g., forcing wincap or freegame, adjusting reel weights)
stakeengine.github.io
.

win_criteria – optional payout multiplier threshold used to enforce acceptance only when wins exceed a certain multiplier
stakeengine.github.io
.

BetMode: defines game modes with specific cost multipliers, RTP, and quotas for each distribution. Flags include auto_close_disabled, is_feature, is_buybonus. Each BetMode may specify distribution conditions for basegame and freegame entries and values such as reel weights or scatter triggers
stakeengine.github.io
.

6.2 Configs & Symbols

Reels and weights – The GameConfig may define multiple reel strips for basegame and freegame. Reels are represented as arrays of symbols with associated weights; the code randomly selects positions using these weights to draw a board
stakeengine.github.io
.

Scatter triggers and anticipation – You can define scatter symbols that trigger free spins. Anticipation rules delay the reveal of reels if multiple scatters appear to build excitement
stakeengine.github.io
.

Symbol definitions – Each Symbol object has a name (e.g., H1, L4), a special_flag dictionary (wild, scatter), and a paytable value (how much it pays for 3/4/5‑kind). Special functions (e.g., multiplier value) are assigned via assign_special_sym_function()
stakeengine.github.io
.

6.3 Board & Tumble Mechanics

Boards are generated by reading the selected reel strip and slicing a window equal to the number of rows. Anticipation may slow down reveal based on scatter presence
stakeengine.github.io
. Special symbols on the board are tracked and used for triggering events
stakeengine.github.io
.

Tumble (cascade) – For games with tumbling, the Tumble class removes winning symbols (those marked with explode=True) and fills empty positions from above. New symbols may come from the reel or from off‑board padding for cluster/ways games
stakeengine.github.io
.

6.4 Win Evaluation

Lines – A win occurs when a payline (predefined list of symbol positions across reels) contains matching symbols from left to right. Wilds can substitute but only pay when part of a combination and may add multiplier values in free spins
stakeengine.github.io
.

Ways – Any combination of like symbols on consecutive reels counts; the number of winning ways equals the product of matching symbol counts on each reel. Wilds may carry multipliers in freegame
stakeengine.github.io
.

Scatter – Pays anywhere on the board. Payouts can be defined by fixed values or range‑based pay groups generated using convert_range_table()
stakeengine.github.io
.

Cluster – Adjacent (up/down/left/right) clusters of like symbols are detected using breadth‑first search. Payouts depend on cluster size and may use pay groups; tumbling cascades continue after wins
stakeengine.github.io
.

Win manager – The WinManager tracks basegame and freegame wins for each simulation and cumulatively. It maintains total_cumulative_wins, cumulative_base_wins, cumulative_free_wins, running_bet_win, spin_win, and tumble_win, updating values through functions like update_spin_win()
stakeengine.github.io
.

6.5 Events & Force Files

Events – Each action in a spin (symbol reveal, line win, tumble, free spin, total win) is recorded as an event with an index, type, payload and optional meta fields
stakeengine.github.io
. The events.py module provides functions like reveal_event, fs_trigger_event, set_win_event, update_tumble_win_event and final_win_event to emit these events
stakeengine.github.io
.

Force files – When custom events are recorded via gamestate.record(), their keys and associated book IDs are stored in force_mode.json. These files count how many times specific scenarios occur. After simulations finish, a summary force.json contains all unique keys and counts
stakeengine.github.io
. The optimisation algorithm uses these force files to isolate simulation IDs corresponding to maximum wins or freegame triggers
stakeengine.github.io
.

6.6 Executables & State Classes

Executables – A central class grouping common game actions: drawing boards (draw_board()), forcing boards (force_board_from_reelstrips()), emitting win and tumble events, evaluating win cap and free spin triggers, running free spins, updating global multipliers and evaluating final wins
stakeengine.github.io
. Game developers override or extend these methods to implement unique features. The class uses functions from modules like lines, ways, scatter, and cluster for win evaluation
stakeengine.github.io
.

GeneralGameState – An abstract base class defining core functions such as creating symbol maps, assigning special symbol functions, resetting seeds, retrieving bet modes, combining books, recording events and running simulations. It requires overriding assign_special_sym_function, run_spin and run_freespin
stakeengine.github.io
stakeengine.github.io
.

7. Source Modules

The src/ directory splits functionality into submodules
stakeengine.github.io
:

Calculations – Contains modules for board drawing, tumble logic, line/ways/scatter/cluster win calculation. Examples: board.py, tumble.py, lines.py, ways.py, scatter.py, cluster.py
stakeengine.github.io
stakeengine.github.io
stakeengine.github.io
.

Config – Contains classes for game configuration, bet modes, distribution conditions, output file naming and simulation acceptance【103493707730613†L94-L183】
stakeengine.github.io
.

Events – The events.py module defines functions to create JSON‑ready event objects and update game state
stakeengine.github.io
.

Executables – Contains base and game‑specific classes implementing actions like drawing boards, tumbling, win evaluation and free spin management
stakeengine.github.io
.

State – Houses general_state.py and derived classes that manage simulation runs and book creation
stakeengine.github.io
.

Win Manager – Implements WinManager, tracking spin‑level and cumulative wins
stakeengine.github.io
.

8. Output Files

The OutputFiles class builds directories and filenames for generated data
stakeengine.github.io
. Four categories of outputs are produced
stakeengine.github.io
:

Books – Uncompressed JSONL files used for front‑end testing and debugging. Compressed books (e.g., .jsonl.zst) are uploaded to AWS and used by RGS; only compressed books are returned by the /play API
stakeengine.github.io
.

Force files – Per‑mode force_<mode>.json accumulate record() calls, mapping search keys to book IDs. After all simulations, a force.json summarises all unique keys and counts
stakeengine.github.io
.

Lookup tables – CSV files summarising simulation ID, probability and payout. Additional IdToCriteria.csv and lookUpTableSegmented.csv files identify the criteria (e.g., basegame or freegame) of each simulation and segment wins by gametype
stakeengine.github.io
.

Config files – config_math.json (optimisation parameters and bet mode details), config_fe.json (frontend symbol and reel info), config.json (bet mode info and file hash for publication)
stakeengine.github.io
.

9. Utilities

The utils package offers helper functions for analysing results and managing files
stakeengine.github.io
:

Game analytics – run_analysis.py can analyse optimised lookup tables to produce hit‑rate, RTP contributions and simulation count spreadsheets. It expects a force_record_<mode>.json file containing recorded events with keys symbol and kind. A .xlsx file summarises hit‑rates by symbol, kind and gametype (base/free)
stakeengine.github.io
.

Analysis – Additional functions assist in analysing win distributions after optimisation
stakeengine.github.io
.

Swap lookups – Tools for replacing weights in lookup tables stored in <game>/library/lookup_tables/lookUpTable_<mode>_0.csv
stakeengine.github.io
.

Get file hash – Functions to print SHA‑256 hashes of files so you can verify that local files match the config.json values
stakeengine.github.io
.

10. Example Games

Four sample games demonstrate different win types and mechanics
stakeengine.github.io
:

Lines Game – Classic 5×3 slot with 9 paying symbols, wilds and scatters. Basegame: 3 scatters trigger free spins
stakeengine.github.io
. Free spins use a separate reel set; wilds have larger multipliers and may appear on all reels; 2 scatters retrigger spins
stakeengine.github.io
.

Ways Game – 5×3 game with 9 paying symbols, one wild and one scatter. Wilds do not appear on reel 1. Basegame: need 3 scatters; free spins apply multiplicative wild multipliers (1×–5×)
stakeengine.github.io
.

Cluster‑based Game – Tumbling grid‑based game where clusters of ≥5 like symbols pay. Basegame: 4 scatters needed to enter free spins
stakeengine.github.io
. Free spins assign multipliers to grid positions: each win activates the position and doubles its multiplier up to 512×; a global multiplier increases by +1 per free spin
stakeengine.github.io
. Retrigger occurs on 3 scatters
stakeengine.github.io
.

Scatter‑Pays Game – 6×5 tumbling game; payouts depend on cluster size with pay groups (8–8, 9–10, etc.)
stakeengine.github.io
. Basegame: 3 scatters trigger free spins awarding 2 spins per scatter
stakeengine.github.io
. Free spins increment a global multiplier on every tumble; after the cascade, cumulative tumble wins are multiplied by board multipliers and global multiplier
stakeengine.github.io
. No upper limit on free spins; they equal 2 × number of scatters
stakeengine.github.io
.

Expanding Wilds Lines + Superspin – 5×5 lines game with 15 paylines and 9 paying symbols. Basegame: standard lines rules; wilds pay on 3/4/5 kind
stakeengine.github.io
. Freegame: one wild per reel expands to fill the reel and stays sticky; each reveal assigns a random multiplier 2×–50×; no retriggers
stakeengine.github.io
. Superspin mode costs 25×; player buys a spin with 3 lives; prize symbols reset lives, are sticky and evaluated when no spins remain; there is no free spin entry
stakeengine.github.io
.

These examples can be found under games/ and include a readme.txt summarising rules
stakeengine.github.io
.

11. Uploads & Publication

The Uploads section describes a temporary method for uploading math‑engine outputs to S3. Use the upload_to_aws() function (provided in uploads/) with your AWS credentials (stored in a .env file). It compares local files with those referenced in config.json and verifies RTP before uploading via the boto3 client
stakeengine.github.io
. Eventually, games will be uploaded directly through the Admin Control Panel (ACP)
stakeengine.github.io
.

12. Optimisation Algorithm

The SDK includes a Rust‑based optimisation tool that iteratively modifies lookup table weights to achieve desired RTP targets and hit‑rate distributions
stakeengine.github.io
.

12.1 Setup Parameters

OptParams – For each bet mode, define conditions, scaling and parameters keys in a dictionary. Use the OptimizationSetup class in run.py to build these entries
stakeengine.github.io
. The resulting configuration is stored in config_math.json and setup.txt
stakeengine.github.io
.

Conditions – Constructed via ConstructConditions; specify which simulation IDs to optimise. For each win type (e.g., freegame, max win, 0‑win) you must supply two of the three variables: RTP, average win, hit‑rate
stakeengine.github.io
. The order of condition keys matters: simulation IDs matching earlier keys are removed from the pool for later keys, so put high‑priority conditions (e.g., max win) first
stakeengine.github.io
.

Scaling – Biases particular payout ranges by applying a scale factor to Gaussian weights. Use sparingly; large biases can reduce acceptance rates
stakeengine.github.io
.

Parameters – Defines the number of trial distributions, volatility controls (mean‑to‑median ratio), and the number of simulated spins used to evaluate distributions
stakeengine.github.io
.

12.2 Running the Optimisation

Build the Rust binary using cargo build --release (only required on first run or when code changes)
stakeengine.github.io
.

In run.py, instantiate OptimizationSetup with the game config and set opt_params. Use OptimizationExecution().run_all_modes(config, optimization_modes_to_run, rust_threads) to run the algorithm
stakeengine.github.io
.

The tool updates lookup table weights and generates new optimisation files in game/library/optimization_files/. Use utilities to swap these weights into the main lookup table
stakeengine.github.io
.

13. RGS Technical Details

Developers must understand how the RGS endpoints consume the static files generated by the Math‑SDK. The RGS documentation explains request/response structures and behaviours
stakeengine.github.io
.

13.1 URL Structure & Query Parameters

Games are hosted at https://{TeamName}.cdn.stake-engine.com/{GameID}/{GameVersion}/index.html?sessionID={SessionID}&lang={Lang}&device={Device}&rgs_url={RgsUrl} 
stakeengine.github.io
. Parameters:

sessionID – Unique ID for the player; required on all requests
stakeengine.github.io
.

lang – ISO 639‑1 language code (supported languages: ar, de, en, es, fi, fr, hi, id, ja, ko, pl, pt, ru, tr, vi, zh)
stakeengine.github.io
.

device – ‘mobile’ or ‘desktop’
stakeengine.github.io
.

rgs_url – The dynamic base URL for authentication, betting and ending rounds
stakeengine.github.io
.

13.2 Monetary Values

RGS uses integers with six decimal places of precision
stakeengine.github.io
. For example, an amount of 1000000 represents $1.00. Supported currencies include USD, CAD, EUR, JPY and many more
stakeengine.github.io
, plus social‑casino currencies XGC and XSC
stakeengine.github.io
.

13.3 Bet Levels and Modes

Although bet levels are optional, bets must lie between minBet and maxBet and be divisible by stepBet. Use the predefined betLevels array returned by /wallet/authenticate to guide players
stakeengine.github.io
. Bet modes (cost multipliers) correspond to the game’s bet modes defined in the math config; the player debit equals baseBet × mode.costMultiplier
stakeengine.github.io
.

13.4 Wallet Endpoints

The RGS interacts with the operator’s wallet API. Endpoints include
stakeengine.github.io
:

Authenticate POST /wallet/authenticate – Validate a session ID and receive balance, bet configuration and current or previous round information
stakeengine.github.io
.

Balance POST /wallet/balance – Retrieve current player balance
stakeengine.github.io
.

Play POST /wallet/play – (in examples, POST /bet/play) Debits the bet amount and returns the new round with events and updated balance
stakeengine.github.io
.

End Round POST /wallet/end-round – Finalises the bet and triggers payout
stakeengine.github.io
.

Event POST /bet/event – Used to persist intermediate events during a round; helps resume gameplay if the player reconnects
stakeengine.github.io
.

13.5 Response Codes

Stake Engine uses standard HTTP response codes with error codes such as ERR_VAL (invalid request), ERR_IPB (insufficient player balance), ERR_IS (invalid session), ERR_ATE (authentication failure), ERR_GLE (gambling limits exceeded) and ERR_LOC (invalid location) for 400‑series; ERR_GEN and ERR_MAINTENANCE for 500‑series
stakeengine.github.io
.

13.6 Math Publication

When publishing games, ensure the math file formats described earlier (index, lookup table, compressed JSONL) are strictly followed
stakeengine.github.io
.

14. RGS Connection Example

A tutorial guides you through building a simple game (“fifty‑fifty”) that connects to the RGS
stakeengine.github.io
:

Game overview – The player calls /play and has a 50/50 chance to either double their bet or lose it
stakeengine.github.io
. After each round the JSON response is displayed; if a win occurs, the /end-round API must be manually called to finalise the bet
stakeengine.github.io
.

Generating math files – Execute run.py within games/fifty_fifty/ to produce compressed simulation results, lookup tables and the index.json needed for publication
stakeengine.github.io
. Files are placed in library/publish_files/
stakeengine.github.io
.

Frontend implementation – A simple Svelte 5 app built with Vite demonstrates authentication, playing and ending rounds. Steps include creating the project, editing vite.config.ts, replacing style files with provided snippets, building the project and deploying the dist/ folder
stakeengine.github.io
. The app authenticates a session, calls the play API and (if applicable) calls end-round to finalise wins
stakeengine.github.io
.

15. Additional Notes & Best Practices

Separation of basegame and freegame – For cluster and scatter‑pays games where board state persists, ensure freegame triggers are handled carefully. The docs note that scatter symbols tumbling onto the board may erroneously appear in basegame criteria; perform additional checks in the freespin entry function
stakeengine.github.io
.

Symbol multipliers – In lines and ways games, multiplier values on wilds add (lines) or multiply (ways) the base win only when the multiplier is > 1
stakeengine.github.io
stakeengine.github.io
. For scatter and cluster games, multipliers may be applied to the tumble win or final payout; board positions can accumulate and double multipliers in cluster free games
stakeengine.github.io
.

Buy bonus modes – A BetMode may represent a feature buy (e.g., 25× superspin). Set is_buybonus flag to true and ensure cost multipliers reflect the purchase price. Force distributions might skip basegame draws for buy bonuses (i.e., only simulate free spins or hold‑em style events)
stakeengine.github.io
.

Anticipation – Use the anticipation feature to delay reel reveals when multiple scatters are present. This is configured in GameConfig and implemented in board drawing; helps build suspense
stakeengine.github.io
.

Event logging – Always send events in chronological order and include index numbers. Use deep copies when constructing events to avoid mutating the original state
stakeengine.github.io
.

Quotas and simulation distribution – Carefully plan distribution quotas in BetMode definitions to ensure enough samples for rare outcomes (freegame, max wins). Without quotas, random draws may not capture important events
stakeengine.github.io
.

Optimisation caution – Scaling biases can drastically change hit rates. Start with conservative scale factors and monitor acceptance rates; ensure conditions keys are ordered so that overlapping criteria (e.g., max win and freegame) are handled correctly
stakeengine.github.io
stakeengine.github.io
.

16. Conclusion

The Math‑SDK offers a comprehensive, modular framework for slot‑game development. By following the structured approach of defining configuration, implementing custom logic in run_spin/run_freespin, simulating outcomes, generating static files and (optionally) optimising win distributions, developers can efficiently build mathematically sound games that integrate seamlessly with the Stake RGS. The combination of detailed simulation outputs, robust configuration classes and supporting utilities ensures precise control over RTP and player experience, while the RGS documentation explains how to deploy and interact with games once they are uploaded.