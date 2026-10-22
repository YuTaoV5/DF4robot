"""Download attributed paper/project figures used in the navigation chapter."""
from pathlib import Path
import hashlib
import json
import time
import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deck' / 'media' / 'navigation'
FIGURES = [
    ('scan.jpg', 'https://raw.githubusercontent.com/wuyi2121/SCAN-Planner/348e8a590a50a5a6bbab8d8c6dcfd171f009be26/assets/images/abstract_real.jpg', 'SCAN-Planner 官方项目封面', 'https://github.com/wuyi2121/SCAN-Planner'),
    ('vbot.png', 'https://arxiv.org/html/2610.14634v1/figure1.png', 'VbotNav-0 论文 Figure 1', 'https://arxiv.org/html/2610.14634v1'),
    ('dronepc.jpg', 'https://arxiv.org/html/2503.00496v1/figures/indoor.jpg', 'Flying on Point Clouds 论文实机实验图', 'https://arxiv.org/html/2503.00496v1'),
    ('dronedepth.png', 'https://arxiv.org/html/2602.08653v2/outdoor.png', 'Safety-Shielded RL 论文室外实验图', 'https://arxiv.org/html/2602.08653v2'),
    ('parkour.jpg', 'https://extreme-parkour.github.io/static/live/parkour-poster.jpg', 'Extreme Parkour 官方演示封面', 'https://extreme-parkour.github.io/'),
]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, url, label, page in FIGURES:
        target = OUT / name
        if not target.exists():
            for attempt in range(3):
                try:
                    response = requests.get(url, timeout=40)
                    response.raise_for_status()
                    assert response.headers.get('Content-Type', '').startswith('image/')
                    target.write_bytes(response.content)
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(1)
        data = target.read_bytes()
        manifest.append(dict(file=name, url=url, page=page, label=label,
                             sha256=hashlib.sha256(data).hexdigest(),
                             usage='教学介绍中的署名原图引用；原图版权归原作者，未改绘。'))
        print(name, len(data))
    (OUT / 'sources.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
