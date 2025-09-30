#!/usr/bin/env python3
"""
Validation script for M3U-Repo content
"""

import os
import json
import sys
from pathlib import Path

def validate_json_file(file_path):
    """Validate if a file contains valid JSON"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

def validate_movie_structure(movie_path):
    """Validate movie folder structure"""
    errors = []
    
    # Check required files
    about_file = os.path.join(movie_path, 'about.json')
    urls_file = os.path.join(movie_path, 'urls.json')
    
    if not os.path.exists(about_file):
        errors.append(f"Missing about.json in {movie_path}")
    else:
        valid, error = validate_json_file(about_file)
        if not valid:
            errors.append(f"Invalid about.json in {movie_path}: {error}")
        else:
            # Check required fields
            with open(about_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'title' not in data:
                    errors.append(f"Missing 'title' field in {about_file}")
    
    if not os.path.exists(urls_file):
        errors.append(f"Missing urls.json in {movie_path}")
    else:
        valid, error = validate_json_file(urls_file)
        if not valid:
            errors.append(f"Invalid urls.json in {movie_path}: {error}")
        else:
            # Check if it's a list with valid URLs
            with open(urls_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if not isinstance(data, list):
                    errors.append(f"urls.json should be a list in {movie_path}")
                elif len(data) == 0:
                    errors.append(f"urls.json is empty in {movie_path}")
    
    return errors

def validate_tv_series_structure(series_path):
    """Validate TV series folder structure"""
    errors = []
    
    # Check about.json
    about_file = os.path.join(series_path, 'about.json')
    if not os.path.exists(about_file):
        errors.append(f"Missing about.json in {series_path}")
    else:
        valid, error = validate_json_file(about_file)
        if not valid:
            errors.append(f"Invalid about.json in {series_path}: {error}")
    
    # Check seasons structure
    seasons_path = os.path.join(series_path, 's')
    if os.path.exists(seasons_path):
        for season_dir in os.listdir(seasons_path):
            season_path = os.path.join(seasons_path, season_dir)
            if os.path.isdir(season_path):
                episodes_path = os.path.join(season_path, 'e')
                if os.path.exists(episodes_path):
                    for episode_dir in os.listdir(episodes_path):
                        episode_path = os.path.join(episodes_path, episode_dir)
                        if os.path.isdir(episode_path):
                            urls_file = os.path.join(episode_path, 'urls.json')
                            if os.path.exists(urls_file):
                                valid, error = validate_json_file(urls_file)
                                if not valid:
                                    errors.append(f"Invalid urls.json in {urls_file}: {error}")
    
    return errors

def main():
    """Main validation function"""
    repo_root = Path(__file__).parent.parent
    api_path = repo_root / 'api'
    
    if not api_path.exists():
        print("Error: api folder not found")
        sys.exit(1)
    
    total_errors = 0
    
    # Validate movies
    movies_path = api_path / 'movies'
    if movies_path.exists():
        print("Validating movies...")
        for movie_dir in movies_path.iterdir():
            if movie_dir.is_dir() and movie_dir.name != 'stub':
                errors = validate_movie_structure(str(movie_dir))
                if errors:
                    print(f"Movie {movie_dir.name}:")
                    for error in errors:
                        print(f"  - {error}")
                    total_errors += len(errors)
                else:
                    print(f"  ✓ {movie_dir.name}")
    
    # Validate TV series
    tv_series_path = api_path / 'tv-series'
    if tv_series_path.exists():
        print("\nValidating TV series...")
        for series_dir in tv_series_path.iterdir():
            if series_dir.is_dir() and series_dir.name != 'stub':
                errors = validate_tv_series_structure(str(series_dir))
                if errors:
                    print(f"TV Series {series_dir.name}:")
                    for error in errors:
                        print(f"  - {error}")
                    total_errors += len(errors)
                else:
                    print(f"  ✓ {series_dir.name}")
    
    # Summary
    print(f"\nValidation complete. Total errors: {total_errors}")
    
    if total_errors > 0:
        sys.exit(1)
    else:
        print("All content is valid!")
        sys.exit(0)

if __name__ == "__main__":
    main()