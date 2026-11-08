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
end
function UnApply(A0_12)
  local L1_13
end
function OnRemove(A0_14, A1_15, A2_16, A3_17, A4_18, A5_19, A6_20, A7_21, A8_22, A9_23)
  local L10_24, L11_25, L12_26, L13_27
  L10_24 = GetPlayer
  L11_25 = A0_14
  L10_24 = L10_24(L11_25)
  if not L10_24 then
    return
  end
  L11_25 = L10_24.GetBuff
  L12_26 = 3276
  L13_27 = 1
  L11_25 = L11_25(L12_26, L13_27)
  if L11_25 then
    L12_26 = L11_25.nStackNum
    L13_27 = L11_25.nLeftActiveCount
    L10_24.DelGroupBuff(3276, 1)
    for _FORV_17_ = 1, L12_26 do
      L10_24.AddBuff(L10_24.dwID, L10_24.nLevel, 3276, 1, L13_27)
    end
  end
end
function OnEarlyWarning(A0_28, A1_29)
end
function OnChannelBegin(A0_30)
  local L1_31
end
function OnChannelEnd(A0_32, A1_33)
end
