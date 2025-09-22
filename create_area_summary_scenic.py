#!/usr/bin/env python3
"""
Create area summary with scoring using the new path-based scenic loop ordering
"""

import pandas as pd
import numpy as np
import re

def parse_rating(rating_str):
    """Parse climbing rating and return difficulty level."""
    if pd.isna(rating_str) or rating_str == '':
        return 0
    
    # Convert to string and clean up
    rating = str(rating_str).strip().upper()
    
    # Remove modifiers like PG13, R, X, etc.
    rating = re.sub(r'\s+(PG13|PG|R|X|A\d|C\d)', '', rating)
    
    # Handle 5.x ratings
    if rating.startswith('5.'):
        try:
            # Extract the numeric part after 5.
            parts = rating[2:].split()
            base_rating = parts[0] if parts else ''
            
            # Remove +/- modifiers for classification
            clean_rating = re.sub(r'[+-]', '', base_rating)
            
            # Convert to float for comparison
            if clean_rating.isdigit():
                num_rating = int(clean_rating)
            elif '.' in clean_rating:
                num_rating = float(clean_rating)
            else:
                # Handle cases like 10a, 10b, 10c, 10d, 11a, etc.
                if len(clean_rating) >= 2 and clean_rating[:-1].isdigit():
                    base_num = int(clean_rating[:-1])
                    letter = clean_rating[-1]
                    # Convert letter grades to decimal
                    letter_values = {'A': 0.0, 'B': 0.25, 'C': 0.5, 'D': 0.75}
                    num_rating = base_num + letter_values.get(letter, 0)
                else:
                    num_rating = 0
            
            return num_rating
        except:
            return 0
    
    # Handle other rating systems or return 0
    return 0

def calculate_difficulty_score(rating_str):
    """Calculate difficulty score based on 5.7-5.10 sweet spot."""
    difficulty = parse_rating(rating_str)
    
    if difficulty == 0:
        return 0
    elif difficulty >= 7 and difficulty <= 10.75:  # 5.7-5.10d (sweet spot)
        return 2
    elif difficulty < 7:  # Under 5.7 (easier/warm-up routes)
        return 1
    else:  # Above 5.10d (too difficult for target grade)
        return 0

def calculate_route_type_score(route_type_str):
    """Calculate route type score."""
    if pd.isna(route_type_str):
        return 0
    
    route_type = str(route_type_str).strip()
    
    if 'Sport' in route_type:
        return 1  # Bonus for sport routes
    elif 'Multi-Pitch' in route_type:
        return -1  # Penalty for multi-pitch complexity
    else:
        return 0

def calculate_pitch_score(pitches):
    """Calculate pitch score (penalty for multi-pitch)."""
    if pd.isna(pitches):
        return 0
    
    try:
        pitch_count = int(pitches)
        if pitch_count > 1:
            return -1  # Multi-pitch penalty
        else:
            return 0
    except:
        return 0

def calculate_stars_score(avg_stars):
    """Calculate stars score."""
    if pd.isna(avg_stars) or avg_stars <= 0:
        return 0
    return avg_stars

def categorize_grade(rating_str):
    """Categorize route by grade."""
    difficulty = parse_rating(rating_str)
    
    if difficulty == 0:
        return 'unknown'
    elif difficulty <= 6.75:  # 5.0-5.6
        return '5.0-5.6'
    elif difficulty >= 7 and difficulty <= 8.75:  # 5.7-5.8
        return '5.7-5.8'
    elif difficulty >= 9 and difficulty <= 10.75:  # 5.9-5.10d
        return '5.9-5.10'
    elif difficulty >= 11 and difficulty <= 11.75:  # 5.11a-5.11d
        return '5.11'
    elif difficulty >= 12:  # 5.12+
        return '5.12+'
    else:
        return 'unknown'

