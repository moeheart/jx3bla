Include("scripts/Include/Skill.lh")
Include("scripts/Include/NewSkill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 703,
    nSpunkAttackPower = 807,
    nNeutralHit = 10,
    nLunarCritical = 4,
    nMagicDefence = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 982,
    nSpunkAttackPower = 907,
    nNeutralHit = 18,
    nLunarCritical = 6,
    nMagicDefence = 26
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1491,
    nSpunkAttackPower = 1107,
    nNeutralHit = 28,
    nLunarCritical = 8,
    nMagicDefence = 40
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2000,
    nSpunkAttackPower = 1307,
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
tSkillnPhysicsShielddata = {
  {nPhysicsShield = 2},
  {nPhysicsShield = 4},
  {nPhysicsShield = 7},
  {nPhysicsShield = 10},
  {nPhysicsShield = 12},
  {nPhysicsShield = 15},
  {nPhysicsShield = 18},
  {nPhysicsShield = 21},
  {nPhysicsShield = 23},
  {nPhysicsShield = 52},
  {nPhysicsShield = 115},
  {nPhysicsShield = 254},
  {nPhysicsShield = 559},
  {nPhysicsShield = 1721}
}
function GetSkillLevelData(A0_0)
  local L1_1, L2_2
  L1_1 = false
  L2_2 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ADAPT_ATTRIBUTE_TYPE, 1, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  if L2_2 >= 1 and L2_2 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L2_2 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT_WITH_PARAM, "skill_mobile/无相楼/移动端_心法_幽罗引.lua", L2_2)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[102393], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.LUNAR_MAGIC, SKILL_KIND_TYPE.LUNAR_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_ATTACK_POWER_COF, 717, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_LUNAR_CRITICAL_STRIKE_COF, 51, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LUNAR_CRITICAL_STRIKE, tSkillData[L2_2].nLunarCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 9150, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_3, A1_4)
  return A1_4
end
function CanLearnSkill(A0_5, A1_6)
  local L2_7
  L2_7 = true
  return L2_7
end
function OnSkillLevelUp(A0_8, A1_9)
  if not A1_9.GetKungfuMount() then
    A1_9.MountKungfu(A0_8.dwSkillID, A0_8.dwLevel)
  end
end
function Apply(A0_10, A1_11, A2_12)
  if GetPlayer(A0_10) then
    GetPlayer(A0_10).bSurplusAutoCast = false
    GetPlayer(A0_10).bSurplusAutoReplenish = false
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 14275, 1)
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 71621, 1)
    if A1_11 == 14 then
      GetPlayer(A0_10).SetTimer(16, "scripts/skill/无相楼/无相楼心法.lua", 0, 0)
      if GetPlayer(A0_10).nLevel == GetPlayer(A0_10).nMaxLevel then
        if GetPlayer(A0_10).GetSkillLevel(100004) == 0 then
          GetPlayer(A0_10).LearnSkillLevel(100004, 1, false)
        end
        if GetPlayer(A0_10).GetSkillLevel(100005) == 0 then
          GetPlayer(A0_10).LearnSkillLevel(100005, 1, false)
        end
        if GetPlayer(A0_10).GetSkillLevel(101937) == 0 then
          GetPlayer(A0_10).LearnSkillLevel(101937, 1, false)
        end
      end
    end
    if GetPlayer(A0_10).GetSkillLevel(102737) == 0 then
      GetPlayer(A0_10).LearnSkillLevel(102737, 1, false)
    end
    if GetPlayer(A0_10).GetSkillLevel(102748) == 0 then
      GetPlayer(A0_10).LearnSkillLevel(102748, 1, false)
    end
  end
end
function UnApply(A0_13)
  if GetPlayer(A0_13) then
    GetPlayer(A0_13).DelBuff(31374, 1)
    GetPlayer(A0_13).DelBuff(71566, 1)
    GetPlayer(A0_13).DelBuff(71593, 1)
    GetPlayer(A0_13).DelBuff(71621, 1)
    if GetPlayer(A0_13).GetPet() then
      GetPlayer(A0_13).GetPet().Die()
    end
    for _FORV_6_, _FORV_7_ in pairs(tKLSkin_Buff) do
      GetPlayer(A0_13).DelBuff(_FORV_7_.dwBuffID, 1)
      GetPlayer(A0_13).DelBuff(31896, 1)
    end
    GetPlayer(A0_13).dwPuppetSkinID = 0
  end
end
function OnTimer(A0_14, A1_15, A2_16)
end
