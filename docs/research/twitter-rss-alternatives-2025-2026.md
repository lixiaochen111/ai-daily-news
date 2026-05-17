# Twitter/X RSS Feed Alternatives (2025-2026)

**Research Date:** May 15, 2026  
**Context:** Finding working alternatives to official X API ($100+/month) for tracking Twitter users via RSS

---

## Summary

As of 2025-2026, getting Twitter/X user feeds as RSS is extremely challenging:

- Official X API requires $100+/month minimum
- Most third-party scrapers (TWINT, snscrape) are broken or archived
- Public Nitter instances are largely shut down
- RSS bridge services are unstable or blocked
- Browser extensions and free tools are mostly non-functional

**Current Working Solutions:**

1. **Self-hosted Nitter** (requires Twitter accounts)
2. **twscrape** (Python, requires Twitter accounts)
3. **twitter_openapi_python** (Python library, no official API)
4. **RSS.app** (paid service, $8.32/month minimum)
5. **IFTTT** (automation platform with Twitter support)
6. **Follow Builders approach** (centralized scraping + public JSON feeds)

---

## 1. Self-Hosted Solutions

### Nitter (Self-Hosted)

**Status:** Still functional but requires Twitter accounts

**Requirements:**
- Self-hosting capability (Docker or manual installation)
- Real Twitter account(s) with session tokens
- Redis/Valkey database
- Nim programming language (for manual install)

**Pros:**
- Open source and privacy-focused
- Generates RSS feeds for users, searches, hashtags
- No JavaScript, lightweight
- Full control over instance

**Cons:**
- Requires real Twitter accounts (session tokens)
- Twitter actively blocks Nitter instances
- Maintenance burden
- Account risk (may get suspended)

**Setup:**
```bash
# Docker installation
docker pull zedeus/nitter
# Follow wiki for session token configuration
```

**URLs:**
- GitHub: https://github.com/zedeus/nitter
- Instance list: https://github.com/zedeus/nitter/wiki/Instances
- Status checker: https://status.d420.de

**Working Public Instances (as of May 2026):**
- xcancel.com
- nitter.poast.org
- nitter.privacyredirect.com
- lightbrd.com (Turkey, NSFW enabled)
- nitter.space (US, with ads)
- nitter.tiekoetter.com (Germany)
- nuku.trabun.org (Chile)
- nitter.catsarch.com
- nitter.kareem.one (Singapore)

**Note:** Public instances are unreliable and frequently go offline. Self-hosting is recommended for production use.

---

### twscrape (Python Library)

**Status:** Actively maintained (latest release April 2025)

**Requirements:**
- Python 3.8+
- Authorized Twitter/X accounts (multiple recommended)
- Optional: proxy service for rate limit management

**Features:**
- Async/await support for parallel scraping
- Search results, user profiles, tweets, followers/following
- Automatic account switching for rate limits
- Session management (saves/restores login state)
- Supports both Search & GraphQL Twitter API

**Pros:**
- Recently updated (April 2025)
- Good documentation
- Does not require official API access
- Handles rate limiting automatically

**Cons:**
- Requires Twitter accounts
- Account suspension risk
- Need proxies for large-scale scraping
- No built-in RSS generation (need custom code)

**Installation:**
```bash
pip install twscrape
```

**Example Usage:**
```python
from twscrape import AccountsPool, API

pool = AccountsPool()
await pool.add_account("username", "password", "email", "email_password")
api = API(pool)

# Search tweets
async for tweet in api.search("AI", limit=100):
    print(tweet.text)
```

**URLs:**
- GitHub: https://github.com/vladkens/twscrape
- PyPI: https://pypi.org/project/twscrape/

**Use Case for RSS:** You can build a custom RSS generator on top of twscrape:
1. Scrape user timeline periodically
2. Convert tweets to RSS items
3. Cache results to avoid re-scraping
4. Serve via local RSS feed

---

### twitter_openapi_python

**Status:** Active (v0.0.14, February 2024)

**Requirements:**
- Python environment
- Pydantic library

**Features:**
- Python library for Twitter's internal GraphQL API
- Typed interface with Pydantic validation
- Two packages: human-friendly and auto-generated
- No official API access required

**Pros:**
- Type-safe with Pydantic
- Well-structured API
- Active development

**Cons:**
- Less mature than twscrape
- May break if Twitter changes internal API
- No built-in RSS generation
- Requires Twitter account credentials

**Installation:**
```bash
pip install twitter-openapi-python
```

**URLs:**
- GitHub: https://github.com/fa0311/twitter_openapi_python
- Documentation: See GitHub README

