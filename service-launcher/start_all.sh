#!/bin/bash

# The name for the tmux session
SESSION_NAME="services"

# Get the directory of the script to resolve paths correctly
# SCRIPT_DIR will be /root/WHUCS-Qwen3/service-launcher
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Check if the session already exists.
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "Session '$SESSION_NAME' already exists. Attaching to it."
    tmux attach-session -t $SESSION_NAME
    exit 0
fi

echo "Creating new tmux session '$SESSION_NAME'..."

# --- Commands to run in each window ---
# Use 'conda run' for reliability in non-interactive shells.
# Corrected the script paths to point to 'service-launcher/scripts/'.
# IMPORTANT: Replace 'base' if you use a different conda environment name.
CMD_CHROMA="conda run -n base --no-capture-output bash ${SCRIPT_DIR}/scripts/chromadb_service_startup.sh; exec bash"
CMD_VLLM="conda run -n base --no-capture-output bash ${SCRIPT_DIR}/scripts/vllm_service_startup.sh; exec bash"
CMD_FASTAPI="conda run -n base --no-capture-output bash ${SCRIPT_DIR}/scripts/fastapi_backend_startup.sh; exec bash"
CMD_CPOLAR="conda run -n base --no-capture-output bash ${SCRIPT_DIR}/scripts/cpolar_startup.sh; exec bash"

# Create a new detached session and the first window
tmux new-session -d -s $SESSION_NAME -n 'chromadb' "$CMD_CHROMA"

# Create the other windows
tmux new-window -t $SESSION_NAME -n 'vllm' "$CMD_VLLM"
tmux new-window -t $SESSION_NAME -n 'fastapi' "$CMD_FASTAPI"
tmux new-window -t $SESSION_NAME -n 'cpolar' "$CMD_CPOLAR"

# Send the command to the last window and exit
tmux send-keys -t $SESSION_NAME:cpolar "$CMD_CPOLAR" C-m
tmux send-keys -t $SESSION_NAME:cpolar "exit" C-m

echo "All services started in tmux session '$SESSION_NAME'."
echo "To attach to the session, run: tmux attach-session -t $SESSION_NAME"

# Attach to the newly created session
tmux attach-session -t $SESSION_NAME