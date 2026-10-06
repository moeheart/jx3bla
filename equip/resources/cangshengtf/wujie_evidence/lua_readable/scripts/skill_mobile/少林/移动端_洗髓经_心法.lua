Include("scripts/Include/Skill.lh")
tSkillData = {
  {
    nMana = 499,
    nMagicDefence = 53,
    nDuck = 20,
    nPhysicDefence = 32
  },
  {
    nMana = 698,
    nMagicDefence = 75,
    nDuck = 28,
    nPhysicDefence = 45
  },
  {
    nMana = 1060,
    nMagicDefence = 113,
    nDuck = 42,
    nPhysicDefence = 68
  },
  {
    nMana = 1920,
    nMagicDefence = 152,
    nDuck = 56,
    nPhysicDefence = 91
  },
  {
    nMana = 5760,
    nMagicDefence = 457,
    nDuck = 169,
    nPhysicDefence = 274
  },
  {
    nMana = 5760,
    nMagicDefence = 457,
    nDuck = 169,
    nPhysicDefence = 274
  },
  {
    nMana = 5760,
    nMagicDefence = 457,
    nDuck = 169,
    nPhysicDefence = 274
  },
  {
    nMana = 5760,
    nMagicDefence = 457,
    nDuck = 169,
    nPhysicDefence = 274
  },
  {
    nMana = 5760,
    nMagicDefence = 457,
    nDuck = 169,
    nPhysicDefence = 274
  },
  {
    nMana = 5760,
    nMagicDefence = 457,
    nDuck = 169,
    nPhysicDefence = 274
  },
  {
    nMana = 499,
    nMagicDefence = 53,
    nDuck = 20,
    nPhysicDefence = 32
  },
  {
    nMana = 698,
    nMagicDefence = 75,
    nDuck = 28,
    nPhysicDefence = 45
  },
  {
    nMana = 1060,
    nMagicDefence = 113,
    nDuck = 42,
    nPhysicDefence = 68
  },
  {
    nMana = 1920,
    nMagicDefence = 152,
    nDuck = 56,
    nPhysicDefence = 91
  },
  {
    nMana = 5760,
    nMagicDefence = 457,
    nDuck = 169,
    nPhysicDefence = 274
  }
}
function GetSkillLevelData(A0_0)
  local L1_1, L2_2, L3_3
  L1_1 = false
  L2_2 = A0_0.dwLevel
  L3_3 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_SOLAR_ATTACK_POWER_COF, 163, 0)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_LIFE_COF, 2253, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAGIC_SHIELD_COF, 164, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_PARRY_VALUE_COF, 1280, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_LIFE_PERCENT_ADD, 81.92, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXTRA_THREAT_COEFFICIENT, 11776, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_REFLECTION, tSkillData[L2_2].nDuck, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.POISON_MAGIC_REFLECTION, tSkillData[L2_2].nDuck, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SOLAR_MAGIC_REFLECTION, tSkillData[L2_2].nDuck, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NEUTRAL_MAGIC_REFLECTION, tSkillData[L2_2].nDuck, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LUNAR_MAGIC_REFLECTION, tSkillData[L2_2].nDuck, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L2_2].nPhysicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, 512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/少林/移动端_洗髓经_心法.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.SOLAR_MAGIC, SKILL_KIND_TYPE.SOLAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 9087, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 9108, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.T, 0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function CanLearnSkill(A0_6, A1_7)
  local L2_8
  L2_8 = true
  return L2_8
end
function OnSkillLevelUp(A0_9, A1_10)
  if not A1_10.GetKungfuMount() then
    A1_10.MountKungfu(A0_9.dwSkillID, A0_9.dwLevel)
  end
  A1_10.AddSkillRecipe(17174, 1)
  A1_10.AddSkillRecipe(17175, 1)
  A1_10.AddSkillRecipe(17176, 1)
  A1_10.AddSkillRecipe(17177, 1)
  A1_10.AddSkillRecipe(17178, 1)
  A1_10.AddSkillRecipe(17179, 1)
  A1_10.AddSkillRecipe(17180, 1)
  A1_10.AddSkillRecipe(17181, 1)
  A1_10.AddSkillRecipe(17182, 1)
  A1_10.AddSkillRecipe(17183, 1)
  A1_10.AddSkillRecipe(17184, 1)
  A1_10.AddSkillRecipe(17185, 1)
  A1_10.AddSkillRecipe(17186, 1)
  A1_10.AddSkillRecipe(17187, 1)
  A1_10.AddSkillRecipe(17188, 1)
  A1_10.AddSkillRecipe(17189, 1)
  A1_10.AddSkillRecipe(17190, 1)
  A1_10.AddSkillRecipe(17191, 1)
  A1_10.AddSkillRecipe(17192, 1)
  A1_10.AddSkillRecipe(17193, 1)
end
function Apply(A0_11)
  if GetPlayer(A0_11) then
    GetPlayer(A0_11).AddBuff(GetPlayer(A0_11).dwID, GetPlayer(A0_11).nLevel, 14275, 1)
    GetPlayer(A0_11).bSurplusAutoCast = false
    GetPlayer(A0_11).bSurplusAutoReplenish = false
    GetPlayer(A0_11).LearnSkillLevel(102680, 1, false)
  end
end
function UnApply(A0_12)
  local L1_13
end
function OnTimer(A0_14, A1_15, A2_16)
end
