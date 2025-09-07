HAZARD_FEATURE_MAP = {
    "flood": ["hospitals", "shelters", "evacuation_routes", "road_status",
              "flood_zones", "critical_infra"],
    "cyclone": ["hospitals", "shelters", "evacuation_routes", "road_status",
                "flood_zones", "critical_infra"],
    "earthquake": ["hospitals", "shelters", "road_status", "terrain_profile",
                   "critical_infra"],
    "landslide": ["hospitals", "shelters", "road_status", "terrain_profile",
                  "critical_infra"],
    "wildfire": ["hospitals", "shelters", "evacuation_routes", "road_status",
                 "land_use_land_cover", "critical_infra"],
    "heatwave": ["hospitals", "shelters", "water_points", "critical_infra"],
    "drought": ["hospitals", "water_points", "critical_infra"],
    "industrial_accident": ["hospitals", "shelters", "evacuation_routes",
                            "police_fire", "critical_infra"],
    "unknown": ["hospitals", "shelters", "critical_infra"]
}