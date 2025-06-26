# AliExpress Scraping Project

A comprehensive Python-based web scraping solution for extracting product information from AliExpress. This project includes tools for both single product scraping and large-scale batch processing, with built-in data analysis capabilities.

## Features

- **Live Web Scraping**: Real-time scraping using Selenium WebDriver
- **Comprehensive Data Extraction**: Extracts all available product information including:
  - Product details (title, description, specifications)
  - Pricing information (current price, discounts, currency)
  - Reviews and ratings
  - Product variations and SKUs
  - Images and media
  - Shipping information
  - Seller details
  - JavaScript embedded data
- **Batch Processing**: Process thousands of URLs with rate limiting and error handling
- **Data Analysis**: Built-in analytics for scraped data with insights and statistics
- **Unified Management**: Central management interface for all operations

## Project Structure

```
├── ali-scrape.py                    # Original HTML dumper script
├── comprehensive_scraper.py         # HTML file parser for offline analysis
├── live_aliexpress_scraper.py      # Live web scraping with Selenium
├── batch_scraper.py                # Batch processing for multiple URLs
├── data_analyzer.py                # Data analysis and reporting tool
├── scraper_manager.py              # Unified management interface
├── requirements.txt                # Python dependencies
├── 9kAliexpresUrls.txt             # Sample URLs for testing
├── aliexpress_full.html            # Sample HTML for analysis
└── README.md                       # This file
```

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment (recommended):**
   ```bash
   python scraper_manager.py setup
   ```

## Usage

### Method 1: Interactive Management Interface

Run the management script for a user-friendly interface:

```bash
python scraper_manager.py
```

This will show an interactive menu where you can:
- Check project status
- Configure settings
- Run single or batch scraping
- Analyze scraped data

### Method 2: Command Line Interface

#### Setup Environment
```bash
python scraper_manager.py setup
```

#### Single Product Scraping
```bash
# Using the live scraper directly
python live_aliexpress_scraper.py "https://www.aliexpress.com/item/1005006722922099.html"

# With options
python live_aliexpress_scraper.py "URL" --headless=false --output=my_product.json

# Using the manager
python scraper_manager.py single "https://www.aliexpress.com/item/1005006722922099.html"
```

#### Batch Scraping
```bash
# Process first 10 URLs from the file
python batch_scraper.py 9kAliexpresUrls.txt --limit=10 --output=scraped_data

# With custom settings
python batch_scraper.py 9kAliexpresUrls.txt --limit=50 --rate-limit=3 --headless=true

# Using the manager
python scraper_manager.py batch 10
```

#### Data Analysis
```bash
# Analyze scraped data
python data_analyzer.py scraped_data

# Using the manager
python scraper_manager.py analyze scraped_data
```

### Method 3: Direct Script Usage

#### Parse Existing HTML Files
```bash
python comprehensive_scraper.py aliexpress_full.html
```

#### Live Scraping Options
```bash
# Basic usage
python live_aliexpress_scraper.py "URL"

# Advanced options
python live_aliexpress_scraper.py "URL" \
    --headless=false \
    --proxy=proxy.example.com:8080 \
    --output=custom_output.json
```

#### Batch Processing Options
```bash
# Basic batch processing
python batch_scraper.py 9kAliexpresUrls.txt --limit=100

# With all options
python batch_scraper.py 9kAliexpresUrls.txt \
    --limit=50 \
    --headless=true \
    --rate-limit=5 \
    --output=my_data_folder \
    --proxy=proxy.example.com:8080
```

## Configuration

The project uses a configuration file (`scraper_config.json`) that gets created automatically. You can modify settings through:

1. **Interactive menu**: `python scraper_manager.py` → Option 3
2. **Command line**: `python scraper_manager.py config`
3. **Direct editing**: Edit `scraper_config.json`

### Configuration Options

