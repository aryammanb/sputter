import urllib.request,re
u='https://www.lesker.com/flanges/hardware-kf-centeringrings/part/qf25-100-srv'
try:
 s=urllib.request.urlopen(u,timeout=20).read().decode('utf-8','replace')
 print('\n'.join(re.findall(r'<img[^>]*>',s,re.I)[-25:]))
except Exception as e:print(type(e).__name__,str(e))
