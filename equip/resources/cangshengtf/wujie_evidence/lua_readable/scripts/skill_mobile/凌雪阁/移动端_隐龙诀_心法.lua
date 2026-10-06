Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    DecriticalDamagePowerBase = 25,
    nMaxMana = 531,
    nPhysicsAttackPower = 816,
    nPhysicsHit = 9,
    nPhysicsOvercome = 14
  },
  {
    DecriticalDamagePowerBase = 44,
    nMaxMana = 741,
    nPhysicsAttackPower = 916,
    nPhysicsHit = 16,
    nPhysicsOvercome = 20
  },
  {
    DecriticalDamagePowerBase = 70,
    nMaxMana = 1126,
    nPhysicsAttackPower = 1116,
    nPhysicsHit = 25,
    nPhysicsOvercome = 30
  },
  {
    DecriticalDamagePowerBase = 95,
    nMaxMana = 2040,
    nPhysicsAttackPower = 1316,
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
  if A0_0.dwLevel >= 1 and A0_0.dwLevel < 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 90, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 90, 0)
  elseif A0_0.dwLevel >= 5 then
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAGIC_SHIELD, 280, 0)
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_SHIELD_BASE, 280, 0)
  end
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DROP_DEFENCE, 250, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH, tSkillData[A0_0.dwLevel].nMaxMana / 240, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MANA_REPLENISH_EXT, tSkillData[A0_0.dwLevel].nMaxMana / 1200, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ACTIVE_THREAT_COEFFICIENT, 0, -819)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_ATTACK_POWER_COF, 737, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.AGILITY_TO_PHYSICS_OVERCOME_COF, 31, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.VITALITY_TO_MAX_MANA_COF, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.BEAT_BACK_RATE, -819, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.MAX_MANA_BASE, 0, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_OVERCOME_BASE, tSkillData[A0_0.dwLevel].nPhysicsOvercome, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.PHYSICS_ATTACK_POWER_BASE, tSkillData[L3_2].nPhysicsAttackPower, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 639, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SKILL_EVENT_HANDLER, 640, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.ALL_SHIELD_IGNORE_PERCENT, 614, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.DST_NPC_DAMAGE_COEFFICIENT, tSkillKungfuConst.LOGIC.NPC[101173], 1)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.KUNGFU_TYPE, PLAYER_ARENA_TYPE.DPS, 0)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_ADAPTIVE_SKILL_TYPE, SKILL_KIND_TYPE.PHYSICS, SKILL_KIND_TYPE.PHYSICS)
  A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.EXECUTE_SCRIPT, "skill_mobile/凌雪阁/移动端_隐龙诀_心法.lua", 0)
  AdditionalAttribute(A0_0)
  return true
end
function CanCast(A0_3, A1_4)
  return A1_4
end
function OnSkillLevelUp(A0_5, A1_6)
  if not A1_6.GetKungfuMount() then
    A1_6.MountKungfu(A0_5.dwSkillID, A0_5.dwLevel)
  end
  A1_6.AddSkillRecipe(17012, 1)
  A1_6.AddSkillRecipe(17013, 1)
  A1_6.AddSkillRecipe(17014, 1)
  A1_6.AddSkillRecipe(17015, 1)
  A1_6.AddSkillRecipe(17016, 1)
  A1_6.AddSkillRecipe(17017, 1)
  A1_6.AddSkillRecipe(17018, 1)
  A1_6.AddSkillRecipe(17019, 1)
  A1_6.AddSkillRecipe(17020, 1)
  A1_6.AddSkillRecipe(17021, 1)
  A1_6.AddSkillRecipe(17022, 1)
  A1_6.AddSkillRecipe(17023, 1)
  A1_6.AddSkillRecipe(17024, 1)
  A1_6.AddSkillRecipe(17025, 1)
  A1_6.AddSkillRecipe(17026, 1)
  A1_6.AddSkillRecipe(17027, 1)
  A1_6.AddSkillRecipe(17028, 1)
  A1_6.AddSkillRecipe(17029, 1)
  A1_6.AddSkillRecipe(17030, 1)
  A1_6.AddSkillRecipe(17031, 1)
end
function Apply(A0_7)
  if GetPlayer(A0_7) then
    GetPlayer(A0_7).AddBuff(GetPlayer(A0_7).dwID, GetPlayer(A0_7).nLevel, 14275, 1)
    GetPlayer(A0_7).bSurplusAutoCast = false
    GetPlayer(A0_7).bSurplusAutoReplenish = false
    if GetPlayer(A0_7).GetSkillLevel(102732) == 0 then
      GetPlayer(A0_7).LearnSkillLevel(102732, 1, false)
    end
  end
end
function UnApply(A0_8)
  local L1_9
end
function OnTimer(A0_10, A1_11, A2_12)
end
