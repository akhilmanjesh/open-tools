import os
import sys
import subprocess
import argparse
from pathlib import Path

def get_video_duration(input_file):
    """Get video duration in seconds using ffprobe"""
    cmd = [
        'ffprobe', 
        '-v', 'error', 
        '-show_entries', 'format=duration', 
        '-of', 'default=noprint_wrappers=1:nokey=1', 
        input_file
    ]
    
    try:
        output = subprocess.check_output(cmd).decode('utf-8').strip()
        return float(output)
    except (subprocess.CalledProcessError, ValueError):
        print("Error: Could not determine video duration.")
        return None

def compress_video(input_file, target_size_mb=100, output_dir=None):
    """Compress video to target size by adjusting bitrate"""
    input_path = Path(input_file).resolve()
    
    if not input_path.exists():
        print(f"Error: Input file '{input_file}' not found.")
        return None
    
    if output_dir is None:
        output_dir = Path(__file__).parent.resolve()
    
    output_filename = f"{input_path.stem}_compressed{input_path.suffix}"
    output_path = Path(output_dir) / output_filename
    
    duration = get_video_duration(input_path)
    if duration is None:
        return None
    
    target_size_bytes = target_size_mb * 1024 * 1024
    video_size_bytes = target_size_bytes * 0.875
    video_bitrate = int((video_size_bytes * 8) / duration)
    audio_bitrate = "128k"  
    
    cmd = [
        'ffmpeg',
        '-i', str(input_path),
        '-map_metadata', '-1',  
        '-c:v', 'libx264',      
        '-preset', 'slow',      
        '-b:v', f'{video_bitrate}',
        '-maxrate', f'{int(video_bitrate * 1.5)}',
        '-bufsize', f'{int(video_bitrate * 3)}',
        '-c:a', 'aac',          
        '-b:a', audio_bitrate,
        '-movflags', '+faststart',  
        '-y',                   
        str(output_path)
    ]
    
    print(f"Compressing video to target size of {target_size_mb}MB...")
    print(f"Calculated video bitrate: {video_bitrate/1024:.2f}kbps")
    
    try:
        subprocess.run(cmd, check=True)
        output_size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"Compression complete: {output_path}")
        print(f"Output file size: {output_size_mb:.2f}MB")
        
        if output_size_mb > target_size_mb * 1.05:  
            print(f"Warning: Output file is larger than target size. You may need to adjust parameters.")
        
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error during video compression: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Compress video and strip metadata')
    parser.add_argument('input_file', help='Path to the input video file')
    parser.add_argument('--target-size', type=int, default=100, 
                        help='Target size in MB (default: 100)')
    args = parser.parse_args()
    
    result = compress_video(args.input_file, args.target_size)
    if result:
        print(f"Successfully compressed video to: {result}")
    else:
        print("Video compression failed.")

if __name__ == "__main__":
    main()