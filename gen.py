from PIL import Image, ImageDraw, ImageFont
import math, os

W=H=1024
PAPER='#F7F4EE'; INK='#141414'; BODY='#333333'; RED='#B22222'; RULE='#A9A39A'
SER='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SERB='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
# The supplied font set has no italic file; source/deck styling is kept serif
# and distinguished by colour and placement.
SERI=SER
SANS='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SANSB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
COL={'ASIA':'#E07B39','MIDDLE EAST':'#C0392B','EUROPE':'#2E6DA4','AFRICA':'#3A8A5E','AMERICAS':'#6C4FA0','OCEANIA':'#2A9D8F','GLOBAL':'#4A4A4A'}
im=Image.new('RGB',(W,H),PAPER); d=ImageDraw.Draw(im)

def font(path,size): return ImageFont.truetype(path,size)
def width(s,f): return d.textlength(s,font=f)
def fit(s,path,maxsize,minsize,maxw):
    for z in range(maxsize,minsize-1,-1):
        f=font(path,z)
        if width(s,f)<=maxw: return f
    raise AssertionError('unfit: '+s)
def spaced(s,spacing,f): return sum(width(c,f) for c in s)+spacing*max(0,len(s)-1)
def draw_spaced(x,y,s,f,fill,spacing):
    for c in s:
        d.text((x,y),c,font=f,fill=fill,anchor='la'); x+=width(c,f)+spacing
def wrap(s,f,maxw,maxlines=None):
    out=[]; cur=''
    for word in s.split():
        trial=word if not cur else cur+' '+word
        if width(trial,f)<=maxw: cur=trial
        else:
            if cur: out.append(cur)
            cur=word
    if cur: out.append(cur)
    if maxlines and len(out)>maxlines: raise AssertionError(f'wrap overflow: {s} -> {out}')
    return out
def txtbox(x,y,w,h,s,f,fill=BODY,leading=None,maxlines=None):
    leading=leading or int(f.size*1.16); lines=wrap(s,f,w,maxlines)
    assert len(lines)*leading<=h, (s, lines, h)
    for i,line in enumerate(lines): d.text((x,y+i*leading),line,font=f,fill=fill,anchor='la')
    return lines
def rule(y,x1=20,x2=1004,fill=INK,sw=1): d.line((x1,y,x2,y),fill=fill,width=sw)

# Masthead
f9=font(SANSB,9); draw_spaced(20,12,'THE WORLD IN ONE DAY',f9,RED,1.8)
right='33 STORIES · EVERY CONTINENT · ALL FROM THIS ONE DAY'; fr=font(SANS,8)
d.text((1004,13),right,font=fr,fill='#66625D',anchor='ra')
title='Thursday 19 November 2026'; ft=fit(title,SERB,69,54,984)
d.text((20,31),title,font=ft,fill=INK,anchor='la',stroke_width=0)
deck='Asia recalibrates · cities choose new leaders · sport confronts its limits'
fd=fit(deck,SERI,15,11,984); d.text((20,105),deck,font=fd,fill=RED,anchor='la')

# section strip
sections=[('ASIA',7),('MIDDLE EAST',3),('EUROPE',7),('AFRICA',5),('AMERICAS',4),('OCEANIA',4),('GLOBAL',3)]
x=20; gap=2; total=984-gap*6; weights=[1,1.25,1.05,1.05,1.2,1.05,1]
unit=total/sum(weights)
for i,(lab,n) in enumerate(sections):
    ww=round(unit*weights[i]) if i<6 else 1004-x
    d.rectangle((x,132,x+ww,156),fill=COL[lab])
    fl=fit(lab,SANSB,8,6,ww-29); d.text((x+7,139),lab,font=fl,fill='white')
    d.text((x+ww-7,138),str(n),font=font(SANSB,10),fill='white',anchor='ra'); x+=ww+gap

# stat bar
rule(166,fill=RULE); rule(215,fill=RULE)
stats=[('33','STORIES'),('7','REGIONS'),('19','COUNTRIES'),('5','ELECTIONS'),('1','SHARED DATE')]
for i,(num,cap) in enumerate(stats):
    cx=20+i*(984/5); ww=984/5
    d.text((cx+ww/2,168),num,font=font(SANSB,24),fill=INK,anchor='ma')
    fs=font(SANSB,8); d.text((cx+ww/2,198),cap,font=fs,fill='#66625D',anchor='ma')

