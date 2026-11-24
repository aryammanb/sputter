from pathlib import Path

root=Path(__file__).resolve().parent
source=(root/'build-magnetron-r09.ps1').read_text(encoding='utf-8-sig')
source=source[:source.index(' class Item {')].replace('public static class Magnetron','public static class SealClosure')
tail=(root/'seal-closure-methods.cs').read_text(encoding='utf-8')
source+=tail+"\n}\n'@\n[SealClosure]::Run($OutputDirectory,$templates)\n"
(root/'build-seal-closure.ps1').write_text(source,encoding='utf-8')
