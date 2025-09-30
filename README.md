# M3U-Repo - Movie & TV Database

**M3U-Repo** is a movie and TV series metadata database organized by available providers like IMDB, TMDB, and others. This database serves as the main source for the **[Pusoo](https://github.com/cacing69/pusoo)** project.

## Easy Contributing

Want to add content? It's super easy! Just create an issue with interactive forms

### Super Simple Format

**For Movies**: Just need title, year, and streaming URL
**For TV Series**: Just need title, year, and episode URLs like this:

```md
### Season 1
#### Episodes
**URLs:**
- url episode 1
- url episode 2
```

**For Alternative URLs**: Add backup links to existing content anytime!

> **Note:** Data is very limited, but Pull Requests and contributions are very welcome!

## How It Works

### Automated Contribution Process

1. **Create Issue**: Use our templates to create an issue for adding movies or TV series
2. **Fill Template**: Provide title, year, streaming URLs, and optional metadata
3. **Submit**: GitHub Actions automatically processes your issue
4. **Done**: Content is added to the repository and M3U playlists are updated

### For TV Series

When adding TV series, you can include multiple seasons and episodes:

```md
### Season 1

#### Episode 1
**URLs:**
- Primary: https://your-streaming-link.com/s01e01.mp4
- Alternative: https://backup-link.com/s01e01.mp4

#### Episode 2
**URLs:**
- Primary: https://your-streaming-link.com/s01e02.mp4
```

The system will automatically create the proper folder structure

## Playlist

> Movies Playlist

```bash
https://raw.githubusercontent.com/cacing69/m3u-repo/refs/heads/main/movies.m3u
```

> TV Series Playlist

```bash
https://raw.githubusercontent.com/cacing69/m3u-repo/refs/heads/main/tv-series.m3u
```

## API Usage

This repository can be used as an API by utilizing GitHub's raw file access:

### GitHub API Key (Recommended)

For better rate limits and reliability, use a GitHub API key:

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Example API call
curl -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/cacing69/m3u-repo/contents/api/movies/{slug-name}/subtitles/id/index.json"
```

### Raw File Access

Direct access to raw files (limited rate):

```bash
# Example raw file URL
https://raw.githubusercontent.com/cacing69/m3u-repo/main/api/movies/{slug-name}/subtitles/id/index.json
```

### Rate Limits

- **Without API key**: 60 requests/hour
- **With API key**: 5,000 requests/hour

## Structure

- api/movie/{slug-name}/subtitles/{language_code}/index.json
- api/tv/{slug-name}/s/{season}/e/{episode}/subtitles/{language_code}/index.json
- api/alts/movies/{imdb_id}.json - Slug name return refer to movies and tv-series

### Parameters

- `{slug-name}` - Slug name
- `{language_code}` - Language code (see below)
- `{season}` - Season number (unsigned int, e.g., 1, 2, 3)
- `{episode}` - Episode number (unsigned int, e.g., 1, 2, 3)
- `{title}` - Title slug (e.g., el-camino, breaking-bad)

### Language Codes (ISO 639-1)

- `id` - Indonesian
- `en` - English
