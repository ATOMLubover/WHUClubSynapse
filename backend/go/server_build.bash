#!/bin/bash

BIN_DIR="./bin"
mkdir -p "$BIN_DIR"

find cmd -maxdepth 1 -type d -not -path "cmd\$" -print0 | while IFS= read -r -d $'\0' dir; do
    main_file="$dir/main.go"
    if [ -f "$main_file" ]; then
        base_dir=$(basename "$dir")
        output_path="$BIN_DIR/$base_dir"
        echo "Building $main_file -> $output_path"
        go build -o "$output_path" "$main_file"
    fi
done