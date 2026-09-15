Include("scripts/Include/Skill.lh")
Include("scripts/skill/装备/治疗全能属性转治疗量.lua")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    nMaxMana = 518,
    nTherapy = 828,
    nLifeReplenish = 22,
    nMagicDefence = 32,
    DecriticalDamagePowerBase = 25
  },
  {
    nMaxMana = 723,
    nTherapy = 1152,
    nLifeReplenish = 31,
    nMagicDefence = 44,
    DecriticalDamagePowerBase = 44
  },
  {
    nMaxMana = 1098,
    nTherapy = 1747,
    nLifeReplenish = 48,
    nMagicDefence = 68,
    DecriticalDamagePowerBase = 70
  },
  {
    nMaxMana = 1990,
    nTherapy = 2342,
    nLifeReplenish = 65,
    nMagicDefence = 91,
    DecriticalDamagePowerBase = 95
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
    DecriticalDamagePowerBase = 120
  },
  {
    nMaxMana = 518,
    nTherapy = 828,
    nLifeReplenish = 22,
    nMagicDefence = 32,
    DecriticalDamagePowerBase = 25
  },
  {
    nMaxMana = 723,
    nTherapy = 1152,
    nLifeReplenish = 31,
    nMagicDefence = 44,
    DecriticalDamagePowerBase = 44
  },
  {
    nMaxMana = 1098,
    nTherapy = 1747,
    nLifeReplenish = 48,
    nMagicDefence = 68,
    DecriticalDamagePowerBase = 70
  },
  {
    nMaxMana = 1990,
    nTherapy = 2342,
    nLifeReplenish = 65,
    nMagicDefence = 91,
    DecriticalDamagePowerBase = 95
  },
  {
    nMaxMana = 5970,
    nTherapy = 7049,
    nLifeReplenish = 195,
    nMagicDefence = 273,
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.THERAPY, 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  AdditionalAttribute(A0_0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L1_1].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_ENERGY, tSkillKungfuConst.LOGIC.QI[10448].MAX, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.QI_ENERGY_REPLENISH, tSkillKungfuConst.LOGIC.QI[10448].REPLENISH, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STOP_MAKE_QI_CONTROL_CANCEL, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_CONTROL_COUNT, 6, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.THERAPY_POWER_BASE, tSkillData[L1_1].nTherapy, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L1_1].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LIFE_REPLENISH_EXT, tSkillData[L1_1].nLifeReplenish, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_THERAPY_POWER_COF, 707, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_CRITICAL_STRIKE_COF, 61, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NO_LIMIT_CHANGE_SKILL_ICON, 14064, 14137)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NO_LIMIT_CHANGE_SKILL_ICON, 14298, 14137)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/长歌/套路及子技能/内功_相知.lua", 0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMount() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.LearnSkillLevel(14088, A0_4.dwLevel, A1_5.dwID)
end
function Apply(A0_6)
  local L1_7, L2_8, L3_9, L4_10, L5_11, L6_12
  L1_7 = GetPlayer
  L2_8 = A0_6
  L1_7 = L1_7(L2_8)
  if not L1_7 then
    return
  end
  L2_8 = L1_7.AddBuff
  L3_9 = L1_7.dwID
  L4_10 = L1_7.nLevel
  L5_11 = 14275
  L6_12 = 1
  L2_8(L3_9, L4_10, L5_11, L6_12)
  L2_8 = PVXTherapyAllRound2TherapyPowerBase
  L3_9 = L1_7
  L2_8(L3_9)
  L2_8 = L1_7.GetBuff
  L3_9 = 9377
  L4_10 = 0
  L2_8 = L2_8(L3_9, L4_10)
  if L2_8 then
    L2_8 = L1_7.DelBuffByID
    L3_9 = 9377
    L2_8(L3_9)
  end
  L2_8 = L1_7.LearnSkillLevel
  L3_9 = 33116
  L4_10 = 1
  L5_11 = L1_7.dwID
  L2_8(L3_9, L4_10, L5_11)
  L2_8 = L1_7.GetBuff
  L3_9 = 31441
  L4_10 = 1
  L2_8 = L2_8(L3_9, L4_10)
  if L2_8 then
    L2_8 = L1_7.DelBuff
    L3_9 = 31441
    L4_10 = 1
    L2_8(L3_9, L4_10)
  end
  L2_8 = L1_7.GetSkillLevel
  L3_9 = 14070
  L2_8 = L2_8(L3_9)
  if L2_8 ~= 0 then
    L3_9 = L1_7.LearnSkillLevel
    L4_10 = 15090
    L5_11 = L2_8
    L6_12 = L1_7.dwID
    L3_9(L4_10, L5_11, L6_12)
    L3_9 = RemoteCallToClient
    L4_10 = L1_7.dwID
    L5_11 = "OnSkillReplace"
    L6_12 = 14230
    L3_9(L4_10, L5_11, L6_12, 15090, L2_8, 14230)
  end
  L3_9 = L1_7.GetSkillLevel
  L4_10 = 14138
  L3_9 = L3_9(L4_10)
  if L3_9 ~= 0 then
    L4_10 = RemoteCallToClient
    L5_11 = L1_7.dwID
    L6_12 = "OnActionBarSkillReplace"
    L4_10(L5_11, L6_12, 14065, 14138, L3_9)
  end
  L4_10 = L1_7.GetSkillLevel
  L5_11 = 14139
  L4_10 = L4_10(L5_11)
  if L4_10 ~= 0 then
    L5_11 = RemoteCallToClient
    L6_12 = L1_7.dwID
    L5_11(L6_12, "OnActionBarSkillReplace", 14066, 14139, L4_10)
  end
  L5_11 = L1_7.GetSkillLevel
  L6_12 = 14140
  L5_11 = L5_11(L6_12)
  if L5_11 ~= 0 then
    L6_12 = RemoteCallToClient
    L6_12(L1_7.dwID, "OnActionBarSkillReplace", 14067, 14140, L5_11)
    L6_12 = RemoteCallToClient
    L6_12(L1_7.dwID, "OnActionBarSkillReplace", 14299, 14301, L5_11)
  end
  L6_12 = L1_7.GetSkillLevel
  L6_12 = L6_12(14141)
  if L6_12 ~= 0 then
    RemoteCallToClient(L1_7.dwID, "OnActionBarSkillReplace", 14068, 14141, L6_12)
  end
  L1_7.AddBuff(L1_7.dwID, L1_7.nLevel, 33608, 1)
