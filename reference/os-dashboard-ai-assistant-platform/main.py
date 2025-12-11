#!/usr/bin/env python3
"""
OS Dashboard AI Assistant Platform - Main Entry Point
Launch the complete autonomous workflow system
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_environment():
    """Setup the environment for the application"""
    # Create necessary directories
    directories = [
        'workspace',
        'output', 
        'logs',
        'temp',
        'backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/dashboard.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main entry point for the OS Dashboard AI Assistant Platform"""
    parser = argparse.ArgumentParser(
        description='OS Dashboard AI Assistant Platform - Advanced Autonomous Workflows'
    )
    
    parser.add_argument(
        '--mode', 
        choices=['dashboard', 'cli', 'server'],
        default='dashboard',
        help='Launch mode: dashboard (GUI), cli (command line), or server (web server)'
    )
    
    parser.add_argument(
        '--config',
        default='config/default_config.yaml',
        help='Configuration file path'
    )
    
    parser.add_argument(
        '--workspace',
        default='./workspace',
        help='Workspace directory path'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for server mode'
    )
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    logger = logging.getLogger(__name__)
    logger.info("Starting OS Dashboard AI Assistant Platform...")
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Config: {args.config}")
    logger.info(f"Workspace: {args.workspace}")
    
    try:
        if args.mode == 'dashboard':
            # Launch GUI dashboard
            from src.dashboard.main_interface import main as dashboard_main
            logger.info("Launching GUI Dashboard...")
            dashboard_main()
            
        elif args.mode == 'cli':
            # Launch CLI interface
            logger.info("Launching CLI Interface...")
            from src.cli.command_interface import main as cli_main
            cli_main(args)
            
        elif args.mode == 'server':
            # Launch web server
            logger.info(f"Launching Web Server on port {args.port}...")
            from src.server.web_interface import main as server_main
            server_main(args.port, args.config)
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    
    logger.info("OS Dashboard AI Assistant Platform shutdown complete")

if __name__ == "__main__":
    main()