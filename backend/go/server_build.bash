#!/bin/bash

BIN_DIR="../../bin"
mkdir -p "$BIN_DIR"

for dir in cmd/*/; do
    service_name=$(basename "$dir")
    output_path="$BIN_DIR/$service_name"
    
    echo "Building $service_name service -> $output_path"
    (cd "$dir" && go build -o "$output_path")
done