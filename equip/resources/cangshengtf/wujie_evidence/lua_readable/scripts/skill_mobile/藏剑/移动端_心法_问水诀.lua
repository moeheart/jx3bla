Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nPhysicsAttackPower = 798,
    nDodge = 0,
    nPhysicsCri = 32,
    nPhysicsHit = 6
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nPhysicsAttackPower = 898,
    nDodge = 0,
    nPhysicsCri = 45,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nPhysicsAttackPower = 1098,
    nDodge = 0,
    nPhysicsCri = 68,
    nPhysicsHit = 17
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nPhysicsAttackPower = 1298,
    nDodge = 0,
    nPhysicsCri = 91,
    nPhysicsHit = 23
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2535,
    nDodge = 0,
    nPhysicsCri = 274,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2535,
    nDodge = 0,
    nPhysicsCri = 274,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2535,
    nDodge = 0,
    nPhysicsCri = 274,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2535,
    nDodge = 0,
    nPhysicsCri = 274,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2535,
    nDodge = 0,
    nPhysicsCri = 274,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2535,
    nDodge = 0,
    nPhysicsCri = 274,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nPhysicsAttackPower = 298,
    nDodge = 0,
    nPhysicsCri = 32,
    nPhysicsHit = 6
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nPhysicsAttackPower = 413,
    nDodge = 0,
    nPhysicsCri = 45,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nPhysicsAttackPower = 627,
    nDodge = 0,
    nPhysicsCri = 68,
    nPhysicsHit = 17
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nPhysicsAttackPower = 838,
    nDodge = 0,
    nPhysicsCri = 91,
    nPhysicsHit = 23
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2535,
    nDodge = 0,
    nPhysicsCri = 274,
    nPhysicsHit = 29
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100725], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_ATTACK_POWER_COF, 717, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_OVERCOME_COF, 51, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_USE_BIG_SWORD_FLAG, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 9095, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L1_1].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L1_1].nPhysicsCri, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  AdditionalAttribute(A0_0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/藏剑/移动端_心法_问水诀.lua", 0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  A1_5.AddSkillRecipe(16814, 1)
  A1_5.AddSkillRecipe(16819, 1)
  A1_5.AddSkillRecipe(16820, 1)
  A1_5.AddSkillRecipe(16821, 1)
  A1_5.AddSkillRecipe(16843, 1)
  A1_5.AddSkillRecipe(16850, 1)
  A1_5.AddSkillRecipe(16852, 1)
  A1_5.AddSkillRecipe(16859, 1)
  A1_5.AddSkillRecipe(16860, 1)
  A1_5.AddSkillRecipe(16865, 1)
  A1_5.AddSkillRecipe(17196, 1)
  A1_5.AddSkillRecipe(17197, 1)
  A1_5.AddSkillRecipe(17198, 1)
  A1_5.AddSkillRecipe(17199, 1)
  A1_5.AddSkillRecipe(17200, 1)
  A1_5.AddSkillRecipe(17201, 1)
  A1_5.AddSkillRecipe(17202, 1)
  A1_5.AddSkillRecipe(17203, 1)
  A1_5.AddSkillRecipe(16820, 1)
  A1_5.AddSkillRecipe(16821, 1)
  A1_5.AddSkillRecipe(16853, 1)
  A1_5.AddSkillRecipe(16854, 1)
  A1_5.AddSkillRecipe(16855, 1)
  A1_5.AddSkillRecipe(16856, 1)
  A1_5.AddSkillRecipe(16857, 1)
  A1_5.AddSkillRecipe(16858, 1)
  A1_5.AddSkillRecipe(16861, 1)
  A1_5.AddSkillRecipe(16862, 1)
  A1_5.AddSkillRecipe(16863, 1)
  A1_5.AddSkillRecipe(16864, 1)
  A1_5.AddSkillRecipe(17207, 1)
  A1_5.AddSkillRecipe(17208, 1)
  A1_5.AddSkillRecipe(17209, 1)
  A1_5.AddSkillRecipe(17210, 1)
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  if GetPlayer(A0_6) then
    GetPlayer(A0_6).bSurplusAutoCast = false
    GetPlayer(A0_6).bSurplusAutoReplenish = false
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
    if GetPlayer(A0_6).GetSkillLevel(100905) == 0 then
      GetPlayer(A0_6).LearnSkillLevel(100905, 1, false)
    end
  end
end
function UnApply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
end
