import sys
import json
import os
from BB.bbConfig import bbPRIVATE

# Define required configuration variables
REQUIRED_CONFIG_VARS = [
    "botToken", "userDBPath", "guildDBPath", "bountyDBPath", 
    "reactionMenusDBPath", "loggingFolderPath", "developers", 
    "shipsDir", "skinsDir"
]

def load_config_from_file(filepath):
    """Load configuration from JSON file."""
    try:
        with open(filepath, "r") as cfgFile:
            return json.load(cfgFile)
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        return {}

def get_config_value(key, file_config):
    """Get configuration value from environment variable or file (env takes priority)."""
    # First check environment variables (convert to uppercase)
    env_key = key.upper()
    env_value = os.getenv(env_key)
    if env_value is not None:
        return env_value
    
    # Then check config file
    if key in file_config:
        return file_config[key]
    
    return None

def validate_required_config(file_config):
    """Check that all required configuration variables are available."""
    missing_vars = []
    
    for var in REQUIRED_CONFIG_VARS:
        if get_config_value(var, file_config) is None:
            if os.getenv(var.upper()) is None:
                missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required configuration variables: {missing_vars}. "
            f"Please provide them either as environment variables "
            f"(uppercase: {[var.upper() for var in missing_vars]}) or in the config file"
        )


debugPrint = False
if os.getenv("DEBUG_MODE") is not None:
    if os.getenv("DEBUG_MODE").upper() == "TRUE":
        debugPrint = True

# Main configuration loading logic - handle optional config file
config_file_path = None
if len(sys.argv) >= 2:
    config_file_path = sys.argv[1]

cfg = load_config_from_file(config_file_path)

# Validate that all required variables are available
validate_required_config(cfg)

# Set configuration values with priority to environment variables
if get_config_value("botToken", cfg):
    bbPRIVATE.botToken = get_config_value("botToken", cfg)
    if debugPrint:
        print("botToken", bbPRIVATE.botToken, sep=": ")

if get_config_value("userDBPath", cfg):
    bbPRIVATE.userDBPath = get_config_value("userDBPath", cfg)
    if debugPrint:
        print("userDBPath", bbPRIVATE.userDBPath, sep=": ")

if get_config_value("guildDBPath", cfg):
    bbPRIVATE.guildDBPath = get_config_value("guildDBPath", cfg)
    if debugPrint:
        print("guildDBPath", bbPRIVATE.guildDBPath, sep=": ")

if get_config_value("bountyDBPath", cfg):
    bbPRIVATE.bountyDBPath = get_config_value("bountyDBPath", cfg)
    if debugPrint:
        print("bountyDBPath", bbPRIVATE.bountyDBPath, sep=": ")

if get_config_value("reactionMenusDBPath", cfg):
    bbPRIVATE.reactionMenusDBPath = get_config_value("reactionMenusDBPath", cfg)
    if debugPrint:
        print("reactionMenusDBPath", bbPRIVATE.reactionMenusDBPath, sep=": ")

if get_config_value("loggingFolderPath", cfg):
    bbPRIVATE.loggingFolderPath = get_config_value("loggingFolderPath", cfg)
    if debugPrint:
        print("loggingFolderPath", bbPRIVATE.loggingFolderPath, sep=": ")

if get_config_value("developers", cfg):
    developers_value = get_config_value("developers", cfg)
    bbPRIVATE.developers = [int(i.strip()) for i in developers_value.split(",")]
    if debugPrint:
        print("developers", bbPRIVATE.developers, sep=": ")

if get_config_value("shipsDir", cfg):
    bbPRIVATE.shipsDir = get_config_value("shipsDir", cfg)
    if debugPrint:
        print("shipsDir", bbPRIVATE.shipsDir, sep=": ")

if get_config_value("skinsDir", cfg):
    bbPRIVATE.skinsDir = get_config_value("skinsDir", cfg)
    if debugPrint:
        print("skinsDir", bbPRIVATE.skinsDir, sep=": ")

import BB.bountybot
