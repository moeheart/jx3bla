Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nSpunkAttackPower = 298,
    nNeHit = 6,
    nLifeReplenish = 15,
    nMagicDefence = 13
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nSpunkAttackPower = 413,
    nNeHit = 10,
    nLifeReplenish = 21,
    nMagicDefence = 18
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nSpunkAttackPower = 627,
    nNeHit = 17,
    nLifeReplenish = 32,
    nMagicDefence = 27
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nSpunkAttackPower = 838,
    nNeHit = 23,
    nLifeReplenish = 43,
    nMagicDefence = 37
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nSpunkAttackPower = 298,
    nNeHit = 6,
    nLifeReplenish = 15,
    nMagicDefence = 13
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nSpunkAttackPower = 413,
    nNeHit = 10,
    nLifeReplenish = 21,
    nMagicDefence = 18
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nSpunkAttackPower = 627,
    nNeHit = 17,
    nLifeReplenish = 32,
    nMagicDefence = 27
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nSpunkAttackPower = 838,
    nNeHit = 23,
    nLifeReplenish = 43,
    nMagicDefence = 37
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/万花/万花_内功_花间游.lua", 0)
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_NEUTRAL_ATTACK_POWER_COF, 686, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_NEUTRAL_OVERCOME_COF, 82, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10021], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LIFE_REPLENISH_EXT, tSkillData[L2_2].nLifeReplenish, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 100, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.NEUTRAL_MAGIC, SKILL_KIND_TYPE.NEUTRAL_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2941, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 60, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_ENERGY, 9, 0)
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
  A1_10.LearnSkillLevel(487, L3_12, A1_10.dwID)
  A1_10.LearnSkill(491)
end
function Apply(A0_13)
  if GetPlayer(A0_13) then
    GetPlayer(A0_13).AddBuff(GetPlayer(A0_13).dwID, GetPlayer(A0_13).nLevel, 14275, 1)
    GetPlayer(A0_13).bSurplusAutoCast = false
    GetPlayer(A0_13).bSurplusAutoReplenish = false
    if not GetPlayer(A0_13).IsHaveBuff(24277, 1) then
      GetPlayer(A0_13).AddBuff(GetPlayer(A0_13).dwID, GetPlayer(A0_13).nLevel, 24277, 1)
    end
    if GetPlayer(A0_13).GetSkillLevel(33285) == 0 then
      GetPlayer(A0_13).LearnSkillLevel(33285, 7, true)
    end
  end
end
function UnApply(A0_14)
  if GetPlayer(A0_14) then
    GetPlayer(A0_14).DelBuffByID(24277)
    GetPlayer(A0_14).DelBuffByID(24281)
  end
end
function OnTimer(A0_15, A1_16, A2_17)
end
