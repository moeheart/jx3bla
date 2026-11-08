local L0_0, L1_1, L2_2, L3_3, L4_4, L5_5, L6_6, L7_7, L8_8, L9_9
L0_0 = Include
L1_1 = "scripts/Include/Skill.lh"
L0_0(L1_1)
L0_0 = Include
L1_1 = "scripts/player/include/Kungfu2ArenaType.lh"
L0_0(L1_1)
L0_0 = {L1_1, L2_2}
L1_1 = {}
L1_1.nDamageBase = 13524
L2_2 = {}
L2_2.nDamageBase = 19745
function L1_1(A0_10)
  local L1_11
  L1_11 = A0_10.dwLevel
  A0_10.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_DEST_NOT_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT_WITH_PARAM, "skill/装备/苍生铸世赛季输出护手固定伤害.lua", L1_11)
  A0_10.AddSlowCheckSelfBuff(15453, 0, BUFF_COMPARE_FLAG.EQUAL, 0, BUFF_COMPARE_FLAG.EQUAL)
  A0_10.bIgnorePrepareState = true
  A0_10.bIgnorePrepareState = true
  A0_10.nMaxRadius = 30 * LENGTH_BASE
  A0_10.nAngleRange = 256
  A0_10.nTargetCountLimit = 1
  A0_10.nChannelInterval = 0
  return true
end
GetSkillLevelData = L1_1
L1_1 = {}
L2_2 = {}
L3_3 = {}
L4_4 = {}
L5_5 = {}
for L9_9, _FORV_10_ in L6_6(L7_7) do
  if _FORV_10_.adaptiveType == 1 then
    table.insert(L1_1, L9_9)
  elseif _FORV_10_.adaptiveType == 2 then
    table.insert(L2_2, L9_9)
  elseif _FORV_10_.adaptiveType == 3 then
    table.insert(L3_3, L9_9)
  elseif _FORV_10_.adaptiveType == 4 then
    table.insert(L4_4, L9_9)
  else
    table.insert(L5_5, L9_9)
  end
end
CanCast = L6_6
OnSkillLevelUp = L6_6
OnSkillForgotten = L6_6
Apply = L6_6
UnApply = L6_6
OnRemove = L6_6
OnEarlyWarning = L6_6
