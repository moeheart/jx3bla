Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nSpunkAttackPower = 798,
    nNeHit = 6,
    nLifeReplenish = 15,
    nMagicDefence = 13
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nSpunkAttackPower = 898,
    nNeHit = 10,
    nLifeReplenish = 21,
    nMagicDefence = 18
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nSpunkAttackPower = 1098,
    nNeHit = 17,
    nLifeReplenish = 32,
    nMagicDefence = 27
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nSpunkAttackPower = 1298,
    nNeHit = 23,
    nLifeReplenish = 43,
    nMagicDefence = 37
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nSpunkAttackPower = 298,
    nNeHit = 6,
    nLifeReplenish = 15,
    nMagicDefence = 13
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nSpunkAttackPower = 413,
    nNeHit = 10,
    nLifeReplenish = 21,
    nMagicDefence = 18
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nSpunkAttackPower = 627,
    nNeHit = 17,
    nLifeReplenish = 32,
    nMagicDefence = 27
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nSpunkAttackPower = 838,
    nNeHit = 23,
    nLifeReplenish = 43,
    nMagicDefence = 37
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6120,
    nSpunkAttackPower = 2535,
    nNeHit = 29,
    nLifeReplenish = 130,
    nMagicDefence = 110
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/万花/移动端_花间游_心法.lua", 0)
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_NEUTRAL_ATTACK_POWER_COF, 686, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPUNK_TO_NEUTRAL_OVERCOME_COF, 82, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.LIFE_REPLENISH_EXT, tSkillData[L2_2].nLifeReplenish, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.NEUTRAL_MAGIC, SKILL_KIND_TYPE.NEUTRAL_MAGIC)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100408], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
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
  A1_10.AddSkillRecipe(16513, 1)
  A1_10.AddSkillRecipe(16514, 1)
  A1_10.AddSkillRecipe(16518, 1)
  A1_10.AddSkillRecipe(16519, 1)
  A1_10.AddSkillRecipe(16520, 1)
  A1_10.AddSkillRecipe(16521, 1)
  A1_10.AddSkillRecipe(16522, 1)
  A1_10.AddSkillRecipe(16523, 1)
  A1_10.AddSkillRecipe(16524, 1)
  A1_10.AddSkillRecipe(16525, 1)
  A1_10.AddSkillRecipe(16543, 1)
  A1_10.AddSkillRecipe(16544, 1)
  A1_10.AddSkillRecipe(16547, 1)
  A1_10.AddSkillRecipe(16548, 1)
  A1_10.AddSkillRecipe(16549, 1)
  A1_10.AddSkillRecipe(16550, 1)
  A1_10.AddSkillRecipe(16551, 1)
  A1_10.AddSkillRecipe(16552, 1)
  A1_10.AddSkillRecipe(17127, 1)
  A1_10.AddSkillRecipe(17128, 1)
end
function Apply(A0_11)
  if GetPlayer(A0_11) then
    GetPlayer(A0_11).AddBuff(GetPlayer(A0_11).dwID, GetPlayer(A0_11).nLevel, 14275, 1)
    GetPlayer(A0_11).bSurplusAutoCast = false
    GetPlayer(A0_11).bSurplusAutoReplenish = false
    if GetPlayer(A0_11).GetSkillLevel(102718) == 0 then
      GetPlayer(A0_11).LearnSkillLevel(102718, 1, false)
    end
  end
end
function UnApply(A0_12)
  if GetPlayer(A0_12) then
  end
end
function OnTimer(A0_13, A1_14, A2_15)
end
