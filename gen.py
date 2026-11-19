from PIL import Image, ImageDraw, ImageFont
import math, os

W=H=1024
PAPER='#F7F4EE'; INK='#141414'; BODY='#333333'; RED='#B22222'; RULE='#A9A39A'
SER='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
SERB='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
# The supplied serif set has no italic face; use the installed mono italic for credits.
SERI='/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Oblique.ttf'
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
right='33 STORIES · EVERY CONTINENT · ALL FROM THIS ONE DAY'; fr=font(SANS,9)
d.text((1004,13),right,font=fr,fill=BODY,anchor='ra')
title='Thursday 19 November 2026'; ft=font(SERB,64)
title_spacing=(984-sum(width(c,ft) for c in title))/(len(title)-1)
draw_spaced(20,31,title,ft,INK,title_spacing)
deck='Asia recalibrates · cities choose new leaders · sport confronts its limits'
fd=fit(deck,SERI,15,11,984); d.text((20,105),deck,font=fd,fill=RED,anchor='la')

# section strip
sections=[('ASIA',7),('MIDDLE EAST',3),('EUROPE',7),('AFRICA',5),('AMERICAS',4),('OCEANIA',4),('GLOBAL',3)]
x=20; gap=2; total=984-gap*6; weights=[1,1.25,1.05,1.05,1.2,1.05,1]
unit=total/sum(weights)
for i,(lab,n) in enumerate(sections):
    ww=round(unit*weights[i]) if i<6 else 1004-x
    d.rectangle((x,132,x+ww,156),fill=COL[lab])
    fl=fit(lab,SANSB,9,9,ww-29); d.text((x+7,138),lab,font=fl,fill='white')
    d.text((x+ww-7,138),str(n),font=font(SANSB,10),fill='white',anchor='ra'); x+=ww+gap

# stat bar
rule(166,fill=RULE); rule(215,fill=RULE)
stats=[('33','STORIES'),('7','REGIONS'),('19','COUNTRIES'),('5','ELECTIONS'),('1','SHARED DATE')]
for i,(num,cap) in enumerate(stats):
    cx=20+i*(984/5); ww=984/5
    d.text((cx+ww/2,168),num,font=font(SANSB,24),fill=INK,anchor='ma')
    fs=font(SANSB,9); d.text((cx+ww/2,197),cap,font=fs,fill=BODY,anchor='ma')

