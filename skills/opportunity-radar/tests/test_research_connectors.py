import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from research_connectors import search,ENDPOINTS

class FakeResponse:
 def __init__(self,url,payload):self.url=url;self.payload=payload
 def __enter__(self):return self
 def __exit__(self,*args):return False
 def geturl(self):return self.url
 def read(self,n):return json.dumps(self.payload).encode("utf-8")

class ResearchConnectorTests(unittest.TestCase):
 def test_network_off_by_default(self):
  with self.assertRaises(PermissionError):search("openalex","topic")
 def test_reject_bad_provider(self):
  with self.assertRaises(ValueError):search("unknown","topic",allow_network=True)
 def test_reject_unbounded_query_and_limits(self):
  with self.assertRaises(ValueError):search("openalex","a"*201,allow_network=True)
  with self.assertRaises(ValueError):search("crossref","topic",100,True)
 def test_openalex_metadata_is_not_validated_demand(self):
  payload={"results":[{"id":"https://openalex.org/W123","doi":"https://doi.org/10.1234/test","title":"Example paper","publication_year":2023}]}
  with patch("research_connectors.urllib.request.urlopen",return_value=FakeResponse(ENDPOINTS["openalex"],payload)):
   r=search("openalex","topic",allow_network=True)
  self.assertEqual(r["results"][0]["review_status"],"unchecked")
  self.assertEqual(r["results"][0]["claim_status"],"SOURCE_DISCOVERY_ONLY")
 def test_crossref_extract(self):
  payload={"message":{"items":[{"DOI":"10.1234/example","title":["Example"],"published":{"date-parts":[[2024,1]]},"URL":"https://doi.org/10.1234/example"}]}}
  with patch("research_connectors.urllib.request.urlopen",return_value=FakeResponse(ENDPOINTS["crossref"],payload)):
   r=search("crossref","topic",allow_network=True)
  self.assertEqual(r["results"][0]["publication_year"],2024)
 def test_redirect_host_rejected(self):
  with patch("research_connectors.urllib.request.urlopen",return_value=FakeResponse("https://evil.example/",{"results":[]})):
   with self.assertRaises(ValueError):search("openalex","topic",allow_network=True)
if __name__=="__main__":unittest.main()
