Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10144], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2941, 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 4087, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_ATTACK_POWER_COF, 717, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_OVERCOME_COF, 51, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_USE_BIG_SWORD_FLAG, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 279, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 334, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.RAGE_REPLENISH, -2, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_ADDITIONAL, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L1_1].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L1_1].nPhysicsCri, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_PERCENT, 1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2201, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 363, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 663, 1)
  AdditionalAttribute(A0_0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/藏剑/藏剑_套路_内功_问水诀.lua", 0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  local L2_6, L3_7
  L2_6 = A1_5.GetKungfuMountID
  L2_6 = L2_6()
  if not L2_6 then
    L3_7 = A1_5.MountKungfu
    L3_7(A0_4.dwSkillID, A0_4.dwLevel)
  end
  L3_7 = A0_4.dwLevel
  if A1_5.dwForceID == 8 and A1_5.GetSkillLevel(10201) < 1 then
    A1_5.LearnSkill(10201)
  end
  A1_5.LearnSkillLevel(1720, L3_7, A1_5.dwID)
  A1_5.LearnSkill(1721)
end
function Apply(A0_8)
  if not GetPlayer(A0_8) then
    return
  end
  GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 14275, 1)
  if GetPlayer(A0_8).GetSkillLevel(6799) == 1 and not GetPlayer(A0_8).GetBuff(9900, 1) then
    GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 9900, 1)
  end
  GetPlayer(A0_8).bSurplusAutoCast = false
  GetPlayer(A0_8).bSurplusAutoReplenish = false
end
function UnApply(A0_9)
  if not GetPlayer(A0_9) then
    return
  end
  if GetPlayer(A0_9).GetBuff(9900, 1) then
    GetPlayer(A0_9).DelBuff(9900, 1)
  end
end
