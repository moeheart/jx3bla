Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nManaAdd = 515,
    nLunarAPAdd = 804,
    nDodge = 6,
    nLunarHit = 6,
    nMagicDefence = 17
  },
  {
    DecriticalDamagePowerBase = 44,
    nManaAdd = 720,
    nLunarAPAdd = 904,
    nDodge = 10,
    nLunarHit = 10,
    nMagicDefence = 25
  },
  {
    DecriticalDamagePowerBase = 70,
    nManaAdd = 1093,
    nLunarAPAdd = 1104,
    nDodge = 17,
    nLunarHit = 17,
    nMagicDefence = 38
  },
  {
    DecriticalDamagePowerBase = 95,
    nManaAdd = 1980,
    nLunarAPAdd = 1304,
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  if L2_2 >= 1 and L2_2 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L2_2 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/七秀/移动端_心法_冰心诀.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100410], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L2_2].nManaAdd / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L2_2].nManaAdd / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillnPhysicsShielddata[L2_2].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_ATTACK_POWER_COF, 748, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_CRITICAL_STRIKE_COF, 20, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LUNAR_ATTACK_POWER_BASE, tSkillData[L2_2].nLunarAPAdd, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
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
  if not A1_9.GetKungfuMount() then
    A1_9.MountKungfu(A0_8.dwSkillID, A0_8.dwLevel)
  end
  A1_9.AddSkillRecipe(16707, 1)
  A1_9.AddSkillRecipe(16708, 1)
  A1_9.AddSkillRecipe(16709, 1)
  A1_9.AddSkillRecipe(16710, 1)
  A1_9.AddSkillRecipe(16711, 1)
  A1_9.AddSkillRecipe(16712, 1)
  A1_9.AddSkillRecipe(16713, 1)
  A1_9.AddSkillRecipe(16714, 1)
  A1_9.AddSkillRecipe(16715, 1)
  A1_9.AddSkillRecipe(16716, 1)
  A1_9.AddSkillRecipe(16717, 1)
  A1_9.AddSkillRecipe(16718, 1)
  A1_9.AddSkillRecipe(16719, 1)
  A1_9.AddSkillRecipe(16720, 1)
  A1_9.AddSkillRecipe(16721, 1)
  A1_9.AddSkillRecipe(16722, 1)
  A1_9.AddSkillRecipe(16723, 1)
  A1_9.AddSkillRecipe(16724, 1)
  A1_9.AddSkillRecipe(16725, 1)
  A1_9.AddSkillRecipe(16726, 1)
  A1_9.AddSkillRecipe(17631, 1)
  A1_9.AddSkillRecipe(17632, 1)
end
function Apply(A0_10)
  if GetPlayer(A0_10) then
    GetPlayer(A0_10).bSurplusAutoCast = false
    GetPlayer(A0_10).bSurplusAutoReplenish = false
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 14275, 1)
  end
  if GetPlayer(A0_10).GetSkillLevel(102742) == 0 then
    GetPlayer(A0_10).LearnSkillLevel(102742, 1, GetPlayer(A0_10).dwID)
  end
end
function UnApply(A0_11)
  local L1_12
end
function OnTimer(A0_13, A1_14, A2_15)
end
