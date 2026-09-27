import yaml
import logging
import time
import asyncio
from typing import Optional
from splinterlands.game.account import Account
from splinterlands.game.card_pool import build_card_pool
from splinterlands.game.battle_state import BattleState
from splinterlands.game.team import TeamManager
from splinterlands.strategy.rule_engine import choose_team
from splinterlands.blockchain.monitor import monitor_for_battles
from splinterlands.browser.battle_queue import monitor_and_submit_battles


# Set up logging
def setup_logging(log_level: str):
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def load_config():
    """Load configuration from config.yaml"""
    with open("config/config.yaml", "r") as f:
        return yaml.safe_load(f)


def run_single_battle():
    """
    Handle a single battle cycle:
    - Check for active battle
    - Select team
    - Submit team
    
    Returns:
        True if battle handled, False if no active battle
    """
    config = load_config()
    username = config["account"]["username"]
    posting_key = config["account"]["posting_key"]
    logger = logging.getLogger(__name__)
    
    # Download account data
    account = Account(username)
    account.download()
    
    # Check if player has active battle
    if not account.has_active_battle():
        return False
    
    logger.info("\n⚔️  Active battle found! Starting team selection...")
    
    # Parse battle state
    try:
        battle_state = BattleState(account.battle_data)
        logger.info(f"Battle Summary: {battle_state.summary()}")
    except ValueError as e:
        logger.error(f"Failed to parse battle: {e}")
        return False
    
    # Build card pool
    logger.info("\n🃏 Loading card pool...")
    card_pool = build_card_pool(username)
    logger.info(f"   Total available cards: {len(card_pool)}")
    
    # Select team using strategy
    logger.info("\n🎯 Selecting team with Water Bot strategy...")
    team_selection = choose_team(battle_state, card_pool)
    
    if not team_selection:
        logger.error("❌ Failed to select a valid team")
        return False
    
    summoner, monsters = team_selection
    
    # Create team object
    team_manager = TeamManager(username, posting_key)
    team = team_manager.create_team(battle_state.battle_id, summoner, monsters)
    print(team.summary())
    
    # Submit team
    logger.info("\n📤 Submitting team to battle...")
    success = team_manager.submit_and_confirm(team)
    
    return success


def run_bot_loop(continuous: bool = False, check_interval: int = 5, limit: int = None):
    """
    Main bot loop
    
    Args:
        continuous: If True, continuously check for battles. If False, run once.
        check_interval: Seconds between battle checks (in continuous mode)
        limit: Max number of battles to handle before exiting (optional, continuous mode only)
    """
    config = load_config()
    setup_logging(config["bot"].get("log_level", "info"))
    logger = logging.getLogger(__name__)
    
    username = config["account"]["username"]
    
    logger.info(f"🤖 Splinterlands Wild Bot Starting")
    logger.info(f"   Account: {username}")
    
    if continuous:
        logger.info(f"   Mode: CONTINUOUS (checking every {check_interval}s)")
        if limit:
            logger.info(f"   Limit: {limit} battles")
        logger.info("   Waiting for battles...\n")
        battle_count = 0
        
        try:
            while True:
                # Check if we've reached the battle limit
                if limit and battle_count >= limit:
                    logger.info(f"\n✅ Battle limit ({limit}) reached. Exiting...")
                    break
                
                # Show account status
                try:
                    account = Account(username)
                    account.download()
                    
                    if account.has_active_battle():
                        battle_count += 1
                        logger.info(f"\n{'='*60}")
                        logger.info(f"🎯 BATTLE #{battle_count} DETECTED")
                        logger.info(f"{'='*60}")
                        
                        # Handle the battle
                        success = run_single_battle()
                        
                        if success:
                            logger.info("✅ Battle handled successfully!")
                        else:
                            logger.warning("⚠️  Battle handling completed with issues")
                        
                        # Wait before checking for next battle
                        logger.info(f"\n⏳ Waiting {check_interval}s before next check...")
                        time.sleep(check_interval)
                    else:
                        # Debug: Log what the API returned
                        if account.battle_data and 'battle' not in account.battle_data:
                            logger.debug(f"⏳ API returned, but no 'battle' field. Status: {account.battle_data.get('status', 'unknown')}")
                        logger.debug(f"⏳ No active battle. Checking again in {check_interval}s...")
                        time.sleep(check_interval)
                
                except Exception as e:
                    # Handle network errors gracefully - retry after interval
                    logger.warning(f"⚠️  API error: {type(e).__name__} - {str(e)[:100]}")
                    logger.debug(f"Retrying in {check_interval}s...")
                    time.sleep(check_interval)
        
        except KeyboardInterrupt:
            logger.info("\n\n👋 Bot stopped by user")
            logger.info(f"Total battles handled: {battle_count}")
    else:
        # Single run mode
        logger.info("\n📥 Downloading account data...")
        account = Account(username)
        account.download()
        print(account.summary())
        
        if not account.has_active_battle():
            logger.warning("\n⏳ No active battle. Waiting for battle matchmaking...")
            return False
        
        return run_single_battle()


