Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 525,
    nPhysicsAttackPower = 813,
    nPhysicsHit = 9,
    nPhysicsCritical = 17
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 734,
    nPhysicsAttackPower = 913,
    nPhysicsHit = 16,
    nPhysicsCritical = 24
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1115,
    nPhysicsAttackPower = 1113,
    nPhysicsHit = 25,
    nPhysicsCritical = 37
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2020,
    nPhysicsAttackPower = 1313,
    nPhysicsHit = 35,
    nPhysicsCritical = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6060,
    nPhysicsAttackPower = 2662,
    nPhysicsHit = 44,
    nPhysicsCritical = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6060,
    nPhysicsAttackPower = 2662,
    nPhysicsHit = 44,
    nPhysicsCritical = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6060,
    nPhysicsAttackPower = 2662,
    nPhysicsHit = 44,
    nPhysicsCritical = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6060,
    nPhysicsAttackPower = 2662,
    nPhysicsHit = 44,
    nPhysicsCritical = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6060,
    nPhysicsAttackPower = 2662,
    nPhysicsHit = 44,
    nPhysicsCritical = 147
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6060,
    nPhysicsAttackPower = 2662,
    nPhysicsHit = 44,
    nPhysicsCritical = 147
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 525,
    nPhysicsAttackPower = 313,
    nPhysicsHit = 9,
    nPhysicsCritical = 17
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 734,
    nPhysicsAttackPower = 434,
    nPhysicsHit = 16,
    nPhysicsCritical = 24
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1115,
    nPhysicsAttackPower = 658,
    nPhysicsHit = 25,
    nPhysicsCritical = 37
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2020,
    nPhysicsAttackPower = 880,
    nPhysicsHit = 35,
    nPhysicsCritical = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6060,
    nPhysicsAttackPower = 2662,
    nPhysicsHit = 44,
    nPhysicsCritical = 147
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[101090], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_ATTACK_POWER_COF, 707, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_CRITICAL_STRIKE_COF, 61, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L2_2].nPhysicsCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L2_2].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1558, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/蓬莱/移动端_心法_凌海决.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function OnSkillLevelUp(A0_6, A1_7)
  if not A1_7.GetKungfuMountID() then
    A1_7.MountKungfu(A0_6.dwSkillID, A0_6.dwLevel)
  end
  A1_7.AddSkillRecipe(16907, 1)
  A1_7.AddSkillRecipe(16908, 1)
  A1_7.AddSkillRecipe(16909, 1)
  A1_7.AddSkillRecipe(16910, 1)
  A1_7.AddSkillRecipe(16911, 1)
  A1_7.AddSkillRecipe(16912, 1)
  A1_7.AddSkillRecipe(16913, 1)
  A1_7.AddSkillRecipe(16914, 1)
  A1_7.AddSkillRecipe(16915, 1)
  A1_7.AddSkillRecipe(16916, 1)
  A1_7.AddSkillRecipe(16917, 1)
  A1_7.AddSkillRecipe(16918, 1)
  A1_7.AddSkillRecipe(16919, 1)
  A1_7.AddSkillRecipe(16920, 1)
  A1_7.AddSkillRecipe(16921, 1)
  A1_7.AddSkillRecipe(16922, 1)
  A1_7.AddSkillRecipe(16923, 1)
  A1_7.AddSkillRecipe(16924, 1)
  A1_7.AddSkillRecipe(16925, 1)
  A1_7.AddSkillRecipe(16926, 1)
  A1_7.AddSkillRecipe(17589, 1)
  A1_7.AddSkillRecipe(17590, 1)
  if A1_7.GetSkillLevel(102695) ~= 1 then
    A1_7.LearnSkillLevel(102695, 1, A1_7.dwID)
  end
  if not A1_7.IsHaveBuff(14487, 1) and not A1_7.IsHaveBuff(14490, 1) and not A1_7.IsHaveBuff(14491, 1) and not A1_7.IsHaveBuff(14492, 1) and not A1_7.IsHaveBuff(14493, 1) and not A1_7.IsHaveBuff(14494, 1) then
    A1_7.AddBuff(A1_7.dwID, A1_7.nLevel, 14487, 1)
  end
end
function Apply(A0_8)
  if not GetPlayer(A0_8) then
    return
  end
  GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 14275, 1)
  GetPlayer(A0_8).bSurplusAutoCast = false
  GetPlayer(A0_8).bSurplusAutoReplenish = false
  if GetPlayer(A0_8).GetSkillLevel(102695) ~= 1 then
    GetPlayer(A0_8).LearnSkillLevel(102695, 1, GetPlayer(A0_8).dwID)
  end
end
function UnApply(A0_9)
  if GetPlayer(A0_9) then
  end
end
