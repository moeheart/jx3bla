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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CALL_BUFF, 15414, 1)
  A0_0.AddSlowCheckSelfOwnBuff(15414, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.BindBuff(1, 15413, L1_1)
  A0_0.bIgnorePrepareState = true
  A0_0.nMinRadius = 0 * LENGTH_BASE
  A0_0.nMaxRadius = 20 * LENGTH_BASE
  A0_0.nAngleRange = 256
  if L1_1 < 15 then
    A0_0.nAreaRadius = 10 * LENGTH_BASE
  else
    A0_0.nAreaRadius = 20 * LENGTH_BASE
  end
  A0_0.nTargetCountLimit = 5
  A0_0.nWeaponDamagePercent = 0
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
