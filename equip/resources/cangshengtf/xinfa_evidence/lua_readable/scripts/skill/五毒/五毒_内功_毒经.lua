Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 523,
    nSpunkAttackPower = 298,
    nNeHit = 9,
    nManaReplenish = 0,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 731,
    nSpunkAttackPower = 413,
    nNeHit = 16,
    nManaReplenish = 0,
    nMagicDefence = 45
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1109,
    nSpunkAttackPower = 627,
    nNeHit = 25,
    nManaReplenish = 0,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2010,
    nSpunkAttackPower = 838,
    nNeHit = 35,
    nManaReplenish = 0,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 523,
    nSpunkAttackPower = 298,
    nNeHit = 9,
    nManaReplenish = 0,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 731,
    nSpunkAttackPower = 413,
    nNeHit = 16,
    nManaReplenish = 0,
    nMagicDefence = 45
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1109,
    nSpunkAttackPower = 627,
    nNeHit = 25,
    nManaReplenish = 0,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2010,
    nSpunkAttackPower = 838,
    nNeHit = 35,
    nManaReplenish = 0,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10175], 1)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 688, 3)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 489, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_POISON_ATTACK_POWER_COF, 748, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_POISON_OVERCOME_COF, 20, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MOON_ENERGY, 31, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STOP_MAKE_MOON_POWER, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.POISON, SKILL_KIND_TYPE.POISON)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2016, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2941, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/五毒/五毒_内功_毒经.lua", 0)
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
  A1_7.LearnSkillLevel(2236, L3_9, A1_7.dwID)
  A1_7.LearnSkill(2237)
end
function Apply(A0_10)
  if not GetPlayer(A0_10) then
    return
  end
  if not GetPlayer(A0_10).GetScene() then
    return
  end
  if GetNpc(GetPlayer(A0_10).dwPetID) then
    GetPlayer(A0_10).GetScene().DestroyNpc(GetNpc(GetPlayer(A0_10).dwPetID).dwID)
  end
  GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 14275, 1)
  GetPlayer(A0_10).bSurplusAutoCast = false
  GetPlayer(A0_10).bSurplusAutoReplenish = false
  if GetPlayer(A0_10).nLevel >= 10 and GetPlayer(A0_10).GetSkillLevel(42288) == 0 then
    GetPlayer(A0_10).LearnSkillLevel(42288, 1, GetPlayer(A0_10).dwID)
  end
  if not GetPlayer(A0_10).IsHaveBuff(32385, 1) then
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 32385, 1)
  end
  if GetPlayer(A0_10).GetSkillLevel(18584) == 0 then
    GetPlayer(A0_10).LearnSkillLevel(18584, 1, GetPlayer(A0_10).dwID)
  end
  RemoteCallToClient(GetPlayer(A0_10).dwID, "OnActionBarSkillReplace", 44354, 18584, 1)
end
function UnApply(A0_11)
  if not GetPlayer(A0_11) then
    return
  end
  if not GetPlayer(A0_11).GetScene() then
    return
  end
  if GetNpc(GetPlayer(A0_11).dwPetID) then
    GetPlayer(A0_11).GetScene().DestroyNpc(GetNpc(GetPlayer(A0_11).dwPetID).dwID)
  end
  GetPlayer(A0_11).DelBuffByID(32385)
end
function OnTimer(A0_12, A1_13, A2_14)
end
