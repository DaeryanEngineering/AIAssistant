# core/event_router.py

from .events import EventType


class EventRouter:
    def __init__(self, engineer_brain):
        self.engineer_brain = engineer_brain

    def handle_event(self, event_type: EventType, **payload):
        mapping = {
            EventType.RED_FLAG: self.engineer_brain.handle_red_flag,
            EventType.RESTART_GRID_READY: self.engineer_brain.handle_red_flag_restart,
            EventType.DELTA_FREEZE_START: self.engineer_brain.handle_delta_freeze_start,
            EventType.DELTA_FREEZE_END: self.engineer_brain.handle_delta_freeze_end,
            EventType.OUT_LAP: self.engineer_brain.handle_out_lap,
            EventType.IN_LAP: self.engineer_brain.handle_in_lap,
            EventType.SAFETY_CAR_DEPLOYED: self.engineer_brain.handle_sc_start,
            EventType.SAFETY_CAR_IN_THIS_LAP: self.engineer_brain.handle_sc_restart,
            EventType.VIRTUAL_SAFETY_CAR_DEPLOYED: self.engineer_brain.handle_vsc_start,
            EventType.VSC_ENDING: self.engineer_brain.handle_vsc_end,
            EventType.CROSSOVER_TO_INTERS: self.engineer_brain.handle_crossover_to_inters,
            EventType.CROSSOVER_TO_SLICKS: self.engineer_brain.handle_crossover_to_slicks,
            EventType.CROSSOVER_TO_FULL_WETS: self.engineer_brain.handle_crossover_to_full_wets,
            EventType.SC_VSC_STRATEGY_RECOMMENDATION: self.engineer_brain.handle_sc_vsc_pit_recommendation,
            EventType.FORMATION_LAP_START: self.engineer_brain.handle_formation_lap,
            EventType.FORMATION_LAP_SECTOR3: self.engineer_brain.handle_find_grid_slot,
            EventType.RACE_START_GRID: self.engineer_brain.handle_race_start,
            EventType.PIT_WINDOW_OPEN: self.engineer_brain.handle_pit_window,
            EventType.PIT_WINDOW_SECTOR3: self.engineer_brain.handle_pit_reminder,
            EventType.PIT_DENIED_OR_SILENT: self.engineer_brain.handle_extend_stint,
            EventType.SAFETY_OVERRIDE_REQUIRED: self.engineer_brain.handle_safety_override,
            EventType.STRATEGY_UPDATE_FROM_GAME: self.engineer_brain.handle_strategy_update,
            EventType.TEAMMATE_PITTING: self.engineer_brain.handle_teammate_pit,
            EventType.START_FLYING_LAP: self.engineer_brain.handle_quali_push_start,
            EventType.FLYING_LAP_COMPLETED: self.engineer_brain.handle_quali_lap_end,
            EventType.POSITION_LOST_IN_QUALI: self.engineer_brain.handle_quali_position_loss,
            EventType.SESSION_TARGET_KNOWN: self.engineer_brain.handle_quali_target,
            EventType.WEATHER_UPDATE: self.engineer_brain.handle_weather_update,
            EventType.LAP_START: self.engineer_brain.handle_gap_report,
            EventType.LAST_FIVE_LAPS: self.engineer_brain.handle_last_five_laps,
            EventType.LAST_LAP: self.engineer_brain.handle_last_lap,
            EventType.RACE_WIN: self.engineer_brain.handle_race_win,
            EventType.CONSTRUCTORS_CHAMPIONSHIP_WON: self.engineer_brain.handle_constructors_title,
            EventType.DRIVERS_CHAMPIONSHIP_WON: self.engineer_brain.handle_drivers_title,
        }

        handler = mapping.get(event_type)
        if handler:
            handler(**payload)

