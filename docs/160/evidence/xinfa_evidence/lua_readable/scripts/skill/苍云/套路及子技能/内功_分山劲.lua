Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nPhysicsAttackPower = 298,
    nParry = 69,
    nPhysicsHit = 6,
    nPhysicsOvercome = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nPhysicsAttackPower = 413,
    nParry = 96,
    nPhysicsHit = 10,
    nPhysicsOvercome = 27
  },
  {
    DecriticalDamagePowerBase = 70,
    nPhysicsAttackPower = 627,
    nParry = 147,
    nPhysicsHit = 17,
    nPhysicsOvercome = 41
  },
  {
    DecriticalDamagePowerBase = 95,
    nPhysicsAttackPower = 838,
    nParry = 197,
    nPhysicsHit = 23,
    nPhysicsOvercome = 55
  },
  {
    DecriticalDamagePowerBase = 120,
    nPhysicsAttackPower = 2535,
    nParry = 591,
    nPhysicsHit = 29,
    nPhysicsOvercome = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nPhysicsAttackPower = 2535,
    nParry = 591,
    nPhysicsHit = 29,
    nPhysicsOvercome = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nPhysicsAttackPower = 2535,
    nParry = 591,
    nPhysicsHit = 29,
    nPhysicsOvercome = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nPhysicsAttackPower = 2535,
    nParry = 591,
    nPhysicsHit = 29,
    nPhysicsOvercome = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nPhysicsAttackPower = 2535,
    nParry = 591,
    nPhysicsHit = 29,
    nPhysicsOvercome = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nPhysicsAttackPower = 2535,
    nParry = 591,
    nPhysicsHit = 29,
    nPhysicsOvercome = 164
  },
  {
    DecriticalDamagePowerBase = 25,
    nPhysicsAttackPower = 298,
    nParry = 69,
    nPhysicsHit = 6,
    nPhysicsOvercome = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nPhysicsAttackPower = 413,
    nParry = 96,
    nPhysicsHit = 10,
    nPhysicsOvercome = 27
  },
  {
    DecriticalDamagePowerBase = 70,
    nPhysicsAttackPower = 627,
    nParry = 147,
    nPhysicsHit = 17,
    nPhysicsOvercome = 41
  },
  {
    DecriticalDamagePowerBase = 95,
    nPhysicsAttackPower = 838,
    nParry = 197,
    nPhysicsHit = 23,
    nPhysicsOvercome = 55
  },
  {
    DecriticalDamagePowerBase = 120,
    nPhysicsAttackPower = 2535,
    nParry = 591,
    nPhysicsHit = 29,
    nPhysicsOvercome = 164
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  if L1_1 >= 1 and L1_1 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L1_1 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10390], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_ENERGY, tSkillKungfuConst.LOGIC.QI[10390].MAX, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.QI_ENERGY_REPLENISH, tSkillKungfuConst.LOGIC.QI[10390].REPLENISH, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_ATTACK_POWER_COF, 768, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PARRY_COF, 102, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PARRY_VALUE_COF, 205, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L1_1].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PARRY_BASE, tSkillData[L1_1].nParry, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_OVERCOME_BASE, tSkillData[L1_1].nPhysicsOvercome, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_PERCENT, 1024, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1219, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 1236, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/苍云/套路及子技能/内功_分山劲.lua", 0)
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
  A1_5.LearnSkillLevel(13149, A0_4.dwLevel, A1_5.dwID)
end
function Apply(A0_6)
  if not GetPlayer(A0_6) then
    return
  end
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 14275, 1)
  GetPlayer(A0_6).bSurplusAutoCast = false
  GetPlayer(A0_6).bSurplusAutoReplenish = false
  if GetPlayer(A0_6).GetSkillLevel(30769) == 1 then
    GetPlayer(A0_6).LearnSkillLevel(45998, 2, GetPlayer(A0_6).dwID)
  else
    GetPlayer(A0_6).LearnSkillLevel(45998, 1, GetPlayer(A0_6).dwID)
  end
  GetPlayer(A0_6).LearnSkillLevel(40721, 1, false)
  GetPlayer(A0_6).AddBuff(GetPlayer(A0_6).dwID, GetPlayer(A0_6).nLevel, 8454, 1)
end
function UnApply(A0_7)
  if not GetPlayer(A0_7) then
    return
  end
  GetPlayer(A0_7).DelMultiGroupBuffByID(8571)
  GetPlayer(A0_7).DelMultiGroupBuffByID(8395)
  GetPlayer(A0_7).DelMultiGroupBuffByID(8454)
  GetPlayer(A0_7).ForgetSkill(40721)
end
function OnTimer(A0_8, A1_9, A2_10)
end