**Use Case:** Similar to twscrape, can be used as foundation for custom RSS feed generator.

---

### ntscraper (Nitter-based scraper)

**Status:** Maintained (v0.4.0, May 2025) but limited functionality

**Requirements:**
- Python
- Working Nitter instance (self-hosted recommended)

**Features:**
- Scrapes tweets via Nitter instances
- Search by term, hashtag, or user profile
- Multiprocessing support
- Configurable logging

**Pros:**
- Works through Nitter (no direct Twitter API)
- Recently updated

**Cons:**
- **Most Nitter instances are down**
- Severely limited due to Twitter blocking
- Requires self-hosted Nitter for reliability
- Not suitable for production without own instance

**Installation:**
```bash
pip install ntscraper
```

**URLs:**
- GitHub: https://github.com/bocchilorenzo/ntscraper

**Warning:** README explicitly states "Twitter has recently made some changes which affected every third party Twitter client, including Nitter."

---

## 2. Paid Services

### RSS.app

**Status:** Working (active as of 2025-2026)

**Pricing:**
- **Free Plan:** 2 feeds, 24-hour refresh, limited features
- **Basic ($8.32/month):** 15 feeds, 25 posts per feed, 60-min refresh
- **Developer ($16.64/month):** 100 feeds, 50 posts/feed, 15-min refresh
- **Pro ($83.32/month):** 500 feeds, API access, team features

**Features:**
- X/Twitter RSS feed generation
- Auto-posting to Discord, Slack, Telegram, email
- Feed filtering and customization
- 7-day free trial (no credit card)

**Pros:**
- Easy to use (no coding)
- Supports multiple platforms
- Reliable service
- Good pricing for small-scale use

**Cons:**
- Paid service (free tier very limited)
- 60-minute refresh on Basic plan (not real-time)
- May be using official API internally (unclear if sustainable)

**URLs:**
- Website: https://rss.app
- Twitter RSS: https://rss.app/rss-feed/create-twitter-rss-feed
- Pricing: https://rss.app/pricing

**Recommendation:** Best option for non-technical users with budget <$20/month.

---

### IFTTT (If This Then That)

**Status:** Working (X/Twitter integration active)

**Features:**
- Automate X/Twitter workflows
- Triggers: new tweet by you, new mention, new hashtag
- Actions: post tweet, cross-post to other platforms
- Log tweets to Google Sheets, Notion, etc.

**Pros:**
- Still supports X integration (as of 2026)
- Easy no-code automation
- Connect to 50+ services
- Can create pseudo-RSS by logging to spreadsheet

**Cons:**
- Not a direct RSS solution
- Limited free tier (exact limits unclear)
- May require Pro/Pro+ for advanced features
- Not designed for feed aggregation

**URLs:**
- Website: https://ifttt.com
- X Integration: https://ifttt.com/twitter

**Use Case for RSS:**
1. Create applet: "New tweet by user" → "Add row to Google Sheet"
2. Share Google Sheet as pseudo-feed
3. Parse sheet with custom script
4. Generate RSS from parsed data

Not ideal, but workable for small-scale personal use.

---

## 3. Broken/Archived Solutions

### TWINT (Archived)

**Status:** Archived March 30, 2023 - DO NOT USE

**Note:** Repository is read-only. Project states "An advanced Twitter scraping & OSINT tool written in Python that doesn't use Twitter's API" but is no longer maintained.

**URLs:**
- GitHub: https://github.com/twintproject/twint

---

### snscrape (Broken)

**Status:** All Twitter scrapes failing with 404 errors

**Last Working:** Before June 2023

**Known Issues:**
- Issue #996: "All Twitter scrapes are failing: blocked (404)"
- Multiple open issues about Twitter module failure
- Maintainer confirmed blocking issue

**URLs:**
- GitHub: https://github.com/JustAnotherArchivist/snscrape
- Issues: https://github.com/JustAnotherArchivist/snscrape/issues

**Recommendation:** Do not use for Twitter scraping.

---

### Zapier Twitter Integration

**Status:** Discontinued August 31, 2023

**Official Statement:** "Due to Twitter's decision to change its API policy and pricing, Zapier's current Twitter integration has stopped working."

**Alternatives Suggested:**
- Buffer, Hootsuite for social media management
- Facebook Pages, Instagram Business, LinkedIn

**URLs:**
- Integration page: https://zapier.com/apps/twitter/integrations/rss

---

### TwitRSS.me, Tweeterss.com

**Status:** Both appear down (521/503 errors)

