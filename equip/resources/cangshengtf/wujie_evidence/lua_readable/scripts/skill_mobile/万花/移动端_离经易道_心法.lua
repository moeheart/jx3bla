Include("scripts/Include/Skill.lh")
Include("scripts/skill/装备/治疗全能属性转治疗量.lua")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 536,
    nTherapyPower = 748,
    nLifeReplenish = 30,
    nManaReplenish = 1,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 749,
    nTherapyPower = 1040,
    nLifeReplenish = 42,
    nManaReplenish = 2,
    nMagicDefence = 44
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1137,
    nTherapyPower = 1578,
    nLifeReplenish = 64,
    nManaReplenish = 2,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2060,
    nTherapyPower = 2115,
    nLifeReplenish = 86,
    nManaReplenish = 3,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6180,
    nTherapyPower = 6367,
    nLifeReplenish = 260,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6180,
    nTherapyPower = 6367,
    nLifeReplenish = 260,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6180,
    nTherapyPower = 6367,
    nLifeReplenish = 260,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6180,
    nTherapyPower = 6367,
    nLifeReplenish = 260,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6180,
    nTherapyPower = 6367,
    nLifeReplenish = 260,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6180,
    nTherapyPower = 6367,
    nLifeReplenish = 260,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 536,
    nTherapyPower = 748,
    nLifeReplenish = 30,
    nManaReplenish = 1,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 749,
    nTherapyPower = 1040,
    nLifeReplenish = 42,
    nManaReplenish = 2,
    nMagicDefence = 44
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1137,
    nTherapyPower = 1578,
    nLifeReplenish = 64,
    nManaReplenish = 2,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2060,
    nTherapyPower = 2115,
    nLifeReplenish = 86,
    nManaReplenish = 3,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6180,
    nTherapyPower = 6367,
    nLifeReplenish = 260,
    nManaReplenish = 4,
    nMagicDefence = 273
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/万花/移动端_离经易道_心法.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.OVERFLOW_THERAPY_INTELLIGENT_TRANSFER, 819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_THERAPY_POWER_COF, 686, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_NEUTRAL_CRITICAL_STRIKE_COF, 82, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.THERAPY_POWER_BASE, tSkillData[L2_2].nTherapyPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LIFE_REPLENISH_EXT, tSkillData[L2_2].nLifeReplenish, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.NEUTRAL_MAGIC, SKILL_KIND_TYPE.NEUTRAL_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.THERAPY, 0)
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
  A1_10.AddSkillRecipe(16647, 1)
  A1_10.AddSkillRecipe(16648, 1)
  A1_10.AddSkillRecipe(16649, 1)
  A1_10.AddSkillRecipe(16650, 1)
  A1_10.AddSkillRecipe(16651, 1)
  A1_10.AddSkillRecipe(16652, 1)
  A1_10.AddSkillRecipe(16653, 1)
  A1_10.AddSkillRecipe(16654, 1)
  A1_10.AddSkillRecipe(16655, 1)
  A1_10.AddSkillRecipe(16656, 1)
  A1_10.AddSkillRecipe(16657, 1)
  A1_10.AddSkillRecipe(16658, 1)
  A1_10.AddSkillRecipe(16661, 1)
  A1_10.AddSkillRecipe(16662, 1)
  A1_10.AddSkillRecipe(16663, 1)
  A1_10.AddSkillRecipe(16664, 1)
  A1_10.AddSkillRecipe(16665, 1)
  A1_10.AddSkillRecipe(16666, 1)
  A1_10.AddSkillRecipe(17129, 1)
  A1_10.AddSkillRecipe(17130, 1)
end
function Apply(A0_11)
  local L1_12
  L1_12 = GetPlayer
  L1_12 = L1_12(A0_11)
  if L1_12 then
    L1_12.AddBuff(L1_12.dwID, L1_12.nLevel, 14275, 1)
    L1_12.bSurplusAutoCast = false
    L1_12.bSurplusAutoReplenish = false
    PVXTherapyAllRound2TherapyPowerBase(L1_12)
    L1_12.LearnSkillLevel(102363, 1, false)
    L1_12.LearnSkillLevel(102365, 1, false)
    if L1_12.GetSkillLevel(102722) == 0 then
      L1_12.LearnSkillLevel(102722, 1, A0_11)
    end
    if L1_12.GetSkillLevel(102753) == 0 then
      L1_12.LearnSkillLevel(102753, 1, A0_11)
    end
  end
end
function UnApply(A0_13)
  local L1_14
end
function OnTimer(A0_15, A1_16, A2_17)
end
