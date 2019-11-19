import pyxel
import random
from mahjongpy import MahjongTable, MahjongTile, MahjongPlayer


table = MahjongTable()
p1,p2,p3,p4 = table.players
#p1.hands = MahjongTile.make_hands_set('129','19','19','1234','123') #和了テスト(国士無双13面待ち)
#p1.hands = MahjongTile.make_hands_set('1122','5566','3388','34') #ポンテスト
#p1.hands = MahjongTile.make_hands_set('234','456','234678','','12') #チーテスト
#p1.hands = MahjongTile.make_hands_set('234','456','234678','','12') #リーチテスト

 
class App:
    def __init__(self):
        pyxel.init(242,242, caption='Mahjong-py-xel', scale=2)
        self.selected_tile_index = 15
        self.selected_tile_index_pre = 15
        pyxel.mouse(True)
        pyxel.load('Mahjongpai.pyxres')
        self.wait_btn = False
        self.wait_tumo = False
        self.wait_ron = False
        self.wait_pon = False
        self.wait_chi = False
        self.wait_riichi = False
        self.wait_minkan = False
        self.wait_ankan = False
        self.ok = False
        self.cancel = False
        self.screen = ""
        self.prev_player = None
 
        pyxel.run(self.update, self.draw)


    def update(self):
        click = False
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            if self.wait_btn:
                if pyxel.mouse_x in range(175,196) and pyxel.mouse_y in range(210,219):
                    self.ok = True
                    self.wait_btn = False
                if pyxel.mouse_x in range(200,219) and pyxel.mouse_y in range(210,219):
                    self.cancel = True
                    self.wait_btn = False
            self.selected_tile_index_pre = self.selected_tile_index
            for i in range(23):
                if (pyxel.mouse_y > 222) and (((11*i)-1) < pyxel.mouse_x <= ((11*(i+1))-1)):
                    self.selected_tile_index = i-3
                    if self.selected_tile_index_pre == self.selected_tile_index:
                        click = True
        if click and self.selected_tile_index in range(len(p1.hands)) and (not self.wait_btn):
            tiles = p1.hands[:]
            if p1.turn != 0 and p1.latest_tile.tile_type is not None:
                try:
                    tiles.remove(p1.latest_tile)
                except ValueError:
                    p1.hands_display()
                    print('+')
                    print(p1.latest_tile.display)
                tiles.append(p1.latest_tile)
            p1.discard(tiles[self.selected_tile_index])
            self.selected_tile_index = 15
            for i in table.players[1:]:
                table.draw(i)
                discard_tile = i.hands[random.randrange(14)]
                self.prev_player = i
                i.discard(discard_tile)
                if p1.can_ron(discard_tile):
                    self.wait_ron = True
                    self.wait_btn = True
                    break
                elif p1.can_minkan(discard_tile) and (not p1.is_riichi):
                    self.wait_minkan = True
                    self.wait_btn = True
                elif p1.can_pon(discard_tile) and (not p1.is_riichi):
                    self.wait_pon = True
                    self.wait_btn = True
                    break
                elif i==p4 and p1.can_chi(discard_tile) and (not p1.is_riichi):
                    self.wait_chi = True
                    self.wait_btn = True
                    break
            else:
                print('draw')
                table.draw(p1)
        if p1.is_hora():
            self.wait_tumo = True
            self.wait_btn = True
        if p1.is_menzen() and  p1.is_tenpai() and (not p1.is_riichi):
            self.wait_riichi = True
            self.wait_btn = True
        if self.ok:
            if self.wait_tumo:
                p1.tumo()
                self.screen = "score"
                print(p1.score_fu())
                print(p1.score_han())
                self.wait_tumo = False
            if self.wait_ron:
                self.screen = "score"
                print(p1.score_fu())
                print(p1.score_han())
                p1.ron(self.prev_player.discards[-1])
                self.wait_ron = False
            if self.wait_minkan:
                p1.kan(self.prev_player.discards[-1])
                self.wait_minkan = False
            if self.wait_pon:
                p1.pon(self.prev_player.discards[-1])
                self.wait_pon = False
            if self.wait_chi:
                print('chi')
                p1.chi(self.prev_player.discards[-1])
                self.wait_chi = False
            if self.wait_riichi:
                p1.riichi()
                self.wait_riichi = False
            self.wait_btn = False
            self.ok = False
        if self.cancel:
            if self.wait_pon or self.wait_chi:
                self.wait_btn = False
                self.wait_pon = False
                self.wait_chi = False
                self.cancel = False
                if self.prev_player != p4:
                    for i in table.players[table.players.index(self.prev_player.next_player()):]:
                        table.draw(i)
                        discard_tile = i.hands[random.randrange(14)]
                        self.prev_player = i
                        i.discard(discard_tile)
                table.draw(p1)
            if self.wait_riichi:
                self.wait_btn = False
                self.cancel = False
                self.wait_riichi = False
    

    def draw(self):
        if self.screen == 'score':
            pyxel.cls(3)
            pyxel.text(70,50,str(p1.score_fu())+' FU',0)
            pyxel.text(70,60,str(p1.score_han())+' HAN',0)
            pyxel.text(70,70,str(p1.score())+' Points',0)
            pyxel.text(70,80,'Dora: '+str(p1.displayed_doras()),0)
            pyxel.text(70,90,'AkaDora: '+str(p1.akadoras()),0)
            pyxel.text(70,100,'YAKU:',0)
            for i,y in enumerate(p1.yakus()):
                pyxel.text(100,100+i*10,y,0)
            self.draw_hands()
        elif self.screen == 'test':
            pass
        else :
            pyxel.cls(3)
            pyxel.rectb(95,100,54,42,0)
            pyxel.text(50,50,str(p1.shanten()),0)
            pyxel.text(50,70,str(p1.turn),0)
            if p1.is_riichi:
                pyxel.bltm(110,131,0,8,14,2,1,0)
            self.draw_hands()
            for i,t in enumerate(table.dora_showing_tiles):
                self.draw_tile_only(10,10,t,0)
            wind_x = [97, 132, 139, 95]
            wind_y = [125, 132, 101, 102]
            score_x = [108]
            score_y = [135]
            pyxel.text(score_x[0],score_y[0],str(p1.points),0)
            for i,p in enumerate(table.players):
                self.draw_tile_trans(wind_x[i],wind_y[i],MahjongTile(p.wind),i*90,7)
                #pyxel.text(score_x[i],score_y[i],str(p.points),0)
                self.draw_discards(p, i*90)
            if self.wait_tumo:
                self.draw_button('TUMO','PASS')
            if self.wait_pon or self.wait_chi or self.wait_ron:
                index = table.players.index(self.prev_player)
                if index == 2:
                    size_x = 1
                    size_y = 2
                else:
                    size_x = 2
                    size_y = 1
                l = len(self.prev_player.discards)+5
                if index == 2:
                    pyxel.bltm(140-(l%6)*9, 83-(l//6)*17,0,3,20,size_x,size_y)
                elif index == 3:
                    pyxel.bltm(78-(l//6)*17, 95+(l%6)*9,0,0,20,size_x,size_y)
                elif index == 1:
                    pyxel.bltm(151+(l//6)*17, 138-(l%6)*9,0,0,21,size_x,size_y)

            if self.wait_ron:
                self.draw_button('RON','PASS')
            if self.wait_minkan:
                self.draw_button('KAN','PASS')
            if self.wait_pon:
                self.draw_button('PON','PASS')
            if self.wait_chi:
                self.draw_button('CHI','PASS')
            if self.wait_riichi:
                self.draw_button('RICHI','PASS')


    def draw_button(self, msg1, msg2):
        pyxel.rect(175,210,20,8,5)
        pyxel.text(178+(4-len(msg1))*2,212,msg1,6)
        pyxel.rect(200,210,20,8,5)
        pyxel.text(203,212,msg2,6)

    def draw_discards(self,p,angle=0):
        if angle == 0:
            for i,t in enumerate(p.discards):
                self.draw_tile_only(95+(i%6)*9, 143+(i//6)*17,t,angle)
        elif angle == 90:
            for i,t in enumerate(p.discards):
                self.draw_tile_only(151+(i//6)*17, 138-(i%6)*9,t,angle)

        elif angle == 270:
            for i,t in enumerate(p.discards):
                self.draw_tile_only(78-(i//6)*17, 95+(i%6)*9,t,angle)

        elif angle == 180:
            for i,t in enumerate(p.discards):
                self.draw_tile_only(140-(i%6)*9, 83-(i//6)*17,t,angle)




    def draw_hands(self):
        tiles = p1.hands[:]
        melds = p1.melds[:]
        minkans = p1.minkans[:]
        if p1.turn != 0 and p1.latest_tile.tile_type is not None and p1.latest_tile in tiles:
            try:
                tiles.remove(p1.latest_tile)
            except ValueError:
                print('ValueError')
                for i in p1.hands:
                    print(i.display)
                print('*')
                print(p1.latest_tile.display)
                pyxel.quit()
            tiles.append(p1.latest_tile)
        for i,t in enumerate(tiles):
           if i == self.selected_tile_index:
                self.draw_tile(33+i*11,215,t)
           else:
                self.draw_tile(33+i*11,225,t)
        for i,m in enumerate(melds):
            padding = 0
            for j,t in enumerate(m):
                if m.count(t)==1: #chi
                    if j == 0:
                        self.draw_tile(204-i*40+j*11,233,t,90)
                    else:
                        self.draw_tile(210-i*40+j*11,225,t)
                elif [(t in k) for k in p1.minkans]: #kan
                    continue
                else: #pon
                    if t.from_tacha:
                        self.draw_tile(204-i*40+j*11,233,t,90)
                        padding = 7
                    else:
                        self.draw_tile(203-i*40+j*11+padding,225,t)
        for i,m in enumerate(minkans):
            i += len(melds)
            padding = 0
            for j, t in enumerate(m):
                if t.from_tacha:
                    self.draw_tile(204-i*40+j*11,233,t,90)
                    padding = 7
                else:
                    self.draw_tile(203-i*40+j*11+padding,225,t)
 
    def draw_tile_trans(self,x,y,tile,angle,color):
        if angle%180==0:
            index_y = {'manzu':0, 'souzu':2, 'pinzu':4,'ton':6,'nan':6,'sha':6,'pei':6,'haku':8,'hatu':8,'tyun':8}
            index_x = {'ton':0,'nan':1,'sha':2,'pei':3,'haku':0,'hatu':1,'tyun':2}
            size_x = 1
            size_y = 2
        else:
            index_y = {'manzu':10, 'souzu':11, 'pinzu':12,'ton':13,'nan':13,'sha':13,'pei':13,'haku':14,'hatu':14,'tyun':14}
            index_x = {'ton':0,'nan':2,'sha':4,'pei':6,'haku':0,'hatu':2,'tyun':4}
            size_x = 2
            size_y = 1

        tm_y = index_y[tile.tile_type]
        if tile.tile_type in ['manzu','souzu','pinzu']:
            if angle%180 == 0:
                tm_x = tile.number-1
            else:
                tm_x = (tile.number-1)*2
        else:
            tm_x = index_x[tile.tile_type]
        if angle == 180:
            tm_x +=9
        elif angle == 270:
            tm_y += 5
        pyxel.bltm(x,y,0,tm_x,tm_y,size_x,size_y,color)


    def draw_tile_only(self, x, y,tile,angle):
        if angle%180==0:
            index_y = {'manzu':0, 'souzu':2, 'pinzu':4,'ton':6,'nan':6,'sha':6,'pei':6,'haku':8,'hatu':8,'tyun':8}
            index_x = {'ton':0,'nan':1,'sha':2,'pei':3,'haku':0,'hatu':1,'tyun':2}
            size_x = 1
            size_y = 2
        else:
            index_y = {'manzu':10, 'souzu':11, 'pinzu':12,'ton':13,'nan':13,'sha':13,'pei':13,'haku':14,'hatu':14,'tyun':14}
            index_x = {'ton':0,'nan':2,'sha':4,'pei':6,'haku':0,'hatu':2,'tyun':4}
            size_x = 2
            size_y = 1
        
        tm_y = index_y[tile.tile_type]
        if tile.tile_type in ['manzu','souzu','pinzu']:
            if angle%180 == 0:
                tm_x = tile.number-1
            else:
                tm_x = (tile.number-1)*2
        else:
            tm_x = index_x[tile.tile_type]
        if angle == 180:
            tm_x +=9
        elif angle == 270:
            tm_y += 5

        if tile.akadora:
            pyxel.pal(0,8)
            pyxel.pal(3,8)
        pyxel.bltm(x,y,0,tm_x,tm_y,size_x,size_y)
        pyxel.pal()
        self.draw_side_mini(x,y,angle)

    def draw_tile(self,x,y,tile,angle=0):
        self.draw_tile_only(x,y,tile,angle)
        if angle == 0:
            self.draw_side(x,y)


    def draw_side(self,x,y):
        pyxel.line(x+1,y-1,x+7,y-1,9)
        pyxel.line(x+2,y-2,x+7,y-2,9)
        pyxel.line(x+8,y-2,x+8,y+14,9)
        pyxel.line(x+9,y-2,x+9,y+13,9)

    def draw_side_mini(self,x,y,angle):
        if angle %180 == 0:
            pyxel.line(x+1,y-1,x+7,y-1,9)
            pyxel.line(x+8,y-1,x+8,y+14,9)
        else:
            pyxel.line(x-1,y-1,x-1,y+6,9)
            pyxel.line(x-1,y-1,x+15,y-1,9)
 
        




App()
