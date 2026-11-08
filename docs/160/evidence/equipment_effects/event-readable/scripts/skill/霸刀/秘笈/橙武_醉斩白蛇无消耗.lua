Include("scripts/Include/Skill.lh")
function GetSkillRecipeData(A0_0, A1_1, A2_2)
  A0_0.nCostSunEnergy = 0
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 5086, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 1979, 0)
  return true
end
function CanCast(A0_3, A1_4)
  return A1_4
end
function CanLearnSkill(A0_5, A1_6)
  local L2_7
  L2_7 = true
  return L2_7
end
function OnSkillLevelUp(A0_8, A1_9)
end
