# SD Craft TrainCarts setup

## Installed and verified

- TrainCarts 2.0.5 build 1787
- BKCommonLib 2.0.6 build 2110 (required dependency)
- Paper 26.3 build 255 / Java 25
- Vault economy hook: `SDCraftCore` / SD Craft Wallet

The disposable full-server boot reached `Done` with 22 plugins. The console
command `train version` reported both plugin builds and Paper 26.3. The files
in `config/Train_Carts/config.yml` and `config/BKCommonLib/config.yml` are the
tested low-memory profile.

## Honest current state

Installation does not create rails or stations. This package currently has no
physical TrainCarts line, no saved train model, and no automated route. The
existing `/sdc ride metro ...` feature remains a fare-and-teleport simulation
until a real line is built and connected deliberately.

## First staging loop

1. Work only in a disposable copy of `world`, never the only live world.
2. Build a short powered-rail loop with safe platforms and barriers.
3. Place a TrainCarts minecart or use `/train chest [name]` for a saved train.
4. Put a station action sign by the rail using four lines:

       [train]
       station
       5
       continue

5. Use redstone as described in the official station-sign documentation. Test
   stopping, the five-second wait, launch direction, boarding, and ejection.
6. Restart the server and confirm the train persists and the route recovers.
7. Run `train version`, `plugins`, `sdc status`, and a five-minute Spark/TPS
   sample while two players ride and the NPC population is active.

## SD Craft production rules

- Leave per-train `keepChunksLoaded` disabled at first. It turns trains into
  moving chunk loaders and can exceed the 3.5 GB host budget.
- Do not expose TrainCarts editing, spawn signs, schematic attachments, or
  unlimited selectors to ordinary players. Assign builder permissions through
  LuckPerms only to trusted staff.
- Use the existing SD Craft Wallet for future fares. Do not install a second
  ticket-shop economy until it declares Paper 26.3 support and the ledger flow
  is integration-tested.
- Keep trains to eight carts or fewer and no more than 80 carts in `world`.
- Add TC-Coasters only if the final design actually needs free-form rails. It
  is not required for a normal metro and is not part of this tested package.

Official references:

- <https://modrinth.com/plugin/traincarts>
- <https://modrinth.com/plugin/bkcommonlib>
- <https://wiki.traincarts.net/p/TrainCarts>
- <https://wiki.traincarts.net/p/TrainCarts/Signs/Station>
