Include("scripts/Include/Skill.lh")
Include("scripts/skill/装备/治疗全能属性转治疗量.lua")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 18,
    nMaxMana = 519,
    nTherapyPower = 828,
    nLifeReplenish = 17,
    nPhysicsShield = 38
  },
  {
    DecriticalDamagePowerBase = 32,
    nMaxMana = 725,
    nTherapyPower = 1152,
    nLifeReplenish = 24,
    nPhysicsShield = 53
  },
  {
    DecriticalDamagePowerBase = 51,
    nMaxMana = 1101,
    nTherapyPower = 1747,
    nLifeReplenish = 37,
    nPhysicsShield = 81
  },
  {
    DecriticalDamagePowerBase = 69,
    nMaxMana = 1994,
    nTherapyPower = 2342,
    nLifeReplenish = 50,
    nPhysicsShield = 109
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 5982,
    nTherapyPower = 7049,
    nLifeReplenish = 151,
    nPhysicsShield = 328
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 5982,
    nTherapyPower = 7049,
    nLifeReplenish = 151,
    nPhysicsShield = 328
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 5982,
    nTherapyPower = 7049,
    nLifeReplenish = 151,
    nPhysicsShield = 328
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 5982,
    nTherapyPower = 7049,
    nLifeReplenish = 151,
    nPhysicsShield = 328
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 5982,
    nTherapyPower = 7049,
    nLifeReplenish = 151,
    nPhysicsShield = 328
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 5982,
    nTherapyPower = 7049,
    nLifeReplenish = 151,
    nPhysicsShield = 328
  },
  {
    DecriticalDamagePowerBase = 18,
    nMaxMana = 519,
    nTherapyPower = 828,
    nLifeReplenish = 17,
    nPhysicsShield = 38
  },
  {
    DecriticalDamagePowerBase = 32,
    nMaxMana = 725,
    nTherapyPower = 1152,
    nLifeReplenish = 24,
    nPhysicsShield = 53
  },
  {
    DecriticalDamagePowerBase = 51,
    nMaxMana = 1101,
    nTherapyPower = 1747,
    nLifeReplenish = 37,
    nPhysicsShield = 81
  },
  {
    DecriticalDamagePowerBase = 69,
    nMaxMana = 1994,
    nTherapyPower = 2342,
    nLifeReplenish = 50,
    nPhysicsShield = 109
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 5982,
    nTherapyPower = 7049,
    nLifeReplenish = 151,
    nPhysicsShield = 328
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.THERAPY, 0)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_THERAPY_POWER_COF, 748, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_POISON_CRITICAL_STRIKE_COF, 20, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.THERAPY_POWER_BASE, tSkillData[L2_2].nTherapyPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LIFE_REPLENISH_EXT, tSkillData[L2_2].nLifeReplenish, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L3_3].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/北天药宗/北天药宗_套路_内功_灵素.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.POISON, SKILL_KIND_TYPE.POISON)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_CONTROL_COUNT, 2, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2036, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function CanLearnSkill(A0_6, A1_7)
  local L2_8
  L2_8 = true
  return L2_8
end
function OnSkillLevelUp(A0_9, A1_10)
  if not A1_10.GetKungfuMountID() then
    A1_10.MountKungfu(A0_9.dwSkillID, A0_9.dwLevel)
  end
  A1_10.LearnSkillLevel(27457, A0_9.dwLevel, A1_10.dwID)
end
function Apply(A0_11)
  local L1_12
  L1_12 = GetPlayer
  L1_12 = L1_12(A0_11)
  if L1_12 then
    if L1_12.GetSkillLevel(28533) > 0 or 0 < L1_12.GetSkillLevel(29471) then
      L1_12.LearnSkillLevel(28553, 2, false)
    end
    L1_12.AddBuff(L1_12.dwID, L1_12.nLevel, 14275, 1)
    L1_12.bSurplusAutoCast = false
    L1_12.bSurplusAutoReplenish = false
    PVXTherapyAllRound2TherapyPowerBase(L1_12)
  end
end
function UnApply(A0_13)
  if not GetPlayer(A0_13) then
    return
  end
  GetPlayer(A0_13).DelMultiGroupBuffByID(20075)
  GetPlayer(A0_13).DelMultiGroupBuffByID(20074)
end
function OnTimer(A0_14, A1_15, A2_16)
end
