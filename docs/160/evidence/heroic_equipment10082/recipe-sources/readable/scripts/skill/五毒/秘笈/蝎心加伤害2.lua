---------------------------------------------------------------------->
-- 脚本名称:	scripts/skill/npc/副本BOSS/白帝江关/5号_宇文灭/Test.lua
-- 更新时间:	2021/1/7 10:52:16
-- 更新用户:	KING-20180801IV
-- 脚本说明:	
----------------------------------------------------------------------<

--------------脚本文件开始------------------------------------------------
Include("scripts/Include/Skill.lh")
--批量替换skill脚本Include("scripts/Include/Player.lh")
--设置武功技能级别相关数值

tSkillRecipeData = 
{	


};


--设置武功技能级别相关数值
function GetSkillRecipeData(skill, SkillRecipeID, SkillRecipeLevel)

	local bRetCode = false;
	local nRecipeLevel = SkillRecipeLevel;
	if skill.dwSkillID == 13476 then
	
	skill.nChannelInterval = skill.nChannelInterval * 1.2; 	--这里是加20 脚本名字错了
	end
	
	return true;
end

