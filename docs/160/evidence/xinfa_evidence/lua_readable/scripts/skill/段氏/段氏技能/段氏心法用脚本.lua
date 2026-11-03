Include("scripts/Include/Skill.lh")
Include("scripts/Include/NewSkill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 703,
    nSpunkAttackPower = 268,
    nNeutralHit = 10,
    nNeutralCritical = 43,
    nMagicDefence = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 982,
    nSpunkAttackPower = 372,
    nNeutralHit = 18,
    nNeutralCritical = 59,
    nMagicDefence = 26
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1491,
    nSpunkAttackPower = 564,
    nNeutralHit = 28,
    nNeutralCritical = 90,
    nMagicDefence = 40
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2000,
    nSpunkAttackPower = 754,
    nNeutralHit = 39,
    nNeutralCritical = 120,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 703,
    nSpunkAttackPower = 268,
    nNeutralHit = 10,
    nNeutralCritical = 43,
    nMagicDefence = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 982,
    nSpunkAttackPower = 372,
    nNeutralHit = 18,
    nNeutralCritical = 59,
    nMagicDefence = 26
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1491,
    nSpunkAttackPower = 564,
    nNeutralHit = 28,
    nNeutralCritical = 90,
    nMagicDefence = 40
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2000,
    nSpunkAttackPower = 754,
    nNeutralHit = 39,
    nNeutralCritical = 120,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
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
  local L1_1, L2_2, L3_3
  L1_1 = false
  L2_2 = A0_0.dwLevel
  L3_3 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/段氏/段氏技能/段氏心法用脚本.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_SUN_ENERGY, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MOON_ENERGY, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2653, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NEUTRAL_CRITICAL_STRIKE, tSkillData[L2_2].nNeutralCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_NEUTRAL_ATTACK_POWER_COF, 625, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_NEUTRAL_CRITICAL_STRIKE_COF, 143, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10786], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.NEUTRAL_MAGIC, SKILL_KIND_TYPE.NEUTRAL_MAGIC)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5, A2_6)
  return A1_5
end
function OnSkillLevelUp(A0_7, A1_8)
  if not A1_8.GetKungfuMountID() then
    A1_8.MountKungfu(A0_7.dwSkillID, A0_7.dwLevel)
  end
  A1_8.LearnSkillLevel(38565, A0_7.dwLevel, A1_8.dwID)
end
function OnSkillForgotten(A0_9, A1_10)
end
function Apply(A0_11)
  if GetPlayer(A0_11) then
    GetPlayer(A0_11).AddBuff(GetPlayer(A0_11).dwID, GetPlayer(A0_11).nLevel, 14275, 1)
    GetPlayer(A0_11).bSurplusAutoCast = false
    GetPlayer(A0_11).bSurplusAutoReplenish = false
    if GetPlayer(A0_11).GetSkillLevel(38014) == 1 then
      GetPlayer(A0_11).AddBuff(GetPlayer(A0_11).dwID, GetPlayer(A0_11).nLevel, 29476, 1)
    end
  end
end
function UnApply(A0_12)
  if not GetPlayer(A0_12) then
    return
  end
  GetPlayer(A0_12).DelBuff(29476, 1)
end
function OnRemove(A0_13, A1_14, A2_15, A3_16, A4_17, A5_18, A6_19, A7_20, A8_21, A9_22)
end
function OnEarlyWarning(A0_23, A1_24)
end
