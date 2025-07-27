# Standard Library
import json
import logging
import os
import pprint
from typing import Any, Optional, Union
# Third Party
from pydantic import BaseModel
from rich.logging import RichHandler


class LoggerFactory:
    @staticmethod
    def create_logger(
        name: str = "app", 
        log_level: Optional[Union[str, int]] = None,
        enabled: bool = True,
        env: Optional[str] = None,
        log_to_file: bool = False,
        log_to_api: bool = False,
        log_file_path: str = "logs/app.log"
    ):
        """
        Create a logger with explicit configuration parameters.
        
        Args:
            name: Logger name
            log_level: Logging level (defaults to INFO)
            enabled: Whether the logger is enabled
            env: Environment (development/production) - defaults to checking ENV var
            log_to_file: Whether to log to file
            log_to_api: Whether to log to API
            log_file_path: Path for log file
        """
        # Set defaults
        if log_level is None:
            log_level = "INFO"
        
        if env is None:
            env = os.environ.get("AI_ENV", "production")
        
        # Convert log level to uppercase string if it's a string, or use logging constant
        if isinstance(log_level, str):
            log_level = log_level.upper()

        # print(f"Creating logger for {name} with log level {log_level} and environment {env}")

        logger = logging.getLogger(name)
        logger.setLevel(log_level)
        logger.disabled = not enabled

        if logger.handlers:
            return logger  # Prevent duplicate handlers

        # Formatters
        console_format = "(%(name)s) %(message)s"
        # print(f"Console format: {console_format}")
        file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(file_format)

        # Console Handler
        if env == "development":
            console_handler = RichHandler(
                rich_tracebacks=True,
                show_time=True,
                omit_repeated_times=False,
                show_level=True,
                show_path=True,
                markup=True
            )
            # Set custom time format for RichHandler to show only time
            console_handler._log_render.show_time = True
            console_handler._log_render.time_format = "[%X]"  # %X shows time in HH:MM:SS format
        else:
            console_handler = logging.StreamHandler()

        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(console_format))
        logger.addHandler(console_handler)

        # Optional File Logging
        if log_to_file:
            # Create logs directory if it doesn't exist
            log_dir = os.path.dirname(log_file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
                
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Optional API Logging
        if log_to_api:
            class APILogHandler(logging.Handler):
                def emit(self, record):
                    log_entry = self.format(record)
                    # TODO: send log_entry to your central API server
                    # e.g., requests.post("https://log.example.com", json={"log": log_entry})
                    pass
            api_handler = APILogHandler(level=logging.WARNING)
            api_handler.setFormatter(formatter)
            logger.addHandler(api_handler)

        logger.propagate = False

        return logger

    @staticmethod
    def create_logger_from_settings(settings, name: str = "app"):
        """
        Create a logger using settings object.
        This is a convenience method for when you have settings available.
        """
        return LoggerFactory.create_logger(
            name=name,
            log_level=settings.log_level,
            enabled=True,
            env=settings.env,
            log_to_file=settings.log_to_file,
            log_to_api=settings.log_to_api
        )

    @staticmethod
    def disable_logger(logger, disabled: bool):
        logger.disabled = disabled
        if disabled:
            logger.handlers = []

def format_for_log(message: str, data: Any) -> str:
    """
    Format a message and data object nicely for logging.

    Args:
        message (str): The log message prefix.
        data (Any): The data object to pretty-print.

    Returns:
        str: Formatted string ready for logging.
    """
    try:
        if isinstance(data, BaseModel):
            data_dict = data.model_dump()
            # formatted_data = json.dumps(data_dict, indent=2, default=str)
            formatted_data = pprint.pformat(data_dict)
        elif isinstance(data, (dict, list)):
            formatted_data = json.dumps(data, indent=2, default=str)
        elif isinstance(data, bytes):
            # CRITICAL CHANGE: Add errors='replace' for robust decoding
            try:
                formatted_data = data.decode("utf-8", errors='replace')
                # Optionally, try to parse as JSON if it looks like JSON
                if formatted_data.strip().startswith(("{", "[")):
                    try:
                        parsed_json = json.loads(formatted_data)
                        formatted_data = json.dumps(parsed_json, indent=2, default=str)
                    except json.JSONDecodeError:
                        # Not valid JSON, just use the decoded string
                        pass
            except Exception as decode_e:
                formatted_data = f"<Could not decode bytes: {decode_e}>"
        else:
            # Fallback: use pprint for arbitrary objects or str()
            formatted_data = pprint.pformat(data)
    except Exception as e:
        # Fallback if something goes wrong
        formatted_data = f"<Could not format data: {e}>"

    return f"{message}:\n{formatted_data}"