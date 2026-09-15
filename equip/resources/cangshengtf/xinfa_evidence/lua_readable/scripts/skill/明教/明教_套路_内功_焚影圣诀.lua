Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nAttackPower = 313,
    nMagicDefence = 17,
    nPhysicsCri = 5,
    nHit = 9
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nAttackPower = 434,
    nMagicDefence = 24,
    nPhysicsCri = 6,
    nHit = 16
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nAttackPower = 658,
    nMagicDefence = 37,
    nPhysicsCri = 9,
    nHit = 25
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nAttackPower = 880,
    nMagicDefence = 49,
    nPhysicsCri = 11,
    nHit = 35
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nAttackPower = 313,
    nMagicDefence = 17,
    nPhysicsCri = 5,
    nHit = 9
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nAttackPower = 434,
    nMagicDefence = 24,
    nPhysicsCri = 6,
    nHit = 16
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nAttackPower = 658,
    nMagicDefence = 37,
    nPhysicsCri = 9,
    nHit = 25
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nAttackPower = 880,
    nMagicDefence = 49,
    nPhysicsCri = 11,
    nHit = 35
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  }
}
tSkillHuajinData = {
  {DecriticalDamagePowerBase = 18},
  {DecriticalDamagePowerBase = 32},
  {DecriticalDamagePowerBase = 51},
  {DecriticalDamagePowerBase = 69},
  {DecriticalDamagePowerBase = 87},
  {DecriticalDamagePowerBase = 106},
  {DecriticalDamagePowerBase = 124},
  {DecriticalDamagePowerBase = 143},
  {DecriticalDamagePowerBase = 161},
  {DecriticalDamagePowerBase = 356},
  {DecriticalDamagePowerBase = 782},
  {DecriticalDamagePowerBase = 1725}
}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/明教/明教_套路_内功_焚影圣诀.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10242], 1)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_SOLAR_AND_LUNAR_ATTACK_POWER_COF, 635, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_SOLAR_AND_LUNAR_CRITICAL_STRIKE_COF, 133, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_SUN_ENERGY, 10000, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MOON_ENERGY, 10000, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LUNAR_ATTACK_POWER_BASE, tSkillData[L1_1].nAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SOLAR_ATTACK_POWER_BASE, tSkillData[L1_1].nAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L1_1].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_PERCENT, 1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2622, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 912, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1296, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1335, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1336, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1337, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1338, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1339, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1340, 1)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  local L2_6, L3_7
  L2_6 = A1_5.GetKungfuMountID
  L2_6 = L2_6()
  if not L2_6 then
    L3_7 = A1_5.MountKungfu
    L3_7(A0_4.dwSkillID, A0_4.dwLevel)
  end
  L3_7 = A0_4.dwLevel
  if A1_5.dwForceID == 10 and A1_5.GetSkillLevel(10240) < 1 then
    A1_5.LearnSkill(10240)
  end
  A1_5.LearnSkillLevel(4258, L3_7, A1_5.dwID)
  A1_5.LearnSkill(4259)
  A1_5.LearnSkill(4431)
end
function Apply(A0_8)
  if not GetPlayer(A0_8) then
    return
  end
  GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 14275, 1)
  GetPlayer(A0_8).bSurplusAutoCast = false
  GetPlayer(A0_8).bSurplusAutoReplenish = false
  GetPlayer(A0_8).nCurrentSunEnergy = 0
  GetPlayer(A0_8).nCurrentMoonEnergy = 0
  GetPlayer(A0_8).nSunPowerValue = 0
  GetPlayer(A0_8).nMoonPowerValue = 0
  GetPlayer(A0_8).DelMultiGroupBuffByID(30270)
  GetPlayer(A0_8).AddBuff(A0_8, GetPlayer(A0_8).nLevel, 30270, 1)
end
function UnApply(A0_9)
  if not GetPlayer(A0_9) then
    return
  end
  GetPlayer(A0_9).nCurrentSunEnergy = 0
  GetPlayer(A0_9).nCurrentMoonEnergy = 0
  GetPlayer(A0_9).nSunPowerValue = 0
  GetPlayer(A0_9).nMoonPowerValue = 0
  GetPlayer(A0_9).DelMultiGroupBuffByID(30270)
end
function OnTimer(A0_10, A1_11, A2_12)
end
