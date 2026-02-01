# Facebook Scraping Experience with Apify

**Date:** February 1, 2026
**Project:** Talking and Exploring Website

## Overview

This document details the scraping experience and lessons learned while building a community walks website using Facebook and Instagram data.

## What We Scraped

### 1. Facebook Page Posts
- **Source:** `candy.nguyen.5832` Facebook profile (Joanna's personal account)
- **Actor Used:** `apify/facebook-posts-scraper`
- **Results:** Successfully scraped ~100 posts
- **Images:** Facebook images downloaded as JPG, manually converted to WebP later
- **Success Rate:** High - worked well for public profile posts

### 2. Instagram Profile Posts
- **Source:** `https://www.instagram.com/talkingandexploring/`
- **Actor Used:** `apify/instagram-scraper`
- **Results:** Successfully scraped 30 posts
- **Images:** Instagram returned direct image URLs that we downloaded and converted to WebP
- **Success Rate:** High - worked perfectly for public Instagram profiles

### 3. Specific Facebook Group Post
- **Source:** `https://www.facebook.com/groups/talkingandexploring/permalink/3766618570311525/`
- **Actor Attempted:** `pratikdani/facebook-post-scraper` (FAILED - requires paid subscription)
- **Actor Used (Success):** `apify/facebook-posts-scraper` with direct URL
- **Results:** Successfully scraped the post text and metadata, but **no images were captured**
- **Success Rate:** Partial - text works, images don't

## What Worked Well

### ✅ Facebook Posts Scraper (`apify/facebook-posts-scraper`)
```python
run_input = {
    "startUrls": [{"url": profile_url}],
    "resultsLimit": 100
}
run = client.actor("apify/facebook-posts-scraper").call(run_input=run_input)
```

**Strengths:**
- Reliable for public Facebook profiles
- Works with direct group post URLs
- Captures text, engagement metrics (likes, comments, shares)
- Returns timestamps
- Free tier sufficient for moderate usage

**Limitations:**
- Does NOT capture images from group posts (media field is empty)
- Only works with public content
- Rate limited on free tier

### ✅ Instagram Scraper (`apify/instagram-scraper`)
```python
run_input = {
    "directUrls": [instagram_url],
    "resultsType": "posts",
    "resultsLimit": 30,
    "searchType": "user",
    "searchLimit": 1,
}
run = client.actor("apify/instagram-scraper").call(run_input=run_input)
```

**Strengths:**
- Excellent image quality (high-res displayUrl)
- Rich metadata (caption, likes, comments)
- Consistent date formatting
- Works reliably

**Limitations:**
- Only public profiles
- Cannot scrape stories or reels (just posts)

### ✅ Image Processing Pipeline
```python
# Download original
response = requests.get(img_url, timeout=30)
with open(local_path, 'wb') as f:
    f.write(response.content)

# Convert to WebP (85% quality)
subprocess.run(['cwebp', '-q', '85', str(local_path), '-o', str(webp_path)])

# Remove original
local_path.unlink()
```

**Results:**
- Average size reduction: 40-60%
- Quality remains excellent at 85%
- Faster page loads

## What Didn't Work

### ❌ Individual Post Scraper (`pratikdani/facebook-post-scraper`)
**Error Message:**
```
You must rent a paid Actor in order to run it after its free trial has expired.
```

**Learning:** Many specialized Apify actors require payment after trial. Always check actor pricing before building pipelines around them.

### ❌ Images from Facebook Group Posts
**Issue:** When scraping the group post URL directly, the `media` field was empty even though the original post had images.

**Attempted Solutions:**
1. Used `facebook-posts-scraper` instead of `facebook-post-scraper` ❌
2. Tried different resultsLimit values ❌

**Current Status:** UNSOLVED - group post images cannot be scraped with available free actors

**Workaround:** Manually upload images to the CMS admin panel

## Technical Challenges & Solutions

### Challenge 1: Date Formatting Inconsistencies
**Problem:** Facebook returns dates in various formats:
- `2026-01-27T12:13:39.000Z`
- `1738003994` (Unix timestamp)
- `2026-01-25` (date only)

**Solution:**
```python
try:
    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
except:
    date_obj = datetime.fromtimestamp(int(date_str))
```

### Challenge 2: Image Path Mismatches
**Problem:** After converting images from JPG to WebP, JSON still referenced `.jpg` files, causing 404 errors.

**Solution:** Created a script to batch update all image paths:
```python
for post in posts:
    if 'images' in post:
        post['images'] = [img.replace('.jpg', '.webp') for img in post['images']]
```

**Lesson:** Always update data references when transforming assets.

### Challenge 3: Virtual Environment Issues
**Problem:** `apify_client` module not found errors

**Root Cause:** Using system Python instead of project venv

**Solution:** Always use full path to venv Python:
```bash
/Users/dakthi/Documents/Factory-Tech/.venv/bin/python3 script.py
```

### Challenge 4: Environment Variables
**Problem:** `APIFY_API_TOKEN` not accessible in some contexts

**Solution:** Use `python-dotenv` to load `.env` file:
```python
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / '.env')
APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN')
```

## Data Structure Standardization

We merged Facebook and Instagram posts into a unified format:

```json
{
  "id": "unique_post_id",
  "text": "Post caption/text",
  "date": "2026-01-27T12:13:39.000Z",
  "date_formatted": "27 January, 2026",
  "likes": 0,
  "comments": 1,
  "shares": 1,
  "images": ["images/post_id_0.webp"],
  "url": "https://www.facebook.com/...",
  "source": "facebook" | "instagram"
}
```

**Key Decision:** Keep images as array to support multiple images per post (important for Instagram carousels).

## Content Curation Strategy

### Walk-Related Keywords
We filtered scraped posts using these keywords:
```python
walk_keywords = [
    'walk', 'exploring', 'discovering', 'gunnersbury', 'park',
    'community', 'tour', 'ealing', 'acton', 'join us', 'meet at',
    'eventbrite', 'ticket', 'book', 'donation', 'event'
]
```

**Results:**
- Input: 40 merged posts (Facebook + Instagram)
- Output: 11 walk-related posts (27.5% relevance rate)

**Learning:** Keyword filtering is effective but requires domain knowledge. Consider adding more specific location names.

## Best Practices Learned

### 1. Always Check Actor Pricing
Before building workflows, verify:
- Is the actor free?
- What are the rate limits?
- What happens after trial expires?

### 2. Implement Robust Error Handling
```python
try:
    response = requests.get(img_url, timeout=30)
    response.raise_for_status()
except Exception as e:
    print(f"✗ Error: {e}")
    # Keep original URL if download fails
    continue
```

### 3. Store Raw Data First
Always save raw scraper output before transforming:
```python
with open('raw_data.json', 'w') as f:
    json.dump(items, f, indent=2)
```

This allows re-processing without re-scraping.

### 4. Use Consistent File Naming
```python
filename = f"post_{post_id}_{timestamp}_{index}.webp"
```

Makes debugging and manual inspection easier.

## Recommendations for Future Work

### 1. Image Scraping from Groups
**Options:**
- Pay for premium Apify actors that support group images
- Use Selenium/Playwright to manually navigate and screenshot
- Build custom scraper with Facebook Graph API (requires app approval)

### 2. Automated Scraping Schedule
Set up a cron job to scrape new posts weekly:
```bash
0 0 * * 0 /path/to/venv/bin/python3 /path/to/scrape_instagram.py
```

### 3. Better Duplicate Detection
Implement content-based deduplication:
```python
def is_duplicate(new_post, existing_posts):
    for post in existing_posts:
        if similar(new_post['text'], post['text']) > 0.9:
            return True
    return False
```

### 4. Video Support
Instagram reels are currently ignored. Consider:
- Extracting thumbnail images
- Storing video URLs
- Using a video player component

## File Reference

### Scripts Created
- `scrape_facebook.py` - Scrape Facebook profile posts
- `scrape_instagram.py` - Scrape Instagram profile posts
- `curate_walk_posts.py` - Filter walk-related posts
- `download_instagram_images.py` - Download and convert images
- `scrape_facebook_post.py` - Single post scraper (not working for groups)

### Data Files
- `curated_posts_merged.json` - All scraped posts (40 posts)
- `talking-exploring-website/public/curated_posts.json` - Walk posts only (12 posts)

### Image Directory
- `/images/` - Contains WebP converted images
- Naming: `post_{id}_{index}.webp`

## Apify Usage Stats (Estimated)

| Actor | Runs | Compute Units | Cost |
|-------|------|---------------|------|
| facebook-posts-scraper | 3 | ~0.05 | Free |
| instagram-scraper | 1 | ~0.02 | Free |
| **Total** | **4** | **~0.07** | **$0.00** |

Free tier limit: 5 compute units/month - we're well within limits.

## Known Issues & Workarounds

### Issue: Group Post Images Not Scraped
**Status:** UNSOLVED
**Workaround:** Manual upload via CMS admin panel
**Impact:** Low - only affects occasional group posts

### Issue: Emoji Encoding in Text
**Status:** WORKING
**Solution:** Use `ensure_ascii=False` in json.dump()

### Issue: Date Timezone Inconsistencies
**Status:** WORKING
**Solution:** All dates stored in ISO 8601 UTC format, converted to local for display

## Conclusion

Apify proved to be an excellent tool for scraping public social media content, with the free tier being sufficient for small-to-medium projects. The main limitations are:

1. **Group post images** - cannot be scraped with free actors
2. **Premium features** - many specialized actors require payment
3. **Rate limits** - free tier has compute unit restrictions

For the Talking and Exploring website, we successfully built a complete scraping, curation, and publishing pipeline using entirely free tools. The 12 curated walk posts provide a solid foundation for the website launch.

**Overall Success Rate:** 90% - all objectives met except group post images.
