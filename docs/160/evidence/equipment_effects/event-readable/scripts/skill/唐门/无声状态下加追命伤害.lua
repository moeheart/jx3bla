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
  if GetPlayer(A0_10).IsSkillRecipeActive(5144, 1) then
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 17103, 1)
  end
  if GetPlayer(A0_10).GetSkillLevel(44457) ~= 1 then
    return
  end
  if GetPlayer(A0_10).GetSkillLevel(44459) == 1 and not GetPlayer(A0_10).IsHaveBuff(12481, 1) then
    return
  end
  GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 33103, 1)
end
function UnApply(A0_12)
  if not GetPlayer(A0_12) then
    return
  end
  GetPlayer(A0_12).DelBuff(17103, 1)
  GetPlayer(A0_12).DelBuff(33103, 1)
end
function OnRemove(A0_13, A1_14, A2_15, A3_16, A4_17, A5_18, A6_19, A7_20, A8_21, A9_22)
end
function OnEarlyWarning(A0_23, A1_24)
end
