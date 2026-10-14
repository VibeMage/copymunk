#!/usr/bin/env python3
"""Render the selected Copymunk artwork into a self-contained, uninstalled asset set."""
import argparse
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops, ImageDraw, ImageFont
import resvg_py

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'sources'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
FONT = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
MAC = [('icon_16x16.png',16),('icon_16x16@2x.png',32),('icon_32x32.png',32),
       ('icon_32x32@2x.png',64),('icon_128x128.png',128),('icon_128x128@2x.png',256),
       ('icon_256x256.png',256),('icon_256x256@2x.png',512),
       ('icon_512x512.png',512),('icon_512x512@2x.png',1024)]
IOS = [('AppIcon.png','ios-light.svg','RGB'),('AppIcon-Dark.png','ios-dark.svg','RGB'),
       ('AppIcon-Tinted.png','ios-tinted.svg','RGBA')]
THEMES = [('浅色环境','#F5F1EA','#302A27','#766B65'),
          ('深色环境','#242127','#F4EADF','#BCAF9F')]

# Deliberate appearance palettes. These are not luminance conversion of a bitmap.
DARK = {
 '#FFD7A5':'#3A2928','#F2AE78':'#1D181C',
 '#F4CAA0':'#DCB58F','#EAB781':'#D0A173','#D28B52':'#B47A4B','#AD643C':'#865036',
 '#F3CEA6':'#DAB690','#E2A570':'#BE8C60','#BD7648':'#925D3D',
 '#FFF0D3':'#E9D7B9','#E3B48D':'#BE9777',
 '#B77D52':'#956747','#CC986A':'#B18660','#F6D5A9':'#D3B18B',
 '#FFF8E5':'#EBDDC0','#FFF2D2':'#E7D4B3','#EDC899':'#C9A57C',
 '#FFF8E7':'#EBDBC0','#F1D2A2':'#CFB184',
 '#E79587':'#C58B80','#FFFDF4':'#F4EAD7','#EDDCCA':'#CCBBA9',
 '#FFF7DF':'#EFE1C6','#D9957C':'#B9806E','#C5946C':'#A78162',
}
TINTED = {
 '#F4CAA0':'#C3C3C3','#EAB781':'#AEAEAE','#D28B52':'#929292','#AD643C':'#747474',
 '#F3CEA6':'#C8C8C8','#E2A570':'#A4A4A4','#BD7648':'#7C7C7C',
 '#FFF0D3':'#EAEAEA','#E3B48D':'#B2B2B2',
 '#B77D52':'#777777','#CC986A':'#8D8D8D','#F6D5A9':'#D5D5D5',
 '#FFF8E5':'#FAFAFA','#FFF2D2':'#F0F0F0','#EDC899':'#D2D2D2',
 '#FFF8E7':'#F8F8F8','#F1D2A2':'#DCDCDC',
 '#4B3326':'#383838','#30221B':'#252525','#211A17':'#171717',
 '#79503A':'#535353','#4E3025':'#393939','#C5946C':'#858585',
 '#E79587':'#D6D6D6','#975433':'#252525','#9C5A33':'#4A4A4A',
 '#FFFDF4':'#FFFFFF','#EDDCCA':'#E8E8E8','#70402F':'#393939',
 '#FFF7DF':'#F8F8F8','#D9957C':'#999999',
}


def font(size):
    return ImageFont.truetype(FONT,size)


def save(im,path):
    im.save(path,icc_profile=(SOURCE/'sRGB.icc').read_bytes())


def paste(dest,im,x,y):
    dest.paste(im,(int(x),int(y)),im.getchannel('A') if im.mode=='RGBA' else None)


def raster(svg,size=1024,ss=4):
    raw=resvg_py.svg_to_bytes(svg_string=svg,width=size*ss,height=size*ss)
    return Image.open(io.BytesIO(raw)).convert('RGBA').resize((size,size),Image.Resampling.BOX)