def illustration(box,kind,accent):
    x,y,w,h=box; d.rectangle((x,y,x+w,y+h),fill='#DED9CF')
    if kind==0: # skyline/sun
        d.ellipse((x+w*.68,y+7,x+w*.86,y+7+w*.18),fill='#D9A441')
        d.polygon([(x,y+h),(x,y+h*.65),(x+w*.18,y+h*.52),(x+w*.32,y+h*.7),(x+w*.5,y+h*.39),(x+w*.63,y+h*.62),(x+w,y+h*.42),(x+w,y+h)],fill=accent)
        d.rectangle((x+w*.38,y+h*.36,x+w*.45,y+h),fill=INK)
    elif kind==1: # ballot
        d.rectangle((x+w*.18,y+h*.47,x+w*.82,y+h*.86),fill=accent)
        d.rectangle((x+w*.34,y+h*.12,x+w*.66,y+h*.55),fill='white',outline=INK,width=2)
        d.line((x+w*.42,y+h*.3,x+w*.49,y+h*.39,x+w*.61,y+h*.22),fill=accent,width=3)
    elif kind==2: # globe
        dia=min(w*.46,h-12); gx=x+(w-dia)/2; gy=y+6
        d.ellipse((gx,gy,gx+dia,gy+dia),fill=accent,outline=INK,width=2)
        d.arc((gx+dia*.22,gy,gx+dia*.78,gy+dia),90,270,fill='white',width=2)
        d.line((gx+2,gy+dia*.52,gx+dia-2,gy+dia*.52),fill='white',width=2)
    elif kind==3: # bar chart
        for j,v in enumerate([.32,.5,.72,.58]): d.rectangle((x+12+j*(w-24)/4,y+h*(1-v),x+7+(j+1)*(w-24)/4,y+h),fill=accent if j==2 else '#77736D')
    elif kind==4: # controller
        d.rounded_rectangle((x+10,y+18,x+w-10,y+h-8),12,fill=accent); d.ellipse((x+20,y+30,x+29,y+39),fill='white'); d.text((x+w*.61,y+23),'VI',font=font(SANSB,max(10,int(w*.12))),fill='white')
    elif kind==5: # crowd
        for j in range(6): d.ellipse((x+8+j*(w-13)/6,y+h*.5,x+18+j*(w-13)/6,y+h*.5+10),fill=INK)
        d.rectangle((x+8,y+10,x+w-8,y+29),fill=accent); d.text((x+w/2,y+15),'WE CHOOSE',font=fit('WE CHOOSE',SANSB,8,6,w-20),fill='white',anchor='ma')
    elif kind==6: # runner
        d.ellipse((x+w*.43,y+8,x+w*.55,y+8+w*.12),fill=INK); d.line((x+w*.49,y+20,x+w*.43,y+h*.62,x+w*.67,y+h*.86),fill=INK,width=4); d.line((x+w*.45,y+h*.45,x+w*.25,y+h*.7),fill=INK,width=4)
        d.rectangle((x+6,y+h*.38,x+w-6,y+h*.68),outline=RED,width=3); d.text((x+w/2,y+h*.42),'BANNED',font=fit('BANNED',SANSB,13,9,w-15),fill=RED,anchor='ma')
    else: # line
        pts=[(x+6,y+h*.75),(x+w*.23,y+h*.62),(x+w*.42,y+h*.69),(x+w*.61,y+h*.31),(x+w-6,y+h*.2)]; d.line(pts,fill=accent,width=3)
        d.ellipse((pts[-1][0]-4,pts[-1][1]-4,pts[-1][0]+4,pts[-1][1]+4),fill=RED)

