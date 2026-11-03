Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    nMP = 519,
    nSpunkAttackPower = 268,
    nNeHit = 8,
    nMagicDefence = 25,
    nLunarCritical = 36,
    DecriticalDamagePowerBase = 25
  },
  {
    nMP = 725,
    nSpunkAttackPower = 372,
    nNeHit = 14,
    nMagicDefence = 35,
    nLunarCritical = 50,
    DecriticalDamagePowerBase = 44
  },
  {
    nMP = 1101,
    nSpunkAttackPower = 564,
    nNeHit = 22,
    nMagicDefence = 54,
    nLunarCritical = 76,
    DecriticalDamagePowerBase = 70
  },
  {
    nMP = 1994,
    nSpunkAttackPower = 754,
    nNeHit = 31,
    nMagicDefence = 73,
    nLunarCritical = 102,
    DecriticalDamagePowerBase = 95
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  },
  {
    nMP = 519,
    nSpunkAttackPower = 268,
    nNeHit = 8,
    nMagicDefence = 25,
    nLunarCritical = 36,
    DecriticalDamagePowerBase = 25
  },
  {
    nMP = 725,
    nSpunkAttackPower = 372,
    nNeHit = 14,
    nMagicDefence = 35,
    nLunarCritical = 50,
    DecriticalDamagePowerBase = 44
  },
  {
    nMP = 1101,
    nSpunkAttackPower = 564,
    nNeHit = 22,
    nMagicDefence = 54,
    nLunarCritical = 76,
    DecriticalDamagePowerBase = 70
  },
  {
    nMP = 1994,
    nSpunkAttackPower = 754,
    nNeHit = 31,
    nMagicDefence = 73,
    nLunarCritical = 102,
    DecriticalDamagePowerBase = 95
  },
  {
    nMP = 5982,
    nSpunkAttackPower = 2282,
    nNeHit = 39,
    nMagicDefence = 219,
    nLunarCritical = 308,
    DecriticalDamagePowerBase = 120
  }
}
tSkillHuajinData = {
  {DecriticalDamagePowerBase = 18},
  {DecriticalDamagePowerBase = 32},
  {DecriticalDamagePowerBase = 51},
  {DecriticalDamagePowerBase = 69},
  {DecriticalDamagePowerBase = 87},
  {DecriticalDamagePowerBase = 106},
  {DecriticalDamagePowerBase = 124},
  {DecriticalDamagePowerBase = 143},
  {DecriticalDamagePowerBase = 161},
  {DecriticalDamagePowerBase = 356},
  {DecriticalDamagePowerBase = 782},
  {DecriticalDamagePowerBase = 1725}
}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L1_1].nMP / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMP / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STOP_MAKE_QI_CONTROL_CANCEL, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_CONTROL_COUNT, 6, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 9, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L1_1].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LUNAR_CRITICAL_STRIKE, tSkillData[L1_1].nLunarCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L1_1].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_ATTACK_POWER_COF, 737, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_CRITICAL_STRIKE_COF, 31, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10447], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_ENERGY, tSkillKungfuConst.LOGIC.QI[10447].MAX, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.QI_ENERGY_REPLENISH, tSkillKungfuConst.LOGIC.QI[10447].REPLENISH, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2176, 1)
  AdditionalAttribute(A0_0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NO_LIMIT_CHANGE_SKILL_ICON, 14137, 14064)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NO_LIMIT_CHANGE_SKILL_ICON, 14300, 14064)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NO_LIMIT_CHANGE_SKILL_ICON, 14303, 14064)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/长歌/套路及子技能/内功_莫问.lua", 0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMount() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.LearnSkillLevel(14087, A0_4.dwLevel, A1_5.dwID)
