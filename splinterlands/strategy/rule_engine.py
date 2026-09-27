"""
Strategy engine for selecting teams based on battle conditions.
Currently implements Water splinter bot for wild battles.
"""
from typing import List, Optional, Tuple
from splinterlands.game.card import Card
from splinterlands.game.summoner_constraints import get_constraints
from splinterlands.game.summoner_abilities import get_summoner_abilities_loader
import os
from datetime import datetime


class TeamSelectionLogger:
    """Logs team selection decisions to both console and file"""
    
    def __init__(self, enable_file_logging: bool = True):
        self.enable_file_logging = enable_file_logging
        self.logs = []
        self.log_dir = "logs"
        self.ensure_log_dir()
    
    def ensure_log_dir(self):
        """Create logs directory if it doesn't exist"""
        if self.enable_file_logging and not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def log(self, message: str, print_to_console: bool = True):
        """Log message to both console and file"""
        self.logs.append(message)
        if print_to_console:
            print(message)
    
    def save(self, filename: str = None):
        """Save logs to file"""
        if not self.enable_file_logging:
            return
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"team_selection_{timestamp}.log"
        
        filepath = os.path.join(self.log_dir, filename)
        with open(filepath, 'w') as f:
            f.write("\n".join(self.logs))
        
        return filepath



import os
from datetime import datetime


