# Saul — AI F1 Co-Driver & Assistant

A Personal AI Assistant that works as an assistant, and as a race engineer for F1 25.

## Modes

| Mode | Trigger | Description |
|------|---------|-------------|
| **AIMode** | Default | Snarky AI assistant. Ollama LLM + streaming + TTS. Animations: listen → think → talk → idle |
| **F1Mode** | F1 25 unpaused, game running | Garage mode. R&D recommendations + practice program selection. No LLM, all pre-cached TTS |
| **F1EngineerMode** | F1 25 paused | Race engineer. Radio calls on all 60 events, gap calls every lap, DRS/ERS automation, MFD navigation |

## Tech Stack

- **TTS**: XTTS v2 with `saul.wav` voice profile, all 573 lines pre-cached on disk (~8s/synthesis first run, instant subsequent runs)
- **LLM**: Ollama (`llama3.2:1b`) via `http://localhost:11434`, streaming, response caching by prompt hash
- **Animation sync**: Audio triggers "talk" animation at exact playback moment — no lag
- **Video**: Tkinter Toplevel, 640×720, bottom-right, transparent black = invisible, always-on-top, borderless
- **UDP**: F1 25 telemetry, 50ms polling thread, all 9 F1 managers wired
- **ERS/DRS**: Auto DRS always, ERS auto per race/qual conditions, ERS=None in ERS Management practice only
- **Pit confirmation**: Via text command — type `confirm` in pause menu

## Keyboard Bindings (in-game)

| Key | Action |
|-----|--------|
| F9 | DRS auto |
| F10 | ERS Overtake |
| F11 | ERS Cycle Left |
| F8 | ERS Cycle Right |
| Numpad 8/2/4/6 | MFD Navigation |
| Enter | MFD Confirm |
| Numpad 0 | Open MFD |

## Controls

- Type in text box to interact with any mode
- `confirm` in pause menu = pit stop confirmation + MFD navigation
- Gamepad button mapped to Insert = not currently working (Steam Input bypasses keyboard hooks)
- Pause F1 25 → Engineer Mode, text box appears

## Architecture

```
saul_app.py
├── AIRoot (mode manager, LLM pre-warm)
├── AudioVideoManager (audio queue + video player)
├── TTSCache (XTTS v2, pre-cached, on-demand synthesis)
├── LLMClient (Ollama streaming + text cache)
├── TelemetryManager (UDP 50ms thread)
│   ├── SafetyManager (SC/VSC detection)
│   ├── SessionManager (session type, garage detection)
│   ├── RaceBehavior (pit calls, SC gap suppression)
│   ├── QualifyingBehavior (cutoff tracking)
│   ├── OnTrackManager (lap events, pace calls)
│   ├── WeatherManager (forecast + rain events)
│   ├── PitBehavior (pit timing, limiter reminder)
│   ├── TeammateManager (teammate pitting)
│   └── LapTracker (gap calculations)
├── ERSDRSManager (DRS/ERS automation 50ms thread)
├── EventRouter (priority queue, 60 events → 75+ handlers)
├── ModeManager (auto-switch AI/F1/Engineer)
├── CareerTracker (year, series, warmth)
└── ResponseBrain (LLM routing for AIMode only)
```

## TTS Cache

573 lines on disk in `assets/voices/cache/`:
- 427 original radio lines
- 145 F1Mode lines (R&D + practice programs)
- Instant load every startup

## Career Warmth Tiers

| Tier | Range | AIMode Personality |
|------|-------|-------------------|
| Sharp | 0-2 | Maximum edge, blunt, no softening |
| Professional | 3-5 | Focused, direct, bite when needed |
| Supportive | 6-8 | Warmer, collaborative, still pushy |
| Partnership | 9-10 | Invested, loyal, stubborn for your good |

## F1Mode Practice Programs

6 validated programs (strict — invalid input asks "Which program?"):
- Track Acclimatisation
- Tyre Management
- Fuel Management
- ERS Management (sets ERS=None, pauses automation)
- Qualifying Simulation
- Race Strategy

## R&D Categories

4 categories — you can't work on what your teammate is on:
- Aero, Powertrain, Chassis, Durability

## Known Issues

- Insert key not working (Steam Input bypasses global keyboard hooks)
- No LLM context for F1Mode (intentional — deterministic responses)
- AIMode LLM requires Ollama running at `localhost:11434`

## Dependencies

```
ollama pull llama3.2:1b
pip install pywin32
```
