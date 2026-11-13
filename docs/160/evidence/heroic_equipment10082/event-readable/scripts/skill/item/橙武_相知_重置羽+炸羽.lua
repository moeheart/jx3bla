Include("scripts/Include/Skill.lh")
tSkillData = {}
function GetSkillLevelData(A0_0)
  if A0_0.dwLevel >= 1 then
    A0_0.bIgnorePrepareState = true
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/item/OrangeWeaponSceneEntry.lua", 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.CLEAR_COOL_DOWN, 1698, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/item/橙武_相知_重置羽+炸羽.lua", 0)
  A0_0.BindBuff(1, 10193, A0_0.dwLevel + 6)
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
  if not GetPlayer(A0_5) then
    return
  end
  GetPlayer(A0_5).ClearCDTime(895)
  GetPlayer(A0_5).ClearCDTime(1698)
  GetPlayer(A0_5).ClearCDTime(3060)
  GetPlayer(A0_5).ClearCDTime(1258)
  GetPlayer(A0_5).ClearCDTime(2842)
  GetPlayer(A0_5).ClearCDTime(1846)
  GetPlayer(A0_5).ClearCDTime(918)
  GetPlayer(A0_5).ClearCDTime(2157)
  GetPlayer(A0_5).ClearCDTime(3250)
  GetPlayer(A0_5).ClearCDTime(3265)
  GetPlayer(A0_5).ClearCDTime(3253)
  GetPlayer(A0_5).ClearCDTime(3252)
  GetPlayer(A0_5).ClearCDTime(3277)
  GetPlayer(A0_5).ClearCDTime(3278)
  GetPlayer(A0_5).ClearCDTime(3264)
  GetPlayer(A0_5).ClearCDTime(3324)
  GetPlayer(A0_5).ClearCDTime(3430)
  GetPlayer(A0_5).ClearCDTime(3431)
  GetPlayer(A0_5).ClearCDTime(5028)
  GetPlayer(A0_5).ClearCDTime(5055)
end
function UnApply(A0_6)
  local L1_7
end
