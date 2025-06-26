#!/usr/bin/env python3
"""
AliExpress Live Scraper with Comprehensive Data Extraction

This script combines live web scraping using Selenium with comprehensive
data extraction from AliExpress product pages. It scrapes the page in real-time
and extracts all available product information.
"""

import time
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# BeautifulSoup for HTML parsing
from bs4 import BeautifulSoup
import html


class AliExpressLiveScraper:
    """
    Live AliExpress scraper that fetches pages in real-time and extracts
    comprehensive product information.
    """
    
    def __init__(self, headless: bool = True, proxy: str = None):
        """
        Initialize the scraper with browser options.
        
        Args:
            headless: Whether to run browser in headless mode
            proxy: Optional proxy server (format: "host:port")
        """
        self.headless = headless
        self.proxy = proxy
        self.driver = None
        self.product_data = {}
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options."""
        opts = Options()
        
        if self.headless:
            opts.add_argument("--headless=new")  # Chrome 109+ headless mode
        
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option('useAutomationExtension', False)
        
        # Add user agent to avoid detection
        opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        if self.proxy:
            opts.add_argument(f"--proxy-server=http://{self.proxy}")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=opts)
            
            # Execute script to avoid detection
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            print(f"Error setting up driver: {e}")
            raise
    
    def scrape_product(self, url: str, wait_time: int = 30) -> Dict[str, Any]:
        """
        Scrape a product page and extract comprehensive data.
        
        Args:
            url: AliExpress product URL
            wait_time: Maximum time to wait for page elements
            
        Returns:
            Dictionary containing all scraped product data
        """
        if not self.driver:
            raise Exception("Driver not initialized")
        
        print(f"Scraping product from: {url}")
        
        try:
            # Navigate to the page
            self.driver.get(url)
            
            # Wait for key elements to load
            print("Waiting for page elements to load...")
            WebDriverWait(self.driver, wait_time).until(
                EC.any_of(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "span.product-price-value")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-pl='product-title']")),
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".price--currentPriceText--V8_y_b5"))
                )
            )
            
            # Scroll to trigger lazy-loading
            print("Scrolling to load additional content...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # Get page source and parse
            html_content = self.driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract comprehensive data
            print("Extracting product data...")
            self.product_data = self._extract_all_data(soup, url)
            
            print("Scraping completed successfully!")
            return self.product_data
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return {}
    
    def _extract_all_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract all available product data from parsed HTML."""
        return {
            'url': url,
            'basic_info': self._extract_basic_info(soup),
            'pricing': self._extract_pricing(soup),
            'reviews_and_ratings': self._extract_reviews_and_ratings(soup),
            'product_variations': self._extract_product_variations(soup),
            'images': self._extract_images(soup),
            'shipping_info': self._extract_shipping_info(soup),
            'specifications': self._extract_specifications(soup),
            'seller_info': self._extract_seller_info(soup),
            'javascript_data': self._extract_javascript_data(soup),
            'meta_tags': self._extract_meta_tags(soup),
            'scraping_timestamp': datetime.now().isoformat(),
            'page_language': self._detect_page_language(soup)
        }
    
    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract basic product information."""
        basic_info = {}
        
        try:
            # Product title
            title_selectors = [
                'h1[data-pl="product-title"]',
                '.title--wrap--UUHae_g h1',
                '.product-title',
                'h1'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    basic_info['title'] = title_elem.get_text(strip=True)
                    break
            
            # Product ID
            product_id = self._extract_product_id(soup)
            if product_id:
                basic_info['product_id'] = product_id
            
            # Category
            basic_info['category'] = self._extract_category(soup)
            
            # Brand information
            brand = self._extract_brand(soup)
            if brand:
                basic_info['brand'] = brand
                
        except Exception as e:
            print(f"Error extracting basic info: {e}")
            
        return basic_info
    
    def _extract_pricing(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract pricing information."""
        pricing = {}
        
        try:
            # Current price selectors
            price_selectors = [
                'span.product-price-value',
                '.price--currentPriceText--V8_y_b5',
                '.pdp-comp-price-current',
                '[data-pl="product-price"] .price--current--I3Zeidd span'
            ]
            
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    pricing['current_price'] = price_elem.get_text(strip=True)
                    break
            
            # Original price (if discounted)
            original_price_selectors = [
                '.price--originalPrice',
                '.product-price-original',
                '.price--lineThrough'
            ]
            
            for selector in original_price_selectors:
                elem = soup.select_one(selector)
                if elem:
                    pricing['original_price'] = elem.get_text(strip=True)
                    break
            
            # Bulk pricing
            bulk_price_elem = soup.find(string=re.compile(r'za szt|per piece|pieces?'))
            if bulk_price_elem:
                parent = bulk_price_elem.parent
                if parent:
                    pricing['bulk_price'] = parent.get_text(strip=True)
            
            # Discount percentage
            discount_elem = soup.select_one('.discount-percent, .sale-percent')
            if discount_elem:
                pricing['discount'] = discount_elem.get_text(strip=True)
            
            # Currency
            if pricing.get('current_price'):
                currency_match = re.search(r'^([A-Z]{3}|[€$£¥₹₽])', pricing['current_price'])
                if currency_match:
                    pricing['currency'] = currency_match.group(1)
            
            # Tax information
            tax_elem = soup.find(string=re.compile(r'bez podatku|tax|VAT', re.I))
            if tax_elem:
                pricing['tax_info'] = tax_elem.strip()
                
        except Exception as e:
            print(f"Error extracting pricing: {e}")
            
        return pricing
    
    def _extract_reviews_and_ratings(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract review and rating information."""
        reviews = {}
        
        try:
            # Rating
            rating_elem = soup.find('strong', string=re.compile(r'\d+\.\d+'))
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                match = re.search(r'(\d+\.\d+)', rating_text)
                if match:
                    reviews['rating'] = float(match.group(1))
            
            # Review count
            review_selectors = [
                'a[href*="review"]',
                '.reviewer--reviews--cx7Zs_V',
                '.review-count'
            ]
            
            for selector in review_selectors:
                elem = soup.select_one(selector)
                if elem and re.search(r'\d+', elem.get_text()):
                    match = re.search(r'(\d+)', elem.get_text())
                    if match:
                        reviews['review_count'] = int(match.group(1))
                        break
            
            # Sales count
            sold_selectors = [
                '.reviewer--sold--ytPeoEy',
                '.product-sold-count',
                '[class*="sold"]'
            ]
            
            for selector in sold_selectors:
                elem = soup.select_one(selector)
                if elem and 'sold' in elem.get_text().lower():
                    match = re.search(r'(\d+)', elem.get_text())
                    if match:
                        reviews['sold_count'] = int(match.group(1))
                        break
            
            # Individual reviews
            review_items = soup.select('.list--itemDesc--JcxNPy5, .review-item, .feedback-item')
            individual_reviews = []
            
            for review in review_items[:10]:  # Limit to 10 reviews
                review_data = self._parse_individual_review(review)
                if review_data:
                    individual_reviews.append(review_data)
            
            if individual_reviews:
                reviews['individual_reviews'] = individual_reviews
                
        except Exception as e:
            print(f"Error extracting reviews: {e}")
            
        return reviews
    
    def _extract_product_variations(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product variations and SKU information."""
        variations = {}
        
        try:
            # SKU wrapper
            sku_wrapper = soup.select_one('.sku--wrap--xgoW06M, .product-sku, .sku-wrap')
            if sku_wrapper:
                sku_items = sku_wrapper.select('.sku-item--wrap--t9Qszzx, .sku-item')
                
                for sku_item in sku_items:
                    variation_data = self._parse_variation_item(sku_item)
                    if variation_data:
                        variations.update(variation_data)
            
            # Current selection
            current_selection = soup.select_one('.sku--menuTitle--UIEMJcG, .current-sku')
            if current_selection:
                variations['current_selection'] = current_selection.get_text(strip=True)
            
            # Available quantities
            quantity_elem = soup.select_one('.quantity-selector, input[name*="quantity"]')
            if quantity_elem:
                if quantity_elem.name == 'input':
                    max_qty = quantity_elem.get('max')
                    if max_qty:
                        variations['max_quantity'] = int(max_qty)
                        
        except Exception as e:
            print(f"Error extracting variations: {e}")
            
        return variations
    
    def _extract_images(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product images."""
        images = {}
        
        try:
            # Main image
            main_img_selectors = [
                '.magnifier--image--EYYoSlr',
                '.product-main-image img',
                '.main-image img'
            ]
            
            for selector in main_img_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    images['main_image'] = img.get('src')
                    break
            
            # Gallery images from JavaScript
            scripts = soup.find_all('script', string=re.compile(r'imagePathList|gallery'))
            for script in scripts:
                content = script.get_text()
                
                # Extract image arrays
                image_patterns = [
                    r'"imagePathList":\s*(\[.*?\])',
                    r'"summImagePathList":\s*(\[.*?\])',
                    r'"images?":\s*(\[.*?\])'
                ]
                
                for pattern in image_patterns:
                    match = re.search(pattern, content)
                    if match:
                        try:
                            image_list = json.loads(match.group(1))
                            if 'imagePathList' in pattern:
                                images['gallery_images'] = image_list
                            elif 'summImagePathList' in pattern:
                                images['thumbnail_images'] = image_list
                        except:
                            continue
            
            # Fallback: extract images from img tags
            if not images.get('gallery_images'):
                img_tags = soup.select('.image-gallery img, .product-images img')
                gallery_imgs = []
                for img in img_tags:
                    src = img.get('src') or img.get('data-src')
                    if src and src not in gallery_imgs:
                        gallery_imgs.append(src)
                
                if gallery_imgs:
                    images['gallery_images'] = gallery_imgs
            
            # Extract video if present
            video_elem = soup.select_one('video source, .product-video')
            if video_elem:
                video_src = video_elem.get('src') or video_elem.get('data-src')
                if video_src:
                    images['product_video'] = video_src
                    
        except Exception as e:
            print(f"Error extracting images: {e}")
            
        return images
    
    def _extract_shipping_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract shipping and delivery information."""
        shipping = {}
        
        try:
            # Free shipping threshold
            free_shipping = soup.find(string=re.compile(r'Free shipping|Darmowa dostawa|免费', re.I))
            if free_shipping:
                parent = free_shipping.parent
                if parent:
                    shipping['free_shipping_info'] = parent.get_text(strip=True)
            
            # Delivery time
            delivery_patterns = [
                r'\b\w{3}\s+\d+\s*-\s*\w{3}\s+\d+\b',  # Jul 18 - Aug 04
                r'\d+\s*-\s*\d+\s*days?',  # 7-15 days
                r'\d+\s*dni\b'  # Polish: X dni
            ]
            
            for pattern in delivery_patterns:
                delivery_elem = soup.find(string=re.compile(pattern))
                if delivery_elem:
                    shipping['delivery_time'] = delivery_elem.strip()
                    break
            
            # Delivery location
            delivery_to = soup.select_one('.delivery-v2--to--Mtweg7y, .delivery-location')
            if delivery_to:
                shipping['delivery_to'] = delivery_to.get_text(strip=True)
            
            # Shipping cost
            shipping_cost = soup.select_one('.shipping-cost, .delivery-cost')
            if shipping_cost:
                shipping['shipping_cost'] = shipping_cost.get_text(strip=True)
            
            # Shipping methods
            shipping_methods = soup.select('.shipping-method, .delivery-option')
            if shipping_methods:
                methods = []
                for method in shipping_methods:
                    method_text = method.get_text(strip=True)
                    if method_text:
                        methods.append(method_text)
                shipping['shipping_methods'] = methods
                
        except Exception as e:
            print(f"Error extracting shipping info: {e}")
            
        return shipping
    
    def _extract_specifications(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract product specifications."""
        specs = {}
        
        try:
            # Look for specification tables
            spec_tables = soup.select('.product-specs table, .specifications table, .product-props table')
            
            for table in spec_tables:
                rows = table.select('tr')
                for row in rows:
                    cells = row.select('td, th')
                    if len(cells) >= 2:
                        key = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)
                        if key and value:
                            specs[key] = value
            
            # Look for key-value pairs in description
            desc_section = soup.select_one('.product-description, .item-description')
            if desc_section:
                # Extract specification-like patterns
                text = desc_section.get_text()
                spec_patterns = [
                    r'([A-Za-z\s]+):\s*([^\n\r]+)',
                    r'([A-Za-z\s]+)\s*-\s*([^\n\r]+)'
                ]
                
                for pattern in spec_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches[:10]:  # Limit to avoid noise
                        key, value = match
                        key = key.strip()
                        value = value.strip()
                        if len(key) < 50 and len(value) < 200:  # Reasonable limits
                            specs[key] = value
                            
        except Exception as e:
            print(f"Error extracting specifications: {e}")
            
        return specs
    
    def _extract_seller_info(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract seller/store information."""
        seller = {}
        
        try:
            # Store name and link
            store_link = soup.select_one('a[href*="/store/"], .store-link, .seller-link')
            if store_link:
                seller['store_url'] = store_link.get('href', '')
                
                store_name = store_link.select_one('.store-name, .seller-name')
                if store_name:
                    seller['store_name'] = store_name.get_text(strip=True)
                elif store_link.get_text():
                    seller['store_name'] = store_link.get_text(strip=True)
            
            # Store rating
            store_rating = soup.select_one('.store-rating, .seller-rating')
            if store_rating:
                rating_match = re.search(r'(\d+(?:\.\d+)?)', store_rating.get_text())
                if rating_match:
                    seller['store_rating'] = float(rating_match.group(1))
            
            # Store followers
            followers = soup.select_one('.store-followers, .follower-count')
            if followers:
                follower_match = re.search(r'(\d+)', followers.get_text())
                if follower_match:
                    seller['followers'] = int(follower_match.group(1))
            
            # Years in business
            years = soup.select_one('.store-years, .years-in-business')
            if years:
                year_match = re.search(r'(\d+)', years.get_text())
                if year_match:
                    seller['years_in_business'] = int(year_match.group(1))
                    
        except Exception as e:
            print(f"Error extracting seller info: {e}")
            
        return seller
    
    def _extract_javascript_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract data from JavaScript variables."""
        js_data = {}
        
        try:
            scripts = soup.find_all('script')
            
            for script in scripts:
                content = script.get_text()
                
                # Extract various JS data objects
                js_patterns = {
                    'runParams': r'window\.runParams\s*=\s*({.*?});',
                    'DCData': r'window\._d_c_\.DCData\s*=\s*({.*?});',
                    'productData': r'window\.productData\s*=\s*({.*?});',
                    'pageData': r'window\.pageData\s*=\s*({.*?});'
                }
                
                for key, pattern in js_patterns.items():
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        try:
                            js_data[key] = json.loads(match.group(1))
                        except:
                            # If JSON parsing fails, store as string
                            js_data[key] = match.group(1)
                            
        except Exception as e:
            print(f"Error extracting JavaScript data: {e}")
            
        return js_data
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract meta tag information."""
        meta_data = {}
        
        try:
            # OpenGraph tags
            og_tags = soup.select('meta[property^="og:"]')
            for tag in og_tags:
                prop = tag.get('property', '').replace('og:', '')
                content = tag.get('content', '')
                if prop and content:
                    meta_data[f'og_{prop}'] = content
            
            # App links
            app_tags = soup.select('meta[property^="al:"]')
            app_links = {}
            for tag in app_tags:
                prop = tag.get('property', '')
                content = tag.get('content', '')
                if prop and content:
                    app_links[prop] = content
            
            if app_links:
                meta_data['app_links'] = app_links
            
            # Other important meta tags
            important_meta = ['description', 'keywords', 'author']
            for meta_name in important_meta:
                meta_tag = soup.select_one(f'meta[name="{meta_name}"]')
                if meta_tag:
                    meta_data[meta_name] = meta_tag.get('content', '')
                    
        except Exception as e:
            print(f"Error extracting meta tags: {e}")
            
        return meta_data
    
    def _extract_product_id(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract product ID from various sources."""
        try:
            # From URL in meta tags
            og_url = soup.select_one('meta[property="og:url"]')
            if og_url:
                url = og_url.get('content', '')
                match = re.search(r'/item/(\d+)\.html', url)
                if match:
                    return match.group(1)
            
            # From current URL (if available)
            if self.driver:
                current_url = self.driver.current_url
                match = re.search(r'/item/(\d+)\.html', current_url)
                if match:
                    return match.group(1)
            
            # From JavaScript data
            scripts = soup.find_all('script')
            for script in scripts:
                content = script.get_text()
                match = re.search(r'productId["\']?\s*:\s*["\']?(\d+)', content)
                if match:
                    return match.group(1)
                    
        except Exception as e:
            print(f"Error extracting product ID: {e}")
            
        return None
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract product category."""
        try:
            # From breadcrumbs
            breadcrumbs = soup.select('.breadcrumb a, .nav-breadcrumb a')
            if breadcrumbs and len(breadcrumbs) > 1:
                # Return the last meaningful breadcrumb (excluding Home)
                for crumb in reversed(breadcrumbs):
                    text = crumb.get_text(strip=True)
                    if text.lower() not in ['home', 'accueil', 'startseite']:
                        return text
            
            # From meta category
            meta_category = soup.select_one('meta[name="category"]')
            if meta_category:
                return meta_category.get('content', '')
            
            return "Unknown"
            
        except:
            return "Unknown"
    
    def _extract_brand(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract brand information."""
        try:
            # Look for brand in various places
            brand_selectors = [
                '.product-brand',
                '.brand-name',
                '[data-brand]',
                '.manufacturer'
            ]
            
            for selector in brand_selectors:
                elem = soup.select_one(selector)
                if elem:
                    brand = elem.get_text(strip=True) or elem.get('data-brand', '')
                    if brand:
                        return brand
                        
        except:
            pass
            
        return None
    
    def _detect_page_language(self, soup: BeautifulSoup) -> str:
        """Detect the language of the page."""
        try:
            # From html lang attribute
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang'):
                return html_tag.get('lang')
            
            # From meta tag
            lang_meta = soup.select_one('meta[name="language"]')
            if lang_meta:
                return lang_meta.get('content', '')
            
            # Detect from content
            text_sample = soup.get_text()[:1000]
            if re.search(r'[ąćęłńóśźż]', text_sample):
                return 'pl'
            elif re.search(r'[àáâãäåæçèéêëìíîïñòóôõöøùúûüý]', text_sample):
                return 'fr'
            elif re.search(r'[äöüß]', text_sample):
                return 'de'
                
        except:
            pass
            
        return 'en'
    
    def _parse_individual_review(self, review_elem) -> Dict[str, Any]:
        """Parse an individual review element."""
        review_data = {}
        
        try:
            # Reviewer info
            reviewer_info = review_elem.select_one('.reviewer-info, .review-author')
            if reviewer_info:
                review_data['reviewer_info'] = reviewer_info.get_text(strip=True)
            
            # Review text
            review_text = review_elem.select_one('.review-text, .review-content, .list--itemReview--d9Z9Z5Z')
            if review_text:
                review_data['review_text'] = review_text.get_text(strip=True)
            
            # Rating (if present)
            rating_elem = review_elem.select_one('.rating, .stars')
            if rating_elem:
                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_elem.get('class', '')[0] if rating_elem.get('class') else '')
                if rating_match:
                    review_data['rating'] = float(rating_match.group(1))
            
            # SKU/variant info
            sku_elem = review_elem.select_one('.sku-info, .variant-info, .list--itemSku--idEQSGC')
            if sku_elem:
                review_data['sku'] = sku_elem.get_text(strip=True)
            
            # Review images
            review_images = review_elem.select('.review-image img')
            if review_images:
                image_urls = []
                for img in review_images:
                    src = img.get('src') or img.get('data-src')
                    if src:
                        image_urls.append(src)
                if image_urls:
                    review_data['images'] = image_urls
                    
        except Exception as e:
            print(f"Error parsing review: {e}")
            
        return review_data
    
    def _parse_variation_item(self, sku_item) -> Dict[str, Any]:
        """Parse a product variation item."""
        variation_data = {}
        
        try:
            # Variation name
            title_elem = sku_item.select_one('.sku-item--title--Z0HLO87, .variation-title')
            if title_elem:
                variation_name = title_elem.get_text(strip=True).replace(':', '').strip()
                
                # Options
                options = []
                option_elems = sku_item.select('[data-sku-col], .variation-option')
                
                for option in option_elems:
                    option_data = {}
                    
                    # Option image
                    img = option.select_one('img')
                    if img:
                        option_data['image'] = img.get('src', '')
                        option_data['alt_text'] = img.get('alt', '')
                    
                    # Option text
                    option_text = option.get_text(strip=True)
                    if option_text:
                        option_data['text'] = option_text
                    
                    # Status
                    classes = option.get('class', [])
                    if any('selected' in cls for cls in classes):
                        option_data['selected'] = True
                    if any('soldOut' in cls or 'sold-out' in cls for cls in classes):
                        option_data['sold_out'] = True
                    
                    if option_data:
                        options.append(option_data)
                
                if options:
                    variation_data[variation_name] = options
                    
        except Exception as e:
            print(f"Error parsing variation: {e}")
            
        return variation_data
    
    def save_to_json(self, filename: str = None) -> bool:
        """Save scraped data to JSON file."""
        if not self.product_data:
            print("No data to save")
            return False
        
        if not filename:
            product_id = self.product_data.get('basic_info', {}).get('product_id', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"aliexpress_product_{product_id}_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.product_data, f, indent=2, ensure_ascii=False)
            print(f"Data saved to: {filename}")
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def print_summary(self):
        """Print a summary of scraped data."""
        if not self.product_data:
            print("No data available")
            return
        
        print("\n" + "="*80)
        print("ALIEXPRESS LIVE SCRAPING SUMMARY")
        print("="*80)
        
        basic = self.product_data.get('basic_info', {})
        pricing = self.product_data.get('pricing', {})
        reviews = self.product_data.get('reviews_and_ratings', {})
        images = self.product_data.get('images', {})
        shipping = self.product_data.get('shipping_info', {})
        
        print(f"URL: {self.product_data.get('url', 'N/A')}")
        print(f"Product ID: {basic.get('product_id', 'N/A')}")
        print(f"Title: {basic.get('title', 'N/A')[:100]}...")
        print(f"Category: {basic.get('category', 'N/A')}")
        print(f"Brand: {basic.get('brand', 'N/A')}")
        
        print(f"\nPricing:")
        print(f"  Current Price: {pricing.get('current_price', 'N/A')}")
        print(f"  Original Price: {pricing.get('original_price', 'N/A')}")
        print(f"  Currency: {pricing.get('currency', 'N/A')}")
        
        print(f"\nReviews & Ratings:")
        print(f"  Rating: {reviews.get('rating', 'N/A')}")
        print(f"  Review Count: {reviews.get('review_count', 'N/A')}")
        print(f"  Items Sold: {reviews.get('sold_count', 'N/A')}")
        
        print(f"\nImages:")
        gallery_count = len(images.get('gallery_images', []))
        thumb_count = len(images.get('thumbnail_images', []))
        print(f"  Gallery Images: {gallery_count}")
        print(f"  Thumbnail Images: {thumb_count}")
        print(f"  Has Video: {'Yes' if images.get('product_video') else 'No'}")
        
        print(f"\nShipping:")
        print(f"  Delivery Time: {shipping.get('delivery_time', 'N/A')}")
        print(f"  Delivery To: {shipping.get('delivery_to', 'N/A')}")
        print(f"  Free Shipping: {shipping.get('free_shipping_info', 'N/A')}")
        
        variations = self.product_data.get('product_variations', {})
        if variations:
            print(f"\nVariations: {len([k for k in variations.keys() if k != 'current_selection'])} types")
        
        specs = self.product_data.get('specifications', {})
        if specs:
            print(f"Specifications: {len(specs)} items")
        
        print("="*80)
    
    def close(self):
        """Close the browser driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None


def main():
    """Main function to demonstrate the live scraper."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python live_aliexpress_scraper.py <aliexpress_url> [options]")
        print("\nOptions:")
        print("  --headless=false    Run browser in visible mode")
        print("  --proxy=host:port   Use proxy server")
        print("  --output=filename   Custom output filename")
        print("\nExample:")
        print("  python live_aliexpress_scraper.py https://www.aliexpress.com/item/1005006722922099.html")
        return
    
    url = sys.argv[1]
    headless = True
    proxy = None
    output_file = None
    
    # Parse options
    for arg in sys.argv[2:]:
        if arg.startswith('--headless='):
            headless = arg.split('=')[1].lower() == 'true'
        elif arg.startswith('--proxy='):
            proxy = arg.split('=')[1]
        elif arg.startswith('--output='):
            output_file = arg.split('=')[1]
    
    # Validate URL
    if 'aliexpress.com' not in url and 'aliexpress.' not in url:
        print("Error: Please provide a valid AliExpress URL")
        return
    
    scraper = None
    try:
        print(f"Initializing scraper (headless={headless})...")
        scraper = AliExpressLiveScraper(headless=headless, proxy=proxy)
        
        print("Starting live scraping...")
        data = scraper.scrape_product(url)
        
        if data:
            scraper.print_summary()
            scraper.save_to_json(output_file)
        else:
            print("Failed to scrape product data")
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if scraper:
            scraper.close()


if __name__ == "__main__":
    main()
