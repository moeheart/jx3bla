Include("scripts/Include/Skill.lh")
tSkillData = {
  {
    nDamageBase = 3,
    nDamageRand = 1,
    nCostMana = 0
  }
}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_THERAPY, 1, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_THERAPY_RAND, 1, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_DEST_NOT_ROLLBACK, ATTRIBUTE_TYPE.CALL_THERAPY, 0, 0)
  A0_0.AddSlowCheckSelfBuff(24793, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.BindBuff(1, 24766, 1)
  A0_0.bIgnorePrepareState = true
  A0_0.nMinRadius = 0 * LENGTH_BASE
  A0_0.nMaxRadius = 50 * LENGTH_BASE
  A0_0.nAngleRange = 256
  A0_0.nTargetCountLimit = 1
  A0_0.nChannelInterval = 40
  A0_0.nSelfLifePercentMin = 75
  return true
end
function CanCast(A0_2, A1_3, A2_4)
  return A1_3
end
function OnSkillLevelUp(A0_5, A1_6)
end
function OnSkillForgotten(A0_7, A1_8)
end
function Apply(A0_9, A1_10)
end
function UnApply(A0_11)
  local L1_12
end
function OnRemove(A0_13, A1_14, A2_15, A3_16, A4_17, A5_18, A6_19, A7_20, A8_21, A9_22)
end
function OnEarlyWarning(A0_23, A1_24)
end
