Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nPhysicsAttackPower = 283,
    nPhysicsHit = 11,
    nPhysicsCritical = 47
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nPhysicsAttackPower = 392,
    nPhysicsHit = 20,
    nPhysicsCritical = 65
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nPhysicsAttackPower = 596,
    nPhysicsHit = 31,
    nPhysicsCritical = 99
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nPhysicsAttackPower = 796,
    nPhysicsHit = 42,
    nPhysicsCritical = 133
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nPhysicsAttackPower = 283,
    nPhysicsHit = 11,
    nPhysicsCritical = 47
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nPhysicsAttackPower = 392,
    nPhysicsHit = 20,
    nPhysicsCritical = 65
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nPhysicsAttackPower = 596,
    nPhysicsHit = 31,
    nPhysicsCritical = 99
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nPhysicsAttackPower = 796,
    nPhysicsHit = 42,
    nPhysicsCritical = 133
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nPhysicsAttackPower = 2408,
    nPhysicsHit = 54,
    nPhysicsCritical = 401
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_RAGE, 100, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3196, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 1711, 1)
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 716, 2)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, 717, 2)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -307)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_ATTACK_POWER_COF, 727, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_CRITICAL_STRIKE_COF, 41, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_CRITICAL_STRIKE, tSkillData[L2_2].nPhysicsCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L2_2].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 228, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 117, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 3143, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 2941, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[10015], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_QI_ENERGY, tSkillKungfuConst.LOGIC.QI[10015].MAX, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.QI_ENERGY_REPLENISH, tSkillKungfuConst.LOGIC.QI[10015].REPLENISH, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill/纯阳/纯阳_套路_太虚剑意.lua", 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function OnSkillLevelUp(A0_6, A1_7)
  local L2_8, L3_9
  L2_8 = A1_7.GetKungfuMount
  L2_8 = L2_8()
  if not L2_8 then
    L3_9 = A1_7.MountKungfu
    L3_9(A0_6.dwSkillID, A0_6.dwLevel)
  end
  L3_9 = A0_6.dwLevel
  if A1_7.dwForceID == 4 and A1_7.GetSkillLevel(10199) < 1 then
    A1_7.LearnSkill(10199)
  end
  A1_7.LearnSkillLevel(342, L3_9, A1_7.dwID)
  A1_7.LearnSkill(343)
end
function Apply(A0_10)
  if GetPlayer(A0_10) then
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 5860, 1)
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 6094, 1)
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 6095, 1)
    GetPlayer(A0_10).AddBuff(GetPlayer(A0_10).dwID, GetPlayer(A0_10).nLevel, 14275, 1)
    if GetPlayer(A0_10).GetSkillLevel(38530) ~= 1 then
      GetPlayer(A0_10).LearnSkillLevel(38530, 1, GetPlayer(A0_10).dwID)
    end
    GetPlayer(A0_10).LearnSkillLevel(46187, 1, GetPlayer(A0_10).dwID)
    GetPlayer(A0_10).LearnSkillLevel(46188, 1, GetPlayer(A0_10).dwID)
    GetPlayer(A0_10).LearnSkillLevel(309, 33, GetPlayer(A0_10).dwID)
  end
  for _FORV_5_ = 1, 5 do
    if GetPlayer(A0_10).IsHaveBuff(12499 + _FORV_5_, 1) then
      GetPlayer(A0_10).DelBuff(12499 + _FORV_5_, 1)
    elseif GetPlayer(A0_10).IsHaveBuff(12778 + _FORV_5_, 1) then
      GetPlayer(A0_10).DelBuff(12778 + _FORV_5_, 1)
    end
  end
  GetPlayer(A0_10).bSurplusAutoCast = false
  GetPlayer(A0_10).bSurplusAutoReplenish = false
end
function UnApply(A0_11)
  if GetPlayer(A0_11) then
    GetPlayer(A0_11).DelBuff(6094, 1)
    GetPlayer(A0_11).DelBuff(5860, 1)
    GetPlayer(A0_11).DelBuff(6095, 1)
    GetPlayer(A0_11).DelBuff(6428, 1)
    GetPlayer(A0_11).nCurrentRage = 0
    GetPlayer(A0_11).ForgetSkill(38530)
  end
end
function OnTimer(A0_12, A1_13, A2_14)
end
