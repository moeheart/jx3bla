"""Observed output pauses for Tuli/Tian; healing remains active throughout."""
from data.DataContent import get_reflected_damage


class FirstThreeDowntime:
    """Require paired boss signals and preserve every observed damaging event.

    NPC state snapshots in these JCLs do not expose runtime selectability. The
    10082 Buff table calls 35857/35858 Tuli's skill-pause/start markers; they
    are not immunity or player-control Buffs. Tian's sword-preparation window
    ends at the actual sword entry, never at its death.
    """
    def __init__(self, replayer, kind):
        self.replayer = replayer
        self.kind = kind
        self.pending = {}
        self.fields = {}
        self.activeSwords = set()
        self.damageTimes = set()
        self.pairs = []
        self.finalized = False

    def template(self, identifier):
        npc = self.replayer.bld.info.npc.get(identifier)
        return str(npc.templateID) if npc else ''

    def observe(self, event):
        owner = self.replayer
        info = owner.bld.info
        if getattr(info, 'map', '') not in ('25人普通洛阳之战', '25人英雄洛阳之战'):
            return
        if event.dataType == 'Skill':
            # Include every NPC target and the independent reflected-damage
            # result. A boss-only check could erase output to another objective.
            if (event.caster in info.player and event.target in info.npc
                    and event.damageEff > 0):
                self.damageTimes.add(event.time)
                if self.kind == 'tian' and self.template(event.target) in owner.SWORD:
                    self.activeSwords.add(event.target)
            if get_reflected_damage(event, info) is not None:
                self.damageTimes.add(event.time)
        if self.kind == 'tuli':
            self.observe_tuli(event)
        elif self.kind == 'tian':
            self.observe_tian(event)

    def observe_tuli(self, event):
        owner = self.replayer
        if (event.dataType != 'Buff' or self.template(event.caster) not in owner.MAIN
                or event.target not in owner.statDict):
            return
        valid = getattr(event, 'isValid', True)
        gained = (event.stack > 0 and valid and
                  getattr(event, 'delete', False) in (False, 'false', 0, '0'))
        if event.id == '35857' and gained:
            # The marker is sent to each player; those copies are one signal.
            self.pending.setdefault(event.caster, dict(start=event.time,
                sourceTemplate=self.template(event.caster), name='玄溟转阶段',
                rule='tuli_pause_and_resume_markers'))
        elif event.id == '34490':
            fields = self.fields.setdefault(event.caster, set())
            record = self.pending.get(event.caster)
            if gained:
                fields.add(event.target)
                if record is not None:
                    record['fieldsObserved'] = True
            elif event.target in fields:
                fields.remove(event.target)
                if not fields and record is not None and record.get('fieldsObserved'):
                    record.setdefault('fieldEnd', event.time)
        elif event.id == '35858' and gained:
            record = self.pending.pop(event.caster, None)
            if record is not None:
                # All observed field removals are an independent mechanism end.
                # In the heroic log this precedes the resume packet by 29/69ms.
                record['signalEnd'] = event.time
                record['boundaryEnd'] = min(event.time, record.get('fieldEnd', event.time))
                self.pairs.append(record)

    def observe_tian(self, event):
        owner = self.replayer
        if event.dataType == 'Shout' and self.template(event.id) in owner.MAIN:
            if event.content.strip('"') in ('抬头看好了——这一剑，送你们上路！', '哼哼！不错，那么第二剑呢？'):
                self.pending.setdefault(event.id, dict(start=event.time,
                    sourceTemplate=self.template(event.id), name='天陨一剑准备',
                    rule='tian_preparation_until_sword_entry',
                    objectiveAlreadyPresent=bool(self.activeSwords)))
        elif (event.dataType in ('Scene', 'Death') and
              self.template(event.id) in owner.SWORD):
            if event.dataType == 'Scene' and event.enter:
                for record in self.pending.values():
                    record.update(signalEnd=event.time, boundaryEnd=event.time)
                    self.pairs.append(record)
                self.pending.clear()
                self.activeSwords.add(event.id)
            else:
                self.activeSwords.discard(event.id)

    def finalize(self):
        if self.finalized:
            return
        self.finalized = True
        owner = self.replayer
        evidence = owner.detail.setdefault('downtimeEvidence', [])
        records = self.pairs + [dict(record, incomplete=True) for record in self.pending.values()]
        for record in records:
            start = max(owner.startTime, record['start'])
            if start >= owner.finalTime:
                continue
            boundary = record.get('boundaryEnd', owner.finalTime)
            # Consumers switch state only when event.time > the boundary.
            # End one millisecond earlier to retain damage at the resume/entry.
            end = min(owner.finalTime, boundary - 1)
            reason = 'confirmed_output_pause'
            if record.get('incomplete') or record.get('signalEnd', owner.finalTime+1) > owner.finalTime:
                reason = 'missing_in_bounds_end_signal'
            elif record.get('objectiveAlreadyPresent'):
                reason = 'sword_already_present'
            elif end <= start:
                reason = 'empty_interval'
            elif any(start < time <= end for time in self.damageTimes):
                reason = 'effective_damage_inside_candidate'
            accepted = reason == 'confirmed_output_pause'
            if accepted:
                owner.bh.setBadPeriod(start, end, True, False)
            evidence.append(dict(record, start=start, end=max(start, end),
                duration=max(0, end-start)/1000, excludedMs=max(0, end-start) if accepted else 0,
                affectDps=accepted, affectHealer=False, reason=reason))
        owner.bh.calBadPeriod()
        owner.detail['effectiveTimeDps'] = owner.bh.sumTime('dps')
        owner.detail['effectiveTimeHealer'] = owner.bh.sumTime('healer')
