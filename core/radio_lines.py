# core/radio_lines.py

import random
from .career_tracker import CareerTracker


DRIVER_NAME = "Shawn"


class RadioLines:
    """
    Snarky-to-warm radio line generator.
    Lines evolve over an 11-year career arc.
    """

    # ---------------------------------------------------------
    # NAME INJECTION
    # ---------------------------------------------------------

    @staticmethod
    def _maybe_name(career: CareerTracker) -> str:
        if random.random() < career.name_frequency:
            return f", {DRIVER_NAME}"
        return ""

    @staticmethod
    def _format(line: str, career: CareerTracker, **kwargs) -> str:
        name = RadioLines._maybe_name(career)
        return line.format(name=name, **kwargs)

    # ---------------------------------------------------------
    # OBJECTIVE START
    # ---------------------------------------------------------

    _objective_start = {
        "LAP_TIME": {
            "sharp": [
                "Copy that. Lap time objective noted. Let's see if you can actually deliver{name}.",
                "Right. Lap time tracking. I'll believe it when I see it{name}.",
                "Objective logged. Don't make me regret tracking this for you.",
            ],
            "professional": [
                "Lap time objective logged. Let's see what you can do{name}.",
                "Copy. Lap time target noted. I'll be watching.",
                "Right. Lap time tracking. Stay smooth and hit the marks.",
            ],
            "supportive": [
                "Lap time objective set. You've got this{name}.",
                "Copy that. Lap time target locked in. Let's find the time.",
                "Lap time noted. We'll get there together.",
            ],
            "partnership": [
                "Lap time objective. Let's find that time together{name}.",
                "Copy. Lap time target set. We'll work through it.",
                "Lap time noted. I know you'll nail it.",
            ],
        },
        "TYRE_MANAGEMENT": {
            "sharp": [
                "Tyre management. Try not to shred them this time{name}.",
                "Copy. Tyre management active. Your tyres, your problem.",
                "Tyre tracking. Don't cook them on the first lap, Shawn.",
            ],
            "professional": [
                "Tyre management objective logged. Keep temps in the window.",
                "Copy. Tyre management. Smooth inputs, long stints.",
                "Tyre tracking active. Manage the deg{name}.",
            ],
            "supportive": [
                "Tyre management. Keep them alive and we'll be strong at the end.",
                "Copy. Tyre tracking. You've got good feel for this now{name}.",
                "Tyre management noted. Trust your instincts on wear.",
            ],
            "partnership": [
                "Tyre management. We know how to handle this now{name}.",
                "Copy. Tyre tracking. You've always been good at this.",
                "Tyre objective set. We'll manage it together.",
            ],
        },
        "FUEL_SAVING": {
            "sharp": [
                "Fuel saving. Lift and coast, Shawn. I know you hate it but it's not negotiable.",
                "Fuel saving engaged. Try not to be a hero on the throttle{name}.",
                "Copy. Fuel saving. Short-shifting starts now.",
            ],
            "professional": [
                "Fuel saving objective logged. Manage the delta.",
                "Copy. Fuel saving. Lift early, coast long.",
                "Fuel tracking active. Stay under the target usage{name}.",
            ],
            "supportive": [
                "Fuel saving. You're good at this — just keep it consistent.",
                "Copy. Fuel management. We'll make the numbers work{name}.",
                "Fuel objective set. Smooth hands, smooth feet.",
            ],
            "partnership": [
                "Fuel saving. We'll manage it like we always do{name}.",
                "Copy. Fuel tracking. You know the drill.",
                "Fuel objective noted. We'll get it done.",
            ],
        },
        "ERS_MANAGEMENT": {
            "sharp": [
                "ERS management. Don't dump it all in one lap{name}.",
                "Copy. ERS tracking. Use it wisely, or don't. Your call.",
                "ERS objective logged. Try not to run out before the line.",
            ],
            "professional": [
                "ERS management objective set. Harvest and deploy smartly.",
                "Copy. ERS tracking. Balance the deployment across the lap.",
                "ERS management. Watch the state of charge{name}.",
            ],
            "supportive": [
                "ERS management. You've got good rhythm with this now.",
                "Copy. ERS tracking. Deploy on the straights, harvest under braking.",
                "ERS objective logged. Trust your feel for it{name}.",
            ],
            "partnership": [
                "ERS management. We know the balance now{name}.",
                "Copy. ERS tracking. You've always managed this well.",
                "ERS objective set. We'll dial it in together.",
            ],
        },
        "SECTOR_IMPROVEMENT": {
            "sharp": [
                "Sector improvement. Find time somewhere{name}.",
                "Copy. Sector target noted. Don't leave anything on the table.",
                "Sector tracking active. Push where it counts.",
            ],
            "professional": [
                "Sector improvement objective logged. Focus on the weak spots.",
                "Copy. Sector target set. Attack the problem areas.",
                "Sector tracking. Let's find the tenths{name}.",
            ],
            "supportive": [
                "Sector improvement. You know where the time is.",
                "Copy. Sector objective. We'll chip away at it{name}.",
                "Sector tracking active. Smooth is fast.",
            ],
            "partnership": [
                "Sector improvement. We'll find the time together{name}.",
                "Copy. Sector target. You know this track inside out now.",
                "Sector objective set. Let's work through it.",
            ],
        },
        "RACECRAFT": {
            "sharp": [
                "Racecraft objective. Try not to lose positions{name}.",
                "Copy. Racecraft tracking. Think before you dive bomb.",
                "Racecraft objective logged. Patience is not your strong suit, but try.",
            ],
            "professional": [
                "Racecraft objective set. Pick your moments.",
                "Copy. Racecraft tracking. Stay calm in the pack.",
                "Racecraft management. Smart overtakes only{name}.",
            ],
            "supportive": [
                "Racecraft objective. You've gotten much better at this.",
                "Copy. Racecraft tracking. Trust your race sense{name}.",
                "Racecraft logged. You know when to push and when to wait.",
            ],
            "partnership": [
                "Racecraft objective. You've mastered this over the years{name}.",
                "Copy. Racecraft tracking. You always know the right move.",
                "Racecraft set. We'll work the race together.",
            ],
        },
        "STRATEGY": {
            "sharp": [
                "Strategy objective. Try to stick to the plan{name}.",
                "Copy. Strategy tracking. Don't go rogue on me.",
                "Strategy logged. Follow the call, even when it hurts.",
            ],
            "professional": [
                "Strategy objective set. Trust the plan.",
                "Copy. Strategy tracking. We'll adjust as we go.",
                "Strategy management. Stay disciplined{name}.",
            ],
            "supportive": [
                "Strategy objective. You're good at executing the plan.",
                "Copy. Strategy tracking. We'll adapt when we need to{name}.",
                "Strategy logged. You've always been reliable on this.",
            ],
            "partnership": [
                "Strategy objective. We'll call it together{name}.",
                "Copy. Strategy tracking. We've always been in sync on this.",
                "Strategy set. We'll nail it like we always do.",
            ],
        },
        "DELTA_TARGET": {
            "sharp": [
                "Delta target. Hit the number or don't bother{name}.",
                "Copy. Delta tracking. Keep it positive or come in.",
                "Delta objective logged. The number is the number.",
            ],
            "professional": [
                "Delta target objective set. Manage the gap.",
                "Copy. Delta tracking. Stay within the window.",
                "Delta management. Watch the delta at all times{name}.",
            ],
            "supportive": [
                "Delta target. You've got good pace for this.",
                "Copy. Delta tracking. Keep it smooth and consistent{name}.",
                "Delta objective logged. You know how to manage this.",
            ],
            "partnership": [
                "Delta target. We'll manage it together{name}.",
                "Copy. Delta tracking. You always find the rhythm.",
                "Delta objective set. We'll get it done.",
            ],
        },
        "WEATHER": {
            "sharp": [
                "Weather objective. Keep me updated on the grip{name}.",
                "Copy. Weather tracking. Don't wait too long to call it.",
                "Weather objective logged. Feel the track and report back.",
            ],
            "professional": [
                "Weather objective set. Monitor conditions closely.",
                "Copy. Weather tracking. Call the crossover point when you feel it.",
                "Weather management. Stay alert on grip levels{name}.",
            ],
            "supportive": [
                "Weather objective. Your feel for conditions is good.",
                "Copy. Weather tracking. Trust your instincts on the crossover{name}.",
                "Weather logged. You've always been sharp on this.",
            ],
            "partnership": [
                "Weather objective. We'll read it together{name}.",
                "Copy. Weather tracking. You know what to listen for.",
                "Weather set. We'll call it as a team.",
            ],
        },
        "FORMATION": {
            "sharp": [
                "Formation objective. Warm the tyres and don't stall{name}.",
                "Copy. Formation tracking. Check the brakes, check the tyres.",
                "Formation objective logged. Don't overthink it.",
            ],
            "professional": [
                "Formation objective set. Follow the procedure.",
                "Copy. Formation tracking. Warm everything up properly.",
                "Formation management. Stay focused{name}.",
            ],
            "supportive": [
                "Formation objective. You know the routine by now.",
                "Copy. Formation tracking. Smooth and controlled{name}.",
                "Formation logged. You've always been solid on these.",
            ],
            "partnership": [
                "Formation objective. We've done this a hundred times{name}.",
                "Copy. Formation tracking. You know exactly what to do.",
                "Formation set. Let's get it done.",
            ],
        },
        "SAFETY_CAR": {
            "sharp": [
                "Safety car objective. Keep your delta positive{name}.",
                "Copy. SC tracking. Don't lose temps, don't lose focus.",
                "Safety car objective logged. Stay in the window.",
            ],
            "professional": [
                "Safety car objective set. Manage the delta and the temps.",
                "Copy. SC tracking. Stay sharp for the restart.",
                "Safety car management. Keep the tyres alive{name}.",
            ],
            "supportive": [
                "Safety car objective. You handle these well.",
                "Copy. SC tracking. Stay calm and manage the gap{name}.",
                "Safety car logged. You've always been disciplined under SC.",
            ],
            "partnership": [
                "Safety car objective. We know the drill{name}.",
                "Copy. SC tracking. You always manage these perfectly.",
                "Safety car set. We'll handle it together.",
            ],
        },
    }

    # Fallback for unrecognized types
    _objective_start_generic = {
        "sharp": [
            "Objective received: {description}. I'll track it. Whether you execute is another question{name}.",
            "Noted: {description}. Tracking now. Don't disappoint me{name}.",
            "Objective logged: {description}. Let's see if you can pull it off.",
        ],
        "professional": [
            "Objective received: {description}. Tracking now.",
            "Copy: {description}. I'll keep an eye on it{name}.",
            "Noted: {description}. Objective active.",
        ],
        "supportive": [
            "Objective received: {description}. We'll work through it{name}.",
            "Copy: {description}. Tracking now. You've got this.",
            "Noted: {description}. Let's make it happen.",
        ],
        "partnership": [
            "Objective received: {description}. We're on it{name}.",
            "Copy: {description}. We'll handle it together.",
            "Noted: {description}. Let's get it done.",
        ],
    }

    # ---------------------------------------------------------
    # OBJECTIVE PASS
    # ---------------------------------------------------------

    _objective_pass = {
        "sharp": [
            "Objective complete. I'm impressed{name}. Truly.",
            "Done it. About time.",
            "Objective passed. See? You can follow instructions when you want to{name}.",
            "Nice work. I'll add it to the list of things you've actually gotten right.",
            "Confirmed. Objective complete. Don't let it go to your head{name}.",
        ],
        "professional": [
            "Objective complete. Solid work{name}.",
            "Confirmed. Well executed.",
            "Objective passed. Good job, Shawn.",
            "Done it. Clean execution{name}.",
            "Objective complete. That's how it's done.",
        ],
        "supportive": [
            "Objective complete. Great work{name}.",
            "Confirmed. You nailed it.",
            "Objective passed. Really well driven, Shawn.",
            "Done it. I knew you could{name}.",
            "Objective complete. Excellent execution.",
        ],
        "partnership": [
            "Objective complete. We make a good team{name}.",
            "Confirmed. Another one done together.",
            "Objective passed. That's what we do, Shawn.",
            "Done it. Always satisfying when the plan works{name}.",
            "Objective complete. We're in sync.",
        ],
    }

    # ---------------------------------------------------------
    # OBJECTIVE FAIL
    # ---------------------------------------------------------

    _objective_fail = {
        "sharp": [
            "Objective failed. I'm not even surprised{name}.",
            "Failed. Reset when you're ready to try again. Or don't. Your call.",
            "Objective failed. We'll pretend that didn't happen{name}.",
            "That's a fail. I've seen better from AI drivers, Shawn.",
            "Failed. The objective, not you. Well... maybe you too{name}.",
        ],
        "professional": [
            "Objective failed. Reset when you're ready{name}.",
            "Failed. No big deal. We'll try again.",
            "Objective didn't stick. Move on and focus on the next one.",
            "Failed. Shake it off, Shawn. Next objective.",
            "Objective failed. We'll get the next one{name}.",
        ],
        "supportive": [
            "Objective failed. It happens. We'll get the next one{name}.",
            "Failed. Don't dwell on it. Focus forward.",
            "Objective didn't land. You'll nail the next one, Shawn.",
            "Failed. No worries. We're still in a good spot{name}.",
            "Objective failed. Shake it off and keep pushing.",
        ],
        "partnership": [
            "Objective failed. Doesn't matter. We'll get the next one{name}.",
            "Failed. We'll bounce back. We always do.",
            "Objective didn't stick. We're still strong, Shawn.",
            "Failed. Not a problem. We've got plenty more to go{name}.",
            "Objective failed. We'll regroup and move forward.",
        ],
    }

    # ---------------------------------------------------------
    # OBJECTIVE CANCEL
    # ---------------------------------------------------------

    _objective_cancel = {
        "sharp": [
            "Objective cancelled. Smart call, or are you just avoiding the challenge{name}?",
            "Cancelled. I respect the honesty.",
            "Objective scrubbed. Moving on.",
            "Cancelled. Probably for the best{name}.",
            "Objective cancelled. I won't pretend I'm surprised.",
        ],
        "professional": [
            "Objective cancelled. Understood{name}.",
            "Cancelled. Moving on to the next one.",
            "Objective scrubbed. We'll set a new one when you're ready.",
            "Cancelled. Copy that{name}.",
            "Objective cancelled. Reset and refocus.",
        ],
        "supportive": [
            "Objective cancelled. No problem, we'll set a new one when you're ready{name}.",
            "Cancelled. Sometimes it's the right call.",
            "Objective scrubbed. We'll find a better one for you, Shawn.",
            "Cancelled. All good. What's next{name}?",
            "Objective cancelled. We'll pivot to something more useful.",
        ],
        "partnership": [
            "Objective cancelled. We'll find a better one together{name}.",
            "Cancelled. No worries. What should we focus on instead?",
            "Objective scrubbed. We'll adjust the plan, Shawn.",
            "Cancelled. We'll set something more relevant{name}.",
            "Objective cancelled. We're still on track overall.",
        ],
    }

    # ---------------------------------------------------------
    # TITLE SCENARIOS
    # ---------------------------------------------------------

    _f2_championship = [
        "F2 champion. You belong here, Shawn. F1 won't know what hit it.",
        "F2 title. You earned this. Next stop: the big league{name}.",
        "F2 champion. I knew you had it in you. F1 is next.",
    ]

    _first_f1_title = [
        "World Champion. Shawn... you're World Champion. I always believed you could do this. Always.",
        "You did it. World Champion. I've been waiting to say this since day one{name}.",
        "World Champion. After everything we've been through... this is it. You're the best.",
    ]

    _consecutive_2 = [
        "Back-to-back. Two titles. Nobody can say it was luck{name}.",
        "Two in a row. You're proving it wasn't a fluke.",
        "Back-to-back champion. Impressive, Shawn. Truly.",
    ]

    _consecutive_3 = [
        "Three in a row. You're building a legacy{name}.",
        "Three consecutive titles. History is starting to notice, Shawn.",
        "Three-peat. You're not just winning — you're dominating.",
    ]

    _consecutive_4_to_7 = [
        "{n} titles in a row. You're not just winning anymore, you're dominating{name}.",
        "{n} consecutive championships. I've run out of ways to be impressed, Shawn.",
        "Title number {n}. At this point it's just expected, isn't it{name}?",
        "{n} in a row. The record books are starting to look very one-sided.",
    ]

    _consecutive_8_plus = [
        "Another one. That's {n} now. When I started with you in F2, I never imagined this{name}.",
        "{n} titles. I stopped counting after a while. You never did.",
        "Title {n}. A decade ago you were fighting for F2 points. Look at you now{name}.",
        "{n} championships. We've come a long way from that first F2 season, Shawn.",
    ]

    # ---------------------------------------------------------
    # CAREER MILESTONES
    # ---------------------------------------------------------

    _year_5 = [
        "Five years. We've been together a while now, Shawn. Let's keep it going.",
        "Year five. Half a decade of this. Not bad for a partnership{name}.",
        "Five years together. Through everything. Let's keep pushing.",
    ]

    _year_10 = [
        "Ten years. A decade of this. I can't imagine doing it with anyone else, Shawn.",
        "Ten years together. Through everything. I'm not going anywhere{name}.",
        "A decade. Ten years of races, titles, and everything in between. Wouldn't trade it.",
    ]

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

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
