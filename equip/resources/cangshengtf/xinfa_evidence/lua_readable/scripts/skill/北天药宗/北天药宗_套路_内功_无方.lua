Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 18,
    nMaxMana = 521,
    nSpunkAttackPower = 274,
    nPoisonOvercome = 43,
    nPhysicsShield = 19
  },
  {
    DecriticalDamagePowerBase = 32,
    nMaxMana = 728,
    nSpunkAttackPower = 380,
    nPoisonOvercome = 59,
    nPhysicsShield = 26
  },
  {
    DecriticalDamagePowerBase = 51,
    nMaxMana = 1106,
    nSpunkAttackPower = 577,
    nPoisonOvercome = 90,
    nPhysicsShield = 40
  },
  {
    DecriticalDamagePowerBase = 69,
    nMaxMana = 2004,
    nSpunkAttackPower = 771,
    nPoisonOvercome = 120,
    nPhysicsShield = 54
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6012,
    nSpunkAttackPower = 2332,
    nPoisonOvercome = 363,
    nPhysicsShield = 164
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6012,
    nSpunkAttackPower = 2332,
    nPoisonOvercome = 363,
    nPhysicsShield = 164
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6012,
    nSpunkAttackPower = 2332,
    nPoisonOvercome = 363,
    nPhysicsShield = 164
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6012,
    nSpunkAttackPower = 2332,
    nPoisonOvercome = 363,
    nPhysicsShield = 164
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6012,
    nSpunkAttackPower = 2332,
    nPoisonOvercome = 363,
    nPhysicsShield = 164
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6012,
    nSpunkAttackPower = 2332,
    nPoisonOvercome = 363,
    nPhysicsShield = 164
  },
  {
    DecriticalDamagePowerBase = 18,
    nMaxMana = 521,
    nSpunkAttackPower = 274,
    nPoisonOvercome = 43,
    nPhysicsShield = 19
  },
  {
    DecriticalDamagePowerBase = 32,
    nMaxMana = 728,
    nSpunkAttackPower = 380,
    nPoisonOvercome = 59,
    nPhysicsShield = 26
  },
  {
    DecriticalDamagePowerBase = 51,
    nMaxMana = 1106,
    nSpunkAttackPower = 577,
    nPoisonOvercome = 90,
    nPhysicsShield = 40
  },
  {
    DecriticalDamagePowerBase = 69,
    nMaxMana = 2004,
    nSpunkAttackPower = 771,
    nPoisonOvercome = 120,
    nPhysicsShield = 54
  },
  {
    DecriticalDamagePowerBase = 87,
    nMaxMana = 6012,
    nSpunkAttackPower = 2332,
    nPoisonOvercome = 363,
    nPhysicsShield = 164
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
  local L1_1, L3_2
  L1_1 = false
  L3_2 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  if A0_0.dwLevel >= 1 and A0_0.dwLevel < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif A0_0.dwLevel >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[A0_0.dwLevel].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[A0_0.dwLevel].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_POISON_ATTACK_POWER_COF, 707, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_POISON_OVERCOME_COF, 61, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L3_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/北天药宗/北天药宗_套路_内功_无方.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[A0_0.dwLevel].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.POISON_OVERCOME_BASE, tSkillData[A0_0.dwLevel].nPoisonOvercome, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.POISON, SKILL_KIND_TYPE.POISON)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10627], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_CONTROL_COUNT, 2, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2036, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2074, 0)
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
  if not A1_9.GetKungfuMountID() then
    A1_9.MountKungfu(A0_8.dwSkillID, A0_8.dwLevel)
  end
  A1_9.LearnSkillLevel(27458, A0_8.dwLevel, A1_9.dwID)
end
function Apply(A0_10)
  if GetPlayer(A0_10) then
    if GetPlayer(A0_10).GetSkillLevel(28533) > 0 or 0 < GetPlayer(A0_10).GetSkillLevel(29471) then
      GetPlayer(A0_10).LearnSkillLevel(28553, 1, false)
    end
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 14275, 1)
    GetPlayer(A0_10).bSurplusAutoCast = false
    GetPlayer(A0_10).bSurplusAutoReplenish = false
  end
end
function UnApply(A0_11)
  if not GetPlayer(A0_11) then
    return
  end
  GetPlayer(A0_11).DelMultiGroupBuffByID(20075)
  GetPlayer(A0_11).DelMultiGroupBuffByID(20074)
end
function OnTimer(A0_12, A1_13, A2_14)
end
