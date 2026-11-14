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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_DEST_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT_WITH_PARAM, "skill/item/橙武_明教T_加BUFF.lua", L1_1)
  A0_0.AddSlowCheckSelfBuff(2584, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.GREATER_EQUAL)
  A0_0.AddSlowCheckSelfBuff(7913, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(7049, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(10864, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(7525, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(7561, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(9982, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(4964, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(11594, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(13096, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(13260, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_0.AddSlowCheckSelfBuff(14341, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
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
  if GetPlayer(A0_6) and GetPlayer(A0_6).nSkillPlatformType ~= SKILL_PLATFORM_TYPE.MOBILE then
    GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 4931, A1_7)
  end
  GetPlayer(A0_6).ClearCDTime(508)
  GetPlayer(A0_6).ClearCDTime(505)
  GetPlayer(A0_6).ClearCDTime(2591)
end
function UnApply(A0_8)
  local L1_9
end
