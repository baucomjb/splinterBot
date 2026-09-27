from splinterlands.game.card_pool import build_card_pool

def main():
    username = "tardigrade123"
    print(f"Loading card pool for {username}...\n")

    pool = build_card_pool(username)
    monsters = pool[0]
    summoners = pool[1]

    #print(f"Monsters: ")
    print((monsters.summary))
    #for m in monsters[:10]:
    #    print(m.summary(), "\n")

    #print(f"Summoners: {len(summoners)}")
    #for s in summoners:
    print((monsters.summary))
    #    print(s.summary())

if __name__ == "__main__":
    main()

