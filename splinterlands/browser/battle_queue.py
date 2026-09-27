"""
Browser automation for Splinterlands battle queue monitoring.

This module uses Playwright to monitor the Splinterlands battle page and 
auto-submit teams when a battle is matched. Requires Brave to already be 
logged in via normal browser use (doesn't need Keychain extension).
"""

import asyncio
import logging
import time
import subprocess
import shutil
import os
import re
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Page, BrowserContext

logger = logging.getLogger(__name__)



class SplinterlandsBattleMonitor:
    """Monitors Splinterlands battle page and auto-submits teams."""
    
    def __init__(self, username: str, headless: bool = False):
        """
        Initialize battle monitor.
        
        Args:
            username: Splinterlands username
            headless: Whether to run browser in headless mode (default False - show browser)
        """
        self.username = username
        self.headless = headless
        self.browser: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright_instance = None
        self.temp_user_dir = None
        self.team_manager = None  # Will be set by monitor_and_submit_battles
        
    async def launch_browser(self):
        """Launch Brave browser with user's existing login."""
        logger.info(f"🌐 Launching Brave browser (must be already logged into Splinterlands)...")
        
        self.playwright_instance = await async_playwright().start()
        
        # Find Brave path and user data directory
        brave_paths = {
            "linux": "/usr/bin/brave-browser",
            "darwin": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
            "win32": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
        }
        
        brave_user_data_dirs = {
            "linux": str(Path.home() / ".config/BraveSoftware/Brave-Browser"),
            "darwin": str(Path.home() / "Library/Application Support/BraveSoftware/Brave-Browser"),
            "win32": str(Path.home() / "AppData/Local/BraveSoftware/Brave-Browser"),
        }
        
        import sys
        platform_key = sys.platform
        if platform_key == "win32":
            platform_key = "win32"
        elif platform_key == "darwin":
            platform_key = "darwin"
        else:
            platform_key = "linux"
        
        brave_path = brave_paths.get(platform_key)
        brave_user_dir = brave_user_data_dirs.get(platform_key)
        
        if brave_path and Path(brave_path).exists():
            logger.info(f"✓ Found Brave: {brave_path}")
        else:
            brave_path = None
            logger.warning(f"⚠️  Brave not found at expected location, will use system default")
        
        # If user data dir exists, try to copy it to a temp location to avoid singleton lock
        browser = None
        if brave_user_dir and Path(brave_user_dir).exists():
            logger.info(f"✓ Found Brave user data: {brave_user_dir}")
            
            # Create a temporary copy of the user data to avoid singleton lock issues
            import tempfile
            temp_user_dir = tempfile.mkdtemp(prefix="brave_temp_")
            logger.info(f"📋 Creating temporary user data copy: {temp_user_dir}")
            
            try:
                # Copy user data directory, skipping singleton lock files
                def ignore_patterns(dir, files):
                    return [f for f in files if f in ('SingletonSocket', 'SingletonCookie', 'SingletonLock')]
                
                shutil.copytree(brave_user_dir, temp_user_dir, dirs_exist_ok=True, ignore=ignore_patterns)
                
                # Try to launch with the temporary user data
                browser = await self.playwright_instance.chromium.launch_persistent_context(
                    user_data_dir=temp_user_dir,
                    executable_path=brave_path if brave_path else None,
                    headless=self.headless,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                    ],
                )
                self.page = await browser.new_page()
                logger.info("✓ Browser launched with temporary copy of user data (keeps login)")
                self.browser = browser
                self.temp_user_dir = temp_user_dir  # Store for cleanup
                return
                
            except Exception as e:
                logger.warning(f"⚠️  Failed to use temp user data copy: {e}")
                # Cleanup temp dir on failure
                try:
                    shutil.rmtree(temp_user_dir)
                except:
                    pass
        
        # Fallback: try fresh launch as fallback
        logger.info("Trying fresh browser launch...")
        try:
            chrome = await self.playwright_instance.chromium.launch(
                executable_path=brave_path if brave_path else None,
                headless=self.headless,
            )
            self.browser = chrome
            self.page = await self.browser.new_page()
            logger.warning("⚠️  Launched fresh browser (you may need to log in manually)")
            
        except Exception as e:
            logger.error(f"❌ Failed to launch browser: {e}")
            if self.playwright_instance:
                await self.playwright_instance.stop()
            raise
    
    async def navigate_to_queue(self):
        """Navigate to Splinterlands battle queue page."""
        url = "https://splinterlands.com/?p=battle"
        logger.info(f"📍 Opening {url}")
        
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(1)
            logger.info("✓ Queue page loaded")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to navigate: {e}")
            return False
    
    async def monitor_for_team_selection(self, timeout_seconds: int = 120, check_interval: float = 1.0) -> bool:
        """
        Monitor battle page for team selection UI to appear (battle was matched).
        When detected, auto-submit team with strategy.
        
        Args:
            timeout_seconds: How long to monitor before giving up
            check_interval: Check frequency in seconds
            
        Returns:
            True if battle detected and team submitted, False if timeout
        """
        logger.info(f"👁️  Monitoring for battle match (timeout: {timeout_seconds}s, checking every {check_interval}s)...")
        
        start_time = time.time()
        last_page_url = None
        check_count = 0
        
        while time.time() - start_time < timeout_seconds:
            try:
                check_count += 1
                current_url = self.page.url
                
                # Log URL every 10 checks to show progress
                if check_count % 10 == 0 or check_count == 1:
                    logger.debug(f"Check #{check_count}: URL = {current_url}")
                
                # Detect URL change - when matched, Splinterlands often redirects to a specific battle URL
                if current_url != last_page_url:
                    last_page_url = current_url
                    
                    # Look for battle-specific URL patterns
                    if "/battle/" in current_url or "battle_id" in current_url:
                        elapsed = time.time() - start_time
                        logger.info(f"✅ Battle URL detected: {current_url} ({elapsed:.1f}s)")
                        return True
                
                # Check for key team selection UI elements - be strict about detection
                # Only consider it a battle if we can clearly see UI for team selection
                selectors_to_check = [
                    'button:has-text("SUBMIT")',  # Final submit button - strongest signal
                    'text="Your team"',  # Specific text that appears in battle UI
                    'text="Score"',  # Battle scoring UI
                    '[class*="summon"]',  # Summon/card selection
                    '[class*="rule"]:visible',  # Visible ruleset (indicates battle screen)
                ]
                
                for selector in selectors_to_check:
                    try:
                        elements = self.page.locator(selector)
                        count = await elements.count()
                        if count > 0:
                            elapsed = time.time() - start_time
                            logger.info(f"✅ Battle matched! Found: {selector} ({elapsed:.1f}s)")
                            return True
                    except:
                        pass
                
                # Log every 30 seconds to show we're still monitoring
                if check_count % 30 == 0:
                    logger.info(f"⏳ Still monitoring... (checked {check_count} times, elapsed {time.time() - start_time:.0f}s)")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.debug(f"Monitor error: {e}")
                await asyncio.sleep(check_interval)
        
        logger.warning(f"⏱️  No battle detected after {timeout_seconds}s (checked {check_count} times)")
        logger.info(f"Final URL: {self.page.url}")
        return False
    
    async def submit_team_if_visible(self) -> bool:
        """
        If team selection UI is visible, submit a team via the API.
        
        Returns:
            True if submission worked, False otherwise
        """
        try:
            logger.info("🎯 Battle detected! Analyzing page...")
            
            # Wait longer for page to fully render (battles need more time)
            logger.info("⏳ Waiting for UI to fully render...")
            await asyncio.sleep(4)
            
            # Take a screenshot for debugging (save to /tmp)
            try:
                screenshot_path = "/tmp/splinterlands_battle_screenshot.png"
                await self.page.screenshot(path=screenshot_path)
                logger.info(f"📸 Screenshot saved: {screenshot_path}")
            except Exception as e:
                logger.debug(f"Screenshot failed: {e}")
            
            # Extract battle_id from page URL or content
            current_url = self.page.url
            logger.info(f"Current URL: {current_url}")
            
            # Try to extract battle_id from URL (pattern: /battle/<id>)
            battle_id_match = re.search(r'/battle[/?#]*([0-9a-f]+)', current_url)
            if battle_id_match:
                battle_id = battle_id_match.group(1)
                logger.info(f"✓ Extracted battle_id from URL: {battle_id}")
            else:
                # Try to find battle_id in page content (look for data attributes or window variables)
                logger.debug("Battle ID not in URL, searching page content...")
                try:
                    # Look for battle_id in window.battle variable or data attributes
                    battle_id_from_page = await self.page.evaluate("() => window.battle_id || globalThis.battle_id || document.body.getAttribute('data-battle-id') || ''")
                    if battle_id_from_page:
                        battle_id = battle_id_from_page
                        logger.info(f"✓ Found battle_id in page: {battle_id}")
                    else:
                        logger.error("Could not find battle_id in URL or page content")
                        # Still try API submission with what we have
                        battle_id = None
                except:
                    battle_id = None
            
            # If we managed to get a battle_id and have a team_manager, use API submission
            if battle_id and self.team_manager:
                logger.info(f"🔄 Using API to submit team for battle: {battle_id}")
                return await self._submit_via_api(battle_id)
            
            # Fallback: Try UI-based submission (button clicks)
            logger.info("🖱️  Falling back to UI-based submission...")
            return await self._submit_via_ui()
                
        except Exception as e:
            logger.error(f"❌ Error in team submission: {e}")
            return False
    
    async def _submit_via_api(self, battle_id: str) -> bool:
        """
        Submit team via the Splinterlands API.
        
        Args:
            battle_id: The battle ID to submit for
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"📤 Submitting team via API for battle {battle_id}...")
            
            # Use water strategy as default
            from splinterlands.strategy import water_strategy
            from splinterlands.game.card_pool import CardPool
            
            # Build a water team using the strategy
            try:
                pool = CardPool()
                team = water_strategy.build_team(pool, battle_id)
                
                if team:
                    logger.info(f"🎯 Selected team: {team.summoner.name} + {len(team.monsters)} monsters")
                    
                    # Submit via API
                    response = self.team_manager.submit_team(team)
                    
                    if response.get("success"):
                        logger.info(f"✅ Team submitted successfully via API!")
                        return True
                    else:
                        error_msg = response.get("message", "Unknown error")
                        logger.error(f"❌ API submission failed: {error_msg}")
                        return False
                else:
                    logger.error("Could not build team from strategy")
                    return False
            except Exception as e:
                logger.error(f"Strategy/team building failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"API submission error: {e}")
            return False
    
    async def _submit_via_ui(self) -> bool:
        """
        Fallback: Submit team by clicking buttons in the UI.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Log ALL buttons on the page so we can identify the right one
            logger.info("--- ALL BUTTONS ON PAGE ---")
            all_buttons = self.page.locator('button')
            button_count = await all_buttons.count()
            for i in range(button_count):
                try:
                    btn = all_buttons.nth(i)
                    btn_text = await btn.text_content()
                    btn_class = await btn.get_attribute('class')
                    btn_id = await btn.get_attribute('id')
                    is_visible = await btn.is_visible()
                    logger.info(f"Button {i}: text='{btn_text[:50]}' class='{btn_class}' id='{btn_id}' visible={is_visible}")
                except Exception as e:
                    logger.debug(f"Error reading button {i}: {e}")
            logger.info("--- END BUTTON LIST ---")
            
            # Now look for SUBMIT button and click it
            # Try increasingly specific selectors with longer waits
            submit_selectors = [
                # Most specific - exact case match with SUBMIT text
                ('button:has-text("SUBMIT")', 5000),
                ('button:has-text("Submit")', 5000),
                ('button:has-text("submit")', 5000),
                
                # Try common CSS classes/IDs for submit
                ('[id*="submit"]:visible', 5000),
                ('[class*="submit"]:visible', 5000),
                ('button[class*="btn-primary"]', 5000),
                ('button[class*="btn-success"]', 5000),
                ('[type="submit"]', 5000),  # Form submit button
                ('form button', 5000),       # Button inside a form
            ]
            
            for selector, wait_timeout in submit_selectors:
                try:
                    logger.debug(f"Trying selector: {selector}")
                    submit_button = self.page.locator(selector).first
                    
                    # Wait for it to be visible
                    try:
                        await submit_button.wait_for(state="visible", timeout=wait_timeout)
                        logger.debug(f"✓ Found element: {selector}")
                    except:
                        logger.debug(f"Not visible yet: {selector}")
                        continue
                    
                    # Try to get and log the button details BEFORE clicking
                    try:
                        btn_text = await submit_button.text_content()
                        btn_class = await submit_button.get_attribute('class')
                        logger.info(f"About to click button - text: '{btn_text[:100]}' class: '{btn_class}'")
                    except:
                        logger.debug("Could not read button details")
                    
                    # Check if this looks like a real SUBMIT - should have "SUBMIT" or "Submit" in text
                    try:
                        btn_text = await submit_button.text_content()
                        if "submit" in btn_text.lower():
                            logger.info(f"CONFIRMED: Button contains 'submit' text")
                    except:
                        # If we can't read text, be cautious with generic selectors
                        if selector.startswith('button:nth') or selector.startswith('button[type'):
                            logger.warning(f"Skipping generic selector {selector} - can't verify it's SUBMIT button")
                            continue
                    
                    # Now click it
                    logger.info(f"🖱️  Clicking button (selector: {selector})")
                    await submit_button.click(timeout=5000)
                    logger.info(f"✅ Button clicked!")
                    await asyncio.sleep(3)  # Wait for submission to process
                    
                    # Verify we left the team selection page (page should change)
                    new_url = self.page.url
                    logger.info(f"Page after button click: {new_url}")
                    
                    return True
                except Exception as e:
                    logger.debug(f"Failed with {selector}: {str(e)[:100]}")
                    continue
            
            logger.error("❌ Could not find/click SUBMIT button")
            logger.info("⚠️  Please check the screenshot at /tmp/splinterlands_battle_screenshot.png")
            logger.info("⚠️  Screenshot will show the actual UI - check what buttons/elements are visible")
            return False
                
        except Exception as e:
            logger.error(f"❌ Error in UI submission: {e}")
            return False
    
    async def close(self):
        """Close browser and cleanup temp directories."""
        if self.page:
            try:
                await self.page.close()
            except:
                pass
        if self.browser:
            try:
                await self.browser.close()
            except:
                pass
        if self.playwright_instance:
            try:
                await self.playwright_instance.stop()
            except:
                pass
        
        # Clean up temporary user data directory if created
        if hasattr(self, 'temp_user_dir'):
            try:
                import shutil
                shutil.rmtree(self.temp_user_dir)
                logger.debug(f"Cleaned up temp user data: {self.temp_user_dir}")
            except:
                pass