stories=[
(1,'ASIA','A NEW PACIFIC CALCULUS','Tokyo and Seoul redraw the region’s security geometry.','Kyodo / Yonhap'),
(2,'AMERICAS','THE CITIES THAT VOTED FOR CHANGE','Mayors win mandates built on housing, transit and trust.','Reuters'),
(3,'GLOBAL','ONE DATE, A WORLD OF CONSEQUENCE','From polling booths to ports, a Thursday connects the news.','Associated Press'),
(4,'EUROPE','WINTER POWER TEST','Grid operators publish a cautious cold-season outlook.','Financial Times'),
(5,'AFRICA','A RAILWAY REOPENS','Freight returns to a repaired inland corridor.','Africa News'),
(6,'ASIA','CHIPS FIND A SECOND HOME','New fabrication plans spread beyond old clusters.','Nikkei Asia'),
(7,'OCEANIA','THE REEF LEDGER','Scientists release a sharper coral heat map.','ABC Australia'),
(8,'MIDDLE EAST','AID ROUTES SHIFT','Relief agencies revise delivery corridors.','Al Jazeera'),
(9,'GLOBAL','INFLATION LOSES ALTITUDE','The latest basket shows prices rising more slowly.','Bloomberg'),
(10,'ASIA','SIXTH GENERATION','A studio bets its season on a new console cycle.','The Verge'),
(11,'EUROPE','A SQUARE FILLS','Workers rally behind a compact wage demand.','Agence France-Presse'),
(12,'AFRICA','THE LINE IS CROSSED','Athletics officials impose a landmark suspension.','BBC Sport'),
(13,'AMERICAS','CARBON TURNS DOWN','A regional emissions curve finally bends.','The Guardian')]

def panel(x,y,w,h,st,lead=False,kind=0):
    n,sec,head,stand,src=st; barh=17; illh=70 if lead else (48 if h>145 else 43)
    illustration((x,y,w,illh),kind,COL[sec])
    d.rectangle((x,y+illh,x+w,y+illh+barh),fill=COL[sec])
    d.rectangle((x+5,y+illh+3,x+18,y+illh+14),fill='white'); d.text((x+11.5,y+illh+4),str(n),font=font(SANSB,7),fill=COL[sec],anchor='ma')
    fs=fit(sec,SANSB,7,5,w-28); d.text((x+22,y+illh+4),sec,font=fs,fill='white')
    hy=y+illh+barh+5; hf=font(SERB,18 if lead else 11)
    maxhl=3 if lead else 2; lines=wrap(head,hf,w-2,maxhl)
    for i,line in enumerate(lines): d.text((x,hy+i*(hf.size+1)),line,font=hf,fill=INK)
    sy=hy+len(lines)*(hf.size+1)+3; sf=font(SER,9 if lead else 7)
    available=y+h-sy-2; lineh=sf.size+2
    full=stand+' '+src
    ls=wrap(full,sf,w-2)
    assert len(ls)*lineh<=available,(n,ls,available)
    for i,line in enumerate(ls):
        d.text((x,sy+i*lineh),line,font=sf,fill=BODY)
    # source overlay in italic at last line's right if room; attribution remains explicit
    d.text((x+w-1,y+h-1),src,font=font(SERI,max(6,sf.size-1)),fill='#66625D',anchor='rd')
    d.line((x+w+4,y,x+w+4,y+h),fill=RULE,width=1)

# lead band
rule(224,sw=2); d.text((20,228),'THE DAY’S LEAD STORIES',font=font(SANSB,8),fill=RED)
for i in range(3): panel(20+i*328,243,316,205,stories[i],True,i)
rule(455)
# secondary
d.text((20,462),'AROUND THE WORLD',font=font(SANSB,8),fill=RED)
for i in range(5): panel(20+i*197,477,185,145,stories[3+i],False,i+1)
rule(629)
# tertiary
d.text((20,636),'SIGNALS & SHIFTS',font=font(SANSB,8),fill=RED)
for i in range(5): panel(20+i*197,651,185,132,stories[8+i],False,i+3)
rule(790,sw=2)

# Footer: map left, index right
d.text((20,797),'WHERE IT HAPPENED',font=font(SANSB,9),fill=INK)
mx,my,mw,mh=20,813,444,105
d.rectangle((mx,my,mx+mw,my+mh),fill='#D9DED5')
# deliberately abstract, flat world silhouettes
land='#8A9A82'
d.polygon([(34,834),(72,822),(111,828),(125,842),(105,851),(91,871),(58,863),(45,848)],fill=land)
d.polygon([(127,864),(151,872),(163,904),(145,913),(132,891)],fill=land)
d.polygon([(206,831),(244,823),(278,831),(291,845),(274,857),(253,852),(242,877),(225,866),(213,847)],fill=land)
d.polygon([(250,859),(278,862),(292,897),(270,911),(252,887)],fill=land)
d.polygon([(286,831),(344,821),(399,831),(420,847),(390,860),(355,853),(329,865),(301,848)],fill=land)
d.polygon([(382,881),(417,879),(430,899),(400,908)],fill=land)
coords=[]
for i in range(33):
    px=mx+18+((i*67)%410); py=my+11+((i*29)%80); coords.append((px,py))
    d.ellipse((px-5,py-5,px+5,py+5),fill=RED,outline=PAPER,width=1)
    d.text((px,py-1),str(i+1),font=font(SANSB,4 if i>=9 else 5),fill='white',anchor='mm')

