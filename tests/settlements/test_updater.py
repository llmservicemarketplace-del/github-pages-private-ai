import importlib.util,pathlib,unittest,hashlib
from unittest.mock import patch
p=pathlib.Path(__file__).resolve().parents[2]/'tools/update_settlements.py'
spec=importlib.util.spec_from_file_location('updater',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class UpdaterTests(unittest.TestCase):
 def test_no_script_changes(self):
  self.assertEqual(m.normalized(b'<p>Deadline</p><script>1</script>'),m.normalized(b'<p>Deadline</p><script>2</script>'))
 def test_claim_deadline_only(self):
  self.assertEqual(m.claim_deadline('Claim Deadline: November 27, 2026'),'2026-11-27')
  self.assertIsNone(m.claim_deadline('Final hearing November 27, 2026'))
  self.assertIsNone(m.claim_deadline('Claim Deadline: November 27, 2026','2026-11-28'))
 def test_ftc_followup_is_not_open(self):
  self.assertEqual(m.classify_ftc('We are sending an additional payment to people who cashed their first payment.'),'follow_up')
  self.assertEqual(m.classify_ftc('We will send automatic refunds.'),'automatic')
 def test_ftc_discovery_requires_official_table(self):
  html=b'<a href="/enforcement/refunds/outside">outside</a><table><a href="/enforcement/refunds/real">Real Refunds</a><a href="https://evil.example/enforcement/refunds/fake">Fake</a></table>'
  with patch.object(m,'fetch',return_value=(html,'text/html','https://www.ftc.gov/enforcement/refunds')):
   rows=m.discover_source(dict(id='ftc',kind='ftc',url='https://www.ftc.gov/enforcement/refunds'))
  self.assertEqual(len(rows),1);self.assertIn('/real',rows[0]['official_url']);self.assertEqual(rows[0]['availability'],'needs_review')
 def test_failed_check_preserves_success(self):
  r=dict(source_url='https://example.org',last_checked='2026-01-01',review_status='verified')
  with patch.object(m,'fetch',side_effect=OSError('offline')):out=m.check_record(r)
  self.assertEqual(out['last_checked'],'2026-01-01');self.assertEqual(out['source_status'],'unavailable')
 def test_notice_change_requires_review(self):
  body=('<p>Changed court notice. '+('Eligibility rules. '*15)+'</p>').encode()
  r=dict(source_url='https://example.org',source_hash='old',review_status='verified')
  with patch.object(m,'fetch',return_value=(body,'text/html','https://example.org')):out=m.check_record(r)
  self.assertEqual(out['review_status'],'needs_review')
 def test_discovery_requires_claim_route_and_matching_date(self):
  r=m.base_record('Example','https://example.org','directory');r['deadline_date']='2099-11-27'
  for html in [b'<p>Claim Deadline: November 27, 2099</p>',b'<a href="/claim">File a Claim</a><p>Final hearing November 27, 2099</p>']:
   with patch.object(m,'fetch',return_value=(html,'text/html','https://example.org')):out=m.verify_lead(dict(r))
   self.assertEqual(out['availability'],'needs_review')
  html=b'<a href="/claim">File a Claim</a><p>Claim Deadline: November 27, 2099</p>'
  with patch.object(m,'fetch',return_value=(html,'text/html','https://example.org')):out=m.verify_lead(dict(r))
  self.assertEqual(out['availability'],'new_claims');self.assertIsNone(out['receipt_required']);self.assertEqual(out['states'],['UNKNOWN'])
if __name__=='__main__':unittest.main()