def run_queue_loop(check_interval: int = 1, limit: Optional[int] = None):
    """
    Monitor Splinterlands battle queue page and auto-submit teams.
    
    This simple approach: opens Brave browser, monitors the battle page,
    and submits teams when opponent is matched.
    
    Args:
        check_interval: Seconds between checks (default 1s)
        limit: Max number of battles to submit (optional)
    """
    config = load_config()
    setup_logging(config["bot"].get("log_level", "info"))
    logger = logging.getLogger(__name__)
    
    username = config["account"]["username"]
    posting_key = config["account"]["posting_key"]
    
    logger.info(f"🤖 Splinterlands Wild Bot Starting")
    logger.info(f"   Account: {username}")
    logger.info(f"   Mode: AUTO-SUBMIT (monitoring for battles)")
    logger.info(f"   Check interval: {check_interval}s")
    if limit:
        logger.info(f"   Limit: {limit} battles")
    logger.info("   Requirements: Must be logged into Splinterlands in Brave\n")
    
    try:
        # Create team manager for API submissions
        team_manager = TeamManager(username, posting_key)
        
        # Run the monitor function with team_manager for API-based submissions
        submitted = asyncio.run(monitor_and_submit_battles(
            username=username,
            team_manager=team_manager,
            check_interval=check_interval,
            limit=limit or float('inf')
        ))
        
        logger.info(f"\n✅ Complete! Submitted {submitted} battles total.")
        
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)


def run_blockchain_loop(check_interval: int = 3, limit: Optional[int] = None):
    """
    Monitor Hive blockchain for battle challenges and auto-submit teams.
    
    This is the most reliable approach:
    - Monitors blockchain for 'sm_challenge' operations (battles)
    - No REST API polling, no browser automation needed
    - Works completely unattended
    
    Args:
        check_interval: Seconds between blockchain checks (default 3s)
        limit: Max number of battles to submit (optional)
    """
    config = load_config()
    setup_logging(config["bot"].get("log_level", "info"))
    logger = logging.getLogger(__name__)
    
    username = config["account"]["username"]
    posting_key = config["account"]["posting_key"]
    
    logger.info(f"🤖 Splinterlands Wild Bot Starting")
    logger.info(f"   Account: {username}")
    logger.info(f"   Mode: BLOCKCHAIN MONITORING (Hive chain)")
    logger.info(f"   Check interval: {check_interval}s")
    if limit:
        logger.info(f"   Limit: {limit} battles")
    logger.info("   Monitoring for 'sm_challenge' operations on Hive blockchain\n")
    
    battle_count = 0
    
    try:
        while True:
            # Check if we've reached the battle limit
            if limit and battle_count >= limit:
                logger.info(f"\n✅ Battle limit ({limit}) reached. Exiting...")
                break
            
            # Monitor blockchain for a new battle
            try:
                challenge = monitor_for_battles(username, check_interval=check_interval)
                
                if challenge:
                    battle_count += 1
                    logger.info(f"\n{'='*60}")
                    logger.info(f"⛓️  BATTLE #{battle_count} DETECTED ON BLOCKCHAIN")
                    logger.info(f"   Block: {challenge.get('block_num')}")
                    logger.info(f"{'='*60}\n")
                    
                    # Now wait a moment for the battle to fully load on the server
                    logger.info("⏳ Waiting for Splinterlands server to process battle...")
                    time.sleep(2)
                    
                    # Try to detect and submit using API
                    success = run_single_battle()
                    
                    if success:
                        logger.info("✅ Battle handled successfully!")
                    else:
                        logger.warning("⚠️  Battle handling completed with issues")
                    
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(f"⚠️  Blockchain check error: {e}")
                time.sleep(check_interval)
    
    except KeyboardInterrupt:
        logger.info("\n\n👋 Bot stopped by user")
        logger.info(f"Total battles handled: {battle_count}")


