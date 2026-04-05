from __future__ import annotations


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
