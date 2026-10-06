Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nAttackPower = 813,
    nMagicDefence = 17,
    nPhysicsCri = 5,
    nHit = 9
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nAttackPower = 913,
    nMagicDefence = 24,
    nPhysicsCri = 6,
    nHit = 16
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nAttackPower = 1113,
    nMagicDefence = 37,
    nPhysicsCri = 9,
    nHit = 25
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nAttackPower = 1313,
    nMagicDefence = 49,
    nPhysicsCri = 11,
    nHit = 35
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nAttackPower = 313,
    nMagicDefence = 17,
    nPhysicsCri = 5,
    nHit = 9
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nAttackPower = 434,
    nMagicDefence = 24,
    nPhysicsCri = 6,
    nHit = 16
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nAttackPower = 658,
    nMagicDefence = 37,
    nPhysicsCri = 9,
    nHit = 25
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nAttackPower = 880,
    nMagicDefence = 49,
    nPhysicsCri = 11,
    nHit = 35
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nAttackPower = 2662,
    nMagicDefence = 147,
    nPhysicsCri = 13,
    nHit = 44
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/明教/移动端_焚影圣诀_心法.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100618], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_SOLAR_AND_LUNAR_ATTACK_POWER_COF, 635, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_SOLAR_AND_LUNAR_CRITICAL_STRIKE_COF, 133, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_SUN_ENERGY, 10000, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MOON_ENERGY, 10000, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LUNAR_ATTACK_POWER_BASE, tSkillData[L1_1].nAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SOLAR_ATTACK_POWER_BASE, tSkillData[L1_1].nAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L1_1].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_PERCENT, 1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 9139, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMountID() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.AddSkillRecipe(16774, 1)
  A1_5.AddSkillRecipe(16775, 1)
  A1_5.AddSkillRecipe(16776, 1)
  A1_5.AddSkillRecipe(16777, 1)
  A1_5.AddSkillRecipe(16778, 1)
  A1_5.AddSkillRecipe(16779, 1)
  A1_5.AddSkillRecipe(16780, 1)
  A1_5.AddSkillRecipe(16781, 1)
  A1_5.AddSkillRecipe(16782, 1)
  A1_5.AddSkillRecipe(16783, 1)
  A1_5.AddSkillRecipe(16784, 1)
  A1_5.AddSkillRecipe(16785, 1)
  A1_5.AddSkillRecipe(16786, 1)
  A1_5.AddSkillRecipe(16787, 1)
  A1_5.AddSkillRecipe(16788, 1)
  A1_5.AddSkillRecipe(16789, 1)
  A1_5.AddSkillRecipe(16790, 1)
  A1_5.AddSkillRecipe(16791, 1)
  A1_5.AddSkillRecipe(16792, 1)
  A1_5.AddSkillRecipe(16793, 1)
  A1_5.AddSkillRecipe(17595, 1)
  A1_5.AddSkillRecipe(17596, 1)
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  GetPlayer(A0_6).bSurplusAutoCast = false
  GetPlayer(A0_6).bSurplusAutoReplenish = false
  GetPlayer(A0_6).LearnSkillLevel(102704, 1, false)
  if GetPlayer(A0_6) then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
  end
end
function UnApply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
  GetPlayer(A0_7).nMoonPowerValue = 0
  GetPlayer(A0_7).nSunPowerValue = 0
  GetPlayer(A0_7).nCurrentMoonEnergy = 0
  GetPlayer(A0_7).nCurrentSunEnergy = 0
  GetPlayer(A0_7).DelBuff(70212, 1)
end
function OnTimer(A0_8, A1_9, A2_10)
end
