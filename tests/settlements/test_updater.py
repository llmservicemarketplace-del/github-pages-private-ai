import importlib.util, pathlib, unittest
p=pathlib.Path(__file__).resolve().parents[2]/"tools/update_settlements.py"
spec=importlib.util.spec_from_file_location("updater",p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class UpdaterTests(unittest.TestCase):
    def test_ftc_links_require_official_host_and_table(self):
        b=b'<a href="/enforcement/refunds/fake">Outside table</a><table><a href="/enforcement/refunds/example">Example Refunds</a><a href="https://evil.example/enforcement/refunds/scam">Bad</a></table>'
        self.assertEqual(m.discover(b),[("https://www.ftc.gov/enforcement/refunds/example","Example Refunds")])
    def test_ignores_script_changes_but_keeps_deadline_changes(self):
        self.assertEqual(m.normalized(b'<p>Deadline Dec 29</p><script>1</script>'),m.normalized(b'<p>Deadline Dec 29</p><script>2</script>'))
        self.assertNotEqual(m.normalized(b'<p>Deadline Dec 29</p>'),m.normalized(b'<p>Deadline Dec 30</p>'))
    def test_pdf_hash_uses_exact_bytes(self):
        self.assertEqual(m.normalized(b'%PDF-1.7 binary'),b'%PDF-1.7 binary')
if __name__=="__main__":unittest.main()

from unittest.mock import patch
import tempfile, json, hashlib
class RefreshTests(unittest.TestCase):
    def exercise(self, failure=False):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder); data=root/'data.json'; page=root/'page.html'
            record=dict(id='example',title='Example',type='settlement',summary='Summary',eligibility='Eligibility',official_url='https://example.org',source_url='https://example.org/source',source_hash=hashlib.sha256(b'original').hexdigest(),review_status='verified',last_checked='2026-01-01T00:00:00Z')
            data.write_text(json.dumps(dict(records=[record])),encoding='utf-8')
            page.write_text('<div><!-- LISTINGS_START --><!-- LISTINGS_END --></div><script id="settlement-data" type="application/json">{}</script>',encoding='utf-8')
            ftc=('<table>'+''.join('<a href="/enforcement/refunds/test-'+str(i)+'">Test Refund '+str(i)+'</a>' for i in range(5))+'</table>').encode()
            def fake_fetch(url):
                if url==m.FTC:return ftc,'text/html'
                if failure:raise OSError('offline')
                return b'<p>changed deadline</p>','text/html'
            with patch.object(m,'DATA',data),patch.object(m,'PAGE',page),patch.object(m,'fetch',fake_fetch):
                code=m.update()
            result=json.loads(data.read_text()); embedded=page.read_text().split('type="application/json">')[1].split('</script>')[0]
            self.assertEqual(len(json.loads(embedded)['records']),6)
            return code,result['records'][0]
    def test_source_change_requires_review(self):
        code,r=self.exercise();self.assertEqual(code,0);self.assertEqual(r['review_status'],'needs_review');self.assertIn('change_detected_at',r)
    def test_failure_preserves_last_success(self):
        code,r=self.exercise(True);self.assertEqual(code,1);self.assertEqual(r['last_checked'],'2026-01-01T00:00:00Z');self.assertIn('check_error',r)
