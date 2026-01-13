from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.board import Board
from src.config.config import Config


class GameCalculations(Executables):
    """
    Sugar Rush cluster evaluation with grid position multipliers.
    Overrides evaluate_clusters() to account for multiplier spots on the grid.
    """

    # Override cluster evaluation functions to include grid position multipliers
    def evaluate_clusters_with_grid(
        self,
        config: Config,
        board: Board,
        clusters: dict,
        pos_mult_grid: list,
        global_multiplier: int = 1,
        return_data: dict = {"totalWin": 0, "wins": []},
    ) -> type:
        """
        Determine payout amount from cluster, including position multipliers and global multiplier.
        Sugar Rush: Multiple multipliers in same cluster add together.
        Optimized: Use set for exploding_symbols for faster lookups, early skip for non-paying clusters.
        """
        # Optimized: Use set for O(1) lookup instead of list O(n)
        exploding_symbols = set()
        total_win = 0
        
        # Early exit if no clusters
        if not clusters:
            return board, return_data
        
        for sym in clusters:
            for cluster in clusters[sym]:
                syms_in_cluster = len(cluster)
                # Skip clusters that don't pay (size < 5)
                if syms_in_cluster < 5:
                    continue
                    
                if (syms_in_cluster, sym) in config.paytable:
                    # Sum all multipliers in the cluster (they add together)
                    # Optimized: Pre-allocate and sum in one pass
                    board_mult = sum(pos_mult_grid[positions[0]][positions[1]] for positions in cluster)
                    # If no multipliers, use 1x (no multiplication)
                    board_mult = max(board_mult, 1)
                    sym_win = config.paytable[(syms_in_cluster, sym)]
                    symwin_mult = sym_win * board_mult * global_multiplier
                    total_win += symwin_mult
                    
                    # Optimized: Create json_positions once
                    json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]

                    central_pos = Cluster.get_central_cluster_position(json_positions)
                    return_data["wins"].append({
                        "symbol": sym,
                        "clusterSize": syms_in_cluster,
                        "win": symwin_mult,
                        "positions": json_positions,
                        "meta": {
                            "globalMult": global_multiplier,
                            "clusterMult": board_mult,
                            "winWithoutMult": sym_win,
                            "overlay": {"reel": central_pos[0], "row": central_pos[1]},
                        },
                    })

                    # Mark symbols for explosion
                    for positions in cluster:
                        board[positions[0]][positions[1]].explode = True
                        pos_key = (positions[0], positions[1])
                        exploding_symbols.add(pos_key)

        return_data["totalWin"] += total_win

        return board, return_data
