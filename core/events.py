# core/events.py

from enum import Enum, auto


class EventType(Enum):
    RED_FLAG = auto()
    RESTART_GRID_READY = auto()
    SAFETY_CAR_DEPLOYED = auto()
    SAFETY_CAR_IN_THIS_LAP = auto()
    VIRTUAL_SAFETY_CAR_DEPLOYED = auto()
    VSC_ENDING = auto()
    SC_VSC_STRATEGY_RECOMMENDATION = auto()
    FORMATION_LAP_START = auto()
    FORMATION_LAP_SECTOR3 = auto()
    RACE_START_GRID = auto()
    PIT_WINDOW_OPEN = auto()
    PIT_WINDOW_SECTOR3 = auto()
    PIT_DENIED_OR_SILENT = auto()
    SAFETY_OVERRIDE_REQUIRED = auto()
    STRATEGY_UPDATE_FROM_GAME = auto()
    TEAMMATE_PITTING = auto()
    START_FLYING_LAP = auto()
    FLYING_LAP_COMPLETED = auto()
    POSITION_LOST_IN_QUALI = auto()
    SESSION_TARGET_KNOWN = auto()
    WEATHER_UPDATE = auto()
    LAP_START = auto()
    RACE_WIN = auto()
    CONSTRUCTORS_CHAMPIONSHIP_WON = auto()
    DRIVERS_CHAMPIONSHIP_WON = auto()
    LAST_FIVE_LAPS = "last_five_laps"
    LAST_LAP = "last_lap"
    CROSSOVER_TO_INTERS = "crossover_to_inters"
    CROSSOVER_TO_SLICKS = "crossover_to_slicks"
    CROSSOVER_TO_FULL_WETS = "crossover_to_full_wets"
    DELTA_FREEZE_START = "delta_freeze_start"
    DELTA_FREEZE_END = "delta_freeze_end"
    IN_LAP = "in_lap"
    OUT_LAP = "out_lap"
    WEATHER_CHANGED = "weather_changed"
    TRACK_DRYING = "track_drying"
    TRACK_WORSENING = "track_worsening"
    FORECAST_WEATHER_CHANGE = "forecast_weather_change"
    FORECAST_RAIN_CHANGE = "forecast_rain_change"
    RAIN_SOON = "rain_soon"
    RAIN_ETA_UPDATE = "rain_eta_update"

