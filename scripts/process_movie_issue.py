import os
import json
import sys
import re
from urllib.parse import urlparse

def slugify(text):
    """Convert text to slug format"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

def parse_movie_issue(issue_body):
    """Parse movie issue body and extract information"""
    data = {}
    
    # Check if this is from issue form (contains ### format) or old template
    if '### Movie Title' in issue_body or '### Release Year' in issue_body:
        # Parse GitHub Issue Form format
        return parse_issue_form_movie(issue_body)
    else:
        # Parse old markdown template format
        return parse_markdown_template_movie(issue_body)

def parse_issue_form_movie(issue_body):
    """Parse movie issue from GitHub Issue Form"""
    data = {}
    urls = []
    
    # Extract title
    title_match = re.search(r'### Movie Title\s*\n\s*(.+)', issue_body, re.IGNORECASE)
    if title_match:
        data['title'] = title_match.group(1).strip()
    
    # Extract year
    year_match = re.search(r'### Release Year\s*\n\s*(\d{4})', issue_body, re.IGNORECASE)
    if year_match:
        data['year'] = int(year_match.group(1))
    
    # Extract source
    source_match = re.search(r'### Source\s*\n\s*(.+)', issue_body, re.IGNORECASE)
    source = source_match.group(1).strip() if source_match else 'GitHub Issue Form'
    
    # Extract primary URL
    primary_url_match = re.search(r'### Primary Streaming URL\s*\n\s*(https?://\S+)', issue_body, re.IGNORECASE)
    if primary_url_match:
        urls.append({
            'source': source,
            'url': primary_url_match.group(1),
            'quality': '1080p',
            'language': 'en'
        })
    
    # Extract alternative URLs
    alt_urls_match = re.search(r'### Alternative URLs \(Optional\)\s*\n\s*(.*?)(?=\n### |$)', issue_body, re.IGNORECASE | re.DOTALL)
    if alt_urls_match:
        alt_urls_text = alt_urls_match.group(1).strip()
        if alt_urls_text and alt_urls_text != '_No response_':
            lines = alt_urls_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and line.startswith('http'):
                    urls.append({
                        'source': source,
                        'url': line,
                        'quality': '1080p',
                        'language': 'en'
                    })
    
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
    
    return data, urls

def parse_markdown_template_movie(issue_body):
    """Parse movie issue from old markdown template format"""
    data = {}
    
    # Extract title
    title_match = re.search(r'\*\*Title:\*\*\s*(.+)', issue_body, re.IGNORECASE)
    if title_match:
        data['title'] = title_match.group(1).strip()
    
    # Extract year
    year_match = re.search(r'\*\*Year:\*\*\s*(\d{4})', issue_body, re.IGNORECASE)
    if year_match:
        data['year'] = int(year_match.group(1))
    
    # Extract URLs
    urls = []
    
    # Primary URL
    primary_url_match = re.search(r'\*\*Primary URL:\*\*\s*(https?://\S+)', issue_body, re.IGNORECASE)
    if primary_url_match:
        urls.append({
            'source': 'GitHub Issue',
            'url': primary_url_match.group(1),
            'quality': '1080p',
            'language': 'en'
        })
    
    # Alternative URLs - look for URLs in the code block
    alt_urls_section = re.search(r'\*\*Alternative URLs.*:\*\*\s*```\s*(.*?)\s*```', issue_body, re.IGNORECASE | re.DOTALL)
    if alt_urls_section:
        alt_urls_text = alt_urls_section.group(1).strip()
        if alt_urls_text:
            lines = alt_urls_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and line.startswith('http'):
                    urls.append({
                        'source': 'GitHub Issue',
                        'url': line,
                        'quality': '1080p',
                        'language': 'en'
                    })
    
    return data, urls

def create_movie_structure(data, urls, issue_number):
    """Create movie folder structure and files"""
    if not data.get('title'):
        raise ValueError("Movie title is required")
    
    # Generate slug
    slug = slugify(data['title'])
    if data.get('year'):
        slug = f"{slug}-{data['year']}"
    
    # Create folder path
    movie_path = os.path.join('api', 'movies', slug)
    os.makedirs(movie_path, exist_ok=True)
    
    # Check if about.json already exists
    about_file = os.path.join(movie_path, 'about.json')
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
        # Create new about.json
        about_data = {
            'title': data['title'],
            'category': 'Movies'
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
    
    # Save about.json
    with open(about_file, 'w', encoding='utf-8') as f:
        json.dump(about_data, f, indent=4, ensure_ascii=False)
    
    # Handle URLs - merge with existing if file exists
    urls_file = os.path.join(movie_path, 'urls.json')
    if urls:
        if os.path.exists(urls_file):
            # Load existing URLs and merge
            with open(urls_file, 'r', encoding='utf-8') as f:
                existing_urls = json.load(f)
            
            # Get existing URL set to avoid duplicates
            existing_url_set = {url_obj.get('url') for url_obj in existing_urls if isinstance(url_obj, dict)}
            
            # Add new URLs that don't already exist
            added_count = 0
            for new_url in urls:
                if new_url['url'] not in existing_url_set:
                    existing_urls.append(new_url)
                    added_count += 1
            
            # Save merged URLs
            with open(urls_file, 'w', encoding='utf-8') as f:
                json.dump(existing_urls, f, indent=4, ensure_ascii=False)
            
            print(f"Added {added_count} new URLs to existing movie: {data['title']}")
        else:
            # Create new urls.json
            with open(urls_file, 'w', encoding='utf-8') as f:
                json.dump(urls, f, indent=4, ensure_ascii=False)
            
            print(f"Created new movie: {data['title']}")
    
    # Create alternative mapping if IMDB ID is provided
    if data.get('imdb_id'):
        alt_path = os.path.join('api', 'alts', 'movies')
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
                'type': 'movies',
                'title': data['title'],
                'slug': [slug]
            }
        
        # Save alternative mapping
        with open(alt_file, 'w', encoding='utf-8') as f:
            json.dump(alt_data, f, indent=4, ensure_ascii=False)
    
    return slug

def main():
    if len(sys.argv) != 3:
        print("Usage: python process_movie_issue.py <issue_number> <issue_body>")
        sys.exit(1)
    
    issue_number = sys.argv[1]
    issue_body = sys.argv[2]
    
    try:
        data, urls = parse_movie_issue(issue_body)
        
        if not data.get('title'):
            print("Error: Movie title is required")
            sys.exit(1)
        
        if not urls:
            print("Error: At least one streaming URL is required")
            sys.exit(1)
        
        slug = create_movie_structure(data, urls, issue_number)
        print(f"Successfully processed movie issue #{issue_number}: {data['title']}")
        
    except Exception as e:
        print(f"Error processing movie issue: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()