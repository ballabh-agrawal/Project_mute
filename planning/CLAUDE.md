# CLAUDE.md

Project: group-conversation accessibility tool (hackathon). Read the docs in `docs/` before writing code.

## Read order
1. Project Master Brief
2. Cross-Module Contract (wins for shared data: objects, messages, constants)
3. The module doc you are working on (Sync, Network, Server, Remaining Modules Spec)

If any document conflicts with the Server doc or final design.pdf, stop and ask before coding.

## Rules
- Build only what the specs say. If a spec looks wrong or incomplete, say so and ask before changing it.
- Write the tests first, then make them pass.
- Pass time and callbacks in as parameters so tests run without hardware.
- Modules talk to each other only through the interfaces in the contract.
- Never run model inference on the event loop.
- Record every decision and every spec change in DECISIONS.md (date, change, reason).
- Choose the simplest thing that works for a 15-minute demo. No production infrastructure.
- Do not copy the old prototype code (server.py, device_client.py, coordinator.py, sync_utils.py). It is outdated.
- Resolve the mismatches listed in section 8 of the Cross-Module Contract before coding the affected parts.

## Build order
1. Shared models and constants
2. Sync module (fake clock)
3. Network module
4. ASR benchmark, then the ASR worker
5. Server app (hub, queue, ASR worker, coordinator, storage)
6. Device pipeline (recorded audio first, then live mic)
7. TTS and the reply path
8. UI, then integration on the demo network

A step is finished only when its tests pass.

## Out of scope
Emotion layer, multiple sessions, multiple deaf users, smart glasses, login and encryption, audio compression.

## Style
Python, type hints, small files, no extra features.
