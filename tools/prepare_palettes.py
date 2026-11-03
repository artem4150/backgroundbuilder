"""Build exact palette variants from the shared palette catalog."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
palettes=json.loads((ROOT/'frontend/shared/palettes.json').read_text(encoding='utf-8'))
catalog=json.loads((ROOT/'frontend/app/catalog.json').read_text(encoding='utf-8'))
for asset in catalog:
 if asset['kind']!='component':continue
 path=ROOT/'frontend/public/assets'/Path(asset['url']).name
 text=(ROOT/'Тестовое _ иллюстрации'/asset['file']).read_text(encoding='utf-8')
 for palette in palettes:
  mapping=dict(zip(palettes[0]['colors'],palette['colors']))
  if asset['role']=='main' and asset['object'] in ('wallet','coin'):
   mapping['#D7CDF5']=palette['roles']['objectLight'] if asset['object']=='wallet' else palette['roles']['objectSoft']
   if asset['object']=='wallet':mapping['#F9ECB0']=palette['roles']['objectSoft']
  colored=re.sub('|'.join(map(re.escape,mapping)),lambda m:mapping[m[0]],text)
  destination=path if palette['id']=='purple' else path.with_name(path.stem+'-'+palette['id']+'.svg')
  destination.write_text(colored,encoding='utf-8')
print('Prepared 80 palette variants from the shared catalog')