def prepare_ios():
    """Geometry is unchanged; transform tile-relative coordinates to full bleed."""
    source=(SOURCE/'macos.svg').read_text()
    for appearance in ('light','dark','tinted'):
        tree=ET.fromstring(source)
        parents={c:p for p in tree.iter() for c in p}
        bg=next(e for e in tree.iter() if e.get('id')=='background')
        face=next(e for e in tree.iter() if e.get('id')=='face')
        parent=parents[bg]
        assert parents[face] is parent
        parent.attrib.pop('clip-path',None)
        scale=1024/823.296
        matrix=f'matrix({scale} 0 0 {scale} {-100.352*scale} {-100.352*scale})'
        parent.remove(face)
        wrapper=ET.SubElement(parent,f'{{{NS}}}g',{'transform':matrix})
        wrapper.append(face)
        bg.attrib.update(x='0',y='0',width='1024',height='1024',rx='0')
        grad=next(e for e in tree.iter() if e.get('id')=='warm-background')
        grad.set('gradientTransform',matrix)
        if appearance=='tinted':
            parent.remove(bg)
            defs=next(e for e in tree if e.tag==f'{{{NS}}}defs')
            defs.remove(grad)
        palette=DARK if appearance=='dark' else TINTED if appearance=='tinted' else {}
        for e in tree.iter():
            for k,v in list(e.attrib.items()):
                if v in palette:
                    e.set(k,palette[v])
        (SOURCE/f'ios-{appearance}.svg').write_text(ET.tostring(tree,encoding='unicode')+'\n')
    print('Prepared three iOS sources',flush=True)


def render():
    master=raster((SOURCE/'macos.svg').read_text())
    bysize={1024:master}
    for size in (16,32,64,128,256,512):
        optical=SOURCE/f'macos-optical-{size}.svg'
        if optical.exists():
            # Direct target-grid drawing. Never derives 16/32 from the 1024 master.
            bysize[size]=raster(optical.read_text(),size,8)
        else:
            assert size not in (16,32),'Required optical source missing'
            bysize[size]=master.resize((size,size),Image.Resampling.LANCZOS)
    for name,size in MAC:
        save(bysize[size],ROOT/'appiconset'/name)
    for filename,svgname,mode in IOS:
        im=raster((SOURCE/svgname).read_text())
        if mode=='RGB':
            assert im.getchannel('A').getextrema()==(255,255)
        save(im.convert(mode),ROOT/'ios-appiconset'/filename)
    module_spec=importlib.util.spec_from_file_location('copymunk_menubar',SOURCE/'menubar.py')
    module=importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    module.main()
    print('Rendered 10 macOS + 3 iOS + 2 menu assets',flush=True)


def system_mask(size):
    """Presentation-only continuous-corner approximation, not an Apple mask asset."""
    ss=4
    mask=Image.new('L',(size*ss,size*ss),0)
    draw=ImageDraw.Draw(mask)
    radius=size*ss/2
    pts=[]
    for n in range(720):
        a=n*math.tau/720
        c,s=math.cos(a),math.sin(a)
        pts.append((radius+radius*math.copysign(abs(c)**(2/4.8),c),
                    radius+radius*math.copysign(abs(s)**(2/4.8),s)))
    draw.polygon(pts,fill=255)
    return mask.resize((size,size),Image.Resampling.BOX)


def ios_preview(name,size):
    im=Image.open(ROOT/'ios-appiconset'/name).convert('RGBA').resize((size,size),Image.Resampling.LANCZOS)
    if 'Tinted' in name:
        # Neutral system background proxy for review; no claim to reproduce a runtime tint algorithm.
        base=Image.new('RGBA',(size,size),'#343139')
        base.alpha_composite(im)
        im=base
    im.putalpha(ImageChops.multiply(im.getchannel('A'),system_mask(size)))
    return im


