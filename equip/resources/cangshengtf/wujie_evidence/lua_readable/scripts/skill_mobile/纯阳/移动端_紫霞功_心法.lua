Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 520,
    nSpunkAttackPower = 768,
    nNeutralHit = 10,
    nNeutralCritical = 85,
    nMagicDefence = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 727,
    nSpunkAttackPower = 868,
    nNeutralHit = 18,
    nNeutralCritical = 119,
    nMagicDefence = 26
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1104,
    nSpunkAttackPower = 1068,
    nNeutralHit = 28,
    nNeutralCritical = 180,
    nMagicDefence = 40
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2000,
    nSpunkAttackPower = 1268,
    nNeutralHit = 39,
    nNeutralCritical = 120,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
    nMagicDefence = 164
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 520,
    nSpunkAttackPower = 268,
    nNeutralHit = 10,
    nNeutralCritical = 85,
    nMagicDefence = 19
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 727,
    nSpunkAttackPower = 372,
    nNeutralHit = 18,
    nNeutralCritical = 119,
    nMagicDefence = 26
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1104,
    nSpunkAttackPower = 564,
    nNeutralHit = 28,
    nNeutralCritical = 180,
    nMagicDefence = 40
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2000,
    nSpunkAttackPower = 754,
    nNeutralHit = 39,
    nNeutralCritical = 120,
    nMagicDefence = 54
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6000,
    nSpunkAttackPower = 2282,
    nNeutralHit = 49,
    nNeutralCritical = 363,
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
function GetSkillLevelData(A0_0)
  local L1_1, L2_2, L3_3
  L1_1 = false
  L2_2 = A0_0.dwLevel
  L3_3 = A0_0.dwLevel
  if L3_3 >= 1 and L3_3 < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif L3_3 >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_NEUTRAL_ATTACK_POWER_COF, 727, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_NEUTRAL_CRITICAL_STRIKE_COF, 41, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.NEUTRAL_CRITICAL_STRIKE, tSkillData[L2_2].nNeutralCritical, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/纯阳/移动端_紫霞功_心法.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100398], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.NEUTRAL_MAGIC, SKILL_KIND_TYPE.NEUTRAL_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_4, A1_5)
  return A1_5
end
function OnSkillLevelUp(A0_6, A1_7)
  if not A1_7.GetKungfuMount() then
    A1_7.MountKungfu(A0_6.dwSkillID, A0_6.dwLevel)
  end
  A1_7.AddSkillRecipe(16667, 1)
  A1_7.AddSkillRecipe(16668, 1)
  A1_7.AddSkillRecipe(16669, 1)
  A1_7.AddSkillRecipe(16670, 1)
  A1_7.AddSkillRecipe(16671, 1)
  A1_7.AddSkillRecipe(16672, 1)
  A1_7.AddSkillRecipe(16673, 1)
  A1_7.AddSkillRecipe(16674, 1)
  A1_7.AddSkillRecipe(16675, 1)
  A1_7.AddSkillRecipe(16676, 1)
  A1_7.AddSkillRecipe(16677, 1)
  A1_7.AddSkillRecipe(16678, 1)
  A1_7.AddSkillRecipe(16679, 1)
  A1_7.AddSkillRecipe(16680, 1)
  A1_7.AddSkillRecipe(16681, 1)
  A1_7.AddSkillRecipe(16682, 1)
  A1_7.AddSkillRecipe(16683, 1)
  A1_7.AddSkillRecipe(16684, 1)
  A1_7.AddSkillRecipe(16685, 1)
  A1_7.AddSkillRecipe(16686, 1)
end
function Apply(A0_8)
  if GetPlayer(A0_8) then
    GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 14275, 1)
    GetPlayer(A0_8).bSurplusAutoCast = false
    GetPlayer(A0_8).bSurplusAutoReplenish = false
    if GetPlayer(A0_8).GetSkillLevel(102733) == 0 then
      GetPlayer(A0_8).LearnSkillLevel(102733, 1, A0_8)
    end
  end
end
function UnApply(A0_9)
  local L1_10
end
function OnTimer(A0_11, A1_12, A2_13)
end