def main():
    """Entry point for the bot"""
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--queue":
            # Browser automation mode - queue battles and submit teams
            check_interval = 30  # Default: queue every 30 seconds
            limit = None  # Default: unlimited
            
            # Parse remaining arguments
            for i in range(2, len(sys.argv)):
                if sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
                    try:
                        limit = int(sys.argv[i + 1])
                    except ValueError:
                        pass
                else:
                    try:
                        check_interval = int(sys.argv[i])
                    except ValueError:
                        pass
            
            run_queue_loop(check_interval=check_interval, limit=limit)
        
        elif sys.argv[1] == "--continuous":
            # Continuous monitoring mode (wait for battles)
            check_interval = 1  # Default: check every 1 second for faster detection
            limit = None  # Default: unlimited battles
            
            # Parse remaining arguments
            for i in range(2, len(sys.argv)):
                if sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
                    try:
                        limit = int(sys.argv[i + 1])
                    except ValueError:
                        pass
                else:
                    try:
                        check_interval = int(sys.argv[i])
                    except ValueError:
                        pass
            
            run_bot_loop(continuous=True, check_interval=check_interval, limit=limit)
        
        elif sys.argv[1] == "--blockchain":
            # Blockchain monitoring mode - monitor Hive chain for battles
            check_interval = 3  # Default: check blockchain every 3 seconds
            limit = None  # Default: unlimited battles
            
            # Parse remaining arguments
            for i in range(2, len(sys.argv)):
                if sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
                    try:
                        limit = int(sys.argv[i + 1])
                    except ValueError:
                        pass
                else:
                    try:
                        check_interval = int(sys.argv[i])
                    except ValueError:
                        pass
            
            run_blockchain_loop(check_interval=check_interval, limit=limit)
        
        else:
            print_usage()
    else:
        # Single run mode (default)
        try:
            result = run_bot_loop(continuous=False)
            if result:
                print("\n✅ Bot cycle completed successfully!")
            else:
                print("\n⚠️  Bot cycle completed with warnings")
        except KeyboardInterrupt:
            print("\n\n👋 Bot interrupted by user")
        except Exception as e:
            print(f"\n❌ Bot error: {e}")
            import traceback
            traceback.print_exc()


def print_usage():
    """Print usage information"""
    print("""
🤖 Splinterlands Wild Bot - Usage

Modes:
  python bot.py                            Single run - detect and submit one battle
  python bot.py --blockchain [N] [--limit M]  RECOMMENDED: Monitor Hive blockchain, N = check interval (default 3s)
  python bot.py --continuous [N] [--limit M]  Poll REST API for battles, N = interval (default 1s)
  python bot.py --queue [N] [--limit M]       Browser automation (experimental)

Examples:
  python bot.py                            Run single battle detection
  python bot.py --blockchain               Monitor blockchain indefinitely
  python bot.py --blockchain 5             Check blockchain every 5 seconds
  python bot.py --blockchain --limit 10    Submit max 10 battles then exit
  python bot.py --continuous               Poll API indefinitely (slower, unreliable)
  python bot.py --queue                    Browser automation (requires Brave + login)

RECOMMENDED: --blockchain mode
  • Monitors Hive blockchain for 'sm_challenge' operations
  • Detects when Splinterlands creates a battle for your account
  • Works completely unattended - no browser, no REST API limitations
  • Most reliable and simplest approach
  • Zero browser/extension/login requirements

REST API Polling (--continuous):
  • Polls /players/details every N seconds
  • Less reliable (API doesn't expose active battles)
  • Better for testing
  • Faster initial detection (1s intervals possible)

Browser Automation (--queue):
  • Monitors web UI for incoming battles
  • Auto-submits teams without clicking
  • Requires Brave browser + login

Universal:
  • Ctrl+C to stop any mode
  • Team submission works via REST API (uses HMAC-SHA256 with posting_key)
  • No Splinterlands API key required (uses blockchain + REST only)
    """)


if __name__ == "__main__":
    main()




