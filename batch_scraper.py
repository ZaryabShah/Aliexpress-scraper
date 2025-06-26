#!/usr/bin/env python3
"""
AliExpress Batch Scraper

This script processes multiple AliExpress URLs from the 9kAliexpresUrls.txt file
and scrapes them in batches with proper rate limiting and error handling.
"""

import json
import time
import random
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from live_aliexpress_scraper import AliExpressLiveScraper


class BatchScraper:
    """Batch scraper for processing multiple AliExpress URLs."""
    
    def __init__(self, headless: bool = True, proxy: str = None, rate_limit: float = 5.0):
        """
        Initialize batch scraper.
        
        Args:
            headless: Whether to run browser in headless mode
            proxy: Optional proxy server
            rate_limit: Minimum delay between requests (seconds)
        """
        self.headless = headless
        self.proxy = proxy
        self.rate_limit = rate_limit
        self.scraper = None
        self.results = []
        self.failed_urls = []
        
    def load_urls_from_file(self, file_path: str, limit: int = None) -> List[str]:
        """
        Load URLs from the JSON file.
        
        Args:
            file_path: Path to the URLs file
            limit: Maximum number of URLs to process (None for all)
            
        Returns:
            List of URLs to scrape
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            urls = [item['url'] for item in data if 'url' in item]
            
            if limit:
                urls = urls[:limit]
                
            print(f"Loaded {len(urls)} URLs from {file_path}")
            return urls
            
        except Exception as e:
            print(f"Error loading URLs from file: {e}")
            return []
    
    def scrape_batch(self, urls: List[str], output_dir: str = "scraped_data") -> Dict[str, Any]:
        """
        Scrape a batch of URLs with rate limiting and error handling.
        
        Args:
            urls: List of URLs to scrape
            output_dir: Directory to save results
            
        Returns:
            Summary of scraping results
        """
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize scraper
        print("Initializing scraper...")
        self.scraper = AliExpressLiveScraper(headless=self.headless, proxy=self.proxy)
        
        total_urls = len(urls)
        successful = 0
        failed = 0
        start_time = datetime.now()
        
        print(f"Starting batch scraping of {total_urls} URLs...")
        print(f"Rate limit: {self.rate_limit} seconds between requests")
        print("-" * 60)
        
        try:
            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{total_urls}] Processing: {url}")
                
                try:
                    # Add random delay to avoid detection
                    delay = self.rate_limit + random.uniform(0, 2)
                    if i > 1:  # Don't delay on first request
                        print(f"Waiting {delay:.1f} seconds...")
                        time.sleep(delay)
                    
                    # Scrape the product
                    product_data = self.scraper.scrape_product(url, wait_time=20)
                    
                    if product_data and 'basic_info' in product_data:
                        # Save individual result
                        filename = f"product_{i:04d}_{int(time.time())}.json"
                        filepath = os.path.join(output_dir, filename)
                        
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(product_data, f, indent=2, ensure_ascii=False)
                        
                        self.results.append({
                            'url': url,
                            'status': 'success',
                            'filename': filename,
                            'scraped_at': datetime.now().isoformat()
                        })
                        
                        successful += 1
                        print(f"✓ Success - Data saved to {filename}")
                        
                    else:
                        raise Exception("No product data extracted")
                        
                except Exception as e:
                    print(f"✗ Failed: {e}")
                    self.failed_urls.append({'url': url, 'error': str(e)})
                    failed += 1
                
                # Progress update
                elapsed = datetime.now() - start_time
                avg_time = elapsed.total_seconds() / i
                remaining = (total_urls - i) * avg_time
                
                print(f"Progress: {i}/{total_urls} ({i/total_urls*100:.1f}%) | "
                      f"Success: {successful} | Failed: {failed} | "
                      f"ETA: {remaining/60:.1f} min")
        
        finally:
            if self.scraper:
                self.scraper.close()
        
        # Generate summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        summary = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_urls': total_urls,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_urls * 100) if total_urls > 0 else 0,
            'results': self.results,
            'failed_urls': self.failed_urls
        }
        
        # Save summary
        summary_path = os.path.join(output_dir, f"batch_summary_{int(time.time())}.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n" + "=" * 60)
        print(f"BATCH SCRAPING COMPLETE")
        print(f"Duration: {duration}")
        print(f"Success rate: {summary['success_rate']:.1f}%")
        print(f"Successful: {successful}/{total_urls}")
        print(f"Failed: {failed}/{total_urls}")
        print(f"Summary saved to: {summary_path}")
        print("=" * 60)
        
        return summary


def main():
    """Main function for batch scraping."""
    if len(sys.argv) < 2:
        print("Usage: python batch_scraper.py <urls_file> [options]")
        print("Options:")
        print("  --limit=N          Process only first N URLs")
        print("  --headless=false   Run browser in non-headless mode")
        print("  --proxy=host:port  Use proxy server")
        print("  --rate-limit=N     Delay between requests (seconds, default: 5)")
        print("  --output=dir       Output directory (default: scraped_data)")
        return
    
    urls_file = sys.argv[1]
    limit = None
    headless = True
    proxy = None
    rate_limit = 5.0
    output_dir = "scraped_data"
    
    # Parse options
    for arg in sys.argv[2:]:
        if arg.startswith('--limit='):
            limit = int(arg.split('=')[1])
        elif arg.startswith('--headless='):
            headless = arg.split('=')[1].lower() == 'true'
        elif arg.startswith('--proxy='):
            proxy = arg.split('=')[1]
        elif arg.startswith('--rate-limit='):
            rate_limit = float(arg.split('=')[1])
        elif arg.startswith('--output='):
            output_dir = arg.split('=')[1]
    
    # Initialize batch scraper
    batch_scraper = BatchScraper(
        headless=headless, 
        proxy=proxy, 
        rate_limit=rate_limit
    )
    
    # Load URLs
    urls = batch_scraper.load_urls_from_file(urls_file, limit=limit)
    
    if not urls:
        print("No URLs to process")
        return
    
    # Start batch scraping
    try:
        summary = batch_scraper.scrape_batch(urls, output_dir)
    except KeyboardInterrupt:
        print("\nBatch scraping interrupted by user")
    except Exception as e:
        print(f"Error during batch scraping: {e}")


if __name__ == "__main__":
    main()