These services were popular free Twitter RSS generators but are no longer accessible as of May 2026.

---

## 4. Alternative Approaches

### Follow Builders Pattern (Recommended for this project)

**Status:** Working (used by zarazhangrui/follow-builders)

**Concept:**
1. Centralized service uses official X API with credentials
2. Scrapes curated list of builders/accounts
3. Publishes results as public JSON feeds
4. Downstream users consume JSON (no API needed)

**Example:**
- Follow Builders generates: `feed-x.json`, `feed-blogs.json`, `feed-podcasts.json`
- AI News Radar consumes these public files
- End users never need X API credentials

**Pros:**
- Separates API costs from end users
- Sustainable for curated lists
- Public consumers don't need credentials
- Good for community-maintained lists

**Cons:**
- Requires central maintainer with API access
- Not suitable for arbitrary user tracking
- Centralization risk

**Implementation Pattern:**
```python
# In a GitHub Actions workflow with X API credentials
def fetch_twitter_builders():
    # Use official API to fetch tweets from curated list
    tweets = fetch_from_x_api(user_list)
    # Save to public JSON
    save_json("feed-x.json", tweets)
    # Commit and push to GitHub
    
# In downstream project (no credentials needed)
def consume_builders():
    # Fetch public JSON
    data = requests.get("https://example.com/feed-x.json").json()
    # Convert to RSS or display
```

**Use Case for AI News Radar:**
- Track specific AI builders/researchers
- Maintain curated list in GitHub
- Use GitHub Actions with X API secret
- Publish sanitized feed for public consumption

---

### Browser Extensions

**Status:** Limited availability

**Found Projects:**
- Squawker (Android, MIT License) - F-Droid available
- Squawkkers (Android, MIT License)
- piko (Android, GPL-3.0)
- Fritter (Android, open source Twitter client)

**Limitation:** All Android-only, no desktop browser extensions found for RSS generation.

**Recommendation:** Not suitable for server-side or automated RSS generation.

---

### Gallery-dl / yt-dlp

**Status:** Uncertain for Twitter

Both tools support downloading from many platforms, but specific Twitter support status in 2025-2026 is unclear:

