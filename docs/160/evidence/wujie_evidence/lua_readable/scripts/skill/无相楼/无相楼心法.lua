Include("scripts/Include/Skill.lh")
Include("scripts/Include/NewSkill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 703,
    nSpunkAttackPower = 307,
    nNeutralHit = 10,
    nLunarCritical = 4,
    nMagicDefence = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 982,
    nSpunkAttackPower = 425,
    nNeutralHit = 18,
    nLunarCritical = 6,
    nMagicDefence = 26
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1491,
    nSpunkAttackPower = 646,
    nNeutralHit = 28,
    nLunarCritical = 8,
    nMagicDefence = 40
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2000,
    nSpunkAttackPower = 863,
    nNeutralHit = 39,
    nLunarCritical = 11,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2611,
    nNeutralHit = 49,
    nLunarCritical = 34,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2611,
    nNeutralHit = 49,
    nLunarCritical = 34,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2611,
    nNeutralHit = 49,
    nLunarCritical = 34,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2611,
    nNeutralHit = 49,
    nLunarCritical = 34,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2611,
    nNeutralHit = 49,
    nLunarCritical = 34,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2611,
    nNeutralHit = 49,
    nLunarCritical = 34,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 703,
    nSpunkAttackPower = 307,
    nNeutralHit = 10,
    nLunarCritical = 4,
    nMagicDefence = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 982,
    nSpunkAttackPower = 425,
    nNeutralHit = 18,
    nLunarCritical = 6,
    nMagicDefence = 26
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1491,
    nSpunkAttackPower = 646,
    nNeutralHit = 28,
    nLunarCritical = 8,
    nMagicDefence = 40
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2000,
    nSpunkAttackPower = 863,
    nNeutralHit = 39,
    nLunarCritical = 11,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2611,
    nNeutralHit = 49,
    nLunarCritical = 34,
    nMagicDefence = 164
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
  local L1_1, L2_2, L3_3
  L1_1 = false
  L2_2 = A0_0.dwLevel
  L3_3 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ADAPT_ATTRIBUTE_TYPE, 1, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_ENERGY, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ENERGY_REPLENISH, 1, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT_WITH_PARAM, "skill/无相楼/无相楼心法.lua", L3_3)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_ATTACK_POWER_COF, 717, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_CRITICAL_STRIKE_COF, 51, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LUNAR_CRITICAL_STRIKE, tSkillData[L3_3].nLunarCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10821], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5, A2_6)
  return A1_5
end
function OnSkillLevelUp(A0_7, A1_8)
  if not A1_8.GetKungfuMountID() then
    A1_8.MountKungfu(A0_7.dwSkillID, A0_7.dwLevel)
  end
  A1_8.LearnSkillLevel(41117, A0_7.dwLevel, A1_8.dwID)
end
function OnSkillForgotten(A0_9, A1_10)
end
function Apply(A0_11, A1_12, A2_13)
  if GetPlayer(A0_11) then
    GetPlayer(A0_11).AddBuff(GetPlayer(A0_11).dwID, GetPlayer(A0_11).nLevel, 14275, 1)
    GetPlayer(A0_11).bSurplusAutoCast = false
    GetPlayer(A0_11).bSurplusAutoReplenish = false
    if GetPlayer(A0_11).GetPet() then
      GetPlayer(A0_11).GetPet().Die()
    end
    GetPlayer(A0_11).LearnSkill(42730)
    GetPlayer(A0_11).LearnSkill(42722)
    GetPlayer(A0_11).LearnSkill(42723)
    GetPlayer(A0_11).LearnSkill(42725)
    GetPlayer(A0_11).LearnSkill(42726)
    GetPlayer(A0_11).LearnSkill(42727)
    GetPlayer(A0_11).LearnSkill(42728)
    if A1_12 == 14 then
      GetPlayer(A0_11).SetTimer(16, "scripts/skill/无相楼/无相楼心法.lua", 0, 0)
    end
  end
end
function UnApply(A0_14)
  if GetPlayer(A0_14) then
    if GetPlayer(A0_14).GetPet() then
      GetPlayer(A0_14).GetPet().Die()
    end
    GetPlayer(A0_14).DelBuff(31213, 1)
    GetPlayer(A0_14).DelBuff(31374, 1)
    GetPlayer(A0_14).DelBuff(32113, 1)
    for _FORV_6_, _FORV_7_ in pairs(tKLSkin_Buff) do
      GetPlayer(A0_14).DelBuff(_FORV_7_.dwBuffID, 1)
    end
    GetPlayer(A0_14).dwPuppetSkinID = 0
  end
end
function OnTimer(A0_15, A1_16, A2_17)
  local L3_18
  L3_18 = 31896
  for _FORV_8_, _FORV_9_ in pairs(tKLSkin_Buff) do
    A0_15.DelMultiGroupBuffByID(_FORV_9_.dwBuffID)
  end
  if A0_15.GetKungfuMountID() ~= 10821 then
    A0_15.dwPuppetSkinID = 0
    return
  end
  for _FORV_8_, _FORV_9_ in pairs(tKLSkin_Buff) do
    if A0_15.IsSkillSkinActive(_FORV_9_.dwSkinID) then
      L3_18 = _FORV_9_.dwBuffID
      break
    end
  end
  A0_15.AddBuff(A0_15.dwID, A0_15.nLevel, L3_18, 1)
  A0_15.dwPuppetSkinID = _FORV_9_.dwLoginShowID
end
function OnRemove(A0_19, A1_20, A2_21, A3_22, A4_23, A5_24, A6_25, A7_26, A8_27, A9_28)
end
function OnEarlyWarning(A0_29, A1_30)
end
