from pathlib import Path
from PIL import Image, ImageDraw
base=Path(__file__).resolve().parent
import json
count=len(json.loads((base/'slides.json').read_text(encoding='utf-8')))
files=[base/'rendered'/f'slide-{i:02}.png' for i in range(1,count+1)]
if not files: raise SystemExit('Render slides first')
tw,th,cols,gap=480,270,4,12
sheet=Image.new('RGB',(cols*tw+(cols+1)*gap,((len(files)+cols-1)//cols)*(th+32+gap)+gap),'#D2D2D7')
draw=ImageDraw.Draw(sheet)
for k,f in enumerate(files):
 x=gap+(k%cols)*(tw+gap);y=gap+(k//cols)*(th+32+gap)
 im=Image.open(f).convert('RGB');sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(x,y))
 draw.text((x+8,y+th+6),f'{k+1:02d}',fill='#1D1D1F')
sheet.save(base/'预览-全部页面.png')
for part in range((len(files)+15)//16):
 a=part*4*(th+32+gap);b=min(sheet.height,a+4*(th+32+gap)+gap)
 sheet.crop((0,a,sheet.width,b)).save(base/'rendered'/f'contact-{part+1}.png')
print(len(files),'pages; contact sheet created')
