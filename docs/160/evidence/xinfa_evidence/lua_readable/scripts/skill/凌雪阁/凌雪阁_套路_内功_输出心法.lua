Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nPhysicsAttackPower = 316,
    nPhysicsHit = 9,
    nPhysicsOvercome = 14
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nPhysicsAttackPower = 438,
    nPhysicsHit = 16,
    nPhysicsOvercome = 20
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nPhysicsAttackPower = 665,
    nPhysicsHit = 25,
    nPhysicsOvercome = 30
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nPhysicsAttackPower = 888,
    nPhysicsHit = 35,
    nPhysicsOvercome = 41
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2687,
    nPhysicsHit = 44,
    nPhysicsOvercome = 122
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2687,
    nPhysicsHit = 44,
    nPhysicsOvercome = 122
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2687,
    nPhysicsHit = 44,
    nPhysicsOvercome = 122
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2687,
    nPhysicsHit = 44,
    nPhysicsOvercome = 122
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2687,
    nPhysicsHit = 44,
    nPhysicsOvercome = 122
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2687,
    nPhysicsHit = 44,
    nPhysicsOvercome = 122
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nPhysicsAttackPower = 316,
    nPhysicsHit = 9,
    nPhysicsOvercome = 14
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nPhysicsAttackPower = 438,
    nPhysicsHit = 16,
    nPhysicsOvercome = 20
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nPhysicsAttackPower = 665,
    nPhysicsHit = 25,
    nPhysicsOvercome = 30
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nPhysicsAttackPower = 888,
    nPhysicsHit = 35,
    nPhysicsOvercome = 41
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2687,
    nPhysicsHit = 44,
    nPhysicsOvercome = 122
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10585], 1)
  if A0_0.dwLevel >= 1 and A0_0.dwLevel < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif A0_0.dwLevel >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2941, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[A0_0.dwLevel].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[A0_0.dwLevel].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_ATTACK_POWER_COF, 737, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_OVERCOME_COF, 31, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_OVERCOME_BASE, tSkillData[A0_0.dwLevel].nPhysicsOvercome, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L3_2].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1722, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1799, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/凌雪阁/凌雪阁_套路_内功_输出心法.lua", 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_3, A1_4)
  return A1_4
end
function OnSkillLevelUp(A0_5, A1_6)
  if not A1_6.GetKungfuMountID() then
    A1_6.MountKungfu(A0_5.dwSkillID, A0_5.dwLevel)
  end
  A1_6.LearnSkillLevel(22049, A0_5.dwLevel, A1_6.dwID)
end
function Apply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
  GetPlayer(A0_7).AddBuff(GetPlayer(A0_7).dwID, GetPlayer(A0_7).nLevel, 14275, 1)
  GetPlayer(A0_7).bSurplusAutoCast = false
  GetPlayer(A0_7).bSurplusAutoReplenish = false
end
function UnApply(A0_8)
end
function OnTimer(A0_9, A1_10, A2_11)
  if not A0_9 then
    return
  end
end
