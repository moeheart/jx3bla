import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace as NS

from data.ReplayLibrary import ReplayLibrary, discover_recorders, fingerprint, list_logs, signature


class LibraryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.path = self.root/'record.jcl'
        self.path.write_bytes(b'example')
        self.stamp = fingerprint(self.path)
        self.library = ReplayLibrary(self.root/'cache'/'replays.sqlite3')
        self.result = NS(bossAnalyseName='首领',mapDetail='副本',server='服',timestamp=10,
                         battleTime=1000,win=1,mask=False,statDict=[dict(name='队友',occ='2h')],
                         occResult={'队友':{'result':{'overall':{}}}},potList=[],
                         bh=NS(log={'environment':[]},startTime=50,finalTime=1050))
        self.session = NS(playerEquipment={'42':{'slot':'weapon'}},playerEquipmentAnalysed={},
                          playerEquipmentOwners={'42':('服','队友')})

    def test_directory_discovery_lists_every_role_and_duplicate_names(self):
        data = self.root/'MY#DATA'
        for account, names in [('first',('全名','同名')),('second',('同名',))]:
            for role in names:
                (data/account/role).mkdir(parents=True)
            (data/account/'userdata/combat_logs').mkdir(parents=True)
            (data/account/'config').mkdir()
        self.assertCountEqual(discover_recorders(str(data),'jcl'),
            [('全名',data/'first/userdata/combat_logs'),('同名',data/'first/userdata/combat_logs'),
             ('同名',data/'second/userdata/combat_logs')])

    def test_restart_restores_notes_ids_and_equipment_without_raw_log(self):
        self.library.save(self.path,self.stamp,'v',self.result,self.session)
        self.result.potList.append(['队友','2h',0,'首领','[手动] 测试',[],1])
        self.result.occResult['队友']['result']['overall']['shortID']=12
        self.library.save_notes(self.path,self.stamp,'v',self.result)
        reopened = ReplayLibrary(self.library.path)
        files = list_logs(self.root)
        self.assertEqual(reopened.summaries(self.root,files,'v')[self.path].potList,self.result.potList)
        restored, equipment = reopened.load(self.path,self.stamp,'v')
        self.assertEqual(restored.occResult,self.result.occResult)
        self.assertEqual(restored.bh.startTime,50)
        self.assertEqual(equipment[2],self.session.playerEquipmentOwners)
        self.assertIsNone(reopened.load(self.path,self.stamp,'changed-settings'))
        annotations = reopened.annotations(self.path, self.stamp)
        self.assertEqual((annotations.potList, annotations.links), (self.result.potList, {'队友': 12}))
        self.path.write_bytes(b'changed log')
        self.assertEqual(reopened.summaries(self.root,list_logs(self.root),'v'),{})
        self.assertIsNone(reopened.load(self.path,fingerprint(self.path),'v'))
        self.assertIsNone(reopened.annotations(self.path, fingerprint(self.path)))

    def test_unreadable_cached_payload_can_be_reanalysed(self):
        self.library.save(self.path,self.stamp,'v',self.result,self.session)
        with closing(sqlite3.connect(self.library.path)) as db, db:
            db.execute('update replay set result=?',(b'bad',))
        self.assertIsNone(self.library.load(self.path,self.stamp,'v'))

    def test_equipment_context_is_limited_to_earlier_valid_logs_of_the_same_raid(self):
        files = [self.root / f'2026-11-26-14-{minute:02}-00-洛阳(835)-首领.jcl' for minute in (7,14,20)]
        for i, path in enumerate(files):
            path.write_bytes(b'record')
            self.session.playerEquipment = {'42':str(i)}
            self.library.save(path,fingerprint(path),'v',self.result,self.session)
        self.assertIsNone(self.library.previous_equipment(files[0],'v'))
        self.assertEqual(self.library.previous_equipment(files[2],'v')[0],{'42':'1'})
        self.assertIsNone(self.library.previous_equipment(files[2],'v',after=files[1]))
        files[1].write_bytes(b'replaced')
        self.assertEqual(self.library.previous_equipment(files[2],'v')[0],{'42':'0'})

    def test_recording_selection_does_not_invalidate_shared_account_results(self):
        config = NS(item={'general':{'playername':'甲','mask':0}, 'actor':{'active':1}})
        first = signature(config)
        config.item['general']['playername']='乙'
        self.assertEqual(signature(config),first)
        config.item['general']['mask']=1
        self.assertNotEqual(signature(config),first)
