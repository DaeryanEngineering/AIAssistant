# f1/weather_manager.py

from core.events import EventType


class WeatherManager:
    """
    Handles weather-related state transitions:
    - current weather changes
    - forecast changes
    - rain ETA changes
    - intensity changes
    - drying track
    - worsening track
    - crossover conditions
    Emits events to TelemetryState → EventRouter → EngineerBrain.
    """

    def __init__(self, telemetry_state):
        self.telemetry_state = telemetry_state

        # Cached state
        self.last_weather = None
        self.last_rain_intensity = None
        self.last_forecast = None
        self.last_rain_eta = None
        self.last_track_wetness = None

    # ---------------------------------------------------------
    # Internal helper
    # ---------------------------------------------------------
    def _emit(self, event_type, **payload):
        self.telemetry_state._emit(event_type, **payload)

    # ---------------------------------------------------------
    # Main update loop
    # ---------------------------------------------------------
    def update(self, session, status):
        """
        session: SessionData
        status: carStatus for player
        """

        # -----------------------------------------------------
        # CURRENT WEATHER
        # -----------------------------------------------------
        current_weather = session.m_weather  # 0=clear,1=light cloud,2=overcast,3=light rain,4=heavy rain,5=storm
        track_wetness = session.m_trackWetness  # 0–100 scale

        if self.last_weather is None:
            self.last_weather = current_weather

        if current_weather != self.last_weather:
            self._emit(EventType.WEATHER_CHANGED,
                       old=self.last_weather,
                       new=current_weather)

        # -----------------------------------------------------
        # FORECAST CHANGES
        # -----------------------------------------------------
        forecast = list(session.m_weatherForecastSamples)  # list of segments

        if self.last_forecast is None:
            self.last_forecast = forecast

        # Compare segment-by-segment
        for i, seg in enumerate(forecast):
            if i >= len(self.last_forecast):
                break

            old_seg = self.last_forecast[i]
            new_seg = seg

            # Weather type changed
            if new_seg.m_weather != old_seg.m_weather:
                self._emit(EventType.FORECAST_WEATHER_CHANGE,
                           segment=i,
                           old=old_seg.m_weather,
                           new=new_seg.m_weather)

            # Rain percentage changed significantly
            if abs(new_seg.m_rainPercentage - old_seg.m_rainPercentage) >= 10:
                self._emit(EventType.FORECAST_RAIN_CHANGE,
                           segment=i,
                           old=old_seg.m_rainPercentage,
                           new=new_seg.m_rainPercentage)

        # -----------------------------------------------------
        # RAIN ETA (first rain segment)
        # -----------------------------------------------------
        rain_eta = self._get_rain_eta_minutes(forecast)

        if rain_eta is not None:
            if self.last_rain_eta is None:
                self.last_rain_eta = rain_eta

            # Only announce meaningful changes
            if self.last_rain_eta is not None:
                if rain_eta <= 10 and self.last_rain_eta > 10:
                    self._emit(EventType.RAIN_SOON, minutes=rain_eta)

                if abs(rain_eta - self.last_rain_eta) >= 5:
                    self._emit(EventType.RAIN_ETA_UPDATE, minutes=rain_eta)

        # -----------------------------------------------------
        # CROSSOVER CONDITIONS (PRIORITY OVER DRYING/WORSENING)
        # -----------------------------------------------------
        current_tyre = status.m_tyreCompound  # 7=slicks, 8=inters, 9=full wets

        # Slicks → Inters
        if self._is_crossover_to_inters(session) and current_tyre != 8:
            self._emit(EventType.CROSSOVER_TO_INTERS)
            self.last_track_wetness = track_wetness
            self.last_weather = current_weather
            self.last_forecast = forecast
            self.last_rain_eta = rain_eta
            return

        # Inters → Slicks
        if self._is_crossover_to_slicks(session) and current_tyre != 7:
            self._emit(EventType.CROSSOVER_TO_SLICKS)
            self.last_track_wetness = track_wetness
            self.last_weather = current_weather
            self.last_forecast = forecast
            self.last_rain_eta = rain_eta
            return

        # Inters → Full Wets
        if self._is_crossover_to_full_wets(session) and current_tyre != 9:
            self._emit(EventType.CROSSOVER_TO_FULL_WETS)
            self.last_track_wetness = track_wetness
            self.last_weather = current_weather
            self.last_forecast = forecast
            self.last_rain_eta = rain_eta
            return

        # -----------------------------------------------------
        # RAIN INTENSITY (track wetness)
        # -----------------------------------------------------

        if self.last_track_wetness is None:
            self.last_track_wetness = track_wetness

        # Drying track
        if track_wetness < self.last_track_wetness - 5:
            self._emit(EventType.TRACK_DRYING,
                       wetness=track_wetness)

        # Worsening track
        if track_wetness > self.last_track_wetness + 5:
            self._emit(EventType.TRACK_WORSENING,
                       wetness=track_wetness)


        # -----------------------------------------------------
        # Update cached values
        # -----------------------------------------------------
        self.last_weather = current_weather
        self.last_track_wetness = track_wetness
        self.last_forecast = forecast
        self.last_rain_eta = rain_eta

    # ---------------------------------------------------------
    # Helper: detect rain ETA
    # ---------------------------------------------------------
    def _get_rain_eta_minutes(self, forecast):
        for seg in forecast:
            if seg.m_rainPercentage >= 20:
                return seg.m_timeOffset
        return None

    # ---------------------------------------------------------
    # Helper: crossover detection
    # ---------------------------------------------------------
    def _is_crossover_to_full_wets(self, session):
        return (
            session.m_trackWetness > 60 and session.m_weather in (4, 5) # storm
        )
    
    def _is_crossover_to_inters(self, session):
        return (
            session.m_trackWetness > 20 and
            session.m_weather in (3, 4)  # light/heavy rain
        )

    def _is_crossover_to_slicks(self, session):
        return (
            session.m_trackWetness < 10 and
            session.m_weather in (0, 1, 2)  # dry conditions
        )
