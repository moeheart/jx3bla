Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    nParryValue = 124,
    nParry = 53,
    nPhysicsShield = 32
  },
  {
    nParryValue = 173,
    nParry = 75,
    nPhysicsShield = 45
  },
  {
    nParryValue = 262,
    nParry = 113,
    nPhysicsShield = 68
  },
  {
    nParryValue = 352,
    nParry = 152,
    nPhysicsShield = 91
  },
  {
    nParryValue = 1056,
    nParry = 457,
    nPhysicsShield = 274
  },
  {
    nParryValue = 1056,
    nParry = 457,
    nPhysicsShield = 274
  },
  {
    nParryValue = 1056,
    nParry = 457,
    nPhysicsShield = 274
  },
  {
    nParryValue = 1056,
    nParry = 457,
    nPhysicsShield = 274
  },
  {
    nParryValue = 1056,
    nParry = 457,
    nPhysicsShield = 274
  },
  {
    nParryValue = 1056,
    nParry = 457,
    nPhysicsShield = 274
  },
  {
    nParryValue = 124,
    nParry = 53,
    nPhysicsShield = 32
  },
  {
    nParryValue = 173,
    nParry = 75,
    nPhysicsShield = 45
  },
  {
    nParryValue = 262,
    nParry = 113,
    nPhysicsShield = 68
  },
  {
    nParryValue = 352,
    nParry = 152,
    nPhysicsShield = 91
  },
  {
    nParryValue = 1056,
    nParry = 457,
    nPhysicsShield = 274
  }
}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 9108, 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_PARRY_COF, 164, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_PARRY_VALUE_COF, 1638, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_LIFE_COF, 2253, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_PHYSICS_ATTACK_POWER_COF, 146, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, 512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_LIFE_PERCENT_ADD, 51.2, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L1_1].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PARRY_BASE, tSkillData[L1_1].nParry, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PARRYVALUE_BASE, tSkillData[L1_1].nParryValue, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_PERCENT, 1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.T, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXTRA_THREAT_COEFFICIENT, 11776, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/苍云/移动端_心法_铁骨衣.lua", 0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMount() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.AddSkillRecipe(17259, 1)
  A1_5.AddSkillRecipe(17260, 1)
  A1_5.AddSkillRecipe(17261, 1)
  A1_5.AddSkillRecipe(17262, 1)
  A1_5.AddSkillRecipe(17263, 1)
  A1_5.AddSkillRecipe(17264, 1)
  A1_5.AddSkillRecipe(17265, 1)
  A1_5.AddSkillRecipe(17266, 1)
  A1_5.AddSkillRecipe(17267, 1)
  A1_5.AddSkillRecipe(17268, 1)
  A1_5.AddSkillRecipe(17269, 1)
  A1_5.AddSkillRecipe(17270, 1)
  A1_5.AddSkillRecipe(17271, 1)
  A1_5.AddSkillRecipe(17272, 1)
  A1_5.AddSkillRecipe(17273, 1)
  A1_5.AddSkillRecipe(17274, 1)
  A1_5.AddSkillRecipe(17275, 1)
  A1_5.AddSkillRecipe(17276, 1)
  A1_5.AddSkillRecipe(17277, 1)
  A1_5.AddSkillRecipe(17278, 1)
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
  GetPlayer(A0_6).bSurplusAutoCast = false
  GetPlayer(A0_6).bSurplusAutoReplenish = false
  if GetPlayer(A0_6).GetSkillLevel(102765) ~= 1 then
    GetPlayer(A0_6).LearnSkillLevel(102765, 1, false)
  end
end
function UnApply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
end
function OnTimer(A0_8, A1_9, A2_10)
end
