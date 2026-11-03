Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nManaAdd = 515,
    nLunarAPAdd = 304,
    nDodge = 6,
    nLunarHit = 6,
    nMagicDefence = 17
  },
  {
    DecriticalDamagePowerBase = 44,
    nManaAdd = 720,
    nLunarAPAdd = 421,
    nDodge = 10,
    nLunarHit = 10,
    nMagicDefence = 25
  },
  {
    DecriticalDamagePowerBase = 70,
    nManaAdd = 1093,
    nLunarAPAdd = 640,
    nDodge = 17,
    nLunarHit = 17,
    nMagicDefence = 38
  },
  {
    DecriticalDamagePowerBase = 95,
    nManaAdd = 1980,
    nLunarAPAdd = 855,
    nDodge = 23,
    nLunarHit = 23,
    nMagicDefence = 51
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
  },
  {
    DecriticalDamagePowerBase = 120,
    nManaAdd = 5940,
    nLunarAPAdd = 2586,
    nDodge = 29,
    nLunarHit = 29,
    nMagicDefence = 153
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
tSkillnPhysicsShielddata = {
  {nPhysicsShield = 14},
  {nPhysicsShield = 19},
  {nPhysicsShield = 29},
  {nPhysicsShield = 40},
  {nPhysicsShield = 120},
  {nPhysicsShield = 120},
  {nPhysicsShield = 120},
  {nPhysicsShield = 120},
  {nPhysicsShield = 120},
  {nPhysicsShield = 120},
  {nPhysicsShield = 120},
  {nPhysicsShield = 120},
  {nPhysicsShield = 120},
  {nPhysicsShield = 120}
}
function GetSkillLevelData(A0_0)
  local L1_1, L2_2
  L1_1 = false
  L2_2 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_ACCUMULATE_VALUE, -5, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  if L2_2 >= 1 and L2_2 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L2_2 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/七秀/七秀_内功_冰心诀.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10081], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 680, 2)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 681, 2)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillnPhysicsShielddata[L2_2].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L2_2].nManaAdd / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L2_2].nManaAdd / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_ATTACK_POWER_COF, 748, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_CRITICAL_STRIKE_COF, 20, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LUNAR_ATTACK_POWER_BASE, tSkillData[L2_2].nLunarAPAdd, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_3, A1_4)
  return A1_4
end
function CanLearnSkill(A0_5, A1_6)
  local L2_7
  L2_7 = true
  return L2_7
end
function OnSkillLevelUp(A0_8, A1_9)
  local L2_10, L3_11
  L2_10 = A1_9.GetKungfuMount
  L2_10 = L2_10()
  if not L2_10 then
    L3_11 = A1_9.MountKungfu
    L3_11(A0_8.dwSkillID, A0_8.dwLevel)
  end
  L3_11 = A0_8.dwLevel
  if A1_9.dwForceID == 5 and A1_9.GetSkillLevel(10200) < 1 then
    A1_9.LearnSkill(10200)
  end
  A1_9.LearnSkillLevel(542, L3_11, A1_9.dwID)
  A1_9.LearnSkill(560)
end
function Apply(A0_12)
  if GetPlayer(A0_12) then
    GetPlayer(A0_12).AddBuff(GetPlayer(A0_12).dwID, GetPlayer(A0_12).nLevel, 6176, 1)
    GetPlayer(A0_12).AddBuff(GetPlayer(A0_12).dwID, GetPlayer(A0_12).nLevel, 14275, 1)
  end
  GetPlayer(A0_12).bSurplusAutoCast = false
  GetPlayer(A0_12).bSurplusAutoReplenish = false
  GetPlayer(A0_12).LearnSkillLevel(32635, 1, GetPlayer(A0_12).dwID)
  GetPlayer(A0_12).LearnSkillLevel(33104, 1, GetPlayer(A0_12).dwID)
end
function UnApply(A0_13)
  if GetPlayer(A0_13) then
    GetPlayer(A0_13).DelBuff(6176, 1)
    GetPlayer(A0_13).DelBuff(9768, 1)
  end
end
function OnTimer(A0_14, A1_15, A2_16)
end
