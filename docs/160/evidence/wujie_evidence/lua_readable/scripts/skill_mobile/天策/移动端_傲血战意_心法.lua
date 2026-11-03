Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 520,
    nPhysicsAttackPower = 828,
    nPhysicsShield = 2,
    nPhysicsHit = 9
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 727,
    nPhysicsAttackPower = 928,
    nPhysicsShield = 3,
    nPhysicsHit = 16
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1104,
    nPhysicsAttackPower = 1128,
    nPhysicsShield = 5,
    nPhysicsHit = 25
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nPhysicsAttackPower = 1328,
    nPhysicsShield = 7,
    nPhysicsHit = 35
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2789,
    nPhysicsShield = 20,
    nPhysicsHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2789,
    nPhysicsShield = 20,
    nPhysicsHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2789,
    nPhysicsShield = 20,
    nPhysicsHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2789,
    nPhysicsShield = 20,
    nPhysicsHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2789,
    nPhysicsShield = 20,
    nPhysicsHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2789,
    nPhysicsShield = 20,
    nPhysicsHit = 44
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 520,
    nPhysicsAttackPower = 328,
    nPhysicsShield = 2,
    nPhysicsHit = 9
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 727,
    nPhysicsAttackPower = 454,
    nPhysicsShield = 3,
    nPhysicsHit = 16
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1104,
    nPhysicsAttackPower = 690,
    nPhysicsShield = 5,
    nPhysicsHit = 25
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nPhysicsAttackPower = 922,
    nPhysicsShield = 7,
    nPhysicsHit = 35
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2789,
    nPhysicsShield = 20,
    nPhysicsHit = 44
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/天策/移动端_傲血战意_心法.lua", 0)
  AdditionalAttribute(A0_0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100406], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L1_1].nMP / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMP / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_ATTACK_POWER_COF, 563, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_OVERCOME_COF, 205, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L1_1].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L1_1].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMountID() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.AddSkillRecipe(16500, 1)
  A1_5.AddSkillRecipe(16507, 1)
  A1_5.AddSkillRecipe(16508, 1)
  A1_5.AddSkillRecipe(16511, 1)
  A1_5.AddSkillRecipe(16516, 1)
  A1_5.AddSkillRecipe(16517, 1)
  A1_5.AddSkillRecipe(16526, 1)
  A1_5.AddSkillRecipe(16527, 1)
  A1_5.AddSkillRecipe(16541, 1)
  A1_5.AddSkillRecipe(16542, 1)
  A1_5.AddSkillRecipe(16554, 1)
  A1_5.AddSkillRecipe(16555, 1)
  A1_5.AddSkillRecipe(16565, 1)
  A1_5.AddSkillRecipe(16566, 1)
  A1_5.AddSkillRecipe(16567, 1)
  A1_5.AddSkillRecipe(16568, 1)
  A1_5.AddSkillRecipe(16596, 1)
  A1_5.AddSkillRecipe(16597, 1)
  A1_5.AddSkillRecipe(16604, 1)
  A1_5.AddSkillRecipe(16605, 1)
  A1_5.AddSkillRecipe(17591, 1)
  A1_5.AddSkillRecipe(17592, 1)
  if A1_5.GetSkillLevel(102700) ~= 1 then
    A1_5.LearnSkillLevel(102700, 1, A1_5.dwID)
  end
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  GetPlayer(A0_6).bSurplusAutoCast = false
  GetPlayer(A0_6).bSurplusAutoReplenish = false
  if GetPlayer(A0_6) then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
  end
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 70810, 1)
  if GetPlayer(A0_6).GetSkillLevel(101558) == 1 then
    GetPlayer(A0_6).ForgetSkill(101558)
    GetPlayer(A0_6).ForgetSkill(100412)
    GetPlayer(A0_6).ForgetSkill(101560)
    GetPlayer(A0_6).LearnSkillLevel(100028, 1, A0_6)
  end
  RemoteCallToClient(GetPlayer(A0_6).dwID, "OnSkillReplace", 100412, 100028, 1)
  if GetPlayer(A0_6).GetSkillLevel(102700) ~= 1 then
    GetPlayer(A0_6).LearnSkillLevel(102700, 1, GetPlayer(A0_6).dwID)
  end
end
function UnApply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
  GetPlayer(A0_7).DelBuff(70810, 1)
  GetPlayer(A0_7).DelBuff(70115, 1)
end
function OnTimer(A0_8, A1_9, A2_10)
end