class WaterBot:
    """Water splinter focused strategy for wild battles"""
    
    WATER_COLOR = "Blue"
    
    # Map between splinter names and card colors
    SPLINTER_TO_COLOR = {
        'Water': 'Blue',
        'Fire': 'Red',
        'Earth': 'Green',
        'Life': 'White',
        'Death': 'Black',
        'Dragon': 'Dragon'
    }
    
    @staticmethod
    def _normalize_splinters(splinter_list):
        """Convert splinter names to card color names"""
        return [WaterBot.SPLINTER_TO_COLOR.get(s, s) for s in splinter_list]
    
    @staticmethod
    def _is_card_water_compatible(card: Card) -> bool:
        """
        Check if a card (especially summoner) is water-compatible.
        Handles multi-color summoners by checking constraints file.
        """
        # Check main color
        if card.color == WaterBot.WATER_COLOR:
            return True
        
        # For summoners, check if they have Blue in their color list
        if card.type == "Summoner":
            constraints = get_constraints()
            # Check if this summoner has Blue in its color options
            if hasattr(constraints, '_constraints') and constraints._constraints:
                for section in constraints._constraints.get('summoners', {}).values():
                    if isinstance(section, dict) and card.name in section:
                        colors = section[card.name].get('colors', [])
                        if isinstance(colors, list) and WaterBot.WATER_COLOR in colors:
                            return True
        
        return False
    
    @staticmethod
    def _get_summoner_colors(summoner: Card) -> List[str]:
        """
        Get all color options for a summoner from constraints file.
        Handles multi-color summoners.
        Returns a list of colors (e.g., ['White', 'Blue'] or ['Blue']).
        Defaults to summoner's card color if not found in constraints.
        """
        constraints = get_constraints()
        if hasattr(constraints, '_constraints') and constraints._constraints:
            for section in constraints._constraints.get('summoners', {}).values():
                if isinstance(section, dict) and summoner.name in section:
                    colors = section[summoner.name].get('colors', [])
                    if isinstance(colors, list) and len(colors) > 0:
                        return colors
        
        # Fallback to card's single color
        return [summoner.color] if summoner.color else []
    
    @staticmethod
    def filter_water_cards(pool: List[Card]) -> List[Card]:
        """
        Filter card pool to water splinter only cards.
        Water splinter is identified by Blue color.
        Includes multi-color summoners that have Blue as one of their options.
        """
        water_cards = []
        for card in pool:
            if WaterBot._is_card_water_compatible(card):
                water_cards.append(card)
        return water_cards
    
    @staticmethod
    def select_summoner(available: List[Card]) -> Optional[Card]:
        """Select the best summoner from available water cards"""
        summoners = [c for c in available if c.type == "Summoner"]
        if not summoners:
            return None
        
        # Filter out disabled summoners
        constraints = get_constraints()
        enabled_summoners = [s for s in summoners if not constraints.is_summoner_disabled(s.name)]
        
        # If no enabled summoners, fallback to any available summoner
        candidates = enabled_summoners if enabled_summoners else summoners
        
        # Prefer higher level summoners
        return max(candidates, key=lambda c: c.level)
    
    @staticmethod
    def _get_effective_monster_level(summoner: Card, monster: Card) -> int:
        """
        Calculate the effective level a monster will be at when summoned.
        If monster level exceeds summoner's constraint, it's downleveled.
        """
        constraints = get_constraints()
        max_level = constraints.get_max_monster_level(
            summoner.name,
            summoner.level,
            monster.rarity
        )
        
        # If no constraint found, monster stays at its level
        if max_level is None:
            return monster.level
        
        # Return whichever is lower - actual level or max allowed
        return min(monster.level, max_level)

    @staticmethod
    def select_monsters(
        available: List[Card],
        summoner: Card,
        mana_cap: int,
        rulesets: List[str],
        num_slots: int = 5,
        logger = None,
        valid_colors = None
    ) -> List[Card]:
        """
        Select monsters for team composition based on:
        - Mana constraints (using actual mana costs from card stats)
        - Rulesets (e.g., "Melee Only", "Armor Up", etc.)
        - Summoner level constraints (monsters may be downleveled per summoner)
        - Available card slots
        
        Strategy: Prefer defensive cards (high armor+health) first,
        then fill remaining mana with efficient cards.
        
        Note: Cards are NOT filtered by summoner level constraints. Instead,
        cards that exceed summoner level limits are downleveled when summoned.
        
        Args:
            available: List of available monster cards
            summoner: The summoner card being used
            mana_cap: Total mana budget
            rulesets: List of active battle rulesets
            num_slots: Max card slots to fill (usually 5)
            logger: Optional TeamSelectionLogger for detailed logging
        
        Returns:
            List of selected monster Cards for slots 1-5
        """
        monsters = [c for c in available if c.type == "Monster"]
        if not monsters:
            return []
        
        # Filter based on rulesets only
        monsters = WaterBot._apply_ruleset_filters(monsters, rulesets)
        if not monsters:
            return []
        
        # Filter by summoner's allowed colors (if multi-color, accept any of them)
        summoner_colors = WaterBot._get_summoner_colors(summoner)
        
        # Use valid_colors if provided (handles Dragon summoners that can use multiple splinter colors)
        colors_to_check = valid_colors if valid_colors else set(summoner_colors)
        
        if colors_to_check:
            # Prefer cards matching summoner colors, but allow Gray (neutral) as fallback
            monsters_by_color = [m for m in monsters if m.color in colors_to_check]
            # If no exact color matches, fall back to including Gray cards
            if not monsters_by_color:
                monsters_by_color = [m for m in monsters if m.color == 'Gray' or m.color in colors_to_check]
        else:
            monsters_by_color = monsters
        
        # Account for summoner mana cost
        summoner_mana = WaterBot._get_estimated_mana_cost(summoner)
        remaining_mana = mana_cap - summoner_mana
        
        if remaining_mana < 0:
            if logger:
                logger.log(f"\n❌ Summoner costs {summoner_mana} mana, exceeds cap of {mana_cap}!", print_to_console=True)
            return []
        
        # Sort by defense priority (armor+health), then by level
        # We prefer tough defensive cards to survive longer
        monsters_by_defense = sorted(
            monsters_by_color,
            key=lambda c: (
                -(c.stats.armor + c.stats.health),  # Higher defense = better
                -c.level,  # Higher level preferred
                c.stats.health  # Tiebreaker: health
            )
        )
        
        selected = []
        
        # Greedy selection: pick best defensive card that fits mana
        for card in monsters_by_defense:
            mana_cost = WaterBot._get_estimated_mana_cost(card)
            
            if mana_cost <= remaining_mana and len(selected) < num_slots:
                selected.append(card)
                remaining_mana -= mana_cost
        
        return selected
    
    @staticmethod
    def _apply_ruleset_filters(cards: List[Card], rulesets: List[str]) -> List[Card]:
        """Filter cards based on active rulesets"""
        result = cards
        
        for ruleset in rulesets:
            if "Melee Only" in ruleset:
                # Only keep cards with melee attack
                result = [c for c in result if c.stats.melee > 0]
            elif "Ranged Only" in ruleset:
                # Only keep ranged/magic cards
                result = [c for c in result if c.stats.ranged > 0 or c.stats.magic > 0]
            elif "Magic Only" in ruleset:
                # Only keep magic cards  
                result = [c for c in result if c.stats.magic > 0]
            elif "Lost Legendaries" in ruleset:
                # Exclude legendary cards (rarity 4)
                result = [c for c in result if c.rarity != 4]
            elif "Lost Epics" in ruleset:
                # Exclude epic cards (rarity 3)
                result = [c for c in result if c.rarity != 3]
            elif "Lost Rares" in ruleset:
                # Exclude rare cards (rarity 2)
                result = [c for c in result if c.rarity != 2]
        
        return result
    
    @staticmethod
    def _get_estimated_mana_cost(card: Card) -> int:
        """
        Get the actual mana cost of a card from its stats.
        Falls back to estimation if mana is not in stats.
        """
        # Try to use real mana cost from card stats
        if card.stats.mana > 0:
            return card.stats.mana
        
        # Fallback: estimate based on rarity
        base_costs = {
            1: 2,   # common
            2: 4,   # rare
            3: 6,   # epic
            4: 8,   # legendary
            5: 10,  # premium (if exists)
        }
        
        rarity = card.rarity or 1
        return base_costs.get(rarity, 2)
    
    @staticmethod
    def _format_card_details(card: Card) -> str:
        """
        Format card details for logging including all stats and abilities.
        Shows: Attack (type), HP/Armor, Speed, Abilities, Rarity
        """
        # Attack type and value
        attack_str = ""
        if card.stats.melee > 0:
            attack_str = f"Melee {card.stats.melee}"
        elif card.stats.ranged > 0:
            attack_str = f"Ranged {card.stats.ranged}"
        elif card.stats.magic > 0:
            attack_str = f"Magic {card.stats.magic}"
        else:
            attack_str = "No Attack"
        
        # Health and armor
        hp_armor = f"HP {card.stats.health} Armor {card.stats.armor}"
        
        # Speed
        speed = f"Spd {card.stats.speed}"
        
        # Abilities
        abilities_str = ", ".join(card.abilities) if card.abilities else "None"
        
        # Rarity name
        rarity_names = {1: "Common", 2: "Rare", 3: "Epic", 4: "Legendary"}
        rarity_name = rarity_names.get(card.rarity, f"Rarity{card.rarity}")
        
        return f"{attack_str} | {hp_armor} | {speed} | Abilities: [{abilities_str}] | {rarity_name}"


