# core/event_router.py
# 4-level priority queue system for audio events
# Priority 1: Personal Pit + Safety (highest)
# Priority 2: Weather Updates (stale skipping)
# Priority 3: Gap Reports (FIFO)
# Priority 4: Teammate Pits (lowest)

import queue
import threading

from .events import EventType


# Priority levels
PRIORITY_PIT = 1      # Personal pit calls + safety flags
PRIORITY_WEATHER = 2  # Weather updates (stale skip)
PRIORITY_GAP = 3      # Gap reports
PRIORITY_TEAMMATE = 4 # Teammate pits

# Route events to priority levels
EVENT_PRIORITIES = {
    # Priority 1: Personal Pit + Safety
    EventType.RED_FLAG: PRIORITY_PIT,
    EventType.RESTART_GRID_READY: PRIORITY_PIT,
    EventType.FORMATION_LAP_START: PRIORITY_PIT,
    EventType.FORMATION_LAP_SECTOR3: PRIORITY_PIT,
    EventType.RACE_START_GRID: PRIORITY_PIT,
    EventType.SAFETY_CAR_DEPLOYED: PRIORITY_PIT,
    EventType.SAFETY_CAR_IN_THIS_LAP: PRIORITY_PIT,
    EventType.SAFETY_CAR_END: PRIORITY_PIT,
    EventType.VIRTUAL_SAFETY_CAR_DEPLOYED: PRIORITY_PIT,
    EventType.VSC_DEPLOYED: PRIORITY_PIT,
    EventType.VSC_END: PRIORITY_PIT,
    EventType.VSC_ENDING: PRIORITY_PIT,
    EventType.DELTA_FREEZE_START: PRIORITY_PIT,
    EventType.DELTA_FREEZE_END: PRIORITY_PIT,
    EventType.PIT_LIMITER_REMINDER: PRIORITY_PIT,
    EventType.PIT_STOP_QUALITY: PRIORITY_PIT,
    EventType.PIT_WINDOW_SECTOR3: PRIORITY_PIT,
    EventType.IN_LAP: PRIORITY_PIT,
    EventType.OUT_LAP: PRIORITY_PIT,
    EventType.LAP_INVALIDATED: PRIORITY_PIT,
    EventType.RACE_WIN: PRIORITY_PIT,
    EventType.RACE_FINISH: PRIORITY_PIT,
    EventType.CONSTRUCTORS_CHAMPIONSHIP_WON: PRIORITY_PIT,
    EventType.DRIVERS_CHAMPIONSHIP_WON: PRIORITY_PIT,
    EventType.SESSION_START: PRIORITY_PIT,
    EventType.SESSION_READY: PRIORITY_PIT,
    EventType.SPRINT_RACE_ANNOUNCED: PRIORITY_PIT,
    EventType.SESSION_END: PRIORITY_PIT,
    EventType.SESSION_TYPE_CHANGED: PRIORITY_PIT,
    EventType.PIT_ENTRY: PRIORITY_PIT,
    EventType.PIT_EXIT: PRIORITY_PIT,
    EventType.PIT_DENIED_OR_SILENT: PRIORITY_PIT,
    EventType.SAFETY_OVERRIDE_REQUIRED: PRIORITY_PIT,
    EventType.STRATEGY_UPDATE_FROM_GAME: PRIORITY_PIT,
    EventType.SC_VSC_STRATEGY_RECOMMENDATION: PRIORITY_PIT,
    EventType.PIT_LANE_ENTERED: PRIORITY_PIT,
    EventType.PIT_LANE_EXITED: PRIORITY_PIT,
    EventType.PIT_SERVICE_START: PRIORITY_PIT,
    EventType.PIT_SERVICE_END: PRIORITY_PIT,
    EventType.PIT_RELEASE: PRIORITY_PIT,
    EventType.PIT_ENTRY_LINE: PRIORITY_PIT,
    EventType.PIT_EXIT_LINE: PRIORITY_PIT,
    EventType.PIT_LIMITER_ON: PRIORITY_PIT,
    EventType.PIT_LIMITER_OFF: PRIORITY_PIT,
    EventType.TRACK_GREEN: PRIORITY_PIT,
    EventType.TRACK_YELLOW: PRIORITY_PIT,
    EventType.TRACK_DOUBLE_YELLOW: PRIORITY_PIT,
    EventType.LAP_START: PRIORITY_PIT,
    EventType.PARTICIPANTS_READY: PRIORITY_PIT,
    EventType.POSITION_GAIN: PRIORITY_PIT,
    EventType.POSITION_LOST: PRIORITY_PIT,
    
    # Priority 2: Weather (stale skipping)
    EventType.WEATHER_UPDATE: PRIORITY_WEATHER,
    EventType.WEATHER_CHANGED: PRIORITY_WEATHER,
    EventType.RAIN_SOON: PRIORITY_WEATHER,
    EventType.TRACK_DRYING: PRIORITY_WEATHER,
    EventType.TRACK_WORSENING: PRIORITY_WEATHER,
    EventType.CROSSOVER_TO_INTERS: PRIORITY_WEATHER,
    EventType.CROSSOVER_TO_SLICKS: PRIORITY_WEATHER,
    EventType.CROSSOVER_TO_FULL_WETS: PRIORITY_WEATHER,
    EventType.FORECAST_WEATHER_CHANGE: PRIORITY_WEATHER,
    EventType.FORECAST_RAIN_CHANGE: PRIORITY_WEATHER,
    
    # Priority 3: Gap Reports
    EventType.RACE_GAP: PRIORITY_GAP,
    EventType.LAST_FIVE_LAPS: PRIORITY_GAP,
    EventType.LAST_LAP: PRIORITY_GAP,
    
    # Priority 4: Teammate
    EventType.TEAMMATE_PITTING: PRIORITY_TEAMMATE,
    EventType.TEAMMATE_DNF: PRIORITY_TEAMMATE,
}

