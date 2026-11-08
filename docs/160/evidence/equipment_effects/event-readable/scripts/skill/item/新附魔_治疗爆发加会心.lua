Include("scripts/Include/Skill.lh")
tSkillData = {}
function GetSkillLevelData(A0_0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_DEST_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/item/新附魔_治疗爆发加会心.lua", 0)
  A0_0.AddSlowCheckSelfBuff(15474, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  if A0_0.dwLevel == 1 then
    A0_0.BindBuff(1, 15475, 1)
  elseif A0_0.dwLevel == 2 then
    A0_0.BindBuff(1, 15475, 2)
  end
  A0_0.nMinRadius = 0 * LENGTH_BASE
  A0_0.nMaxRadius = 25 * LENGTH_BASE
  A0_0.nAngleRange = 256
  A0_0.nSelfLifePercentMin = 0
  A0_0.nSelfLifePercentMax = 30
  return true
end
function CanCast(A0_1, A1_2)
  return A1_2
end
function OnSkillLevelUp(A0_3, A1_4)
end
function Apply(A0_5, A1_6)
  if not GetPlayer(A0_5) then
    return
  end
  GetPlayer(A0_5).AddBuff(GetPlayer(A0_5).dwID, GetPlayer(A0_5).nLevel, 15474, 1, 16)
end
function UnApply(A0_7)
  local L1_8
end
