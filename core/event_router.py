# core/event_router.py

import queue
import threading

from .events import EventType


# Events that clear the queue before processing (safety-critical)
PRIORITY_EVENTS = {
    EventType.RED_FLAG,
    EventType.RESTART_GRID_READY,
    EventType.FORMATION_LAP_START,
    EventType.RACE_START_GRID,
    EventType.SAFETY_CAR_DEPLOYED,
    EventType.SAFETY_CAR_IN_THIS_LAP,
    EventType.VIRTUAL_SAFETY_CAR_DEPLOYED,
    EventType.RACE_WIN,
    EventType.PIT_LIMITER_REMINDER,
    EventType.PIT_STOP_QUALITY,
    EventType.RACE_FINISH,
    EventType.CONSTRUCTORS_CHAMPIONSHIP_WON,
    EventType.DRIVERS_CHAMPIONSHIP_WON,
}


class EventRouter:
    def __init__(self, engineer_brain):
        self.engineer_brain = engineer_brain
        self._queue: queue.Queue = queue.Queue()
        self._running = True
        self._init_mapping()
        self._thread = threading.Thread(target=self._worker, daemon=True, name="EventRouter")
        self._thread.start()

    def _worker(self):
        while self._running:
            try:
                item = self._queue.get(timeout=0.05)
                if item is None:
                    continue
                event_type, payload = item
                if event_type is None:
                    continue

                if event_type in PRIORITY_EVENTS:
                    while not self._queue.empty():
                        try:
                            self._queue.get_nowait()
                        except queue.Empty:
                            break

                handler = self._mapping.get(event_type)
                if handler:
                    handler(**payload)
            except queue.Empty:
                continue
            except Exception:
                continue

    def handle_event(self, event_type: EventType, **payload):
        self._queue.put((event_type, payload))

    def stop(self):
        self._running = False
        self._queue.put((None, None))
        if self._thread.is_alive():
            self._thread.join(timeout=2)

    def _init_mapping(self):
        self._mapping = {
            # Priority events
            EventType.RED_FLAG: self.engineer_brain.handle_red_flag,
            EventType.RESTART_GRID_READY: self.engineer_brain.handle_red_flag_restart,
            EventType.FORMATION_LAP_START: self.engineer_brain.handle_formation_lap,
            EventType.FORMATION_LAP_SECTOR3: self.engineer_brain.handle_find_grid_slot,
            EventType.RACE_START_GRID: self.engineer_brain.handle_race_start,
            EventType.SAFETY_CAR_DEPLOYED: self.engineer_brain.handle_sc_start,
            EventType.SAFETY_CAR_IN_THIS_LAP: self.engineer_brain.handle_sc_restart,
            EventType.VIRTUAL_SAFETY_CAR_DEPLOYED: self.engineer_brain.handle_vsc_start,
            EventType.RACE_WIN: self.engineer_brain.handle_race_win,
            EventType.CONSTRUCTORS_CHAMPIONSHIP_WON: self.engineer_brain.handle_constructors_title,
            EventType.DRIVERS_CHAMPIONSHIP_WON: self.engineer_brain.handle_drivers_title,
            # Session events
            EventType.SESSION_START: self.engineer_brain.handle_session_start,
            EventType.SESSION_END: self.engineer_brain.handle_session_end,
            EventType.SESSION_TYPE_CHANGED: self.engineer_brain.handle_session_type_changed,
            # Safety / delta
            EventType.SAFETY_CAR_END: self.engineer_brain.handle_sc_end,
            EventType.VSC_END: self.engineer_brain.handle_vsc_end,
            EventType.VSC_ENDING: self.engineer_brain.handle_vsc_end,
            EventType.DELTA_FREEZE_START: self.engineer_brain.handle_delta_freeze_start,
            EventType.DELTA_FREEZE_END: self.engineer_brain.handle_delta_freeze_end,
            # Pit events
            EventType.PIT_LIMITER_REMINDER: self.engineer_brain.handle_pit_limiter_reminder,
            EventType.PIT_STOP_QUALITY: self.engineer_brain.handle_pit_stop_quality,
            # Lap / race
            EventType.LAP_START: self.engineer_brain.handle_lap_start,
            EventType.RACE_GAP: self.engineer_brain.handle_gap_report,
            EventType.RACE_FINISH: self.engineer_brain.handle_race_finish,
            EventType.LAST_FIVE_LAPS: self.engineer_brain.handle_last_five_laps,
            EventType.LAST_LAP: self.engineer_brain.handle_last_lap,
            # Lap invalidated
            EventType.LAP_INVALIDATED: self.engineer_brain.handle_lap_invalidated,
            # Garage
            EventType.GARAGE_ENTERED: self.engineer_brain.handle_garage_entered,
            EventType.GARAGE_EXITED: self.engineer_brain.handle_garage_exited,
            # Teammate
            EventType.TEAMMATE_PITTING: self.engineer_brain.handle_teammate_pit,
            EventType.TEAMMATE_DNF: self.engineer_brain.handle_teammate_dnf,
            # Weather
            EventType.WEATHER_UPDATE: self.engineer_brain.handle_weather_update,
            EventType.WEATHER_CHANGED: self.engineer_brain.handle_weather_changed,
            EventType.TRACK_DRYING: self.engineer_brain.handle_track_drying,
            EventType.TRACK_WORSENING: self.engineer_brain.handle_track_worsening,
            EventType.RAIN_SOON: self.engineer_brain.handle_rain_soon,
            # Crossover
            EventType.CROSSOVER_TO_INTERS: self.engineer_brain.handle_crossover_to_inters,
            EventType.CROSSOVER_TO_SLICKS: self.engineer_brain.handle_crossover_to_slicks,
            EventType.CROSSOVER_TO_FULL_WETS: self.engineer_brain.handle_crossover_to_full_wets,
            # Pit window / strategy
            EventType.PIT_WINDOW_OPEN: self.engineer_brain.handle_pit_window,
            EventType.PIT_WINDOW_SECTOR3: self.engineer_brain.handle_pit_reminder,
            EventType.PIT_DENIED_OR_SILENT: self.engineer_brain.handle_extend_stint,
            EventType.SAFETY_OVERRIDE_REQUIRED: self.engineer_brain.handle_safety_override,
            EventType.STRATEGY_UPDATE_FROM_GAME: self.engineer_brain.handle_strategy_update,
            EventType.SC_VSC_STRATEGY_RECOMMENDATION: self.engineer_brain.handle_sc_vsc_pit_recommendation,
            # Qualifying
            EventType.START_FLYING_LAP: self.engineer_brain.handle_quali_push_start,
            EventType.FLYING_LAP_COMPLETED: self.engineer_brain.handle_quali_lap_end,
            EventType.POSITION_LOST_IN_QUALI: self.engineer_brain.handle_quali_position_loss,
            EventType.SESSION_TARGET_KNOWN: self.engineer_brain.handle_quali_target,
            EventType.QUALI_PROVISIONAL_POLE: self.engineer_brain.handle_quali_provisional_pole,
            EventType.QUALI_GOAL: self.engineer_brain.handle_quali_goal,
            EventType.QUALI_FINAL_POLE: self.engineer_brain.handle_quali_final_pole,
            EventType.QUALI_RECOMMEND_GO_BACK_OUT: self.engineer_brain.handle_quali_go_back_out,
            EventType.QUALI_LAP_COMPLETE_VALID: self.engineer_brain.handle_quali_lap_complete_valid,
            EventType.QUALI_LAP_COMPLETE_INVALID: self.engineer_brain.handle_quali_lap_complete_invalid,
            EventType.QUALI_POSITION_UPDATE: self.engineer_brain.handle_quali_position_update,
            EventType.QUALI_POSITION_LOST: self.engineer_brain.handle_quali_position_loss,
            # In/out laps
            EventType.OUT_LAP: self.engineer_brain.handle_out_lap,
            EventType.IN_LAP: self.engineer_brain.handle_in_lap,
            # Pit entry / exit
            EventType.PIT_ENTRY: self.engineer_brain.handle_pit_entry,
            EventType.PIT_EXIT: self.engineer_brain.handle_pit_exit,
            # Pit limiter
            EventType.PIT_LIMITER_ON: self.engineer_brain.handle_pit_limiter_on,
            EventType.PIT_LIMITER_OFF: self.engineer_brain.handle_pit_limiter_off,
            # Track flags
            EventType.TRACK_GREEN: self.engineer_brain.handle_track_green,
            EventType.TRACK_YELLOW: self.engineer_brain.handle_track_yellow,
            EventType.TRACK_DOUBLE_YELLOW: self.engineer_brain.handle_track_double_yellow,
            # On track
            EventType.ON_TRACK_ENTERED: self.engineer_brain.handle_on_track_entered,
            EventType.ON_TRACK_EXITED: self.engineer_brain.handle_on_track_exited,
            # Quali lap start
            EventType.QUALI_LAP_START: self.engineer_brain.handle_quali_lap_start,
            # Pit lane / service
            EventType.PIT_LANE_ENTERED: self.engineer_brain.handle_pit_lane_entered,
            EventType.PIT_LANE_EXITED: self.engineer_brain.handle_pit_lane_exited,
            EventType.PIT_SERVICE_START: self.engineer_brain.handle_pit_service_start,
            EventType.PIT_SERVICE_END: self.engineer_brain.handle_pit_service_end,
            EventType.PIT_RELEASE: self.engineer_brain.handle_pit_release,
            EventType.PIT_ENTRY_LINE: self.engineer_brain.handle_pit_entry_line,
            EventType.PIT_EXIT_LINE: self.engineer_brain.handle_pit_exit_line,
            # Forecast
            EventType.FORECAST_RAIN_CHANGE: self.engineer_brain.handle_forecast_rain_change,
            EventType.FORECAST_WEATHER_CHANGE: self.engineer_brain.handle_forecast_weather_change,
        }
