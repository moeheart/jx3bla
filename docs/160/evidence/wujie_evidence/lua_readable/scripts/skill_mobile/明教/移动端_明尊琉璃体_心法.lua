Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    nMP = 703,
    nPhysicsDefence = 27,
    nMagicDefence = 27,
    nDodge = 53,
    nPhysicsCri = 5,
    nPhysicsHit = 4
  },
  {
    nMP = 982,
    nPhysicsDefence = 37,
    nMagicDefence = 37,
    nDodge = 75,
    nPhysicsCri = 6,
    nPhysicsHit = 5
  },
  {
    nMP = 1491,
    nPhysicsDefence = 57,
    nMagicDefence = 57,
    nDodge = 113,
    nPhysicsCri = 9,
    nPhysicsHit = 7
  },
  {
    nMP = 2000,
    nPhysicsDefence = 76,
    nMagicDefence = 76,
    nDodge = 152,
    nPhysicsCri = 11,
    nPhysicsHit = 9
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 703,
    nPhysicsDefence = 27,
    nMagicDefence = 27,
    nDodge = 53,
    nPhysicsCri = 5,
    nPhysicsHit = 4
  },
  {
    nMP = 982,
    nPhysicsDefence = 37,
    nMagicDefence = 37,
    nDodge = 75,
    nPhysicsCri = 6,
    nPhysicsHit = 5
  },
  {
    nMP = 1491,
    nPhysicsDefence = 57,
    nMagicDefence = 57,
    nDodge = 113,
    nPhysicsCri = 9,
    nPhysicsHit = 7
  },
  {
    nMP = 2000,
    nPhysicsDefence = 76,
    nMagicDefence = 76,
    nDodge = 152,
    nPhysicsCri = 11,
    nPhysicsHit = 9
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  }
}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/明教/移动端_明尊琉璃体_心法.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 9108, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, 512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.T, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_LIFE_COF, 2253, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_PARRY_VALUE_COF, 1280, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_DODGE_COF, 164, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_SUN_ENERGY, 10000, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MOON_ENERGY, 10000, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_SOLAR_ATTACK_POWER_COF, 163, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_LUNAR_ATTACK_POWER_COF, 163, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_LIFE_PERCENT_ADD, 51.2, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DODGE, tSkillData[L1_1].nDodge, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L1_1].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L1_1].nPhysicsDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_PERCENT, 1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXTRA_THREAT_COEFFICIENT, 11776, 0)
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
  A1_5.AddSkillRecipe(16867, 1)
  A1_5.AddSkillRecipe(16868, 1)
  A1_5.AddSkillRecipe(16869, 1)
  A1_5.AddSkillRecipe(16870, 1)
  A1_5.AddSkillRecipe(16871, 1)
  A1_5.AddSkillRecipe(16872, 1)
  A1_5.AddSkillRecipe(16873, 1)
  A1_5.AddSkillRecipe(16874, 1)
  A1_5.AddSkillRecipe(16875, 1)
  A1_5.AddSkillRecipe(16876, 1)
  A1_5.AddSkillRecipe(16877, 1)
  A1_5.AddSkillRecipe(16878, 1)
  A1_5.AddSkillRecipe(16879, 1)
  A1_5.AddSkillRecipe(16880, 1)
  A1_5.AddSkillRecipe(16881, 1)
  A1_5.AddSkillRecipe(16882, 1)
  A1_5.AddSkillRecipe(16883, 1)
  A1_5.AddSkillRecipe(16884, 1)
  A1_5.AddSkillRecipe(16885, 1)
  A1_5.AddSkillRecipe(16886, 1)
  A1_5.AddSkillRecipe(17635, 1)
  A1_5.AddSkillRecipe(17636, 1)
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  GetPlayer(A0_6).bSurplusAutoCast = false
  GetPlayer(A0_6).bSurplusAutoReplenish = false
  GetPlayer(A0_6).LearnSkillLevel(100872, 1, false)
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
