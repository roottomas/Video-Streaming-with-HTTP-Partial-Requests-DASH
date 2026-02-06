#!/usr/bin/env python3

import sys
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
        total_size = 0
        for _ in range(num_segments):
            segment_info = lines[line_idx].strip().split()
            offset = int(segment_info[0])
            size = int(segment_info[1])
            segments.append((offset, size))
            total_size += size
            line_idx += 1
        
        tracks.append({
            'filename': filename,
            'num_segments': num_segments,
            'total_size': total_size,
            'segments': segments
        })
    
    return num_tracks, tracks


def main():
    if len(sys.argv) != 4:
        print("Usage: python3 programA.py serverURL movieName resultsFileName")
        sys.exit(1)
    
    server_url = sys.argv[1]
    movie_name = sys.argv[2]
    results_file = sys.argv[3]
    
    try:
        # Download manifest
        manifest_content = download_manifest(server_url, movie_name)
        
        # Parse manifest
        num_tracks, tracks = parse_manifest(manifest_content)
        
        # Write results
        with open(results_file, 'w') as f:
            # Number of tracks
            f.write(f"{num_tracks}\n")
            
            # Number of segments (same for all tracks)
            if tracks:
                f.write(f"{tracks[0]['num_segments']}\n")
            
            # Total size of each track
            for track in tracks:
                f.write(f"{track['total_size']}\n")
        
        print(f"Results written to {results_file}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

