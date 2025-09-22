"""Configuration management for Sherlock SRE toolkit."""
import logging
import os
import base64
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
    def _setup_langfuse() -> None:
        """Setup Langfuse OTLP configuration."""
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        langfuse_host = os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
        
        if not public_key or not secret_key:
            logger = logging.getLogger(__name__)
            logger.warning("Langfuse keys not found in environment variables. Skipping Langfuse setup.")
            return
        
        # Build Basic Auth header (following Langfuse docs exactly)
        langfuse_auth = base64.b64encode(f"{public_key}:{secret_key}".encode()).decode()
        
        # Configure OpenTelemetry endpoint & headers (following Langfuse docs)
        os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{langfuse_host}/api/public/otel"
        os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {langfuse_auth}"
        
        logger = logging.getLogger(__name__)
        logger.info(f"Langfuse OTLP configured - Endpoint: {langfuse_host}/api/public/otel")

    @staticmethod
    def setup_telemetry(enable_otlp: bool = False, enable_console: bool = False, enable_langfuse: bool = False) -> None:
        """Setup centralized telemetry configuration."""
        if not enable_otlp and not enable_console and not enable_langfuse:
            # Telemetry disabled
            return
        
        # Setup Langfuse if enabled (this will override OTLP endpoint for Langfuse)
        if enable_langfuse:
            Config._setup_langfuse()
            
        if Config._telemetry_instance is None:
            Config._telemetry_instance = StrandsTelemetry()
            # Only set Jaeger endpoint if Langfuse is not enabled
            if not enable_langfuse:
                os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
        
        if enable_otlp or enable_langfuse:
            # Use setup_otlp_exporter() as shown in Langfuse docs
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

        # Enable both Jaeger and Langfuse if available
        enable_langfuse = bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
        Config.setup_telemetry(enable_otlp=True, enable_console=True, enable_langfuse=enable_langfuse)
        Config.setup_environment()
    
    @staticmethod
    def setup_for_development() -> None:
        """Setup configuration for local development."""
        # Development-specific configuration
        Config.setup_logging(
            log_level="INFO",
            include_console=True
        )
        # Enable both Jaeger and Langfuse if available
        enable_langfuse = bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
        Config.setup_telemetry(enable_otlp=True, enable_console=False, enable_langfuse=enable_langfuse)
        Config.setup_environment()
    
