local L0_0
L0_0 = Include
L0_0("scripts/Include/NewSkill.lh")
L0_0 = {}
L0_0[2432] = {33295, 1}
L0_0[2433] = {33324, 1}
L0_0[2434] = {33318, 1}
L0_0[2435] = {33317, 1}
L0_0[2436] = {33316, 1}
L0_0[2758] = {1854, 8}
L0_0[2747] = {1855, 8}
L0_0[2740] = {1856, 8}
L0_0[2751] = {33295, 2}
L0_0[2741] = {1850, 8}
L0_0[2742] = {1851, 8}
L0_0[2739] = {1853, 8}
L0_0[2753] = {1852, 8}
L0_0[2719] = {1858, 8}
L0_0[2720] = {33324, 2}
L0_0[2717] = {3065, 8}
L0_0[2721] = {33318, 2}
L0_0[2736] = {3477, 8}
L0_0[2737] = {3476, 8}
L0_0[2744] = {1881, 8}
L0_0[2743] = {1882, 8}
L0_0[2738] = {6950, 8}
L0_0[2759] = {4940, 8}
L0_0[2760] = {4941, 8}
L0_0[2754] = {13410, 15}
L0_0[2755] = {13410, 16}
L0_0[2718] = {15183, 8}
L0_0[2722] = {33317, 2}
L0_0[2761] = {16984, 8}
L0_0[2749] = {21185, 8}
L0_0[2745] = {23396, 8}
L0_0[2756] = {25831, 8}
L0_0[2762] = {29694, 8}
L0_0[2752] = {33316, 2}
L0_0[2757] = {33238, 3}
L0_0[2746] = {36578, 3}
L0_0[2724] = {39078, 2}
L0_0[2943] = {43080, 1}
L0_0[3243] = {1854, 9}
L0_0[3244] = {1855, 9}
L0_0[3245] = {1856, 9}
L0_0[3246] = {33295, 3}
L0_0[3247] = {1850, 9}
L0_0[3248] = {1851, 9}
L0_0[3249] = {1853, 9}
L0_0[3250] = {1852, 9}
L0_0[3251] = {1858, 9}
L0_0[3252] = {33324, 3}
L0_0[3253] = {3065, 9}
L0_0[3254] = {33318, 3}
L0_0[3255] = {3477, 9}
L0_0[3256] = {3476, 9}
L0_0[3257] = {1881, 9}
L0_0[3258] = {1882, 9}
L0_0[3259] = {6950, 9}
L0_0[3260] = {4940, 9}
L0_0[3261] = {4941, 9}
L0_0[3262] = {13410, 19}
L0_0[3263] = {13410, 20}
L0_0[3264] = {15183, 9}
L0_0[3265] = {33317, 3}
L0_0[3266] = {16984, 9}
L0_0[3267] = {21185, 9}
L0_0[3268] = {23396, 9}
L0_0[3269] = {25831, 9}
L0_0[3270] = {29694, 9}
L0_0[3271] = {33316, 3}
L0_0[3272] = {33238, 9}
L0_0[3273] = {36578, 9}
L0_0[3274] = {39078, 9}
L0_0[3275] = {43080, 2}
function OnUse(A0_1, A1_2, A2_3, A3_4, A4_5, A5_6)
  if not A0_1 then
    return false, false, true
  end
  if not A1_2 or GetOrangeWeaponSceneMode(A0_1) ~= tOrangeWeaponSceneMode.ACTIVE then
    RemoteCallToClient(A0_1.dwID, "OnOutputWarningMessage", "MSG_NOTICE_RED", GetEditorString(11, 3929), 4)
    return false, false, true
  end
  if not GetItemInfo(A1_2.dwTabType, A1_2.dwIndex) then
    return false, false, true
  end
  if _UPVALUE0_(A0_1, GetItemInfo(A1_2.dwTabType, A1_2.dwIndex).dwCoolDownID) then
    RemoteCallToClient(A0_1.dwID, "OnOutputWarningMessage", "MSG_NOTICE_RED", GetEditorString(10, 2186), 4)
    return false, false, true
  end
  return true, false, false
end
function OnSkillEvent(A0_7, A1_8, A2_9, A3_10, A4_11)
  local L5_12, L6_13
  L5_12 = _UPVALUE0_
  L5_12 = L5_12[A4_11]
  if not L5_12 then
    return
  end
  L6_13 = GetPlayer
  L6_13 = L6_13(A0_7)
  if not L6_13 then
    return
  end
  if GetOrangeWeaponSceneMode(L6_13) ~= tOrangeWeaponSceneMode.PASSIVE then
    return
  end
  if _UPVALUE1_(L6_13) then
    return
  end
  L6_13.ResetCD(_UPVALUE2_)
  L6_13.CastSkillNoChangeTarget(L5_12[1], L5_12[2], TARGET.PLAYER, L6_13.dwID)
end
function Apply(A0_14)
  local L1_15
  L1_15 = GetPlayer
  L1_15 = L1_15(A0_14)
  if not L1_15 then
    return
  end
  if GetOrangeWeaponSceneMode(L1_15) ~= tOrangeWeaponSceneMode.ACTIVE then
    return
  end
  if L1_15.GetOTActionState() == CHARACTER_OTACTION_TYPE.ACTION_SKILL_PREPARE or L1_15.GetOTActionState() == CHARACTER_OTACTION_TYPE.ACTION_SKILL_CHANNEL or L1_15.GetOTActionState() == CHARACTER_OTACTION_TYPE.ACTION_SKILL_HOARD then
    L1_15.CastSkillNoChangeTarget(46965, 1, TARGET.PLAYER, L1_15.dwID)
  end
end
