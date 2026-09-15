Include("scripts/Include/Skill.lh")
Include("scripts/skill/include/kungfuConst.lh")
tSkillData = {
  {
    nMP = 703,
    nPhysicsDefence = 27,
    nMagicDefence = 27,
    nDodge = 53,
    nPhysicsCri = 5,
    nPhysicsHit = 4
  },
  {
    nMP = 982,
    nPhysicsDefence = 37,
    nMagicDefence = 37,
    nDodge = 75,
    nPhysicsCri = 6,
    nPhysicsHit = 5
  },
  {
    nMP = 1491,
    nPhysicsDefence = 57,
    nMagicDefence = 57,
    nDodge = 113,
    nPhysicsCri = 9,
    nPhysicsHit = 7
  },
  {
    nMP = 2000,
    nPhysicsDefence = 76,
    nMagicDefence = 76,
    nDodge = 152,
    nPhysicsCri = 11,
    nPhysicsHit = 9
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  },
  {
    nMP = 703,
    nPhysicsDefence = 27,
    nMagicDefence = 27,
    nDodge = 53,
    nPhysicsCri = 5,
    nPhysicsHit = 4
  },
  {
    nMP = 982,
    nPhysicsDefence = 37,
    nMagicDefence = 37,
    nDodge = 75,
    nPhysicsCri = 6,
    nPhysicsHit = 5
  },
  {
    nMP = 1491,
    nPhysicsDefence = 57,
    nMagicDefence = 57,
    nDodge = 113,
    nPhysicsCri = 9,
    nPhysicsHit = 7
  },
  {
    nMP = 2000,
    nPhysicsDefence = 76,
    nMagicDefence = 76,
    nDodge = 152,
    nPhysicsCri = 11,
    nPhysicsHit = 9
  },
  {
    nMP = 6000,
    nPhysicsDefence = 228,
    nMagicDefence = 228,
    nDodge = 457,
    nPhysicsCri = 13,
    nPhysicsHit = 11
  }
}
function GetSkillLevelData(A0_0)
  local L1_1, L2_2, L3_3, L4_4, L5_5
  L1_1 = A0_0.dwLevel
  L5_5 = PLAYER_ARENA_TYPE
  L5_5 = L5_5.T
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = "skill/明教/明教_套路_内功_明尊琉璃体.lua"
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 1865
  L2_2(L3_3, L4_4, L5_5, 0)
  if L1_1 >= 1 and L1_1 < 5 then
    L5_5 = 90
    L2_2(L3_3, L4_4, L5_5, 0)
    L5_5 = 90
    L2_2(L3_3, L4_4, L5_5, 0)
  elseif L1_1 >= 5 then
    L5_5 = 280
    L2_2(L3_3, L4_4, L5_5, 0)
    L5_5 = 280
    L2_2(L3_3, L4_4, L5_5, 0)
  end
  L5_5 = 1711
  L2_2(L3_3, L4_4, L5_5, 1)
  L5_5 = 250
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 2253
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 1280
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 164
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = -1024
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 10000
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 10000
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 163
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 163
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 51.2
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = tSkillData
  L5_5 = L5_5[L1_1]
  L5_5 = L5_5.nDodge
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = tSkillData
  L5_5 = L5_5[L1_1]
  L5_5 = L5_5.nMagicDefence
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = tSkillData
  L5_5 = L5_5[L1_1]
  L5_5 = L5_5.nPhysicsDefence
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 1024
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 11776
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = SKILL_KIND_TYPE
  L5_5 = L5_5.LUNAR_MAGIC
  L2_2(L3_3, L4_4, L5_5, SKILL_KIND_TYPE.LUNAR_MAGIC)
  L5_5 = 639
  L2_2(L3_3, L4_4, L5_5, 0)
  L5_5 = 640
  L2_2(L3_3, L4_4, L5_5, 0)
  for L5_5 = 1154, 1163 do
    A0_0.AddAttribute(ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, ATTRIBUTE_TYPE.SET_TALENT_RECIPE, L5_5, 1)
  end
  L5_5 = 0
  L2_2(L3_3, L4_4, L5_5, 512)
  L5_5 = 1296
  L2_2(L3_3, L4_4, L5_5, 1)
  L5_5 = 1335
  L2_2(L3_3, L4_4, L5_5, 1)
  L5_5 = 1336
  L2_2(L3_3, L4_4, L5_5, 1)
  L5_5 = 1337
  L2_2(L3_3, L4_4, L5_5, 1)
  L5_5 = 1338
  L2_2(L3_3, L4_4, L5_5, 1)
  L5_5 = 1339
  L2_2(L3_3, L4_4, L5_5, 1)
  L5_5 = 1340
  L2_2(L3_3, L4_4, L5_5, 1)
  L5_5 = 2622
  L2_2(L3_3, L4_4, L5_5, 0)
  return L2_2
end
function CanCast(A0_6, A1_7)
  return A1_7
end
function OnSkillLevelUp(A0_8, A1_9)
  local L2_10, L3_11
  L2_10 = A1_9.GetKungfuMountID
  L2_10 = L2_10()
  if not L2_10 then
    L3_11 = A1_9.MountKungfu
    L3_11(A0_8.dwSkillID, A0_8.dwLevel)
  end
  L3_11 = A0_8.dwLevel
  if A1_9.dwForceID == 10 and A1_9.GetSkillLevel(10240) < 1 then
    A1_9.LearnSkill(10240)
  end
  A1_9.LearnSkillLevel(4260, L3_11, A1_9.dwID)
  A1_9.LearnSkill(4261)
  A1_9.LearnSkill(4432)
end
function Apply(A0_12)
  if not GetPlayer(A0_12) then
    return
  end
  GetPlayer(A0_12).AddBuff(GetPlayer(A0_12).dwID, GetPlayer(A0_12).nLevel, 14275, 1)
  GetPlayer(A0_12).bSurplusAutoCast = false
  GetPlayer(A0_12).bSurplusAutoReplenish = false
  GetPlayer(A0_12).nCurrentSunEnergy = 0
  GetPlayer(A0_12).nCurrentMoonEnergy = 0
  GetPlayer(A0_12).nSunPowerValue = 0
  GetPlayer(A0_12).nMoonPowerValue = 0
  GetPlayer(A0_12).DelMultiGroupBuffByID(30270)
  GetPlayer(A0_12).AddBuff(A0_12, GetPlayer(A0_12).nLevel, 30270, 1)
end
function UnApply(A0_13)
  if not GetPlayer(A0_13) then
    return
  end
  GetPlayer(A0_13).nCurrentSunEnergy = 0
  GetPlayer(A0_13).nCurrentMoonEnergy = 0
  GetPlayer(A0_13).nSunPowerValue = 0
  GetPlayer(A0_13).nMoonPowerValue = 0
  GetPlayer(A0_13).DelMultiGroupBuffByID(30270)
end
function OnTimer(A0_14, A1_15, A2_16)
end
