Include("scripts/Include/Skill.lh")
tSkillData = {
  {nLifeAdd = 25},
  {nLifeAdd = 28},
  {nLifeAdd = 31},
  {nLifeAdd = 49},
  {nLifeAdd = 60},
  {nLifeAdd = 67},
  {nLifeAdd = 74},
  {nLifeAdd = 110},
  {nLifeAdd = 100},
  {nLifeAdd = 121},
  {nLifeAdd = 133},
  {nLifeAdd = 148},
  {nLifeAdd = 288},
  {nLifeAdd = 317},
  {nLifeAdd = 346},
  {nLifeAdd = 425},
  {nLifeAdd = 498},
  {nLifeAdd = 2047},
  {nLifeAdd = 2250}
}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_DEST_NOT_ROLLBACK, ATTRIBUTE_TYPE.CALL_THERAPY, tSkillData[A0_0.dwLevel].nLifeAdd, 0)
  A0_0.AddSlowCheckSelfOwnBuff(15423, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.BindBuff(1, 15423, 1)
  A0_0.bIgnorePrepareState = true
  A0_0.nMinRadius = 0 * LENGTH_BASE
  A0_0.nMaxRadius = 4 * LENGTH_BASE
  A0_0.nAngleRange = 256
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
end
function OnSkillForgotten(A0_6, A1_7)
end
function Apply(A0_8, A1_9)
end
function UnApply(A0_10)
  local L1_11
end
function OnRemove(A0_12, A1_13, A2_14, A3_15, A4_16, A5_17, A6_18, A7_19, A8_20, A9_21)
end