```json
{
  "scraping": {
    "headless": true,                # Run browser in headless mode
    "rate_limit": 5.0,              # Delay between requests (seconds)
    "wait_time": 30,                # Max wait time for page elements
    "proxy": null,                  # Proxy server (host:port)
    "user_agent": "..."             # Browser user agent
  },
  "batch": {
    "default_limit": 50,            # Default number of URLs to process
    "output_dir": "scraped_data",   # Output directory
    "retry_failed": true,           # Retry failed URLs
    "max_retries": 3                # Maximum retry attempts
  },
  "analysis": {
    "auto_analyze": true,           # Auto-analyze after batch scraping
    "generate_charts": false,       # Generate visualization charts
    "export_csv": true              # Export results to CSV
  }
}
```

## Output Data Structure

The scrapers extract comprehensive product information organized into these categories:

```json
{
  "url": "Product URL",
  "basic_info": {
    "title": "Product title",
    "description": "Product description",
    "category": "Product category",
    "brand": "Brand name"
  },
  "pricing": {
    "current_price": {"value": 29.99, "currency": "USD"},
    "original_price": {"value": 39.99, "currency": "USD"},
    "discount_percentage": "25%"
  },
  "reviews_and_ratings": {
    "average_rating": 4.5,
    "total_reviews": 1250,
    "rating_breakdown": {...},
    "sales_count": "5000+ sold"
  },
  "product_variations": [...],
  "images": [...],
  "shipping_info": {...},
  "specifications": {...},
  "seller_info": {...},
  "javascript_data": {...},
  "meta_tags": {...}
}
```

## Analysis Reports

The data analyzer generates comprehensive reports including:

- **Pricing Analysis**: Price statistics, currency distribution, discount patterns
- **Quality Metrics**: Rating distributions, review counts, seller ratings
- **Category Analysis**: Product categories, brand distribution, common keywords
- **Seller Analysis**: Seller performance metrics, top sellers

Example analysis output:
```
ALIEXPRESS DATA ANALYSIS SUMMARY
================================================================
Analysis Date: 2024-01-15T14:30:00
Total Products: 100

PRICING:
  Average Price: $25.67
  Price Range: $1.99 - $299.99
  Most Common Currency: USD

RATINGS & REVIEWS:
  Average Rating: 4.2/5.0
  High-Rated Products: 78.5%

CATEGORIES:
  Total Categories: 25
  Total Brands: 45
  Most Common Category: Electronics
```

## Best Practices

1. **Rate Limiting**: Always use appropriate delays between requests (recommended: 3-10 seconds)
2. **Proxy Usage**: Consider using proxies for large-scale scraping
3. **Error Handling**: The tools include built-in retry mechanisms and error handling
4. **Data Storage**: Results are saved in JSON format for easy processing
5. **Legal Compliance**: Ensure your usage complies with AliExpress terms of service

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**: Run `python scraper_manager.py setup` to auto-install
2. **Rate limiting/blocking**: Increase delay times and consider using proxies
3. **Element not found**: Some product pages have different layouts; the scraper handles multiple selectors
4. **Memory issues**: For large batch jobs, process data in smaller chunks

### Browser Requirements

- Chrome or Chromium browser installed
- ChromeDriver (automatically managed by webdriver-manager)
- Internet connection for live scraping

### Dependencies Issues

If you encounter dependency conflicts:
```bash
pip install --upgrade -r requirements.txt
```

Or create a virtual environment:
```bash
python -m venv aliexpress_scraper
source aliexpress_scraper/bin/activate  # On Windows: aliexpress_scraper\Scripts\activate
pip install -r requirements.txt
```

## Legal Notice

This tool is for educational and research purposes. Users are responsible for:
- Complying with AliExpress Terms of Service
- Respecting robots.txt files
- Following applicable laws and regulations
- Not overwhelming servers with excessive requests

## License

This project is provided as-is for educational purposes. Use responsibly and at your own risk.
#   A l i e x p r e s s - s c r a p e r  
 