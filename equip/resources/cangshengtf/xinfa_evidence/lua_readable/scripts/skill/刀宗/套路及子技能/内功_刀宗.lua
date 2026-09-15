Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 528,
    nPhysicsAttackPower = 289,
    nPhysicsCriticalStrike = 41
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 738,
    nPhysicsAttackPower = 401,
    nPhysicsCriticalStrike = 57
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1121,
    nPhysicsAttackPower = 608,
    nPhysicsCriticalStrike = 87
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2030,
    nPhysicsAttackPower = 813,
    nPhysicsCriticalStrike = 116
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 528,
    nPhysicsAttackPower = 289,
    nPhysicsCriticalStrike = 41
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 738,
    nPhysicsAttackPower = 401,
    nPhysicsCriticalStrike = 57
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1121,
    nPhysicsAttackPower = 608,
    nPhysicsCriticalStrike = 87
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2030,
    nPhysicsAttackPower = 813,
    nPhysicsCriticalStrike = 116
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6090,
    nPhysicsAttackPower = 2459,
    nPhysicsCriticalStrike = 350
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
  {DecriticalDamagePowerBase = 1725},
  {DecriticalDamagePowerBase = 1725}
}
function GetSkillLevelData(A0_0)
  local L1_1
  L1_1 = A0_0.dwLevel
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/刀宗/套路及子技能/内功_刀宗.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_ENERGY, 100, 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10698], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L1_1].nMP / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -512)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_ATTACK_POWER_COF, 604, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_CRITICAL_STRIKE_COF, 164, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L1_1].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L1_1].nPhysicsCriticalStrike, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
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
  A1_5.LearnSkillLevel(31559, A0_4.dwLevel, false)
end
function Apply(A0_6)
  local L1_7, L2_8
  L1_7 = GetPlayer
  L2_8 = A0_6
  L1_7 = L1_7(L2_8)
  if not L1_7 then
    return
  end
  L2_8 = L1_7.DelMultiGroupBuffByID
  L2_8(24029)
  L2_8 = L1_7.DelMultiGroupBuffByID
  L2_8(24110)
  L2_8 = L1_7.AddBuff
  L2_8(L1_7.dwID, L1_7.nLevel, 24029, 1)
  L2_8 = L1_7.AddBuff
  L2_8(L1_7.dwID, L1_7.nLevel, 24042, 1)
  L2_8 = L1_7.AddBuff
  L2_8(L1_7.dwID, L1_7.nLevel, 14275, 1)
  L1_7.bSurplusAutoCast = false
  L1_7.bSurplusAutoReplenish = false
  L2_8 = L1_7.GetSkillLevel
  L2_8 = L2_8(10698)
  if L2_8 > L1_7.GetSkillLevel(31559) then
    L1_7.LearnSkillLevel(31559, L2_8, false)
  end
end
function UnApply(A0_9)
  if not GetPlayer(A0_9) then
    return
  end
  GetPlayer(A0_9).DelBuff(24042, 1)
  GetPlayer(A0_9).DelMultiGroupBuffByID(24029)
  GetPlayer(A0_9).DelMultiGroupBuffByID(24110)
end
function OnTimer(A0_10, A1_11, A2_12)
end
