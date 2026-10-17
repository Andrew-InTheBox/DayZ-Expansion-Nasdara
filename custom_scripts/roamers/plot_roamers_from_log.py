import re
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import glob
from datetime import datetime

# Shared Nasdara image bounds (world size supplied by the server owner).
from pathlib import Path
import json
_map_settings_path = Path(__file__).resolve().parents[1] / "assets" / "nasdara-map-settings.json"
_map_settings = json.loads(_map_settings_path.read_text(encoding="utf-8"))
NASDARA_BOUNDS = tuple(_map_settings["background_bounds"])
if not _map_settings.get("calibrated", False):
    print("Note: Nasdara background bounds are provisional; calibrate custom_scripts/assets/nasdara-map-settings.json.")


def get_newest_log_file(log_dir):
    # Get all ExpLog files in the directory
    log_pattern = os.path.join(log_dir, 'ExpLog_*.log')
    log_files = glob.glob(log_pattern)
    
    if not log_files:
        raise FileNotFoundError("No log files found in specified directory")
    
    # Get the most recent file
    newest_log = max(log_files, key=os.path.getctime)
    return newest_log

def extract_datetime_from_filename(filepath):
    # Extract datetime string from filename (ExpLog_2025-02-01_16-01-25.log)
    filename = os.path.basename(filepath)
    date_time_str = filename.replace('ExpLog_', '').replace('.log', '')
    # Parse the datetime string
    dt = datetime.strptime(date_time_str, '%Y-%m-%d_%H-%M-%S')
    return dt

def plot_ai_patrol_coords(log_file_path, map_image_path, output_dir, dot_color='yellow', scale=None):
    bounds = NASDARA_BOUNDS if scale is None else (0, scale, 0, scale)
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read log file
    with open(log_file_path, 'r') as file:
        log_data = file.read()

    # Extract coordinates using regex
    coordinates = re.findall(r'<(\d+\.\d+),\s*(-?\d+\.\d+),\s*(\d+\.\d+)>', log_data)

    # Convert to float and separate X and Y (Y represented by third value)
    x_coords = [float(coord[0]) for coord in coordinates]
    y_coords = [float(coord[2]) for coord in coordinates]

    # Load map image
    img = mpimg.imread(map_image_path) if os.path.isfile(map_image_path) else None

    # Get formatted datetime for title
    dt = extract_datetime_from_filename(log_file_path)
    formatted_datetime = dt.strftime('%m/%d/%Y %H:%M')

    # Plotting with background map
    plt.figure(figsize=(10, 10))
    if img is not None:
        plt.imshow(img, extent=bounds, origin="upper")
    plt.scatter(x_coords, y_coords, color=dot_color, marker='o')
    plt.title(f'AI Patrol Coordinates - {formatted_datetime}\n({dot_color.capitalize()} Dots, Bounds {bounds})')
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.xlim(*bounds[:2])
    plt.ylim(*bounds[2:])
    plt.grid(False)

    # Generate output filename using datetime from log filename
    output_filename = f'roamer_plot_{dt.strftime("%Y-%m-%d_%H-%M-%S")}.png'
    output_path = os.path.join(output_dir, output_filename)
    
    # Save the plot
    plt.savefig(output_path)
    plt.close()
    
    return output_path

def main():
    # Define paths
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_dir = os.path.join(base_path, 'config', 'ExpansionMod', 'Logs')
    map_image_path = os.path.join(base_path, 'custom_scripts', 'assets', 'nasdara-map-background.png')
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

    try:
        # Get the newest log file
        newest_log = get_newest_log_file(log_dir)
        
        # Generate and save the plot
        output_path = plot_ai_patrol_coords(
            newest_log,
            map_image_path,
            output_dir,
            dot_color='yellow',
            scale=None
        )
        print(f"Plot saved successfully to: {output_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
