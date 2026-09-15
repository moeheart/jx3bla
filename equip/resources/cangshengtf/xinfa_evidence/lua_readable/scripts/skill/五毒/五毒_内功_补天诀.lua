Include("scripts/Include/Skill.lh")
Include("scripts/skill/装备/治疗全能属性转治疗量.lua")
Include("scripts/skill/include/kungfuConst.lh")
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.THERAPY, 0)
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 688, 3)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 489, 0)
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2941, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/五毒/五毒_内功_补天诀.lua", 0)
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
  if A1_7.dwForceID == 6 and A1_7.GetSkillLevel(10210) < 1 then
    A1_7.LearnSkill(10210)
  end
  A1_7.LearnSkillLevel(2244, L3_9, A1_7.dwID)
  A1_7.LearnSkill(2245)
end
function Apply(A0_10)
  local L1_11
  L1_11 = GetPlayer
  L1_11 = L1_11(A0_10)
  if not L1_11 then
    return
  end
  if not L1_11.GetScene() then
    return
  end
  if GetNpc(L1_11.dwPetID) then
    L1_11.GetScene().DestroyNpc(GetNpc(L1_11.dwPetID).dwID)
  end
  L1_11.DelGroupBuff(70929, 1)
  if L1_11.IsSkillRecipeExist(1481, 2) then
    L1_11.DelSkillRecipe(1481, 2)
  end
  L1_11.AddBuff(L1_11.dwID, L1_11.nLevel, 14275, 1)
  PVXTherapyAllRound2TherapyPowerBase(L1_11)
  if L1_11.GetSkillLevel(44354) == 0 then
    L1_11.LearnSkillLevel(44354, 1, L1_11.dwID)
  end
  RemoteCallToClient(L1_11.dwID, "OnActionBarSkillReplace", 18584, 44354, 1)
end
function UnApply(A0_12)
  if not GetPlayer(A0_12) then
    return
  end
  if not GetPlayer(A0_12).GetScene() then
    return
  end
  GetPlayer(A0_12).DelGroupBuff(2844, 1)
  if GetNpc(GetPlayer(A0_12).dwPetID) then
    GetPlayer(A0_12).GetScene().DestroyNpc(GetNpc(GetPlayer(A0_12).dwPetID).dwID)
    GetPlayer(A0_12).DelBuff(25994, 1)
  end
end
function OnTimer(A0_13, A1_14, A2_15)
end
