package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// Config holds simulation configuration
type Config struct {
	GameID    string
	Mode      string
	GamePath  string
	OutputPath string
	ReelsPath string
}

// Load reads configuration from file or uses defaults
func Load(gameID, mode, configPath string) (*Config, error) {
	cfg := &Config{
		GameID: gameID,
		Mode:   mode,
	}

	// If config file provided, load it
	if configPath != "" {
		data, err := os.ReadFile(configPath)
		if err != nil {
			return nil, fmt.Errorf("failed to read config file: %w", err)
		}

		var fileConfig map[string]interface{}
		if err := json.Unmarshal(data, &fileConfig); err != nil {
			return nil, fmt.Errorf("failed to parse config: %w", err)
		}

		// Extract values from config file
		if path, ok := fileConfig["path_to_games"].(string); ok {
			cfg.GamePath = path
		}
	}

	// Default paths (adjust based on your project structure)
	if cfg.GamePath == "" {
		cfg.GamePath = "games"
	}

	gameDir := filepath.Join(cfg.GamePath, gameID)
	cfg.OutputPath = filepath.Join(gameDir, "library", "books")
	cfg.ReelsPath = filepath.Join(gameDir, "reels")

	// Ensure output directory exists
	if err := os.MkdirAll(cfg.OutputPath, 0755); err != nil {
		return nil, fmt.Errorf("failed to create output directory: %w", err)
	}

	return cfg, nil
}