# Weather event types that should skip stale (only keep latest of same type)
WEATHER_STALE_TYPES = {
    EventType.WEATHER_UPDATE,
    EventType.WEATHER_CHANGED,
    EventType.RAIN_SOON,
    EventType.TRACK_DRYING,
    EventType.TRACK_WORSENING,
}


class EventRouter:
    def __init__(self, engineer_brain):
        self.engineer_brain = engineer_brain
        self._running = True
        self._init_mapping()
        
        # 4 separate queues for priority levels
        self._pit_queue = queue.Queue()
        self._weather_queue = queue.Queue()
        self._gap_queue = queue.Queue()
        self._teammate_queue = queue.Queue()
        
        self._thread = threading.Thread(target=self._worker, daemon=True, name="EventRouter")
        self._thread.start()

    def _get_next_event(self):
        """Get next event from highest priority non-empty queue."""
        # Priority 1: Pit
        if not self._pit_queue.empty():
            return self._pit_queue.get()
        # Priority 2: Weather
        if not self._weather_queue.empty():
            return self._weather_queue.get()
        # Priority 3: Gap
        if not self._gap_queue.empty():
            return self._gap_queue.get()
        # Priority 4: Teammate
        if not self._teammate_queue.empty():
            return self._teammate_queue.get()
        return None

    def _worker(self):
        while self._running:
            try:
                item = self._get_next_event()
                if item is None:
                    continue
                
                event_type, payload = item
                if event_type is None:
                    continue
                
                handler = self._mapping.get(event_type)
                if handler:
                    handler(**payload)
                    
            except Exception:
                continue

    def _route_event(self, event_type: EventType, payload: dict):
        """Route event to appropriate queue based on priority."""
        priority = EVENT_PRIORITIES.get(event_type, PRIORITY_GAP)
        
        if priority == PRIORITY_PIT:
            self._pit_queue.put((event_type, payload))
        elif priority == PRIORITY_WEATHER:
            # Stale skipping: remove old same-type events before adding new
            self._remove_stale_weather(event_type)
            self._weather_queue.put((event_type, payload))
        elif priority == PRIORITY_GAP:
            # Remove stale gap events - only keep latest
            self._remove_stale_gap()
            self._gap_queue.put((event_type, payload))
        elif priority == PRIORITY_TEAMMATE:
            self._teammate_queue.put((event_type, payload))

    def _remove_stale_weather(self, event_type: EventType):
        """Remove old same-type weather events from queue (only keep latest)."""
        if event_type not in WEATHER_STALE_TYPES:
            return
        
        temp_items = []
        
        # Drain queue
        while not self._weather_queue.empty():
            try:
                item = self._weather_queue.get_nowait()
                if item[0] == event_type:
                    pass  # Discard stale event
                else:
                    temp_items.append(item)
            except queue.Empty:
                break
        
        # Put back non-stale items
        for item in temp_items:
            self._weather_queue.put(item)

    def _remove_stale_gap(self):
        """Remove all gap events from queue - only keep the latest."""
        temp_items = []
        
        # Drain queue
        while not self._gap_queue.empty():
            try:
                item = self._gap_queue.get_nowait()
                temp_items.append(item)
            except queue.Empty:
                break
        
        # Only keep the last one (latest)
        if temp_items:
            self._gap_queue.put(temp_items[-1])

    def handle_event(self, event_type: EventType, **payload):
        self._route_event(event_type, payload)

    def stop(self):
        self._running = False
        if self._thread.is_alive():
            self._thread.join(timeout=2)

    def _init_mapping(self):
        self._mapping = {
            # Priority events (handled via pit_queue)
            EventType.RED_FLAG: self.engineer_brain.handle_red_flag,
            EventType.RESTART_GRID_READY: self.engineer_brain.handle_red_flag_restart,
            EventType.FORMATION_LAP_START: self.engineer_brain.handle_formation_lap,
            EventType.FORMATION_LAP_SECTOR3: self.engineer_brain.handle_find_grid_slot,
            EventType.RACE_START_GRID: self.engineer_brain.handle_race_start,
            EventType.SAFETY_CAR_DEPLOYED: self.engineer_brain.handle_sc_start,
            EventType.SAFETY_CAR_IN_THIS_LAP: self.engineer_brain.handle_sc_restart,
            EventType.SAFETY_CAR_END: self.engineer_brain.handle_sc_end,
            EventType.VIRTUAL_SAFETY_CAR_DEPLOYED: self.engineer_brain.handle_vsc_start,
            EventType.VSC_DEPLOYED: self.engineer_brain.handle_vsc_start,
            EventType.VSC_END: self.engineer_brain.handle_vsc_end,
            EventType.VSC_ENDING: self.engineer_brain.handle_vsc_end,
            EventType.DELTA_FREEZE_START: self.engineer_brain.handle_delta_freeze_start,
            EventType.DELTA_FREEZE_END: self.engineer_brain.handle_delta_freeze_end,
            EventType.RACE_WIN: self.engineer_brain.handle_race_win,
            EventType.CONSTRUCTORS_CHAMPIONSHIP_WON: self.engineer_brain.handle_constructors_title,
            EventType.DRIVERS_CHAMPIONSHIP_WON: self.engineer_brain.handle_drivers_title,
            EventType.RACE_FINISH: self.engineer_brain.handle_race_finish,
            EventType.LAP_START: self.engineer_brain.handle_lap_start,
            EventType.LAP_INVALIDATED: self.engineer_brain.handle_lap_invalidated,
            EventType.SESSION_START: self.engineer_brain.handle_session_start,
            EventType.SESSION_READY: self.engineer_brain.handle_session_ready,
            EventType.SPRINT_RACE_ANNOUNCED: self.engineer_brain.handle_sprint_announcement,
            EventType.SESSION_END: self.engineer_brain.handle_session_end,
            EventType.SESSION_TYPE_CHANGED: self.engineer_brain.handle_session_type_changed,
            EventType.PARTICIPANTS_READY: self.engineer_brain.handle_participants_ready,
            EventType.IN_LAP: self.engineer_brain.handle_in_lap,
            EventType.OUT_LAP: self.engineer_brain.handle_out_lap,
            EventType.PIT_ENTRY: self.engineer_brain.handle_pit_entry,
            EventType.PIT_EXIT: self.engineer_brain.handle_pit_exit,
            EventType.PIT_DENIED_OR_SILENT: self.engineer_brain.handle_extend_stint,
            EventType.SAFETY_OVERRIDE_REQUIRED: self.engineer_brain.handle_safety_override,
            EventType.STRATEGY_UPDATE_FROM_GAME: self.engineer_brain.handle_strategy_update,
            EventType.SC_VSC_STRATEGY_RECOMMENDATION: self.engineer_brain.handle_sc_vsc_pit_recommendation,
            EventType.PIT_LIMITER_REMINDER: self.engineer_brain.handle_pit_limiter_reminder,
            EventType.PIT_STOP_QUALITY: self.engineer_brain.handle_pit_stop_quality,
            EventType.PIT_WINDOW_SECTOR3: self.engineer_brain.handle_pit_reminder,
            EventType.PIT_LANE_ENTERED: self.engineer_brain.handle_pit_lane_entered,
            EventType.PIT_LANE_EXITED: self.engineer_brain.handle_pit_lane_exited,
            EventType.PIT_SERVICE_START: self.engineer_brain.handle_pit_service_start,
            EventType.PIT_SERVICE_END: self.engineer_brain.handle_pit_service_end,
            EventType.PIT_RELEASE: self.engineer_brain.handle_pit_release,
            EventType.PIT_ENTRY_LINE: self.engineer_brain.handle_pit_entry_line,
            EventType.PIT_EXIT_LINE: self.engineer_brain.handle_pit_exit_line,
            EventType.PIT_LIMITER_ON: self.engineer_brain.handle_pit_limiter_on,
            EventType.PIT_LIMITER_OFF: self.engineer_brain.handle_pit_limiter_off,
            EventType.TRACK_GREEN: self.engineer_brain.handle_track_green,
            EventType.TRACK_YELLOW: self.engineer_brain.handle_track_yellow,
            EventType.TRACK_DOUBLE_YELLOW: self.engineer_brain.handle_track_double_yellow,
            
            # Weather (handled via weather_queue)
            EventType.WEATHER_UPDATE: self.engineer_brain.handle_weather_update,
            EventType.WEATHER_CHANGED: self.engineer_brain.handle_weather_changed,
            EventType.RAIN_SOON: self.engineer_brain.handle_rain_soon,
            EventType.TRACK_DRYING: self.engineer_brain.handle_track_drying,
            EventType.TRACK_WORSENING: self.engineer_brain.handle_track_worsening,
            EventType.CROSSOVER_TO_INTERS: self.engineer_brain.handle_crossover_to_inters,
            EventType.CROSSOVER_TO_SLICKS: self.engineer_brain.handle_crossover_to_slicks,
            EventType.CROSSOVER_TO_FULL_WETS: self.engineer_brain.handle_crossover_to_full_wets,
            EventType.FORECAST_WEATHER_CHANGE: self.engineer_brain.handle_forecast_weather_change,
            EventType.FORECAST_RAIN_CHANGE: self.engineer_brain.handle_forecast_rain_change,
            
            # Gap (handled via gap_queue)
            EventType.RACE_GAP: self.engineer_brain.handle_gap_report,
            EventType.LAST_FIVE_LAPS: self.engineer_brain.handle_last_five_laps,
            EventType.LAST_LAP: self.engineer_brain.handle_last_lap,
            EventType.POSITION_GAIN: self.engineer_brain.handle_position_gain,
            EventType.POSITION_LOST: self.engineer_brain.handle_position_lost,
            
            # Teammate (handled via teammate_queue)
            EventType.TEAMMATE_PITTING: self.engineer_brain.handle_teammate_pit,
            EventType.TEAMMATE_DNF: self.engineer_brain.handle_teammate_dnf,
        }
