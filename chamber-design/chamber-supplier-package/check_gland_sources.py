import urllib.request,re,json,concurrent.futures
urls=['https://www.lesker.com/flanges/hardware-kf-centeringrings/part/qf25-100-srv','https://www.lesker.com/flanges/adapters-fittings-quickconnects/part/qf25xvc100','https://www.ebay.com/itm/198508082866']
def read(u):
 try:
  req=urllib.request.urlopen(u,timeout=15);s=req.read().decode('utf-8','replace')
  if 'ebay' in u:
   return {'url':u,'http':req.status,'title':re.findall(r'<title>(.*?)</title>',s,re.S),'product_meta':re.findall(r'<meta[^>]*(?:property|name)=[\"\x27](?:og:title|og:description|product:price:amount|og:price:amount|twitter:title)[\"\x27][^>]*>',s,re.I),'schema':re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',s,re.S)[:2]}
  return {'url':u,'drawing_references':sorted(set(re.findall(r'[^\s\"\x27<>]+\.(?:gif|jpg|png|svg|pdf|avif)',s,re.I)))}
 except Exception as e:return {'url':u,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 for d in ex.map(read,urls):print(json.dumps(d)[:6000])
