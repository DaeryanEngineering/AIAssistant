# core/radio_lines.py

import re
import random
from .career_tracker import CareerTracker


DRIVER_NAME = "Shawn"


class RadioLines:
    """
    Snarky-to-warm radio line generator, Lines evolve over an 11-year career arc, """

    # =========================================================
    # NAME INJECTION
    # =========================================================

    @staticmethod
    def _maybe_name(career: CareerTracker) -> str:
        if random.random() < career.name_frequency:
            return f", {DRIVER_NAME}"
        return ""

    @staticmethod
    def _format(line: str, career: CareerTracker, **kwargs) -> str:
        name = RadioLines._maybe_name(career)
        return line.format(name=name, **kwargs)

    # =========================================================
    # GAP FORMATTING
    # =========================================================

    GAP_SPEECH_MAP = {
        0.0:  "zero",
        0.1:  "one-tenth",
        0.2:  "two-tenths",
        0.3:  "three-tenths",
        0.4:  "four-tenths",
        0.5:  "five-tenths",
        0.6:  "six-tenths",
        0.7:  "seven-tenths",
        0.8:  "eight-tenths",
        0.9:  "nine-tenths",
        1.0:  "one second",
        1.1:  "one-point-one",
        1.2:  "one-point-two",
        1.3:  "one-point-three",
        1.4:  "one-point-four",
        1.5:  "one-point-five",
        1.6:  "one-point-six",
        1.7:  "one-point-seven",
        1.8:  "one-point-eight",
        1.9:  "one-point-nine",
        2.0:  "two seconds",
        2.1:  "two-point-one",
        2.2:  "two-point-two",
        2.3:  "two-point-three",
        2.4:  "two-point-four",
        2.5:  "two-point-five",
        2.6:  "two-point-six",
        2.7:  "two-point-seven",
        2.8:  "two-point-eight",
        2.9:  "two-point-nine",
        3.0:  "three seconds",
        3.1:  "three-point-one",
        3.2:  "three-point-two",
        3.3:  "three-point-three",
        3.4:  "three-point-four",
        3.5:  "three-point-five",
        3.6:  "three-point-six",
        3.7:  "three-point-seven",
        3.8:  "three-point-eight",
        3.9:  "three-point-nine",
        4.0:  "four seconds",
        4.1:  "four-point-one",
        4.2:  "four-point-two",
        4.3:  "four-point-three",
        4.4:  "four-point-four",
        4.5:  "four-point-five",
        4.6:  "four-point-six",
        4.7:  "four-point-seven",
        4.8:  "four-point-eight",
        4.9:  "four-point-nine",
        5.0:  "five seconds",
        5.1:  "five-point-one",
        5.2:  "five-point-two",
        5.3:  "five-point-three",
        5.4:  "five-point-four",
        5.5:  "five-point-five",
        5.6:  "five-point-six",
        5.7:  "five-point-seven",
        5.8:  "five-point-eight",
        5.9:  "five-point-nine",
        6.0:  "six seconds",
        6.1:  "six-point-one",
        6.2:  "six-point-two",
        6.3:  "six-point-three",
        6.4:  "six-point-four",
        6.5:  "six-point-five",
        6.6:  "six-point-six",
        6.7:  "six-point-seven",
        6.8:  "six-point-eight",
        6.9:  "six-point-nine",
        7.0:  "seven seconds",
        7.1:  "seven-point-one",
        7.2:  "seven-point-two",
        7.3:  "seven-point-three",
        7.4:  "seven-point-four",
        7.5:  "seven-point-five",
        7.6:  "seven-point-six",
        7.7:  "seven-point-seven",
        7.8:  "seven-point-eight",
        7.9:  "seven-point-nine",
        8.0:  "eight seconds",
        8.1:  "eight-point-one",
        8.2:  "eight-point-two",
        8.3:  "eight-point-three",
        8.4:  "eight-point-four",
        8.5:  "eight-point-five",
        8.6:  "eight-point-six",
        8.7:  "eight-point-seven",
        8.8:  "eight-point-eight",
        8.9:  "eight-point-nine",
        9.0:  "nine seconds",
        9.1:  "nine-point-one",
        9.2:  "nine-point-two",
        9.3:  "nine-point-three",
        9.4:  "nine-point-four",
        9.5:  "nine-point-five",
        9.6:  "nine-point-six",
        9.7:  "nine-point-seven",
        9.8:  "nine-point-eight",
        9.9:  "nine-point-nine",
        10.0: "ten seconds"
    }

    @staticmethod
    def _format_large_gap(gap: float) -> str:
        """Format large gaps (10+ seconds)."""
        if gap < 20:
            sec = int(round(gap))
            return f"{sec} seconds"
        if gap < 60:
            sec = int(round(gap / 5) * 5)
            return f"{sec} seconds"
        if gap < 120:
            minutes = int(gap // 60)
            seconds = int(gap % 60)
            if seconds < 5:
                return f"{minutes} minute"
            return f"{minutes} minute {seconds} seconds"
        minutes = int(round(gap / 60))
        return f"{minutes} minutes"

    @staticmethod
    def format_gap(seconds: float) -> str:
        """Format gap into spoken text using MAP."""
        if seconds < 0:
            return ""
        if seconds <= 10.0:
            key = round(seconds * 10) / 10
            return RadioLines.GAP_SPEECH_MAP.get(key, RadioLines._format_large_gap(seconds))
        return RadioLines._format_large_gap(seconds)

    @staticmethod
    def format_gap_text(seconds: float | None, is_lapped: bool = False) -> str:
        """Format gap into spoken text."""
        if seconds is None or seconds < 0.1:
            return ""
        return RadioLines.format_gap(seconds)

    # =========================================================
    # OBJECTIVE LINES (existing)
    # =========================================================

    _objective_start = {
        "LAP_TIME": {
            "sharp": [
                "Copy that, Lap time objective noted, Let's see if you can actually deliver{name}, ",
                "Right, Lap time tracking, I'll believe it when I see it{name}, ",
                "Objective logged, Don't make me regret tracking this for you, ",
            ],
            "professional": [
                "Lap time objective logged, Let's see what you can do{name}, ",
                "Copy, Lap time target noted, I'll be watching, ",
                "Right, Lap time tracking, Stay smooth and hit the marks, ",
            ],
            "supportive": [
                "Lap time objective set, You've got this{name}, ",
                "Copy that, Lap time target locked in, Let's find the time, ",
                "Lap time noted, We'll get there together, ",
            ],
            "partnership": [
                "Lap time objective, Let's find that time together{name}, ",
                "Copy, Lap time target set, We'll work through it, ",
                "Lap time noted, I know you'll nail it, ",
            ],
        },
        "TYRE_MANAGEMENT": {
            "sharp": [
                "Tyre management, Try not to shred them this time{name}, ",
                "Copy, Tyre management active, Your tyres, your problem, ",
                "Tyre tracking, Don't cook them on the first lap, Shawn, ",
            ],
            "professional": [
                "Tyre management objective logged, Keep temps in the window, ",
                "Copy, Tyre management, Smooth inputs, long stints, ",
                "Tyre tracking active, Manage the deg{name}, ",
            ],
            "supportive": [
                "Tyre management, Keep them alive and we'll be strong at the end, ",
                "Copy, Tyre tracking, You've got good feel for this now{name}, ",
                "Tyre management noted, Trust your instincts on wear, ",
            ],
            "partnership": [
                "Tyre management, We know how to handle this now{name}, ",
                "Copy, Tyre tracking, You've always been good at this, ",
                "Tyre objective set, We'll manage it together, ",
            ],
        },
        "FUEL_SAVING": {
            "sharp": [
                "Fuel saving, Lift and coast, Shawn, I know you hate it but it's not negotiable, ",
                "Fuel saving engaged, Try not to be a hero on the throttle{name}, ",
                "Copy, Fuel saving, Short-shifting starts now, ",
            ],
            "professional": [
                "Fuel saving objective logged, Manage the delta, ",
                "Copy, Fuel saving, Lift early, coast long, ",
                "Fuel tracking active, Stay under the target usage{name}, ",
            ],
            "supportive": [
                "Fuel saving, You're good at this — just keep it consistent, ",
                "Copy, Fuel management, We'll make the numbers work{name}, ",
                "Fuel objective set, Smooth hands, smooth feet, ",
            ],
            "partnership": [
                "Fuel saving, We'll manage it like we always do{name}, ",
                "Copy, Fuel tracking, You know the drill, ",
                "Fuel objective noted, We'll get it done, ",
            ],
        },
        "ERS_MANAGEMENT": {
            "sharp": [
                "ERS management, Don't dump it all in one lap{name}, ",
                "Copy, ERS tracking, Use it wisely, or don't, Your call, ",
                "ERS objective logged, Try not to run out before the line, ",
            ],
            "professional": [
                "ERS management objective set, Harvest and deploy smartly, ",
                "Copy, ERS tracking, Balance the deployment across the lap, ",
                "ERS management, Watch the state of charge{name}, ",
            ],
            "supportive": [
                "ERS management, You've got good rhythm with this now, ",
                "Copy, ERS tracking, Deploy on the straights, harvest under braking, ",
                "ERS objective logged, Trust your feel for it{name}, ",
            ],
            "partnership": [
                "ERS management, We know the balance now{name}, ",
                "Copy, ERS tracking, You've always managed this well, ",
                "ERS objective set, We'll dial it in together, ",
            ],
        },
        "SECTOR_IMPROVEMENT": {
            "sharp": [
                "Sector improvement, Find time somewhere{name}, ",
                "Copy, Sector target noted, Don't leave anything on the table, ",
                "Sector tracking active, Push where it counts, ",
            ],
            "professional": [
                "Sector improvement objective logged, Focus on the weak spots, ",
                "Copy, Sector target set, Attack the problem areas, ",
                "Sector tracking, Let's find the tenths{name}, ",
            ],
            "supportive": [
                "Sector improvement, You know where the time is, ",
                "Copy, Sector objective, We'll chip away at it{name}, ",
                "Sector tracking active, Smooth is fast, ",
            ],
            "partnership": [
                "Sector improvement, We'll find the time together{name}, ",
                "Copy, Sector target, You know this track inside out now, ",
                "Sector objective set, Let's work through it, ",
            ],
        },
        "RACECRAFT": {
            "sharp": [
                "Racecraft objective, Try not to lose positions{name}, ",
                "Copy, Racecraft tracking, Think before you dive bomb, ",
                "Racecraft objective logged, Patience is not your strong suit, but try, ",
            ],
            "professional": [
                "Racecraft objective set, Pick your moments, ",
                "Copy, Racecraft tracking, Stay calm in the pack, ",
                "Racecraft management, Smart overtakes only{name}, ",
            ],
            "supportive": [
                "Racecraft objective, You've gotten much better at this, ",
                "Copy, Racecraft tracking, Trust your race sense{name}, ",
                "Racecraft logged, You know when to push and when to wait, ",
            ],
            "partnership": [
                "Racecraft objective, You've mastered this over the years{name}, ",
                "Copy, Racecraft tracking, You always know the right move, ",
                "Racecraft set, We'll work the race together, ",
            ],
        },
        "STRATEGY": {
            "sharp": [
                "Strategy objective, Try to stick to the plan{name}, ",
                "Copy, Strategy tracking, Don't go rogue on me, ",
                "Strategy logged, Follow the call, even when it hurts, ",
            ],
            "professional": [
                "Strategy objective set, Trust the plan, ",
                "Copy, Strategy tracking, We'll adjust as we go, ",
                "Strategy management, Stay disciplined{name}, ",
            ],
            "supportive": [
                "Strategy objective, You're good at executing the plan, ",
                "Copy, Strategy tracking, We'll adapt when we need to{name}, ",
                "Strategy logged, You've always been reliable on this, ",
            ],
            "partnership": [
                "Strategy objective, We'll call it together{name}, ",
                "Copy, Strategy tracking, We've always been in sync on this, ",
                "Strategy set, We'll nail it like we always do, ",
            ],
        },
        "DELTA_TARGET": {
            "sharp": [
                "Delta target, Hit the number or don't bother{name}, ",
                "Copy, Delta tracking, Keep it positive or come in, ",
                "Delta objective logged, The number is the number, ",
            ],
            "professional": [
                "Delta target objective set, Manage the gap, ",
                "Copy, Delta tracking, Stay within the window, ",
                "Delta management, Watch the delta at all times{name}, ",
            ],
            "supportive": [
                "Delta target, You've got good pace for this, ",
                "Copy, Delta tracking, Keep it smooth and consistent{name}, ",
                "Delta objective logged, You know how to manage this, ",
            ],
            "partnership": [
                "Delta target, We'll manage it together{name}, ",
                "Copy, Delta tracking, You always find the rhythm, ",
                "Delta objective set, We'll get it done, ",
            ],
        },
        "WEATHER": {
            "sharp": [
                "Weather objective, Keep me updated on the grip{name}, ",
                "Copy, Weather tracking, Don't wait too long to call it, ",
                "Weather objective logged, Feel the track and report back, ",
            ],
            "professional": [
                "Weather objective set, Monitor conditions closely, ",
                "Copy, Weather tracking, Call the crossover point when you feel it, ",
                "Weather management, Stay alert on grip levels{name}, ",
            ],
            "supportive": [
                "Weather objective, Your feel for conditions is good, ",
                "Copy, Weather tracking, Trust your instincts on the crossover{name}, ",
                "Weather logged, You've always been sharp on this, ",
            ],
            "partnership": [
                "Weather objective, We'll read it together{name}, ",
                "Copy, Weather tracking, You know what to listen for, ",
                "Weather set, We'll call it as a team, ",
            ],
        },
        "FORMATION": {
            "sharp": [
                "Formation objective, Warm the tyres and don't stall{name}, ",
                "Copy, Formation tracking, Check the brakes, check the tyres, ",
                "Formation objective logged, Don't overthink it, ",
            ],
            "professional": [
                "Formation objective set, Follow the procedure, ",
                "Copy, Formation tracking, Warm everything up properly, ",
                "Formation management, Stay focused{name}, ",
            ],
            "supportive": [
                "Formation objective, You know the routine by now, ",
                "Copy, Formation tracking, Smooth and controlled{name}, ",
                "Formation logged, You've always been solid on these, ",
            ],
            "partnership": [
                "Formation objective, We've done this a hundred times{name}, ",
                "Copy, Formation tracking, You know exactly what to do, ",
                "Formation set, Let's get it done, ",
            ],
        },
        "SAFETY_CAR": {
            "sharp": [
                "Safety car objective, Keep your delta positive{name}, ",
                "Copy, SC tracking, Don't lose temps, don't lose focus, ",
                "Safety car objective logged, Stay in the window, ",
            ],
            "professional": [
                "Safety car objective set, Manage the delta and the temps, ",
                "Copy, SC tracking, Stay sharp for the restart, ",
                "Safety car management, Keep the tyres alive{name}, ",
            ],
            "supportive": [
                "Safety car objective, You handle these well, ",
                "Copy, SC tracking, Stay calm and manage the gap{name}, ",
                "Safety car logged, You've always been disciplined under SC, ",
            ],
            "partnership": [
                "Safety car objective, We know the drill{name}, ",
                "Copy, SC tracking, You always manage these perfectly, ",
                "Safety car set, We'll handle it together, ",
            ],
        },
    }

    _objective_start_generic = {
        "sharp": [
            "Objective received: {description}, I'll track it, Whether you execute is another question{name}, ",
            "Noted: {description}, Tracking now, Don't disappoint me{name}, ",
            "Objective logged: {description}, Let's see if you can pull it off, ",
        ],
        "professional": [
            "Objective received: {description}, Tracking now, ",
            "Copy: {description}, I'll keep an eye on it{name}, ",
            "Noted: {description}, Objective active, ",
        ],
        "supportive": [
            "Objective received: {description}, We'll work through it{name}, ",
            "Copy: {description}, Tracking now, You've got this, ",
            "Noted: {description}, Let's make it happen, ",
        ],
        "partnership": [
            "Objective received: {description}, We're on it{name}, ",
            "Copy: {description}, We'll handle it together, ",
            "Noted: {description}, Let's get it done, ",
        ],
    }

    _objective_pass = {
        "sharp": [
            "Objective complete, I'm impressed{name}, Truly, ",
            "Done it, About time, ",
            "Objective passed, See? You can follow instructions when you want to{name}, ",
            "Nice work, I'll add it to the list of things you've actually gotten right, ",
            "Confirmed, Objective complete, Don't let it go to your head{name}, ",
        ],
        "professional": [
            "Objective complete, Solid work{name}, ",
            "Confirmed, Well executed, ",
            "Objective passed, Good job, Shawn, ",
            "Done it, Clean execution{name}, ",
            "Objective complete, That's how it's done, ",
        ],
        "supportive": [
            "Objective complete, Great work{name}, ",
            "Confirmed, You nailed it, ",
            "Objective passed, Really well driven, Shawn, ",
            "Done it, I knew you could{name}, ",
            "Objective complete, Excellent execution, ",
        ],
        "partnership": [
            "Objective complete, We make a good team{name}, ",
            "Confirmed, Another one done together, ",
            "Objective passed, That's what we do, Shawn, ",
            "Done it, Always satisfying when the plan works{name}, ",
            "Objective complete, We're in sync, ",
        ],
    }

    _objective_fail = {
        "sharp": [
            "Objective failed, I'm not even surprised{name}, ",
            "Failed, Reset when you're ready to try again, Or don't, Your call, ",
            "Objective failed, We'll pretend that didn't happen{name}, ",
            "That's a fail, I've seen better from AI drivers, Shawn, ",
            "Failed, The objective, not you, Well... maybe you too{name}, ",
        ],
        "professional": [
            "Objective failed, Reset when you're ready{name}, ",
            "Failed, No big deal, We'll try again, ",
            "Objective didn't stick, Move on and focus on the next one, ",
            "Failed, Shake it off, Shawn, Next objective, ",
            "Objective failed, We'll get the next one{name}, ",
        ],
        "supportive": [
            "Objective failed, It happens, We'll get the next one{name}, ",
            "Failed, Don't dwell on it, Focus forward, ",
            "Objective didn't land, You'll nail the next one, Shawn, ",
            "Failed, No worries, We're still in a good spot{name}, ",
            "Objective failed, Shake it off and keep pushing, ",
        ],
        "partnership": [
            "Objective failed, Doesn't matter, We'll get the next one{name}, ",
            "Failed, We'll bounce back, We always do, ",
            "Objective didn't stick, We're still strong, Shawn, ",
            "Failed, Not a problem, We've got plenty more to go{name}, ",
            "Objective failed, We'll regroup and move forward, ",
        ],
    }

    _objective_cancel = {
        "sharp": [
            "Objective cancelled, Smart call, or are you just avoiding the challenge{name}?",
            "Cancelled, I respect the honesty, ",
            "Objective scrubbed, Moving on, ",
            "Cancelled, Probably for the best{name}, ",
            "Objective cancelled, I won't pretend I'm surprised, ",
        ],
        "professional": [
            "Objective cancelled, Understood{name}, ",
            "Cancelled, Moving on to the next one, ",
            "Objective scrubbed, We'll set a new one when you're ready, ",
            "Cancelled, Copy that{name}, ",
            "Objective cancelled, Reset and refocus, ",
        ],
        "supportive": [
            "Objective cancelled, No problem, we'll set a new one when you're ready{name}, ",
            "Cancelled, Sometimes it's the right call, ",
            "Objective scrubbed, We'll find a better one for you, Shawn, ",
            "Cancelled, All good, What's next{name}?",
            "Objective cancelled, We'll pivot to something more useful, ",
        ],
        "partnership": [
            "Objective cancelled, We'll find a better one together{name}, ",
            "Cancelled, No worries, What should we focus on instead?",
            "Objective scrubbed, We'll adjust the plan, Shawn, ",
            "Cancelled, We'll set something more relevant{name}, ",
            "Objective cancelled, We're still on track overall, ",
        ],
    }

    # =========================================================
    # TITLE SCENARIOS
    # =========================================================

    _f2_championship = [
        "F2 champion, You belong here, Shawn, F1 won't know what hit it, ",
        "F2 title, You earned this, Next stop: the big league{name}, ",
        "F2 champion, I knew you had it in you, F1 is next, ",
    ]

    _first_f1_title = [
        "World Champion, Shawn... you're World Champion, I always believed you could do this, Always, ",
        "You did it, World Champion, I've been waiting to say this since day one{name}, ",
        "World Champion, After everything we've been through... this is it, You're the best, ",
    ]

    _consecutive_2 = [
        "Back-to-back, Two titles, Nobody can say it was luck{name}, ",
        "Two in a row, You're proving it wasn't a fluke, ",
        "Back-to-back champion, Impressive, Shawn, Truly, ",
    ]

    _consecutive_3 = [
        "Three in a row, You're building a legacy{name}, ",
        "Three consecutive titles, History is starting to notice, Shawn, ",
        "Three-peat, You're not just winning — you're dominating, ",
    ]

    _consecutive_4_to_7 = [
        "{n} titles in a row, You're not just winning anymore, you're dominating{name}, ",
        "{n} consecutive championships, I've run out of ways to be impressed, Shawn, ",
        "Title number {n}, At this point it's just expected, isn't it{name}?",
        "{n} in a row, The record books are starting to look very one-sided, ",
    ]

    _consecutive_8_plus = [
        "Another one, That's {n} now, When I started with you in F2, I never imagined this{name}, ",
        "{n} titles, I stopped counting after a while, You never did, ",
        "Title {n}, A decade ago you were fighting for F2 points, Look at you now{name}, ",
        "{n} championships, We've come a long way from that first F2 season, Shawn, ",
    ]

    _year_5 = [
        "Five years, We've been together a while now, Shawn, Let's keep it going, ",
        "Year five, Half a decade of this, Not bad for a partnership{name}, ",
        "Five years together, Through everything, Let's keep pushing, ",
    ]

    _year_10 = [
        "Ten years, A decade of this, I can't imagine doing it with anyone else, Shawn, ",
        "Ten years together, Through everything, I'm not going anywhere{name}, ",
        "A decade, Ten years of races, titles, and everything in between, Wouldn't trade it, ",
    ]

    # =========================================================
    # RACE EVENT LINES
    # =========================================================

    _race_events = {
        # ---------------------------------------------------------
        # RACE GAP — every racing lap, not lap 1, not SC/VSC/Red
        # Structure: P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}.
        # All lines include explicit "ahead" and "behind".
        # P1-P5 in supportive/partnership get encouragement, P6+ straight data.
        # ---------------------------------------------------------
        "race_gap": {
            "sharp": [
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
                "P{position}, Gap to {ahead} ahead: {gap}. {behind} {behind_gap} behind, ",
                "P{position}. {ahead} {gap} ahead. {behind} {behind_gap} behind, ",
                "P{position}. {gap} to {ahead} ahead. {behind} {behind_gap} behind, ",
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
            ],
            "professional": [
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
                "P{position}, Gap to {ahead} ahead: {gap}. {behind} {behind_gap} behind, ",
                "P{position}. {ahead} {gap} ahead. {behind} {behind_gap} behind, ",
                "P{position}. {gap} to {ahead} ahead. {behind} {behind_gap} behind, ",
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
            ],
            "supportive_p1_p5": [
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, Looking good, ",
                "P{position}, Gap to {ahead} ahead: {gap}. {behind} {behind_gap} behind, Solid, ",
                "P{position}. {ahead} {gap} ahead. {behind} {behind_gap} behind, Looking good, ",
                "P{position}. {gap} to {ahead} ahead. {behind} {behind_gap} behind, Solid, ",
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, Good, ",
            ],
            "supportive_p6_plus": [
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
                "P{position}, Gap to {ahead} ahead: {gap}. {behind} {behind_gap} behind, ",
                "P{position}. {ahead} {gap} ahead. {behind} {behind_gap} behind, ",
                "P{position}. {gap} to {ahead} ahead. {behind} {behind_gap} behind, ",
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
            ],
            "partnership_p1_p5": [
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, Looking good, ",
                "P{position}, Gap to {ahead} ahead: {gap}. {behind} {behind_gap} behind, Solid, ",
                "P{position}. {ahead} {gap} ahead. {behind} {behind_gap} behind, Looking good, ",
                "P{position}. {gap} to {ahead} ahead. {behind} {behind_gap} behind, Solid, ",
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, Good, ",
            ],
            "partnership_p6_plus": [
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
                "P{position}, Gap to {ahead} ahead: {gap}. {behind} {behind_gap} behind, ",
                "P{position}. {ahead} {gap} ahead. {behind} {behind_gap} behind, ",
                "P{position}. {gap} to {ahead} ahead. {behind} {behind_gap} behind, ",
                "P{position}. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
            ],
        },

        # ---------------------------------------------------------
        # RACE FINISH — P1
        # ---------------------------------------------------------
        "race_finish_p1": {
            "sharp": [
                "Race complete, P1, ",
                "P1, Good work, ",
                "P1, Brought it home, ",
            ],
            "professional": [
                "Race complete, P1, ",
                "P1, Good work, ",
                "P1, Brought it home, ",
            ],
            "supportive": [
                "Race complete, P1, ",
                "P1, Good work today, ",
                "P1, That's a solid win, ",
            ],
            "partnership": [
                "Race complete, P1, ",
                "P1, Like we always do, ",
                "P1, Good work today, ",
            ],
        },

        # ---------------------------------------------------------
        # RACE FINISH — P2 to P6
        # ---------------------------------------------------------
        "race_finish_p2_p6": {
            "sharp": [
                "Race complete, P{position}, ",
                "P{position}, Not bad, ",
                "P{position}, Solid result, ",
            ],
            "professional": [
                "Race complete, P{position}, ",
                "P{position}, Good result, ",
                "P{position}, ",
            ],
            "supportive": [
                "Race complete, P{position}, A solid finish, ",
                "P{position}, Well driven, ",
                "P{position}, That's a good result, ",
            ],
            "partnership": [
                "Race complete, P{position}, ",
                "P{position}, A solid finish, We did well today, ",
                "P{position}, Good work today, ",
            ],
        },

        # ---------------------------------------------------------
        # RACE FINISH — P7 to P11
        # ---------------------------------------------------------
        "race_finish_p7_p11": {
            "sharp": [
                "Race complete, P{position}, Points, ",
                "P{position}, On the board, ",
                "P{position}, Points secured, ",
            ],
            "professional": [
                "Race complete, P{position}, ",
                "P{position}, Points, ",
                "P{position}, On the board, ",
            ],
            "supportive": [
                "Race complete, P{position}, A fighting finish, ",
                "P{position}, Points secured, ",
                "P{position}, That's racing, ",
            ],
            "partnership": [
                "Race complete, P{position}, Points, ",
                "P{position}, We fought for that one, ",
                "P{position}, On the board, ",
            ],
        },

        # ---------------------------------------------------------
        # RACE FINISH — P12 to P16
        # ---------------------------------------------------------
        "race_finish_p12_p16": {
            "sharp": [
                "Race complete, P{position}, Outside the points, ",
                "P{position}, Not the result we wanted, ",
                "P{position}, Just outside, ",
            ],
            "professional": [
                "Race complete, P{position}, ",
                "P{position}, Outside the points, ",
                "P{position}, Not the day we needed, ",
            ],
            "supportive": [
                "Race complete, P{position}, Outside the points, but we gave it a go, ",
                "P{position}, Not quite, ",
                "P{position}, We'll come back stronger, ",
            ],
            "partnership": [
                "Race complete, P{position}, ",
                "P{position}, Outside the points, We'll work on it, ",
                "P{position}, We'll regroup, ",
            ],
        },

        # ---------------------------------------------------------
        # RACE FINISH — P17 to P22
        # ---------------------------------------------------------
        "race_finish_p17_p22": {
            "sharp": [
                "Race complete, P{position}, Difficult day, ",
                "P{position}, Not the result we deserved, ",
                "P{position}, ",
            ],
            "professional": [
                "Race complete, P{position}, ",
                "P{position}, A tough one, ",
                "P{position}, Not the day, ",
            ],
            "supportive": [
                "Race complete, P{position}, A difficult day, We'll regroup, ",
                "P{position}, Not the result we wanted, ",
                "P{position}, We'll come back from this, ",
            ],
            "partnership": [
                "Race complete, P{position}, ",
                "P{position}, We'll get them next time, ",
                "P{position}, A tough day, We'll work through it together, ",
            ],
        },

        # ---------------------------------------------------------
        # RACE WIN
        # ---------------------------------------------------------
        "race_win": {
            "sharp": [
                "Race win, Incredible, ",
                "You did it, P1, ",
                "P1, That's the way to do it, ",
            ],
            "professional": [
                "Race win, Incredible drive, ",
                "P1, Well done, ",
                "Race win, That's how it's done, ",
            ],
            "supportive": [
                "Race win, You did it, Shawn, ",
                "P1, Incredible, Well done, ",
                "Race win, That was driven beautifully, ",
            ],
            "partnership": [
                "Race win, We did it, ",
                "P1, Like we always knew you could, ",
                "Race win, Together, ",
            ],
        },

        # ---------------------------------------------------------
        # CONSTRUCTORS CHAMPIONSHIP
        # ---------------------------------------------------------
        "constructors_title": {
            "sharp": [
                "P{position}, That seals it. {team} has won the Constructors' Championship, ",
                "Constructors' title. {team}, That's done, ",
                "{team} wins the Constructors', P{position}, ",
            ],
            "professional": [
                "P{position}. {team} wins the Constructors' Championship, ",
                "Constructors' Championship. {team}, P{position}, Done, ",
                "{team} takes the Constructors', P{position}, ",
            ],
            "supportive": [
                "P{position}, That seals it. {team} has won the Constructors' Championship, Incredible effort from the whole team, ",
                "Constructors' Championship. {team}, P{position}, Well done, everyone, ",
                "{team} wins the Constructors', P{position}, ",
            ],
            "partnership": [
                "P{position}. {team}, We did this together, ",
                "Constructors' Championship. {team}, P{position}, Like we always knew we would, ",
                "{team} wins the Constructors', P{position}, All of us, ",
            ],
        },

        # ---------------------------------------------------------
        # DRIVERS CHAMPIONSHIP — First time
        # ---------------------------------------------------------
        "drivers_title_first": {
            "sharp": [
                "Shawn… you're World Champion, Every step of the way, ",
            ],
            "professional": [
                "World Champion, You did it, Shawn, ",
            ],
            "supportive": [
                "Shawn… you're World Champion, I always knew you could, ",
            ],
            "partnership": [
                "World Champion, We did this together, Shawn, Every single step, ",
            ],
        },

        # ---------------------------------------------------------
        # DRIVERS CHAMPIONSHIP — Consecutive
        # ---------------------------------------------------------
        "drivers_title_consecutive": {
            "sharp": [
                "Back-to-back, You're World Champion again, ",
                "Another one, World Champion, ",
                "World Champion, Again, ",
            ],
            "professional": [
                "World Champion, Another one, ",
                "Back-to-back, Well done, ",
                "World Champion, You did it again, ",
            ],
            "supportive": [
                "World Champion, Another one, You never stopped, ",
                "Back-to-back, Incredible, ",
                "World Champion again, Well done, Shawn, ",
            ],
            "partnership": [
                "World Champion, Like we always knew it would happen, ",
                "Another one, We did this together, ",
                "World Champion, Right where we belong, ",
            ],
        },

        # ---------------------------------------------------------
        # FORMATION LAP
        # ---------------------------------------------------------
        "formation_lap": {
            "sharp": [
                "Formation lap, Warm the tyres, Check the brakes",
                "Formation, Don't stall, Warm the tyres",
                "Mode formation, Procedure",
            ],
            "professional": [
                "Formation lap, Warm the tyres and brakes",
                "Formation mode, Procedure",
                "Formation, Stay close to the car ahead",
            ],
            "supportive": [
                "Formation lap, You've done this a thousand times",
                "Formation, Warm up and stay focused",
                "Formation lap, You've got this",
            ],
            "partnership": [
                "Formation lap, Like we always do",
                "Formation, We know this one",
                "Formation lap, Stay right where you are",
            ],
        },

        # ---------------------------------------------------------
        # FIND GRID SLOT
        # ---------------------------------------------------------
        "find_grid_slot": {
            "sharp": [
                "Find your grid slot, Now",
                "Grid slot, Don't overshoot",
            ],
            "professional": [
                "Grid slot, Park it",
                "Find your position, Park it clean",
            ],
            "supportive": [
                "Find your box, Park it clean",
                "Almost there, Grid slot",
            ],
            "partnership": [
                "Your box, We know where it is",
                "Grid slot, Park it",
            ],
        },

        # ---------------------------------------------------------
        # RACE START
        # ---------------------------------------------------------
        "race_start": {
            "sharp": [
                "Mode launch, Turn 1, Don't be a hero",
                "Lights out, Go",
                "Launch, Be smart into Turn 1",
                "Go, No mistakes",
                "This is it, Launch",
            ],
            "professional": [
                "Mode launch, Be clean into Turn 1",
                "Lights out, Stay focused",
                "Go, Good start",
                "Launch, Smart into Turn 1",
                "Green light, Let's race",
            ],
            "supportive": [
                "Mode launch, Trust yourself, Go",
                "Lights out, You've got this",
                "Go, Let's see what you've got",
                "Mode launch, Enjoy it",
                "Launch, Let's race",
            ],
            "partnership": [
                "Mode launch, Let's go",
                "Lights out, Let's do what we do",
                "Launch, We've got this",
                "Go, Like we always do",
                "This is it, Together",
            ],
        },

        # ---------------------------------------------------------
        # SAFETY CAR DEPLOYED
        # ---------------------------------------------------------
        "safety_car_deployed": {
            "sharp": [
                "Safety car, Delta positive, Don't lose time, ",
                "SC deployed, Slow down, Keep the gap, ",
                "Safety car, Stay in the window, ",
                "SC, Delta positive or box, ",
            ],
            "professional": [
                "Safety car deployed, Delta positive, ",
                "SC out, Manage the gap and the temps, ",
                "Safety car, Keep it clean, ",
                "SC deployed, Reduce pace, keep the gap, ",
            ],
            "supportive": [
                "Safety car, Stay calm, Delta positive, ",
                "SC, You've handled these before, ",
                "Safety car, Keep the tyres warm and the delta in the window, ",
            ],
            "partnership": [
                "Safety car, Like we always do, Delta positive, ",
                "SC, We've got this, ",
                "Safety car, Stay right where you are, ",
                "SC, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # SAFETY CAR IN THIS LAP
        # ---------------------------------------------------------
        "safety_car_in_this_lap": {
            "sharp": [
                "SC in this lap, No overtaking until the line, ",
                "Safety car in, Don't cross until the line, ",
                "SC this lap, Hold position, ",
            ],
            "professional": [
                "Safety car in this lap, No overtaking until the line, ",
                "SC in, Maintain position, ",
                "Safety car in, Hold your grid position, ",
            ],
            "supportive": [
                "SC in this lap, Hold your position, ",
                "Safety car, One more lap, Stay calm, ",
                "SC in, Almost there, ",
            ],
            "partnership": [
                "SC in this lap, Like we always do, Hold it, ",
                "Safety car in, Almost there, ",
                "SC in, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # SAFETY CAR END (green flag)
        # ---------------------------------------------------------
        "safety_car_end": {
            "sharp": [
                "Green flag, Go, ",
                "SC ending, Green, Push now, ",
                "Green, Go, Push, ",
                "Green flag, Racing, ",
            ],
            "professional": [
                "Safety car ending, Green flag, ",
                "SC ending, Green flag, Let's go, ",
                "Green flag, Racing, ",
                "Green, Push now, ",
            ],
            "supportive": [
                "Green flag, Back to it, ",
                "SC ending, Go, You've got this, ",
                "Green, Let's race, ",
            ],
            "partnership": [
                "Green flag, Like we always do, ",
                "SC ending, Let's race, ",
                "Green, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # VSC DEPLOYED
        # ---------------------------------------------------------
        "vsc_deployed": {
            "sharp": [
                "VSC, Delta positive, Stay in the window, ",
                "Virtual safety car, Reduce pace, ",
                "VSC, Watch the delta, ",
            ],
            "professional": [
                "Virtual safety car, Delta positive, ",
                "VSC, Manage the gap, ",
                "Virtual safety car, Reduce pace, ",
            ],
            "supportive": [
                "VSC, Stay calm, Keep the delta, ",
                "VSC, You've handled these, ",
                "Virtual safety car, Stay in the window, ",
            ],
            "partnership": [
                "VSC, Like we always do, ",
                "Virtual safety car, We'll manage it, ",
                "VSC, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # VSC END
        # ---------------------------------------------------------
        "vsc_end": {
            "sharp": [
                "VSC ending, Get ready, ",
                "VSC in, Short one, Go, ",
                "VSC ending, Almost green, ",
            ],
            "professional": [
                "VSC ending, Almost green, ",
                "VSC in, Get ready to go, ",
                "VSC ending, Almost there, ",
            ],
            "supportive": [
                "VSC ending, Almost there, ",
                "VSC in, Stay sharp, ",
                "VSC ending, Almost green, ",
            ],
            "partnership": [
                "VSC ending, Almost green, ",
                "VSC in, Ready when you are, ",
                "VSC ending, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # RED FLAG
        # ---------------------------------------------------------
        "red_flag": {
            "sharp": [
                "Red flag, Box, Now, ",
                "Red flag, Return to the pits, End of it, ",
            ],
            "professional": [
                "Red flag, Return to the pits, ",
                "Red flag, Head to the garage, ",
                "Red flag, Back to the pits, ",
            ],
            "supportive": [
                "Red flag, Back to the pits, It's over, ",
                "Red flag, Head to the garage, ",
            ],
            "partnership": [
                "Red flag, Back to the garage, ",
                "Red flag, We'll wait it out together, ",
                "Red flag, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # RESTART GRID READY
        # ---------------------------------------------------------
        "restart_grid_ready": {
            "sharp": [
                "Grid ready, Mode launch, Be smart, ",
                "Restart ready, No heroics, ",
                "Restart ready, Mode launch, ",
            ],
            "professional": [
                "Grid ready, Mode launch, ",
                "Restart ready, Clean start, ",
                "Restart ready, Mode launch, Be clean, ",
            ],
            "supportive": [
                "Restart ready, You've done this, ",
                "Grid ready, Mode launch, ",
                "Restart ready, You've got this, ",
            ],
            "partnership": [
                "Grid ready, Like we always do, ",
                "Restart ready, Let's go again, ",
                "Grid ready, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # DELTA FREEZE START
        # ---------------------------------------------------------
        "delta_freeze_start": {
            "sharp": [
                "Delta active, Stay positive, ",
                "Delta, Don't go negative, ",
                "Delta freeze, Watch the number, ",
            ],
            "professional": [
                "Delta active, Keep it positive, ",
                "Delta, Stay in the window, ",
                "Delta freeze, Watch your gap, ",
            ],
            "supportive": [
                "Delta active, You've got this, ",
                "Delta freeze, Stay right there, ",
                "Delta, Stay in the window, ",
            ],
            "partnership": [
                "Delta active, Like we always do, ",
                "Delta, We're right here with you, ",
                "Delta, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # DELTA FREEZE END
        # ---------------------------------------------------------
        "delta_freeze_end": {
            "sharp": [
                "Delta ending, Back to racing, ",
                "Delta free, Go, ",
                "Delta ending, Resume racing, ",
            ],
            "professional": [
                "Delta ending, Back to racing, ",
                "Delta free, Resume racing pace, ",
                "Delta ending, Back to it, ",
            ],
            "supportive": [
                "Delta ending, Back to racing, ",
                "Delta free, Like we always do, ",
            ],
            "partnership": [
                "Delta ending, Like we always do, ",
                "Delta free, Back to racing, ",
                "Delta, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT WINDOW OPEN
        # ---------------------------------------------------------
        "pit_window_open": {
            "sharp": [
                "Box this lap, Confirm, ",
                "Pit window open, Box this lap, ",
                "We're pitting this lap, Confirm, ",
            ],
            "professional": [
                "Box this lap, Confirm if you're ready, ",
                "Pit window is open, Box this lap, ",
                "Stop this lap, Confirm, ",
            ],
            "supportive": [
                "Box this lap, Confirm when you're ready, ",
                "Pit window open, Time to box, ",
                "Box this lap, We need to know, ",
            ],
            "partnership": [
                "Box this lap, Confirm, ",
                "Pit window, Let's go, Confirm when you're ready, ",
                "Box this lap, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT WINDOW SECTOR 3
        # ---------------------------------------------------------
        "pit_window_sector3": {
            "sharp": [
                "Box this lap, Still time, Confirm, ",
                "Pit reminder, Box this lap or stay out, ",
                "Sector 3, Box or extend, Confirm, ",
            ],
            "professional": [
                "Reminder, Box this lap, Confirm, ",
                "Pit reminder, Confirm your call, ",
                "Sector 3, Box or extend, ",
            ],
            "supportive": [
                "Reminder, Box this lap, Confirm when you're ready, ",
                "Pit window, We need to know, Confirm or extend, ",
                "Box this lap, Let me know, ",
            ],
            "partnership": [
                "Box this lap, Confirm when you're ready, ",
                "Pit reminder, Let me know, ",
                "Box this lap, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT LIMITER REMINDER
        # ---------------------------------------------------------
        "pit_limiter_reminder": {
            "sharp": [
                "Pit limiter, Mind the speed, ",
                "Pit limiter on, Don't overspeed, ",
                "Speed, Pit limiter, ",
            ],
            "professional": [
                "Pit limiter, Watch the speed limit, ",
                "Pit limiter, Don't overspeed, ",
                "Pit limiter, Speed, ",
            ],
            "supportive": [
                "Pit limiter, Slow down, ",
                "Pit limiter, Watch your entry speed, ",
                "Pit limiter, Slow down, ",
            ],
            "partnership": [
                "Pit limiter, Slow down, ",
                "Pit limiter, Like we always do, ",
                "Pit limiter, Mind the speed, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT STOP QUALITY — Good
        # ---------------------------------------------------------
        "pit_stop_quality_good": {
            "sharp": [
                "Good stop, Blend line, ",
            ],
            "professional": [
                "Good stop, Blend line, Watch the traffic, ",
                "Stop complete, Blend line, ",
            ],
            "supportive": [
                "Good stop, Blend line, You've got this, ",
            ],
            "partnership": [
                "Good stop, Blend line, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT STOP QUALITY — Acceptable
        # ---------------------------------------------------------
        "pit_stop_quality_acceptable": {
            "sharp": [
                "Acceptable stop, Blend line, ",
            ],
            "professional": [
                "Acceptable stop, Watch the blend, ",
            ],
            "supportive": [
                "Acceptable stop, Watch the blend line, ",
            ],
            "partnership": [
                "Acceptable stop, Watch the blend line, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT STOP QUALITY — Slow (same across tiers)
        # ---------------------------------------------------------
        "pit_stop_quality_slow": {
            "sharp": [
                "Slow stop, Blend line, Watch out, ",
            ],
            "professional": [
                "Slow stop, Blend line, Watch out, ",
            ],
            "supportive": [
                "Slow stop, Blend line, Watch out, ",
            ],
            "partnership": [
                "Slow stop, Blend line, Watch out, ",
            ],
        },

        # ---------------------------------------------------------
        # EXTEND STINT
        # ---------------------------------------------------------
        "extend_stint": {
            "sharp": [
                "Understood, Extending, Don't cook the tyres, ",
                "Staying out, One more lap if it's safe, ",
                "Extending, Don't push it, ",
            ],
            "professional": [
                "Extending the stint, Stay smooth, ",
                "Understood, Staying out, Manage the tyres, ",
                "Extending, Watch the degradation, ",
            ],
            "supportive": [
                "Extending, You've got the feel for it, ",
                "Staying out, One more lap if you can, ",
                "Extending, Trust your feel, ",
            ],
            "partnership": [
                "Extending, We've got this, ",
                "Staying out, Like we always do, ",
                "Extending, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # SAFETY OVERRIDE
        # ---------------------------------------------------------
        "safety_override": {
            "sharp": [
                "Box, Now, It's not safe, ",
                "Shawn, Box, Don't argue, ",
                "Box this lap, Safety issue, No debate, ",
            ],
            "professional": [
                "Box this lap, Safety priority, ",
                "We need to box, Now, ",
                "Safety concern, Box immediately, ",
            ],
            "supportive": [
                "Box this lap, We need to stop, ",
                "Box, I know it's not ideal but we have to, ",
                "Box this lap, We have to, ",
            ],
            "partnership": [
                "Box this lap, Trust me on this, ",
                "Box, We've got to stop, ",
                "Box, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # TEAMMATE PITTING
        # ---------------------------------------------------------
        "teammate_pitting": {
            "sharp": [
                "{first} is boxing this lap, ",
                "{first} pitting, Good luck out there, ",
                "{first} in the pit lane, ",
            ],
            "professional": [
                "{first} is boxing this lap, ",
                "{first} pitting, ",
                "{first} in the pit lane, ",
            ],
            "supportive": [
                "{first} is boxing, Good luck out there, ",
                "{first} pitting, ",
                "{first} in the pit lane, ",
            ],
            "partnership": [
                "{first} is boxing, We'll keep an eye out, ",
                "{first} pitting, ",
                "{first} in the pit lane, ",
            ],
        },

        # ---------------------------------------------------------
        # TEAMMATE DNF
        # ---------------------------------------------------------
        "teammate_dnf": {
            "sharp": [
                "{first} is out, You've got the team to yourself now, ",
                "{first} retired, Focus on your race, ",
                "{first} is out of the race, ",
            ],
            "professional": [
                "{first} is out of the race, ",
                "{first} DNF, Keep pushing, ",
                "{first} retired, Keep going, ",
            ],
            "supportive": [
                "{first} is out, Stay focused, ",
                "{first} retired, We've still got a race to run, ",
                "{first} is out, Keep going, ",
            ],
            "partnership": [
                "{first} is out, Let's make it count, ",
                "{first} DNF, We'll miss them out there, ",
                "{first} is out, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # QUALI GOAL
        # ---------------------------------------------------------
        "quali_goal": {
            "sharp": [
                "Qualifying lap, Give me everything, ",
                "This is it, Full push, ",
                "Quali lap, No lifting, ",
            ],
            "professional": [
                "Qualifying lap, Full push, ",
                "This is a qualifying lap, Everything, ",
                "Quali lap, Everything, ",
            ],
            "supportive": [
                "Qualifying lap, Trust yourself, ",
                "This is it, Give me everything you've got, ",
                "Quali lap, You've got this, ",
            ],
            "partnership": [
                "Qualifying lap, Like we always do, ",
                "This is it, Let's find the time together, ",
                "Qualifying lap, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # QUALI LAP COMPLETE VALID
        # ---------------------------------------------------------
        "quali_lap_complete": {
            "sharp": [
                "Lap complete, P{position}, ",
                "Good lap, P{position}, ",
                "Lap done, P{position}, ",
            ],
            "professional": [
                "Lap complete, P{position}, ",
                "Good lap, P{position}, ",
                "Lap done, P{position}, ",
            ],
            "supportive": [
                "Lap complete, That's a good lap, P{position}, ",
                "P{position}, Well driven, ",
                "Lap complete, P{position}, Well done, ",
            ],
            "partnership": [
                "Lap complete, P{position}, That's a great lap, ",
                "P{position}, We found the time, ",
                "Lap complete, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # QUALI LAP INVALID
        # ---------------------------------------------------------
        "quali_lap_invalid": {
            "sharp": [
                "Lap deleted, That won't count, ",
                "Deleted, Run it again, ",
                "Lap deleted, Not good enough, Go again, ",
            ],
            "professional": [
                "Lap deleted, That won't count, ",
                "Invalid lap, Try again, ",
                "Lap deleted, Run it again, ",
            ],
            "supportive": [
                "Lap deleted, Don't let it rattle you, Go again, ",
                "Lap deleted, Shake it off and go again, ",
                "Lap deleted, It happens, Try again, ",
            ],
            "partnership": [
                "Lap deleted, It happens, Go again, ",
                "Lap deleted, We've got time, Try again, ",
                "Lap deleted, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # QUALI PROVISIONAL POLE
        # ---------------------------------------------------------
        "quali_provisional_pole": {
            "sharp": [
                "Provisional pole, Good lap, ",
                "Provisional pole, Let's see if it holds, ",
            ],
            "professional": [
                "Provisional pole, Good effort, ",
                "Provisional pole, ",
                "Pole, Provisional, Good lap, ",
            ],
            "supportive": [
                "Provisional pole, That was a great lap, ",
                "Pole, Provisional, Well done, ",
                "Provisional pole, Let's see, ",
            ],
            "partnership": [
                "Provisional pole, That's what I expected, ",
                "Pole, Provisional, Like we always do, ",
                "Provisional pole, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # QUALI FINAL POLE
        # ---------------------------------------------------------
        "quali_final_pole": {
            "sharp": [
                "Pole position, Incredible, ",
                "Pole, You did it, ",
                "Pole position, Locked in, ",
            ],
            "professional": [
                "Pole position, That's the way to start, ",
                "Pole, Locked in, ",
                "Pole position, Incredible, ",
            ],
            "supportive": [
                "Pole position, That's a great lap to start from pole, ",
                "Pole, Incredible, ",
                "Pole position, Well done, ",
            ],
            "partnership": [
                "Pole position, Like we always knew you could, ",
                "Pole, Like we always do, ",
                "Pole position, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # QUALI POSITION LOST
        # ---------------------------------------------------------
        "quali_position_lost": {
            "sharp": [
                "Dropped to P{position}, Worth going again, ",
                "P{position}, Not good enough, Go again, ",
                "Position lost, P{position}, Try again, ",
            ],
            "professional": [
                "Position lost, P{position}, Try again, ",
                "P{position}, Worth going back out, ",
                "Dropped to P{position}, Try again, ",
            ],
            "supportive": [
                "P{position}, You've got time, Go again, ",
                "Dropped to P{position}, Not a disaster, Go again, ",
                "P{position}, Not the end, Try again, ",
            ],
            "partnership": [
                "P{position}, We can do better, Go again, ",
                "Dropped to P{position}, Let's find it, ",
                "P{position}, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # QUALI GO BACK OUT
        # ---------------------------------------------------------
        "quali_go_back_out": {
            "sharp": [
                "Not good enough, Go back out, ",
                "Back out, That wasn't your best, ",
                "Not good enough, Another shot, ",
            ],
            "professional": [
                "Go back out, That wasn't quite there, ",
                "Back out, Try again, ",
                "Go back out, One more, ",
            ],
            "supportive": [
                "Go back out, You've got time, One more shot, ",
                "Not quite, Go back out, ",
                "Go back out, You've got this, ",
            ],
            "partnership": [
                "Go back out, We'll find it, ",
                "Back out, One more lap, ",
                "Go back out, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # WEATHER CHANGED
        # ---------------------------------------------------------
        "weather_changed": {
            "sharp": [
                "Track conditions changing, Watch the grip, ",
                "Conditions shifting, Let me know what you feel, ",
            ],
            "professional": [
                "Track conditions changing, Monitor grip closely, ",
                "Weather shift, Keep me updated, ",
            ],
            "supportive": [
                "Conditions are changing, Trust your feel, ",
                "Conditions shifting, Stay focused on the grip, ",
            ],
            "partnership": [
                "Conditions shifting, We'll read it together, ",
                "Weather changing, Stay sharp, ",
            ],
        },

        # ---------------------------------------------------------
        # RAIN SOON
        # ---------------------------------------------------------
        "rain_soon": {
            "sharp": [
                "Rain in {n} minutes, Be ready, ",
                "{n} minutes to rain, ",
            ],
            "professional": [
                "Rain expected in about {n} minutes, ",
                "{n} minutes to rain, Stay alert, ",
            ],
            "supportive": [
                "Rain in about {n} minutes, Stay focused, ",
                "{n} minutes to rain, ",
            ],
            "partnership": [
                "Rain in about {n} minutes, We'll call it, ",
                "{n} minutes to rain, Stay sharp, ",
            ],
        },

        # ---------------------------------------------------------
        # TRACK DRYING
        # ---------------------------------------------------------
        "track_drying": {
            "sharp": [
                "Track drying, Inters may be the move soon, ",
                "Track drying, Slicks could be on soon, ",
            ],
            "professional": [
                "Track is drying, Inters may become viable, ",
                "Track drying, Keep an eye on conditions, ",
            ],
            "supportive": [
                "Track drying, The crossover is coming, ",
                "Conditions drying, Watch for the switch, ",
            ],
            "partnership": [
                "Track drying, We'll call the crossover, ",
                "Conditions drying, We'll read it together, ",
            ],
        },

        # ---------------------------------------------------------
        # TRACK WORSENING
        # ---------------------------------------------------------
        "track_worsening": {
            "sharp": [
                "Conditions worsening, Stay focused, ",
                "Getting worse out there, ",
            ],
            "professional": [
                "Conditions getting worse, Stay sharp, ",
                "Track worsening, Stay focused, ",
            ],
            "supportive": [
                "Conditions worsening, Keep pushing but watch it, ",
                "Conditions getting worse, Stay focused, ",
            ],
            "partnership": [
                "Conditions worsening, Stay sharp, ",
                "It's getting worse out there, Stay focused, ",
            ],
        },

        # ---------------------------------------------------------
        # CROSSOVER TO INTERS
        # ---------------------------------------------------------
        "crossover_inters": {
            "sharp": [
                "Track is too wet for slicks, Intermediates are the right tyre now, ",
                "Inters, Now, The track is too wet, ",
            ],
            "professional": [
                "Track too wet for slicks, Intermediates are the call, ",
                "Inters, The track is too wet, ",
            ],
            "supportive": [
                "Track is too wet, Inters are the right tyre now, ",
                "Inters, The track's too wet for slicks, ",
            ],
            "partnership": [
                "Track too wet, Inters, Like we always do, ",
                "Inters, We'll call it, ",
            ],
        },

        # ---------------------------------------------------------
        # CROSSOVER TO SLICKS
        # ---------------------------------------------------------
        "crossover_slicks": {
            "sharp": [
                "Conditions are dry, Inters are costing you time, Come in for slicks, ",
                "Dry track, Slicks, Now, ",
            ],
            "professional": [
                "Track is dry, Slicks are the call, ",
                "Conditions dry, Come in for slicks, ",
            ],
            "supportive": [
                "Track is dry, Slicks are the right tyre now, ",
                "Dry track, Slicks, Let's go, ",
            ],
            "partnership": [
                "Track dry, Slicks, Like we always do, ",
                "Slicks, We'll call it, ",
            ],
        },

        # ---------------------------------------------------------
        # CROSSOVER TO FULL WETS
        # ---------------------------------------------------------
        "crossover_wets": {
            "sharp": [
                "Conditions are extreme, Full wets are the right tyre now, ",
                "Full wets, The track is too wet, ",
            ],
            "professional": [
                "Track extreme, Full wets are the call, ",
                "Full wets, The track is too wet, ",
            ],
            "supportive": [
                "Conditions extreme, Full wets, Stay safe, ",
                "Full wets, The track is too wet, ",
            ],
            "partnership": [
                "Full wets, Like we always do, ",
                "Wets, We'll call it, ",
            ],
        },

        # ---------------------------------------------------------
        # LAST FIVE LAPS
        # ---------------------------------------------------------
        "last_five_laps": {
            "sharp": [
                "Five laps to go. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
                "Five laps. {ahead}: {gap}. {behind}: {behind_gap}, ",
                "Five laps. {gap} to {ahead}. {behind}: {behind_gap} behind, ",
                "Five laps to go, Keep it tidy, ",
            ],
            "professional": [
                "Five laps to go. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
                "Five laps, Gap to {ahead}: {gap}. {behind}: {behind_gap} behind, ",
                "Five laps to go. {gap} to {ahead}. {behind}: {behind_gap} behind, ",
                "Five laps to go, Keep it clean, ",
            ],
            "supportive": [
                "Five laps to go. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, Looking good, ",
                "Five laps, Gap to {ahead}: {gap}. {behind}: {behind_gap} behind, Solid, ",
                "Five laps. {gap} to {ahead}. {behind}: {behind_gap} behind, Good, ",
                "Five laps to go, You've got this, ",
            ],
            "partnership": [
                "Five laps to go. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, Like we always do, ",
                "Five laps, Gap to {ahead}: {gap}. {behind}: {behind_gap} behind, ",
                "Five laps. {gap} to {ahead}. {behind}: {behind_gap} behind, ",
                "Five laps to go, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # LAST LAP
        # ---------------------------------------------------------
        "last_lap": {
            "sharp": [
                "Last lap. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
                "Last lap. {gap} to {ahead}. {behind}: {behind_gap} behind, ",
                "Last lap, Bring it home, ",
                "Last lap, No risks, ",
            ],
            "professional": [
                "Last lap. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, ",
                "Last lap, Gap to {ahead}: {gap}. {behind}: {behind_gap} behind, ",
                "Last lap, Bring it home, ",
                "Last lap, Keep it clean, ",
            ],
            "supportive": [
                "Last lap. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, You've done this, ",
                "Last lap, Gap to {ahead}: {gap}. {behind}: {behind_gap} behind, Stay clean, ",
                "Last lap, Like we always do, ",
                "Last lap, Bring it home, You've done this, ",
            ],
            "partnership": [
                "Last lap. {ahead} ahead, {gap}. {behind} behind, {behind_gap}, Like we always do, ",
                "Last lap, Gap to {ahead}: {gap}. {behind}: {behind_gap} behind, Together, ",
                "Last lap, Like we always do, Bring it home, ",
                "Last lap, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # LAP INVALIDATED
        # ---------------------------------------------------------
        "lap_invalidated": {
            "sharp": [
                "Lap deleted, That won't count, ",
                "Deleted, Run it again, ",
                "Lap deleted, Not good enough, Go again, ",
            ],
            "professional": [
                "Lap deleted, That won't count, ",
                "Invalid lap, Try again, ",
                "Lap deleted, Run it again, ",
            ],
            "supportive": [
                "Lap deleted, Don't let it rattle you, Go again, ",
                "Lap deleted, Shake it off and go again, ",
                "Lap deleted, It happens, Try again, ",
            ],
            "partnership": [
                "Lap deleted, It happens, Go again, ",
                "Lap deleted, We've got time, Try again, ",
                "Lap deleted, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # SESSION START
        # ---------------------------------------------------------
        "session_start": {
            "sharp": [
                "Session starting, Focus, ",
                "Session live, Let's go, ",
                "Session starting, ",
            ],
            "professional": [
                "Session starting, Focus, ",
                "Session live, ",
                "Session starting, ",
            ],
            "supportive": [
                "Session starting, You've got this, ",
                "Session live, Let's find the time, ",
                "Session starting, Let's go, ",
            ],
            "partnership": [
                "Session starting, Like we always do, ",
                "Session live, Let's go, ",
                "Session starting, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # SESSION READY
        # ---------------------------------------------------------
        "session_ready": {
            "sharp": [
                "Session ready, Let's go, ",
                "Ready to race, ",
            ],
            "professional": [
                "Session ready, Let's go, ",
                "Ready to race, ",
            ],
            "supportive": [
                "Session ready, Let's do this, ",
                "Ready to race, You've got this, ",
            ],
            "partnership": [
                "Session ready, Together we got this, ",
                "Ready to race, Let's go, ",
            ],
        },

        # ---------------------------------------------------------
        # SESSION END
        # ---------------------------------------------------------
        "session_end": {
            "sharp": [
                "Session complete, ",
                "Session over, Good work, ",
                "Session complete, Good work, ",
            ],
            "professional": [
                "Session complete, ",
                "Session over, ",
                "Session complete, Good work, ",
            ],
            "supportive": [
                "Session complete, Good effort, ",
                "Session over, Well done, ",
                "Session complete, Well done, ",
            ],
            "partnership": [
                "Session complete, Like we always do, ",
                "Session over, Good work, ",
                "Session complete, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # SESSION TYPE CHANGED
        # ---------------------------------------------------------
        "session_type_changed": {
            "sharp": [
                "Qualifying, Let's go, ",
                "Race start, Focus, ",
                "Practice, Track time, ",
            ],
            "professional": [
                "Qualifying starting, Let's go, ",
                "Race mode, Focus, ",
                "Practice session, ",
            ],
            "supportive": [
                "Qualifying, This is what matters, ",
                "Race, Let's do it, ",
                "Practice, Track time, ",
            ],
            "partnership": [
                "Qualifying, Like we always do, ",
                "Race, Let's go, ",
                "Practice, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # GARAGE ENTERED
        # ---------------------------------------------------------
        "garage_entered": {
            "sharp": [
                "In the garage, ",
                "Back in the garage, Take your time, ",
                "In the garage, No rush, ",
            ],
            "professional": [
                "In the garage, ",
                "Returned to the garage, ",
            ],
            "supportive": [
                "In the garage, Take your time, ",
                "Back in the garage, We'll be ready, ",
            ],
            "partnership": [
                "In the garage, Like we always do, ",
                "Back in the garage, No rush, ",
            ],
        },

        # ---------------------------------------------------------
        # DRIVERS READY (driver map loaded from participants packet)
        # ---------------------------------------------------------
        "drivers_ready": {
            "sharp": [
                "Drivers ready, let's go, ",
            ],
            "professional": [
                "Drivers ready, let's go, ",
            ],
            "supportive": [
                "Drivers ready, You've got this, ",
            ],
            "partnership": [
                "Drivers ready, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # GARAGE EXITED
        # ---------------------------------------------------------
        "garage_exited": {
            "sharp": [
                "Out of the garage, Back on track, ",
                "Out, Let's go, ",
                "Out of the garage, Let's go, ",
            ],
            "professional": [
                "Out of the garage, Back on track, ",
                "Back on track, ",
                "Out of the garage, Let's go, ",
            ],
            "supportive": [
                "Out of the garage, Back on it, ",
                "Back on track, Let's go, ",
                "Out of the garage, Let's go, ",
            ],
            "partnership": [
                "Out of the garage, Like we always do, ",
                "Back on track, Let's go, ",
                "Out of the garage, Like we always do, ",
            ],
        },

        # ---------------------------------------------------------
        # LAP START
        # ---------------------------------------------------------
        "lap_start": {
            "sharp": [
                "Lap {lap}, Push, ",
                "Lap {lap}, Go, ",
                "Lap {lap}, Find the limit, ",
            ],
            "professional": [
                "Lap {lap}, Push, ",
                "Lap {lap}, Let's go, ",
                "Lap {lap}, Find the pace, ",
            ],
            "supportive": [
                "Lap {lap}, Good start, ",
                "Lap {lap}, Let's do this, ",
                "Lap {lap}, You've got this, ",
            ],
            "partnership": [
                "Lap {lap}, Good start, ",
                "Lap {lap}, Let's find the pace together, ",
                "Lap {lap}, We've got this, ",
            ],
        },

        # ---------------------------------------------------------
        # QUALI POSITION UPDATE
        # ---------------------------------------------------------
        "quali_position_update": {
            "sharp": [
                "P{position}, ",
                "P{position}, That's where we are, ",
                "P{position}, Current, ",
            ],
            "professional": [
                "P{position}, ",
                "P{position}, Current, ",
                "P{position}, Holding, ",
            ],
            "supportive": [
                "P{position}, Looking good, ",
                "P{position}, Solid, ",
                "P{position}, Nice, ",
            ],
            "partnership": [
                "P{position}, Looking good, ",
                "P{position}, Solid, ",
                "P{position}, Nice work, ",
            ],
        },

        # ---------------------------------------------------------
        # QUALI LAP COMPLETE VALID
        # ---------------------------------------------------------
        "quali_lap_complete_valid": {
            "sharp": [
                "Lap done, P{position}, ",
                "P{position}, Done, ",
                "Lap complete, P{position}, ",
            ],
            "professional": [
                "Lap done, P{position}, ",
                "P{position}, Lap complete, ",
                "Lap complete, P{position}, ",
            ],
            "supportive": [
                "Lap done, P{position}, Good, ",
                "P{position}, Nice lap, ",
                "Lap complete, P{position}, Solid, ",
            ],
            "partnership": [
                "Lap done, P{position}, Nice work, ",
                "P{position}, Good lap, ",
                "Lap complete, P{position}, Well driven, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT LIMITER ON
        # ---------------------------------------------------------
        "pit_limiter_on": {
            "sharp": [
                "Pit limiter, ",
                "Pit limiter on, ",
            ],
            "professional": [
                "Pit limiter on, ",
                "Pit limiter, ",
            ],
            "supportive": [
                "Pit limiter on, ",
                "Pit limiter, ",
            ],
            "partnership": [
                "Pit limiter on, ",
                "Pit limiter, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT LIMITER OFF
        # ---------------------------------------------------------
        "pit_limiter_off": {
            "sharp": [
                "Pit limiter off, ",
                "Pit limiter disengaged, ",
            ],
            "professional": [
                "Pit limiter off, ",
                "Pit limiter disengaged, ",
            ],
            "supportive": [
                "Pit limiter off, ",
                "Pit limiter disengaged, ",
            ],
            "partnership": [
                "Pit limiter off, ",
                "Pit limiter disengaged, ",
            ],
        },

        # ---------------------------------------------------------
        # TRACK GREEN FLAG
        # ---------------------------------------------------------
        "track_green": {
            "sharp": [
                "Track is green, ",
                "Green flag, ",
                "Green, Push, ",
            ],
            "professional": [
                "Green flag, Push, ",
                "Track is green, ",
                "Green, Let's go, ",
            ],
            "supportive": [
                "Green flag, Push, ",
                "Green, Go for it, ",
                "Track is green, Let's go, ",
            ],
            "partnership": [
                "Green flag, Let's go, ",
                "Green, Push, ",
                "Track is green, We've got this, ",
            ],
        },

        # ---------------------------------------------------------
        # TRACK YELLOW FLAG
        # ---------------------------------------------------------
        "track_yellow": {
            "sharp": [
                "Yellow flag, Slow down, ",
                "Yellow, Caution, ",
                "Yellow flag, Be careful, ",
            ],
            "professional": [
                "Yellow flag, Slow down, ",
                "Yellow, Caution, ",
                "Yellow flag, Caution, ",
            ],
            "supportive": [
                "Yellow flag, Caution, ",
                "Yellow, Slow down, ",
                "Yellow flag, Be careful, ",
            ],
            "partnership": [
                "Yellow flag, Caution, ",
                "Yellow, Slow down, ",
                "Yellow flag, Be careful, ",
            ],
        },

        # ---------------------------------------------------------
        # TRACK DOUBLE YELLOW
        # ---------------------------------------------------------
        "track_double_yellow": {
            "sharp": [
                "Double yellow, Slow down significantly, ",
                "Double yellow, Very slow, ",
                "Double yellow, Be very careful, ",
            ],
            "professional": [
                "Double yellow, Slow down significantly, ",
                "Double yellow, Very slow, ",
                "Double yellow, Full caution, ",
            ],
            "supportive": [
                "Double yellow, Be careful, ",
                "Double yellow, Slow right down, ",
                "Double yellow, Full caution, ",
            ],
            "partnership": [
                "Double yellow, Slow down, ",
                "Double yellow, Be careful, ",
                "Double yellow, Full caution, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT ENTRY
        # ---------------------------------------------------------
        "pit_entry": {
            "sharp": [
                "Pitting, ",
                "Boxing, ",
                "Pitting this lap, ",
            ],
            "professional": [
                "Pitting, ",
                "Boxing this lap, ",
                "Pitting this lap, ",
            ],
            "supportive": [
                "Pitting, ",
                "Boxing this lap, ",
                "Pitting this lap, ",
            ],
            "partnership": [
                "Pitting, ",
                "Boxing this lap, ",
                "Pitting this lap, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT EXIT
        # ---------------------------------------------------------
        "pit_exit": {
            "sharp": [
                "Out of the box, ",
                "Out, ",
                "Back on track, ",
            ],
            "professional": [
                "Out of the box, ",
                "Back on track, ",
                "Out, ",
            ],
            "supportive": [
                "Out of the box, ",
                "Back on track, ",
                "Out, Let's go, ",
            ],
            "partnership": [
                "Out of the box, ",
                "Back on track, ",
                "Out, Let's go, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT ENTRY LINE
        # ---------------------------------------------------------
        "pit_entry_line": {
            "sharp": [
                "Pit entry, ",
                "Approaching pit entry, ",
            ],
            "professional": [
                "Pit entry, ",
                "Approaching pit entry, ",
            ],
            "supportive": [
                "Pit entry, ",
                "Approaching pit entry, ",
            ],
            "partnership": [
                "Pit entry, ",
                "Approaching pit entry, ",
            ],
        },

        # ---------------------------------------------------------
        # PIT EXIT LINE
        # ---------------------------------------------------------
        "pit_exit_line": {
            "sharp": [
                "Pit exit, ",
                "Pit exit coming up, ",
            ],
            "professional": [
                "Pit exit, ",
                "Pit exit coming up, ",
            ],
            "supportive": [
                "Pit exit, ",
                "Pit exit coming up, ",
            ],
            "partnership": [
                "Pit exit, ",
                "Pit exit coming up, ",
            ],
        },

        # ---------------------------------------------------------
        # FORECAST WEATHER CHANGE
        # ---------------------------------------------------------
        "forecast_weather_change": {
            "sharp": [
                "Weather shift incoming, ",
                "Conditions changing, ",
                "Weather change coming, ",
            ],
            "professional": [
                "Weather shift incoming, ",
                "Conditions changing, Stay aware, ",
                "Weather change coming, ",
            ],
            "supportive": [
                "Weather shift incoming, Stay aware, ",
                "Conditions changing, ",
                "Weather change coming, ",
            ],
            "partnership": [
                "Weather shift incoming, Stay aware, ",
                "Conditions changing, ",
                "Weather change coming, ",
            ],
        },
    }

    # =========================================================
    # PUBLIC API
    # =========================================================

    @staticmethod
    def objective_start(career: CareerTracker, description: str, obj_type: str) -> str:
        tier = career.warmth_tier
        obj_type_upper = obj_type.upper() if isinstance(obj_type, str) else str(obj_type)

        type_lines = RadioLines._objective_start.get(obj_type_upper)
        if type_lines:
            lines = type_lines.get(tier, type_lines.get("professional", type_lines.get("sharp", [])))
        else:
            lines = RadioLines._objective_start_generic.get(tier, RadioLines._objective_start_generic["sharp"])

        line = random.choice(lines)
        return RadioLines._format(line, career, description=description)

    @staticmethod
    def objective_pass(career: CareerTracker) -> str:
        tier = career.warmth_tier
        lines = RadioLines._objective_pass.get(tier, RadioLines._objective_pass["sharp"])
        line = random.choice(lines)
        return RadioLines._format(line, career)

    @staticmethod
    def objective_fail(career: CareerTracker) -> str:
        tier = career.warmth_tier
        lines = RadioLines._objective_fail.get(tier, RadioLines._objective_fail["sharp"])
        line = random.choice(lines)
        return RadioLines._format(line, career)

    @staticmethod
    def objective_cancel(career: CareerTracker) -> str:
        tier = career.warmth_tier
        lines = RadioLines._objective_cancel.get(tier, RadioLines._objective_cancel["sharp"])
        line = random.choice(lines)
        return RadioLines._format(line, career)

    @staticmethod
    def f2_championship(career: CareerTracker) -> str:
        line = random.choice(RadioLines._f2_championship)
        return RadioLines._format(line, career)

    @staticmethod
    def first_f1_title(career: CareerTracker) -> str:
        line = random.choice(RadioLines._first_f1_title)
        return RadioLines._format(line, career)

    @staticmethod
    def consecutive_title(career: CareerTracker) -> str:
        n = career.consecutive_titles
        if n == 2:
            line = random.choice(RadioLines._consecutive_2)
        elif n == 3:
            line = random.choice(RadioLines._consecutive_3)
        elif n <= 7:
            line = random.choice(RadioLines._consecutive_4_to_7)
        else:
            line = random.choice(RadioLines._consecutive_8_plus)

        return RadioLines._format(line, career, n=n)

    @staticmethod
    def year_5(career: CareerTracker) -> str:
        line = random.choice(RadioLines._year_5)
        return RadioLines._format(line, career)

    @staticmethod
    def year_10(career: CareerTracker) -> str:
        line = random.choice(RadioLines._year_10)
        return RadioLines._format(line, career)

    # =========================================================
    # F1 MODE: R&D RESPONSES (48 lines: 12 combos × 4 warmth tiers)
    # =========================================================
    # Format: {teammate_category}_{chosen_category}_{tier}
    # Teammate on Aero → pick Powertrain/Chassis/Durability
    # Teammate on Powertrain → pick Aero/Chassis/Durability
    # Teammate on Chassis → pick Aero/Powertrain/Durability
    # Teammate on Durability → pick Aero/Powertrain/Chassis

    _f1_rnd = {
        # Teammate on Aero → choose Powertrain/Chassis/Durability
        "Aero_Powertrain": {
            "sharp": [
                "Aero's taken, Let's dig into Powertrain then, ",
                "Aero's their deal, Powertrain it is, ",
                "Not Aero, Powertrain, ",
            ],
            "professional": [
                "Aero's taken, Powertrain it is, ",
                "Powertrain, Let's see what we can find, ",
                "Aero's not ours, Powertrain, ",
            ],
            "supportive": [
                "Aero's Oscar's to deal with, Let's work on Powertrain, ",
                "Powertrain looks good for us, Let's see what's there, ",
                "Not chasing Aero, Powertrain it is, ",
            ],
            "partnership": [
                "Aero's their focus, We'll take Powertrain, Let's dig in together, ",
                "Powertrain — that's our path, Let's see what we can build, ",
                "Aero's not our lane, Powertrain, We'll find something there, ",
            ],
        },
        "Aero_Chassis": {
            "sharp": [
                "Aero's taken, Chassis, ",
                "Not Aero, Chassis it is, ",
                "Aero's their job, Chassis for us, ",
            ],
            "professional": [
                "Aero's taken, Chassis is ours, ",
                "Chassis, Let's see what we can do, ",
                "Aero's not ours, Chassis, ",
            ],
            "supportive": [
                "Aero's Oscar's to worry about, Let's take Chassis, ",
                "Chassis looks promising, Let's work it, ",
                "Not chasing Aero, Chassis is our move, ",
            ],
            "partnership": [
                "Aero's their focus, We'll take Chassis, Let's build something there, ",
                "Chassis — that's our angle, Let's see what we find, ",
                "Aero's not our lane, Chassis, We'll make it work, ",
            ],
        },
        "Aero_Durability": {
            "sharp": [
                "Aero's taken, Durability, ",
                "Not Aero, Durability, ",
                "Aero's their deal, Durability for us, ",
            ],
            "professional": [
                "Aero's taken, Durability it is, ",
                "Durability, Let's see what's there, ",
                "Aero's not ours, Durability, ",
            ],
            "supportive": [
                "Aero's Oscar's to worry about, Let's work on Durability, ",
                "Durability looks worth a look, ",
                "Not chasing Aero, Durability it is, ",
            ],
            "partnership": [
                "Aero's their focus, We'll take Durability, Let's dig in, ",
                "Durability — good call, Let's see what we can find, ",
                "Aero's not our lane, Durability, We'll make it work, ",
            ],
        },
        # Teammate on Powertrain → choose Aero/Chassis/Durability
        "Powertrain_Aero": {
            "sharp": [
                "Powertrain's taken, Aero, ",
                "Not Powertrain, Aero, ",
                "Powertrain's their job, Aero for us, ",
            ],
            "professional": [
                "Powertrain's taken, Aero it is, ",
                "Aero, Let's see what we can do, ",
                "Powertrain's not ours, Aero, ",
            ],
            "supportive": [
                "Powertrain's Oscar's to deal with, Let's take Aero, ",
                "Aero looks worth exploring, ",
                "Not chasing Powertrain, Aero is our move, ",
            ],
            "partnership": [
                "Powertrain's their focus, We'll take Aero, Let's see what we find, ",
                "Aero — good angle, Let's build something, ",
                "Powertrain's not our lane, Aero, We'll make it work, ",
            ],
        },
        "Powertrain_Chassis": {
            "sharp": [
                "Powertrain's taken, Chassis, ",
                "Not Powertrain, Chassis it is, ",
                "Powertrain's their deal, Chassis for us, ",
            ],
            "professional": [
                "Powertrain's taken, Chassis is ours, ",
                "Chassis, Let's work it, ",
                "Powertrain's not ours, Chassis, ",
            ],
            "supportive": [
                "Powertrain's Oscar's to worry about, Let's take Chassis, ",
                "Chassis looks promising, Let's dig in, ",
                "Not chasing Powertrain, Chassis is our move, ",
            ],
            "partnership": [
                "Powertrain's their focus, We'll take Chassis, Let's build there, ",
                "Chassis — good call, Let's see what we can find, ",
                "Powertrain's not our lane, Chassis, We'll make it work, ",
            ],
        },
        "Powertrain_Durability": {
            "sharp": [
                "Powertrain's taken, Durability, ",
                "Not Powertrain, Durability, ",
                "Powertrain's their job, Durability for us, ",
            ],
            "professional": [
                "Powertrain's taken, Durability it is, ",
                "Durability, Let's see what's there, ",
                "Powertrain's not ours, Durability, ",
            ],
            "supportive": [
                "Powertrain's Oscar's to worry about, Let's work on Durability, ",
                "Durability looks worth a look, ",
                "Not chasing Powertrain, Durability it is, ",
            ],
            "partnership": [
                "Powertrain's their focus, We'll take Durability, Let's dig in, ",
                "Durability — good angle, Let's see what we find, ",
                "Powertrain's not our lane, Durability, We'll make it work, ",
            ],
        },
        # Teammate on Chassis → choose Aero/Powertrain/Durability
        "Chassis_Aero": {
            "sharp": [
                "Chassis' taken, Aero, ",
                "Not Chassis, Aero, ",
                "Chassis' their deal, Aero for us, ",
            ],
            "professional": [
                "Chassis' taken, Aero it is, ",
                "Aero, Let's see what we can do, ",
                "Chassis' not ours, Aero, ",
            ],
            "supportive": [
                "Chassis' Oscar's to deal with, Let's take Aero, ",
                "Aero looks worth exploring, ",
                "Not chasing Chassis, Aero is our move, ",
            ],
            "partnership": [
                "Chassis' their focus, We'll take Aero, Let's see what we find, ",
                "Aero — good angle, Let's build something, ",
                "Chassis' not our lane, Aero, We'll make it work, ",
            ],
        },
        "Chassis_Powertrain": {
            "sharp": [
                "Chassis' taken, Powertrain, ",
                "Not Chassis, Powertrain it is, ",
                "Chassis' their deal, Powertrain for us, ",
            ],
            "professional": [
                "Chassis' taken, Powertrain is ours, ",
                "Powertrain, Let's work it, ",
                "Chassis' not ours, Powertrain, ",
            ],
            "supportive": [
                "Chassis' Oscar's to worry about, Let's take Powertrain, ",
                "Powertrain looks promising, Let's dig in, ",
                "Not chasing Chassis, Powertrain is our move, ",
            ],
            "partnership": [
                "Chassis' their focus, We'll take Powertrain, Let's build there, ",
                "Powertrain — good call, Let's see what we can find, ",
                "Chassis' not our lane, Powertrain, We'll make it work, ",
            ],
        },
        "Chassis_Durability": {
            "sharp": [
                "Chassis' taken, Durability, ",
                "Not Chassis, Durability, ",
                "Chassis' their deal, Durability for us, ",
            ],
            "professional": [
                "Chassis' taken, Durability it is, ",
                "Durability, Let's see what's there, ",
                "Chassis' not ours, Durability, ",
            ],
            "supportive": [
                "Chassis' Oscar's to worry about, Let's work on Durability, ",
                "Durability looks worth a look, ",
                "Not chasing Chassis, Durability it is, ",
            ],
            "partnership": [
                "Chassis' their focus, We'll take Durability, Let's dig in, ",
                "Durability — good angle, Let's see what we find, ",
                "Chassis' not our lane, Durability, We'll make it work, ",
            ],
        },
        # Teammate on Durability → choose Aero/Powertrain/Chassis
        "Durability_Aero": {
            "sharp": [
                "Durability's taken, Aero, ",
                "Not Durability, Aero, ",
                "Durability's their job, Aero for us, ",
            ],
            "professional": [
                "Durability's taken, Aero it is, ",
                "Aero, Let's see what we can do, ",
                "Durability's not ours, Aero, ",
            ],
            "supportive": [
                "Durability's Oscar's to deal with, Let's take Aero, ",
                "Aero looks worth exploring, ",
                "Not chasing Durability, Aero is our move, ",
            ],
            "partnership": [
                "Durability's their focus, We'll take Aero, Let's see what we find, ",
                "Aero — good angle, Let's build something, ",
                "Durability's not our lane, Aero, We'll make it work, ",
            ],
        },
        "Durability_Powertrain": {
            "sharp": [
                "Durability's taken, Powertrain, ",
                "Not Durability, Powertrain it is, ",
                "Durability's their job, Powertrain for us, ",
            ],
            "professional": [
                "Durability's taken, Powertrain is ours, ",
                "Powertrain, Let's work it, ",
                "Durability's not ours, Powertrain, ",
            ],
            "supportive": [
                "Durability's Oscar's to worry about, Let's take Powertrain, ",
                "Powertrain looks promising, Let's dig in, ",
                "Not chasing Durability, Powertrain is our move, ",
            ],
            "partnership": [
                "Durability's their focus, We'll take Powertrain, Let's build there, ",
                "Powertrain — good call, Let's see what we can find, ",
                "Durability's not our lane, Powertrain, We'll make it work, ",
            ],
        },
        "Durability_Chassis": {
            "sharp": [
                "Durability's taken, Chassis, ",
                "Not Durability, Chassis it is, ",
                "Durability's their job, Chassis for us, ",
            ],
            "professional": [
                "Durability's taken, Chassis is ours, ",
                "Chassis, Let's work it, ",
                "Durability's not ours, Chassis, ",
            ],
            "supportive": [
                "Durability's Oscar's to worry about, Let's take Chassis, ",
                "Chassis looks promising, Let's dig in, ",
                "Not chasing Durability, Chassis is our move, ",
            ],
            "partnership": [
                "Durability's their focus, We'll take Chassis, Let's build there, ",
                "Chassis — good call, Let's see what we can find, ",
                "Durability's not our lane, Chassis, We'll make it work, ",
            ],
        },
    }

    # =========================================================
    # ERS AUTOMATION LINES (48 lines: 3 types × 4 warmth tiers × 4 variations)
    # All use comma style (no periods) to avoid TTS "dot"
    # Some include {name} placeholder for warmth-based injection
    # =========================================================

    _ers_lines = {
        # ERS OFF - when cornering or battery critical
        "ers_off": {
            "sharp": [
                "ERS off{name}, ",
                "ERS off, ",
            ],
            "professional": [
                "ERS off{name}, ",
                "ERS off, ",
            ],
            "supportive": [
                "ERS off{name}, ",
                "ERS off, ",
            ],
            "partnership": [
                "ERS off{name}, ",
                "ERS off, ",
            ],
        },
        # ERS DEPLOY - on straight when attacking
        "ers_deploy": {
            "sharp": [
                "Deploy ERS{name}, ",
                "ERS on{name}, ",
                "ERS deploy, ",
            ],
            "professional": [
                "ERS deploy{name}, ",
                "ERS on{name}, ",
                "ERS deploy, ",
            ],
            "supportive": [
                "ERS deploy{name}, ",
                "ERS on{name}, ",
                "ERS deploy, ",
            ],
            "partnership": [
                "ERS deploy{name}, ",
                "ERS on{name}, ",
                "ERS deploy, ",
            ],
        },
        # ERS RECHARGE - high battery, switch to harvest mode
        "ers_recharge": {
            "sharp": [
                "ERS harvest{name}, ",
                "ERS to harvest{name}, ",
                "ERS recharge{name}, ",
            ],
            "professional": [
                "ERS harvest{name}, ",
                "ERS to harvest{name}, ",
                "ERS recharge{name}, ",
            ],
            "supportive": [
                "ERS harvest{name}, ",
                "ERS to harvest{name}, ",
                "ERS recharge{name}, ",
            ],
            "partnership": [
                "ERS harvest{name}, ",
                "ERS to harvest{name}, ",
                "ERS recharge{name}, ",
            ],
        },
        # ERS HOTLAP - quali push lap
        "ers_hotlap": {
            "sharp": [
                "ERS hotlap{name}, Give it everything, ",
                "ERS on{name}, Full push, ",
            ],
            "professional": [
                "ERS hotlap{name}, Give it everything, ",
                "ERS on{name}, Full push, ",
            ],
            "supportive": [
                "ERS hotlap{name}, Give it everything, ",
                "ERS on{name}, Full push, ",
            ],
            "partnership": [
                "ERS hotlap{name}, Give it everything, ",
                "ERS on{name}, Full push, ",
            ],
        },
        # ERS BATTERY LOW - critical warning
        "ers_battery_low": {
            "sharp": [
                "Battery low{name}, Save ERS, ",
                "ERS depleted{name}, Save what's left, ",
            ],
            "professional": [
                "Battery low{name}, Save ERS, ",
                "ERS depleted{name}, Save what's left, ",
            ],
            "supportive": [
                "Battery low{name}, Save ERS, ",
                "ERS depleted{name}, Save what's left, ",
            ],
            "partnership": [
                "Battery low{name}, Save ERS, ",
                "ERS depleted{name}, Save what's left, ",
            ],
        },
        # ERS LAST LAP - dump everything
        "ers_last_lap": {
            "sharp": [
                "Last lap{name}, Empty the battery, ",
                "Last lap{name}, Full deployment, ",
            ],
            "professional": [
                "Last lap{name}, Empty the battery, ",
                "Last lap{name}, Full deployment, ",
            ],
            "supportive": [
                "Last lap{name}, Empty the battery, ",
                "Last lap{name}, Full deployment, ",
            ],
            "partnership": [
                "Last lap{name}, Empty the battery, ",
                "Last lap{name}, Full deployment, ",
            ],
        },
        # ERS PUSH - close the gap
        "ers_push": {
            "sharp": [
                "Deploy ERS{name}, Push, ",
                "ERS on{name}, Push now, ",
            ],
            "professional": [
                "Deploy ERS{name}, Push, ",
                "ERS on{name}, Push now, ",
            ],
            "supportive": [
                "Deploy ERS{name}, Push, ",
                "ERS on{name}, Push now, ",
            ],
            "partnership": [
                "Deploy ERS{name}, Push, ",
                "ERS on{name}, Push now, ",
            ],
        },
        # ERS DEFEND - defending position
        "ers_defend": {
            "sharp": [
                "Defend{name}, Deploy ERS, ",
                "ERS on{name}, Defend the position, ",
            ],
            "professional": [
                "Deploy ERS{name}, Defend, ",
                "ERS on{name}, Defend the position, ",
            ],
            "supportive": [
                "Deploy ERS{name}, Defend, ",
                "ERS on{name}, Defend the position, ",
            ],
            "partnership": [
                "Deploy ERS{name}, Defend, ",
                "ERS on{name}, Defend the position, ",
            ],
        },
    }

    # =========================================================
    # F1 MODE: R&D MAXED/UPGRADE RESPONSES (40 lines: 4 scenarios × 4 warmth tiers × ~3 lines)
    # =========================================================

    _f1_rnd_meta = {
        # Category marked as maxed
        "category_maxed": {
            "sharp": [
                "Got it, {category} marked as done, ",
                "{category} noted as maxed, ",
                "{category} is done, What else is there?",
            ],
            "professional": [
                "Got it, {category} marked as done, ",
                "{category} noted, Let's work with the others, ",
                "{category} is complete, What's next?",
            ],
            "supportive": [
                "Got it, {category} marked as done, ",
                "Alright, {category} is done, Let's see what else we've got, ",
                "{category} noted, What else is available?",
            ],
            "partnership": [
                "Got it, {category} marked as done, Let's keep track of that together, ",
                "{category} is done, What else should we look at?",
            ],
        },
        # Category has new upgrades available
        "category_available": {
            "sharp": [
                "{category} is back on the table, ",
                "{category} has new upgrades, Let's see what's there, ",
                "{category} is open again, ",
            ],
            "professional": [
                "{category} is back on the table, ",
                "{category} has new upgrades, Good to know, ",
                "{category} is open, Let's see what we can find, ",
            ],
            "supportive": [
                "{category} is back on the table, ",
                "Nice, {category} has new upgrades, Let's explore, ",
                "{category} is open again, This could be worth it, ",
            ],
            "partnership": [
                "{category} is back on the table, Good catch, ",
                "{category} has new upgrades, Let's work on that together, ",
                "{category} is open again, Let's see what we can build, ",
            ],
        },
        # Player picked a category that was marked as maxed
        "picking_maxed": {
            "sharp": [
                "I thought {category} was maxed, Any new upgrades?",
                "{category}? That was marked as done, Did it unlock?",
                "{category} was marked as complete, New tiers?",
            ],
            "professional": [
                "I thought {category} was marked as done, Any new upgrades?",
                "{category} was noted as complete, New upgrades?",
                "{category} was maxed, Did something change?",
            ],
            "supportive": [
                "I thought {category} was marked as done, Any new upgrades?",
                "{category}? That's been complete, New tiers available?",
                "Wasn't {category} done? New upgrades?",
            ],
            "partnership": [
                "I thought {category} was marked as done, Any new upgrades?",
                "{category}? That one was complete, Did something unlock?",
                "{category} was marked as done, New tiers available?",
            ],
        },
        # Reset all categories
        "reset_all": {
            "sharp": [
                "All categories cleared, Starting fresh, ",
                "Done, Everything's back on the table, ",
                "Reset complete, All R&D is available, ",
            ],
            "professional": [
                "All categories cleared, Starting fresh, ",
                "Done, Everything's back on the table, ",
                "Reset complete, All R&D options available, ",
            ],
            "supportive": [
                "All categories cleared, Starting fresh, ",
                "Done, Everything's available again, ",
                "Reset complete, Let's see what we can work with, ",
            ],
            "partnership": [
                "All categories cleared, Starting fresh together, ",
                "Done, Everything's back on the table, Let's see what we need, ",
                "Reset complete, All R&D is available, Let's build something, ",
            ],
        },
    }

    # Garage entry greetings
    _f1_garage = {
        # No teammate name stored - ask who they're working with
        "ask_teammate": {
            "sharp": [
                "Hey, Who are we working with this season?",
                "Hey, Who's our teammate this year?",
            ],
            "professional": [
                "Hey, Who are we working with this season?",
                "Hey, Who's our teammate this year?",
            ],
            "supportive": [
                "Hey, Who are we working with this season?",
                "Hey, Who's our teammate this year?",
            ],
            "partnership": [
                "Hey, Who are we working with this season?",
                "Hey, Who's our teammate this year?",
            ],
        },
        # Teammate name known - ask what they're working on
        "ask_rnd": {
            "sharp": [
                "Hey, What is {teammate} working on?",
                "Hey, What's {teammate} on?",
            ],
            "professional": [
                "Hey, What is {teammate} working on?",
                "Hey, What's {teammate} on?",
            ],
            "supportive": [
                "Hey, What is {teammate} working on?",
                "Hey, What's {teammate} on?",
            ],
            "partnership": [
                "Hey, What is {teammate} working on?",
                "Hey, What's {teammate} on?",
            ],
        },
        # Player corrected teammate name - acknowledge
        "teammate_updated": {
            "sharp": [
                "Got it, What is {teammate} working on?",
                "Understood, What's {teammate} on?",
            ],
            "professional": [
                "Got it, What is {teammate} working on?",
                "Understood, What's {teammate} on?",
            ],
            "supportive": [
                "Got it, What is {teammate} working on?",
                "Understood, What's {teammate} on?",
            ],
            "partnership": [
                "Got it, What is {teammate} working on?",
                "Understood, What's {teammate} on? Let's work together, ",
            ],
        },
        # No upgrades available
        "no_upgrades": {
            "sharp": [
                "Alright, Let's work with what we've got, ",
                "Got it, ",
            ],
            "professional": [
                "Alright, Let's work with what we've got, ",
                "Got it, ",
            ],
            "supportive": [
                "Alright, Let's work with what we've got, ",
                "Got it, ",
            ],
            "partnership": [
                "Alright, Let's work with what we've got, ",
                "Got it, Let's see what we can do, ",
            ],
        },
    }

    # =========================================================
    # F1 MODE: PRACTICE PROGRAM ACKNOWLEDGMENTS (24 lines)
    # =========================================================

    _f1_practice = {
        "Track Acclimatisation": {
            "sharp": ["Track acclimatisation, Let's get the laps in, "],
            "professional": ["Track acclimatisation, Let's get the laps in, "],
            "supportive": ["Track acclimatisation, Let's get the laps in and find the limits, "],
            "partnership": ["Track acclimatisation, Let's get the laps in together and find the limits, "],
        },
        "Tyre Management": {
            "sharp": ["Tyre management, Let's find the window, "],
            "professional": ["Tyre management, Let's find the window, "],
            "supportive": ["Tyre management, Let's work the tyres and find the window, "],
            "partnership": ["Tyre management, Let's find the window together, "],
        },
        "Fuel Management": {
            "sharp": ["Fuel management, Let's find the balance, "],
            "professional": ["Fuel management, Let's find the balance, "],
            "supportive": ["Fuel management, Let's find the balance, "],
            "partnership": ["Fuel management, Let's find the balance together, "],
        },
        "ERS Management": {
            "sharp": ["ERS off, "],
            "professional": ["ERS off, "],
            "supportive": ["ERS management, Let's see how you get on without the extra push, "],
            "partnership": ["ERS management, Let's work on that feel together, "],
        },
        "Qualifying Simulation": {
            "sharp": ["Quali sim, Full push from the out-lap, "],
            "professional": ["Qualifying simulation, Full push from the out-lap, "],
            "supportive": ["Qualifying simulation, Let's find that lap together, "],
            "partnership": ["Qualifying simulation, Let's find that lap together, "],
        },
        "Race Strategy": {
            "sharp": ["Race strategy, Let's find the pace, "],
            "professional": ["Race strategy, Let's find the pace, "],
            "supportive": ["Race strategy, Let's find the pace and build the long run, "],
            "partnership": ["Race strategy, Let's build this together, "],
        },
    }

    _f1_practice_invalid = {
        "sharp": ["Which program?"],
        "professional": ["Which program?"],
        "supportive": ["Which program?"],
        "partnership": ["Which program?"],
    }

    # =========================================================
    # F1 MODE: PUBLIC API
    # =========================================================

    @staticmethod
    def get_f1_rnd(teammate_category: str, chosen_category: str, tier: str) -> str:
        pool = RadioLines._f1_rnd.get(f"{teammate_category}_{chosen_category}", {})
        lines = pool.get(tier, pool.get("professional", []))
        return random.choice(lines) if lines else f"Let's work on {chosen_category}, "

    @staticmethod
    def get_f1_practice(program: str, tier: str) -> str:
        pool = RadioLines._f1_practice.get(program, {})
        lines = pool.get(tier, pool.get("professional", []))
        return random.choice(lines) if lines else "Alright, Let's get after it, "

    @staticmethod
    def get_f1_practice_invalid(tier: str) -> str:
        lines = RadioLines._f1_practice_invalid.get(tier, ["Which program?"])
        return random.choice(lines)

    @staticmethod
    def get_f1_rnd_meta(response_type: str, tier: str, **kwargs) -> str:
        """Get R&D meta responses (maxed, available, picking maxed, reset)."""
        pool = RadioLines._f1_rnd_meta.get(response_type, {})
        lines = pool.get(tier, pool.get("professional", []))
        if not lines:
            return ""
        line = random.choice(lines)
        return line.format(**kwargs)

    @staticmethod
    def get_f1_garage(greeting_type: str, tier: str, **kwargs) -> str:
        """Get garage entry greetings."""
        pool = RadioLines._f1_garage.get(greeting_type, {})
        lines = pool.get(tier, pool.get("professional", []))
        if not lines:
            return ""
        line = random.choice(lines)
        return line.format(**kwargs)

    @staticmethod
    def get_ers_line(line_type: str, tier: str, name: str = "") -> str:
        """Get ERS automation line (comma style, no periods)."""
        pool = RadioLines._ers_lines.get(line_type, {})
        lines = pool.get(tier, pool.get("professional", []))
        if not lines:
            return ""
        line = random.choice(lines)
        return line.format(name=name)

    # =========================================================
    # RACE EVENT LINE LOOKUP
    # =========================================================

    @staticmethod
    def get(event: str, career: CareerTracker, **kwargs) -> str:
        """
        Get a radio line for a race event, selected by warmth tier.
        kwargs are injected into the line template, """
        tier = career.warmth_tier

        # Race gap has position-dependent sub-tiers
        if event == "race_gap":
            position = kwargs.get("position", 99)
            sub_tier = f"{tier}_p1_p5" if position <= 5 else f"{tier}_p6_plus"
            lines = RadioLines._race_events.get(event, {}).get(sub_tier, [])
        else:
            lines = RadioLines._race_events.get(event, {}).get(tier, [])

        if not lines:
            return ""

        line = random.choice(lines)
        return RadioLines._format(line, career, **kwargs)

    @staticmethod
    def get_all_static() -> list[str]:
        """
        Return all unique static radio lines for pre-synthesis, Strips {name} and {driver} placeholders (name injection happens at audio level), Excludes lines with other dynamic kwargs (description, position, etc.), """
        lines = set()
        safe_placeholders = {"{name}", "{driver}"}

        for pool_name, pool_data in RadioLines._race_events.items():
            for tier_lines in pool_data.values():
                for line in tier_lines:
                    found = set(re.findall(r'\{[^}]+\}', line))
                    dynamic = found - safe_placeholders
                    if dynamic:
                        continue  # skip lines with dynamic placeholders

                    # Strip safe placeholders
                    result = line
                    for ph in found:
                        result = result.replace(ph, "")
                    result = result.strip()
                    if result:
                        lines.add(result)

        return sorted(lines)

    @staticmethod
    def get_all_f1_mode() -> list[str]:
        """Return all F1Mode static lines for pre-synthesis, """
        lines = set()

        # _f1_rnd and _f1_practice: {category: {tier: [lines]}}
        for pool in [RadioLines._f1_rnd, RadioLines._f1_practice]:
            for tier_dict in pool.values():
                for line_list in tier_dict.values():
                    for line in line_list:
                        if line:
                            lines.add(line)

        # _f1_practice_invalid: {tier: [lines]}
        for tier_lines in RadioLines._f1_practice_invalid.values():
            for line in tier_lines:
                if line:
                    lines.add(line)

        # _f1_rnd_meta: {type: {tier: [lines]}}
        for meta_pool in RadioLines._f1_rnd_meta.values():
            for tier_lines in meta_pool.values():
                for line in tier_lines:
                    if line:
                        lines.add(line)

        # _f1_garage: {type: {tier: [lines]}}
        for garage_pool in RadioLines._f1_garage.values():
            for tier_lines in garage_pool.values():
                for line in tier_lines:
                    if line:
                        lines.add(line)

        # _ers_lines: {type: {tier: [lines]}}
        for ers_pool in RadioLines._ers_lines.values():
            for tier_lines in ers_pool.values():
                for line in tier_lines:
                    if line:
                        lines.add(line)

        # Generate all gap call variations
        lines.update(RadioLines._generate_gap_calls())
        lines.update(RadioLines._generate_teammate_pit_calls())
        lines.update(RadioLines._generate_last_five_calls())
        lines.update(RadioLines._generate_last_lap_calls())

        return sorted(lines)

    # =========================================================
    # GAP CALL GENERATION (for pre-caching)
    # =========================================================

    # F1 25 driver last names
    F1_DRIVERS = [
        "Verstappen", "Leclerc", "Norris", "Hamilton", "Russell",
        "Piastri", "Alonso", "Gasly", "Albon", "Ocon",
        "Stroll", "Magnussen", "Bottas", "Zhou", "Ricciardo",
        "Tsunoda", "Colapinto", "Lawson", "Hadjar", "Martinez"
    ]

    # Gap values for pre-caching (0.1 to 10.0 in 0.1 steps + large gaps)
    CACHE_GAP_VALUES = [round(i * 0.1, 1) for i in range(1, 101)]  # 0.1 to 10.0
    LARGE_GAPS = [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 90, 120, 180]  # Large gaps

    @staticmethod
    def _generate_gap_calls() -> set[str]:
        """Generate gap calls with driver names + gap values."""
        lines = set()
        
        # Single gap ahead
        for driver in RadioLines.F1_DRIVERS:
            for gap in RadioLines.CACHE_GAP_VALUES:
                gap_text = RadioLines.format_gap(gap)
                lines.add(f"{driver} ahead, {gap_text}")
        
        # Single gap behind
        for driver in RadioLines.F1_DRIVERS:
            for gap in RadioLines.CACHE_GAP_VALUES:
                gap_text = RadioLines.format_gap(gap)
                lines.add(f"{driver} behind, {gap_text}")
        
        # Large gaps (ahead)
        for driver in RadioLines.F1_DRIVERS:
            for gap in RadioLines.LARGE_GAPS:
                gap_text = RadioLines.format_gap(gap)
                lines.add(f"{driver} ahead, {gap_text}")
                lines.add(f"{driver} behind, {gap_text}")
        
        return lines

    @staticmethod
    def _generate_teammate_pit_calls() -> set[str]:
        """Generate teammate pit calls with driver first names."""
        lines = set()
        
        # Driver first names
        first_names = ["Max", "Lewis", "Charles", "Lando", "George", "Carlos", 
                       "Oscar", "Fernando", "Pierre", "Alex", "Esteban", "Lance",
                       "Kevin", "Valtteri", "Guanyu", "Daniel", "Yuki", "Franco",
                       "Liam", "Gabriel"]
        
        # Templates (from teammate_pitting)
        templates = [
            "{first} is boxing this lap",
            "{first} pitting",
            "{first} in the pit lane",
        ]
        
        for name in first_names:
            for template in templates:
                lines.add(template.format(first=name))
        
        return lines

    @staticmethod
    def _generate_last_five_calls() -> set[str]:
        """Generate common last 5 laps variations."""
        lines = set()
        
        positions = list(range(1, 21))
        gaps = ["point 5", "one second", "two seconds", "three seconds", "four seconds"]
        
        # Basic position calls
        for pos in positions:
            lines.add(f"Five laps to go, P{pos}")
        
        # Position + gap ahead
        for pos in positions[:10]:  # P1-P10
            for gap in gaps:
                lines.add(f"Five laps to go, P{pos}, {gap} to the leader")
        
        # Podium / win scenarios
        lines.add("Five laps to go, This is for the win")
        lines.add("Five laps to go, This is for the podium")
        
        return lines

    @staticmethod
    def _generate_last_lap_calls() -> set[str]:
        """Generate common last lap variations."""
        lines = set()
        
        positions = list(range(1, 21))
        gaps = ["point 5", "one second", "two seconds", "three seconds"]
        
        # Basic
        lines.add("Last lap, Bring it home")
        
        # Win / podium
        lines.add("Last lap, This is for the win, Bring it home")
        lines.add("Last lap, This is for the podium, Keep it clean")
        
        # Position only
        for pos in positions:
            lines.add(f"Last lap, P{pos}")
        
        # Position + threat
        for pos in positions[:10]:
            for gap in gaps:
                lines.add(f"Last lap, P{pos}, {gap} to DRIVER behind, Defend the position")
        
        return lines
