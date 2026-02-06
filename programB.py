#!/usr/bin/env python3

import sys
import time
import requests


def download_manifest(server_url, movie_name):
    """Download and return the manifest.txt file content."""
    manifest_url = f"{server_url}/movies/{movie_name}/manifest.txt"
    response = requests.get(manifest_url)
    response.raise_for_status()
    return response.text


def parse_manifest(manifest_content):
    """Parse manifest.txt and return track information."""
    lines = manifest_content.strip().split('\n')
    
    # First line: movie name (skip)
    # Second line: number of tracks
    num_tracks = int(lines[1])
    
    # Parse each track
    tracks = []
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
        
        tracks.append({
            'filename': filename,
            'num_segments': num_segments,
            'segments': segments
        })
    
    return num_tracks, tracks


def download_track(server_url, movie_name, track):
    """Download a track using partial requests and return download time and rate."""
    file_url = f"{server_url}/movies/{movie_name}/{track['filename']}"
    
    start_time = time.time()
    total_bytes = 0
    
    # Download each segment using partial requests and save to file
    with open(track['filename'], 'wb') as f:
        for offset, size in track['segments']:
            headers = {"Range": f"bytes={offset}-{offset + size - 1}"}
            response = requests.get(file_url, headers=headers)
            response.raise_for_status()
            segment_data = response.content
            total_bytes += len(segment_data)
            f.write(segment_data)
    
    end_time = time.time()
    download_time = end_time - start_time
    download_rate = total_bytes / download_time if download_time > 0 else 0
    
    return download_time, download_rate


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 programB.py serverURL movieName resultsFileName")
        sys.exit(1)
    
    server_url = sys.argv[1]
    movie_name = sys.argv[2]
    results_file = sys.argv[3]
    
    try:
        # Download manifest
        manifest_content = download_manifest(server_url, movie_name)
        
        # Parse manifest
        num_tracks, tracks = parse_manifest(manifest_content)
        
        # Download each track and measure performance
        results = []
        for track_num, track in enumerate(tracks):
            print(f"Downloading track {track_num}...")
            download_time, download_rate = download_track(server_url, movie_name, track)
            results.append((download_time, download_rate))
            print(f"Track {track_num}: {download_time:.2f}s, {download_rate:.2f} bytes/s")
        
        # Write results
        with open(results_file, 'w') as f:
            for download_time, download_rate in results:
                f.write(f"{download_time}\n")
                f.write(f"{download_rate}\n")
        
        print(f"Results written to {results_file}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