end
function UnApply(A0_13)
  if not GetPlayer(A0_13) then
    return
  end
  GetPlayer(A0_13).DelBuff(33608, 1)
  if GetPlayer(A0_13).GetBuff(9641, 1) then
    GetPlayer(A0_13).DelBuff(9641, 1)
  end
  if GetPlayer(A0_13).dwShapeShiftID == 0 then
    GetPlayer(A0_13).DelBuff(9320, 1)
  end
  for _FORV_5_ = 1, 6 do
    if GetPlayer(A0_13).GetBuff(9992 + _FORV_5_, 1) then
      GetPlayer(A0_13).DelBuff(9992 + _FORV_5_, 1)
    end
  end
  if GetPlayer(A0_13).GetBuff(9321, 1) then
    GetPlayer(A0_13).DelBuff(9321, 1)
  end
  if GetPlayer(A0_13).GetBuff(9319, 1) then
    GetPlayer(A0_13).DelBuff(9319, 1)
  end
  GetPlayer(A0_13).DelGroupBuff(24153, 1)
  GetPlayer(A0_13).DelGroupBuff(31569, 1)
  GetPlayer(A0_13).DelGroupBuff(30677, 1)
  if GetPlayer(A0_13).GetBuff(31441, 1) then
    GetPlayer(A0_13).DelBuff(31441, 1)
  end
end
function OnTimer(A0_14, A1_15, A2_16)
end
