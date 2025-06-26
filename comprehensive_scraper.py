#!/usr/bin/env python3
"""
Comprehensive AliExpress Product Scraper

This script extracts detailed product information from AliExpress HTML files,
including product details, prices, reviews, specifications, images, and more.
"""

import os
import re
import json
import sys
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import html
from typing import Dict, List, Any, Optional


class AliExpressProductScraper:
    """
    A comprehensive scraper for AliExpress product pages.
    Extracts all available product information from HTML content.
    """
    
    def __init__(self, html_file_path: str):
        """Initialize the scraper with an HTML file."""
        self.html_file_path = html_file_path
        self.soup = None
        self.product_data = {}
        
    def load_html(self) -> bool:
        """Load and parse the HTML file."""
        try:
            with open(self.html_file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            self.soup = BeautifulSoup(html_content, 'html.parser')
            return True
        except Exception as e:
            print(f"Error loading HTML file: {e}")
            return False
    
    def extract_basic_info(self) -> Dict[str, Any]:
        """Extract basic product information."""
        basic_info = {}
        
        try:
            # Product title
            title_elem = self.soup.find('h1', {'data-pl': 'product-title'})
            if title_elem:
                basic_info['title'] = title_elem.get_text(strip=True)
            
            # Product ID from URL or meta tags
            og_url = self.soup.find('meta', {'property': 'og:url'})
            if og_url:
                url_content = og_url.get('content', '')
                match = re.search(r'/item/(\d+)\.html', url_content)
                if match:
                    basic_info['product_id'] = match.group(1)
            
            # Category from breadcrumbs or meta
            basic_info['category'] = self.extract_category()
            
            # Store information
            store_info = self.extract_store_info()
            if store_info:
                basic_info['store'] = store_info
                
        except Exception as e:
            print(f"Error extracting basic info: {e}")
            
        return basic_info
    
    def extract_pricing(self) -> Dict[str, Any]:
        """Extract pricing information."""
        pricing = {}
        
        try:
            # Main price
            price_elem = self.soup.find('span', class_='product-price-value')
            if price_elem:
                pricing['current_price'] = price_elem.get_text(strip=True)
            
            # Alternative price selector
            if not pricing.get('current_price'):
                price_elem = self.soup.find('span', {'class': 'price--currentPriceText--V8_y_b5'})
                if price_elem:
                    pricing['current_price'] = price_elem.get_text(strip=True)
            
            # Bulk pricing
            bulk_price = self.soup.find('span', style=lambda x: x and 'color: #D3031C' in x)
            if bulk_price and 'za szt' in bulk_price.get_text():
                pricing['bulk_price'] = bulk_price.get_text(strip=True)
            
            # Original price (if on sale)
            original_price = self.soup.find('span', class_='price--originalPrice')
            if original_price:
                pricing['original_price'] = original_price.get_text(strip=True)
            
            # Tax information
            tax_elem = self.soup.find('span', string=re.compile(r'Cena bez podatku|bez podatku'))
            if tax_elem:
                pricing['tax_info'] = tax_elem.get_text(strip=True)
                
        except Exception as e:
            print(f"Error extracting pricing: {e}")
            
        return pricing
    
    def extract_reviews_and_ratings(self) -> Dict[str, Any]:
        """Extract review and rating information."""
        reviews = {}
        
        try:
            # Rating
            rating_elem = self.soup.find('strong', string=re.compile(r'\d+\.\d+'))
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                match = re.search(r'(\d+\.\d+)', rating_text)
                if match:
                    reviews['rating'] = float(match.group(1))
            
            # Review count
            review_count_elem = self.soup.find('a', class_='reviewer--reviews--cx7Zs_V')
            if review_count_elem:
                review_text = review_count_elem.get_text(strip=True)
                match = re.search(r'(\d+)', review_text)
                if match:
                    reviews['review_count'] = int(match.group(1))
            
            # Sales count
            sold_elem = self.soup.find('span', class_='reviewer--sold--ytPeoEy')
            if sold_elem:
                sold_text = sold_elem.get_text(strip=True)
                match = re.search(r'(\d+)', sold_text)
                if match:
                    reviews['sold_count'] = int(match.group(1))
            
            # Individual reviews
            review_items = self.soup.find_all('div', class_='list--itemDesc--JcxNPy5')
            individual_reviews = []
            
            for review in review_items[:10]:  # Limit to first 10 reviews
                review_data = {}
                
                # Reviewer and date
                info_elem = review.find('span', string=re.compile(r'\w+\s+\|\s+\d+'))
                if info_elem:
                    review_data['reviewer_info'] = info_elem.get_text(strip=True)
                
                # Review text
                review_text_elem = review.find('div', class_='list--itemReview--d9Z9Z5Z')
                if review_text_elem:
                    review_data['review_text'] = review_text_elem.get_text(strip=True)
                
                # SKU information
                sku_elem = review.find('div', class_='list--itemSku--idEQSGC')
                if sku_elem:
                    review_data['sku'] = sku_elem.get_text(strip=True)
                
                if review_data:
                    individual_reviews.append(review_data)
            
            if individual_reviews:
                reviews['individual_reviews'] = individual_reviews
                
        except Exception as e:
            print(f"Error extracting reviews: {e}")
            
        return reviews
    
    def extract_product_variations(self) -> Dict[str, Any]:
        """Extract product variations and SKU information."""
        variations = {}
        
        try:
            # SKU options
            sku_wrapper = self.soup.find('div', class_='sku--wrap--xgoW06M')
            if sku_wrapper:
                sku_items = sku_wrapper.find_all('div', class_='sku-item--wrap--t9Qszzx')
                
                for sku_item in sku_items:
                    # Variation name (e.g., "kolor")
                    title_elem = sku_item.find('div', class_='sku-item--title--Z0HLO87')
                    if title_elem:
                        variation_name = title_elem.get_text(strip=True).replace(':', '')
                        
                        # Variation options
                        options = []
                        option_elems = sku_item.find_all('div', {'data-sku-col': True})
                        
                        for option in option_elems:
                            option_data = {}
                            
                            # Option image
                            img = option.find('img')
                            if img:
                                option_data['image'] = img.get('src', '')
                                option_data['alt_text'] = img.get('alt', '')
                            
                            # Check if option is selected
                            if 'sku-item--selected--ITGY_EO' in option.get('class', []):
                                option_data['selected'] = True
                            
                            # Check if option is sold out
                            if 'sku-item--soldOut--YJfuCGq' in option.get('class', []):
                                option_data['sold_out'] = True
                            
                            if option_data:
                                options.append(option_data)
                        
                        if options:
                            variations[variation_name] = options
            
            # Current selection
            current_selection = self.soup.find('span', class_='sku--menuTitle--UIEMJcG')
            if current_selection:
                variations['current_selection'] = current_selection.get_text(strip=True)
                
        except Exception as e:
            print(f"Error extracting variations: {e}")
            
        return variations
    
    def extract_images(self) -> Dict[str, Any]:
        """Extract product images."""
        images = {}
        
        try:
            # Main product image
            main_img = self.soup.find('img', class_='magnifier--image--EYYoSlr')
            if main_img:
                images['main_image'] = main_img.get('src', '')
            
            # Gallery images from script tags
            script_tags = self.soup.find_all('script', string=re.compile(r'imagePathList'))
            for script in script_tags:
                script_content = script.get_text()
                # Extract imagePathList
                match = re.search(r'"imagePathList":\s*(\[.*?\])', script_content)
                if match:
                    try:
                        image_list = json.loads(match.group(1))
                        images['gallery_images'] = image_list
                    except:
                        pass
                
                # Extract thumbnail images
                match = re.search(r'"summImagePathList":\s*(\[.*?\])', script_content)
                if match:
                    try:
                        thumb_list = json.loads(match.group(1))
                        images['thumbnail_images'] = thumb_list
                    except:
                        pass
            
            # OpenGraph image
            og_image = self.soup.find('meta', {'property': 'og:image'})
            if og_image:
                images['og_image'] = og_image.get('content', '')
                
        except Exception as e:
            print(f"Error extracting images: {e}")
            
        return images
    
    def extract_shipping_info(self) -> Dict[str, Any]:
        """Extract shipping and delivery information."""
        shipping = {}
        
        try:
            # Free shipping threshold
            free_shipping = self.soup.find('strong', string=re.compile(r'Darmowa dostawa.*PKR'))
            if free_shipping:
                shipping['free_shipping_threshold'] = free_shipping.get_text(strip=True)
            
            # Delivery timeframe
            delivery_elem = self.soup.find('strong', string=re.compile(r'\w{3}\s+\d+\s+-\s+\w{3}\s+\d+'))
            if delivery_elem:
                shipping['delivery_time'] = delivery_elem.get_text(strip=True)
            
            # Delivery location
            delivery_to = self.soup.find('span', class_='delivery-v2--to--Mtweg7y')
            if delivery_to:
                shipping['delivery_to'] = delivery_to.get_text(strip=True)
            
            # Shipping policies
            shipping_items = self.soup.find_all('div', class_='shipping--item--F04J6q9')
            policies = []
            
            for item in shipping_items:
                title_elem = item.find('div', class_='shipping--title--sZAnuQw')
                if title_elem:
                    policy_title = title_elem.get_text(strip=True)
                    
                    # Get policy description if available
                    desc_elems = item.find_all('div', class_='shipping--descText--UVpscND')
                    descriptions = [desc.get_text(strip=True) for desc in desc_elems]
                    
                    policies.append({
                        'title': policy_title,
                        'descriptions': descriptions
                    })
            
            if policies:
                shipping['policies'] = policies
                
        except Exception as e:
            print(f"Error extracting shipping info: {e}")
            
        return shipping
    
    def extract_store_info(self) -> Dict[str, Any]:
        """Extract store/seller information."""
        store = {}
        
        try:
            # Store link
            store_link = self.soup.find('a', class_='store-detail--wrap--IhR4e1j')
            if store_link:
                store['store_url'] = store_link.get('href', '')
                
                # Store name
                store_name = store_link.find('span', class_='store-detail--storeName--hpOD8R8')
                if store_name:
                    store['store_name'] = store_name.get_text(strip=True)
            
            # Additional store details can be extracted here
            
        except Exception as e:
            print(f"Error extracting store info: {e}")
            
        return store
    
    def extract_category(self) -> str:
        """Extract product category."""
        try:
            # Try to find category in breadcrumbs or navigation
            # This is a simplified version - actual implementation may vary
            return "Electronics"  # Placeholder
        except:
            return ""
    
    def extract_javascript_data(self) -> Dict[str, Any]:
        """Extract structured data from JavaScript variables."""
        js_data = {}
        
        try:
            # Extract runParams
            script_tags = self.soup.find_all('script', string=re.compile(r'window\.runParams'))
            for script in script_tags:
                script_content = script.get_text()
                match = re.search(r'window\.runParams\s*=\s*({.*?});', script_content, re.DOTALL)
                if match:
                    try:
                        js_data['runParams'] = json.loads(match.group(1))
                    except:
                        pass
            
            # Extract _d_c_ data
            script_tags = self.soup.find_all('script', string=re.compile(r'window\._d_c_'))
            for script in script_tags:
                script_content = script.get_text()
                match = re.search(r'window\._d_c_\.DCData\s*=\s*({.*?});', script_content, re.DOTALL)
                if match:
                    try:
                        js_data['DCData'] = json.loads(match.group(1))
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error extracting JavaScript data: {e}")
            
        return js_data
    
    def extract_meta_tags(self) -> Dict[str, Any]:
        """Extract relevant meta tag information."""
        meta_data = {}
        
        try:
            # OpenGraph tags
            og_tags = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']
            for tag in og_tags:
                elem = self.soup.find('meta', {'property': tag})
                if elem:
                    meta_data[tag.replace(':', '_')] = elem.get('content', '')
            
            # App links
            app_links = self.soup.find_all('meta', {'property': re.compile(r'^al:')})
            if app_links:
                meta_data['app_links'] = {}
                for link in app_links:
                    prop = link.get('property', '')
                    content = link.get('content', '')
                    if prop and content:
                        meta_data['app_links'][prop] = content
                        
        except Exception as e:
            print(f"Error extracting meta tags: {e}")
            
        return meta_data
    
    def scrape_all(self) -> Dict[str, Any]:
        """Perform comprehensive scraping of all product data."""
        if not self.load_html():
            return {}
        
        print("Starting comprehensive product scraping...")
        
        # Extract all information
        self.product_data = {
            'basic_info': self.extract_basic_info(),
            'pricing': self.extract_pricing(),
            'reviews_and_ratings': self.extract_reviews_and_ratings(),
            'product_variations': self.extract_product_variations(),
            'images': self.extract_images(),
            'shipping_info': self.extract_shipping_info(),
            'javascript_data': self.extract_javascript_data(),
            'meta_tags': self.extract_meta_tags(),
            'scraping_timestamp': self.get_timestamp()
        }
        
        print("Scraping completed successfully!")
        return self.product_data
    
    def get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def save_to_json(self, output_file: str = None) -> bool:
        """Save scraped data to JSON file."""
        if not self.product_data:
            print("No data to save. Run scrape_all() first.")
            return False
        
        if not output_file:
            base_name = os.path.splitext(os.path.basename(self.html_file_path))[0]
            output_file = f"{base_name}_scraped_data.json"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.product_data, f, indent=2, ensure_ascii=False)
            print(f"Data saved to: {output_file}")
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False
    
    def print_summary(self):
        """Print a summary of scraped data."""
        if not self.product_data:
            print("No data available. Run scrape_all() first.")
            return
        
        print("\n" + "="*60)
        print("ALIEXPRESS PRODUCT SCRAPING SUMMARY")
        print("="*60)
        
        # Basic info
        basic = self.product_data.get('basic_info', {})
        print(f"Product Title: {basic.get('title', 'N/A')}")
        print(f"Product ID: {basic.get('product_id', 'N/A')}")
        print(f"Category: {basic.get('category', 'N/A')}")
        
        # Pricing
        pricing = self.product_data.get('pricing', {})
        print(f"Current Price: {pricing.get('current_price', 'N/A')}")
        if pricing.get('bulk_price'):
            print(f"Bulk Price: {pricing.get('bulk_price', 'N/A')}")
        
        # Reviews
        reviews = self.product_data.get('reviews_and_ratings', {})
        print(f"Rating: {reviews.get('rating', 'N/A')}")
        print(f"Review Count: {reviews.get('review_count', 'N/A')}")
        print(f"Items Sold: {reviews.get('sold_count', 'N/A')}")
        
        # Variations
        variations = self.product_data.get('product_variations', {})
        if variations.get('current_selection'):
            print(f"Current Selection: {variations.get('current_selection')}")
        
        # Images
        images = self.product_data.get('images', {})
        image_count = len(images.get('gallery_images', [])) + (1 if images.get('main_image') else 0)
        print(f"Images Found: {image_count}")
        
        # Shipping
        shipping = self.product_data.get('shipping_info', {})
        if shipping.get('delivery_time'):
            print(f"Delivery Time: {shipping.get('delivery_time')}")
        if shipping.get('free_shipping_threshold'):
            print(f"Free Shipping: {shipping.get('free_shipping_threshold')}")
        
        print("="*60)


def main():
    """Main function to demonstrate the scraper."""
    # Check if HTML file path is provided
    if len(sys.argv) < 2:
        html_file = "aliexpress_full.html"  # Default file
        if not os.path.exists(html_file):
            print("Please provide the path to the HTML file as an argument.")
            print("Usage: python comprehensive_scraper.py <html_file_path>")
            return
    else:
        html_file = sys.argv[1]
    
    if not os.path.exists(html_file):
        print(f"HTML file not found: {html_file}")
        return
    
    print(f"Scraping AliExpress product data from: {html_file}")
    
    # Initialize scraper
    scraper = AliExpressProductScraper(html_file)
    
    # Perform scraping
    data = scraper.scrape_all()
    
    if data:
        # Print summary
        scraper.print_summary()
        
        # Save to JSON
        scraper.save_to_json()
        
        # Print some detailed information
        print(f"\nDetailed data structure:")
        for key, value in data.items():
            if isinstance(value, dict):
                print(f"- {key}: {len(value)} items")
            elif isinstance(value, list):
                print(f"- {key}: {len(value)} items")
            else:
                print(f"- {key}: {type(value).__name__}")
    else:
        print("Failed to scrape data from the HTML file.")


if __name__ == "__main__":
    main()
