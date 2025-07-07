#!/bin/bash

# Stop all services started by start_all.sh

# List of tmux session names
sessions=("service1" "service2")

# Loop through each session and kill it
for session in "${sessions[@]}"; do
    if tmux has-session -t "$session" 2>/dev/null; then
        tmux kill-session -t "$session"
        echo "Stopped service in session: $session"
    else
        echo "No running session found for: $session"
    fi
done

echo "All services have been stopped."