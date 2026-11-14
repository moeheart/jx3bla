"""Conservative objective availability inside an independently observed transition."""
from data.DataContent import get_reflected_damage


class TransitionAvailability:
    """Object lifetimes and actual damage can preserve, never invent, downtime.

    The boss must supply a complete, owned transition start/end pair. Silence
    outside that pair is not evidence. Scene/Death edges keep the previous
    phase's objectives available until the final one departs. A positive hit
    inside the remaining candidate rejects it instead of deleting real output.
    """

    def __init__(self, start_time, objective_templates):
        self.startTime = start_time
        self.templates = frozenset(objective_templates)
        self.active = {}
        self.closed = []
        self.closedIDs = set()
        self.damageTimes = []

    def observe(self, event, info):
        if event.dataType in ('Scene', 'Death'):
            npc = info.npc.get(event.id)
            if npc is not None and str(npc.templateID) in self.templates:
                if event.dataType == 'Scene' and event.enter:
                    self.active.setdefault(event.id, (event.time, str(npc.templateID)))
                else:
                    if event.id not in self.active and event.id in self.closedIDs:
                        return
                    # A departure also proves an objective existed when its
                    # entry was outside this log; keep the earlier span valid.
                    start, template = self.active.pop(event.id, (self.startTime, str(npc.templateID)))
                    self.closed.append((start, event.time, template))
                    self.closedIDs.add(event.id)
        elif event.dataType == 'Skill':
            if event.target in info.npc and event.damageEff > 0:
                self.damageTimes.append(event.time)
                npc = info.npc[event.target]
                if str(npc.templateID) in self.templates:
                    self.active.setdefault(event.target, (event.time, str(npc.templateID)))
            if get_reflected_damage(event, info) is not None:
                self.damageTimes.append(event.time)

    def resolve(self, start, end, encounter_end, complete):
        result = dict(affectDps=False, affectHealer=False, duration=0,
                      rule='owned_transition_after_objectives_depart')
        if not complete or end > encounter_end or end <= start:
            return dict(result, reason='missing_in_bounds_transition_end')
        if any(first < end for first, _ in self.active.values()):
            return dict(result, reason='objective_still_present')
        periods = [row for row in self.closed if row[0] < end]
        if not periods:
            return dict(result, reason='missing_objective_departure_evidence')
        if any(last > end for _, last, _ in periods):
            return dict(result, reason='objective_present_through_transition_end')
        candidate_start = max(start, max(last for _, last, _ in periods))
        if candidate_start >= end:
            return dict(result, reason='objectives_cover_transition')
        if any(candidate_start <= time <= end for time in self.damageTimes):
            return dict(result, reason='effective_damage_inside_candidate')
        return dict(result, affectDps=True, start=candidate_start, end=end,
                    duration=end-candidate_start, reason='confirmed_targetless_transition',
                    lastObjectiveDeparture=max(last for _, last, _ in periods),
                    objectiveTemplates=sorted({template for _, _, template in periods}))
