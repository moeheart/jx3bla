Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 523,
    nSpunkAttackPower = 798,
    nNeHit = 9,
    nManaReplenish = 0,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 731,
    nSpunkAttackPower = 898,
    nNeHit = 16,
    nManaReplenish = 0,
    nMagicDefence = 45
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1109,
    nSpunkAttackPower = 1098,
    nNeHit = 25,
    nManaReplenish = 0,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2010,
    nSpunkAttackPower = 1298,
    nNeHit = 35,
    nManaReplenish = 0,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
  },
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 523,
    nSpunkAttackPower = 298,
    nNeHit = 9,
    nManaReplenish = 0,
    nMagicDefence = 32
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 731,
    nSpunkAttackPower = 413,
    nNeHit = 16,
    nManaReplenish = 0,
    nMagicDefence = 45
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1109,
    nSpunkAttackPower = 627,
    nNeHit = 25,
    nManaReplenish = 0,
    nMagicDefence = 68
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2010,
    nSpunkAttackPower = 838,
    nNeHit = 35,
    nManaReplenish = 0,
    nMagicDefence = 91
  },
  {
    DecriticalDamagePowerBase = 120,
    nMaxMana = 6030,
    nSpunkAttackPower = 2535,
    nNeHit = 44,
    nManaReplenish = 0,
    nMagicDefence = 274
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
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[L3_3].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[L3_3].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_POISON_ATTACK_POWER_COF, 748, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SPIRIT_TO_POISON_OVERCOME_COF, 20, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_ATTACK_POWER_BASE, tSkillData[L2_2].nSpunkAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, tSkillData[L2_2].nMagicDefence, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/五毒/移动端_毒经_心法.lua", 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[100654], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.POISON, SKILL_KIND_TYPE.POISON)
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
  A1_7.AddSkillRecipe(16733, 1)
  A1_7.AddSkillRecipe(16734, 1)
  A1_7.AddSkillRecipe(16756, 1)
  A1_7.AddSkillRecipe(16757, 1)
  A1_7.AddSkillRecipe(16758, 1)
  A1_7.AddSkillRecipe(16759, 1)
  A1_7.AddSkillRecipe(16760, 1)
  A1_7.AddSkillRecipe(16761, 1)
  A1_7.AddSkillRecipe(16762, 1)
  A1_7.AddSkillRecipe(16763, 1)
  A1_7.AddSkillRecipe(16764, 1)
  A1_7.AddSkillRecipe(16765, 1)
  A1_7.AddSkillRecipe(16766, 1)
  A1_7.AddSkillRecipe(16767, 1)
  A1_7.AddSkillRecipe(16768, 1)
  A1_7.AddSkillRecipe(16769, 1)
  A1_7.AddSkillRecipe(16770, 1)
  A1_7.AddSkillRecipe(16771, 1)
  A1_7.AddSkillRecipe(16772, 1)
  A1_7.AddSkillRecipe(16773, 1)
  A1_7.AddSkillRecipe(17633, 1)
  A1_7.AddSkillRecipe(17634, 1)
end
function Apply(A0_8)
  if not GetPlayer(A0_8) then
    return
  end
  if not GetPlayer(A0_8).GetScene() then
    return
  end
  if GetNpc(GetPlayer(A0_8).dwPetID) then
    GetPlayer(A0_8).GetScene().DestroyNpc(GetNpc(GetPlayer(A0_8).dwPetID).dwID)
  end
  GetPlayer(A0_8).AddBuff(GetPlayer(A0_8).dwID, GetPlayer(A0_8).nLevel, 14275, 1)
  GetPlayer(A0_8).bSurplusAutoCast = false
  GetPlayer(A0_8).bSurplusAutoReplenish = false
  if GetPlayer(A0_8).GetSkillLevel(102744) == 0 then
    GetPlayer(A0_8).LearnSkillLevel(102744, 1, A0_8)
  end
end
function UnApply(A0_9)
  if not GetPlayer(A0_9) then
    return
  end
  if not GetPlayer(A0_9).GetScene() then
    return
  end
  if GetNpc(GetPlayer(A0_9).dwPetID) then
    GetPlayer(A0_9).GetScene().DestroyNpc(GetNpc(GetPlayer(A0_9).dwPetID).dwID)
  end
  if GetPlayer(A0_9).GetScene().GetNpcByNickName("GuChong" .. GetPlayer(A0_9).dwID) and GetPlayer(A0_9) and GetPlayer(A0_9).GetScene().IsNickNameNpcExist("GuChong" .. GetPlayer(A0_9).dwID) then
    GetPlayer(A0_9).GetScene().GetNpcByNickName("GuChong" .. GetPlayer(A0_9).dwID).PlaySfx(40167, GetPlayer(A0_9).GetScene().GetNpcByNickName("GuChong" .. GetPlayer(A0_9).dwID).nX, GetPlayer(A0_9).GetScene().GetNpcByNickName("GuChong" .. GetPlayer(A0_9).dwID).nY, GetPlayer(A0_9).GetScene().GetNpcByNickName("GuChong" .. GetPlayer(A0_9).dwID).nZ)
    GetPlayer(A0_9).GetScene().GetNpcByNickName("GuChong" .. GetPlayer(A0_9).dwID).Die()
  end
end
function OnTimer(A0_10, A1_11, A2_12)
end
