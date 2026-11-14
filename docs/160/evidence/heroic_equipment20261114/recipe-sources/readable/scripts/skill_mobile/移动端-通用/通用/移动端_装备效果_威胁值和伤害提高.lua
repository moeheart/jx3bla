Include("scripts/Include/Skill.lh")
tSkillRecipeData = {}
function GetSkillRecipeData(A0_0, A1_1, A2_2)
  local L3_3
  L3_3 = A2_2
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/移动端-通用/通用/移动端_装备效果_威胁值和伤害提高.lua", 0)
  return
end
function Apply(A0_4, A1_5)
  if not GetPlayer(A0_4) then
    return
  end
  GetPlayer(A0_4).CastSkillNoChangeTarget(102259, 1, TARGET.PLAYER, GetPlayer(A0_4).dwID)
end
function CanCast(A0_6, A1_7)
  return A1_7
end
function CanLearnSkill(A0_8, A1_9)
  local L2_10
  L2_10 = true
  return L2_10
end
function OnSkillLevelUp(A0_11, A1_12)
end
function UnApply(A0_13)
  local L1_14
end
