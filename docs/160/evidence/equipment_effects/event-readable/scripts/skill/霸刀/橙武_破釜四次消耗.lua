Include("scripts/Include/Skill.lh")
function Apply(A0_0, A1_1)
end
function UnApply(A0_2)
  local L1_3
end
function OnRemove(A0_4, A1_5, A2_6, A3_7, A4_8, A5_9, A6_10, A7_11, A8_12, A9_13)
  if not GetPlayer(A0_4) then
    return
  end
  if GetPlayer(A0_4).IsSkillRecipeExist(6584, 1) then
    GetPlayer(A0_4).DelSkillRecipe(6584, 1)
  end
end
