Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nNeHit = 8,
    nPhysicsCri = 36,
    nPoisonAttackPower = 268,
    nMagicDefence = 25
  },
  {
    DecriticalDamagePowerBase = 44,
    nNeHit = 14,
    nPhysicsCri = 50,
    nPoisonAttackPower = 372,
    nMagicDefence = 35
  },
  {
    DecriticalDamagePowerBase = 70,
    nNeHit = 22,
    nPhysicsCri = 76,
    nPoisonAttackPower = 564,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 95,
    nNeHit = 31,
    nPhysicsCri = 102,
    nPoisonAttackPower = 754,
    nMagicDefence = 73
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
  },
  {
    DecriticalDamagePowerBase = 25,
    nNeHit = 8,
    nPhysicsCri = 36,
    nPoisonAttackPower = 268,
    nMagicDefence = 25
  },
  {
    DecriticalDamagePowerBase = 44,
    nNeHit = 14,
    nPhysicsCri = 50,
    nPoisonAttackPower = 372,
    nMagicDefence = 35
  },
  {
    DecriticalDamagePowerBase = 70,
    nNeHit = 22,
    nPhysicsCri = 76,
    nPoisonAttackPower = 564,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 95,
    nNeHit = 31,
    nPhysicsCri = 102,
    nPoisonAttackPower = 754,
    nMagicDefence = 73
  },
  {
    DecriticalDamagePowerBase = 120,
    nNeHit = 39,
    nPhysicsCri = 308,
    nPoisonAttackPower = 2282,
    nMagicDefence = 219
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/唐门/唐门_内功_机关.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10225], 1)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_POISON_ATTACK_POWER_COF, 543, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_PHYSICS_CRITICAL_STRIKE_COF, 225, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.POISON_ATTACK_POWER_BASE, tSkillData[L2_2].nPoisonAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L3_3].nPhysicsCri, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_ENERGY, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ENERGY_REPLENISH, 10, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 580, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_PERCENT, 1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.POISON)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STOP_MAKE_QI_CONTROL_CANCEL, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_CONTROL_COUNT, 2, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2941, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function OnSkillLevelUp(A0_6, A1_7)
  local L2_8, L3_9
  L2_8 = A1_7.GetKungfuMountID
  L2_8 = L2_8()
  if not L2_8 then
    L3_9 = A1_7.MountKungfu
    L3_9(A0_6.dwSkillID, A0_6.dwLevel)
  end
  L3_9 = A0_6.dwLevel
  if A1_7.dwForceID == 7 and A1_7.GetSkillLevel(10230) < 1 then
    A1_7.LearnSkill(10230)
  end
  if 1 > A1_7.GetSkillLevel(3373) then
    A1_7.LearnSkill(3373)
  end
  if 1 > A1_7.GetSkillLevel(3374) then
    A1_7.LearnSkill(3374)
  end
  A1_7.LearnSkillLevel(3211, L3_9, A1_7.dwID)
  A1_7.LearnSkill(3212)
end
function Apply(A0_10)
  if GetPlayer(A0_10) then
    GetPlayer(A0_10).AddBuff(A0_10, GetPlayer(A0_10).nLevel, 12738, 1)
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 14275, 1)
    GetPlayer(A0_10).bSurplusAutoCast = false
    GetPlayer(A0_10).bSurplusAutoReplenish = false
  end
  if GetPlayer(A0_10).GetSkillLevel(3109) ~= 0 then
    for _FORV_5_ = 1, 3 do
      if GetPlayer(A0_10).GetSkillLevel(38878 + _FORV_5_) ~= 1 then
        GetPlayer(A0_10).LearnSkillLevel(38878 + _FORV_5_, 1, GetPlayer(A0_10).dwID)
      end
    end
  end
end
function UnApply(A0_11)
  if GetPlayer(A0_11) then
    GetPlayer(A0_11).DelBuffByID(5994)
    GetPlayer(A0_11).DelBuffByID(9719)
    GetPlayer(A0_11).DelBuffByID(20939)
  end
end
function OnTimer(A0_12, A1_13, A2_14)
end
