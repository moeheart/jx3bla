Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nNeHit = 10,
    nPhysicsOvercome = 47,
    nPhysicsAttackPower = 783
  },
  {
    DecriticalDamagePowerBase = 44,
    nNeHit = 18,
    nPhysicsOvercome = 65,
    nPhysicsAttackPower = 883
  },
  {
    DecriticalDamagePowerBase = 70,
    nNeHit = 28,
    nPhysicsOvercome = 99,
    nPhysicsAttackPower = 1083
  },
  {
    DecriticalDamagePowerBase = 95,
    nNeHit = 39,
    nPhysicsOvercome = 133,
    nPhysicsAttackPower = 1283
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 49,
    nPhysicsOvercome = 401,
    nPhysicsAttackPower = 2408
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 49,
    nPhysicsOvercome = 401,
    nPhysicsAttackPower = 2408
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 49,
    nPhysicsOvercome = 401,
    nPhysicsAttackPower = 2408
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 49,
    nPhysicsOvercome = 401,
    nPhysicsAttackPower = 2408
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 49,
    nPhysicsOvercome = 401,
    nPhysicsAttackPower = 2408
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 49,
    nPhysicsOvercome = 401,
    nPhysicsAttackPower = 2408
  },
  {
    DecriticalDamagePowerBase = 25,
    nNeHit = 10,
    nPhysicsOvercome = 47,
    nPhysicsAttackPower = 283
  },
  {
    DecriticalDamagePowerBase = 44,
    nNeHit = 18,
    nPhysicsOvercome = 65,
    nPhysicsAttackPower = 392
  },
  {
    DecriticalDamagePowerBase = 70,
    nNeHit = 28,
    nPhysicsOvercome = 99,
    nPhysicsAttackPower = 596
  },
  {
    DecriticalDamagePowerBase = 95,
    nNeHit = 39,
    nPhysicsOvercome = 133,
    nPhysicsAttackPower = 796
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 49,
    nPhysicsOvercome = 401,
    nPhysicsAttackPower = 2408
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/唐门/移动端_惊羽诀_心法.lua", 0)
  AdditionalAttribute(A0_0)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[101716], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_ATTACK_POWER_COF, 584, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_CRITICAL_STRIKE_COF, 184, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_OVERCOME_BASE, tSkillData[L2_2].nPhysicsOvercome, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L2_2].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_PERCENT, 1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function OnSkillLevelUp(A0_6, A1_7)
  if not A1_7.GetKungfuMountID() then
    A1_7.MountKungfu(A0_6.dwSkillID, A0_6.dwLevel)
  end
  A1_7.AddSkillRecipe(17131, 1)
  A1_7.AddSkillRecipe(17132, 1)
  A1_7.AddSkillRecipe(17133, 1)
  A1_7.AddSkillRecipe(17134, 1)
  A1_7.AddSkillRecipe(17135, 1)
  A1_7.AddSkillRecipe(17136, 1)
  A1_7.AddSkillRecipe(17137, 1)
  A1_7.AddSkillRecipe(17138, 1)
  A1_7.AddSkillRecipe(17139, 1)
  A1_7.AddSkillRecipe(17140, 1)
  A1_7.AddSkillRecipe(17141, 1)
  A1_7.AddSkillRecipe(17142, 1)
  A1_7.AddSkillRecipe(17143, 1)
  A1_7.AddSkillRecipe(17144, 1)
  A1_7.AddSkillRecipe(17145, 1)
  A1_7.AddSkillRecipe(17146, 1)
  A1_7.AddSkillRecipe(17147, 1)
  A1_7.AddSkillRecipe(17148, 1)
  A1_7.AddSkillRecipe(17149, 1)
  A1_7.AddSkillRecipe(17150, 1)
  A1_7.AddSkillRecipe(17151, 1)
  A1_7.AddSkillRecipe(17152, 1)
end
function Apply(A0_8)
  if GetPlayer(A0_8) then
    GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 14275, 1)
    GetPlayer(A0_8).bSurplusAutoCast = false
    GetPlayer(A0_8).bSurplusAutoReplenish = false
    if GetPlayer(A0_8).GetSkillLevel(102689) == 0 then
      GetPlayer(A0_8).LearnSkillLevel(102689, 1, A0_8)
    end
  end
end
function UnApply(A0_9)
  local L1_10
end
function OnTimer(A0_11, A1_12, A2_13)
end
