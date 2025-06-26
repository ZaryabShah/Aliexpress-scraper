#!/usr/bin/env python3
"""
AliExpress Scraper Management Script

This script provides a unified interface for managing all aspects of
the AliExpress scraping project, including setup, configuration,
execution, and analysis.
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, Any, List


class ScraperManager:
    """Unified manager for AliExpress scraping operations."""
    
    def __init__(self):
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.project_dir, "scraper_config.json")
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load or create configuration file."""
        default_config = {
            "scraping": {
                "headless": True,
                "rate_limit": 5.0,
                "wait_time": 30,
                "proxy": None,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            "batch": {
                "default_limit": 50,
                "output_dir": "scraped_data",
                "retry_failed": True,
                "max_retries": 3
            },
            "analysis": {
                "auto_analyze": True,
                "generate_charts": False,
                "export_csv": True
            },
            "files": {
                "urls_file": "9kAliexpresUrls.txt",
                "requirements_file": "requirements.txt"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file."""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_environment(self):
        """Setup the scraping environment and install dependencies."""
        print("Setting up AliExpress scraping environment...")
        
        # Check if requirements.txt exists
        req_file = os.path.join(self.project_dir, self.config['files']['requirements_file'])
        if not os.path.exists(req_file):
            print(f"Requirements file not found: {req_file}")
            return False
        
        try:
            # Install requirements
            print("Installing Python dependencies...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", req_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Dependencies installed successfully")
            else:
                print(f"✗ Error installing dependencies: {result.stderr}")
                return False
            
            # Check Chrome/Chromium availability
            print("Checking browser availability...")
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                
                # Try to setup a driver (this will download ChromeDriver if needed)
                service = Service(ChromeDriverManager().install())
                print("✓ Browser and WebDriver setup successful")
                
            except Exception as e:
                print(f"✗ Browser setup error: {e}")
                print("Please ensure Chrome or Chromium is installed")
                return False
            
            print("Environment setup completed successfully!")
            return True
            
        except Exception as e:
            print(f"Error during setup: {e}")
            return False
    
    def run_single_scrape(self, url: str, options: Dict[str, Any] = None):
        """Run single product scraping."""
        print(f"Scraping single product: {url}")
        
        if options is None:
            options = {}
        
        # Build command
        cmd = [
            sys.executable, 
            os.path.join(self.project_dir, "live_aliexpress_scraper.py"),
            url
        ]
        
        # Add options
        headless = options.get('headless', self.config['scraping']['headless'])
        cmd.append(f"--headless={str(headless).lower()}")
        
        proxy = options.get('proxy', self.config['scraping']['proxy'])
        if proxy:
            cmd.append(f"--proxy={proxy}")
        
        output_file = options.get('output_file')
        if output_file:
            cmd.append(f"--output={output_file}")
        
        # Run scraping
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Single scraping completed successfully")
                print(result.stdout)
            else:
                print("✗ Scraping failed")
                print(result.stderr)
        except Exception as e:
            print(f"Error running single scrape: {e}")
    
    def run_batch_scrape(self, options: Dict[str, Any] = None):
        """Run batch scraping."""
        print("Starting batch scraping...")
        
        if options is None:
            options = {}
        
        urls_file = os.path.join(self.project_dir, self.config['files']['urls_file'])
        if not os.path.exists(urls_file):
            print(f"URLs file not found: {urls_file}")
            return
        
        # Build command
        cmd = [
            sys.executable,
            os.path.join(self.project_dir, "batch_scraper.py"),
            urls_file
        ]
        
        # Add options
        limit = options.get('limit', self.config['batch']['default_limit'])
        if limit:
            cmd.append(f"--limit={limit}")
        
        headless = options.get('headless', self.config['scraping']['headless'])
        cmd.append(f"--headless={str(headless).lower()}")
        
        proxy = options.get('proxy', self.config['scraping']['proxy'])
        if proxy:
            cmd.append(f"--proxy={proxy}")
        
        rate_limit = options.get('rate_limit', self.config['scraping']['rate_limit'])
        cmd.append(f"--rate-limit={rate_limit}")
        
        output_dir = options.get('output_dir', self.config['batch']['output_dir'])
        cmd.append(f"--output={output_dir}")
        
        # Run batch scraping
        try:
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, text=True)
            
            if result.returncode == 0:
                print("✓ Batch scraping completed")
                
                # Auto-analyze if configured
                if self.config['analysis']['auto_analyze']:
                    self.run_analysis(output_dir)
            else:
                print("✗ Batch scraping failed")
        except Exception as e:
            print(f"Error running batch scrape: {e}")
    
    def run_analysis(self, data_dir: str = None):
        """Run data analysis."""
        if data_dir is None:
            data_dir = self.config['batch']['output_dir']
        
        data_path = os.path.join(self.project_dir, data_dir)
        if not os.path.exists(data_path):
            print(f"Data directory not found: {data_path}")
            return
        
        print(f"Analyzing data from: {data_path}")
        
        # Build command
        cmd = [
            sys.executable,
            os.path.join(self.project_dir, "data_analyzer.py"),
            data_path
        ]
        
        # Run analysis
        try:
            result = subprocess.run(cmd, text=True)
            if result.returncode == 0:
                print("✓ Data analysis completed")
            else:
                print("✗ Data analysis failed")
        except Exception as e:
            print(f"Error running analysis: {e}")
    
    def show_status(self):
        """Show current project status."""
        print("\n" + "=" * 60)
        print("ALIEXPRESS SCRAPER PROJECT STATUS")
        print("=" * 60)
        
        # Check files
        files_to_check = [
            ("Configuration", self.config_file),
            ("URLs File", os.path.join(self.project_dir, self.config['files']['urls_file'])),
            ("Requirements", os.path.join(self.project_dir, self.config['files']['requirements_file'])),
            ("Live Scraper", os.path.join(self.project_dir, "live_aliexpress_scraper.py")),
            ("Batch Scraper", os.path.join(self.project_dir, "batch_scraper.py")),
            ("Data Analyzer", os.path.join(self.project_dir, "data_analyzer.py")),
            ("Comprehensive Scraper", os.path.join(self.project_dir, "comprehensive_scraper.py"))
        ]
        
        print("\nFILES:")
        for name, path in files_to_check:
            status = "✓" if os.path.exists(path) else "✗"
            print(f"  {status} {name}: {os.path.basename(path)}")
        
        # Check data directories
        data_dir = os.path.join(self.project_dir, self.config['batch']['output_dir'])
        if os.path.exists(data_dir):
            json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
            print(f"\nDATA:")
            print(f"  Data Directory: {data_dir}")
            print(f"  Scraped Files: {len(json_files)} JSON files")
        
        # Show configuration
        print(f"\nCONFIGURATION:")
        print(f"  Headless Mode: {self.config['scraping']['headless']}")
        print(f"  Rate Limit: {self.config['scraping']['rate_limit']} seconds")
        print(f"  Default Batch Limit: {self.config['batch']['default_limit']}")
        print(f"  Auto Analysis: {self.config['analysis']['auto_analyze']}")
        
        print("=" * 60)
    
    def interactive_menu(self):
        """Show interactive menu for managing operations."""
        while True:
            print("\n" + "=" * 50)
            print("ALIEXPRESS SCRAPER MANAGEMENT")
            print("=" * 50)
            print("1. Show Status")
            print("2. Setup Environment")
            print("3. Configure Settings")
            print("4. Single Product Scrape")
            print("5. Batch Scrape")
            print("6. Analyze Data")
            print("7. View Configuration")
            print("8. Exit")
            print("-" * 50)
            
            try:
                choice = input("Select option (1-8): ").strip()
                
                if choice == '1':
                    self.show_status()
                
                elif choice == '2':
                    self.setup_environment()
                
                elif choice == '3':
                    self.configure_settings()
                
                elif choice == '4':
                    url = input("Enter AliExpress product URL: ").strip()
                    if url:
                        options = {}
                        headless = input(f"Headless mode? (y/n) [default: {'y' if self.config['scraping']['headless'] else 'n'}]: ").strip()
                        if headless.lower() in ['n', 'no', 'false']:
                            options['headless'] = False
                        self.run_single_scrape(url, options)
                
                elif choice == '5':
                    options = {}
                    limit = input(f"Number of URLs to process [default: {self.config['batch']['default_limit']}]: ").strip()
                    if limit.isdigit():
                        options['limit'] = int(limit)
                    self.run_batch_scrape(options)
                
                elif choice == '6':
                    data_dir = input(f"Data directory [default: {self.config['batch']['output_dir']}]: ").strip()
                    if not data_dir:
                        data_dir = None
                    self.run_analysis(data_dir)
                
                elif choice == '7':
                    print(json.dumps(self.config, indent=2))
                
                elif choice == '8':
                    print("Goodbye!")
                    break
                
                else:
                    print("Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def configure_settings(self):
        """Interactive configuration menu."""
        print("\nCONFIGURATION MENU")
        print("-" * 30)
        
        # Scraping settings
        print("Scraping Settings:")
        headless = input(f"Headless mode (y/n) [current: {'y' if self.config['scraping']['headless'] else 'n'}]: ").strip()
        if headless.lower() in ['y', 'yes', 'true']:
            self.config['scraping']['headless'] = True
        elif headless.lower() in ['n', 'no', 'false']:
            self.config['scraping']['headless'] = False
        
        rate_limit = input(f"Rate limit in seconds [current: {self.config['scraping']['rate_limit']}]: ").strip()
        if rate_limit.replace('.', '').isdigit():
            self.config['scraping']['rate_limit'] = float(rate_limit)
        
        # Batch settings
        print("\nBatch Settings:")
        batch_limit = input(f"Default batch limit [current: {self.config['batch']['default_limit']}]: ").strip()
        if batch_limit.isdigit():
            self.config['batch']['default_limit'] = int(batch_limit)
        
        # Analysis settings
        print("\nAnalysis Settings:")
        auto_analyze = input(f"Auto-analyze after batch scraping (y/n) [current: {'y' if self.config['analysis']['auto_analyze'] else 'n'}]: ").strip()
        if auto_analyze.lower() in ['y', 'yes', 'true']:
            self.config['analysis']['auto_analyze'] = True
        elif auto_analyze.lower() in ['n', 'no', 'false']:
            self.config['analysis']['auto_analyze'] = False
        
        # Save configuration
        self.save_config()
        print("Configuration updated!")


def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Command-line interface
        command = sys.argv[1].lower()
        manager = ScraperManager()
        
        if command == 'setup':
            manager.setup_environment()
        elif command == 'status':
            manager.show_status()
        elif command == 'config':
            manager.configure_settings()
        elif command == 'single' and len(sys.argv) > 2:
            manager.run_single_scrape(sys.argv[2])
        elif command == 'batch':
            options = {}
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                options['limit'] = int(sys.argv[2])
            manager.run_batch_scrape(options)
        elif command == 'analyze':
            data_dir = sys.argv[2] if len(sys.argv) > 2 else None
            manager.run_analysis(data_dir)
        else:
            print("Usage: python scraper_manager.py <command> [options]")
            print("Commands: setup, status, config, single <url>, batch [limit], analyze [data_dir]")
    else:
        # Interactive interface
        manager = ScraperManager()
        manager.interactive_menu()


if __name__ == "__main__":
    main()