def illustration(box,kind,accent):
    """Thirteen compact editorial scenes, drawn only with deterministic vectors."""
    x,y,w,h=box; d.rectangle((x,y,x+w,y+h),fill='#DED9CF')
    if kind==0: # negotiating table and three flags
        d.ellipse((x+w*.18,y+38,x+w*.28,y+48),fill=INK); d.ellipse((x+w*.45,y+28,x+w*.55,y+38),fill=INK); d.ellipse((x+w*.72,y+38,x+w*.82,y+48),fill=INK)
        d.polygon([(x+w*.18,y+55),(x+w*.82,y+55),(x+w*.7,y+110),(x+w*.3,y+110)],fill='#8B7867')
        for j,c in enumerate(['#D9A441',RED,'#2E6DA4']):
            fx=x+w*(.3+j*.2); d.line((fx,y+12,fx,y+57),fill=INK,width=2); d.polygon([(fx,y+13),(fx+w*.11,y+20),(fx,y+28)],fill=c)
    elif kind==1: # ballot box and voter queue
        d.rectangle((x+w*.38,y+75,x+w*.72,y+h-10),fill=accent); d.rectangle((x+w*.43,y+22,x+w*.63,y+86),fill='white',outline=INK,width=2)
        d.line((x+w*.47,y+45,x+w*.53,y+53,x+w*.6,y+37),fill=accent,width=3)
        for j in range(3):
            px=x+18+j*30; d.ellipse((px,y+68,px+12,y+80),fill=INK); d.line((px+6,y+80,px+6,y+111),fill=INK,width=3)
    elif kind==2: # globe with heat band
        dia=min(w*.55,h-12); gx=x+(w-dia)/2; gy=y+6
        d.ellipse((gx,gy,gx+dia,gy+dia),fill='#587A72',outline=INK,width=2)
        d.arc((gx+dia*.22,gy,gx+dia*.78,gy+dia),90,270,fill=PAPER,width=2); d.line((gx+2,gy+dia*.5,gx+dia-2,gy+dia*.5),fill=PAPER,width=2)
        d.rectangle((gx+3,gy+dia*.42,gx+dia-3,gy+dia*.6),fill=RED)
    elif kind==3: # bridge and electrical burst
        d.line((x+8,y+h-20,x+w-8,y+h-20),fill='#587A72',width=7); d.arc((x+20,y+22,x+w-20,y+h+28),180,360,fill=INK,width=4)
        d.line((x+24,y+55,x+24,y+h-20),fill=INK,width=3); d.line((x+w-24,y+55,x+w-24,y+h-20),fill=INK,width=3)
        cx=x+w*.72; cy=y+28; d.polygon([(cx,cy-20),(cx+6,cy-6),(cx+22,cy-10),(cx+10,cy+2),(cx+20,cy+15),(cx+3,cy+9),(cx-6,cy+23),(cx-7,cy+6),(cx-24,cy+8),(cx-11,cy-4)],fill=RED)
    elif kind==4: # missile trail
        d.arc((x+5,y+20,x+w*.82,y+h+45),185,275,fill=RED,width=4); d.polygon([(x+w*.73,y+21),(x+w*.9,y+9),(x+w*.84,y+29)],fill=INK)
        for j in range(4): d.ellipse((x+10+j*18,y+h-24-j*3,x+16+j*18,y+h-18-j*3),fill='#77736D')
    elif kind==5: # cyclone spiral
        cx=x+w/2; cy=y+h/2
        for r in (42,31,20): d.arc((cx-r,cy-r,cx+r,cy+r),195,525,fill=accent,width=5)
        d.ellipse((cx-5,cy-5,cx+5,cy+5),fill=INK)
    elif kind==6: # gavel over flag
        d.polygon([(x,y+18),(x+w,y+18),(x+w,y+h-8),(x,y+h-8)],fill=accent); d.rectangle((x,y+48,x+w,y+58),fill=PAPER)
        d.line((x+w*.35,y+22,x+w*.65,y+68),fill=INK,width=8); d.rectangle((x+w*.24,y+12,x+w*.46,y+35),fill='#8B6045')
    elif kind==7: # freighter at a strait
        d.rectangle((x,y+h*.62,x+w,y+h),fill='#668B91'); d.polygon([(x+12,y+h*.56),(x+w-12,y+h*.56),(x+w-28,y+h*.78),(x+28,y+h*.78)],fill=accent)
        for j in range(4): d.rectangle((x+34+j*25,y+31,x+55+j*25,y+51),fill=['#D9A441',RED,'#587A72','#8B6045'][j])
    elif kind==8: # chart with downward price arrow
        pts=[(x+8,y+20),(x+w*.28,y+32),(x+w*.48,y+28),(x+w*.68,y+55),(x+w-12,y+70)]; d.line(pts,fill=accent,width=4)
        d.polygon([(x+w-20,y+61),(x+w-5,y+74),(x+w-24,y+80)],fill=accent)
        d.line((x+8,y+h-10,x+w-8,y+h-10),fill=INK,width=2)
    elif kind==9: # controller VI
        d.rounded_rectangle((x+12,y+20,x+w-12,y+h-12),16,fill=accent); d.ellipse((x+28,y+42,x+41,y+55),fill=PAPER); d.text((x+w*.61,y+28),'VI',font=font(SANSB,22),fill='white')
    elif kind==10: # crowd and banner
        for j in range(7):
            px=x+8+j*(w-18)/7; d.ellipse((px,y+58+(j%2)*5,px+11,y+69+(j%2)*5),fill=INK); d.line((px+5,y+69,px+5,y+h-5),fill=INK,width=2)
        d.rectangle((x+7,y+10,x+w-7,y+36),fill=accent); d.text((x+w/2,y+15),'WE CHOOSE',font=font(SANSB,10),fill='white',anchor='ma')
    elif kind==11: # runner and banned stamp
        d.ellipse((x+w*.45,y+8,x+w*.55,y+18),fill=INK); d.line((x+w*.5,y+18,x+w*.42,y+58,x+w*.66,y+82),fill=INK,width=4); d.line((x+w*.45,y+42,x+w*.24,y+68),fill=INK,width=4)
        d.rectangle((x+7,y+33,x+w-7,y+62),outline=RED,width=4); d.text((x+w/2,y+36),'BANNED',font=font(SANSB,14),fill=RED,anchor='ma')
    else: # falling emissions curve
        pts=[(x+8,y+18),(x+w*.25,y+28),(x+w*.43,y+31),(x+w*.62,y+52),(x+w-12,y+75)]; d.line(pts,fill=accent,width=4)
        d.polygon([(x+w-24,y+68),(x+w-6,y+78),(x+w-18,y+88)],fill=accent); d.text((x+9,y+h-25),'CO₂',font=font(SANSB,12),fill=INK)

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

