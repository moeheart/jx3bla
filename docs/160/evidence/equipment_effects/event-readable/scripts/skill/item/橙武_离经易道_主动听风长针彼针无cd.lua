Include("scripts/Include/Skill.lh")
tSkillData = {}
function GetSkillLevelData(A0_0)
  if A0_0.dwLevel >= 1 then
    A0_0.bIgnorePrepareState = true
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/item/OrangeWeaponSceneEntry.lua", 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 446, 0)
  A0_0.BindBuff(1, 12770, A0_0.dwLevel + 6)
  A0_0.SetNormalCoolDown(1, 5079)
  A0_0.nMaxRadius = 10 * LENGTH_BASE
  A0_0.nAngleRange = 256
  return true
end
function CanCast(A0_1, A1_2)
  return A1_2
end
function OnSkillLevelUp(A0_3, A1_4)
end
function Apply(A0_5)
  local L1_6
end
function UnApply(A0_7)
  local L1_8
end
