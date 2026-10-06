Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    nMP = 519,
    nSpunkAttackPower = 768,
    nNeHit = 8,
    nMagicDefence = 25,
    nLunarCritical = 36,
    DecriticalDamagePowerBase = 25
  },
  {
    nMP = 725,
    nSpunkAttackPower = 868,
    nNeHit = 14,
    nMagicDefence = 35,
    nLunarCritical = 50,
    DecriticalDamagePowerBase = 44
  },
  {
    nMP = 1101,
    nSpunkAttackPower = 1068,
    nNeHit = 22,
    nMagicDefence = 54,
    nLunarCritical = 76,
    DecriticalDamagePowerBase = 70
  },
  {
    nMP = 1994,
    nSpunkAttackPower = 1268,
    nNeHit = 31,
    nMagicDefence = 73,
    nLunarCritical = 102,
    DecriticalDamagePowerBase = 95
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 519,
    nSpunkAttackPower = 268,
    nNeHit = 8,
    nMagicDefence = 25,
    nLunarCritical = 36,
    DecriticalDamagePowerBase = 25
  },
  {
    nMP = 725,
    nSpunkAttackPower = 372,
    nNeHit = 14,
    nMagicDefence = 35,
    nLunarCritical = 50,
    DecriticalDamagePowerBase = 44
  },
  {
    nMP = 1101,
    nSpunkAttackPower = 564,
    nNeHit = 22,
    nMagicDefence = 54,
    nLunarCritical = 76,
    DecriticalDamagePowerBase = 70
  },
  {
    nMP = 1994,
    nSpunkAttackPower = 754,
    nNeHit = 31,
    nMagicDefence = 73,
    nLunarCritical = 102,
    DecriticalDamagePowerBase = 95
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
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
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L1_1].nMP / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMP / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L1_1].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LUNAR_CRITICAL_STRIKE, tSkillData[L1_1].nLunarCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L1_1].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_ATTACK_POWER_COF, 737, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_CRITICAL_STRIKE_COF, 31, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[101124], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_ENERGY, tSkillKungfuConst.LOGIC.QI[101124].MAX, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.QI_ENERGY_REPLENISH, tSkillKungfuConst.LOGIC.QI[101124].REPLENISH, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  AdditionalAttribute(A0_0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/长歌/移动端_莫问_心法.lua", 0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMount() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.AddSkillRecipe(16928, 1)
  A1_5.AddSkillRecipe(16929, 1)
  A1_5.AddSkillRecipe(16930, 1)
  A1_5.AddSkillRecipe(16931, 1)
  A1_5.AddSkillRecipe(16932, 1)
  A1_5.AddSkillRecipe(16933, 1)
  A1_5.AddSkillRecipe(16934, 1)
  A1_5.AddSkillRecipe(16935, 1)
  A1_5.AddSkillRecipe(16936, 1)
  A1_5.AddSkillRecipe(16937, 1)
  A1_5.AddSkillRecipe(16938, 1)
  A1_5.AddSkillRecipe(16939, 1)
  A1_5.AddSkillRecipe(16940, 1)
  A1_5.AddSkillRecipe(16941, 1)
  A1_5.AddSkillRecipe(16942, 1)
  A1_5.AddSkillRecipe(16943, 1)
  A1_5.AddSkillRecipe(16944, 1)
  A1_5.AddSkillRecipe(16945, 1)
  A1_5.AddSkillRecipe(16946, 1)
  A1_5.AddSkillRecipe(16947, 1)
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  GetPlayer(A0_6).LearnSkillLevel(102688, 1, false)
  GetPlayer(A0_6).LearnSkillLevel(102693, 1, false)
  GetPlayer(A0_6).LearnSkillLevel(102686, 1, false)
  if GetPlayer(A0_6).GetBuff(9319, 1) then
    GetPlayer(A0_6).DelBuff(9319, 1)
  end
  if GetPlayer(A0_6).GetBuff(9320, 1) then
    GetPlayer(A0_6).DelBuff(9320, 1)
  end
  if GetPlayer(A0_6).GetBuff(9321, 1) then
    GetPlayer(A0_6).DelBuff(9321, 1)
  end
  if GetPlayer(A0_6).GetBuff(9322, 1) then
    GetPlayer(A0_6).DelBuff(9322, 1)
  end
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
  GetPlayer(A0_6).bSurplusAutoCast = false
  GetPlayer(A0_6).bSurplusAutoReplenish = false
  if GetPlayer(A0_6).GetBuff(9377, 0) then
    GetPlayer(A0_6).DelBuffByID(9377)
  end
  if GetPlayer(A0_6).GetBuff(9506, 1) then
    GetPlayer(A0_6).DelBuff(9506, 1)
  end
end
function UnApply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
end
function OnTimer(A0_8, A1_9, A2_10)
end
