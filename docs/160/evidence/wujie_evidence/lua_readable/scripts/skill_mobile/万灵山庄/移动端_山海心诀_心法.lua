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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_ATTACK_POWER_COF, 717, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_CRITICAL_STRIKE_COF, 51, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L2_2].nPhysicsCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L2_2].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[101740], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/万灵山庄/移动端_山海心诀_心法.lua", 0)
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
  A1_7.AddSkillRecipe(17279, 1)
  A1_7.AddSkillRecipe(17280, 1)
  A1_7.AddSkillRecipe(17281, 1)
  A1_7.AddSkillRecipe(17282, 1)
  A1_7.AddSkillRecipe(17283, 1)
  A1_7.AddSkillRecipe(17284, 1)
  A1_7.AddSkillRecipe(17285, 1)
  A1_7.AddSkillRecipe(17286, 1)
  A1_7.AddSkillRecipe(17287, 1)
  A1_7.AddSkillRecipe(17288, 1)
  A1_7.AddSkillRecipe(17289, 1)
  A1_7.AddSkillRecipe(17290, 1)
  A1_7.AddSkillRecipe(17291, 1)
  A1_7.AddSkillRecipe(17292, 1)
  A1_7.AddSkillRecipe(17293, 1)
  A1_7.AddSkillRecipe(17294, 1)
  A1_7.AddSkillRecipe(17295, 1)
  A1_7.AddSkillRecipe(17296, 1)
  A1_7.AddSkillRecipe(17297, 1)
  A1_7.AddSkillRecipe(17298, 1)
end
function Apply(A0_8)
  if GetPlayer(A0_8) then
    GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 14275, 1)
    GetPlayer(A0_8).bSurplusAutoCast = false
    GetPlayer(A0_8).bSurplusAutoReplenish = false
    if GetPlayer(A0_8).GetSkillLevel(102724) == 0 then
      GetPlayer(A0_8).LearnSkillLevel(102724, 1, A0_8)
    end
    GetPlayer(A0_8).SetTimer(4, "scripts/skill_mobile/万灵山庄/移动端_山海心诀_心法.lua", 0, 0)
  end
end
function UnApply(A0_9)
  if not GetPlayer(A0_9) then
    return
  end
end
function OnTimer(A0_10, A1_11, A2_12)
  A0_10.CastSkill(102218, 1)
end
