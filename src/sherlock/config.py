"""Configuration management for Sherlock SRE toolkit."""
import logging
import os
from pathlib import Path
from typing import Optional

from strands.telemetry import StrandsTelemetry


class Config:
    """Centralized configuration management."""
    
    _telemetry_instance: Optional[StrandsTelemetry] = None
    
    @staticmethod
    def setup_logging(
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        include_console: bool = True
    ) -> None:
        """Setup centralized logging configuration."""
        handlers = []
        
        # Add file handler if specified
        if log_file:
            log_path = Path.home() / ".aws" / "amazonq" / log_file
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handlers.append(logging.FileHandler(log_path))
        
        # Add console handler if requested
        if include_console:
            handlers.append(logging.StreamHandler())
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            handlers=handlers,
            force=True  # Override any existing configuration
        )
        
        # Configure strands logging
        logging.getLogger("strands").setLevel(getattr(logging, log_level.upper()))
        
        if log_file:
            logger = logging.getLogger(__name__)
            logger.info(f"Logging configured - File: {log_path}, Level: {log_level}")
    
    @staticmethod
    def setup_telemetry(enable_otlp: bool = False, enable_console: bool = False) -> None:
        """Setup centralized telemetry configuration."""
        if not enable_otlp and not enable_console:
            # Telemetry disabled
            return
            
        if Config._telemetry_instance is None:
            Config._telemetry_instance = StrandsTelemetry()
            os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
        
        if enable_otlp:
            Config._telemetry_instance.setup_otlp_exporter()
        
        if enable_console:
            Config._telemetry_instance.setup_console_exporter()
    
    @staticmethod
    def setup_environment() -> None:
        """Setup common environment variables."""
        os.environ.setdefault("BYPASS_TOOL_CONSENT", "true")
        os.environ.setdefault("AWS_REGION", "us-east-1")
        os.environ["KUBECONFIG"] = os.path.expanduser("~/.kube/config")
    
    @staticmethod
    def setup_for_mcp() -> None:
        """Setup configuration for MCP server execution."""
        Config.setup_logging(
            log_level="INFO",
            log_file="sherlock-mcp.log",
            include_console=True
        )

        Config.setup_telemetry(enable_otlp=True, enable_console=True)
        Config.setup_environment()
    
    @staticmethod
    def setup_for_development() -> None:
        """Setup configuration for local development."""
        # Development-specific configuration
        Config.setup_logging(
            log_level="INFO",
            include_console=True
        )
        Config.setup_telemetry(enable_otlp=True, enable_console=False)
        Config.setup_environment()
    
