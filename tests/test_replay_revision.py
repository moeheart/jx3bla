"""Same-version hotfix replacement keeps public URLs and quality protection."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

import test_luoyang_heroic_upload as fixtures
from tools.RecordQuality import get_record_quality, load_record_quality, invalidate_quality_cache
from tools.ReplayRevision import LUOYANG_EFFECTIVE_TIME, mark_recalculation, revision_change


class RevisionReceiptTests(unittest.TestCase):
    setUpClass=classmethod(fixtures.HeroicUploadTests.setUpClass.__func__)
    setUp=fixtures.HeroicUploadTests.setUp
    battle=fixtures.HeroicUploadTests.battle
    replay=fixtures.HeroicUploadTests.replay
    _upload=fixtures.HeroicUploadTests._upload

    def records(self):
        from MainWindow import MainWindow
        window=MainWindow.__new__(MainWindow)
        window.uploadData=[]
        window.setNotice=Mock()
        battle=self.battle(fixtures.MAP,1794576000)
        replay=self.replay(fixtures.MAP,1794576000)
        battle['edition']=replay['edition']=replay['replayedition']='8.16.8'
        replay['editionfull']=self.server.parseEdition('8.16.8')
        battle['statistics']['attributeStatus']={'status':'supported','staticAttributes':'available'}
        replay['statistics']['overall']['attributeStatus']={'status':'supported','staticAttributes':'available'}
        return window,battle,replay

    def send(self,window,battle,replay):
        window.addUploadData({'type':'battle','data':copy.deepcopy(battle),'anchor':None})
        window.addUploadData({'type':'replay','data':copy.deepcopy(replay),'anchor':copy.deepcopy(replay['statistics'])})
        return self._upload(window)[0]

    def test_same_8168_recalculation_replaces_once_and_keeps_id_and_ranks(self):
        window,battle,replay=self.records()
        old=self.send(window,battle,replay)
        identifier=old['data'][1]['shortID']
        for payload in (battle,replay):
            mark_recalculation(payload['statistics'],payload['mapdetail'],payload['boss'])
        replay['statistics']['overall']['sumTimeEff']=9000
        replay['statistics']['skill']['general']['rdps']=2300
        self.server.app.percent_data.update({'lingsu-836-史朝义-stat-%s-161'%metric:
            {'num':101,'value':json.dumps([i*scale for i in range(101)])}
            for metric,scale in (('score',1),('rdps',100))})
        updated=self.send(window,battle,replay)
        self.assertEqual([r['result'] for r in updated['data']],['success','success'])
        self.assertEqual(updated['data'][1]['shortID'],identifier)
        saved=json.loads(self.files['database/ReplayProStat/%d'%identifier])
        self.assertEqual(saved['analysisRevision'],LUOYANG_EFFECTIVE_TIME)
        self.assertEqual(saved['overall']['sumTimeEff'],9000)
        row=self.cursor.replays[replay['hash']]
        for metric in ('score','rdps'):
            self.assertGreaterEqual(row[self.server.RANK_ID[metric]],0)
        stable=dict(self.files)
        repeated=self.send(window,battle,replay)
        self.assertEqual([r['result'] for r in repeated['data']],['dupid','dupid'])
        self.assertEqual(repeated['data'][1]['shortID'],identifier)
        for payload in (battle,replay):
            payload['statistics'].pop('analysisRevision')
        outdated=self.send(window,battle,replay)
        self.assertEqual([r['result'] for r in outdated['data']],['dupid','dupid'])
        self.assertEqual(self.files,stable)

    def test_new_marker_cannot_downgrade_equipment_quality(self):
        window,battle,replay=self.records()
        self.send(window,battle,replay)
        before=dict(self.files)
        for payload in (battle,replay):
            mark_recalculation(payload['statistics'],payload['mapdetail'],payload['boss'])
        battle['statistics']['attributeStatus']={'status':'estimated','staticAttributes':'estimated'}
        replay['statistics']['overall']['attributeStatus']={'status':'estimated','staticAttributes':'estimated'}
        result=self.send(window,battle,replay)
        self.assertEqual([r['result'] for r in result['data']],['dupid','dupid'])
        self.assertEqual(self.files,before)

    def test_team_and_public_updates_cannot_overwrite_a_newer_numbered_release(self):
        window,battle,replay=self.records()
        battle['edition']=replay['edition']=replay['replayedition']='8.16.9'
        replay['editionfull']=self.server.parseEdition('8.16.9')
        battle['team']=''
        replay['public']=0
        for payload in (battle,replay):
            mark_recalculation(payload['statistics'],payload['mapdetail'],payload['boss'])
        self.send(window,battle,replay)
        before=dict(self.files)
        battle['edition']=replay['edition']=replay['replayedition']='8.16.8'
        replay['editionfull']=self.server.parseEdition('8.16.8')
        battle['team']='补全团队'
        replay['public']=1
        for keep_marker in (True,False):
            if not keep_marker:
                for payload in (battle,replay):
                    payload['statistics'].pop('analysisRevision')
            result=self.send(window,battle,replay)
            self.assertEqual([r['result'] for r in result['data']],['dupid','dupid'])
            self.assertEqual(self.files,before)


class RevisionMetadataTests(unittest.TestCase):
    def test_cache_and_quality_round_trip_preserve_only_recognized_fix(self):
        data={'attributeStatus':{'status':'supported'},'analysisRevision':LUOYANG_EFFECTIVE_TIME}
        quality=get_record_quality(data)
        self.assertEqual(get_record_quality(quality),quality)
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'record'
            path.write_text(json.dumps(data),encoding='utf-8')
            self.assertEqual(load_record_quality(path),quality)
            data['analysisRevision']='unknown-future-token'
            path.write_text(json.dumps(data),encoding='utf-8')
            self.assertNotIn('analysisRevision',load_record_quality(path))
            invalidate_quality_cache(path)

    def test_scope_and_numbered_release_policy_are_preserved(self):
        current={'analysisRevision':LUOYANG_EFFECTIVE_TIME}
        args=('25人英雄洛阳之战','史朝义',8016008,8016008)
        self.assertEqual(revision_change({},current,*args),'upgrade')
        self.assertEqual(revision_change(current,{},*args),'downgrade')
        self.assertIsNone(revision_change({},current,'25人英雄阆风悬城','阿史那承庆',8016008,8016008))
        self.assertIsNone(revision_change({},current,'836','未知首领',8016008,8016008))
        self.assertEqual(revision_change({},current,'836','史朝义',8016009,8016008),'downgrade')
        self.assertIsNone(revision_change(current,{},'836','史朝义',8016008,8016009))
        self.assertIsNone(revision_change({}, {'analysisRevision':True}, *args))


if __name__=='__main__':
    unittest.main()
