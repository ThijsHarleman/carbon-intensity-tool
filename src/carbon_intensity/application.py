"""Application entry point for the Carbon Intensity tool."""

import logging

def configure_logging() -> None:
    """Configure basic console logging for development."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

def main() -> None:
    """Start the application."""
    configure_logging()

    logger = logging.getLogger(__name__)
    logger.info("Carbon Intensity tool started.")

if __name__ == "__main__":
    main()
