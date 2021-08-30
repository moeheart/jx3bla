# Created by moeheart at 08/30/2021
# 维护装备信息类.

class EquipmentInfo():
    '''
    装备信息类，包括属性的读取与获得。
    '''

    def getAttribute(self, full_id, attribute):
        '''
        通过带标签的ID获取装备特定的属性。
        params:
        - full_id: 装备带标签的编号，例如6,12345.
        - attribute: 要查找的属性，必须是表头中的一项.
        returns:
        - 属性值
        '''
        if full_id not in self.data:
            return 0
        if attribute not in self.headerID:
            return 0
        return self.data[full_id][self.headerID[attribute]]

    def getFeature(self, full_id):
        '''
        通过装备ID获取关心的所有属性.

        params:
        - full_id: 装备带标签的编号，例如6,12345.
        returns:
        - 字典，为对应的装备属性列表.
        '''

        result = {}
        result["name"] = self.getAttribute(full_id, "Name")
        for i in range(1, 11):
            attribName = "Magic%dType"%i
            attribID = self.getAttribute(full_id, attribName)
            if attribID == "" or attribID == "0":
                break
            print(self.attrib[attribID])

        return {}


    def loadSingleFile(self, path, scene):
        '''
        从文件中读取装备，并打上对应的标签保存在data中.
        params:
        - path: 文件路径
        - scene: 表的编号，可能是6,7,8
        '''
        header = []
        first = True
        with open(path, 'r') as f:
            for line in f:
                if first:
                    header = line.strip('\n').split('\t')
                    first = False
                else:
                    content = line.strip('\n').split('\t')
                    new_id = "%d,%s"%(scene, content[0])
                    self.data[new_id] = content

        for i in range(len(header)):
            self.headerID[header[i]] = i

    def LoadFromStaticData(self):
        '''
        从解包中读取所有装备的属性。
        '''
        TRINKET_PATH = 'equip/resources/Custom_Trinket(0).tab'
        ARMOR_PATH = 'equip/resources/Custom_Armor(0).tab'
        WEAPON_PATH = 'equip/resources/Custom_Weapon(0).tab'
        self.loadSingleFile(TRINKET_PATH, 6)
        self.loadSingleFile(ARMOR_PATH, 7)
        self.loadSingleFile(WEAPON_PATH, 8)

        ATTRIB_PATH='equip/resources/Attrib.tab'
        first = True
        with open(ATTRIB_PATH, 'r') as f:
            for line in f:
                if first:
                    header = line.strip('\n').split('\t')
                    first = False
                else:
                    content = line.strip('\n').split('\t')
                    self.attrib[content[0]] = {content[2]: content[3]}  # 只记录最简单的形式

    def __init__(self):
        self.data = {}
        self.attrib = {}
        self.headerID = {}

if __name__ == "__main__":
    t = EquipmentInfo()
    print("准备读取")
    t.LoadFromStaticData()
    print("读取完成")
    res = t.getAttribute("7,50953", "Name")
    print(res)
    t.getFeature("7,50953")


