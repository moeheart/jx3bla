Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nPhysicsAttackPower = 322,
    nPhysicsShield = 8,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nPhysicsAttackPower = 446,
    nPhysicsShield = 12,
    nPhysicsHit = 18
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nPhysicsAttackPower = 677,
    nPhysicsShield = 18,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nPhysicsAttackPower = 905,
    nPhysicsShield = 24,
    nPhysicsHit = 39
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 703,
    nPhysicsAttackPower = 322,
    nPhysicsShield = 8,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 982,
    nPhysicsAttackPower = 446,
    nPhysicsShield = 12,
    nPhysicsHit = 18
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1491,
    nPhysicsAttackPower = 677,
    nPhysicsShield = 18,
    nPhysicsHit = 29
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2000,
    nPhysicsAttackPower = 905,
    nPhysicsShield = 24,
    nPhysicsHit = 39
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6000,
    nPhysicsAttackPower = 2738,
    nPhysicsShield = 71,
    nPhysicsHit = 49
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/霸刀/霸刀_套路_内功_输出心法.lua", 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10464], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_ENERGY, tSkillKungfuConst.LOGIC.QI[10464].MAX, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.QI_ENERGY_REPLENISH, tSkillKungfuConst.LOGIC.QI[10464].REPLENISH, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_ENERGY, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STOP_MAKE_SUN_POWER, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_SUN_ENERGY, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMP / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_ATTACK_POWER_COF, 553, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_OVERCOME_COF, 215, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L1_1].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[L1_1].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1441, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1446, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1435, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_2, A1_3)
  return A1_3
end
function OnSkillLevelUp(A0_4, A1_5)
  if not A1_5.GetKungfuMount() then
    A1_5.MountKungfu(A0_4.dwSkillID, A0_4.dwLevel)
  end
  A1_5.LearnSkillLevel(16023, A0_4.dwLevel, A1_5.dwID)
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  GetPlayer(A0_6).bSurplusAutoCast = false
  GetPlayer(A0_6).bSurplusAutoReplenish = false
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 10919, 1)
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
  if not GetPlayer(A0_6).IsHaveBuff(10816, 1) or not GetPlayer(A0_6).IsHaveBuff(10814, 1) or not GetPlayer(A0_6).IsHaveBuff(10815, 1) then
    GetPlayer(A0_6).CastSkill(16168, 1)
  end
  GetPlayer(A0_6).LearnSkillLevel(42428, 1, false)
end
function UnApply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
  GetPlayer(A0_7).DelBuff(10919, 1)
  GetPlayer(A0_7).DelMultiGroupBuffByID(10814)
  GetPlayer(A0_7).DelMultiGroupBuffByID(11381)
  GetPlayer(A0_7).DelMultiGroupBuffByID(10815)
  GetPlayer(A0_7).DelMultiGroupBuffByID(10816)
end
function OnTimer(A0_8, A1_9, A2_10)
end
