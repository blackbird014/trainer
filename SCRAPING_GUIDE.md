# Web Scraping with Cursor Browser Automation

## Overview

Instead of writing Python scripts with Selenium/Playwright, you can use Cursor's built-in browser automation tools directly! Just ask me to scrape websites and I'll use the MCP browser tools.

## How to Use

### Method 1: Direct Commands (Easiest)
Just tell me what you want to scrape:
- "Scrape the headlines from news.ycombinator.com"
- "Get all product prices from [website]"
- "Extract all links from [URL]"

### Method 2: Step-by-Step Control
You can guide me through the process:
- "Navigate to [URL]"
- "Take a snapshot"
- "Click the button with text 'Load More'"
- "Extract all the data"

## Common Scraping Patterns

### 1. Simple Text Extraction
**What you say:** "Get all headings from example.com"

**What I do:**
- Navigate to the page
- Use JavaScript evaluation to extract headings
- Return structured data

### 2. Form Interaction
**What you say:** "Fill out the search form on [site] with 'query'"

**What I do:**
- Navigate to page
- Take snapshot to find form fields
- Fill form using `browser_fill_form`
- Submit and extract results

### 3. Clicking and Navigating
**What you say:** "Click the 'Next' button and scrape the results"

**What I do:**
- Take snapshot to find button
- Click using `browser_click`
- Wait for page to load
- Extract new data

### 4. Screenshot Documentation
**What you say:** "Take a screenshot of [page]"

**What I do:**
- Navigate to page
- Take screenshot using `browser_take_screenshot`
- Save to file

## Example: Scraping Hacker News

Try asking me:
**"Scrape the top 10 headlines from news.ycombinator.com"**

I'll:
1. Navigate to the site
2. Take a snapshot to see the structure
3. Extract headline text and links using JavaScript
4. Return structured data

## Advantages Over Python Scripts

✅ **No code needed** - Just describe what you want  
✅ **Visual feedback** - I can see the page structure  
✅ **Interactive** - Can handle dynamic content, clicks, forms  
✅ **Built-in** - No need to install Selenium/Playwright  
✅ **Smart** - I understand page structure automatically  

## Available Browser Tools

- **Navigation**: Navigate, go back, manage tabs
- **Interaction**: Click, type, hover, drag, select
- **Information**: Snapshots, screenshots, console logs, network requests
- **JavaScript**: Evaluate code on the page
- **Forms**: Fill multiple fields at once
- **Waiting**: Wait for elements or timeouts

## Tips

1. **Be specific**: "Get product names and prices" is better than "scrape this"
2. **Handle dynamic content**: I can wait for elements to load
3. **Multiple pages**: I can navigate through pagination
4. **Screenshots**: Ask for screenshots if you want visual proof

## Ready to Try?

Just ask me to scrape any website! For example:
- "Scrape the current top stories from [news site]"
- "Get all product listings from [e-commerce site]"
- "Extract contact information from [business site]"

