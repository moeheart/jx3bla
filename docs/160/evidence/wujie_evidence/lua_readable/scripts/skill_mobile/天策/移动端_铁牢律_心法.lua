Include("scripts/Include/Skill.lh")
tSkillData = {
  {
    nMP = 494,
    nPhysicsShield = 53,
    nParry = 32,
    nParryValue = 124,
    nThreatCof = 204
  },
  {
    nMP = 691,
    nPhysicsShield = 75,
    nParry = 45,
    nParryValue = 173,
    nThreatCof = 204
  },
  {
    nMP = 1049,
    nPhysicsShield = 113,
    nParry = 68,
    nParryValue = 262,
    nThreatCof = 204
  },
  {
    nMP = 1900,
    nPhysicsShield = 152,
    nParry = 91,
    nParryValue = 352,
    nThreatCof = 204
  },
  {
    nMP = 5700,
    nPhysicsShield = 457,
    nParry = 274,
    nParryValue = 1056,
    nThreatCof = 204
  },
  {
    nMP = 5700,
    nPhysicsShield = 457,
    nParry = 274,
    nParryValue = 1056,
    nThreatCof = 204
  },
  {
    nMP = 5700,
    nPhysicsShield = 457,
    nParry = 274,
    nParryValue = 1056,
    nThreatCof = 204
  },
  {
    nMP = 5700,
    nPhysicsShield = 457,
    nParry = 274,
    nParryValue = 1056,
    nThreatCof = 204
  },
  {
    nMP = 5700,
    nPhysicsShield = 457,
    nParry = 274,
    nParryValue = 1056,
    nThreatCof = 204
  },
  {
    nMP = 5700,
    nPhysicsShield = 457,
    nParry = 274,
    nParryValue = 1056,
    nThreatCof = 204
  },
  {
    nMP = 494,
    nPhysicsShield = 53,
    nParry = 32,
    nParryValue = 124,
    nThreatCof = 204
  },
  {
    nMP = 691,
    nPhysicsShield = 75,
    nParry = 45,
    nParryValue = 173,
    nThreatCof = 204
  },
  {
    nMP = 1049,
    nPhysicsShield = 113,
    nParry = 68,
    nParryValue = 262,
    nThreatCof = 204
  },
  {
    nMP = 1900,
    nPhysicsShield = 152,
    nParry = 91,
    nParryValue = 352,
    nThreatCof = 204
  },
  {
    nMP = 5700,
    nPhysicsShield = 457,
    nParry = 274,
    nParryValue = 1056,
    nThreatCof = 204
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
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/天策/移动端_铁牢律_心法.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 9108, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, 512)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.T, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L1_1].nMP / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMP / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_PARRY_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_PHYSICS_SHIELD_COF, 164, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_LIFE_COF, 2253, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_PARRY_VALUE_COF, 1280, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_LIFE_PERCENT_ADD, 51.2, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L1_1].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXTRA_THREAT_COEFFICIENT, 11776, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PARRY_BASE, tSkillData[L1_1].nParry, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_PHYSICS_ATTACK_POWER_COF, 146, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PARRYVALUE_BASE, tSkillData[L1_1].nParryValue, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 9015, 0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function CanLearnSkill(A0_4, A1_5)
  local L2_6
  L2_6 = true
  return L2_6
end
function OnSkillLevelUp(A0_7, A1_8)
  if not A1_8.GetKungfuMountID() then
    A1_8.MountKungfu(A0_7.dwSkillID, A0_7.dwLevel)
  end
  A1_8.AddSkillRecipe(16627, 1)
  A1_8.AddSkillRecipe(16628, 1)
  A1_8.AddSkillRecipe(16629, 1)
  A1_8.AddSkillRecipe(16630, 1)
  A1_8.AddSkillRecipe(16631, 1)
  A1_8.AddSkillRecipe(16632, 1)
  A1_8.AddSkillRecipe(16633, 1)
  A1_8.AddSkillRecipe(16634, 1)
  A1_8.AddSkillRecipe(16635, 1)
  A1_8.AddSkillRecipe(16636, 1)
  A1_8.AddSkillRecipe(16637, 1)
  A1_8.AddSkillRecipe(16638, 1)
  A1_8.AddSkillRecipe(16639, 1)
  A1_8.AddSkillRecipe(16640, 1)
  A1_8.AddSkillRecipe(16641, 1)
  A1_8.AddSkillRecipe(16642, 1)
  A1_8.AddSkillRecipe(16643, 1)
  A1_8.AddSkillRecipe(16644, 1)
  A1_8.AddSkillRecipe(16645, 1)
  A1_8.AddSkillRecipe(16646, 1)
  A1_8.AddSkillRecipe(17627, 1)
  A1_8.AddSkillRecipe(17628, 1)
end
function Apply(A0_9)
  if not GetPlayer(A0_9) then
    return
  end
  GetPlayer(A0_9).bSurplusAutoCast = false
  GetPlayer(A0_9).bSurplusAutoReplenish = false
  if GetPlayer(A0_9) then
    GetPlayer(A0_9).AddBuff(GetPlayer(A0_9).dwID, GetPlayer(A0_9).nLevel, 14275, 1)
  end
  if GetPlayer(A0_9).GetSkillLevel(102757) ~= 1 then
    GetPlayer(A0_9).LearnSkillLevel(102757, 1, GetPlayer(A0_9).dwID)
  end
end
function UnApply(A0_10)
  local L1_11
end
function OnTimer(A0_12, A1_13, A2_14)
end
