Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 18,
    nMaxMana = 524,
    nSpunkAttackPower = 804,
    nNeutralCritical = 26
  },
  {
    DecriticalDamagePowerBase = 32,
    nMaxMana = 732,
    nSpunkAttackPower = 904,
    nNeutralCritical = 37
  },
  {
    DecriticalDamagePowerBase = 51,
    nMaxMana = 1112,
    nSpunkAttackPower = 1104,
    nNeutralCritical = 56
  },
  {
    DecriticalDamagePowerBase = 69,
    nMaxMana = 2014,
    nSpunkAttackPower = 1304,
    nNeutralCritical = 75
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6042,
    nSpunkAttackPower = 2586,
    nNeutralCritical = 223
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6042,
    nSpunkAttackPower = 2586,
    nNeutralCritical = 223
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6042,
    nSpunkAttackPower = 2586,
    nNeutralCritical = 223
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6042,
    nSpunkAttackPower = 2586,
    nNeutralCritical = 223
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6042,
    nSpunkAttackPower = 2586,
    nNeutralCritical = 223
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6042,
    nSpunkAttackPower = 2586,
    nNeutralCritical = 223
  },
  {
    DecriticalDamagePowerBase = 18,
    nMaxMana = 524,
    nSpunkAttackPower = 304,
    nNeutralCritical = 26
  },
  {
    DecriticalDamagePowerBase = 32,
    nMaxMana = 732,
    nSpunkAttackPower = 421,
    nNeutralCritical = 37
  },
  {
    DecriticalDamagePowerBase = 51,
    nMaxMana = 1112,
    nSpunkAttackPower = 640,
    nNeutralCritical = 56
  },
  {
    DecriticalDamagePowerBase = 69,
    nMaxMana = 2014,
    nSpunkAttackPower = 855,
    nNeutralCritical = 75
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6042,
    nSpunkAttackPower = 2586,
    nNeutralCritical = 223
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
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.NEUTRAL_MAGIC, SKILL_KIND_TYPE.NEUTRAL_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[101450], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_ENERGY, tSkillKungfuConst.LOGIC.QI[101450].MAX, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.QI_ENERGY_REPLENISH, tSkillKungfuConst.LOGIC.QI[101450].REPLENISH, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_NEUTRAL_ATTACK_POWER_COF, 645, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_NEUTRAL_CRITICAL_STRIKE_COF, 123, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NEUTRAL_CRITICAL_STRIKE, tSkillData[L2_2].nNeutralCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/衍天/移动端_心法_太玄经.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function CanLearnSkill(A0_6, A1_7)
  local L2_8
  L2_8 = true
  return L2_8
end
function OnSkillLevelUp(A0_9, A1_10)
  if not A1_10.GetKungfuMountID() then
    A1_10.MountKungfu(A0_9.dwSkillID, A0_9.dwLevel)
  end
  A1_10.AddSkillRecipe(17076, 1)
  A1_10.AddSkillRecipe(17077, 1)
  A1_10.AddSkillRecipe(17078, 1)
  A1_10.AddSkillRecipe(17079, 1)
  A1_10.AddSkillRecipe(17080, 1)
  A1_10.AddSkillRecipe(17081, 1)
  A1_10.AddSkillRecipe(17082, 1)
  A1_10.AddSkillRecipe(17083, 1)
  A1_10.AddSkillRecipe(17084, 1)
  A1_10.AddSkillRecipe(17085, 1)
  A1_10.AddSkillRecipe(17086, 1)
  A1_10.AddSkillRecipe(17087, 1)
  A1_10.AddSkillRecipe(17088, 1)
  A1_10.AddSkillRecipe(17089, 1)
  A1_10.AddSkillRecipe(17090, 1)
  A1_10.AddSkillRecipe(17091, 1)
  A1_10.AddSkillRecipe(17092, 1)
  A1_10.AddSkillRecipe(17093, 1)
  A1_10.AddSkillRecipe(17094, 1)
  A1_10.AddSkillRecipe(17095, 1)
  A1_10.AddSkillRecipe(17597, 1)
  A1_10.AddSkillRecipe(17598, 1)
end
function Apply(A0_11)
  if not GetPlayer(A0_11) then
    return
  end
  GetPlayer(A0_11).AddBuff(GetPlayer(A0_11).dwID, GetPlayer(A0_11).nLevel, 14275, 1)
  GetPlayer(A0_11).bSurplusAutoCast = false
  GetPlayer(A0_11).bSurplusAutoReplenish = false
  GetPlayer(A0_11).LearnSkillLevel(102709, 1, false)
end
function UnApply(A0_12)
  if not GetPlayer(A0_12) then
    return
  end
  GetPlayer(A0_12).DelBuff(71232, 1)
  GetPlayer(A0_12).DelBuff(71260, 1)
end
function OnTimer(A0_13, A1_14, A2_15)
end