def choose_team(battle_state, card_pool: List[Card], verbose: bool = True, save_log: bool = True) -> Optional[Tuple]:
    """
    Main strategy function to select a team for battle.
    Logs all selection criteria and decisions.
    
    Args:
        battle_state: BattleState object with mana_cap, rulesets, allowed_splinters
        card_pool: List[Card] of available player cards
        verbose: If True, print detailed selection logs to console
        save_log: If True, save logs to file in logs/ directory
    
    Returns:
        Tuple of (summoner_card, [monster_cards]) or None if no valid team possible
    """
    logger = TeamSelectionLogger(enable_file_logging=save_log)
    
    logger.log("\n" + "="*60, verbose)
    logger.log("🔥 WATER BOT TEAM SELECTION", verbose)
    logger.log("="*60, verbose)
    logger.log(f"\nBattle Conditions:", verbose)
    logger.log(f"  Mana Cap: {battle_state.mana_cap}", verbose)
    logger.log(f"  Rulesets: {battle_state.rulesets if battle_state.rulesets else 'None'}", verbose)
    logger.log(f"  Allowed Splinters: {battle_state.allowed_splinters}", verbose)
    logger.log(f"  Card Pool Size: {len(card_pool)} total cards", verbose)
    
    # Get all available summoners (including multi-color ones)
    all_summoners = [c for c in card_pool if c.type == "Summoner"]
    if not all_summoners:
        logger.log(f"\n❌ No summoners in pool!", verbose)
        logger.save()
        return None
    
    # Normalize splinter names to card colors
    allowed_colors = WaterBot._normalize_splinters(battle_state.allowed_splinters)
    
    # Filter summoners to ones with at least one allowed splinter color
    constraints = get_constraints()
    available_summoners = []
    
    for summoner in all_summoners:
        # Skip disabled summoners
        if constraints.is_summoner_disabled(summoner.name):
            continue
        
        # Check if any of this summoner's colors are allowed
        summoner_colors = WaterBot._get_summoner_colors(summoner)
        matching_colors = [c for c in summoner_colors if c in allowed_colors]
        
        if matching_colors:
            available_summoners.append(summoner)
    
    if not available_summoners:
        logger.log(f"\n❌ No summoners with allowed splinter colors!", verbose)
        logger.save()
        return None
    
    # Sort by power level: Legendary > Epic > Rare > Common, then by level
    # Prefer summoners whose colors match the allowed splinters
    def summoner_priority(summoner):
        summoner_colors = WaterBot._get_summoner_colors(summoner)
        matching_colors = [c for c in summoner_colors if c in allowed_colors]
        
        # Prefer summoners that have colors in the allowed list
        has_allowed_color = 1 if matching_colors else 0
        num_allowed_colors = len(matching_colors)  # Tiebreaker: more colors = more flexibility
        
        # Rarity priority (4=Legendary is highest)
        rarity_priority = {1: 0, 2: 1, 3: 2, 4: 3}
        
        return (
            -has_allowed_color,  # Negate to prefer matching colors
            -rarity_priority.get(summoner.rarity, 0),  # Negate for descending
            -summoner.level,  # Negate for descending
            -num_allowed_colors  # Negate to prefer more color options
        )
    
    summoner = min(available_summoners, key=summoner_priority)
    
    if not summoner:
        logger.log(f"❌ No suitable summoner found!", verbose)
        logger.save()
        return None
    
    logger.log(f"\n✅ Selected Summoner: {summoner.name} (Lvl {summoner.level})", verbose)
    summoner_details = WaterBot._format_card_details(summoner)
    logger.log(f"   Details: {summoner_details}", verbose)
    summoner_colors = WaterBot._get_summoner_colors(summoner)
    logger.log(f"   Splinter Colors: {', '.join(summoner_colors)}", verbose)
    
    # Determine valid monster colors for this summoner
    # Dragon summoners can use Dragon + any available splinter colors
    if 'Dragon' in summoner_colors:
        valid_colors = set(summoner_colors) | set(allowed_colors)  # Dragon + all allowed colors
        logger.log(f"   (Dragon summoner - can use Dragon + available splinters: {', '.join(sorted(valid_colors))})", verbose)
    else:
        valid_colors = set(summoner_colors)
    
    # Get available monsters for this summoner's colors
    summoner_monsters = [c for c in card_pool if c.type == "Monster" and 
                         (c.color in valid_colors or c.color == 'Gray')]
    
    if not summoner_monsters:
        logger.log(f"❌ No monsters available for summoner's splinters!", verbose)
        logger.save()
        return None
    
    logger.log(f"✅ Found {len(summoner_monsters)} available monsters for summoner", verbose)
    
    # Show summoner abilities (team buffs)
    abilities_loader = get_summoner_abilities_loader()
    summoner_abilities = abilities_loader.get_summoner_abilities(summoner.name)
    if summoner_abilities:
        logger.log(f"   Team Buffs:", verbose)
        for ability in summoner_abilities:
            logger.log(f"     • {ability}", verbose)
    
    # Show Pallando options if available
    summoner_pallando = abilities_loader.get_summoner_pallando_options(summoner.name)
    if summoner_pallando:
        logger.log(f"   Pallando Options:", verbose)
        for option in summoner_pallando:
            desc = option.get('description', '')
            logger.log(f"     • {desc}", verbose)
    
    # Select monsters from available pool
    monsters = WaterBot.select_monsters(
        summoner_monsters,
        summoner,
        battle_state.mana_cap,
        battle_state.rulesets,
        logger=logger,
        valid_colors=valid_colors
    )
    
    if not monsters:
        logger.log(f"❌ Could not select any monsters!", verbose)
        logger.save()
        return None
    
    summoner_mana = WaterBot._get_estimated_mana_cost(summoner)
    total_monster_mana = sum(WaterBot._get_estimated_mana_cost(m) for m in monsters)
    total_mana = summoner_mana + total_monster_mana
    
    logger.log(f"\n✅ Selected {len(monsters)} Monsters (Mana: {summoner_mana} summoner + {total_monster_mana} monsters = {total_mana}/{battle_state.mana_cap}):", verbose)
    logger.log(f"   Selection criteria: High defense (armor+health), effective levels per summoner constraints", verbose)
    for i, m in enumerate(monsters, 1):
        mana = WaterBot._get_estimated_mana_cost(m)
        defense = m.stats.armor + m.stats.health
        
        # Calculate effective level (considering summoner constraints)
        effective_level = WaterBot._get_effective_monster_level(summoner, m)
        
        # Get abilities at effective level if downleveled
        if m.level == effective_level:
            level_str = f"Lvl {m.level}"
            abilities = m.abilities
        else:
            level_str = f"L{m.level}→L{effective_level}"
            abilities = m.get_abilities_at_level(effective_level)
        
        # Format card details with correct abilities
        abilities_str = ", ".join(abilities) if abilities else "None"
        attack_str = f"Melee {m.stats.melee}" if m.stats.melee > 0 else (
            f"Ranged {m.stats.ranged}" if m.stats.ranged > 0 else (
                f"Magic {m.stats.magic}" if m.stats.magic > 0 else "No Attack"
            )
        )
        hp_armor = f"HP {m.stats.health} Armor {m.stats.armor}"
        speed = f"Spd {m.stats.speed}"
        
        rarity_names = {1: "Common", 2: "Rare", 3: "Epic", 4: "Legendary"}
        rarity_name = rarity_names.get(m.rarity, f"Rarity{m.rarity}")
        
        card_details = f"{attack_str} | {hp_armor} | {speed} | Abilities: [{abilities_str}] | {rarity_name}"
        
        logger.log(f"   {i}. {m.name} ({level_str})", verbose)
        logger.log(f"      Mana: {mana} | Defense: {defense} | {card_details}", verbose)
    
    logger.log("="*60 + "\n", verbose)
    
    # Save logs to file
    if save_log:
        filepath = logger.save()
        if filepath:
            logger.log(f"📝 Selection log saved to: {filepath}", verbose)
    
    return (summoner, monsters)


