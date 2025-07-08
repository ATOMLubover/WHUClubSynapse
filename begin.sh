#!/bin/bash

# 获取当前脚本所在的目录的绝对路径
BEGIN_SH_DIR=$(cd "$(dirname "$0")" && pwd)

# 确定项目根目录的路径
# 根据最新的文件列表，begin.sh 和其他脚本都在 WHUClubSynapse/ 根目录下
PROJECT_ROOT="${BEGIN_SH_DIR}"

# 定义 first.sh, second.sh, third.sh, forth.sh 的完整路径
# 这些脚本都位于项目根目录
FIRST_SCRIPT="${PROJECT_ROOT}/first.sh"
SECOND_SCRIPT="${PROJECT_ROOT}/second.sh"
THIRD_SCRIPT="${PROJECT_ROOT}/third.sh"
FORTH_SCRIPT="${PROJECT_ROOT}/forth.sh"

# 确保所有脚本都具有执行权限
chmod +x "${FIRST_SCRIPT}" "${SECOND_SCRIPT}" "${THIRD_SCRIPT}" "${FORTH_SCRIPT}"

# 在新的 Windows Terminal 窗口中启动 WSL Ubuntu 终端，并执行 first.sh
# wt.exe -d Ubuntu-24.04 负责打开新的 Ubuntu 终端会话
# wsl.exe -e "..." 负责在新会话中执行 Bash 命令
wt.exe -d Ubuntu-24.04 wsl.exe -e "bash -c '"${FIRST_SCRIPT}"'" &

# 在新的 Windows Terminal 窗口中启动 WSL Ubuntu 终端并执行 second.sh
wt.exe -d Ubuntu-24.04 wsl.exe -e "bash -c '"${SECOND_SCRIPT}"'" &

# 在新的 Windows Terminal 窗口中启动 WSL Ubuntu 终端并执行 third.sh
wt.exe -d Ubuntu-24.04 wsl.exe -e "bash -c '"${THIRD_SCRIPT}"'" &

# 暂停 10 秒
sleep 10

# 在当前终端中执行 forth.sh
"${FORTH_SCRIPT}"