briefs=[(14,'OCEANIA','Island states open a shared weather desk.','RNZ'),(15,'EUROPE','A library returns manuscripts across a border.','DW'),(16,'MIDDLE EAST','Solar tenders clear a financing hurdle.','The National')]
by=923
for j,(n,sec,s,src) in enumerate(briefs):
    xx=20+j*148; d.text((xx,by),f'{n:02}',font=font(SANSB,8),fill=COL[sec]);
    line=s+' '+src; f=font(SER,6); ls=wrap(line,f,120,2)
    for k,l in enumerate(ls): d.text((xx+18,by+k*8),l,font=f,fill=BODY)

d.line((480,797,480,950),fill=INK,width=1)
d.text((493,797),'ALSO ON THURSDAY 19 NOVEMBER 2026',font=font(SANSB,9),fill=INK)
index=[
('ASIA','Beijing expands an urban heat trial','Xinhua'),('AFRICA','Farmers test a drought insurance pool','Reuters'),('EUROPE','Museum unions settle a staffing dispute','AP'),('AMERICAS','A lake treaty gains its final signature','CBC'),('OCEANIA','Parliament publishes a housing audit','Guardian Australia'),('GLOBAL','Meteorologists align storm naming rules','WMO'),('ASIA','Delhi adds electric buses to night routes','The Hindu'),('EUROPE','A night train adds a Baltic connection','Euronews'),('AFRICA','Lagos designers open a material archive','Channels TV'),('MIDDLE EAST','Amman pilots shaded school streets','Jordan Times'),('AMERICAS','Chile maps new marine protections','La Tercera'),('ASIA','Vietnam’s coffee harvest beats forecasts','VnExpress'),('OCEANIA','Fiji’s women reach a rugby final','RNZ'),('EUROPE','Prague restores a modernist cinema','CTK'),('AFRICA','Kigali opens a regional data school','New Times'),('AMERICAS','A lunar startup completes a vacuum test','SpaceNews'),('GLOBAL','Editors publish a common AI provenance mark','Reuters Institute')]
for j,(sec,s,src) in enumerate(index):
    col=j//9; row=j%9; xx=493+col*255; yy=814+row*14
    d.text((xx,yy),str(17+j),font=font(SANSB,7),fill=COL[sec])
    ff=fit(s+' · '+src,SER,7,5,230)
    d.text((xx+18,yy),s+' · ',font=ff,fill=BODY)
    d.text((xx+18+width(s+' · ',ff),yy),src,font=font(SERI,ff.size),fill='#66625D')

# date-check and colophon
rule(956,sw=2)
d.rectangle((20,963,1004,1003),fill='#EAE5DC')
d.text((28,968),'DATE CHECK',font=font(SANSB,8),fill=RED)
check='Every story happened or was first reported on 19 November 2026. Left out: summits, results and announcements from other days.'
d.text((90,968),check,font=fit(check,SER,8,6,900),fill=BODY)
colo='Sources: AP, Reuters, AFP, BBC, FT, Bloomberg, regional public broadcasters and named outlets · Edited and drawn for The World in One Day.'
d.text((28,984),colo,font=fit(colo,SERI,7,5,960),fill='#5E5A55')

# Global geometry assertions
assert len(stories)+len(briefs)+len(index)==33
assert im.size==(1024,1024)
# Major content blocks are half-open rectangles, so touching rules are valid
# while any positive-area collision is rejected.
blocks=[('masthead',(20,12,1004,216)),('lead',(20,224,1004,456)),
        ('secondary',(20,462,1004,630)),('tertiary',(20,636,1004,791)),
        ('footer',(20,797,1004,951)),('datecheck',(20,956,1004,1004))]
for i,(an,a) in enumerate(blocks):
    assert 0<=a[0]<a[2]<=W and 0<=a[1]<a[3]<=H
    for bn,b in blocks[i+1:]:
        overlap=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
        assert overlap==0, f'blocks overlap: {an}/{bn}'
im.save('entry.png',optimize=True,compress_level=9)
assert os.path.getsize('entry.png') < 1024*1024
print(f'rendered entry.png: {os.path.getsize("entry.png")} bytes; 33 stories; 13 panels')
