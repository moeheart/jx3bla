---------------------------------------------------------------------->
-- 脚本名称:	scripts/skill_mobile/移动端-通用/通用/移动端_装备效果_招式威胁值提高.lua
-- 更新时间:	2024/2/1 9:57:39
-- 更新用户:	SK-20220819MWLC
-- 脚本说明:	
----------------------------------------------------------------------<
--------------脚本文件开始------------------------------------------------

Include("scripts/Include/Skill.lh")
--批量替换skill脚本Include("scripts/Include/Player.lh")

tSkillRecipeData =
{

};

--设置武功技能级别相关数值
function GetSkillRecipeData(skill, SkillRecipeID, SkillRecipeLevel)
	skill.nBaseThreat = skill.nBaseThreat * 1.05
	return
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