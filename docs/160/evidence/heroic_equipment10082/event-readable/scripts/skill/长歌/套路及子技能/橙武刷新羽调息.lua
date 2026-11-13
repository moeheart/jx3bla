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
  local L1_1, L2_2
  L1_1 = A0_0.dwLevel
  L2_2 = true
  return L2_2
end
function CanCast(A0_3, A1_4, A2_5)
  return A1_4
end
function OnSkillLevelUp(A0_6, A1_7)
end
function OnSkillForgotten(A0_8, A1_9)
end
function Apply(A0_10, A1_11)
  if not GetPlayer(A0_10) then
    return
  end
end
function UnApply(A0_12)
  local L1_13
end
function OnRemove(A0_14, A1_15, A2_16, A3_17, A4_18, A5_19, A6_20, A7_21, A8_22, A9_23)
end
function OnEarlyWarning(A0_24, A1_25)
end
