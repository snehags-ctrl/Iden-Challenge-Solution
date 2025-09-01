import json
import os
import time
import logging
from typing import List, Dict, Set, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError, Page, BrowserContext, Browser

# ============================================================================
# CONFIGURATION
# ============================================================================
SESSION_FILE = "session.json"
PRODUCTS_FILE = "products.json"
LOG_FILE = "scraping.log"

EMAIL = "sneha.g.s@campusuvce.in"
PASSWORD = "8D2g2xCT"
APP_URL = "https://hiring.idenhq.com/"

HEADERS = [
    "item_#", "cost", "sku", "details", "product",
    "dimensions", "weight_(kg)", "type"
]

# ============================================================================
# LOGGING SETUP
# ============================================================================
def setup_logging():
    """Configure comprehensive logging for debugging and monitoring."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

# ============================================================================
# SESSION MANAGEMENT
# ============================================================================
def save_session(context: BrowserContext) -> None:
    """Save browser session state for future reuse."""
    try:
        context.storage_state(path=SESSION_FILE)
        logger.info(f"✅ Session saved to {SESSION_FILE}")
    except Exception as e:
        logger.error(f"❌ Failed to save session: {e}")
        raise

def load_session_if_exists() -> Optional[str]:
    """Check if a valid session file exists."""
    if os.path.exists(SESSION_FILE):
        try:
            # Validate session file is readable JSON
            with open(SESSION_FILE, 'r') as f:
                json.load(f)
            logger.info("✅ Valid existing session found")
            return SESSION_FILE
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"⚠️ Corrupted session file: {e}")
            os.remove(SESSION_FILE)
    return None

def get_page_with_session(p) -> tuple[Page, BrowserContext, Browser]:
    """
    Smart session management: load existing session or create new one.
    
    Excellence Strategy: Properly manages user sessions with validation
    """
    browser = p.chromium.launch(headless=False)
    context = None

    session_file = load_session_if_exists()
    
    if session_file:
        try:
            logger.info("🔄 Attempting to use existing session...")
            context = browser.new_context(storage_state=session_file)
            page = context.new_page()
            page.goto(APP_URL)
            
            # Smart waiting: Check if session is still valid
            try:
                page.wait_for_selector("text=Menu", timeout=5000)
                logger.info("✅ Existing session is valid")
                return page, context, browser
            except PWTimeoutError:
                logger.warning("⚠️ Session expired, will create new login")
                context.close()
                os.remove(session_file)
                
        except Exception as e:
            logger.error(f"❌ Failed to load session: {e}")
            if os.path.exists(session_file):
                os.remove(session_file)

    # Create new session
    logger.info("🆕 Creating new session...")
    context = browser.new_context()
    page = context.new_page()
    page.goto(APP_URL)
    
    # Smart waiting: Wait for page to fully load
    page.wait_for_load_state("domcontentloaded")
    
    # Perform login
    login(page)
    save_session(context)
    
    return page, context, browser

# ============================================================================
# SMART LOGIN WITH ROBUST ERROR HANDLING
# ============================================================================
def login(page: Page) -> None:
    """
    Robust login function with smart waiting and comprehensive error handling.
    
    Excellence Strategy: Implement smart waiting strategies for elements to appear
    """
    try:
        logger.info("🔐 Starting login process...")
        
        # Smart waiting: Wait for login form to be ready
        page.wait_for_selector("input[type='email']", timeout=15000)
        page.wait_for_selector("input[type='password']", timeout=15000)
        
        # Fill credentials with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Clear and fill email
                email_input = page.locator("input[type='email']").first
                email_input.clear()
                email_input.fill(EMAIL)
                
                # Clear and fill password
                password_input = page.locator("input[type='password']").first
                password_input.clear()
                password_input.fill(PASSWORD)
                
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise RuntimeError(f"Failed to fill credentials after {max_retries} attempts: {e}")
                logger.warning(f"⚠️ Attempt {attempt + 1} failed, retrying...")
                time.sleep(1)
        
        # Smart waiting: Wait for sign-in button and click
        signin_button = page.locator("button:has-text('Sign in')").first
        signin_button.wait_for(state="visible", timeout=10000)
        signin_button.click()
        
        # Smart waiting: Wait for successful login (Menu button appears)
        page.wait_for_selector("text=Menu", timeout=20000)
        
        logger.info("✅ Login successful")
        
    except PWTimeoutError as e:
        logger.error(f"❌ Login timeout: {e}")
        raise RuntimeError("❌ Login failed: Timeout waiting for elements")
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        raise RuntimeError(f"❌ Login failed: {e}")

# ============================================================================
# INTELLIGENT NAVIGATION WITH SMART WAITING
# ============================================================================
def navigate_to_products(page: Page) -> None:
    """
    Navigate to product table with intelligent waiting and error handling.
    
    Excellence Strategy: Implement smart waiting strategies for elements to appear
    """
    try:
        logger.info("🧭 Starting navigation to product table...")
        
        # Step 1: Click Menu button
        menu_button = page.locator("text=Menu").first
        menu_button.wait_for(state="visible", timeout=10000)
        menu_button.click()
        logger.info("✅ Clicked Menu button")
        
        # Smart waiting: Wait for menu to expand
        page.wait_for_timeout(1000)
        
        # Step 2: Click Data Management
        data_mgmt = page.locator("text=Data Management").first
        data_mgmt.wait_for(state="visible", timeout=10000)
        data_mgmt.click()
        logger.info("✅ Clicked Data Management")
        
        # Smart waiting: Wait for submenu
        page.wait_for_timeout(1000)
        
        # Step 3: Click Inventory
        inventory = page.locator("text=Inventory").first
        inventory.wait_for(state="visible", timeout=10000)
        inventory.click()
        logger.info("✅ Clicked Inventory")
        
        # Smart waiting: Wait for submenu
        page.wait_for_timeout(1000)
        
        # Step 4: Click View All Products
        view_products = page.locator("text=View All Products").first
        view_products.wait_for(state="visible", timeout=10000)
        view_products.click()
        logger.info("✅ Clicked View All Products")
        
        # Smart waiting: Wait for table to load
        page.wait_for_timeout(3000)
        page.wait_for_selector("table, div[role='table']", timeout=20000)
        
        # Take screenshot for verification
        page.screenshot(path="after_navigation.png")
        logger.info("📸 Screenshot saved as after_navigation.png")
        logger.info("✅ Successfully reached product table")
        
    except Exception as e:
        logger.error(f"❌ Navigation failed: {e}")
        raise RuntimeError(f"❌ Navigation failed: {e}")

# ============================================================================
# DATA VALIDATION AND DEDUPLICATION
# ============================================================================
def validate_product_data(product: Dict) -> bool:
    """Validate product data integrity."""
    try:
        # Check all required fields exist
        for header in HEADERS:
            if header not in product:
                logger.warning(f"⚠️ Missing field: {header}")
                return False
        
        # Check item_# is numeric
        try:
            int(product["item_#"])
        except ValueError:
            logger.warning(f"⚠️ Invalid item_#: {product['item_#']}")
            return False
        
        # Check SKU format
        if not product["sku"] or len(product["sku"]) < 3:
            logger.warning(f"⚠️ Invalid SKU: {product['sku']}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"❌ Data validation error: {e}")
        return False

def load_existing_products(filename: str = PRODUCTS_FILE) -> List[Dict]:
    """Load existing products with validation."""
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                products = json.load(f)
                logger.info(f"✅ Loaded {len(products)} existing products")
                
                # Validate existing data
                valid_products = [p for p in products if validate_product_data(p)]
                if len(valid_products) != len(products):
                    logger.warning(f"⚠️ Filtered out {len(products) - len(valid_products)} invalid products")
                
                return valid_products
        except Exception as e:
            logger.error(f"❌ Failed to load existing products: {e}")
            return []
    return []

def save_products_to_json(products: List[Dict], filename: str = PRODUCTS_FILE) -> None:
    """Save products with error handling and backup."""
    try:
        # Create backup of existing file
        if os.path.exists(filename):
            backup_name = f"{filename}.backup"
            os.rename(filename, backup_name)
            logger.info(f"📦 Created backup: {backup_name}")
        
        # Save new data
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4, ensure_ascii=False)
        
        logger.info(f"✅ Saved {len(products)} products to {filename}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save products: {e}")
        # Restore backup if save failed
        if os.path.exists(f"{filename}.backup"):
            os.rename(f"{filename}.backup", filename)
            logger.info("🔄 Restored backup file")
        raise

# ============================================================================
# ROBUST SCRAPING WITH EXCELLENCE STRATEGIES
# ============================================================================
def scrape_products(page: Page, existing_products: List[Dict]) -> List[Dict]:
    """
    Advanced product scraping with comprehensive deduplication and error handling.
    
    Excellence Strategy: Develop robust techniques to handle pagination or lazy-loaded content
    """
    products = existing_products.copy()
    
    # Enhanced deduplication: Track both item_# and SKU
    seen_item_nums: Set[str] = set(p["item_#"] for p in products)
    seen_skus: Set[str] = set(p["sku"] for p in products)
    
    logger.info(f"🔄 Starting scraping with {len(products)} existing products")
    logger.info(f"📊 Tracking {len(seen_item_nums)} unique item_# and {len(seen_skus)} unique SKUs")
    
    # Wait for table to be ready
    table_body = page.locator("table tbody")
    table_body.locator("tr").first.wait_for(state="visible", timeout=15000)
    
    MAX_RETRIES = 5
    scroll_pause = 0.5
    page_num = 1
    total_new_products = 0
    
    while True:
        try:
            rows = table_body.locator("tr")
            total_rows = rows.count()
            any_new = False
            
            logger.info(f"📄 Processing page {page_num} with {total_rows} rows")
            
            for i in range(total_rows):
                for attempt in range(MAX_RETRIES):
                    try:
                        row = rows.nth(i)
                        cells = [cell.inner_text().strip() for cell in row.locator("td").all()]
                        
                        if len(cells) != len(HEADERS):
                            logger.warning(f"⚠️ Row {i+1} has {len(cells)} cells, expected {len(HEADERS)}")
                            continue
                        
                        row_dict = dict(zip(HEADERS, cells))
                        
                        # Enhanced deduplication logic
                        item_num = row_dict["item_#"]
                        sku = row_dict["sku"]
                        
                        # Check if this is a truly new product
                        if item_num not in seen_item_nums and sku not in seen_skus:
                            if validate_product_data(row_dict):
                                seen_item_nums.add(item_num)
                                seen_skus.add(sku)
                                products.append(row_dict)
                                any_new = True
                                total_new_products += 1
                                
                                # Progress update
                                if total_new_products % 10 == 0:
                                    logger.info(f"🆕 Added {total_new_products} new products so far")
                            else:
                                logger.warning(f"⚠️ Skipped invalid product: {item_num}")
                        elif item_num in seen_item_nums:
                            logger.debug(f"🔄 Skipped duplicate item_#: {item_num}")
                        elif sku in seen_skus:
                            logger.debug(f"🔄 Skipped duplicate SKU: {sku}")
                        
                        break
                        
                    except Exception as e:
                        if attempt == MAX_RETRIES - 1:
                            logger.error(f"❌ Failed to process row {i+1} after {MAX_RETRIES} attempts: {e}")
                        else:
                            time.sleep(scroll_pause)
                            # Try to refresh the row data
                            try:
                                table_handle = table_body.element_handle()
                                if table_handle:
                                    page.evaluate("table => table.scrollTop += 50", table_handle)
                            except:
                                pass
            
            # Smart pagination handling
            next_btn = page.locator("button:has-text('Next')").first
            if next_btn.count() > 0 and next_btn.get_attribute("aria-disabled") != "true":
                logger.info(f"➡️ Moving to next page...")
                next_btn.click()
                page.wait_for_timeout(2000)  # Increased wait time
                table_body.locator("tr").first.wait_for(state="visible", timeout=15000)
                page_num += 1
            else:
                logger.info("🏁 Reached end of pagination")
                break
            
            # Save progress every 50 new products
            if total_new_products % 50 == 0 and total_new_products > 0:
                save_products_to_json(products)
                logger.info(f"💾 Progress saved: {len(products)} total products")
            
            if not any_new:
                logger.info("🔄 No new products found on this page, stopping")
                break
                
        except Exception as e:
            logger.error(f"❌ Error processing page {page_num}: {e}")
            # Try to continue with next page
            try:
                next_btn = page.locator("button:has-text('Next')").first
                if next_btn.count() > 0 and next_btn.get_attribute("aria-disabled") != "true":
                    next_btn.click()
                    page.wait_for_timeout(2000)
                    table_body.locator("tr").first.wait_for(state="visible", timeout=15000)
                    page_num += 1
                    continue
            except:
                pass
            break
    
    logger.info(f"✅ Scraping completed: {total_new_products} new products added")
    logger.info(f"📊 Total products: {len(products)}")
    logger.info(f"🔢 Unique item_#: {len(set(p['item_#'] for p in products))}")
    logger.info(f"🏷️ Unique SKUs: {len(set(p['sku'] for p in products))}")
    
    return products

# ============================================================================
# MAIN EXECUTION WITH COMPREHENSIVE ERROR HANDLING
# ============================================================================
def main():
    """
    Main execution function with comprehensive error handling and logging.
    
    Excellence Strategy: Create clean, well-documented, and error-resistant Python code
    """
    global logger
    logger = setup_logging()
    
    logger.info("🚀 Starting Iden Challenge Data Extraction")
    logger.info("=" * 50)
    
    try:
        with sync_playwright() as p:
            # Smart session management
            page, context, browser = get_page_with_session(p)
            
            # Intelligent navigation
            navigate_to_products(page)
            
            # Load and validate existing data
            existing_products = load_existing_products()
            
            # Robust scraping with excellence strategies
            products = scrape_products(page, existing_products)
            
            # Save final results
            save_products_to_json(products)
            
            # Final validation
            final_item_nums = [p["item_#"] for p in products]
            final_skus = [p["sku"] for p in products]
            
            logger.info("=" * 50)
            logger.info("🎯 FINAL RESULTS:")
            logger.info(f"📦 Total Products: {len(products)}")
            logger.info(f"🔢 Unique Item Numbers: {len(set(final_item_nums))}")
            logger.info(f"🏷️ Unique SKUs: {len(set(final_skus))}")
            logger.info(f"✅ Duplicate Check: {'PASSED' if len(products) == len(set(final_item_nums)) else 'FAILED'}")
            
            browser.close()
            logger.info("🎉 Data extraction completed successfully!")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Process interrupted by user")
    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        logger.error("Stack trace:", exc_info=True)
        raise
    finally:
        logger.info("🏁 Process finished")

if __name__ == "__main__":
    main()
