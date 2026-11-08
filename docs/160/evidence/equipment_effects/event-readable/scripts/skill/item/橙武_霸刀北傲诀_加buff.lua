Include("scripts/Include/Skill.lh")
tSkillData = {}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  if L1_1 >= 8 then
    A0_0.bIgnorePrepareState = true
    L1_1 = A0_0.AddAttribute
    L1_1(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/item/OrangeWeaponSceneEntry.lua", 0)
  end
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 1157, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 2608, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 2853, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CALL_BUFF, 11376, L1_1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/item/橙武_霸刀北傲诀_加buff.lua", 0)
  A0_0.AddSlowCheckSelfBuff(2584, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.GREATER_EQUAL)
  A0_0.BindBuff(1, 2584, 1)
  if L1_1 >= 8 then
    A0_0.SetNormalCoolDown(1, 5079)
  end
  A0_0.nMaxRadius = 10 * LENGTH_BASE
  A0_0.nAngleRange = 256
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
end
function Apply(A0_6)
  local L1_7, L2_8, L3_9, L4_10, L5_11, L6_12
  L1_7 = GetPlayer
  L2_8 = A0_6
  L1_7 = L1_7(L2_8)
  if not L1_7 then
    return
  end
  L2_8 = L1_7.nMaxRage
  L1_7.nCurrentRage = L2_8
  L2_8 = L1_7.nMaxSunEnergy
  L1_7.nCurrentSunEnergy = L2_8
  L2_8 = L1_7.nMaxEnergy
  L1_7.nCurrentEnergy = L2_8
  L2_8 = L1_7.ClearCDTime
  L2_8(L3_9)
  L2_8 = L1_7.ClearCDTime
  L2_8(L3_9)
  L2_8 = L1_7.ClearCDTime
  L2_8(L3_9)
  L2_8 = nil
  for L6_12 = 1, 9 do
    L2_8 = L1_7.GetBuff(11376, L6_12)
    if L2_8 then
      break
    end
  end
  if L2_8 then
    L2_8.nCustomValue = 3
    if not L3_9 then
      L3_9(L4_10, L5_11)
    end
  end
  L6_12 = 34753
  L3_9(L4_10, L5_11, L6_12, 1)
  L6_12 = 42428
  L3_9(L4_10, L5_11, L6_12, 8)
end
function UnApply(A0_13)
  local L1_14
end
