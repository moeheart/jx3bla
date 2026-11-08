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
  local L2_12, L3_13, L4_14, L5_15
  L2_12 = GetPlayer
  L3_13 = A0_10
  L2_12 = L2_12(L3_13)
  if not L2_12 then
    return
  end
  L3_13 = L2_12.ClearCDTime
  L4_14 = 2822
  L3_13(L4_14)
  L3_13 = 100
  L4_14 = L2_12.GetSkillLevel
  L5_15 = 14834
  L4_14 = L4_14(L5_15)
  if L4_14 == 1 then
    L3_13 = 200
  end
  L4_14 = L2_12.IsHaveBuffByOwner
  L5_15 = 1916
  L4_14 = L4_14(L5_15, 0, L2_12.dwID)
  if not L4_14 then
    L4_14 = L2_12.IsHaveBuffByOwner
    L5_15 = 34903
    L4_14 = L4_14(L5_15, 0, L2_12.dwID)
  elseif L4_14 then
    return
  end
  L4_14 = L2_12.IsHaveBuff
  L5_15 = 17918
  L4_14 = L4_14(L5_15, 0)
  if not L4_14 then
    L4_14 = L2_12.GetSkillLevel
    L5_15 = 34580
    L4_14 = L4_14(L5_15)
    if L4_14 == 1 then
      L4_14 = L2_12.DelBuffByID
      L5_15 = 34557
      L4_14(L5_15)
      L4_14 = 96
      L5_15 = 0
      if L2_12.IsHaveBuff(17918, 1) then
        L2_12.AddBuff(L2_12.dwID, L2_12.nLevel, 12783, 1, L4_14, 16)
        L5_15 = 12783
      else
        L2_12.AddBuff(L2_12.dwID, L2_12.nLevel, 12504, 1, L4_14, 16)
        L5_15 = 12504
      end
      L2_12.nCurrentRage = 5
      if L2_12.GetBuff(L5_15, 1) then
        L2_12.SetBuffLeftActiveCount(L2_12.GetBuff(L5_15, 1).nIndex, math.min(L2_12.GetBuff(L5_15, 1).nLeftActiveCount + 7, L3_13))
      end
    else
      L4_14 = L2_12.IsHaveBuff
      L5_15 = 12504
      L4_14 = L4_14(L5_15, 1)
      if not L4_14 then
        L4_14 = L2_12.IsHaveBuff
        L5_15 = 12783
        L4_14 = L4_14(L5_15, 1)
        if not L4_14 then
          L4_14 = 96
          L5_15 = 0
          if L2_12.IsHaveBuff(17918, 1) then
            L2_12.AddBuff(L2_12.dwID, L2_12.nLevel, 12783, 1, L4_14, 16)
            L5_15 = 12783
          else
            L2_12.AddBuff(L2_12.dwID, L2_12.nLevel, 12504, 1, L4_14, 16)
            L5_15 = 12504
          end
          L2_12.nCurrentRage = 5
          if L2_12.GetBuff(L5_15, 1) then
            L2_12.SetBuffLeftActiveCount(L2_12.GetBuff(L5_15, 1).nIndex, math.min(L2_12.GetBuff(L5_15, 1).nLeftActiveCount + 7, L3_13))
          end
        end
      else
        L4_14 = L2_12.AddBuff
        L5_15 = L2_12.dwID
        L4_14(L5_15, L2_12.nLevel, 19987, 1, 4)
        L4_14 = L2_12.GetSkillLevel
        L5_15 = 14834
        L4_14 = L4_14(L5_15)
        if L4_14 == 1 then
          L4_14 = nil
          L5_15 = L2_12.GetBuff
          L5_15 = L5_15(12504, 1)
          L4_14 = L5_15.nLeftActiveCount
          L2_12.SetTimer(12, "scripts/skill/纯阳/套路及子技能/气纯瞬间满气剑.lua", L4_14, 1)
        else
          L4_14 = L2_12.SetTimer
          L5_15 = 12
          L4_14(L5_15, "scripts/skill/纯阳/北冥剑气_万世不竭释放.lua", 1, 1)
        end
      end
    end
  end
end
function UnApply(A0_16)
  local L1_17
end
function OnRemove(A0_18, A1_19, A2_20, A3_21, A4_22, A5_23, A6_24, A7_25, A8_26, A9_27)
end
function OnEarlyWarning(A0_28, A1_29)
end
function OnTimer(A0_30, A1_31, A2_32)
  local L3_33, L4_34, L5_35
  L3_33 = A0_30.DelBuff
  L4_34 = 12783
  L5_35 = 1
  L3_33(L4_34, L5_35)
  L3_33 = A0_30.DelBuff
  L4_34 = 12504
  L5_35 = 1
  L3_33(L4_34, L5_35)
  if A1_31 and A2_32 == 1 then
    L3_33 = A0_30.SetTimer
    L4_34 = 5
    L5_35 = "scripts/skill/纯阳/套路及子技能/气纯瞬间满气剑.lua"
    L3_33(L4_34, L5_35, A1_31, 2)
  elseif A1_31 and A2_32 == 2 then
    L3_33 = A1_31 + 96
    L4_34 = 100
    L5_35 = A0_30.GetSkillLevel
    L5_35 = L5_35(14834)
    if L5_35 == 1 then
      L4_34 = 200
    end
    L5_35 = 0
    if A0_30.IsHaveBuff(17918, 1) then
      A0_30.AddBuff(A0_30.dwID, A0_30.nLevel, 12783, 1, L3_33, 16)
      L5_35 = 12783
    else
      A0_30.AddBuff(A0_30.dwID, A0_30.nLevel, 12504, 1, L3_33, 16)
      L5_35 = 12504
    end
    A0_30.nCurrentRage = 5
    if A0_30.GetBuff(L5_35, 1) then
      A0_30.SetBuffLeftActiveCount(A0_30.GetBuff(L5_35, 1).nIndex, math.min(A0_30.GetBuff(L5_35, 1).nLeftActiveCount + 7, L4_34))
    end
  end
end
