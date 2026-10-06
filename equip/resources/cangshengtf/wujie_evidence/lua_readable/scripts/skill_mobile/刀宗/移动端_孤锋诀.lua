Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 528,
    nPhysicsAttackPower = 789,
    nPhysicsCriticalStrike = 41
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 738,
    nPhysicsAttackPower = 889,
    nPhysicsCriticalStrike = 57
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1121,
    nPhysicsAttackPower = 1089,
    nPhysicsCriticalStrike = 87
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2030,
    nPhysicsAttackPower = 1289,
    nPhysicsCriticalStrike = 116
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 528,
    nPhysicsAttackPower = 289,
    nPhysicsCriticalStrike = 41
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 738,
    nPhysicsAttackPower = 401,
    nPhysicsCriticalStrike = 57
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1121,
    nPhysicsAttackPower = 608,
    nPhysicsCriticalStrike = 87
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2030,
    nPhysicsAttackPower = 813,
    nPhysicsCriticalStrike = 116
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
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
  {DecriticalDamagePowerBase = 1725},
  {DecriticalDamagePowerBase = 1725}
}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/刀宗/移动端_孤锋诀.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[101375], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 60, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMP / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_ATTACK_POWER_COF, 604, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_CRITICAL_STRIKE_COF, 164, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L1_1].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L1_1].nPhysicsCriticalStrike, 0)
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
  A1_5.AddSkillRecipe(17096, 1)
  A1_5.AddSkillRecipe(17097, 1)
  A1_5.AddSkillRecipe(17098, 1)
  A1_5.AddSkillRecipe(17099, 1)
  A1_5.AddSkillRecipe(17100, 1)
  A1_5.AddSkillRecipe(17101, 1)
  A1_5.AddSkillRecipe(17102, 1)
  A1_5.AddSkillRecipe(17103, 1)
  A1_5.AddSkillRecipe(17104, 1)
  A1_5.AddSkillRecipe(17105, 1)
  A1_5.AddSkillRecipe(17106, 1)
  A1_5.AddSkillRecipe(17107, 1)
  A1_5.AddSkillRecipe(17108, 1)
  A1_5.AddSkillRecipe(17109, 1)
  A1_5.AddSkillRecipe(17110, 1)
  A1_5.AddSkillRecipe(17111, 1)
  A1_5.AddSkillRecipe(17112, 1)
  A1_5.AddSkillRecipe(17113, 1)
  A1_5.AddSkillRecipe(17114, 1)
  A1_5.AddSkillRecipe(17115, 1)
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  GetPlayer(A0_6).DelBuff(24042, 1)
  GetPlayer(A0_6).DelBuff(23646, 1)
  GetPlayer(A0_6).DelBuff(24029, 1)
  GetPlayer(A0_6).DelBuff(24029, 2)
  GetPlayer(A0_6).DelBuff(24104, 1)
  GetPlayer(A0_6).DelBuff(24273, 1)
  GetPlayer(A0_6).DelBuff(24274, 1)
  GetPlayer(A0_6).DelBuff(24110, 1)
  GetPlayer(A0_6).DelBuff(24110, 2)
  if GetPlayer(A0_6).nPoseState == 0 then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 70803, 1)
  elseif GetPlayer(A0_6).nPoseState == 1 then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 70803, 1)
  elseif GetPlayer(A0_6).nPoseState == 2 then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 70803, 2)
  elseif GetPlayer(A0_6).nPoseState == 3 then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 70803, 2)
  elseif GetPlayer(A0_6).nPoseState == 4 then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 70803, 1)
  end
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 70537, 1)
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 71281, 1)
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
  GetPlayer(A0_6).bSurplusAutoCast = false
  GetPlayer(A0_6).bSurplusAutoReplenish = false
  if GetPlayer(A0_6).GetSkillLevel(102740) == 0 then
    GetPlayer(A0_6).LearnSkillLevel(102740, 1, false)
  end
end
function UnApply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
  GetPlayer(A0_7).DelBuff(70537, 1)
  GetPlayer(A0_7).DelBuff(70803, 1)
  GetPlayer(A0_7).DelBuff(70803, 2)
  GetPlayer(A0_7).DelBuff(70804, 1)
  GetPlayer(A0_7).DelBuff(70804, 2)
  GetPlayer(A0_7).DelBuff(71281, 1)
  GetPlayer(A0_7).AddBuff(GetPlayer(A0_7).dwID, GetPlayer(A0_7).nLevel, 24029, 1)
end
function OnTimer(A0_8, A1_9, A2_10)
end
