# Service Launcher

This project provides a simple way to start and stop multiple services using `tmux` sessions. It includes scripts for launching individual services and main scripts for starting and stopping all services at once.

## Project Structure

```
service-launcher
├── scripts
│   ├── chromadb_service_startup.sh
│   └── cpolar_startup.sh
|   |__ fastapi_backend_startup.sh
|   |__ vllm_service_startup.sh
├── start_all.sh
├── stop_all.sh
└── README.md
```

## Scripts

- **scripts/service1.sh**: This script is responsible for starting the first service. Ensure that it contains the necessary commands to launch the service.

- **scripts/service2.sh**: This script is responsible for starting the second service. Ensure that it contains the necessary commands to launch the service.

## Usage

### Starting All Services

To start all services in separate `tmux` sessions, run the following command:

```bash
bash start_all.sh
```

This will execute the startup scripts for all services and create a new `tmux` session for each.

### Stopping All Services

To stop all running services, use the following command:

```bash
bash stop_all.sh
```

This will kill all `tmux` sessions that were started by the `start_all.sh` script.

## Requirements

- `tmux` must be installed on your system.
- Ensure that the scripts have executable permissions. You can set this using:

```bash
chmod +x scripts/service1.sh scripts/service2.sh start_all.sh stop_all.sh
```

## Notes

- Make sure to customize the service scripts (`service1.sh` and `service2.sh`) with the appropriate commands needed to launch your services.
- This project is designed for easy management of services using `tmux`, allowing you to keep services running in the background while you continue to use your terminal.