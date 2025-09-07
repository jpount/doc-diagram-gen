#!/usr/bin/env python3
"""
Centralized logging configuration for n8n services
Writes logs to ../logs/n8n/ directory
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
import sys

# Log directory - outside n8n folder in main logs directory
LOG_DIR = Path(__file__).parent.parent.parent / "logs" / "n8n"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(
    name: str,
    log_file: str = None,
    level: int = logging.INFO,
    console: bool = True,
    file_logging: bool = True
) -> logging.Logger:
    """
    Set up a logger with both file and console handlers
    
    Args:
        name: Logger name (usually __name__)
        log_file: Specific log file name (defaults to service name)
        level: Logging level
        console: Whether to log to console
        file_logging: Whether to log to file
    
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    
    # File handler with rotation
    if file_logging:
        if not log_file:
            # Extract service name from logger name
            service_name = name.split('.')[-1] if '.' in name else name
            log_file = f"{service_name}.log"
        
        file_path = LOG_DIR / log_file
        
        # Rotating file handler - 10MB max, keep 5 backups
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
    
    return logger


def get_session_logger(session_id: str, service: str = "session") -> logging.Logger:
    """
    Get a logger for a specific session
    
    Args:
        session_id: Session ID
        service: Service name
    
    Returns:
        Logger for the session
    """
    log_file = f"{service}_{session_id}_{datetime.now().strftime('%Y%m%d')}.log"
    return setup_logger(f"{service}.{session_id}", log_file=log_file)


def get_agent_logger(agent_name: str, session_id: str = None) -> logging.Logger:
    """
    Get a logger for a specific agent execution
    
    Args:
        agent_name: Agent name
        session_id: Optional session ID
    
    Returns:
        Logger for the agent
    """
    if session_id:
        log_file = f"agents/{agent_name}_{session_id}.log"
    else:
        log_file = f"agents/{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Create agents subdirectory
    (LOG_DIR / "agents").mkdir(exist_ok=True)
    
    return setup_logger(f"agent.{agent_name}", log_file=log_file)


# Create main loggers for services
api_logger = setup_logger("n8n_api", "api_server.log")
executor_logger = setup_logger("n8n_executor", "workflow_executor.log")
agent_executor_logger = setup_logger("agent_executor", "agent_executor.log")
sdk_executor_logger = setup_logger("sdk_executor", "sdk_executor.log")
host_server_logger = setup_logger("host_server", "host_server.log")


def log_execution_start(logger: logging.Logger, component: str, details: dict = None):
    """Helper to log execution start"""
    msg = f"Starting {component}"
    if details:
        msg += f" - {details}"
    logger.info(msg)


def log_execution_complete(logger: logging.Logger, component: str, duration: float = None, success: bool = True):
    """Helper to log execution completion"""
    status = "completed successfully" if success else "failed"
    msg = f"{component} {status}"
    if duration:
        msg += f" (duration: {duration:.2f}s)"
    
    if success:
        logger.info(msg)
    else:
        logger.error(msg)


def log_exception(logger: logging.Logger, component: str, exception: Exception):
    """Helper to log exceptions"""
    logger.error(f"Exception in {component}: {str(exception)}", exc_info=True)