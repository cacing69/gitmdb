import os
import json
import sys
import re

def slugify(text):
    """Convert text to slug format"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

def parse_tv_series_issue(issue_body):
    """Parse TV series issue body and extract information"""
    # Check if this is from issue form (contains ### format) or old template
    if '### Series Title' in issue_body or '### Release Year' in issue_body:
        # Parse GitHub Issue Form format
        return parse_issue_form_tv_series(issue_body)
    else:
        # Parse old markdown template format
        return parse_markdown_template_tv_series(issue_body)

def parse_issue_form_tv_series(issue_body):
    """Parse TV series issue from GitHub Issue Form"""
    data = {}
    episodes = {}
    
    # Extract basic information
    title_match = re.search(r'### Series Title\s*\n\s*(.+)', issue_body, re.IGNORECASE)
    if title_match:
        data['title'] = title_match.group(1).strip()
    
    year_match = re.search(r'### Release Year\s*\n\s*(\d{4})', issue_body, re.IGNORECASE)
    if year_match:
        data['year'] = int(year_match.group(1))
    
    # Extract source
    source_match = re.search(r'### Source\s*\n\s*(.+)', issue_body, re.IGNORECASE)
    source = source_match.group(1).strip() if source_match else 'GitHub Issue Form'
    
    # Extract IMDB ID
    imdb_match = re.search(r'### IMDB ID \(Optional\)\s*\n\s*(tt\d+)', issue_body, re.IGNORECASE)
    if imdb_match:
        data['imdb_id'] = imdb_match.group(1)
    
    # Extract cover URL
    cover_match = re.search(r'### Cover/Poster URL \(Optional\)\s*\n\s*(https?://\S+)', issue_body, re.IGNORECASE)
    if cover_match:
        data['cover'] = cover_match.group(1)
    
    # Extract summary
    summary_match = re.search(r'### Summary \(Optional\)\s*\n\s*(.*?)(?=\n### |$)', issue_body, re.IGNORECASE | re.DOTALL)
    if summary_match:
        summary = summary_match.group(1).strip()
        if summary and summary != '_No response_':
            data['summary'] = summary
    
    # Extract series status
    status_match = re.search(r'### Series Status \(Optional\)\s*\n\s*(.+)', issue_body, re.IGNORECASE)
    if status_match:
        status = status_match.group(1).strip()
        if status and status != '_No response_':
            data['status'] = status.lower()
    
    # Parse episodes data
    episodes_match = re.search(r'### Episodes URLs\s*\n\s*(.*?)(?=\n### |$)', issue_body, re.IGNORECASE | re.DOTALL)
    if episodes_match:
        episodes_text = episodes_match.group(1).strip()
        if episodes_text and episodes_text != '_No response_':
            episodes = parse_episodes_format(episodes_text, source)
    
    return data, episodes

def parse_markdown_template_tv_series(issue_body):
    """Parse TV series issue from old markdown template format"""
    data = {}
    episodes = {}
    
    # Extract basic information
    title_match = re.search(r'\*\*Title:\*\*\s*(.+)', issue_body, re.IGNORECASE)
    if title_match:
        data['title'] = title_match.group(1).strip()
    
    year_match = re.search(r'\*\*Year:\*\*\s*(\d{4})', issue_body, re.IGNORECASE)
    if year_match:
        data['year'] = int(year_match.group(1))
    
    # Parse episodes data with simplified format
    seasons_section = re.search(r'## Episodes Data\s*.*?\n(.*?)(?=---|\Z)', issue_body, re.DOTALL | re.IGNORECASE)
    if seasons_section:
        episodes_text = seasons_section.group(1)
        episodes = parse_episodes_format(episodes_text, 'GitHub Issue')
    
    return data, episodes

def parse_episodes_format(episodes_text, source='GitHub Issue'):
    """Parse episodes format that works for both form and template"""
    episodes = {}
    
    # Find all seasons
    season_matches = re.finditer(r'### Season (\d+)', episodes_text, re.IGNORECASE)
    
    for season_match in season_matches:
        season_num = int(season_match.group(1))
        
        # Find the end of this season section
        next_season = re.search(r'### Season \d+', episodes_text[season_match.end():])
        if next_season:
            season_text = episodes_text[season_match.end():season_match.end() + next_season.start()]
        else:
            season_text = episodes_text[season_match.end():]
        
        # Find URLs list for this season
        urls_match = re.search(r'#### Episodes\s*\*\*URLs:\*\*\s*\n((?:- .*\n?)*)', season_text, re.IGNORECASE | re.MULTILINE)
        
        if urls_match:
            urls_text = urls_match.group(1)
            url_lines = urls_text.strip().split('\n')
            
            season_episodes = {}
            episode_num = 1
            
            for line in url_lines:
                line = line.strip()
                if line.startswith('- ') and 'http' in line:
                    # Extract URL from line
                    url_match = re.search(r'(https?://\S+)', line)
                    if url_match:
                        url = url_match.group(1)
                        
                        if episode_num not in season_episodes:
                            season_episodes[episode_num] = []
                        
                        season_episodes[episode_num].append({
                            'source': source,
                            'url': url,
                            'quality': '1080p',
                            'language': 'en'
                        })
                        episode_num += 1
            
            if season_episodes:
                episodes[season_num] = season_episodes
    
    return episodes

def create_tv_series_structure(data, episodes, issue_number):
    """Create TV series folder structure and files"""
    if not data.get('title'):
        raise ValueError("TV series title is required")
    
    # Generate slug
    slug = slugify(data['title'])
    
    # Create main series folder
    series_path = os.path.join('api', 'tv-series', slug)
    os.makedirs(series_path, exist_ok=True)
    
    # Check if about.json already exists
    about_file = os.path.join(series_path, 'about.json')
    if os.path.exists(about_file):
        # Load existing data and merge
        with open(about_file, 'r', encoding='utf-8') as f:
            existing_about = json.load(f)
        
        # Merge new data with existing, keeping existing values if new ones are not provided
        about_data = existing_about.copy()
        for key, value in data.items():
            if value:  # Only update if new value is not empty
                about_data[key] = value
    else:
        # Create new about.json for series
        about_data = {
            'title': data['title'],
            'category': 'TV Series'
        }
        
        if data.get('year'):
            about_data['year'] = data['year']
        if data.get('summary'):
            about_data['summary'] = data['summary']
        if data.get('cover'):
            about_data['cover'] = data['cover']
        if data.get('imdb_id'):
            about_data['imdb_id'] = data['imdb_id']
        if data.get('tmdb_id'):
            about_data['tmdb_id'] = data['tmdb_id']
        if data.get('genre'):
            about_data['genre'] = data['genre']
        if data.get('total_seasons'):
            about_data['total_seasons'] = data['total_seasons']
        if data.get('status'):
            about_data['status'] = data['status']
    
    # Save about.json
    with open(about_file, 'w', encoding='utf-8') as f:
        json.dump(about_data, f, indent=4, ensure_ascii=False)
    
    # Create seasons and episodes structure
    if episodes:
        seasons_path = os.path.join(series_path, 's')
        os.makedirs(seasons_path, exist_ok=True)
        
        for season_num, season_episodes in episodes.items():
            season_path = os.path.join(seasons_path, str(season_num))
            os.makedirs(season_path, exist_ok=True)
            
            episodes_path = os.path.join(season_path, 'e')
            os.makedirs(episodes_path, exist_ok=True)
            
            for episode_num, episode_urls in season_episodes.items():
                episode_path = os.path.join(episodes_path, str(episode_num))
                os.makedirs(episode_path, exist_ok=True)
                
                # Handle URLs - merge with existing if file exists
                urls_file = os.path.join(episode_path, 'urls.json')
                if os.path.exists(urls_file):
                    # Load existing URLs and merge
                    with open(urls_file, 'r', encoding='utf-8') as f:
                        existing_urls = json.load(f)
                    
                    # Get existing URL set to avoid duplicates
                    existing_url_set = {url_obj.get('url') for url_obj in existing_urls if isinstance(url_obj, dict)}
                    
                    # Add new URLs that don't already exist
                    added_count = 0
                    for new_url in episode_urls:
                        if new_url['url'] not in existing_url_set:
                            existing_urls.append(new_url)
                            added_count += 1
                    
                    # Save merged URLs
                    with open(urls_file, 'w', encoding='utf-8') as f:
                        json.dump(existing_urls, f, indent=4, ensure_ascii=False)
                    
                    if added_count > 0:
                        print(f"Added {added_count} new URLs to S{season_num}E{episode_num}")
                else:
                    # Create new urls.json for episode
                    with open(urls_file, 'w', encoding='utf-8') as f:
                        json.dump(episode_urls, f, indent=4, ensure_ascii=False)
                    
                    print(f"Created new episode S{season_num}E{episode_num}")
                
                # Create empty subtitles folders if they don't exist
                subtitles_path = os.path.join(episode_path, 'subtitles')
                for lang in ['en', 'id']:
                    lang_path = os.path.join(subtitles_path, lang)
                    if not os.path.exists(lang_path):
                        os.makedirs(lang_path, exist_ok=True)
                        
                        # Create empty index.json for subtitles
                        subtitle_index = os.path.join(lang_path, 'index.json')
                        if not os.path.exists(subtitle_index):
                            with open(subtitle_index, 'w', encoding='utf-8') as f:
                                json.dump([], f, indent=4)
    
    # Create alternative mapping if IMDB ID is provided
    if data.get('imdb_id'):
        alt_path = os.path.join('api', 'alts', 'tv-series')
        os.makedirs(alt_path, exist_ok=True)
        
        alt_file = os.path.join(alt_path, f"{data['imdb_id']}.json")
        
        # Check if alternative mapping already exists
        if os.path.exists(alt_file):
            # Load existing and merge slug if not already present
            with open(alt_file, 'r', encoding='utf-8') as f:
                alt_data = json.load(f)
            
            if 'slug' in alt_data and isinstance(alt_data['slug'], list):
                if slug not in alt_data['slug']:
                    alt_data['slug'].append(slug)
            else:
                alt_data['slug'] = [slug]
        else:
            # Create new alternative mapping
            alt_data = {
                'type': 'tv-series',
                'title': data['title'],
                'slug': [slug]
            }
        
        # Save alternative mapping
        with open(alt_file, 'w', encoding='utf-8') as f:
            json.dump(alt_data, f, indent=4, ensure_ascii=False)
    
    return slug

def main():
    if len(sys.argv) != 3:
        print("Usage: python process_tv_series_issue.py <issue_number> <issue_body>")
        sys.exit(1)
    
    issue_number = sys.argv[1]
    issue_body = sys.argv[2]
    
    try:
        data, episodes = parse_tv_series_issue(issue_body)
        
        if not data.get('title'):
            print("Error: TV series title is required")
            sys.exit(1)
        
        if not episodes:
            print("Error: At least one episode with streaming URL is required")
            sys.exit(1)
        
        slug = create_tv_series_structure(data, episodes, issue_number)
        print(f"Successfully processed TV series issue #{issue_number}: {data['title']}")
        
    except Exception as e:
        print(f"Error processing TV series issue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()