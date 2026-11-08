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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_DEST_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/装备/腰带_大附魔_高血量额外治疗及移速加成.lua", 0)
  A0_0.AddSlowCheckSelfBuff(24793, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
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
  local L2_11, L3_12, L4_13
  L2_11 = GetPlayer
  L3_12 = A1_10
  L2_11 = L2_11(L3_12)
  if not L2_11 then
    return
  end
  L3_12, L4_13 = nil, nil
  if not GetPlayer(A0_9) then
    L3_12 = GetNpc(A0_9)
    L4_13 = TARGET.NPC
  else
    L3_12 = GetPlayer(A0_9)
    L4_13 = TARGET.PLAYER
  end
  if not L3_12 then
    return
  end
  if L2_11.bFightState == true and L3_12.bFightState == true then
    L2_11.CastSkill(33613, 1, L4_13, A0_9)
    L2_11.AddBuff(L2_11.dwID, L2_11.nLevel, 24793, 1)
  end
end
function UnApply(A0_14)
  local L1_15
end
function OnRemove(A0_16, A1_17, A2_18, A3_19, A4_20, A5_21, A6_22, A7_23, A8_24, A9_25)
end
function OnEarlyWarning(A0_26, A1_27)
end
