#!/bin/sh
set -e
if [ "$DEV" = "true" ]; then
  echo "Running in development mode"
  exec /scripts/entrypoint.dev.sh
else
  echo "Running in production mode"
  exec /scripts/entrypoint.prod.sh
fi
