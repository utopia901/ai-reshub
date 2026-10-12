# AI ResHub · Reading Room

A read-only mirror of a personal AI research hub, for reading at home. Content is synced daily from the hub: kept papers, learning sessions and headlines. Nothing here can be edited from the page.

- `index.html`: the page (generated from the hub's design; don't edit by hand).
- `data/`: the content, rewritten by the daily sync.
- `scripts/build_data.py`: turns a hub export into `data/`, keeping only whitelisted fields.
- `scripts/publish.sh`: commits `data/` and refuses if anything else changed.
