#!/usr/bin/env python3
"""
AliExpress Data Analyzer

This script analyzes scraped AliExpress data and generates insights,
statistics, and reports from the collected product information.
"""

import json
import os
import re
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
import statistics


class AliExpressDataAnalyzer:
    """Analyzer for scraped AliExpress product data."""
    
    def __init__(self, data_dir: str):
        """
        Initialize analyzer with data directory.
        
        Args:
            data_dir: Directory containing scraped JSON files
        """
        self.data_dir = data_dir
        self.products = []
        self.analysis_results = {}
    
    def load_scraped_data(self) -> int:
        """
        Load all scraped product data from JSON files.
        
        Returns:
            Number of products loaded
        """
        if not os.path.exists(self.data_dir):
            print(f"Data directory not found: {self.data_dir}")
            return 0
        
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json') and f.startswith('product_')]
        
        print(f"Loading data from {len(json_files)} JSON files...")
        
        for filename in json_files:
            filepath = os.path.join(self.data_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    product_data = json.load(f)
                    self.products.append(product_data)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        
        print(f"Loaded {len(self.products)} products successfully")
        return len(self.products)
    
    def analyze_pricing(self) -> Dict[str, Any]:
        """Analyze pricing data across all products."""
        prices = []
        currencies = Counter()
        discount_data = []
        
        for product in self.products:
            pricing = product.get('pricing', {})
            
            # Extract current price
            current_price = pricing.get('current_price', {})
            if current_price.get('value'):
                try:
                    price_value = float(current_price['value'])
                    prices.append(price_value)
                    currencies[current_price.get('currency', 'Unknown')] += 1
                except (ValueError, TypeError):
                    pass
            
            # Extract discount information
            discount = pricing.get('discount_percentage')
            if discount:
                try:
                    discount_value = float(discount.replace('%', ''))
                    discount_data.append(discount_value)
                except (ValueError, TypeError):
                    pass
        
        analysis = {
            'total_products_with_pricing': len(prices),
            'price_statistics': {},
            'currency_distribution': dict(currencies),
            'discount_statistics': {}
        }
        
        if prices:
            analysis['price_statistics'] = {
                'min_price': min(prices),
                'max_price': max(prices),
                'average_price': statistics.mean(prices),
                'median_price': statistics.median(prices),
                'price_ranges': self._categorize_prices(prices)
            }
        
        if discount_data:
            analysis['discount_statistics'] = {
                'min_discount': min(discount_data),
                'max_discount': max(discount_data),
                'average_discount': statistics.mean(discount_data),
                'products_with_discount': len(discount_data),
                'discount_percentage': len(discount_data) / len(self.products) * 100
            }
        
        return analysis
    
    def analyze_ratings_and_reviews(self) -> Dict[str, Any]:
        """Analyze ratings and review data."""
        ratings = []
        review_counts = []
        sales_counts = []
        
        for product in self.products:
            reviews_data = product.get('reviews_and_ratings', {})
            
            # Extract rating
            if reviews_data.get('average_rating'):
                try:
                    rating = float(reviews_data['average_rating'])
                    ratings.append(rating)
                except (ValueError, TypeError):
                    pass
            
            # Extract review count
            if reviews_data.get('total_reviews'):
                try:
                    review_count = int(reviews_data['total_reviews'])
                    review_counts.append(review_count)
                except (ValueError, TypeError):
                    pass
            
            # Extract sales count
            if reviews_data.get('sales_count'):
                try:
                    sales_text = reviews_data['sales_count']
                    sales_num = self._extract_number_from_text(sales_text)
                    if sales_num:
                        sales_counts.append(sales_num)
                except (ValueError, TypeError):
                    pass
        
        analysis = {
            'rating_statistics': {},
            'review_statistics': {},
            'sales_statistics': {},
            'quality_indicators': {}
        }
        
        if ratings:
            analysis['rating_statistics'] = {
                'total_products_with_ratings': len(ratings),
                'average_rating': statistics.mean(ratings),
                'median_rating': statistics.median(ratings),
                'rating_distribution': self._categorize_ratings(ratings)
            }
        
        if review_counts:
            analysis['review_statistics'] = {
                'total_products_with_reviews': len(review_counts),
                'average_reviews': statistics.mean(review_counts),
                'median_reviews': statistics.median(review_counts),
                'max_reviews': max(review_counts),
                'min_reviews': min(review_counts)
            }
        
        if sales_counts:
            analysis['sales_statistics'] = {
                'total_products_with_sales': len(sales_counts),
                'average_sales': statistics.mean(sales_counts),
                'median_sales': statistics.median(sales_counts),
                'max_sales': max(sales_counts),
                'min_sales': min(sales_counts)
            }
        
        # Quality indicators
        high_rated = len([r for r in ratings if r >= 4.0])
        well_reviewed = len([r for r in review_counts if r >= 100])
        
        analysis['quality_indicators'] = {
            'high_rated_products': high_rated,
            'high_rated_percentage': (high_rated / len(ratings) * 100) if ratings else 0,
            'well_reviewed_products': well_reviewed,
            'well_reviewed_percentage': (well_reviewed / len(review_counts) * 100) if review_counts else 0
        }
        
        return analysis
    
    def analyze_categories_and_products(self) -> Dict[str, Any]:
        """Analyze product categories and types."""
        categories = Counter()
        brands = Counter()
        product_titles = []
        
        for product in self.products:
            basic_info = product.get('basic_info', {})
            
            # Extract category information
            category = basic_info.get('category', 'Unknown')
            categories[category] += 1
            
            # Extract brand information (from title or specifications)
            title = basic_info.get('title', '')
            product_titles.append(title)
            
            # Try to extract brand from specifications
            specs = product.get('specifications', {})
            brand = specs.get('Brand', specs.get('brand', ''))
            if brand and brand != 'Unknown':
                brands[brand] += 1
        
        # Analyze common keywords in titles
        keywords = self._extract_common_keywords(product_titles)
        
        return {
            'category_distribution': dict(categories.most_common(20)),
            'brand_distribution': dict(brands.most_common(20)),
            'common_keywords': keywords,
            'total_categories': len(categories),
            'total_brands': len(brands)
        }
    
    def analyze_seller_data(self) -> Dict[str, Any]:
        """Analyze seller information and performance."""
        seller_ratings = []
        seller_years = []
        seller_followers = []
        top_sellers = Counter()
        
        for product in self.products:
            seller_info = product.get('seller_info', {})
            
            # Extract seller rating
            if seller_info.get('rating'):
                try:
                    rating = float(seller_info['rating'].replace('%', ''))
                    seller_ratings.append(rating)
                except (ValueError, TypeError):
                    pass
            
            # Extract seller years
            if seller_info.get('years_in_business'):
                try:
                    years = int(seller_info['years_in_business'])
                    seller_years.append(years)
                except (ValueError, TypeError):
                    pass
            
            # Extract followers
            if seller_info.get('followers'):
                try:
                    followers = self._extract_number_from_text(seller_info['followers'])
                    if followers:
                        seller_followers.append(followers)
                except (ValueError, TypeError):
                    pass
            
            # Count top sellers
            seller_name = seller_info.get('name', 'Unknown')
            if seller_name != 'Unknown':
                top_sellers[seller_name] += 1
        
        analysis = {
            'seller_rating_statistics': {},
            'seller_experience_statistics': {},
            'seller_popularity_statistics': {},
            'top_sellers': dict(top_sellers.most_common(10))
        }
        
        if seller_ratings:
            analysis['seller_rating_statistics'] = {
                'average_seller_rating': statistics.mean(seller_ratings),
                'median_seller_rating': statistics.median(seller_ratings),
                'high_rated_sellers': len([r for r in seller_ratings if r >= 95.0])
            }
        
        if seller_years:
            analysis['seller_experience_statistics'] = {
                'average_years_in_business': statistics.mean(seller_years),
                'median_years_in_business': statistics.median(seller_years),
                'experienced_sellers': len([y for y in seller_years if y >= 5])
            }
        
        if seller_followers:
            analysis['seller_popularity_statistics'] = {
                'average_followers': statistics.mean(seller_followers),
                'median_followers': statistics.median(seller_followers),
                'popular_sellers': len([f for f in seller_followers if f >= 1000])
            }
        
        return analysis
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analysis report."""
        print("Generating comprehensive analysis report...")
        
        self.analysis_results = {
            'metadata': {
                'analysis_date': datetime.now().isoformat(),
                'total_products_analyzed': len(self.products),
                'data_directory': self.data_dir
            },
            'pricing_analysis': self.analyze_pricing(),
            'ratings_and_reviews_analysis': self.analyze_ratings_and_reviews(),
            'categories_and_products_analysis': self.analyze_categories_and_products(),
            'seller_analysis': self.analyze_seller_data()
        }
        
        return self.analysis_results
    
    def save_report(self, output_file: str = None) -> str:
        """Save the analysis report to a JSON file."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"analysis_report_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis report saved to: {output_file}")
        return output_file
    
    def print_summary(self):
        """Print a summary of the analysis results."""
        if not self.analysis_results:
            print("No analysis results available. Run generate_comprehensive_report() first.")
            return
        
        print("\n" + "=" * 60)
        print("ALIEXPRESS DATA ANALYSIS SUMMARY")
        print("=" * 60)
        
        metadata = self.analysis_results['metadata']
        print(f"Analysis Date: {metadata['analysis_date']}")
        print(f"Total Products: {metadata['total_products_analyzed']}")
        
        # Pricing summary
        pricing = self.analysis_results['pricing_analysis']
        if pricing.get('price_statistics'):
            stats = pricing['price_statistics']
            print(f"\nPRICING:")
            print(f"  Average Price: ${stats['average_price']:.2f}")
            print(f"  Price Range: ${stats['min_price']:.2f} - ${stats['max_price']:.2f}")
            print(f"  Most Common Currency: {max(pricing['currency_distribution'], key=pricing['currency_distribution'].get)}")
        
        # Ratings summary
        ratings = self.analysis_results['ratings_and_reviews_analysis']
        if ratings.get('rating_statistics'):
            stats = ratings['rating_statistics']
            print(f"\nRATINGS & REVIEWS:")
            print(f"  Average Rating: {stats['average_rating']:.2f}/5.0")
            print(f"  High-Rated Products: {ratings['quality_indicators']['high_rated_percentage']:.1f}%")
        
        # Categories summary
        categories = self.analysis_results['categories_and_products_analysis']
        print(f"\nCATEGORIES:")
        print(f"  Total Categories: {categories['total_categories']}")
        print(f"  Total Brands: {categories['total_brands']}")
        top_category = max(categories['category_distribution'], key=categories['category_distribution'].get)
        print(f"  Most Common Category: {top_category}")
        
        print("=" * 60)
    
    def _categorize_prices(self, prices: List[float]) -> Dict[str, int]:
        """Categorize prices into ranges."""
        ranges = {
            '$0-10': 0, '$10-25': 0, '$25-50': 0, 
            '$50-100': 0, '$100-250': 0, '$250+': 0
        }
        
        for price in prices:
            if price < 10:
                ranges['$0-10'] += 1
            elif price < 25:
                ranges['$10-25'] += 1
            elif price < 50:
                ranges['$25-50'] += 1
            elif price < 100:
                ranges['$50-100'] += 1
            elif price < 250:
                ranges['$100-250'] += 1
            else:
                ranges['$250+'] += 1
        
        return ranges
    
    def _categorize_ratings(self, ratings: List[float]) -> Dict[str, int]:
        """Categorize ratings into ranges."""
        ranges = {
            '4.5-5.0': 0, '4.0-4.5': 0, '3.5-4.0': 0, 
            '3.0-3.5': 0, '2.5-3.0': 0, 'Below 2.5': 0
        }
        
        for rating in ratings:
            if rating >= 4.5:
                ranges['4.5-5.0'] += 1
            elif rating >= 4.0:
                ranges['4.0-4.5'] += 1
            elif rating >= 3.5:
                ranges['3.5-4.0'] += 1
            elif rating >= 3.0:
                ranges['3.0-3.5'] += 1
            elif rating >= 2.5:
                ranges['2.5-3.0'] += 1
            else:
                ranges['Below 2.5'] += 1
        
        return ranges
    
    def _extract_number_from_text(self, text: str) -> Optional[int]:
        """Extract number from text (handles K, M suffixes)."""
        if not text:
            return None
        
        # Remove non-alphanumeric except decimal points
        clean_text = re.sub(r'[^\d.KMkm]', '', str(text))
        
        # Handle K and M suffixes
        multiplier = 1
        if clean_text.lower().endswith('k'):
            multiplier = 1000
            clean_text = clean_text[:-1]
        elif clean_text.lower().endswith('m'):
            multiplier = 1000000
            clean_text = clean_text[:-1]
        
        try:
            return int(float(clean_text) * multiplier)
        except ValueError:
            return None
    
    def _extract_common_keywords(self, titles: List[str], top_n: int = 20) -> Dict[str, int]:
        """Extract common keywords from product titles."""
        # Common stop words to exclude
        stop_words = {
            'for', 'and', 'the', 'with', 'to', 'of', 'in', 'on', 'at', 'by', 'is', 'are',
            'new', 'hot', 'free', 'shipping', 'sale', 'best', 'high', 'quality'
        }
        
        all_words = []
        for title in titles:
            if title:
                # Extract words, convert to lowercase, remove special characters
                words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
                all_words.extend([w for w in words if w not in stop_words])
        
        return dict(Counter(all_words).most_common(top_n))


def main():
    """Main function for data analysis."""
    if len(sys.argv) < 2:
        print("Usage: python data_analyzer.py <data_directory> [output_file]")
        return
    
    data_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Initialize analyzer
    analyzer = AliExpressDataAnalyzer(data_dir)
    
    # Load data
    products_loaded = analyzer.load_scraped_data()
    if products_loaded == 0:
        print("No product data found to analyze")
        return
    
    # Generate analysis
    try:
        analyzer.generate_comprehensive_report()
        analyzer.print_summary()
        analyzer.save_report(output_file)
    except Exception as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    main()
