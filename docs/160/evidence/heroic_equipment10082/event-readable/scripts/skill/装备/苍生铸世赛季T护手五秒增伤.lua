Include("scripts/Include/Skill.lh")
tSkillData = {
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  },
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  },
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  },
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  },
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  },
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  },
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  },
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  },
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  },
  {
    nDamageBase = 0,
    nDamageRand = 0,
    nCostMana = 0
  }
}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/装备/苍生铸世赛季T护手五秒增伤.lua", 0)
  A0_0.AddSlowCheckSelfBuff(24791, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.SetNormalCoolDown(1, 2516)
  A0_0.bIgnorePrepareState = true
  A0_0.nMaxRadius = 5 * LENGTH_BASE
  A0_0.nAngleRange = 256
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
  if not GetPlayer(A0_9) then
    return
  end
  GetPlayer(A0_9).AddBuff(GetPlayer(A0_9).dwID, GetPlayer(A0_9).nLevel, 24767, 2)
  GetPlayer(A0_9).AddBuff(GetPlayer(A0_9).dwID, GetPlayer(A0_9).nLevel, 24791, 1)
end
function UnApply(A0_11)
  local L1_12
end
function OnRemove(A0_13, A1_14, A2_15, A3_16, A4_17, A5_18, A6_19, A7_20, A8_21, A9_22)
end
function OnEarlyWarning(A0_23, A1_24)
end
