local L1_0
function L1_0(A0_1)
  local L1_2, L2_3, L3_4, L4_5, L5_6, L6_7, L7_8
  L1_2 = GetPlayer
  L2_3 = A0_1
  L1_2 = L1_2(L2_3)
  if not L1_2 then
    return
  end
  L2_3 = 0
  if L3_4 then
    for L6_7 = 1, 5 do
      L7_8 = L1_2.IsHaveBuff
      L7_8 = L7_8(12778 + L6_7, 1)
      if L7_8 then
        L2_3 = L6_7
        break
      end
    end
    if L2_3 == 0 then
      return
    end
    if L3_4 then
      if L4_5 == 1 then
        return
      end
    end
    if L4_5 == 1 then
      return
    end
    if L4_5 == 1 then
      if L3_4 then
        L6_7 = 12
        if L4_5 == 0 then
          L6_7 = 18641
          L7_8 = L2_3
          L5_6(L6_7, L7_8)
        end
      end
    else
      L6_7 = GetNpc
      L7_8 = L5_6
      L6_7 = L6_7(L7_8)
      if not L6_7 then
        L6_7 = GetPlayer
        L7_8 = L5_6
        L6_7 = L6_7(L7_8)
      end
      if not L6_7 then
        return
      end
      if L3_4 then
        L7_8 = nil
        if L1_2.GetSkillLevel(18669) == 1 then
          L7_8 = math.fmod(L3_4.nLeftActiveCount, 9)
        else
          L7_8 = math.fmod(L3_4.nLeftActiveCount, 12)
        end
        if L7_8 == 0 then
          L1_2.CastSkill(18667, L2_3, L4_5, L5_6)
        end
      end
    end
  else
    for L6_7 = 1, 5 do
      L7_8 = L1_2.IsHaveBuff
      L7_8 = L7_8(12499 + L6_7, 1)
      if L7_8 then
        L2_3 = L6_7
        break
      end
    end
    if L2_3 == 0 then
      return
    end
    if L3_4 then
      if L4_5 == 1 then
        return
      end
    end
    if L4_5 == 1 then
      return
    end
    if L4_5 == 1 then
      if L3_4 then
        L6_7 = 12
        if L4_5 == 0 then
          L6_7 = 18641
          L7_8 = L2_3
          L5_6(L6_7, L7_8)
        end
      end
    else
      L6_7 = GetNpc
      L7_8 = L5_6
      L6_7 = L6_7(L7_8)
      if not L6_7 then
        L6_7 = GetPlayer
        L7_8 = L5_6
        L6_7 = L6_7(L7_8)
      end
      if not L6_7 then
        return
      end
      if L3_4 then
        L7_8 = nil
        if L1_2.GetSkillLevel(18669) == 1 then
          L7_8 = math.fmod(L3_4.nLeftActiveCount, 9)
        else
          L7_8 = math.fmod(L3_4.nLeftActiveCount, 12)
        end
        L1_2.CastSkill(18667, L2_3, L4_5, L5_6)
      end
    end
  end
end
Apply = L1_0
