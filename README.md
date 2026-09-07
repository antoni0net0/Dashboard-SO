# Linux Process & Resource Dashboard

A real-time system monitoring dashboard built with **Python, Dash and Plotly**. The application reads Linux `/proc` data directly to display active processes, CPU usage and memory consumption in a web interface.

## Features

- Lists active Linux processes
- Displays PID, process name, CPU time and memory usage
- Real-time CPU usage gauge
- Real-time memory usage gauge
- Sort processes by PID, CPU or memory
- Background data collection with threads
- Automatic dashboard refresh every 5 seconds
- MVC-inspired separation between model, controller and view

## How It Works

The dashboard collects operating-system information directly from Linux pseudo-filesystems:

- `/proc/<pid>/stat` for process information
- `/proc/stat` for CPU statistics
- `/proc/meminfo` for memory statistics

The data collection runs in background threads, while Dash callbacks update the web interface periodically.

## Architecture

```text
Linux /proc
    |
    v
SystemModel
    |
    v
SystemController
(background threads)
    |
    v
SystemView
(Dash + Plotly)
    |
    v
Browser Dashboard
```

## Tech Stack

- Python
- Dash
- Plotly
- Linux `/proc`
- Threading

## Running Locally

This project is designed for **Linux**, since it reads data directly from `/proc`.

Install the dependencies:

```bash
pip install dash plotly
```

Run the application:

```bash
python dashboard.py
```

Then open the local Dash address shown in the terminal, typically:

```text
http://127.0.0.1:8050
```

## Project Structure

```text
Dashboard-SO/
├── dashboard.py
├── dash2.py
├── dashboard.ipynb
└── README.md
```

## Academic Context

Developed as an operating-systems project focused on process monitoring and resource visualization.

### Team

- Antonio Galvão Martins Neto
- Laís Lisboa
