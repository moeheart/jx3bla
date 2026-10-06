Include("scripts/Include/Skill.lh")
Include("scripts/skill/装备/治疗全能属性转治疗量.lua")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nDodge = 5,
    nManaAdd = 520,
    nTherapy = 801,
    nManaReplenish = 1,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nDodge = 10,
    nManaAdd = 727,
    nTherapy = 1115,
    nManaReplenish = 2,
    nMagicDefence = 44
  },
  {
    DecriticalDamagePowerBase = 70,
    nDodge = 15,
    nManaAdd = 1104,
    nTherapy = 1691,
    nManaReplenish = 2,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nDodge = 21,
    nManaAdd = 2000,
    nTherapy = 2267,
    nManaReplenish = 3,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nDodge = 27,
    nManaAdd = 6000,
    nTherapy = 6822,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nDodge = 27,
    nManaAdd = 6000,
    nTherapy = 6822,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nDodge = 27,
    nManaAdd = 6000,
    nTherapy = 6822,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nDodge = 27,
    nManaAdd = 6000,
    nTherapy = 6822,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nDodge = 27,
    nManaAdd = 6000,
    nTherapy = 6822,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 120,
    nDodge = 27,
    nManaAdd = 6000,
    nTherapy = 6822,
    nManaReplenish = 4,
    nMagicDefence = 273
  },
  {
    DecriticalDamagePowerBase = 25,
    nDodge = 5,
    nManaAdd = 520,
    nTherapy = 801,
    nManaReplenish = 1,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nDodge = 10,
    nManaAdd = 727,
    nTherapy = 1115,
    nManaReplenish = 2,
    nMagicDefence = 44
  },
  {
    DecriticalDamagePowerBase = 70,
    nDodge = 15,
    nManaAdd = 1104,
    nTherapy = 1691,
    nManaReplenish = 2,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nDodge = 21,
    nManaAdd = 2000,
    nTherapy = 2267,
    nManaReplenish = 3,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nDodge = 27,
    nManaAdd = 6000,
    nTherapy = 6822,
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
tSkillnPhysicsShielddata = {
  {nPhysicsShield = 32},
  {nPhysicsShield = 44},
  {nPhysicsShield = 68},
  {nPhysicsShield = 91},
  {nPhysicsShield = 273},
  {nPhysicsShield = 273},
  {nPhysicsShield = 273},
  {nPhysicsShield = 273},
  {nPhysicsShield = 273},
  {nPhysicsShield = 273},
  {nPhysicsShield = 32},
  {nPhysicsShield = 44},
  {nPhysicsShield = 68},
  {nPhysicsShield = 91},
  {nPhysicsShield = 273}
}
function GetSkillLevelData(A0_0)
  local L1_1, L2_2
  L1_1 = false
  L2_2 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.OVERFLOW_THERAPY_INTELLIGENT_TRANSFER, 819, 0)
  if L2_2 >= 1 and L2_2 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L2_2 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 680, 2)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 681, 2)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L2_2].nManaAdd / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L2_2].nManaAdd / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_THERAPY_POWER_COF, 727, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_CRITICAL_STRIKE_COF, 41, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/七秀/移动端_心法_云裳心经.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.THERAPY, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.THERAPY_POWER_BASE, tSkillData[L2_2].nTherapy, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillnPhysicsShielddata[L2_2].nPhysicsShield, 0)
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
  A1_9.AddSkillRecipe(16512, 1)
  A1_9.AddSkillRecipe(16515, 1)
  A1_9.AddSkillRecipe(16528, 1)
  A1_9.AddSkillRecipe(16529, 1)
  A1_9.AddSkillRecipe(16530, 1)
  A1_9.AddSkillRecipe(16531, 1)
  A1_9.AddSkillRecipe(16532, 1)
  A1_9.AddSkillRecipe(16533, 1)
  A1_9.AddSkillRecipe(16534, 1)
  A1_9.AddSkillRecipe(16535, 1)
  A1_9.AddSkillRecipe(16539, 1)
  A1_9.AddSkillRecipe(16540, 1)
  A1_9.AddSkillRecipe(16553, 1)
  A1_9.AddSkillRecipe(16562, 1)
  A1_9.AddSkillRecipe(16563, 1)
  A1_9.AddSkillRecipe(16564, 1)
  A1_9.AddSkillRecipe(16569, 1)
  A1_9.AddSkillRecipe(16570, 1)
  A1_9.AddSkillRecipe(16589, 1)
  A1_9.AddSkillRecipe(16591, 1)
  A1_9.AddSkillRecipe(17629, 1)
  A1_9.AddSkillRecipe(17630, 1)
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
  L1_11.bSurplusAutoCast = false
  L1_11.bSurplusAutoReplenish = false
  L1_11.AddBuff(L1_11.dwID, L1_11.nLevel, 14275, 1)
  PVXTherapyAllRound2TherapyPowerBase(L1_11)
  if L1_11.GetSkillLevel(100456) == 1 then
    L1_11.ForgetSkill(100456)
    L1_11.ForgetSkill(100445)
    L1_11.LearnSkillLevel(100099, 1, L1_11.dwID)
  end
  RemoteCallToClient(L1_11.dwID, "OnSkillReplace", 100445, 100099, 1)
  if L1_11.GetSkillLevel(102588) == 0 then
    L1_11.LearnSkillLevel(102588, 1, L1_11.dwID)
  end
  if L1_11.GetSkillLevel(102743) == 0 then
    L1_11.LearnSkillLevel(102743, 1, L1_11.dwID)
  end
end
function UnApply(A0_12)
  if GetPlayer(A0_12) then
    GetPlayer(A0_12).DelBuff(6176, 2)
  end
end
function OnTimer(A0_13, A1_14, A2_15)
end
