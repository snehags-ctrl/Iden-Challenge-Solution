import time
from playwright.sync_api import sync_playwright

EMAIL = "sneha.g.s@campusuvce.in"
PASSWORD = "8D2g2xCT"
APP_URL = "https://hiring.idenhq.com/"

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("🌐 Navigating to application...")
        page.goto(APP_URL)
        page.wait_for_load_state("domcontentloaded")
        
        print("📸 Taking screenshot of login page...")
        page.screenshot(path="login_page.png")
        
        print("🔍 Looking for login elements...")
        
        # Wait a bit for page to fully load
        time.sleep(3)
        
        # Try to find email input
        email_inputs = page.locator("input[type='email']").all()
        print(f"📧 Found {len(email_inputs)} email input fields")
        
        # Try to find password input
        password_inputs = page.locator("input[type='password']").all()
        print(f"🔒 Found {len(password_inputs)} password input fields")
        
        # Try to find login button
        login_buttons = page.locator("button:has-text('Login')").all()
        print(f"🔘 Found {len(login_buttons)} login buttons")
        
        # Try to find any button with text containing 'login' (case insensitive)
        any_login_buttons = page.locator("button").filter(has_text="login").all()
        print(f"🔘 Found {len(any_login_buttons)} buttons with 'login' text")
        
        # List all buttons on the page
        all_buttons = page.locator("button").all()
        print(f"🔘 Total buttons found: {len(all_buttons)}")
        
        for i, btn in enumerate(all_buttons):
            try:
                text = btn.inner_text()
                print(f"  Button {i+1}: '{text}'")
            except:
                print(f"  Button {i+1}: [text not readable]")
        
        # List all input fields
        all_inputs = page.locator("input").all()
        print(f"📝 Total input fields found: {len(all_inputs)}")
        
        for i, inp in enumerate(all_inputs):
            try:
                input_type = inp.get_attribute("type") or "text"
                placeholder = inp.get_attribute("placeholder") or ""
                print(f"  Input {i+1}: type='{input_type}', placeholder='{placeholder}'")
            except:
                print(f"  Input {i+1}: [attributes not readable]")
        
        print("✅ Debug information collected. Check login_page.png for visual reference.")
        browser.close()

if __name__ == "__main__":
    test_login()
