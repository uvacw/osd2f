#!/bin/bash
set -e
cmd="$@"

hypercorn  --reload --bind 0.0.0.0:8000 osd2f.server:app

exec $cmd
