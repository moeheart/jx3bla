---------------------------------------------------------------------->
-- 脚本名称:	scripts/skill/五毒/秘笈/蛇影加伤害10.lua
-- 更新时间:	2018/5/30 19:21:01
-- 更新用户:	chenchen6-pc
-- 脚本说明:
----------------------------------------------------------------------<
------------------------------------------------
-- 文件名    :  增加会心2分.lua
-- 创建人    :  CBG
-- 创建时间  :  2009-08-04
-- 用途(模块):  武功技能
-- 武功门派  :  通用
-- 武功类型  :  秘笈
-- 武功套路  :
-- 技能名称  :
-- 技能效果  :  增加会心2%
------------------------------------------------

--------------脚本文件开始------------------------------------------------

Include("scripts/Include/Skill.lh")
--批量替换skill脚本Include("scripts/Include/Player.lh")

tSkillRecipeData =
{
	{ CriticalPecent = 200},

};

--设置武功技能级别相关数值
function GetSkillRecipeData(skill, SkillRecipeID, SkillRecipeLevel)

	local nRecipeLevel = SkillRecipeLevel;
	skill.nChannelInterval = skill.nChannelInterval * 1.1
	return true;

end

--对技能执行的特殊条件检查，该函数可以在开始施放技能的时候被调用，以确定是否可以施放该机能
--Player: 技能施放者
--nPreResult: 程序里面按照一般流程判断的结果，注意，最终以脚本返回的结果为准
function CanCast(player, nPreResult)
--判断玩家的状态，以判断是否可以发出技能
	return nPreResult;
end

function CanLearnSkill(skill, player)
	return true
end

function OnSkillLevelUp(skill, player)
end