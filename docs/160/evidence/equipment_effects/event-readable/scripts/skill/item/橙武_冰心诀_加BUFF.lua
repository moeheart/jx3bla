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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CALL_BUFF, 18511, L1_1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 123, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 451, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 3050, 0)
  A0_0.AddSlowCheckSelfBuff(2584, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.GREATER_EQUAL)
  A0_0.BindBuff(1, 2584, 1)
  if L1_1 >= 8 then
    A0_0.SetNormalCoolDown(1, 5079)
  end
  A0_0.nMaxRadius = 25 * LENGTH_BASE
  A0_0.nAngleRange = 256
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
end
function Apply(A0_6)
  local L1_7
end
function UnApply(A0_8)
  local L1_9
end
