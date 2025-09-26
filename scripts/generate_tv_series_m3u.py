import os
import json

def generate_m3u_entry(display_name, group_title, urls, logo_url=""):
    attributes = f'tvg-logo="{logo_url}" group-title="{group_title}"'
    url_lines = '\n'.join(urls)
    return f'\n#EXTINF:-1 {attributes},{display_name}\n{url_lines}'

def main():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)

    base_path = os.path.join(project_root, 'api', 'tv-series')
    output_path = os.path.join(project_root, 'tv-series.m3u')

    m3u_content = ['#EXTM3U', '# This file is auto-generated. It will be updated after a PR merge or a push to the main branch.']

    series_folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d != 'stub']

    for series_folder in sorted(series_folders):
        series_path = os.path.join(base_path, series_folder)
        series_about_file = os.path.join(series_path, 'about.json')

        if not os.path.exists(series_about_file):
            continue

        # Parent series metadata (defaults)
        parent_clean_title = series_folder
        parent_title_with_year = series_folder
        parent_cover_url = ""
        try:
            with open(series_about_file, 'r') as f:
                about_data = json.load(f)
                parent_clean_title = about_data.get('title', series_folder)
                parent_title_with_year = parent_clean_title
                year = about_data.get('year')
                if year:
                    parent_title_with_year = f"{parent_clean_title} ({year})"
                parent_cover_url = about_data.get('cover') or ''
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {series_about_file}")
            continue

        seasons_path = os.path.join(series_path, 's')
        if not os.path.exists(seasons_path):
            continue

        for season_folder in sorted(os.listdir(seasons_path), key=lambda f: int(f) if f.isdigit() else 0):
            season_path = os.path.join(seasons_path, season_folder)
            if not os.path.isdir(season_path):
                continue
            
            season_number = season_folder
            group_title_for_season = f"{parent_clean_title} Temporada {season_number}"

            # Season-specific metadata (overrides)
            season_title_with_year = parent_title_with_year
            season_cover_url = parent_cover_url
            season_about_file = os.path.join(season_path, 'about.json')
            if os.path.exists(season_about_file):
                try:
                    with open(season_about_file, 'r') as f_season:
                        season_about_data = json.load(f_season)
                        
                        # Use season-specific title for group-title if it exists
                        season_specific_title = season_about_data.get('title')
                        if season_specific_title:
                            group_title_for_season = season_specific_title
                        
                        # Override display title for the season if present
                        season_display_title = season_about_data.get('title', parent_clean_title)
                        season_year = season_about_data.get('year')
                        if season_year:
                            season_title_with_year = f"{season_display_title} ({season_year})"
                        else:
                            season_title_with_year = season_display_title
                        # Override cover for the season if present
                        season_cover_url = season_about_data.get('cover') or parent_cover_url
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode JSON from {season_about_file}")

            episodes_path = os.path.join(season_path, 'e')
            if not os.path.exists(episodes_path):
                continue

            for episode_folder in sorted(os.listdir(episodes_path), key=lambda f: int(f) if f.isdigit() else 0):
                episode_path = os.path.join(episodes_path, episode_folder)
                if not os.path.isdir(episode_path):
                    continue
                
                episode_number = episode_folder
                
                # Determine display name
                info_file = os.path.join(episode_path, 'info.json')
                display_name = f"{parent_clean_title} Temporada {season_number} - S{season_number}E{episode_number}"
                if os.path.exists(info_file):
                    try:
                        with open(info_file, 'r') as f_info:
                            info_data = json.load(f_info)
                            episode_title = info_data.get('title')
                            if episode_title:
                                display_name = f"{display_name} - {episode_title}"
                    except json.JSONDecodeError:
                        print(f"Warning: Could not decode JSON from {info_file}")

                # Get URLs
                urls_file = os.path.join(episode_path, 'urls.json')
                if os.path.exists(urls_file):
                    episode_urls = []
                    with open(urls_file, 'r') as f_urls:
                        try:
                            urls_data = json.load(f_urls)
                            if urls_data and isinstance(urls_data, list):
                                for url_item in urls_data:
                                    if url_item and isinstance(url_item, dict) and url_item.get('url'):
                                        episode_urls.append(url_item['url'])
                        except (json.JSONDecodeError, IndexError) as e:
                            print(f"Warning: Could not process {urls_file}. Error: {e}")
                    
                    if episode_urls:
                        m3u_entry = generate_m3u_entry(display_name, group_title_for_season, episode_urls, logo_url=season_cover_url)
                        m3u_content.append(m3u_entry)


    with open(output_path, 'w') as f:
        f.write('\n'.join(m3u_content))

    print(f'{os.path.basename(output_path)} generated successfully.')

if __name__ == "__main__":
    main()
