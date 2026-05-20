#!/usr/bin/env python3
"Start Hermes Gateway in-process without .env's TELEGRAM_PROXY."
import os, sys

os.environ.pop("TELEGRAM_PROXY", None)
os.environ["HERMES_TELEGRAM_DISABLE_FALLBACK_IPS"] = "true"
os.environ["http_proxy"] = "http://127.0.0.1:6478"
os.environ["https_proxy"] = "http://127.0.0.1:6478"

sys.path.insert(0, "/Users/mac/.hermes/hermes-agent")

from hermes_cli.gateway import run_gateway
run_gateway(verbose=False, quiet=False, replace=True)
