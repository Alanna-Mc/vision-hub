#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Run database migrations
flask db upgrade

# Execute the command passed as arguments
exec "$@"

