"""Submodule containing the CLI command handlers."""

import logging
import sys
from iceflix.client import Client



LOG_FORMAT = '%(asctime)s' +' ** %(levelname)s **' + '%(message)s'

def setup_logging():
    """Configure the logging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def client():
    """Handles the IceFlix client CLI command."""
    setup_logging()
    logging.info(" Starting IceFlix client...")
    sys.exit(Client().main(sys.argv))
