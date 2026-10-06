Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nPhysicsAttackPower = 822,
    nPhysicsShield = 8,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nPhysicsAttackPower = 922,
    nPhysicsShield = 12,
    nPhysicsHit = 18
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nPhysicsAttackPower = 1122,
    nPhysicsShield = 18,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nPhysicsAttackPower = 1322,
    nPhysicsShield = 24,
    nPhysicsHit = 39
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nPhysicsAttackPower = 322,
    nPhysicsShield = 8,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nPhysicsAttackPower = 446,
    nPhysicsShield = 12,
    nPhysicsHit = 18
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nPhysicsAttackPower = 677,
    nPhysicsShield = 18,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nPhysicsAttackPower = 905,
    nPhysicsShield = 24,
    nPhysicsHit = 39
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
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
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/霸刀/移动端_北傲决.lua", 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100994], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMP / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_ATTACK_POWER_COF, 553, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_OVERCOME_COF, 215, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L1_1].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L1_1].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMount() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.AddSkillRecipe(16964, 1)
  A1_5.AddSkillRecipe(16965, 1)
  A1_5.AddSkillRecipe(16966, 1)
  A1_5.AddSkillRecipe(16967, 1)
  A1_5.AddSkillRecipe(16968, 1)
  A1_5.AddSkillRecipe(16969, 1)
  A1_5.AddSkillRecipe(16970, 1)
  A1_5.AddSkillRecipe(16971, 1)
  A1_5.AddSkillRecipe(16972, 1)
  A1_5.AddSkillRecipe(16973, 1)
  A1_5.AddSkillRecipe(16974, 1)
  A1_5.AddSkillRecipe(16975, 1)
  A1_5.AddSkillRecipe(16976, 1)
  A1_5.AddSkillRecipe(16977, 1)
  A1_5.AddSkillRecipe(16978, 1)
  A1_5.AddSkillRecipe(16979, 1)
  A1_5.AddSkillRecipe(16980, 1)
  A1_5.AddSkillRecipe(16981, 1)
  A1_5.AddSkillRecipe(16982, 1)
  A1_5.AddSkillRecipe(16983, 1)
  A1_5.AddSkillRecipe(17587, 1)
  A1_5.AddSkillRecipe(17588, 1)
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  GetPlayer(A0_6).bSurplusAutoCast = false
  GetPlayer(A0_6).bSurplusAutoReplenish = false
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 71043, 1)
  if GetPlayer(A0_6).GetSkillLevel(102555) ~= 1 then
    GetPlayer(A0_6).LearnSkillLevel(102555, 1, GetPlayer(A0_6).dwID)
  end
  if GetPlayer(A0_6).GetSkillLevel(102691) ~= 1 then
    GetPlayer(A0_6).LearnSkillLevel(102691, 1, GetPlayer(A0_6).dwID)
  end
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
end
function UnApply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
  GetPlayer(A0_7).DelBuff(71043, 1)
end
function OnTimer(A0_8, A1_9, A2_10)
end
