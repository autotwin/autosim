#/bin/bash

# Check lint with ruff
echo "Check lint with Ruff"
ruff check
echo "."

# Check format with ruff
echo "Check format with Ruff"
ruff format
echo "."
