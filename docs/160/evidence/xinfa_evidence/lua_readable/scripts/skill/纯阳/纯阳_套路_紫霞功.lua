Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 520,
    nSpunkAttackPower = 268,
    nNeutralHit = 10,
    nNeutralCritical = 85,
    nMagicDefence = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 727,
    nSpunkAttackPower = 372,
    nNeutralHit = 18,
    nNeutralCritical = 119,
    nMagicDefence = 26
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1104,
    nSpunkAttackPower = 564,
    nNeutralHit = 28,
    nNeutralCritical = 180,
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
    nMaxMana = 520,
    nSpunkAttackPower = 268,
    nNeutralHit = 10,
    nNeutralCritical = 85,
    nMagicDefence = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 727,
    nSpunkAttackPower = 372,
    nNeutralHit = 18,
    nNeutralCritical = 119,
    nMagicDefence = 26
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1104,
    nSpunkAttackPower = 564,
    nNeutralHit = 28,
    nNeutralCritical = 180,
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 5, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_NEUTRAL_ATTACK_POWER_COF, 727, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_NEUTRAL_CRITICAL_STRIKE_COF, 41, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NEUTRAL_CRITICAL_STRIKE, tSkillData[L2_2].nNeutralCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 228, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 354, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2941, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/纯阳/纯阳_套路_紫霞功.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 89, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.NEUTRAL_MAGIC, SKILL_KIND_TYPE.NEUTRAL_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10014], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_ENERGY, tSkillKungfuConst.LOGIC.QI[10014].MAX, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.QI_ENERGY_REPLENISH, tSkillKungfuConst.LOGIC.QI[10014].REPLENISH, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function OnSkillLevelUp(A0_6, A1_7)
  local L2_8, L3_9
  L2_8 = A1_7.GetKungfuMount
  L2_8 = L2_8()
  if not L2_8 then
    L3_9 = A1_7.MountKungfu
    L3_9(A0_6.dwSkillID, A0_6.dwLevel)
  end
  L3_9 = A0_6.dwLevel
  if A1_7.dwForceID == 4 and A1_7.GetSkillLevel(10199) < 1 then
    A1_7.LearnSkill(10199)
  end
  A1_7.LearnSkillLevel(345, L3_9, A1_7.dwID)
  A1_7.LearnSkill(484)
end
function Apply(A0_10)
  if GetPlayer(A0_10) then
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 624, 1)
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 6094, 1)
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 6095, 1)
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 14275, 1)
    GetPlayer(A0_10).bSurplusAutoCast = false
    GetPlayer(A0_10).bSurplusAutoReplenish = false
  end
end
function UnApply(A0_11)
  if GetPlayer(A0_11) then
    GetPlayer(A0_11).DelBuff(624, 1)
    GetPlayer(A0_11).DelBuff(6094, 1)
    GetPlayer(A0_11).DelBuff(6095, 1)
  end
end
function OnTimer(A0_12, A1_13, A2_14)
end
