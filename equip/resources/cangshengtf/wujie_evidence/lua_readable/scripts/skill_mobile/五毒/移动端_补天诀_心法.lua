Include("scripts/Include/Skill.lh")
Include("scripts/skill/装备/治疗全能属性转治疗量.lua")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 515,
    nTherapyPower = 774,
    nLifeReplenish = 25,
    nManaReplenish = 2,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 720,
    nTherapyPower = 1077,
    nLifeReplenish = 35,
    nManaReplenish = 2,
    nMagicDefence = 44
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1093,
    nTherapyPower = 1634,
    nLifeReplenish = 53,
    nManaReplenish = 3,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 1980,
    nTherapyPower = 2191,
    nLifeReplenish = 72,
    nManaReplenish = 4,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 5940,
    nTherapyPower = 6595,
    nLifeReplenish = 216,
    nManaReplenish = 5,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 5940,
    nTherapyPower = 6595,
    nLifeReplenish = 216,
    nManaReplenish = 5,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 5940,
    nTherapyPower = 6595,
    nLifeReplenish = 216,
    nManaReplenish = 5,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 5940,
    nTherapyPower = 6595,
    nLifeReplenish = 216,
    nManaReplenish = 5,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 5940,
    nTherapyPower = 6595,
    nLifeReplenish = 216,
    nManaReplenish = 5,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 5940,
    nTherapyPower = 6595,
    nLifeReplenish = 216,
    nManaReplenish = 5,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 515,
    nTherapyPower = 774,
    nLifeReplenish = 25,
    nManaReplenish = 2,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 720,
    nTherapyPower = 1077,
    nLifeReplenish = 35,
    nManaReplenish = 2,
    nMagicDefence = 44
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1093,
    nTherapyPower = 1634,
    nLifeReplenish = 53,
    nManaReplenish = 3,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 1980,
    nTherapyPower = 2191,
    nLifeReplenish = 72,
    nManaReplenish = 4,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 5940,
    nTherapyPower = 6595,
    nLifeReplenish = 216,
    nManaReplenish = 5,
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.OVERFLOW_THERAPY_INTELLIGENT_TRANSFER, 819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_THERAPY_POWER_COF, 768, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.THERAPY_POWER_BASE, tSkillData[L2_2].nTherapyPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LIFE_REPLENISH_EXT, tSkillData[L2_2].nLifeReplenish, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.POISON, SKILL_KIND_TYPE.POISON)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.THERAPY, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/五毒/移动端_补天诀_心法.lua", 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function OnSkillLevelUp(A0_6, A1_7)
  if not A1_7.GetKungfuMount() then
    A1_7.MountKungfu(A0_6.dwSkillID, A0_6.dwLevel)
  end
  A1_7.AddSkillRecipe(16795, 1)
  A1_7.AddSkillRecipe(16796, 1)
  A1_7.AddSkillRecipe(16797, 1)
  A1_7.AddSkillRecipe(16798, 1)
  A1_7.AddSkillRecipe(16799, 1)
  A1_7.AddSkillRecipe(16800, 1)
  A1_7.AddSkillRecipe(16801, 1)
  A1_7.AddSkillRecipe(16802, 1)
  A1_7.AddSkillRecipe(16803, 1)
  A1_7.AddSkillRecipe(16804, 1)
  A1_7.AddSkillRecipe(16805, 1)
  A1_7.AddSkillRecipe(16806, 1)
  A1_7.AddSkillRecipe(16807, 1)
  A1_7.AddSkillRecipe(16808, 1)
  A1_7.AddSkillRecipe(16809, 1)
  A1_7.AddSkillRecipe(16810, 1)
  A1_7.AddSkillRecipe(16811, 1)
  A1_7.AddSkillRecipe(16812, 1)
  A1_7.AddSkillRecipe(17211, 1)
  A1_7.AddSkillRecipe(17212, 1)
end
function Apply(A0_8)
  local L1_9
  L1_9 = GetPlayer
  L1_9 = L1_9(A0_8)
  if not L1_9 then
    return
  end
  if not L1_9.GetScene() then
    return
  end
  if GetNpc(L1_9.dwPetID) then
    L1_9.GetScene().DestroyNpc(GetNpc(L1_9.dwPetID).dwID)
  end
  if L1_9.GetScene().GetNpcByNickName("GuChong" .. L1_9.dwID) and L1_9 and L1_9.GetScene().IsNickNameNpcExist("GuChong" .. L1_9.dwID) then
    L1_9.GetScene().DestroyNpcByNickName("GuChong" .. L1_9.dwID)
  end
  L1_9.bSurplusAutoCast = false
  L1_9.bSurplusAutoReplenish = false
  PVXTherapyAllRound2TherapyPowerBase(L1_9)
  L1_9.AddBuff(L1_9.dwID, L1_9.nLevel, 14275, 1)
  if L1_9.GetSkillLevel(102561) == 0 then
    L1_9.LearnSkillLevel(102561, 1, L1_9.dwID)
  end
  L1_9.LearnSkillLevel(102671, 1, false)
end
function UnApply(A0_10)
  if not GetPlayer(A0_10) then
    return
  end
  if not GetPlayer(A0_10).GetScene() then
    return
  end
  if GetNpc(GetPlayer(A0_10).dwPetID) then
    GetPlayer(A0_10).GetScene().DestroyNpc(GetNpc(GetPlayer(A0_10).dwPetID).dwID)
  end
end
function OnTimer(A0_11, A1_12, A2_13)
end
