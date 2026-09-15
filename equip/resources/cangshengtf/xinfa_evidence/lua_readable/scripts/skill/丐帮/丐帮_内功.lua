Include("scripts/Include/Skill.lh")
Include("scripts/Include/NewSkill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMP = 523,
    nPhysicsAttackPower = 313,
    nPhysicsShield = 17,
    nPhysicsCri = 0,
    nPhysicsHit = 6
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 731,
    nPhysicsAttackPower = 434,
    nPhysicsShield = 24,
    nPhysicsCri = 0,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1109,
    nPhysicsAttackPower = 658,
    nPhysicsShield = 37,
    nPhysicsCri = 0,
    nPhysicsHit = 16
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2010,
    nPhysicsAttackPower = 880,
    nPhysicsShield = 49,
    nPhysicsCri = 0,
    nPhysicsHit = 21
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  },
  {
    DecriticalDamagePowerBase = 25,
    nMP = 523,
    nPhysicsAttackPower = 313,
    nPhysicsShield = 17,
    nPhysicsCri = 0,
    nPhysicsHit = 6
  },
  {
    DecriticalDamagePowerBase = 44,
    nMP = 731,
    nPhysicsAttackPower = 434,
    nPhysicsShield = 24,
    nPhysicsCri = 0,
    nPhysicsHit = 10
  },
  {
    DecriticalDamagePowerBase = 70,
    nMP = 1109,
    nPhysicsAttackPower = 658,
    nPhysicsShield = 37,
    nPhysicsCri = 0,
    nPhysicsHit = 16
  },
  {
    DecriticalDamagePowerBase = 95,
    nMP = 2010,
    nPhysicsAttackPower = 880,
    nPhysicsShield = 49,
    nPhysicsCri = 0,
    nPhysicsHit = 21
  },
  {
    DecriticalDamagePowerBase = 120,
    nMP = 6030,
    nPhysicsAttackPower = 2662,
    nPhysicsShield = 147,
    nPhysicsCri = 0,
    nPhysicsHit = 27
  }
}
tSkillEventData = {
  {nLevel = 1, nEventID = 118},
  {nLevel = 2, nEventID = 118},
  {nLevel = 3, nEventID = 118},
  {nLevel = 4, nEventID = 145},
  {nLevel = 5, nEventID = 146},
  {nLevel = 6, nEventID = 147},
  {nLevel = 7, nEventID = 148}
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 5844, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 5661, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 3, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/丐帮/丐帮_内功.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  if 1 <= A0_0.dwLevel and A0_0.dwLevel < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif A0_0.dwLevel >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 4872, 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[A0_0.dwLevel].nMP / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[A0_0.dwLevel].nMP / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_ATTACK_POWER_COF, 573, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.STRENGTH_TO_PHYSICS_OVERCOME_COF, 195, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MOVE_SPEED_PERCENT, 105, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[A0_0.dwLevel].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, tSkillData[A0_0.dwLevel].nPhysicsShield, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1127, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1592, 0)
  AdditionalAttribute(A0_0)
  A0_0.nWeaponDamagePercent = 0
  return true
end
function CanCast(A0_1, A1_2)
  return A1_2
end
function OnSkillLevelUp(A0_3, A1_4)
  local L2_5, L3_6
  L2_5 = A1_4.GetKungfuMount
  L2_5 = L2_5()
  if not L2_5 then
    L3_6 = A1_4.MountKungfu
    L3_6(A0_3.dwSkillID, A0_3.dwLevel)
  end
  L3_6 = A0_3.dwLevel
  A1_4.LearnSkillLevel(5308, L3_6, A1_4.dwID)
  A1_4.LearnSkill(5309)
end
function Apply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
  GetPlayer(A0_7).AddBuff(GetPlayer(A0_7).dwID, GetPlayer(A0_7).nLevel, 14275, 1)
  GetPlayer(A0_7).bSurplusAutoCast = false
  GetPlayer(A0_7).bSurplusAutoReplenish = false
  for _FORV_6_ = 1, #{
    18523,
    5265,
    5522,
    5602
  } do
    if 1 <= GetPlayer(A0_7).GetSkillLevel(({
      18523,
      5265,
      5522,
      5602
    })[_FORV_6_]) then
      GetPlayer(A0_7).ForgetSkill(({
        18523,
        5265,
        5522,
        5602
      })[_FORV_6_])
    end
  end
end
function UnApply(A0_8)
  if not GetPlayer(A0_8) then
    return
  end
  GetPlayer(A0_8).DelMultiGroupBuffByID(30400)
end
