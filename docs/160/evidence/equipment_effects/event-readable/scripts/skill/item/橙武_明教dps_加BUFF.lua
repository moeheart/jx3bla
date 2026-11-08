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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_DEST_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT_WITH_PARAM, "skill/item/橙武_明教dps_加BUFF.lua", L1_1)
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
function Apply(A0_6, A1_7)
  local L2_8, L3_9, L4_10, L5_11, L6_12
  L2_8 = GetPlayer
  L2_8 = L2_8(L3_9)
  if L2_8 then
    if L3_9 ~= L4_10 then
      for L6_12 = 1, 9 do
        L2_8.DelGroupBuff(4930, L6_12)
      end
      L6_12 = 4930
      L3_9(L4_10, L5_11, L6_12, A1_7, 0, 0, 4)
    end
  end
end
function UnApply(A0_13)
  local L1_14
end
