Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
Include("scripts/skill/装备/治疗全能属性转治疗量.lua")
tSkillData = {
  {
    nMaxMana = 518,
    nTherapy = 828,
    nLifeReplenish = 22,
    nMagicDefence = 32,
    DecriticalDamagePowerBase = 25
  },
  {
    nMaxMana = 723,
    nTherapy = 1152,
    nLifeReplenish = 31,
    nMagicDefence = 44,
    DecriticalDamagePowerBase = 44
  },
  {
    nMaxMana = 1098,
    nTherapy = 1747,
    nLifeReplenish = 48,
    nMagicDefence = 68,
    DecriticalDamagePowerBase = 70
  },
  {
    nMaxMana = 1990,
    nTherapy = 2342,
    nLifeReplenish = 65,
    nMagicDefence = 91,
    DecriticalDamagePowerBase = 95
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 518,
    nTherapy = 828,
    nLifeReplenish = 22,
    nMagicDefence = 32,
    DecriticalDamagePowerBase = 25
  },
  {
    nMaxMana = 723,
    nTherapy = 1152,
    nLifeReplenish = 31,
    nMagicDefence = 44,
    DecriticalDamagePowerBase = 44
  },
  {
    nMaxMana = 1098,
    nTherapy = 1747,
    nLifeReplenish = 48,
    nMagicDefence = 68,
    DecriticalDamagePowerBase = 70
  },
  {
    nMaxMana = 1990,
    nTherapy = 2342,
    nLifeReplenish = 65,
    nMagicDefence = 91,
    DecriticalDamagePowerBase = 95
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.OVERFLOW_THERAPY_INTELLIGENT_TRANSFER, 819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  AdditionalAttribute(A0_0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L1_1].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.THERAPY_POWER_BASE, tSkillData[L1_1].nTherapy, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L1_1].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LIFE_REPLENISH_EXT, tSkillData[L1_1].nLifeReplenish, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_THERAPY_POWER_COF, 707, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_CRITICAL_STRIKE_COF, 61, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_ENERGY, tSkillKungfuConst.LOGIC.QI[101125].MAX, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.QI_ENERGY_REPLENISH, tSkillKungfuConst.LOGIC.QI[101125].REPLENISH, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.THERAPY, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/长歌/移动端_相知_心法.lua", 0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMount() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.AddSkillRecipe(16948, 1)
  A1_5.AddSkillRecipe(16949, 1)
  A1_5.AddSkillRecipe(16950, 1)
  A1_5.AddSkillRecipe(16951, 1)
  A1_5.AddSkillRecipe(16952, 1)
  A1_5.AddSkillRecipe(16953, 1)
  A1_5.AddSkillRecipe(16954, 1)
  A1_5.AddSkillRecipe(16955, 1)
  A1_5.AddSkillRecipe(16956, 1)
  A1_5.AddSkillRecipe(16957, 1)
  A1_5.AddSkillRecipe(16958, 1)
  A1_5.AddSkillRecipe(16959, 1)
  A1_5.AddSkillRecipe(16960, 1)
  A1_5.AddSkillRecipe(16961, 1)
  A1_5.AddSkillRecipe(16962, 1)
  A1_5.AddSkillRecipe(16963, 1)
  A1_5.AddSkillRecipe(17255, 1)
  A1_5.AddSkillRecipe(17256, 1)
  A1_5.AddSkillRecipe(17257, 1)
  A1_5.AddSkillRecipe(17258, 1)
end
function Apply(A0_6)
  local L1_7
  L1_7 = GetPlayer
  L1_7 = L1_7(A0_6)
  if not L1_7 then
    return
  end
  L1_7.LearnSkillLevel(102681, 1, false)
  if L1_7.GetBuff(9319, 1) then
    L1_7.DelBuff(9319, 1)
  end
  if L1_7.GetBuff(9320, 1) then
    L1_7.DelBuff(9320, 1)
  end
  if L1_7.GetBuff(9321, 1) then
    L1_7.DelBuff(9321, 1)
  end
  if L1_7.GetBuff(9322, 1) then
    L1_7.DelBuff(9322, 1)
  end
  PVXTherapyAllRound2TherapyPowerBase(L1_7)
  L1_7.bSurplusAutoCast = false
  L1_7.bSurplusAutoReplenish = false
  L1_7.AddBuff(L1_7.dwID, L1_7.nLevel, 14275, 1)
  if L1_7.GetBuff(9377, 0) then
    L1_7.DelBuffByID(9377)
  end
  if L1_7.GetBuff(9506, 1) then
    L1_7.DelBuff(9506, 1)
  end
end
function UnApply(A0_8)
  if not GetPlayer(A0_8) then
    return
  end
  if GetPlayer(A0_8).GetBuff(9641, 1) then
    GetPlayer(A0_8).DelBuff(9641, 1)
  end
  if GetPlayer(A0_8).dwShapeShiftID == 0 then
    GetPlayer(A0_8).DelBuff(9320, 1)
  end
end
function OnTimer(A0_9, A1_10, A2_11)
end
