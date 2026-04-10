# f1/ers_drs_manager.py

import threading
import time
import math
from typing import Optional, Callable

from udp.packet_definitions import (
    PacketCarTelemetryData,
    PacketCarStatusData,
    PacketSessionData,
    PacketTyreSetsData,
    PacketCarDamageData,
    TyreCompound,
    Weather,
    SafetyCarStatus,
)


class ERSDRSManager:
    """
    Auto DRS deployment, context-aware ERS, pit window tracking,
    weather updates, and MFD tire change navigation.
    """

    # ERS modes: 0=None, 1=Medium, 2=Hotlap, 3=Overtake
    ERS_NONE = 0
    ERS_MEDIUM = 1
    ERS_HOTLAP = 2
    ERS_OVERTAKE = 3

    # Tyre compound indices for MFD navigation
    COMPOUND_MAP = {
        TyreCompound.F1_MODERN_C5: 0,    # Soft
        TyreCompound.F1_MODERN_C4: 1,    # Medium
        TyreCompound.F1_MODERN_C3: 1,    # Medium
        TyreCompound.F1_MODERN_C2: 2,    # Hard
        TyreCompound.F1_MODERN_C1: 2,    # Hard
        TyreCompound.F1_MODERN_C0: 2,    # Hard
        TyreCompound.F1_MODERN_C6: 2,    # Hard
        TyreCompound.F1_MODERN_INTER: 3, # Inter
        TyreCompound.F1_MODERN_WET: 4,   # Wet
    }

    def __init__(self, telemetry_state, keyboard_controller, engineer_brain):
        self.telemetry = telemetry_state
        self.keyboard = keyboard_controller
        self.engineer = engineer_brain

        # State tracking
        self._last_drs_zone = False
        self._last_ers_mode = None
        self._last_weather_announcement = 0
        self._last_ers_announcement = 0
        self._pit_confirmed = False
        self._pit_announced = False
        self._pit_lap = None
        self._sector3_reminder_done = False
        self._pit_extended = False
        self._emergency_pit = False
        self._emergency_reason = None
        self._last_pit_call_lap = None  # Track lap of last pit call to prevent spam
        self._last_lap_announced = False

        # Weather tracking
        self._last_rain_pct = None
        self._rain_trend = None

        # Callbacks for confirmation flow
        self._on_pit_confirm = None
        self._pending_pit_call = None
        self._pending_tire_compound = None

        # ERS automation pause (for ERS Management practice)
        self._ers_automation_paused = False

        # Timing
        self._last_drs_press = 0
        self._last_ers_press = 0
        self._drs_cooldown = 2.0  # Minimum seconds between DRS activations
        self._ers_cooldown = 3.0  # Minimum seconds between ERS announcements

        # ERS burst timing
        self._ers_burst_active = False
        self._ers_burst_end_time = 0.0

        # Debug tracking
        self._debug_last_recommended_ers = None
        self._debug_last_drs_allowed = None
        self._debug_last_drs_zone = None

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    def register_pit_confirm_callback(self, callback: Callable):
        """Register callback for when user confirms pit stop."""
        self._on_pit_confirm = callback

    def confirm_pit(self):
        """
        Confirm the pending pit stop. Called by Insert key or 'confirm' text command.
        Returns the confirmation text if confirmed, None if nothing to confirm.
        """
        if not self._pending_pit_call:
            return None
        self._pit_confirmed = True
        confirmation = f"Confirmed. {self._pending_pit_call}"

        # If weather tire change needed, navigate MFD
        if self._pending_tire_compound is not None:
            self._navigate_mfd_for_tire(self._pending_tire_compound)

        self._pending_pit_call = None
        self._pending_tire_compound = None
        return confirmation

    def stop_ers_automation(self):
        """Pause ERS automation (called when entering ERS Management practice)."""
        self._ers_automation_paused = True

    def resume_ers_automation(self):
        """Resume ERS automation (called when leaving ERS Management practice)."""
        self._ers_automation_paused = False

    def start_thread(self):
        def _run_loop():
            while True:
                self.update()
                time.sleep(0.1)  # 10Hz - less CPU, still responsive for ERS/DRS

        t = threading.Thread(target=_run_loop, daemon=True, name="ERSDRSThread")
        t.start()

    # ---------------------------------------------------------
    # MAIN UPDATE LOOP
    # ---------------------------------------------------------

    def update(self):
        """Called every telemetry tick."""
        # Get telemetry data for ERS/DRS calculations
        status = self.telemetry.car_status
        telemetry = self.telemetry.car_telemetry
        session = self.telemetry.session
        lap_data = self.telemetry.lap_data

        game_ers = None
        saul_ers = None
        recommended_ers = None
        drs_allowed = False
        drs_zone = False
        battery_pct = 0
        current_mode = 0

        if status and telemetry and session:
            try:
                player_status = status.get_player_status()
                player_telemetry = telemetry.get_player_telemetry()
                
                if player_status and player_telemetry:
                    current_mode = player_status.m_ersDeployMode
                    self.keyboard.sync_ers_mode(player_status.m_ersDeployMode)
                    
                    # Get values for debug
                    game_ers = player_status.m_ersDeployMode
                    saul_ers = self.keyboard.current_ers_mode
                    
                    # Calculate recommended ERS
                    battery = player_status.m_ersStoreEnergy
                    battery_pct = (battery / 4000000.0) * 100.0
                    is_last_lap = self._is_last_lap(session, lap_data)
                    under_sc = self._is_under_safety_car(session)
                    on_straight = self._is_on_straight(player_telemetry)
                    
                    # Calculate recommended ERS mode
                    if self._ers_automation_paused:
                        recommended_ers = None
                    elif is_last_lap:
                        recommended_ers = self.ERS_OVERTAKE
                    elif battery_pct < 15:
                        recommended_ers = self.ERS_NONE
                    elif under_sc:
                        recommended_ers = self.ERS_NONE
                    elif battery_pct > 50 and not under_sc:
                        recommended_ers = self.ERS_MEDIUM
                    elif self._is_quali(session) and on_straight:
                        recommended_ers = self.ERS_HOTLAP
                    elif self._is_defending() and on_straight:
                        recommended_ers = self.ERS_OVERTAKE
                    elif self._is_closing_gap() and on_straight:
                        recommended_ers = self.ERS_OVERTAKE
                    elif on_straight and battery_pct > 30:
                        # HOTLAP burst on straights even when not in combat
                        now = time.time()
                        if self._ers_burst_active:
                            if now < self._ers_burst_end_time:
                                recommended_ers = self.ERS_HOTLAP
                            else:
                                self._ers_burst_active = False
                        if recommended_ers != self.ERS_HOTLAP:
                            self._ers_burst_active = True
                            self._ers_burst_end_time = now + 0.45  # 450ms burst
                            recommended_ers = self.ERS_HOTLAP
                    else:
                        recommended_ers = None  # No recommendation
                    
                    # DRS status
                    drs_allowed = player_status.m_drsAllowed == 1
                    drs_activation_dist = player_status.m_drsActivationDistance > 0
                    drs_zone = drs_allowed and drs_activation_dist and on_straight and not under_sc
                    
                    # Debug print only on significant changes (every 5 sec max)
                    now = time.time()
                    if (recommended_ers != self._debug_last_recommended_ers or 
                        drs_allowed != self._debug_last_drs_allowed or
                        drs_zone != self._debug_last_drs_zone):
                        if now - self._last_drs_press > 5:
                            print(f"[ERS/DRS] Game={game_ers} Saul={saul_ers} Rec={recommended_ers} | "
                                  f"Batt={battery_pct:.0f}% | DRS={drs_allowed}/zone={drs_zone}")
                        self._debug_last_recommended_ers = recommended_ers
                        self._debug_last_drs_allowed = drs_allowed
                        self._debug_last_drs_zone = drs_zone
            except Exception:
                pass

        self._handle_drs()
        self._handle_ers(recommended_ers, battery_pct, current_mode)
        self._handle_pit_window()
        self._handle_weather_updates()
        self._handle_last_lap()

    # ---------------------------------------------------------
    # DRS AUTO-DEPLOY
    # ---------------------------------------------------------

    def _handle_drs(self):
        """Auto-deploy DRS when legal."""
        status = self.telemetry.car_status
        telemetry = self.telemetry.car_telemetry
        session = self.telemetry.session

        if not status or not telemetry or not session:
            return

        player_status = status.get_player_status()
        player_telemetry = telemetry.get_player_telemetry()

        drs_allowed = player_status.m_drsAllowed == 1
        drs_activation_dist = player_status.m_drsActivationDistance
        on_straight, steer, throttle, speed = self._is_on_straight(player_telemetry, get_values=True)
        under_safety_car = self._is_under_safety_car(session)
        sc_status = session.m_safetyCarStatus

        now = time.time()
        in_drs_zone = drs_allowed and drs_activation_dist > 0 and on_straight and not under_safety_car

        # Debounce: don't spam DRS presses
        if in_drs_zone and not self._last_drs_zone:
            if now - self._last_drs_press > self._drs_cooldown:
                print("[DRS] *** PRESSING DRS ***")
                self.keyboard.press_drs()
                self._last_drs_press = now
                self.engineer._say("DRS now.")

        self._last_drs_zone = in_drs_zone

    # ---------------------------------------------------------
    # ERS CONTEXT LOGIC
    # ---------------------------------------------------------

    def _handle_ers(self, recommended_ers, battery_pct, current_mode):
        """Context-aware ERS deployment."""
        if self._ers_automation_paused:
            return

        if recommended_ers is None:
            return

        # Apply the recommended mode
        if recommended_ers != current_mode:
            self.keyboard.cycle_ers_to(recommended_ers)

        # PRIORITY 9: Fallback → OFF
        if current_mode != self.ERS_NONE:
            self.keyboard.cycle_ers_to(self.ERS_NONE)

    # ---------------------------------------------------------
    # PIT WINDOW TRACKING
    # ---------------------------------------------------------

    def _handle_pit_window(self):
        """Track pit window and make pit calls."""
        session = self.telemetry.session
        lap_data = self.telemetry.lap_data

        if not session or not lap_data:
            return

        # Only track pit window for race sessions (type 11 or 15)
        if session.m_sessionType not in (11, 15):
            return

        player_lap = lap_data.get_player_lap_data()
        current_lap = player_lap.m_currentLapNum
        current_sector = player_lap.m_sector

        ideal_lap = session.m_pitStopWindowIdealLap
        latest_lap = session.m_pitStopWindowLatestLap

        # Don't call pit window if ideal_lap is 0 (not set) or if we're on lap 1-2
        if ideal_lap == 0 or current_lap <= 2:
            return

        # Start of in-lap
        if current_lap == ideal_lap and not self._pit_announced:
            self._pit_announced = True
            self._pit_lap = current_lap
            self._sector3_reminder_done = False
            self._pending_pit_call = self._get_pit_call()
            self._pending_tire_compound = self._get_weather_tire_compound()

            self.engineer._say(f"Box this lap, Shawn. {self._pending_pit_call}. Confirm?")
            return

        # Sector 3 reminder
        if current_lap == ideal_lap and current_sector == 2:
            if not self._sector3_reminder_done:
                self._sector3_reminder_done = True
                if self._pit_confirmed:
                    # Already confirmed, just reminder
                    self.engineer._say("Box this lap, Shawn.")
                else:
                    # Not confirmed yet, ask again
                    self.engineer._say(f"Box this lap, Shawn. Confirm?")
            return

        # Lap passed without confirmation
        if current_lap > ideal_lap and not self._pit_confirmed:
            if not self._pit_extended:
                self._pit_extended = True
                # Extend one lap
                self._pit_announced = False
                self._sector3_reminder_done = False
                self._pending_pit_call = self._get_pit_call()
                self._pending_tire_compound = self._get_weather_tire_compound()

    # ---------------------------------------------------------
    # WEATHER UPDATES
    # ---------------------------------------------------------

    def _handle_weather_updates(self):
        """Proactive weather announcements (Saul‑safe version)."""
        session = self.telemetry.session
        status = self.telemetry.car_status
        lap_data = self.telemetry.lap_data

        if not session or not status:
            return

        player_status = status.get_player_status()
        current_compound = player_status.m_actualTyreCompound

        # --- REAL WEATHER SIGNALS ---
        rain_pct = session.m_weatherForecastSamples[0].m_rainPercentage if session.m_weatherForecastSamples else 0
        wetness = self.telemetry.track_wetness
        rain_in_minutes = self._get_rain_eta(session)

        # --- SAFETY GATES -------------------------------------------------------

        now = time.time()

        # Gate 1: Never speak more than once per minute
        if now - self._last_weather_announcement < 60:
            return

        # Gate 2: Never make pit decisions in the first 2 laps of the race
        if lap_data:
            player_lap = lap_data.get_player_lap_data()
            current_lap = getattr(player_lap, 'm_currentLapNum', 0)
            if current_lap <= 2:
                return
        else:
            current_lap = 0

        # Gate 3: Never react to rain % unless the track is actually wet
        track_is_dry = wetness < 10

        # Gate 4: Never make multiple pit calls on the same lap
        # Reset emergency flag when lap changes or damage is fixed
        if self._last_pit_call_lap is not None and self._last_pit_call_lap != current_lap:
            self._emergency_pit = False
            self._emergency_reason = None

        if self._last_pit_call_lap == current_lap and current_lap > 0:
            return

        # --- RAIN TREND ---------------------------------------------------------
        if self._last_rain_pct is not None:
            if rain_pct > self._last_rain_pct + 10:
                self._rain_trend = "increasing"
            elif rain_pct < self._last_rain_pct - 10:
                self._rain_trend = "decreasing"

        self._last_rain_pct = rain_pct

        # --- FORECAST ANNOUNCEMENTS --------------------------------------------

        # Light rain expected later (10–15 min)
        if rain_in_minutes and 10 <= rain_in_minutes <= 15:
            if self._is_on_slicks(current_compound):
                self._last_weather_announcement = now
                self.engineer._say(
                    f"Rain expected in about {rain_in_minutes} minutes, Shawn. "
                    f"Slicks are still the right call."
                )
            return

        # Rain approaching (5–10 min)
        if rain_in_minutes and 5 <= rain_in_minutes < 10:
            if self._is_on_slicks(current_compound):
                self._last_weather_announcement = now
                self.engineer._say(
                    "Rain incoming soon. Keep an eye on grip, Shawn."
                )
            return

        # --- EMERGENCY PIT LOGIC ------------------------------------------------

        # Rain starting (<5 min) → ONLY if track is actually wet
        if rain_in_minutes and rain_in_minutes < 5:
            if not track_is_dry and self._is_on_slicks(current_compound):
                if not self._emergency_pit:
                    self._emergency_pit = True
                    self._emergency_reason = "rain"
                    self._pending_pit_call = "Box for inters"
                    self._pending_tire_compound = 3
                    self._last_weather_announcement = now
                    self._last_pit_call_lap = current_lap
                    self.engineer._say(
                        "Rain's starting to hit the track. Box for inters, Shawn. Confirm."
                    )
            return

        # Heavy rain + on inters → wets (only if wetness supports it)
        if wetness > 40 and self._is_on_inters(current_compound):
            if not self._emergency_pit:
                self._emergency_pit = True
                self._emergency_reason = "heavy_rain"
                self._pending_pit_call = "Box for wets"
                self._pending_tire_compound = 4
                self._last_weather_announcement = now
                self._last_pit_call_lap = current_lap
                self.engineer._say(
                    "Track's getting flooded. Box for wets, Shawn. Confirm."
                )
            return

        # Track drying + on wets
        if wetness < 20 and self._is_on_wets(current_compound) and self._rain_trend == "decreasing":
            self._last_weather_announcement = now
            self.engineer._say(
                "Track's drying out. Window for slicks opening, Shawn."
            )
            return

        # Track dry + on inters
        if wetness < 10 and self._is_on_inters(current_compound):
            if not self._emergency_pit:
                self._emergency_pit = True
                self._emergency_reason = "drying"
                self._pending_pit_call = "Box for slicks"
                self._pending_tire_compound = self._get_best_slick_compound()
                self._last_weather_announcement = now
                self._last_pit_call_lap = current_lap
                self.engineer._say(
                    "Track's dry again. Box for slicks, Shawn. Confirm."
                )
            return

    # ---------------------------------------------------------
    # LAST LAP
    # ---------------------------------------------------------

    def _handle_last_lap(self):
        """Handle last lap ERS dump."""
        # Handled in _handle_ers()

    # ---------------------------------------------------------
    # MFD NAVIGATION
    # ---------------------------------------------------------

    def _navigate_mfd_for_tire(self, compound_index):
        """Navigate MFD to select tire compound for pit stop."""
        self.keyboard.select_pit_compound(compound_index)

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def _is_on_straight(self, telemetry_data, get_values=False):
        """Detect if car is on a straight."""
        if not telemetry_data:
            return (False, 0, 0, 0) if get_values else False
        steer = abs(telemetry_data.m_steer)
        throttle = telemetry_data.m_throttle
        speed = telemetry_data.m_speed
        # Lowered threshold from 200 to 150 km/h for more tracks
        on_straight = steer < 0.15 and throttle > 0.7 and speed > 150
        if get_values:
            return (on_straight, steer, throttle, speed)
        return on_straight

    def _is_under_safety_car(self, session) -> bool:
        """Check if under SC, VSC, or formation lap."""
        if not session:
            return False
        return session.m_safetyCarStatus in (
            SafetyCarStatus.FULL,
            SafetyCarStatus.VIRTUAL,
            SafetyCarStatus.FORMATION,
        )

    def _is_quali(self, session) -> bool:
        """Check if in qualifying session."""
        if not session:
            return False
        return session.m_sessionType in (5, 6, 7, 8)  # Q1, Q2, Q3, one-shot

    def _is_defending(self) -> bool:
        """Check if defending position (car behind within 0.5s)."""
        lap_data = self.telemetry.lap_data
        if not lap_data:
            return False

        player_lap = lap_data.get_player_lap_data()
        # Delta to car behind would need to be calculated from position data
        # For now, use a simplified check
        return False

    def _is_closing_gap(self) -> bool:
        """Check if closing gap to car ahead."""
        lap_data = self.telemetry.lap_data
        if not lap_data:
            return False

        player_lap = lap_data.get_player_lap_data()
        delta = player_lap.delta_to_car_in_front_seconds
        return delta is not None and 0 < delta < 3.0

    def _is_last_lap(self, session, lap_data) -> bool:
        """Check if this is the last lap of the race."""
        if not session or not lap_data:
            return False

        player_lap = lap_data.get_player_lap_data()
        total_laps = session.m_totalLaps
        return total_laps > 0 and player_lap.m_currentLapNum == total_laps

    def _is_on_slicks(self, compound) -> bool:
        """Check if on slick tyres."""
        slick_compounds = {
            TyreCompound.F1_MODERN_C5,
            TyreCompound.F1_MODERN_C4,
            TyreCompound.F1_MODERN_C3,
            TyreCompound.F1_MODERN_C2,
            TyreCompound.F1_MODERN_C1,
            TyreCompound.F1_MODERN_C0,
            TyreCompound.F1_MODERN_C6,
        }
        try:
            return TyreCompound(compound) in slick_compounds
        except ValueError:
            return False

    def _is_on_inters(self, compound) -> bool:
        """Check if on intermediate tyres."""
        try:
            return TyreCompound(compound) == TyreCompound.F1_MODERN_INTER
        except ValueError:
            return False

    def _is_on_wets(self, compound) -> bool:
        """Check if on wet tyres."""
        try:
            return TyreCompound(compound) == TyreCompound.F1_MODERN_WET
        except ValueError:
            return False

    def _is_damage_emergency(self) -> bool:
        """Check if there's emergency damage requiring immediate pit."""
        damage = self.telemetry.car_damage
        if not damage:
            return False
        try:
            player_damage = damage.get_player_damage()
            # Front wing damage > 30%
            if player_damage.m_frontLeftWingDamage > 30 or player_damage.m_frontRightWingDamage > 30:
                return True
            # Tyre blisters > 50%
            if player_damage.m_tyreBlisters and any(b > 50 for b in player_damage.m_tyreBlisters):
                return True
        except Exception:
            pass
        return False

    def _get_rain_eta(self, session) -> Optional[int]:
        """Get minutes until rain from forecast samples."""
        if not session or not session.m_weatherForecastSamples:
            return None

        for i, sample in enumerate(session.m_weatherForecastSamples):
            if sample.m_rainPercentage > 40:
                return sample.m_timeOffset

        return None

    def _get_pit_call(self) -> str:
        """Generate pit call based on current conditions."""
        status = self.telemetry.car_status
        session = self.telemetry.session
        damage = self.telemetry.car_damage

        if not status:
            return "Box this lap"

        player_status = status.get_player_status()
        compound = player_status.m_actualTyreCompound

        # Check damage
        if damage:
            player_damage = damage.get_player_damage()
            if player_damage.m_frontLeftWingDamage > 30 or player_damage.m_frontRightWingDamage > 30:
                return "Front wing damage. Boxing for new wing and tyres"
            if player_damage.m_tyreBlisters and any(b > 50 for b in player_damage.m_tyreBlisters):
                return "Tyre blistering. Boxing this lap"

        # Check tyre wear
        tyre_sets = self.telemetry.tyre_sets
        if tyre_sets:
            fitted = tyre_sets.get_fitted_tyre()
            if fitted.m_wear > 80:
                return "Tyres gone. Boxing this lap"

        # Normal pit call
        if compound in (TyreCompound.F1_MODERN_C5, TyreCompound.F1_MODERN_C4):
            return "Fitting mediums"
        elif compound in (TyreCompound.F1_MODERN_C3, TyreCompound.F1_MODERN_C2):
            return "Fitting hards"
        else:
            return "Boxing for fresh tyres"

    def _get_weather_tire_compound(self) -> Optional[int]:
        """Get MFD compound index for weather-related tire change.
        Returns None if no weather change needed."""
        session = self.telemetry.session
        status = self.telemetry.car_status

        if not session or not status:
            return None

        player_status = status.get_player_status()
        current_compound = player_status.m_actualTyreCompound
        rain_pct = session.m_weatherForecastSamples[0].m_rainPercentage if session.m_weatherForecastSamples else 0

        if rain_pct > 40 and self._is_on_slicks(current_compound):
            return 3  # Inter
        elif rain_pct > 70 and self._is_on_inters(current_compound):
            return 4  # Wet
        elif rain_pct < 10 and self._is_on_wets(current_compound):
            return self._get_best_slick_compound()

        return None

    def _get_best_slick_compound(self) -> int:
        """Get best slick compound index from available tyre sets."""
        tyre_sets = self.telemetry.tyre_sets
        if not tyre_sets:
            return 1  # Default to medium

        # Find best available slick compound (prefer New)
        for ts in tyre_sets.m_tyreSetData:
            if ts.m_available and not ts.m_fitted:
                if self._is_slick_compound(ts.m_actualTyreCompound):
                    return self.COMPOUND_MAP.get(TyreCompound(ts.m_actualTyreCompound), 1)

        return 1  # Default medium

    def _is_slick_compound(self, compound) -> bool:
        try:
            c = TyreCompound(compound)
            return c in (
                TyreCompound.F1_MODERN_C5,
                TyreCompound.F1_MODERN_C4,
                TyreCompound.F1_MODERN_C3,
                TyreCompound.F1_MODERN_C2,
                TyreCompound.F1_MODERN_C1,
                TyreCompound.F1_MODERN_C0,
                TyreCompound.F1_MODERN_C6,
            )
        except ValueError:
            return False
