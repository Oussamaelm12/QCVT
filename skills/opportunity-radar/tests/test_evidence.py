import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from evidence import merge

class EvidenceTests(unittest.TestCase):
    def test_dedup_and_no_validation(self):
        apple={"source":"Apple iTunes Search API","apps":[{"id":11,"name":"Example","url":"https://apps.apple.com/app/id11"},{"id":11,"name":"Example","url":"https://apps.apple.com/app/id11"}]}
        hn={"source":"Hacker News via Algolia public API","results":[{"id":"22","title":"Ask HN","discussion_url":"https://news.ycombinator.com/item?id=22"}]}
        result=merge([apple,hn])
        self.assertEqual(result["record_count"],2)
        self.assertEqual(result["source_count"],2)
        self.assertFalse(result["validation_ready"])
        self.assertTrue(all(r["evidence_class"]=="UNREVIEWED" for r in result["records"]))
    def test_rejects_untrusted_links(self):
        bad={"source":"Hacker News via Algolia public API","results":[{"id":"1","discussion_url":"javascript:alert(1)"}]}
        result=merge([bad])
        self.assertEqual(result["record_count"],0)
        self.assertEqual(len(result["issues"]),1)
    def test_unknown_source(self):
        self.assertEqual(merge([{"source":"Fake","apps":[]}])["source_count"],0)

if __name__=="__main__": unittest.main()