async def monitor_and_submit_battles(username: str, team_manager=None, check_interval: float = 1.0, limit: int = 1) -> int:
    """
    Monitor Splinterlands battle page and auto-submit teams when matched.
    Keeps one browser instance open for all battles (more stable than restarting).
    
    Args:
        username: Splinterlands username
        team_manager: TeamManager instance for API submission (if None, will attempt UI clicks)
        check_interval: How often to check for new battles (seconds)
        limit: Max number of battles to submit before stopping
        
    Returns:
        Number of battles successfully submitted
    """
    submitted_count = 0
    monitor = SplinterlandsBattleMonitor(username, headless=False)
    monitor.team_manager = team_manager  # Store for use in submit method
    
    try:
        # Launch browser ONCE and keep it open for all battles
        await monitor.launch_browser()
        if not await monitor.navigate_to_queue():
            logger.error("Failed to navigate to battle queue")
            return submitted_count
        
        while submitted_count < limit:
            logger.info(f"\n[{submitted_count + 1}/{limit}] Monitoring for battle...")
            logger.info("Queue a battle in Splinterlands NOW...")
            
            # Monitor for battle match to appear
            if await monitor.monitor_for_team_selection(timeout_seconds=600, check_interval=check_interval):
                # Battle detected! Try to submit team
                await asyncio.sleep(0.5)  # Give page a moment to fully load
                
                url_before = monitor.page.url
                logger.info(f"URL before submission: {url_before}")
                
                if await monitor.submit_team_if_visible():
                    # Double check - verify the team was actually submitted
                    url_after = monitor.page.url
                    logger.info(f"URL after submission: {url_after}")
                    
                    # If we're still on the team selection page, submission probably failed
                    if url_before == url_after and "battle" in url_before.lower():
                        logger.warning("⚠️  URL hasn't changed - submission may have failed!")
                        logger.warning("⚠️  Waiting and retrying...")
                        await asyncio.sleep(3)
                        continue
                    
                    submitted_count += 1
                    logger.info(f"✅ Battle #{submitted_count} submitted successfully!")
                    
                    if submitted_count < limit:
                        logger.info(f"⏳ Waiting for next battle ({limit - submitted_count} remaining)...")
                        await asyncio.sleep(3)
                else:
                    logger.warning("⚠️  Battle detected but submission failed, waiting for next...")
                    await asyncio.sleep(3)
            else:
                # Timeout waiting for battle - ask user to try again
                logger.info(f"No battle detected. Make sure you queued it in Splinterlands!")
                if submitted_count >= limit:
                    break
                # Wait a moment then retry
                await asyncio.sleep(5)
        
        logger.info(f"\n✅ All done! Submitted {submitted_count} battles")
        
    except Exception as e:
        logger.error(f"❌ Error in monitor loop: {e}", exc_info=True)
    finally:
        await monitor.close()
    
    return submitted_count


if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    username = sys.argv[1] if len(sys.argv) > 1 else "tardigrade123"
    result = asyncio.run(monitor_and_submit_battles(username, limit=1))
    sys.exit(0 if result > 0 else 1)