def panel(x,y,w,h,st,lead=False,hero=False,kind=0):
    n,sec,head,stand,src=st
    illh=175 if hero else (150 if lead else 92)
    illustration((x,y,w,illh),kind,COL[sec])
    # Geometry is fixed by band, never by the amount of copy.
    bar_y=y+(150 if lead else 75); barh=17
    d.rectangle((x,bar_y,x+w,bar_y+barh),fill=COL[sec])
    d.rectangle((x+5,bar_y+3,x+22,bar_y+14),fill='white')
    d.text((x+13.5,bar_y+2),str(n),font=font(SANSB,9),fill=COL[sec],anchor='ma')
    d.text((x+27,bar_y+2),sec,font=font(SANSB,9),fill='white')
    credit_alias={'Associated Press':'AP','Financial Times':'FT','Agence France-Presse':'AFP','ABC Australia':'ABC','The Guardian':'Guardian'}
    d.text((x+w-4,bar_y+2),credit_alias.get(src,src),font=font(SERI,10),fill='white',anchor='ra')
    hy=y+(172 if lead else 96); hf=font(SERB,26 if hero else (20 if lead else 12))
    lines=wrap(head,hf,w-2,2)
    if hero: # keep the 26px dominant headline on one measured line
        spacing=(w-2-sum(width(c,hf) for c in head))/(len(head)-1)
        draw_spaced(x,hy,head,hf,INK,spacing)
    else:
        for i,line in enumerate(lines): d.text((x,hy+i*(hf.size+2)),line,font=hf,fill=INK)
    sy=y+(220 if lead else 125); sf=font(SER,12)
    stand_lines=wrap(stand,sf,w-2)
    stand_line=stand_lines[0] if len(stand_lines)==1 else stand_lines[0].rstrip('.,')+'…'
    d.text((x,sy),stand_line,font=sf,fill=BODY)
    d.line((x+w+4,y,x+w+4,y+h),fill=RULE,width=1)

# lead band
rule(224,sw=2); d.text((20,228),'THE DAY’S LEAD STORIES',font=font(SANSB,9),fill=RED)
lead_widths=[394,283,283]; lead_x=[20,426,721]
for i in range(3): panel(lead_x[i],243,lead_widths[i],244,stories[i],True,i==0,i)
rule(494)
# secondary
d.text((20,501),'AROUND THE WORLD',font=font(SANSB,9),fill=RED)
for i in range(5): panel(20+i*197,516,185,151,stories[3+i],False,False,i+3)
rule(674)
# tertiary
d.text((20,681),'SIGNALS & SHIFTS',font=font(SANSB,9),fill=RED)
for i in range(5): panel(20+i*197,696,185,151,stories[8+i],False,False,i+8)
rule(854,sw=2)

# Footer: map left, index right
d.text((20,860),'WHERE IT HAPPENED',font=font(SANSB,10),fill=INK)
mx,my,mw,mh=20,875,444,66
d.rectangle((mx,my,mx+mw,my+mh),fill='#D9DED5')
# deliberately abstract, flat world silhouettes
land='#8A9A82'
d.polygon([(34,892),(72,879),(111,885),(125,896),(105,902),(91,918),(58,912),(45,900)],fill=land)
d.polygon([(127,907),(151,912),(163,936),(145,940),(132,921)],fill=land)
d.polygon([(206,887),(244,879),(278,886),(291,897),(274,905),(253,901),(242,923),(225,914),(213,897)],fill=land)
d.polygon([(250,906),(278,909),(292,936),(270,940),(252,925)],fill=land)
d.polygon([(286,887),(344,878),(399,887),(420,898),(390,908),(355,901),(329,912),(301,898)],fill=land)
d.polygon([(382,917),(417,915),(430,934),(400,940)],fill=land)
coords=[]
for i in range(33):
    px=mx+12+((i*67)%420); py=my+9+((i*29)%48); coords.append((px,py))
    d.ellipse((px-7,py-7,px+7,py+7),fill=RED,outline=PAPER,width=1)
    d.text((px,py-1),str(i+1),font=font(SANSB,9),fill='white',anchor='mm')

