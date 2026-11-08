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
function CanCast(A0_3, A1_4)
  return A1_4
end
function OnSkillLevelUp(A0_5, A1_6)
end
function OnSkillForgotten(A0_7, A1_8)
end
function Apply(A0_9, A1_10)
  if not GetPlayer(A0_9) then
    return
  end
  RemoteCallToClient(GetPlayer(A0_9).dwID, "OnSkillReplace", 18640, 18654, 1, 18640)
end
function UnApply(A0_11)
  if not GetPlayer(A0_11) then
    return
  end
  RemoteCallToClient(GetPlayer(A0_11).dwID, "OnSkillReplace", 18654, 18640, 1, 18654)
end
function OnRemove(A0_12, A1_13, A2_14, A3_15, A4_16, A5_17, A6_18, A7_19, A8_20, A9_21)
end