def create_area_summary_scenic(csv_file):
    """Create area summary with scoring using scenic loop ordering."""
    
    # Load the data
    df = pd.read_csv(csv_file)
    
    # Calculate individual scores for each route
    df['difficulty_score'] = df['Rating'].apply(calculate_difficulty_score)
    df['route_type_score'] = df['Route Type'].apply(calculate_route_type_score)
    df['pitch_score'] = df['Pitches'].apply(calculate_pitch_score)
    df['stars_score'] = df['Avg Stars'].apply(calculate_stars_score)
    df['grade_category'] = df['Rating'].apply(categorize_grade)
    
    # Calculate total score for each route
    df['total_score'] = (1 +  # Base point for each climb
                        df['difficulty_score'] + 
                        df['route_type_score'] + 
                        df['pitch_score'] + 
                        df['stars_score'])
    
    # Group by Area and Canyon and calculate basic stats
    area_summary = df.groupby(['Area', 'Canyon']).agg({
        'Route': 'count',  # Number of climbs
        'total_score': 'sum',  # Total score for all routes
        'Path_Position': 'mean',  # Average path position
        'Scenic_Loop_Order': 'min',  # First encounter on scenic drive
        'Avg Stars': 'mean',  # Average stars
        'Latitude': 'mean',  # Average coordinates
        'Longitude': 'mean'
    }).round(4)
    
    # Count routes by grade category
    grade_counts = df.groupby(['Area', 'Canyon', 'grade_category']).size().unstack(fill_value=0)
    
    # Count routes by route type (trad vs sport)
    route_type_counts = df.groupby(['Area', 'Canyon', 'Route Type']).size().unstack(fill_value=0)
    
    # Create trad and sport columns
    trad_count = pd.DataFrame(index=route_type_counts.index, columns=['num_trad'])
    sport_count = pd.DataFrame(index=route_type_counts.index, columns=['num_sport'])
    
    # Count trad routes (anything containing "Trad")
    trad_count['num_trad'] = route_type_counts.filter(regex='.*Trad.*', axis=1).sum(axis=1)
    
    # Count sport routes (anything containing "Sport")  
    sport_count['num_sport'] = route_type_counts.filter(regex='.*Sport.*', axis=1).sum(axis=1)
    
    # Ensure all grade categories exist as columns
    for grade in ['5.0-5.6', '5.7-5.8', '5.9-5.10', '5.11', '5.12+', 'unknown']:
        if grade not in grade_counts.columns:
            grade_counts[grade] = 0

    # Merge the grade counts and route type counts with area summary
    area_summary = area_summary.join(grade_counts)
    area_summary = area_summary.join(trad_count)
    area_summary = area_summary.join(sport_count)
    
    # Rename columns
    area_summary = area_summary.rename(columns={
        'Route': 'num_routes',
        'total_score': 'total_score',
        'Path_Position': 'avg_path_position',
        'Scenic_Loop_Order': 'first_scenic_order',
        'Avg Stars': 'avg_stars'
    })
    
    # Calculate score per route for ranking
    area_summary['score_per_route'] = (area_summary['total_score'] / area_summary['num_routes']).round(2)
    
    # Sort by scenic loop order (encounter order on the road)
    area_summary = area_summary.sort_values('first_scenic_order').reset_index()
    
    # Add a ranking based on total score
    area_summary['score_rank'] = area_summary['total_score'].rank(method='dense', ascending=False).astype(int)
    
    return area_summary

def main():
    """Main function."""
    print("Creating area summary with path-based scenic loop ordering...")
    
    # Create the summary
    summary_df = create_area_summary_scenic('red_rocks_routes_with_scenic_order.csv')
    
    # Save to CSV
    output_file = 'red_rocks_area_summary_scenic_loop.csv'
    summary_df.to_csv(output_file, index=False)
    
    print(f"Area summary saved to: {output_file}")
    print(f"Found {len(summary_df)} unique area/canyon combinations")
    
    # Display first 10 areas (in scenic drive order)
    print(f"\nFirst 10 Areas Encountered on Scenic Drive:")
    first_areas = summary_df.head(10)
    for _, row in first_areas.iterrows():
        grade_breakdown = f"5.7-5.8:{row['5.7-5.8']}, 5.9-5.10:{row['5.9-5.10']}, 5.11:{row['5.11']}"
        print(f"{row['first_scenic_order']:3d}. {row['Area']} ({row['Canyon']}) - "
              f"Score: {row['total_score']:.1f}, Routes: {row['num_routes']}, "
              f"Trad/Sport: {row['num_trad']}/{row['num_sport']} [{grade_breakdown}]")
    
    # Display top scoring areas  
    print(f"\nTop 10 Highest Scoring Areas:")
    top_areas = summary_df.nlargest(10, 'total_score')
    for _, row in top_areas.iterrows():
        grade_breakdown = f"5.7-5.8:{row['5.7-5.8']}, 5.9-5.10:{row['5.9-5.10']}, 5.11:{row['5.11']}"
        print(f"{row['score_rank']:2d}. {row['Area']} ({row['Canyon']}) - "
              f"Order #{row['first_scenic_order']}, Score: {row['total_score']:.1f}, Routes: {row['num_routes']}, "
              f"Trad/Sport: {row['num_trad']}/{row['num_sport']} [{grade_breakdown}]")

    print(f"\nPath-Based Methodology Summary:")
    print(f"- Uses actual waypoints along 13-mile Scenic Loop Drive")
    print(f"- Areas ordered by encounter sequence while driving")  
    print(f"- Pine Creek Canyon now properly grouped together")
    print(f"- First area: {summary_df.iloc[0]['Area']} (Order #{summary_df.iloc[0]['first_scenic_order']})")
    print(f"- Last area: {summary_df.iloc[-1]['Area']} (Order #{summary_df.iloc[-1]['first_scenic_order']})")
    
    print(f"\nTotal routes analyzed: {summary_df['num_routes'].sum()}")
    print(f"Average score per route across all areas: {summary_df['total_score'].sum() / summary_df['num_routes'].sum():.2f}")

if __name__ == "__main__":
    main()