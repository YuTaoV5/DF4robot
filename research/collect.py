"""Reproduce the targeted DeepXiv searches and paper reads (network required)."""
import concurrent.futures, json, os, pathlib, subprocess, sys
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
ROOT = pathlib.Path(__file__).resolve().parent
PAPERS = {
 'eskf':'1711.02508', 'invariant':'1410.1465', 'contact':'1805.10410',
 'vins':'1708.03852', 'orb3':'2007.11898', 'lio-sam':'2007.00258',
 'fast-lio2':'2107.06829', 'lvi-sam':'2104.10831', 'r3live':'2109.07982',
 'lic-fusion2':'2008.07196', 'fast-livo2':'2408.14035',
 'tlio':'2007.01867', 'droid':'2108.10869', 'selective':'1903.01534',
 'diffusion-policy':'2303.04137', 'rt2':'2307.15818', 'openvla':'2406.09246',
 'octo':'2405.12213', 'pi0':'2410.24164', 'pi05':'2504.16054',
 'ikalibr':'2407.11420', 'ris-calib':'2408.02444',
 'radar-multi':'2311.08608', 'dero':'2403.05136', 'dro':'2504.20339',
 'tacvla':'2603.12665', 'trail':'2609.03561', 'fire':'2609.05325',
 'sa-livo':'2606.25699', 'lbdu':'2609.39125', 'tactile-vla':'2507.09160',
 'ct-compare':'2202.08894', 'temporal':'1808.00692', 'preintegration':'1512.02363',
}
def read(item):
 name, aid = item
 path = ROOT / 'briefs' / f'{aid}.txt'
 if not path.exists():
  env = dict(os.environ, PYTHONIOENCODING='utf-8')
  p = subprocess.run(['deepxiv', 'paper', aid, '--brief'], capture_output=True, encoding='utf-8', errors='replace', env=env, timeout=150)
  path.write_text(p.stdout if p.returncode == 0 else p.stderr, encoding='utf-8')
 return name, aid, path.read_text(encoding='utf-8')[:1700]
if __name__ == '__main__':
 (ROOT / 'briefs').mkdir(exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for name, aid, result in pool.map(read, PAPERS.items()):
   print(name, aid, result, flush=True)