def contact():
    columns=[]
    x=48
    for name,size in MAC:
        width=max(size,160)
        columns.append((x,width,'mac',name,size))
        x+=width+26
    for name,_,_ in IOS:
        columns.append((x,320,'ios',name,320));x+=346
    for size in (18,36):
        columns.append((x,100,'menu',f'menubar-template-{size}.png',size));x+=126
    width=x+22
    header,row_h=176,1180
    sheet=Image.new('RGB',(width,header+2*row_h),'#F0EAE1');d=ImageDraw.Draw(sheet)
    d.text((48,25),'COPYMUNK / 04 鼓腮小开心 · 定稿资产',font=font(48),fill='#342D28')
    d.text((48,99),'macOS 十个槽位全部原生像素；iOS 以320px近似系统圆角展示；模板为原生18/36px。浅深两行。',font=font(27),fill='#77695D')
    samples=[]
    for row,(theme,bg,fg,muted) in enumerate(THEMES):
        y=header+row*row_h
        d.rectangle((0,y,width,y+row_h),fill=bg)
        d.text((48,y+10),theme,font=font(30),fill=fg)
        for x,cw,kind,name,size in columns:
            if kind=='mac':
                im=Image.open(ROOT/'appiconset'/name)
                label=name.removeprefix('icon_').removesuffix('.png')
            elif kind=='ios':
                im=ios_preview(name,size);label=name.removesuffix('.png')
            else:
                im=Image.open(ROOT/'menubar'/name).convert('RGBA')
                if row:
                    white=Image.new('RGBA',im.size,'white');white.putalpha(im.getchannel('A'));im=white
                label=f'menu {size}px'
            px=x+(cw-im.width)//2;py=y+112+(1024-im.height)//2
            paste(sheet,im,px,py)
            d.text((x,y+60),label,font=font(21),fill=muted)
            d.text((x,y+88),f'{size}px'+(' optical' if kind=='mac' and size<=32 else ''),font=font(17),fill=muted)
            if kind=='mac':
                samples.append(dict(row=row,name=name,x=px,y=py,size=size,bg=bg))
    save(sheet,ROOT/'contact-sheet.png')
    (ROOT/'previews/contact-layout.json').write_text(json.dumps(dict(size=sheet.size,samples=samples),indent=2)+'\n')


