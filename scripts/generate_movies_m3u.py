import os
import json

def generate_m3u_entry(title, category, logo_url, urls):
    attributes = f'tvg-logo="{logo_url}" group-title="{category}"'
    url_lines = '\n'.join(urls)
    return f'\n#EXTINF:-1 {attributes},{title}\n{url_lines}'

def main():
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    project_root = os.path.dirname(script_dir)

    base_path = os.path.join(project_root, 'api', 'movies')
    output_path = os.path.join(project_root, 'movies.m3u')

    m3u_content = ['#EXTM3U', '# This file is auto-generated. It will be updated after a PR merge or a push to the main branch.']

    movie_folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d)) and d != 'stub']

    for movie_folder in sorted(movie_folders):
        movie_path = os.path.join(base_path, movie_folder)
        about_file = os.path.join(movie_path, 'about.json')
        urls_file = os.path.join(movie_path, 'urls.json')

        if not all([os.path.exists(about_file), os.path.exists(urls_file)]):
            continue

        try:
            with open(about_file, 'r') as f:
                about_data = json.load(f)
            
            with open(urls_file, 'r') as f:
                urls_data = json.load(f)

            title = about_data.get('title', movie_folder)
            year = about_data.get('year')
            if year:
                title = f"{title} ({year})"

            category = about_data.get('category', 'Movies')
            cover_url = about_data.get('cover') or ''
            
            movie_urls = []
            if urls_data and isinstance(urls_data, list):
                for url_item in urls_data:
                    if url_item and isinstance(url_item, dict) and url_item.get('url'):
                        movie_urls.append(url_item['url'])
            
            if movie_urls:
                m3u_entry = generate_m3u_entry(title, category, cover_url, movie_urls)
                m3u_content.append(m3u_entry)

        except (json.JSONDecodeError, IndexError) as e:
            print(f"Warning: Could not process {movie_folder}. Error: {e}")
            continue

    with open(output_path, 'w') as f:
        f.write('\n'.join(m3u_content))

    print(f'{os.path.basename(output_path)} generated successfully.')

if __name__ == "__main__":
    main()