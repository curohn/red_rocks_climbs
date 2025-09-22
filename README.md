# Red Rocks Climbing Route Analysis

A comprehensive analysis of 1,000 climbing routes at Red Rocks National Conservation Area, organized by their order along the scenic loop drive and scored based on climbing preferences.

**🚨 Methodology Update:** This analysis now uses a **path-based approach** that follows the actual Red Rocks Scenic Loop Drive, replacing an earlier polar coordinate method that fragmented canyon groupings. Areas are now correctly sequenced as encountered while driving.

## Overview

This project processes Mountain Project climbing data to:
- **Sequence areas** along the Red Rocks Scenic Loop Drive using coordinate analysis
- **Score climbing areas** based on preferences for 5.7-5.10 grade climbers  
- **Categorize routes** by type (traditional vs sport) and difficulty grades
- **Generate trip planning data** with comprehensive area summaries

## Files Generated

### Data Files
- **`red_rocks_routes_with_scenic_order.csv`** - All 1,000 routes with correct scenic loop positions
- **`red_rocks_area_summary_scenic_loop.csv`** - 176 area summaries with path-based ordering and comprehensive scoring

### Documentation
- **`README.md`** - This comprehensive guide
- **`scenic_loop_order_detailed.txt`** - Complete route listings by area in drive order

### Analysis Scripts
- **`analyze_scenic_loop_path.py`** - Path-based coordinate analysis and scenic drive sequencing
- **`create_area_summary_scenic.py`** - Area scoring and grade categorization with correct drive ordering

## Methodology

### Scenic Loop Drive Sequencing (Path-Based Analysis)
Uses actual waypoints along the Red Rocks 13-mile Scenic Loop Drive to determine the correct order areas are encountered while driving. The algorithm:

1. **Defines waypoints** along the actual one-way scenic drive path from visitor center through all major sections
2. **Calculates distance to path** for each climbing area using line-segment geometry
3. **Orders areas sequentially** by their position along the drive (0=start, 1=end)
4. **Groups canyon areas** properly together (fixing the fragmentation issue from polar coordinates)

**Key Waypoints:**
- Visitor Center / Entrance (starting point)
- Kraft Mountain Area (first climbing areas)
- Calico Basin / First Pullout (major sport climbing section)
- Central and Southern Canyon Areas
- Pine Creek & Juniper Canyons (mid-drive traditional climbing)
- Icebox Canyon & Willow Spring (later traditional areas)
- Wake-Up Wall Area (final major section before return)

### Scoring System (Optimized for 5.7-5.10 Climbers)

**Base Points:**
- Every climb: **+1 point**
- Star rating: **+1 point per star** (0-4 stars)

**Difficulty Bonuses:**
- Routes 5.7-5.10: **+2 points** (sweet spot)
- Routes under 5.7: **+1 point** (warm-up routes)
- Routes over 5.10: **+0 points** (too difficult)

**Route Type Modifiers:**
- Sport routes: **+1 point** (bolt protection)
- Multi-pitch routes: **-1 point** (time/complexity)
- Traditional routes: **+0 points** (neutral)

### Grade Categories
- **5.0-5.6:** Beginner routes
- **5.7-5.8:** Intermediate (target sweet spot)
- **5.9-5.10:** Advanced (target sweet spot)
- **5.11:** Expert level  
- **5.12+:** Very advanced
- **Unknown:** Missing/unclear grades

## Key Statistics

- **Total Areas:** 176 unique climbing areas
- **Total Routes:** 1,000 climbing routes
- **Traditional Routes:** 545 (54.5%)
- **Sport Routes:** 423 (42.3%)
- **Other Route Types:** 32 (3.2%)
- **Average Score per Route:** 5.17 points

## Top Recommended Areas

### Highest Overall Scores
1. **Wake-Up Wall** (131.3 pts) - 24 routes: 3 trad, 21 sport
2. **Panty Wall** (117.1 pts) - 21 routes: 5 trad, 13 sport  
3. **Flight Path Area** (115.0 pts) - 22 routes: all trad
4. **Jungle Wall** (108.2 pts) - 20 routes: 15 trad, 3 sport
5. **Brass Wall** (107.3 pts) - 21 routes: all trad

### Best Sport Climbing Areas
- **Wake-Up Wall:** 21 sport routes (highest score)
- **Southwest Wall:** 15 sport routes (all sport)
- **Cactus Massacre:** 15 sport routes
- **Rift Corridor - Left:** 14 sport routes (all sport)

### Best Traditional Climbing Areas  
- **Flight Path Area:** 22 trad routes (all trad)
- **Brass Wall:** 21 trad routes (all trad)
- **Sunnyside Crags:** 20 trad routes (all trad)
- **Ragged Edges Area:** 20 trad routes (all trad)

## Using the Data

### For Trip Planning
1. **Focus on high-scoring areas** (90+ points) for optimal 5.7-5.10 climbing
2. **Check route type breakdown** to match your gear preferences
3. **Use ring road order** to plan efficient area transitions
4. **Review grade distributions** to ensure appropriate difficulty spread

### CSV Column Reference

**Route Data (`red_rocks_routes_with_scenic_order.csv`):**
- `Path_Position`: Position along scenic drive (0=start, 1=end)
- `Scenic_Loop_Order`: Sequential order (1-1000) encountered on scenic drive
- `Distance_to_Road`: Distance from climbing area to scenic drive path
- Plus all original Mountain Project data (route name, grade, stars, etc.)

**Area Summary (`red_rocks_area_summary_scenic_loop.csv`):**
- `total_score`: Total points for all routes in area
- `score_per_route`: Average points per route (for quality comparison)
- `num_trad` / `num_sport`: Count of traditional vs sport routes
- `5.7-5.8`, `5.9-5.10`, etc.: Route counts by difficulty category
- `first_scenic_order`: When area is first encountered on the scenic drive
- `avg_path_position`: Average position along drive (0=start, 1=end)
- `score_rank`: Overall ranking by total score

## Dependencies

**Python Libraries:**
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computations  
- `matplotlib` - Visualization (optional, for plots)
- `re` - Regular expressions for grade parsing

## Usage

```bash
# Generate scenic loop positions (path-based analysis)
python analyze_scenic_loop_path.py

# Create area summaries with scoring and correct drive ordering
python create_area_summary_scenic.py
```

## Trip Planning Recommendations

**For Sport Climbers:** Focus on the First Pullout (Calico Basin) section - high concentration of bolted routes with excellent scoring.

**For Traditional Climbers:** Pine Creek Canyon and Icebox Canyon areas offer the best trad climbing with high scores.

**For Mixed Preferences:** Wake-Up Wall and Jungle Wall provide both route types with top-tier scoring.

**Scenic Drive Strategy:** Use the path-based scenic loop order to plan your day efficiently, starting from the first areas encountered (Kraft Mountain Area) and working through the drive sequentially to minimize driving time between areas.

---

*Analysis based on Mountain Project data - always verify current route conditions and access before climbing.*