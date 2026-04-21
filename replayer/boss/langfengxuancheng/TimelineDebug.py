from __future__ import annotations


def recordTimelineShout(replayer, event):
    if event.dataType != "Shout":
        return
    if event.content in ['""', ""]:
        return

    replayer.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")


def recordTimelineScene(replayer, event):
    if event.dataType != "Scene" or event.enter != 1:
        return
    if event.id not in replayer.bld.info.npc:
        return

    npc = replayer.bld.info.npc[event.id]
    name = replayer.bld.info.getName(event.id)
    if name == "":
        return
    if "的" in name:
        return

    key = "n%s" % npc.templateID
    if event.time - replayer.bhTime.get(key, 0) <= 3000:
        return

    replayer.bhTime[key] = event.time
    replayer.bh.setEnvironment(npc.templateID, name, "341", event.time, 0, 1, "NPC出现", "npc")


def recordDebugShout(replayer, event):
    if event.dataType != "Shout":
        return
    if event.content in ['""', ""]:
        return
    if not getattr(replayer, "debug", 0):
        return

    replayer.bh.setEnvironment("0", event.content, "341", event.time, 0, 1, "喊话", "shout")


def printDebugTimeline(replayer):
    if getattr(replayer, "debug", 0):
        replayer.bh.printEnvironmentInfo(True)
