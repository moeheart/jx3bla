"""Sequential offline analysis with equipment continuity across encounters."""
from pathlib import Path
from types import SimpleNamespace

from MainWindow import MainWindow


class AnalysisCancelled(Exception):
    """Cooperative cancellation between parser updates and analysis stages."""


def display_result(actor):
    """Keep processed views and shared upload anchors, release raw event streams."""
    from data.PersonalTimeline import build_personal_timelines
    metrics = ('rhps', 'hps', 'ahps', 'ohps', 'chps', 'rdps', 'ndps', 'mrdps', 'mndps', 'rdpsStatus')
    return SimpleNamespace(
        bossAnalyseName=actor.bossAnalyseName, mapDetail=actor.mapDetail,
        server=actor.bld.info.server, timestamp=actor.bld.info.battleTime,
        startTime=actor.startTime, finalTime=actor.finalTime, battleTime=actor.battleTime,
        personalTimelines=build_personal_timelines(actor),
        win=actor.win, statDict=actor.statDict, occResult=actor.occResult,
        playerNames={key: value.name for key, value in actor.bld.info.player.items()},
        detail=actor.detail, bh=actor.bh, attributeStatus=actor.attributeStatus,
        mask=bool(actor.config.item['general'].get('mask', 0)),
        potList=[list(p) if len(p) >= 7 else [*p, 0] for p in actor.potList],
        combatTracker={name: getattr(actor.combatTracker, name) for name in metrics},
    )


class ReplaySession(MainWindow):
    def __init__(self, notice=None):
        super().__init__(notice)
        self.playerEquipment = {}
        self.playerEquipmentAnalysed = {}
        self.playerEquipmentOwners = {}
        self.lastBld = None
        self.stat_percent = {}
        self.cancel_requested = lambda: False

    def checkpoint(self):
        if self.cancel_requested():
            raise AnalysisCancelled()

    def setNotice(self, update):
        self.checkpoint()
        super().setNotice(update)

    def analyse(self, path, config):
        """Return a completed actor, or None for a partial encounter."""
        from data.BattleLogData import BattleLogData
        from replayer.ActorReplayPro import ActorProReplayer

        path = Path(path)
        bld = BattleLogData(self)
        if path.suffix.lower() == '.jcl':
            bld.loadFromJcl(str(path))
        elif path.name.lower().endswith('.fstt.jx3dat'):
            with path.open('rb') as source:
                if source.read(4) == b'CNDK':
                    raise ValueError('此版本的茗伊二进制记录尚不支持，请选择团队工具生成的 JCL。')
            bld.loadFromJx3dat(str(path))
        else:
            raise ValueError('请选择 JCL 或旧版文本 .fstt.jx3dat 战斗记录。')
        if not bld.log:
            raise ValueError('文件中没有可分析的战斗事件。')
        if self.lastBld is not None:
            bld.merge(self.lastBld)

        # Actor analysis can update equipment and enqueue personal results before
        # the final stage succeeds. A failed log must not leak into the next one.
        previous = (self.playerEquipment.copy(), self.playerEquipmentAnalysed.copy(),
                    self.playerEquipmentOwners.copy())
        queued = len(self.uploadData)
        key = str(path)
        try:
            actor = ActorProReplayer(config, [key, 0, 1], '', {key: bld}, self)
            if actor.FirstStageAnalysis() == 1:
                raise ValueError('日志缺少复盘所需的战斗信息。')
            actor.SecondStageAnalysis()
            if not actor.available:
                self.lastBld = bld
                return None
            self.checkpoint()
            actor.ThirdStageAnalysis()
            self.checkpoint()
            actor.OccAnalysis()
            self.checkpoint()
            if actor.upload:
                actor.prepareUpload()
        except Exception:
            self.playerEquipment, self.playerEquipmentAnalysed, self.playerEquipmentOwners = previous
            del self.uploadData[queued:]
            raise
        self.lastBld = None
        return actor
