Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 523,
    nPhysicsAttackPower = 813,
    nPhysicsShield = 17,
    nPhysicsCri = 0,
    nPhysicsHit = 6
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 731,
    nPhysicsAttackPower = 913,
    nPhysicsShield = 24,
    nPhysicsCri = 0,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1109,
    nPhysicsAttackPower = 1113,
    nPhysicsShield = 37,
    nPhysicsCri = 0,
    nPhysicsHit = 16
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2010,
    nPhysicsAttackPower = 1313,
    nPhysicsShield = 49,
    nPhysicsCri = 0,
    nPhysicsHit = 21
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 523,
    nPhysicsAttackPower = 313,
    nPhysicsShield = 17,
    nPhysicsCri = 0,
    nPhysicsHit = 6
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 731,
    nPhysicsAttackPower = 434,
    nPhysicsShield = 24,
    nPhysicsCri = 0,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1109,
    nPhysicsAttackPower = 658,
    nPhysicsShield = 37,
    nPhysicsCri = 0,
    nPhysicsHit = 16
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2010,
    nPhysicsAttackPower = 880,
    nPhysicsShield = 49,
    nPhysicsCri = 0,
    nPhysicsHit = 21
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  }
}
tSkillEventData = {
  {nLevel = 1, nEventID = 118},
  {nLevel = 2, nEventID = 118},
  {nLevel = 3, nEventID = 118},
  {nLevel = 4, nEventID = 145},
  {nLevel = 5, nEventID = 146},
  {nLevel = 6, nEventID = 147},
  {nLevel = 7, nEventID = 148}
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_ATTACK_POWER_COF, 573, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_OVERCOME_COF, 195, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MOVE_SPEED_PERCENT, 105, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L1_1].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L1_1].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1127, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100651], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/丐帮/移动端_笑尘诀_心法.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  AdditionalAttribute(A0_0)
  A0_0.nWeaponDamagePercent = 0
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMount() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  if not A1_5.GetKungfuMount() and A1_5.nSkillPlatformType == SKILL_PLATFORM_TYPE.MOBILE then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.AddSkillRecipe(16822, 1)
  A1_5.AddSkillRecipe(16823, 1)
  A1_5.AddSkillRecipe(16824, 1)
  A1_5.AddSkillRecipe(16825, 1)
  A1_5.AddSkillRecipe(16826, 1)
  A1_5.AddSkillRecipe(16827, 1)
  A1_5.AddSkillRecipe(16828, 1)
  A1_5.AddSkillRecipe(16829, 1)
  A1_5.AddSkillRecipe(16830, 1)
  A1_5.AddSkillRecipe(16831, 1)
  A1_5.AddSkillRecipe(16832, 1)
  A1_5.AddSkillRecipe(16833, 1)
  A1_5.AddSkillRecipe(16834, 1)
  A1_5.AddSkillRecipe(16835, 1)
  A1_5.AddSkillRecipe(16836, 1)
  A1_5.AddSkillRecipe(16837, 1)
  A1_5.AddSkillRecipe(16838, 1)
  A1_5.AddSkillRecipe(16839, 1)
  A1_5.AddSkillRecipe(16840, 1)
  A1_5.AddSkillRecipe(16841, 1)
end
function Apply(A0_6)
  if GetPlayer(A0_6) then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
    GetPlayer(A0_6).bSurplusAutoCast = false
    GetPlayer(A0_6).bSurplusAutoReplenish = false
    if GetPlayer(A0_6).GetSkillLevel(102754) == 0 then
      GetPlayer(A0_6).LearnSkillLevel(102754, 1, A0_6)
    end
  end
end
function UnApply(A0_7)
  local L1_8
end