def overview():
    im=Image.new('RGB',(1920,1130),'#F3EDE4');d=ImageDraw.Draw(im)
    d.text((60,32),'Copymunk / 鼓腮小开心',font=font(45),fill='#342A25')
    d.text((60,93),'保留选中脸与原底色 · 小尺寸独立光学稿 · 三种 iOS 外观 · 菜单栏模板',font=font(24),fill='#786A5F')
    main=Image.open(ROOT/'appiconset/icon_512x512.png');paste(im,main,55,184)
    d.text((110,724),'macOS 512px',font=font(26),fill='#463C34')
    for i,(name,_,_) in enumerate(IOS):
        x=660+i*407
        paste(im,ios_preview(name,320),x,259)
        d.text((x,615),['iOS 浅色','iOS 深色','iOS 着色 · 中性模拟'][i],font=font(24),fill='#463C34')
    for i,size in enumerate((128,64,32,16)):
        filename=next(n for n,s in MAC if s==size)
        p=Image.open(ROOT/'appiconset'/filename);x=120+i*240
        paste(im,p,x,843+(128-size)//2)
        d.text((x,999),f'{size}px'+(' 光学稿' if size<=32 else ''),font=font(23),fill='#463C34')
    for i,size in enumerate((18,36)):
        p=Image.open(ROOT/'menubar'/f'menubar-template-{size}.png');x=1290+i*220
        paste(im,p,x,897-size//2)
        d.text((x-40,999),f'模板 {size}px',font=font(23),fill='#463C34')
    save(im,ROOT/'overview.png')


def ios_review():
    sheet=Image.new('RGB',(1500,620),'#EDE8E0');d=ImageDraw.Draw(sheet)
    for i,(name,_,_) in enumerate(IOS):
        paste(sheet,ios_preview(name,440),30+i*500,70)
        d.text((40+i*500,540),name,font=font(22),fill='#332A24')
    save(sheet,ROOT/'previews/ios-review.png')


def optical_review():
    sheet=Image.new('RGB',(1800,1250),'#F3EDE4');d=ImageDraw.Draw(sheet)
    d.text((48,25),'光学稿检查 / 左：直接缩图　右：最终像素稿',font=font(36),fill='#342A25')
    d.text((48,78),'每组：原尺寸与最近邻放大。64px同样复核；保留原主图比例。',font=font(23),fill='#786A5F')
    master=Image.open(ROOT/'appiconset/icon_512x512@2x.png')
    for row,(theme,bg,fg,muted) in enumerate(THEMES):
        y=140+row*550;d.rectangle((0,y,1800,y+550),fill=bg)
        for i,size in enumerate((16,32,64)):
            x=40+i*590
            d.text((x,y+15),f'{size}px / '+('独立光学稿' if size<=32 else '64px检查'),font=font(26),fill=fg)
            final=Image.open(ROOT/'appiconset'/next(n for n,s in MAC if s==size))
            auto=master.resize((size,size),Image.Resampling.LANCZOS)
            for col,art in enumerate((auto,final)):
                px=x+col*280
                paste(sheet,art,px+105-size//2,y+92-size//2)
                paste(sheet,art.resize((224,224),Image.Resampling.NEAREST),px,y+160)
                d.text((px,y+405),'直接缩图' if col==0 else '最终稿',font=font(21),fill=muted)
        d.text((48,y+490),theme,font=font(23),fill=muted)
    save(sheet,ROOT/'previews/optical-review.png')


def dock():
    sheet=Image.new('RGB',(1600,960),'#EDE6DD');d=ImageDraw.Draw(sheet)
    d.text((60,28),'Dock 模拟 / 布局示意，非运行截图',font=font(34),fill='#392F29')
    for row,(theme,bg,fg,muted) in enumerate(THEMES):
        y=110+row*410
        wallpaper='#DCCCB7' if row==0 else '#273640'
        dock_bg='#F3EDE5' if row==0 else '#403E42'
        d.rounded_rectangle((40,y,1560,y+380),radius=28,fill=wallpaper)
        d.text((80,y+25),theme+' · 96px 图标示意',font=font(24),fill=fg)
        d.rounded_rectangle((256,y+200,1344,y+344),radius=37,fill=dock_bg)
        colors=['#88A3BA','#AAAE8A','#BC9EA5',None,'#A0A0AE','#8AA9A0','#B6A183']
        for i,color in enumerate(colors):
            x=310+i*142
            if color:
                d.rounded_rectangle((x+11,y+227,x+85,y+301),radius=20,fill=color)
                d.rounded_rectangle((x+30,y+247,x+66,y+281),radius=8,outline=dock_bg,width=4)
            else:
                p=Image.open(ROOT/'appiconset/icon_128x128.png').resize((96,96),Image.Resampling.LANCZOS)
                paste(sheet,p,x,y+216)
                d.ellipse((x+45,y+325,x+50,y+330),fill=fg)
                d.rounded_rectangle((x-20,y+155,x+116,y+193),radius=8,fill=dock_bg)
                d.text((x-5,y+159),'Copymunk',font=font(23),fill=fg)
    save(sheet,ROOT/'previews/dock-simulation.png')


def store_preview():
    sheet=Image.new('RGB',(1600,950),'#ECE6DE');d=ImageDraw.Draw(sheet)
    d.text((50,28),'App Store 搜索结果模拟 / 图标比例检查，非商店截图',font=font(32),fill='#392F29')
    for row,(theme,bg,fg,muted) in enumerate(THEMES):
        y=105+row*405
        d.rounded_rectangle((40,y,1560,y+375),radius=28,fill=bg)
        d.text((80,y+26),theme,font=font(24),fill=muted)
        d.rounded_rectangle((80,y+76,1520,y+132),radius=14,fill='#E7E2DA' if row==0 else '#39343C')
        d.text((105,y+86),'搜索：Copymunk',font=font(25),fill=fg)
        # Store mock keeps the default listing artwork on both surrounding themes.
        name='AppIcon.png'
        paste(sheet,ios_preview(name,96),92,y+197)
        d.text((218,y+195),'Copymunk',font=font(35),fill=fg)
        d.text((219,y+249),'剪贴板历史',font=font(23),fill=muted)
        d.rounded_rectangle((1328,y+213,1472,y+266),radius=26,fill='#E4E1DD' if row==0 else '#3C3740')
        d.text((1371,y+222),'查看',font=font(23),fill='#3F82BF' if row==0 else '#77B8EC')
        d.text((92,y+322),'仅模拟展示布局；未包含评分、排名、价格或实际商店状态。',font=font(19),fill=muted)
    save(sheet,ROOT/'previews/app-store-search-simulation.png')


def comparisons():
    ims=[]
    for filename,target in [('macos-original.svg','before-1024.png'),('macos-subtle-background.svg','after-1024.png')]:
        im=raster((SOURCE/filename).read_text());save(im,ROOT/'comparisons'/target);ims.append(im)
    sheet=Image.new('RGB',(1440,920),'#F4F0E8');d=ImageDraw.Draw(sheet)
    d.text((50,22),'04 / 底色微调试验：最终保留左侧原底',font=font(32),fill='#383432')
    for i,(im,label) in enumerate(zip(ims,['原稿 · 最终采用','偏粉杏试稿 · 未采用'])):
        x=40+i*710;d.text((x+48,86),label,font=font(27),fill='#383432')
        paste(sheet,im.resize((600,600),Image.Resampling.LANCZOS),x,135)
        for j,size in enumerate((64,32)):
            paste(sheet,im.resize((size,size),Image.Resampling.LANCZOS),x+120+j*180,754)
            d.text((x+120+j*180,826),str(size)+'px',font=font(18),fill='#6C625D')
    d.text((72,874),'脸部像素未改；64/32px分离改善不明显，依简报保留原色。',font=font(23),fill='#6C625D')
    save(sheet,ROOT/'comparisons/background-comparison.png')


def sheets():
    contact();overview();ios_review();optical_review();dock();store_preview();comparisons()
    print('Rendered comparisons and simulations',flush=True)


def audit():
    report={'status':'PASS','assets':[]}
    for name,size in MAC:
        p=ROOT/'appiconset'/name;im=Image.open(p)
        assert im.mode=='RGBA' and im.size==(size,size)
        assert im.getchannel('A').getextrema()==(0,255)
        if size==1024: assert im.getchannel('A').getbbox()==(100,100,924,924)
        report['assets'].append(dict(file=str(p.relative_to(ROOT)),size=size,mode=im.mode))
    assert (ROOT/'appiconset/icon_16x16@2x.png').read_bytes()==(ROOT/'appiconset/icon_32x32.png').read_bytes()
    for name,_,mode in IOS:
        p=ROOT/'ios-appiconset'/name;im=Image.open(p)
        assert im.mode==mode and im.size==(1024,1024)
        if mode=='RGB': assert 'transparency' not in im.info
        else:
            r,g,b,a=im.split()
            assert ImageChops.difference(r,g).getbbox() is None and ImageChops.difference(r,b).getbbox() is None
            assert a.getextrema()==(0,255) and all(a.getpixel(pt)==0 for pt in [(0,0),(1023,0),(0,1023),(1023,1023)])
        report['assets'].append(dict(file=str(p.relative_to(ROOT)),size=1024,mode=mode))
    for size in (18,36):
        p=ROOT/'menubar'/f'menubar-template-{size}.png';im=Image.open(p)
        assert im.mode=='RGBA' and im.size==(size,size)
        assert im.convert('RGB').getextrema()==((0,0),(0,0),(0,0))
        assert set(im.getchannel('A').getdata())=={0,255}
        svg_im=raster((SOURCE/f'menubar-{size}.svg').read_text(),size,1)
        assert svg_im.tobytes()==im.tobytes(),'Menu SVG/PNG mismatch'
        report['assets'].append(dict(file=str(p.relative_to(ROOT)),size=size,mode='RGBA',binary_alpha=True))
    for directory in ('appiconset','ios-appiconset','menubar'):
        content=json.loads((ROOT/directory/'Contents.json').read_text())
        assert {e['filename'] for e in content['images']}=={p.name for p in (ROOT/directory).glob('*.png')}
    for p in SOURCE.glob('*.svg'): ET.parse(p)
    assert (SOURCE/'macos.svg').read_bytes()==(SOURCE/'macos-original.svg').read_bytes(),'Selected master changed'
    original_face=ET.tostring(next(e for e in ET.parse(SOURCE/'macos.svg').iter() if e.get('id')=='face'))
    light_face=ET.tostring(next(e for e in ET.parse(SOURCE/'ios-light.svg').iter() if e.get('id')=='face'))
    assert original_face==light_face,'Light face geometry/colors changed'
    report['selected_master_unchanged']=True
    master=Image.open(ROOT/'appiconset/icon_512x512@2x.png')
    # 第三轮选中的原图只留在本地探索目录里，没有进仓库；在的时候才比对
    selected_path=ROOT.parents[2]/'art/app-icon-exploration/2026-10-15-copymunk-01-cute-codex/04-delight/macos-1024.png'
    if selected_path.exists():
        assert master.tobytes()==Image.open(selected_path).convert('RGBA').tobytes(),'Selected master pixels changed'
        report['selected_master_pixels_unchanged']=True
    for size in (16,32):
        tree=ET.parse(SOURCE/f'macos-optical-{size}.svg').getroot()
        assert tree.get('viewBox')==f'0 0 {size} {size}'
        im=Image.open(ROOT/'appiconset'/next(n for n,s in MAC if s==size))
        assert ImageChops.difference(im.convert('RGB'),master.resize((size,size),Image.Resampling.LANCZOS).convert('RGB')).getbbox() is not None
    report['optical_source_grids']=[16,32]
    layout=json.loads((ROOT/'previews/contact-layout.json').read_text());sheet=Image.open(ROOT/'contact-sheet.png')
    assert list(sheet.size)==layout['size']
    for entry in layout['samples']:
        im=Image.open(ROOT/'appiconset'/entry['name']);expected=Image.new('RGB',im.size,entry['bg']);paste(expected,im,0,0)
        x,y,s=entry['x'],entry['y'],entry['size']
        assert ImageChops.difference(expected,sheet.crop((x,y,x+s,y+s))).getbbox() is None
    report['native_mac_contact_samples']=len(layout['samples'])
    report['runtime_status']='Integrated via scripts/make-icon.sh; simulations are not runtime screenshots; system mask is a presentation approximation.'
    (ROOT/'qa-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Audit PASS: {len(report['assets'])} assets; 20 native contact samples",flush=True)


def manifest():
    files=[dict(file=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
           for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='manifest.json' and '__pycache__' not in p.parts]
    (ROOT/'manifest.json').write_text(json.dumps(dict(files=files),indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--only',choices=['sources','render','sheets','audit','manifest'])
    args=parser.parse_args()
    if args.only=='sources': prepare_ios()
    if args.only in (None,'render'): render()
    if args.only in (None,'sheets'): sheets()
    if args.only in (None,'audit'): audit()
    manifest()
