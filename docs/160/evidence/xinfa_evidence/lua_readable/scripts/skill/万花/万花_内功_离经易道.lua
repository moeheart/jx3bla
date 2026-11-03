Include("scripts/Include/Skill.lh")
Include("scripts/skill/装备/治疗全能属性转治疗量.lua")
Include("scripts/skill/include/kungfuConst.lh")
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.THERAPY, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/万花/万花_内功_离经易道.lua", 0)
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_THERAPY_POWER_COF, 686, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_NEUTRAL_CRITICAL_STRIKE_COF, 82, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.THERAPY_POWER_BASE, tSkillData[L2_2].nTherapyPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LIFE_REPLENISH_EXT, tSkillData[L2_2].nLifeReplenish, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 100, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 152 + math.min(7, L2_2), 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.NEUTRAL_MAGIC, SKILL_KIND_TYPE.NEUTRAL_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 60, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_SUN_ENERGY, 5, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MOON_ENERGY, 5, 0)
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
  local L2_11, L3_12
  L2_11 = A1_10.GetKungfuMountID
  L2_11 = L2_11()
  if not L2_11 then
    L3_12 = A1_10.MountKungfu
    L3_12(A0_9.dwSkillID, A0_9.dwLevel)
  end
  L3_12 = A0_9.dwLevel
  if A1_10.dwForceID == 2 and A1_10.GetSkillLevel(10198) < 1 then
    A1_10.LearnSkill(10198)
  end
  A1_10.LearnSkillLevel(492, L3_12, A1_10.dwID)
  A1_10.LearnSkill(493)
end
function Apply(A0_13)
  local L1_14, L2_15
  L1_14 = GetPlayer
  L2_15 = A0_13
  L1_14 = L1_14(L2_15)
  if L1_14 then
    L2_15 = L1_14.AddBuff
    L2_15(L1_14.dwID, L1_14.nLevel, 14275, 1)
    L2_15 = PVXTherapyAllRound2TherapyPowerBase
    L2_15(L1_14)
    L2_15 = L1_14.IsHaveBuff
    L2_15 = L2_15(24277, 1)
    if not L2_15 then
      L2_15 = L1_14.AddBuff
      L2_15(L1_14.dwID, L1_14.nLevel, 24277, 1)
    end
    L2_15 = L1_14.GetSkillLevel
    L2_15 = L2_15(32374)
    if L2_15 == 0 then
      L2_15 = L1_14.LearnSkillLevel
      L2_15(32374, 1, true)
    end
    L2_15 = L1_14.GetSkillLevel
    L2_15 = L2_15(36095)
    if L2_15 == 1 then
      L2_15 = L1_14.GetSkillLevel
      L2_15 = L2_15(140)
      L1_14.LearnSkillLevel(36125, L2_15, true)
    end
  end
end
function UnApply(A0_16)
  if GetPlayer(A0_16) then
    GetPlayer(A0_16).DelBuffByID(24277)
    GetPlayer(A0_16).DelBuffByID(24281)
  end
end
function OnTimer(A0_17, A1_18, A2_19)
end
