#!/usr/bin/env python3
"""Read-only primary research connector: OpenAlex scholarly works + Crossref DOI metadata.

Requires explicit --allow-network; default offline. No LLM, secrets or paid APIs.
Results are discovery leads, NOT independent proof of market demand.
"""
import argparse
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime,timezone
from pathlib import Path

ENDPOINTS={
 "openalex":"https://api.openalex.org/works",
 "crossref":"https://api.crossref.org/works"
}
HEADERS={"User-Agent":"OpportunityRadarResearch/1.0 (read-only research; https://github.com/Oussamaelm12/QCVT)",
         "Accept":"application/json"}
MAX_RESULTS=20
MAX_BYTES=1_500_000

def search(provider,query,limit=5,allow_network=False,timeout=12):
 if provider not in ENDPOINTS:raise ValueError("unknown provider")
 if not isinstance(query,str) or not query.strip() or len(query)>200:raise ValueError("query must be 1-200 characters")
 if not isinstance(limit,int) or not 1<=limit<=MAX_RESULTS:raise ValueError("limit out of bounds")
 if not allow_network:raise PermissionError("network disabled; use --allow-network explicitly")
 if provider=="openalex":
  params={"search":query,"per-page":str(limit),"select":"id,doi,title,publication_year,primary_location,authorships"}
 else:
  params={"query":query,"rows":str(limit),"select":"DOI,title,published,URL,publisher,type"}
 url=ENDPOINTS[provider]+"?"+urllib.parse.urlencode(params)
 request=urllib.request.Request(url,headers=HEADERS)
 # urllib redirects are allowed only if final response remains on the expected host.
 with urllib.request.urlopen(request,timeout=timeout) as response:
  final=urllib.parse.urlparse(response.geturl())
  if final.scheme!="https" or final.netloc!=urllib.parse.urlparse(ENDPOINTS[provider]).netloc:
   raise ValueError("unexpected redirect host")
  raw=response.read(MAX_BYTES+1)
 if len(raw)>MAX_BYTES:raise ValueError("provider response exceeds size cap")
 data=json.loads(raw)
 items=data.get("results",[]) if provider=="openalex" else data.get("message",{}).get("items",[])
 if not isinstance(items,list):raise ValueError("unexpected provider response")
 out=[]
 for item in items[:limit]:
  if provider=="openalex":
   doi=item.get("doi")
   title=item.get("title")
   year=item.get("publication_year")
   origin=item.get("id")
  else:
   doi=item.get("DOI")
   title=item.get("title",[])
   title=title[0] if isinstance(title,list) and title else title if isinstance(title,str) else None
   published=item.get("published",{}).get("date-parts",[])
   year=published[0][0] if published and published[0] else None
   origin=item.get("URL")
  if not isinstance(title,str) or not title.strip():continue
  out.append({"title":title.strip()[:500],"doi":doi,"publication_year":year,
              "record_url":origin,"provider":provider,
              "review_status":"unchecked","claim_status":"SOURCE_DISCOVERY_ONLY"})
 return {"provider":provider,"query":query,"captured_at":datetime.now(timezone.utc).isoformat(),
         "endpoint":ENDPOINTS[provider],"results":out,
         "limitations":["Metadata only; full text and original assertions not checked.",
                        "Search results are not evidence of demand, market size or customer payments.",
                        "Review primary text, licensing and relevance before drawing conclusions."]}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--provider",choices=sorted(ENDPOINTS),required=True)
 p.add_argument("--query",required=True)
 p.add_argument("--limit",type=int,default=5)
 p.add_argument("--allow-network",action="store_true")
 p.add_argument("--output",type=Path,required=True)
 a=p.parse_args()
 result=search(a.provider,a.query,a.limit,a.allow_network)
 if a.output.exists():raise FileExistsError("refuse to overwrite previous evidence")
 a.output.parent.mkdir(parents=True,exist_ok=True)
 with a.output.open("x",encoding="utf-8") as f:json.dump(result,f,indent=2,ensure_ascii=False)
 print(json.dumps({"provider":a.provider,"records":len(result["results"]),"output":str(a.output)}))
if __name__=="__main__":main()
