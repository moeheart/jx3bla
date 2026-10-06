Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nNeHit = 8,
    nPhysicsCri = 36,
    nPoisonAttackPower = 768,
    nMagicDefence = 25
  },
  {
    DecriticalDamagePowerBase = 44,
    nNeHit = 14,
    nPhysicsCri = 50,
    nPoisonAttackPower = 868,
    nMagicDefence = 35
  },
  {
    DecriticalDamagePowerBase = 70,
    nNeHit = 22,
    nPhysicsCri = 76,
    nPoisonAttackPower = 1068,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 95,
    nNeHit = 31,
    nPhysicsCri = 102,
    nPoisonAttackPower = 1268,
    nMagicDefence = 73
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 25,
    nNeHit = 8,
    nPhysicsCri = 36,
    nPoisonAttackPower = 268,
    nMagicDefence = 25
  },
  {
    DecriticalDamagePowerBase = 44,
    nNeHit = 14,
    nPhysicsCri = 50,
    nPoisonAttackPower = 372,
    nMagicDefence = 35
  },
  {
    DecriticalDamagePowerBase = 70,
    nNeHit = 22,
    nPhysicsCri = 76,
    nPoisonAttackPower = 564,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 95,
    nNeHit = 31,
    nPhysicsCri = 102,
    nPoisonAttackPower = 754,
    nMagicDefence = 73
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_POISON_ATTACK_POWER_COF, 543, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_PHYSICS_CRITICAL_STRIKE_COF, 225, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.POISON_ATTACK_POWER_BASE, tSkillData[L2_2].nPoisonAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L3_3].nPhysicsCri, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_PERCENT, 1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.POISON)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[101734], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.POISON)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/唐门/移动端_天罗诡道_心法.lua", 0)
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
  A1_7.AddSkillRecipe(17213, 1)
  A1_7.AddSkillRecipe(17214, 1)
  A1_7.AddSkillRecipe(17215, 1)
  A1_7.AddSkillRecipe(17216, 1)
  A1_7.AddSkillRecipe(17217, 1)
  A1_7.AddSkillRecipe(17218, 1)
  A1_7.AddSkillRecipe(17219, 1)
  A1_7.AddSkillRecipe(17220, 1)
  A1_7.AddSkillRecipe(17221, 1)
  A1_7.AddSkillRecipe(17222, 1)
  A1_7.AddSkillRecipe(17223, 1)
  A1_7.AddSkillRecipe(17224, 1)
  A1_7.AddSkillRecipe(17225, 1)
  A1_7.AddSkillRecipe(17226, 1)
  A1_7.AddSkillRecipe(17227, 1)
  A1_7.AddSkillRecipe(17228, 1)
  A1_7.AddSkillRecipe(17229, 1)
  A1_7.AddSkillRecipe(17230, 1)
  A1_7.AddSkillRecipe(17231, 1)
  A1_7.AddSkillRecipe(17232, 1)
end
function Apply(A0_8)
  if GetPlayer(A0_8) then
    GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 14275, 1)
    GetPlayer(A0_8).bSurplusAutoCast = false
    GetPlayer(A0_8).bSurplusAutoReplenish = false
    if GetPlayer(A0_8).GetSkillLevel(102739) == 0 then
      GetPlayer(A0_8).LearnSkillLevel(102739, 1, A0_8)
    end
  end
end
function UnApply(A0_9)
  local L1_10
end
function OnTimer(A0_11, A1_12, A2_13)
end
