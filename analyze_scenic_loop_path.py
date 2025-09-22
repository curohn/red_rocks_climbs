#!/usr/bin/env python3
"""
Red Rocks Scenic Loop Drive - Path-Based Route Analysis

This script uses actual waypoints along the Red Rocks Scenic Loop Drive
to determine the correct order of climbing areas as encountered while driving.

The scenic loop is a 13-mile one-way road that starts at the visitor center
and follows a horseshoe-shaped path through Red Rocks canyons.
"""

import pandas as pd
import numpy as np
import math
from collections import defaultdict

# Red Rocks Scenic Loop Drive waypoints (based on known geography)
# These represent major points along the actual road path
SCENIC_LOOP_WAYPOINTS = [
    # Start at visitor center area
    (36.1588, -115.4264, "Visitor Center / Entrance"),
    
    # Head west, then curve south
    (36.1450, -115.4450, "Early Drive Section"),
    (36.1300, -115.4600, "Calico Hills Approach"),
    
    # Calico Basin / First Pullout area (major climbing section)
    (36.1480, -115.4280, "Calico Basin / First Pullout"),
    
    # Continue south through canyons
    (36.1200, -115.4700, "Central Canyon Area"),
    (36.1000, -115.4800, "Southern Canyon Area"),
    
    # Curve east through Pine Creek, Juniper areas
    (36.1100, -115.5000, "Pine Creek Canyon"),
    (36.1150, -115.4900, "Juniper Canyon"),
    
    # Head back north/northeast
    (36.1250, -115.4850, "Icebox Canyon Area"),
    (36.1350, -115.4800, "Willow Spring Area"),
    
    # Final approach back to entrance
    (36.1500, -115.4650, "Late Drive Section"),
    (36.1588, -115.4264, "Return to Visitor Center")
]

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula."""
    R = 3959  # Earth's radius in miles
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def find_closest_waypoint_on_path(lat, lon):
    """
    Find the position along the scenic drive path for a given coordinate.
    Returns the progress along the path (0 = start, 1 = end).
    """
    min_distance = float('inf')
    closest_segment = 0
    closest_position_on_segment = 0
    
    # Check distance to each segment of the path
    for i in range(len(SCENIC_LOOP_WAYPOINTS) - 1):
        wp1_lat, wp1_lon, _ = SCENIC_LOOP_WAYPOINTS[i]
        wp2_lat, wp2_lon, _ = SCENIC_LOOP_WAYPOINTS[i + 1]
        
        # Find closest point on this segment
        segment_distance, position_on_segment = distance_to_line_segment(
            lat, lon, wp1_lat, wp1_lon, wp2_lat, wp2_lon
        )
        
        if segment_distance < min_distance:
            min_distance = segment_distance
            closest_segment = i
            closest_position_on_segment = position_on_segment
    
    # Calculate overall position along the path (0 to 1)
    total_segments = len(SCENIC_LOOP_WAYPOINTS) - 1
    path_position = (closest_segment + closest_position_on_segment) / total_segments
    
    return path_position, min_distance

def distance_to_line_segment(px, py, x1, y1, x2, y2):
    """
    Calculate distance from point (px, py) to line segment (x1,y1)-(x2,y2).
    Returns (distance, position_on_segment) where position is 0-1 along segment.
    """
    # Vector from start to end of segment
    dx = x2 - x1
    dy = y2 - y1
    
    # If segment has zero length, return distance to start point
    if dx == 0 and dy == 0:
        dist = calculate_distance(px, py, x1, y1)
        return dist, 0
    
    # Parameter t represents position along segment (0 = start, 1 = end)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    
    # Clamp t to segment bounds
    t = max(0, min(1, t))
    
    # Find closest point on segment
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    
    # Calculate distance to closest point
    distance = calculate_distance(px, py, closest_x, closest_y)
    
    return distance, t

def load_data(filename):
    """Load the CSV data and clean it up."""
    df = pd.read_csv(filename)
    
    # Clean up column names
    df.columns = df.columns.str.strip()
    
    # Extract area information from the Location column
    df['Area'] = df['Location'].str.split(' > ').str[0]
    df['Canyon'] = df['Location'].str.split(' > ').str[1]
    
    # Rename lat/lon columns for clarity
    if 'Area Latitude' in df.columns:
        df = df.rename(columns={'Area Latitude': 'Latitude', 'Area Longitude': 'Longitude'})
    
    # Remove rows with invalid coordinates
    df = df.dropna(subset=['Latitude', 'Longitude'])
    df = df[(df['Latitude'] != 0) & (df['Longitude'] != 0)]
    
    return df

def analyze_scenic_loop_order(df):
    """Analyze climbing areas and order them by position along scenic drive."""
    
    # Calculate path position for each route
    path_data = []
    
    for _, row in df.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        
        path_position, distance_to_path = find_closest_waypoint_on_path(lat, lon)
        
        path_data.append({
            'Route': row['Route'],
            'Area': row['Area'],
            'Canyon': row['Canyon'],
            'Latitude': lat,
            'Longitude': lon,
            'Path_Position': path_position,
            'Distance_to_Road': distance_to_path
        })
    
    # Create DataFrame from path data
    path_df = pd.DataFrame(path_data)
    
    # Add path position to original dataframe
    df['Path_Position'] = path_df['Path_Position']
    df['Distance_to_Road'] = path_df['Distance_to_Road']
    
    # Create sequential order based on path position
    df = df.sort_values('Path_Position')
    df['Scenic_Loop_Order'] = range(1, len(df) + 1)
    
    return df

def analyze_climbing_areas(df):
    """Group routes by area and calculate average positions along scenic drive."""
    area_data = defaultdict(list)
    
    for _, row in df.iterrows():
        area_key = f"{row['Area']} ({row['Canyon']})"
        
        area_data[area_key].append({
            'route': row['Route'],
            'latitude': row['Latitude'],
            'longitude': row['Longitude'],
            'path_position': row['Path_Position'],
            'distance_to_road': row['Distance_to_Road']
        })
    
    # Calculate average position for each area
    area_summary = []
    for area_name, routes in area_data.items():
        avg_lat = np.mean([r['latitude'] for r in routes])
        avg_lon = np.mean([r['longitude'] for r in routes])
        avg_path_pos = np.mean([r['path_position'] for r in routes])
        avg_distance = np.mean([r['distance_to_road'] for r in routes])
        
        area_summary.append({
            'area': area_name,
            'route_count': len(routes),
            'avg_latitude': avg_lat,
            'avg_longitude': avg_lon,
            'path_position': avg_path_pos,
            'avg_distance_to_road': avg_distance,
            'routes': routes
        })
    
    # Sort by path position along scenic drive
    area_summary.sort(key=lambda x: x['path_position'])
    
    return area_summary

def create_csv_with_scenic_order(df, output_filename="red_rocks_routes_with_scenic_order.csv"):
    """Create enhanced CSV with scenic loop order."""
    # Make sure we have the scenic loop analysis
    if 'Scenic_Loop_Order' not in df.columns:
        df = analyze_scenic_loop_order(df)
    
    # Save to CSV
    df.to_csv(output_filename, index=False)
    
    print(f"Enhanced route data saved to: {output_filename}")
    print(f"Routes now ordered by position along Scenic Loop Drive")
    print(f"Columns added: Path_Position, Distance_to_Road, Scenic_Loop_Order")
    
    return df

def print_results(area_summary):
    """Print the results in a readable format."""
    print("RED ROCKS SCENIC LOOP DRIVE - CLIMBING AREA ORDER")
    print("=" * 60)
    print("\nClimbing areas in order along the 13-mile one-way scenic drive:")
    print("(Based on path-distance analysis to actual road waypoints)\n")
    
    for i, area in enumerate(area_summary, 1):
        print(f"{i:3d}. {area['area']}")
        print(f"     Routes: {area['route_count']}")
        print(f"     Path Position: {area['path_position']:.4f} (0=start, 1=end)")
        print(f"     Avg Distance to Road: {area['avg_distance_to_road']:.2f} miles")
        print(f"     Coordinates: {area['avg_latitude']:.5f}, {area['avg_longitude']:.5f}")
        
        # Show first few routes as examples
        route_names = [r['route'] for r in area['routes']]
        if len(route_names) <= 3:
            print(f"     Example routes: {', '.join(route_names)}")
        else:
            print(f"     Example routes: {', '.join(route_names[:3])}, ... (+{len(route_names)-3} more)")
        print()

def save_detailed_results(area_summary, filename="scenic_loop_order_detailed.txt"):
    """Save detailed results to a file."""
    with open(filename, 'w') as f:
        f.write("RED ROCKS SCENIC LOOP DRIVE - DETAILED CLIMB ORDER\n")
        f.write("=" * 65 + "\n\n")
        f.write("METHODOLOGY:\n")
        f.write("This analysis uses waypoints along the actual 13-mile Scenic Loop Drive\n")
        f.write("to determine the correct order of climbing areas as encountered while driving.\n")
        f.write("Each area's position is calculated based on distance to the road path.\n\n")
        
        f.write("WAYPOINTS USED:\n")
        for i, (lat, lon, desc) in enumerate(SCENIC_LOOP_WAYPOINTS, 1):
            f.write(f"{i:2d}. {desc} - ({lat:.4f}, {lon:.4f})\n")
        f.write("\n")
        
        f.write("All climbing routes organized by area, in scenic drive order:\n\n")
        
        for i, area in enumerate(area_summary, 1):
            f.write(f"{i:3d}. {area['area']}\n")
            f.write(f"     Total Routes: {area['route_count']}\n")
            f.write(f"     Path Position: {area['path_position']:.4f} (0=start, 1=end)\n")
            f.write(f"     Average Distance to Road: {area['avg_distance_to_road']:.3f} miles\n")
            f.write(f"     Average Coordinates: {area['avg_latitude']:.5f}, {area['avg_longitude']:.5f}\n")
            f.write("     All Routes:\n")
            
            # Sort routes within area by name
            routes = sorted(area['routes'], key=lambda x: x['route'])
            for route in routes:
                f.write(f"       - {route['route']}\n")
            f.write("\n")

def main():
    """Main function."""
    print("Analyzing Red Rocks climbing areas using Scenic Loop Drive path...")
    
    # Load the data
    df = load_data('red_rocks_routes.csv')
    print(f"Loaded {len(df)} climbing routes")
    
    # Analyze scenic loop order
    df = analyze_scenic_loop_order(df)
    
    # Group by areas
    area_summary = analyze_climbing_areas(df)
    
    # Print results
    print_results(area_summary)
    
    # Save detailed results
    save_detailed_results(area_summary)
    
    # Create enhanced CSV with scenic loop order
    create_csv_with_scenic_order(df)
    
    print(f"\nAnalysis complete!")
    print(f"Found {len(area_summary)} unique climbing areas")
    print(f"First area encountered: {area_summary[0]['area']}")
    print(f"Last area encountered: {area_summary[-1]['area']}")

if __name__ == "__main__":
    main()