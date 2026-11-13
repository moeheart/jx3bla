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
  if L1_1 >= 8 then
    A0_0.SetNormalCoolDown(1, 5079)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CALL_BUFF, 10192, L1_1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/item/橙武_莫问_加BUFF.lua", 0)
  A0_0.AddSlowCheckSelfBuff(2584, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.GREATER_EQUAL)
  A0_0.BindBuff(1, 2584, 1)
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
  if not GetPlayer(A0_6) then
    return
  end
  if GetPlayer(A0_6).GetBuffByAppendType(10192) and GetPlayer(A0_6).GetBuffByAppendType(10192).nStackNum < 3 then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 10192, GetPlayer(A0_6).GetBuffByAppendType(10192).nLevel, 0, 0, 3 - GetPlayer(A0_6).GetBuffByAppendType(10192).nStackNum)
  end
  GetPlayer(A0_6).ClearCDTime(918)
  GetPlayer(A0_6).ClearCDTime(3324)
  GetPlayer(A0_6).ClearCDTime(5055)
  GetPlayer(A0_6).ClearCDTime(895)
  GetPlayer(A0_6).ClearCDTime(1698)
end
function UnApply(A0_7)
  local L1_8
end
