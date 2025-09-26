# GitMDB - Movie & TV Database

**GitMDB** is a movie and TV series metadata database organized by available providers like IMDB, TMDB, and others. This database serves as the main source for the **[Pusoo](https://github.com/cacing69/pusoo)** project.

> **Note:** Data is very limited, but Pull Requests and contributions are very welcome!

## API Usage

This repository can be used as an API by utilizing GitHub's raw file access:

### GitHub API Key (Recommended)

For better rate limits and reliability, use a GitHub API key:

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Example API call
curl -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/cacing69/gitmdb/contents/api/movies/{slug-name}/subtitles/id/index.json"
```

### Raw File Access

Direct access to raw files (limited rate):

```bash
# Example raw file URL
https://raw.githubusercontent.com/cacing69/gitmdb/main/api/movies/{slug-name}/subtitles/id/index.json
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