- **gallery-dl:** Mentions Twitter support but no confirmation of current status
- **yt-dlp:** Open issue about x.com rebranding (#33267, Apr 2026), suggests problems

**Recommendation:** Not reliable for RSS generation; designed for downloading media, not tracking timelines.

---

## 5. Services Not Evaluated

Unable to verify these services (connection errors or no Twitter support):

- **Feed43** (503 error)
- **PolitePaul/Politepol** (redirected, no clear Twitter support)
- **OpenRSS** (no specific Twitter mention)
- **Feedspot** (no clear Twitter RSS support)
- **Phantom Buster** (503 error)
- **Apify Twitter scrapers** (404 error)

---

## Recommendations for AI News Radar

Based on the project's requirements (from SOURCE_COVERAGE.md):

### Current Strategy (Keep)

**Follow Builders approach:**
- Consume public `feed-x.json` from zarazhangrui/follow-builders
- No direct X API dependency for public users
- Maintainer handles API credentials centrally

**Pros:**
- Aligns with project philosophy (secret-backed, opt-in)
- Works with GitHub Actions
- No credentials in public repo

### Advanced Strategy (Optional)

**For maintainers with budget:**

1. **Self-hosted Nitter instance:**
   - Deploy on VPS with Twitter accounts
   - Generate RSS for specific users
   - Cost: $5-10/month VPS + account risk
   
2. **twscrape + custom RSS generator:**
   - Python script in GitHub Actions
   - Use GitHub Secrets for credentials
   - Enable with `X_SCRAPER_ENABLED=1`
   - Generate public JSON like Follow Builders

3. **RSS.app Basic plan:**
   - $8.32/month for 15 feeds
   - Suitable for small curated list
   - Less technical maintenance
   - May violate "no paid API" principle

### Not Recommended

- Official X API ($100+/month - too expensive)
- TWINT, snscrape (broken)
- Zapier (discontinued)
- Public Nitter instances (unreliable)
- Browser extensions (not automated)

---

## Technical Implementation Guide

### Option 1: Self-Hosted Nitter

```bash
# 1. Set up VPS (DigitalOcean, Hetzner, etc.)
# 2. Install Docker
# 3. Clone Nitter
git clone https://github.com/zedeus/nitter.git
cd nitter

# 4. Configure with Twitter account tokens
# See: https://github.com/zedeus/nitter/wiki

# 5. Start instance
docker-compose up -d

# 6. RSS feeds available at:
# https://your-nitter.com/username/rss
```

### Option 2: twscrape Custom RSS

```python
# scripts/fetch_twitter_rss.py
import asyncio
from twscrape import AccountsPool, API
import feedgen.feed

async def generate_user_rss(username, limit=50):
    pool = AccountsPool()
    # Load accounts from environment
    await pool.add_account(
        os.getenv("TWITTER_USERNAME"),
        os.getenv("TWITTER_PASSWORD"),
        os.getenv("TWITTER_EMAIL"),
        os.getenv("TWITTER_EMAIL_PASSWORD")
    )
    
    api = API(pool)
    
    # Fetch user tweets
    tweets = []
    async for tweet in api.user_tweets(username, limit=limit):
        tweets.append({
            "id": tweet.id,
            "text": tweet.text,
            "url": tweet.url,
            "created_at": tweet.date
        })
    
    # Generate RSS
    fg = feedgen.feed.FeedGenerator()
    fg.title(f"Twitter - @{username}")
    fg.link(href=f"https://twitter.com/{username}")
    fg.description(f"Latest tweets from @{username}")
    
    for tweet in tweets:
        fe = fg.add_entry()
        fe.id(tweet["url"])
        fe.title(tweet["text"][:100])
        fe.link(href=tweet["url"])
        fe.published(tweet["created_at"])
        fe.content(tweet["text"])
    
    return fg.rss_str(pretty=True)

# Run in GitHub Actions with secrets
if __name__ == "__main__":
    users = ["sama", "demishassabis", "drjimfan"]
    for user in users:
        rss = asyncio.run(generate_user_rss(user))
        with open(f"data/twitter-{user}.rss", "wb") as f:
            f.write(rss)
```

### Option 3: Follow Builders Consumer (Current)

```python
# Already implemented in scripts/update_news.py
def fetch_follow_builders_x(session, now):
    """Fetch public X feed from Follow Builders"""
    url = "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json"
    response = session.get(url, timeout=30)
    data = response.json()
    
    items = []
    for entry in data:
        items.append(RawItem(
            site_id="follow_builders_x",
            site_name="Follow Builders X",
            source="X",
            title=entry["title"],
            url=entry["url"],
            published_at=parse_datetime(entry["publishedAt"]),
            meta={"author": entry.get("author")}
        ))
    return items
```

---

## Cost Comparison

| Solution | Monthly Cost | Setup Difficulty | Maintenance | Account Risk |
|----------|--------------|------------------|-------------|--------------|
| Official X API | $100+ | Easy | Low | None |
| RSS.app Basic | $8.32 | Very Easy | None | Low |
| Self-hosted Nitter | $5-10 (VPS) | Medium | Medium | High |
| twscrape | $0-5 (VPS optional) | Medium | Medium | High |
| Follow Builders | $0 (consumption) | Easy | None | None |
| IFTTT | $0-? | Easy | Low | Low |
| twitter_openapi_python | $0 | Medium | Medium | High |

**Account Risk Explanation:**
- High: Twitter may suspend accounts for scraping
- Low: Using official integrations or public data
- None: No direct Twitter account usage

---

## Conclusion

**For AI News Radar project:**

1. **Keep current Follow Builders consumption** - best balance of reliability and simplicity
2. **Consider RSS.app Basic ($8.32/month)** for additional curated accounts if budget allows
3. **Self-host Nitter or twscrape** only if maintainer accepts account risk and technical burden
4. **Do not use** official X API, broken scrapers, or public Nitter instances

**General recommendation for Twitter RSS in 2025-2026:**
- If budget exists: RSS.app or similar paid service
- If technical: Self-hosted Nitter with burner accounts
- If risk-tolerant: twscrape with multiple accounts
- If community-scale: Follow Builders pattern (central scraper, public feeds)

The Twitter/X RSS landscape is hostile to free/unofficial solutions. Budget $10-100/month for reliable service, or accept account suspension risk with self-hosted tools.

---

## References

- Nitter: https://github.com/zedeus/nitter
- twscrape: https://github.com/vladkens/twscrape
- twitter_openapi_python: https://github.com/fa0311/twitter_openapi_python
- ntscraper: https://github.com/bocchilorenzo/ntscraper
- RSS.app: https://rss.app
- IFTTT: https://ifttt.com/twitter
- Follow Builders: https://github.com/zarazhangrui/follow-builders
- Alternative Front-ends: https://github.com/mendel5/alternative-front-ends
- Nitter Instance Status: https://status.d420.de
