# Video Streaming with HTTP Partial Requests (DASH)

## Overview
This project implements a simplified video streaming system based on **Dynamic Adaptive Streaming over HTTP (DASH)**. The goal is to adapt video quality to network conditions using **HTTP range requests** and segmented media delivery.

The system is composed of multiple Python programs that interact with a standard HTTP server and a media player.

## Key Features
- Parsing of DASH-like `manifest.txt` files
- Video segmentation using HTTP **Range Requests**
- Measurement of download time and throughput per track
- Proxy-based streaming to a media player (e.g., MPlayer or VLC)
- Producer–Consumer architecture using multithreading
- Support for multiple quality tracks

## Components
- **Program A**: Extracts metadata (tracks, segments, sizes)
- **Program B**: Downloads all tracks and measures performance
- **Proxy**: Streams video segments in real time to a media player

## Technologies
- Python
- HTTP / Partial Requests
- Multithreading
- Sockets
- Producer–Consumer pattern

## Skills Demonstrated
- Network programming
- HTTP protocol internals
- Concurrent programming
- Media streaming concepts
- Performance measurement

## Academic Context
Computer Networks (TPC4)