end
function Apply(A0_6)
  local L1_7, L2_8, L3_9, L4_10, L5_11, L6_12, L7_13
  L1_7 = GetPlayer
  L2_8 = A0_6
  L1_7 = L1_7(L2_8)
  if not L1_7 then
    return
  end
  L2_8 = L1_7.ForgetSkill
  L3_9 = 14164
  L2_8(L3_9)
  L2_8 = L1_7.GetSkillLevel
  L3_9 = 14064
  L2_8 = L2_8(L3_9)
  L3_9 = L1_7.LearnSkillLevel
  L4_10 = 45730
  L5_11 = 1
  L6_12 = L1_7.dwID
  L3_9(L4_10, L5_11, L6_12)
  L3_9 = L1_7.AddBuff
  L4_10 = L1_7.dwID
  L5_11 = L1_7.nLevel
  L6_12 = 14275
  L7_13 = 1
  L3_9(L4_10, L5_11, L6_12, L7_13)
  L1_7.bSurplusAutoCast = false
  L1_7.bSurplusAutoReplenish = false
  L3_9 = L1_7.GetBuff
  L4_10 = 9377
  L5_11 = 0
  L3_9 = L3_9(L4_10, L5_11)
  if L3_9 then
    L3_9 = L1_7.DelBuffByID
    L4_10 = 9377
    L3_9(L4_10)
  end
  L3_9 = L1_7.GetBuff
  L4_10 = 31441
  L5_11 = 1
  L3_9 = L3_9(L4_10, L5_11)
  if L3_9 then
    L3_9 = L1_7.DelBuff
    L4_10 = 31441
    L5_11 = 1
    L3_9(L4_10, L5_11)
  end
  L3_9 = L1_7.GetSkillLevel
  L4_10 = 14070
  L3_9 = L3_9(L4_10)
  if L3_9 ~= 0 then
    L4_10 = L1_7.LearnSkillLevel
    L5_11 = 14230
    L6_12 = L3_9
    L7_13 = L1_7.dwID
    L4_10(L5_11, L6_12, L7_13)
    L4_10 = RemoteCallToClient
    L5_11 = L1_7.dwID
    L6_12 = "OnSkillReplace"
    L7_13 = 15090
    L4_10(L5_11, L6_12, L7_13, 14230, L3_9, 15090)
  end
  L4_10 = L1_7.GetSkillLevel
  L5_11 = 14065
  L4_10 = L4_10(L5_11)
  if L4_10 ~= 0 then
    L5_11 = RemoteCallToClient
    L6_12 = L1_7.dwID
    L7_13 = "OnActionBarSkillReplace"
    L5_11(L6_12, L7_13, 14138, 14065, L4_10)
  end
  L5_11 = L1_7.GetSkillLevel
  L6_12 = 14066
  L5_11 = L5_11(L6_12)
  if L5_11 ~= 0 then
    L6_12 = RemoteCallToClient
    L7_13 = L1_7.dwID
    L6_12(L7_13, "OnActionBarSkillReplace", 14139, 14066, L5_11)
  end
  L6_12 = L1_7.GetSkillLevel
  L7_13 = 14067
  L6_12 = L6_12(L7_13)
  if L6_12 ~= 0 then
    L7_13 = RemoteCallToClient
    L7_13(L1_7.dwID, "OnActionBarSkillReplace", 14140, 14067, L6_12)
    L7_13 = RemoteCallToClient
    L7_13(L1_7.dwID, "OnActionBarSkillReplace", 14301, 14299, L6_12)
  end
  L7_13 = L1_7.GetSkillLevel
  L7_13 = L7_13(14068)
  if L7_13 ~= 0 then
    RemoteCallToClient(L1_7.dwID, "OnActionBarSkillReplace", 14141, 14068, L7_13)
  end
  if L1_7.IsHaveBuff(9319, 1) then
    L1_7.DelBuff(9319, 1)
    L1_7.AddBuff(L1_7.dwID, L1_7.nLevel, 9319, 1)
  end
  L1_7.AddBuff(L1_7.dwID, L1_7.nLevel, 33608, 1)
end
function UnApply(A0_14)
  if not GetPlayer(A0_14) then
    return
  end
  GetPlayer(A0_14).DelBuff(33608, 1)
  if GetPlayer(A0_14).GetBuff(9641, 1) then
    GetPlayer(A0_14).DelBuff(9641, 1)
  end
  if GetPlayer(A0_14).dwShapeShiftID == 0 then
    GetPlayer(A0_14).DelBuff(9320, 1)
  end
  for _FORV_5_ = 1, 6 do
    if GetPlayer(A0_14).GetBuff(9992 + _FORV_5_, 1) then
      GetPlayer(A0_14).DelBuff(9992 + _FORV_5_, 1)
    end
  end
  if GetPlayer(A0_14).GetBuff(9322, 1) then
    GetPlayer(A0_14).DelBuff(9322, 1)
  end
  if GetPlayer(A0_14).GetBuff(9319, 1) then
    GetPlayer(A0_14).DelBuff(9319, 1)
  end
  if GetPlayer(A0_14).GetBuff(31441, 1) then
    GetPlayer(A0_14).DelBuff(31441, 1)
  end
end
function OnTimer(A0_15, A1_16, A2_17)
end
