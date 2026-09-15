Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMana = 520,
    nMagicDamage = 298,
    nPhysicDefence = 14,
    nHit = 6,
    nMagicDefence = 17
  },
  {
    DecriticalDamagePowerBase = 44,
    nMana = 726,
    nMagicDamage = 413,
    nPhysicDefence = 20,
    nHit = 10,
    nMagicDefence = 24
  },
  {
    DecriticalDamagePowerBase = 70,
    nMana = 1103,
    nMagicDamage = 627,
    nPhysicDefence = 31,
    nHit = 17,
    nMagicDefence = 36
  },
  {
    DecriticalDamagePowerBase = 95,
    nMana = 1998,
    nMagicDamage = 838,
    nPhysicDefence = 42,
    nHit = 23,
    nMagicDefence = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMana = 5994,
    nMagicDamage = 2535,
    nPhysicDefence = 126,
    nHit = 29,
    nMagicDefence = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMana = 5994,
    nMagicDamage = 2535,
    nPhysicDefence = 126,
    nHit = 29,
    nMagicDefence = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMana = 5994,
    nMagicDamage = 2535,
    nPhysicDefence = 126,
    nHit = 29,
    nMagicDefence = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMana = 5994,
    nMagicDamage = 2535,
    nPhysicDefence = 126,
    nHit = 29,
    nMagicDefence = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMana = 5994,
    nMagicDamage = 2535,
    nPhysicDefence = 126,
    nHit = 29,
    nMagicDefence = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMana = 5994,
    nMagicDamage = 2535,
    nPhysicDefence = 126,
    nHit = 29,
    nMagicDefence = 147
  },
  {
    DecriticalDamagePowerBase = 25,
    nMana = 520,
    nMagicDamage = 298,
    nPhysicDefence = 14,
    nHit = 6,
    nMagicDefence = 17
  },
  {
    DecriticalDamagePowerBase = 44,
    nMana = 726,
    nMagicDamage = 413,
    nPhysicDefence = 20,
    nHit = 10,
    nMagicDefence = 24
  },
  {
    DecriticalDamagePowerBase = 70,
    nMana = 1103,
    nMagicDamage = 627,
    nPhysicDefence = 31,
    nHit = 17,
    nMagicDefence = 36
  },
  {
    DecriticalDamagePowerBase = 95,
    nMana = 1998,
    nMagicDamage = 838,
    nPhysicDefence = 42,
    nHit = 23,
    nMagicDefence = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMana = 5994,
    nMagicDamage = 2535,
    nPhysicDefence = 126,
    nHit = 29,
    nMagicDefence = 147
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10003], 1)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/少林/少林_套路_易筋经.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_SOLAR_ATTACK_POWER_COF, 666, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_SOLAR_CRITICAL_STRIKE_COF, 102, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_LIFE_PERCENT_ADD, 81.92, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nMagicDamage, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L2_2].nPhysicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 86, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.SOLAR_MAGIC, SKILL_KIND_TYPE.SOLAR_MAGIC)
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
  local L2_11, L3_12
  L2_11 = A1_10.GetKungfuMount
  L2_11 = L2_11()
  if not L2_11 then
    L3_12 = A1_10.MountKungfu
    L3_12(A0_9.dwSkillID, A0_9.dwLevel)
  end
  L3_12 = A0_9.dwLevel
  if A1_10.dwForceID == 1 and 1 > A1_10.GetSkillLevel(10196) then
    A1_10.LearnSkill(10196)
  end
  A1_10.LearnSkillLevel(583, L3_12, A1_10.dwID)
  A1_10.LearnSkill(584)
end
function Apply(A0_13)
  if not GetPlayer(A0_13) then
    return
  end
  GetPlayer(A0_13).LearnSkillLevel(5913, 1, GetPlayer(A0_13).dwID)
  GetPlayer(A0_13).AddBuff(A0_13, GetPlayer(A0_13).nLevel, 6193, 1, 1)
  GetPlayer(A0_13).AddBuff(GetPlayer(A0_13).dwID, GetPlayer(A0_13).nLevel, 14275, 1)
  GetPlayer(A0_13).bSurplusAutoCast = false
  GetPlayer(A0_13).bSurplusAutoReplenish = false
end
function UnApply(A0_14)
  if not GetPlayer(A0_14) then
    return
  end
  GetPlayer(A0_14).ForgetSkill(5913)
  GetPlayer(A0_14).ForgetSkill(45935)
  GetPlayer(A0_14).DelBuff(6193, 1)
  GetPlayer(A0_14).DelMultiGroupBuffByID(10023)
  GetPlayer(A0_14).DelMultiGroupBuffByID(10024)
end
function OnTimer(A0_15, A1_16, A2_17)
end
