#!/usr/bin/env python3

import sys
import socket
import threading
import queue
import requests


def download_manifest(server_url, movie_name):
    """Download and return the manifest.txt file content."""
    manifest_url = f"{server_url}/movies/{movie_name}/manifest.txt"
    response = requests.get(manifest_url)
    response.raise_for_status()
    return response.text


def parse_manifest_for_track(manifest_content, track_number):
    """Parse manifest.txt and return segment information for a specific track."""
    lines = manifest_content.strip().split('\n')
    
    # First line: movie name (skip)
    # Second line: number of tracks
    num_tracks = int(lines[1])
    
    if track_number < 0 or track_number >= num_tracks:
        raise ValueError(f"Track number {track_number} is out of range (0-{num_tracks-1})")
    
    # Parse to the desired track
    line_idx = 2
    
    for track_num in range(num_tracks):
        # Track file name
        filename = lines[line_idx].strip()
        line_idx += 1
        
        # Codec (skip)
        line_idx += 1
        
        # Bit rate (skip)
        line_idx += 1
        
        # Duration (skip)
        line_idx += 1
        
        # Number of segments
        num_segments = int(lines[line_idx].strip())
        line_idx += 1
        
        # Read segment offsets and sizes
        segments = []
        for _ in range(num_segments):
            segment_info = lines[line_idx].strip().split()
            offset = int(segment_info[0])
            size = int(segment_info[1])
            segments.append((offset, size))
            line_idx += 1
        
        if track_num == track_number:
            return filename, segments
    
    raise ValueError(f"Track {track_number} not found")


def producer_thread(base_url, movie_name, track_number, segment_queue):
    """Producer thread: downloads segments from server and puts them in queue."""
    try:
        # Obtain manifest.txt
        manifest_content = download_manifest(base_url, movie_name)
        
        # Process manifest to get segment info
        filename, segments = parse_manifest_for_track(manifest_content, track_number)
        file_url = f"{base_url}/movies/{movie_name}/{filename}"
        
        # Download each segment and put in queue
        for segment_idx, (offset, size) in enumerate(segments):
            # Get segment using partial request
            headers = {"Range": f"bytes={offset}-{offset + size - 1}"}
            response = requests.get(file_url, headers=headers)
            response.raise_for_status()
            segment_data = response.content
            
            # Put segment in queue
            is_last = (segment_idx == len(segments) - 1)
            segment_queue.put((segment_data, is_last))
        
        # Return (thread termination)
        
    except Exception as e:
        print(f"Producer error: {e}", file=sys.stderr)

def consumer_thread(player_socket, segment_queue):
    """Consumer thread: gets segments from queue and sends to player."""
    try:
        while True:
            # Get next segment from queue
            segment_data, is_last = segment_queue.get()
            
            if segment_data is None:
                break
            
            # Send segment to player through socket
            try:
                player_socket.sendall(segment_data)
            except BrokenPipeError:
                # Player closed connection, this is normal when playback ends
                print("Player closed connection (playback may have ended)")
                break
            except OSError as e:
                # Connection error
                print(f"Connection error: {e}")
                break
            
            # Mark task as done
            segment_queue.task_done()
            
            # If last segment, break
            if is_last:
                break
        
        # Return (thread termination)
        
    except Exception as e:
        print(f"Consumer error: {e}", file=sys.stderr)

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 proxy.py baseURL movieName track")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')  # Remove trailing slash for safety purposes
    movie_name = sys.argv[2]
    track_number = int(sys.argv[3])
    
    # Connect to player
    print("Proxy connecting to player on localhost:9999...")
    
    player_socket = None
    try:
        player_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        player_socket.connect(('localhost', 8000))
        print("Connected to player")
        
        # Create queue for producer-consumer communication
        segment_queue = queue.Queue()
        
        # Create and start producer thread
        producer = threading.Thread(
            target=producer_thread,
            args=(base_url, movie_name, track_number, segment_queue)
        )
        producer.start()
        
        # Create and start consumer thread
        consumer = threading.Thread(
            target=consumer_thread,
            args=(player_socket, segment_queue)
        )
        consumer.start()
        
        # Wait for threads to complete
        producer.join()
        consumer.join()
        
        print("Streaming complete")
        
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        # Cleanup
        if player_socket is not None:
            try:
                player_socket.close()
            except:
                pass


if __name__ == "__main__":
    main()
