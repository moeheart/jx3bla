local L0_0, L4_1
L0_0 = 34580
L4_1 = 12504
function Apply(A0_2)
  if not GetPlayer(A0_2) then
    return
  end
  if GetPlayer(A0_2).GetSkillLevel(_UPVALUE0_) ~= 1 then
    return
  end
  if not GetPlayer(A0_2).GetBuff(_UPVALUE1_, 1) or GetPlayer(A0_2).GetBuff(_UPVALUE1_, 1).nLeftActiveCount >= _UPVALUE2_ then
    return
  end
  if GetPlayer(A0_2).GetBuff(_UPVALUE3_, 1) then
    GetPlayer(A0_2).SetBuffLeftActiveCount(GetPlayer(A0_2).GetBuff(_UPVALUE3_, 1).nIndex, _UPVALUE4_)
    return
  end
  GetPlayer(A0_2).AddBuff(GetPlayer(A0_2).dwID, GetPlayer(A0_2).nLevel, _UPVALUE3_, 1, _UPVALUE4_, _UPVALUE5_)
end
