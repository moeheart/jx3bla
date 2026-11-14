---------------------------------------------------------------------->
-- 脚本名称:	scripts/skill_mobile/移动端-通用/通用/移动端_装备效果_释放绝技招式后伤害提高.lua
-- 更新时间:	2024/4/10 17:09:41
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
	local nRecipeLevel = SkillRecipeLevel;

		skill.AddAttribute(
			ATTRIBUTE_EFFECT_MODE.EFFECT_TO_SELF_AND_ROLLBACK, -- 属性作用模式
			ATTRIBUTE_TYPE.EXECUTE_SCRIPT_WITH_PARAM, -- 魔法属性
			"skill_mobile/移动端-通用/通用/移动端_装备效果_释放绝技招式后伤害提高.lua", -- 属性值1
			skill.dwSkillID															-- 属性值2
		);
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

function Apply(dwCharacterID, dwSkillID, dwSkillSrcID)
	local player = GetPlayer(dwCharacterID)
	if not player then
		return
	end
	if dwSkillID == 101934 then
		return
	end
	if dwSkillID == 101370 then
		player.SetTimer(1, "scripts/skill_mobile/移动端-通用/通用/移动端_装备效果_释放绝技招式后伤害提高.lua", 0, 0)
	else
		player.CastSkillNoChangeTarget(102255, 1)--放增伤技能（竞技场无效）
	end
end

--魔法属性反应用时的执行函数,dwCharacterID是魔法属性作用的目标ID
function UnApply(dwCharacterID)
end

function OnTimer(player, n1, n2)
	player.CastSkillNoChangeTarget(102255, 1)--放增伤技能（竞技场无效）
end