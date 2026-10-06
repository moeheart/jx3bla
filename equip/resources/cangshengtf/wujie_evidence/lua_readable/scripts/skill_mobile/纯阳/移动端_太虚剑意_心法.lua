Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nPhysicsAttackPower = 783,
    nPhysicsHit = 11,
    nPhysicsCritical = 47
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nPhysicsAttackPower = 883,
    nPhysicsHit = 20,
    nPhysicsCritical = 65
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nPhysicsAttackPower = 1083,
    nPhysicsHit = 31,
    nPhysicsCritical = 99
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nPhysicsAttackPower = 1283,
    nPhysicsHit = 42,
    nPhysicsCritical = 133
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nPhysicsAttackPower = 283,
    nPhysicsHit = 11,
    nPhysicsCritical = 47
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nPhysicsAttackPower = 392,
    nPhysicsHit = 20,
    nPhysicsCritical = 65
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nPhysicsAttackPower = 596,
    nPhysicsHit = 31,
    nPhysicsCritical = 99
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nPhysicsAttackPower = 796,
    nPhysicsHit = 42,
    nPhysicsCritical = 133
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
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
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_ATTACK_POWER_COF, 727, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_CRITICAL_STRIKE_COF, 41, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L2_2].nPhysicsCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L2_2].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100389], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/纯阳/移动端_太虚剑意_心法.lua", 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function OnSkillLevelUp(A0_6, A1_7)
  if not A1_7.GetKungfuMount() then
    A1_7.MountKungfu(A0_6.dwSkillID, A0_6.dwLevel)
  end
  A1_7.AddSkillRecipe(16502, 1)
  A1_7.AddSkillRecipe(16503, 1)
  A1_7.AddSkillRecipe(16573, 1)
  A1_7.AddSkillRecipe(16574, 1)
  A1_7.AddSkillRecipe(16575, 1)
  A1_7.AddSkillRecipe(16576, 1)
  A1_7.AddSkillRecipe(16577, 1)
  A1_7.AddSkillRecipe(16578, 1)
  A1_7.AddSkillRecipe(16579, 1)
  A1_7.AddSkillRecipe(16580, 1)
  A1_7.AddSkillRecipe(16581, 1)
  A1_7.AddSkillRecipe(16582, 1)
  A1_7.AddSkillRecipe(16583, 1)
  A1_7.AddSkillRecipe(16584, 1)
  A1_7.AddSkillRecipe(16585, 1)
  A1_7.AddSkillRecipe(16586, 1)
  A1_7.AddSkillRecipe(16587, 1)
  A1_7.AddSkillRecipe(16588, 1)
  A1_7.AddSkillRecipe(16590, 1)
  A1_7.AddSkillRecipe(16592, 1)
end
function Apply(A0_8)
  if GetPlayer(A0_8) then
    GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 14275, 1)
    GetPlayer(A0_8).bSurplusAutoCast = false
    GetPlayer(A0_8).bSurplusAutoReplenish = false
    if GetPlayer(A0_8).GetSkillLevel(102712) == 0 then
      GetPlayer(A0_8).LearnSkillLevel(102712, 1, A0_8)
    end
    if GetPlayer(A0_8).GetSkillLevel(102755) == 0 then
      GetPlayer(A0_8).LearnSkillLevel(102755, 1, A0_8)
    end
  end
end
function UnApply(A0_9)
  local L1_10
end
function OnTimer(A0_11, A1_12, A2_13)
end
