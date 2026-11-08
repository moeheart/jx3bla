Include("scripts/Include/Skill.lh")
tSkillData = {
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 600,
    nDamageRand = 8
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 750,
    nDamageRand = 16
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 850,
    nDamageRand = 23
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 950,
    nDamageRand = 31
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1050,
    nDamageRand = 39
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1070,
    nDamageRand = 47
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1090,
    nDamageRand = 55
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1110,
    nDamageRand = 62
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1130,
    nDamageRand = 70
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1150,
    nDamageRand = 78
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1170,
    nDamageRand = 86
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1232,
    nDamageRand = 94
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1310,
    nDamageRand = 101
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1388,
    nDamageRand = 109
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1466,
    nDamageRand = 117
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1544,
    nDamageRand = 125
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1622,
    nDamageRand = 133
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1700,
    nDamageRand = 140
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1778,
    nDamageRand = 148
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1856,
    nDamageRand = 156
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 1934,
    nDamageRand = 164
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2012,
    nDamageRand = 172
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2090,
    nDamageRand = 179
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2168,
    nDamageRand = 187
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2246,
    nDamageRand = 195
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2324,
    nDamageRand = 203
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2402,
    nDamageRand = 211
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2480,
    nDamageRand = 218
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2558,
    nDamageRand = 226
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2636,
    nDamageRand = 234
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2714,
    nDamageRand = 242
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2792,
    nDamageRand = 250
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2870,
    nDamageRand = 257
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 2948,
    nDamageRand = 265
  },
  {
    nAddRage = 0,
    nCostRage = 0,
    nDamageBase = 4646,
    nDamageRand = 273
  }
}
function GetSkillLevelData(A0_0)
  local L1_1, L2_2
  L1_1 = A0_0.dwLevel
  L2_2 = 10
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_DEST_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/纯阳/北冥剑气_万世不竭释放.lua", 0)
  A0_0.AddSlowCheckSelfBuff(34557, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.SetPublicCoolDown(16)
  A0_0.nMaxRadius = 20 * LENGTH_BASE
  A0_0.nAngleRange = 128
  A0_0.bFullAngleInAir = true
  A0_0.nBrokenRate = PERCENT_BASE
  return true
end
function CanCast(A0_3, A1_4)
  if A0_3.IsHaveBuff(17918, 1) then
    if not A0_3.IsHaveBuff(12783, 1) then
      return SKILL_RESULT_CODE.FAILED
    end
  elseif not A0_3.IsHaveBuff(12504, 1) then
    return SKILL_RESULT_CODE.FAILED
  end
  if A1_4 == SKILL_RESULT_CODE.SUCCESS then
  end
  return A1_4
end
function OnSkillLevelUp(A0_5, A1_6)
end
function Apply(A0_7, A1_8)
  local L2_9, L3_10, L4_11, L5_12, L6_13, L7_14
  L3_10 = IsPlayer
  L4_11 = A0_7
  L3_10 = L3_10(L4_11)
  if L3_10 then
    L3_10 = GetPlayer
    L4_11 = A0_7
    L3_10 = L3_10(L4_11)
    L2_9 = L3_10
    L3_10 = TARGET
    L3_10 = L3_10.PLAYER
    nType = L3_10
  else
    L3_10 = GetNpc
    L4_11 = A0_7
    L3_10 = L3_10(L4_11)
    L2_9 = L3_10
    L3_10 = TARGET
    L3_10 = L3_10.NPC
    nType = L3_10
  end
  if not L2_9 then
    return
  end
  L3_10 = GetPlayer
  L4_11 = A1_8
  L3_10 = L3_10(L4_11)
  if not L3_10 then
    return
  end
  L4_11 = L2_9.fCurrentLife64
  L5_12 = L2_9.fMaxLife64
  L4_11 = L4_11 / L5_12
  L5_12 = nil
  L6_13 = 1
  lv = L6_13
  L6_13 = L3_10.GetSkillLevel
  L7_14 = 34580
  L6_13 = L6_13(L7_14)
  if L6_13 == 1 then
    L6_13 = L3_10.IsHaveBuff
    L7_14 = 17918
    L6_13 = L6_13(L7_14, 1)
    if L6_13 then
      L6_13 = 12783
      buffid = L6_13
    else
      L6_13 = 12504
      buffid = L6_13
    end
    L6_13 = L3_10.GetBuff
    L7_14 = buffid
    L6_13 = L6_13(L7_14, 1)
    if L6_13 then
      L7_14 = L6_13.nLeftActiveCount
      L7_14 = L7_14 / 4
      L3_10.CastSkill(46142, L7_14, nType, L2_9.dwID)
    end
  end
  L6_13 = nil
  L7_14 = L3_10.GetSkillLevel
  L7_14 = L7_14(34580)
  if L7_14 == 1 then
    L6_13 = 38528
  else
    L6_13 = 22014
  end
  L7_14 = lv
  if L7_14 and L6_13 > 0 then
    L7_14 = L3_10.CastSkill
    L7_14(L6_13, lv, nType, L2_9.dwID)
  end
  L7_14 = L3_10.DelBuffByID
  L7_14(1916)
  L7_14 = L3_10.IsHaveBuffByOwner
  L7_14 = L7_14(1916, 0, L3_10.dwID)
  if not L7_14 then
    L7_14 = L3_10.DelBuffByID
    L7_14(34903)
  end
end
function UnApply(A0_15)
  local L1_16
end
function OnTimer(A0_17, A1_18, A2_19)
  local L3_20, L4_21, L5_22
  L3_20 = A0_17.DelBuff
  L4_21 = 12783
  L5_22 = 1
  L3_20(L4_21, L5_22)
  L3_20 = A0_17.DelBuff
  L4_21 = 12504
  L5_22 = 1
  L3_20(L4_21, L5_22)
  if A1_18 == 1 and A2_19 == 1 then
    L3_20 = A0_17.SetTimer
    L4_21 = 5
    L5_22 = "scripts/skill/纯阳/北冥剑气_万世不竭释放.lua"
    L3_20(L4_21, L5_22, 1, 2)
  elseif A1_18 == 1 and A2_19 == 2 then
    L3_20 = 96
    L4_21 = 100
    L5_22 = A0_17.GetSkillLevel
    L5_22 = L5_22(14834)
    if L5_22 == 1 then
      L4_21 = 200
    end
    L5_22 = 0
    if A0_17.IsHaveBuff(17918, 1) then
      A0_17.AddBuff(A0_17.dwID, A0_17.nLevel, 12783, 1, L3_20, 16)
      L5_22 = 12783
    else
      A0_17.AddBuff(A0_17.dwID, A0_17.nLevel, 12504, 1, L3_20, 16)
      L5_22 = 12504
    end
    A0_17.nCurrentRage = 5
    if A0_17.GetBuff(L5_22, 1) then
      A0_17.SetBuffLeftActiveCount(A0_17.GetBuff(L5_22, 1).nIndex, math.min(A0_17.GetBuff(L5_22, 1).nLeftActiveCount + 7, L4_21))
    end
  end
end