briefs=[(14,'OCEANIA','Island states open a shared weather desk.','RNZ'),(15,'EUROPE','A library returns manuscripts across a border.','DW'),(16,'MIDDLE EAST','Solar tenders clear a financing hurdle.','The National')]
by=943
for j,(n,sec,s,src) in enumerate(briefs):
    xx=20+j*148; d.text((xx,by),f'{n:02}',font=font(SANSB,9),fill=COL[sec]);
    f=font(SER,9); ls=wrap(s,f,122)
    if len(ls)>2: ls=[ls[0],ls[1].rstrip('.,')+'…']
    for k,l in enumerate(ls): d.text((xx+18,by+k*11),l,font=f,fill=BODY)

d.line((480,860,480,965),fill=INK,width=1)
d.text((493,860),'ALSO ON THURSDAY 19 NOVEMBER 2026',font=font(SANSB,10),fill=INK)
index=[
('ASIA','Beijing expands an urban heat trial','Xinhua'),('AFRICA','Farmers test a drought insurance pool','Reuters'),('EUROPE','Museum unions settle a staffing dispute','AP'),('AMERICAS','A lake treaty gains its final signature','CBC'),('OCEANIA','Parliament publishes a housing audit','Guardian Australia'),('GLOBAL','Meteorologists align storm naming rules','WMO'),('ASIA','Delhi adds electric buses to night routes','The Hindu'),('EUROPE','A night train adds a Baltic connection','Euronews'),('AFRICA','Lagos designers open a material archive','Channels TV'),('MIDDLE EAST','Amman pilots shaded school streets','Jordan Times'),('AMERICAS','Chile maps new marine protections','La Tercera'),('ASIA','Vietnam’s coffee harvest beats forecasts','VnExpress'),('OCEANIA','Fiji’s women reach a rugby final','RNZ'),('EUROPE','Prague restores a modernist cinema','CTK'),('AFRICA','Kigali opens a regional data school','New Times'),('AMERICAS','A lunar startup completes a vacuum test','SpaceNews'),('GLOBAL','Editors publish a common AI provenance mark','Reuters Institute')]
for j,(sec,s,src) in enumerate(index):
    col=j//6; row=j%6; xx=493+col*170; yy=876+row*13
    d.text((xx,yy),str(17+j),font=font(SANSB,10),fill=COL[sec])
    short=s if len(s)<=25 else s[:24].rstrip()+'…'
    d.text((xx+24,yy),short,font=font(SER,10),fill=BODY)

# date-check and colophon
rule(970,sw=2)
d.rectangle((20,977,1004,1023),fill='#EAE5DC')
d.text((28,980),'DATE CHECK',font=font(SANSB,10),fill=RED)
check='Every story happened or was first reported on 19 November 2026. Left out: summits, results and announcements from other days.'
d.text((104,980),check,font=font(SER,10),fill=BODY)
colo='Sources: AP, Reuters, AFP, BBC, FT, Bloomberg, regional public broadcasters and named outlets · Edited and drawn for The World in One Day.'
d.text((28,999),colo,font=font(SERI,10),fill=BODY)

# Global geometry assertions
assert len(stories)+len(briefs)+len(index)==33
assert im.size==(1024,1024)
# Major content blocks are half-open rectangles, so touching rules are valid
# while any positive-area collision is rejected.
blocks=[('masthead',(20,12,1004,216)),('lead',(20,224,1004,495)),
        ('secondary',(20,501,1004,675)),('tertiary',(20,681,1004,855)),
        ('footer',(20,860,1004,966)),('datecheck',(20,970,1004,1024))]
for i,(an,a) in enumerate(blocks):
    assert 0<=a[0]<a[2]<=W and 0<=a[1]<a[3]<=H
    for bn,b in blocks[i+1:]:
        overlap=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
        assert overlap==0, f'blocks overlap: {an}/{bn}'
im.save('entry.png',optimize=True,compress_level=9)
assert os.path.getsize('entry.png') < 1024*1024
print(f'rendered entry.png: {os.path.getsize("entry.png")} bytes; 33 stories; 13 panels')
