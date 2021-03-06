import pyxel
import random
from mahjongpy import MahjongTable, MahjongTile, MahjongPlayer


class App:
    def __init__(self):
        pyxel.init(242,256, caption='Mahjong-py-xel ver.0.1.0', scale=2)
        pyxel.mouse(True)
        pyxel.load('Mahjongpai.pyxres')
        self.table = MahjongTable(oya_player=random.randrange(1,5),kandora_sokumekuri=True)
        #self.table = MahjongTable(oya_player=1,kandora_sokumekuri=True)
        self.p1,self.p2,self.p3,self.p4 = self.table.players
        #for i in range(68):
        #    self.table.tiles.pop(0)
        self.init_var()
        pyxel.run(self.update, self.draw)

    def init_var(self):
        self.selected_tile_index = 15
        self.selected_tile_index_pre = 15
        self.wait_btn = False
        self.wait_tumo = False
        self.wait_ron = False
        self.wait_pon = False
        self.wait_chi = False
        self.wait_riichi = False
        self.wait_daiminkan = False
        self.wait_ankan = False
        self.wait_kakan = False
        self.ok = False
        self.cancel = False
        self.screen = 'start'
        self.prev_player = None
        self.riichi_this_turn = False
        self.melds_padding = [0]
        self.cpu_wait = True
        self.waiting = False
        self.tenpai_count = 0
        self.kakan_tile = []
        self.yakunashi = False
        self.furiten = False
        self.gamemode = 1

        #self.p1.hands = MahjongTile.make_hands_set('129','19','19','1234','123') #和了テスト(国士無双13面待ち)
        #self.p1.hands = MahjongTile.make_hands_set('1122','5566','3388','34') #ポンテスト
        #self.p1.hands = MahjongTile.make_hands_set('234','456','234678','','12') #チーテスト
        #self.p1.hands = MahjongTile.make_hands_set('234','456','234678','','12') #リーチテスト
        #self.p1.hands = MahjongTile.make_hands_set('279','456','444469','','12') #暗槓テスト
        #self.p1.hands = MahjongTile.make_hands_set('45','3459999','11678','','') #嶺上開花テスト
        #self.p1.hands = MahjongTile.make_hands_set('222','444','777469','','12') #明槓テスト

    def update(self):
        if self.screen == 'start':
            self.screen = ''
            start = False
            for i in self.table.players[1:]:
                if i.oya: start = True
                if start:
                    if not i.oya:
                        self.table.draw(i)
                    discard_tile = i.hands[random.randrange(14)]
                    self.prev_player = i
                    i.discard(discard_tile)
                    if self.p1.can_ron(discard_tile):
                        self.wait_ron = True
                        self.wait_btn = True
                        break
                    elif self.p1.can_minkan(discard_tile) and (not self.p1.is_riichi):
                        self.wait_daiminkan = True
                        self.wait_btn = True
                        break
                    elif self.p1.can_pon(discard_tile) and (not self.p1.is_riichi):
                        self.wait_pon = True
                        self.wait_btn = True
                        break
                    elif i == self.p4 and self.p1.can_chi(discard_tile) and (not self.p1.is_riichi):
                        self.wait_chi = True
                        self.wait_btn = True
                        break
            else:
                print('draw')
                self.riichi_this_turn = False
                self.table.draw(self.p1)

        click = False
        if self.screen == 'finished': return()
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            if self.screen in ['ryukyoku','score']:
                self.table = self.table.next_round()
                self.p1,self.p2,self.p3,self.p4 = self.table.players
                if (self.gamemode == 1 and self.table.wind == 'nan') or (self.gamemode == 2 and self.table.wind == 'sha'):
                    self.screen = 'finished'
                    return()
                if min([int(j.points) for j in self.table.players]) < 0:
                    self.screen = 'finished'
                    return()
                self.init_var()
                return()

            if self.wait_btn:
                if pyxel.mouse_x in range(175,196) and pyxel.mouse_y in range(210,219):
                    self.ok = True
                    self.wait_btn = False
                if pyxel.mouse_x in range(200,219) and pyxel.mouse_y in range(210,219):
                    self.cancel = True
                    self.wait_btn = False
            self.selected_tile_index_pre = self.selected_tile_index
            for i in range(23):
                if (pyxel.mouse_y > 212) and (((11*i)-1) < pyxel.mouse_x <= ((11*(i+1))-1)):
                    self.selected_tile_index = i-3
                    if self.selected_tile_index_pre == self.selected_tile_index:
                        click = True
        if self.screen in ['score','ryukyoku']: return()
        if click and self.selected_tile_index in range(len(self.p1.hands)) and (not self.wait_btn):
            tiles = self.p1.hands[:]
            if self.p1.turn != 0 and self.p1.latest_tile.tile_type is not None:
                try:
                    tiles.remove(self.p1.latest_tile)
                except ValueError:
                    self.p1.hands_display()
                    print('+')
                    print(self.p1.latest_tile.display)
                tiles.append(self.p1.latest_tile)
            self.p1.discard(tiles[self.selected_tile_index])
            if self.table.tiles_left() < 0:
                self.screen = 'ryukyoku'
                self.table.ryukyoku()
                self.tenpai_count = len([i for i in self.table.players if i.is_tenpai()])
                return()
            self.selected_tile_index = 15
            for i in self.table.players[1:]:
                self.table.draw(i)
                discard_tile = i.hands[random.randrange(14)]
                self.prev_player = i
                i.discard(discard_tile)
                if self.table.tiles_left() < 0:
                    self.screen = 'ryukyoku'
                    self.table.ryukyoku()
                    self.tenpai_count = len([i for i in self.table.players if i.is_tenpai()])
                    return()
                if self.p1.can_ron(discard_tile):
                    self.wait_ron = True
                    self.wait_btn = True
                    break
                elif self.p1.can_minkan(discard_tile) and (not self.p1.is_riichi):
                    self.wait_daiminkan = True
                    self.wait_btn = True
                    break
                elif self.p1.can_pon(discard_tile) and (not self.p1.is_riichi):
                    self.wait_pon = True
                    self.wait_btn = True
                    break
                elif i == self.p4 and self.p1.can_chi(discard_tile) and (not self.p1.is_riichi):
                    self.wait_chi = True
                    self.wait_btn = True
                    break
            else:
                print('draw')
                self.riichi_this_turn = False
                self.table.draw(self.p1)
        if self.p1.is_hora():
            self.wait_tumo = True
            self.wait_btn = True
        if self.p1.is_menzen() and self.p1.is_tenpai() and (not self.p1.is_riichi) and (not self.wait_btn) and (not self.riichi_this_turn) and (not self.wait_btn):
            self.wait_riichi = True
            self.riichi_this_turn = True
            self.wait_btn = True
        elif self.p1.can_ankan() and (not self.p1.is_riichi):
            self.wait_ankan = True
            self.wait_btn = True
        elif self.p1.can_kakan() and (not self.p1.is_riichi):
            self.wait_kakan = True
            self.wait_btn = True

        if self.ok:
            if self.wait_tumo:
                if len(self.p1.yakus()) == 0:
                    self.yakunashi = True
                    self.wait_btn = True
                    self.ok = False
                    return()
                self.p1.tumo()
                self.selected_tile_index = 15
                self.screen = "score"
                print(self.p1.score_fu())
                print(self.p1.score_han())
                self.wait_tumo = False
            if self.wait_ron:
                if len(self.p1.yakus()) == 0:
                    print('yakunashi')
                    self.yakunashi = True
                    self.wait_btn = True
                    self.ok = False
                    return()
                if self.prev_player.discards[-1] in self.p1.discards:  # 赤ドラ未考慮
                    self.furiten = True
                    self.wait_btn = True
                    self.ok = False
                    return()
                self.selected_tile_index = 15
                self.screen = "score"
                print(self.p1.score_fu())
                print(self.p1.score_han())
                self.p1.ron(self.prev_player.discards[-1])
                self.wait_ron = False
            if self.wait_daiminkan:
                self.p1.kan(self.prev_player.discards[-1])
                self.wait_daiminkan = False
            if self.wait_ankan:
                self.p1.kan([i for i in self.p1.hands if self.p1.hands.count(i) == 4][0])
                self.wait_ankan = False
            if self.wait_kakan:
                self.p1.kakan(self.prev_player.discards[-1])
                self.kakan_tile.append(self.prev_player.discards[-1])
                self.wait_kakan = False
            if self.wait_pon:
                self.p1.pon(self.prev_player.discards[-1])
                self.wait_pon = False
            if self.wait_chi:
                print('chi')
                self.p1.chi(self.prev_player.discards[-1])
                self.wait_chi = False
            if self.wait_riichi:
                self.p1.riichi()
                self.wait_riichi = False
            self.wait_btn = False
            self.ok = False
        if self.cancel:
            if self.wait_pon or self.wait_chi or self.wait_ron or self.wait_daiminkan:
                self.wait_btn = False
                self.wait_pon = False
                self.wait_chi = False
                self.wait_ron = False
                self.wait_daiminkan = False
                self.wait_kakan = False
                self.yakunashi = False
                self.furiten = False
                self.cancel = False
                if self.prev_player != self.p4:
                    for i in self.table.players[self.table.players.index(self.prev_player.next_player()):]:
                        self.table.draw(i)
                        discard_tile = i.hands[random.randrange(14)]
                        self.prev_player = i
                        i.discard(discard_tile)
                        if self.table.tiles_left() < 0:
                            self.screen = 'ryukyoku'
                            self.table.ryukyoku()
                            self.tenpai_count = len([i for i in self.table.players if i.is_tenpai()])
                            return()
                self.riichi_this_turn = False
                self.table.draw(self.p1)
            if self.wait_riichi or self.wait_kakan or self.wait_tumo:
                self.wait_btn = False
                self.cancel = False
                self.wait_riichi = False

    def draw(self):
        if self.screen == 'score':
            pyxel.cls(3)
            if self.p1.score_han() < 13:
                pyxel.text(90,70,str(self.p1.score_fu())+' FU',0)
                pyxel.text(90,80,str(self.p1.score_han())+' HAN',0)
            else:
                if self.p1.is_mangan: in_x=0;si_x=4
                if self.p1.is_haneman: in_x=2;si_x=4
                if self.p1.is_baiman: in_x=4;si_x=4
                if self.p1.is_sanbaiman: in_x=6;si_x=6
                if self.p1.is_kazoeyakuman: in_x=9;si_x=8
                if self.p1.yakuman_count() > 0: in_x=11;si_x=4
                pyxel.bltm(90,70,0,in_x*2,24,si_x,2,7)
            pyxel.text(90,90,str(self.p1.score())+' Points',0)
            pyxel.text(90,100,'Dora: '+str(self.p1.displayed_doras()),0)
            pyxel.text(90,110,'AkaDora: '+str(self.p1.akadoras()),0)
            pyxel.text(90,120,'YAKU:',0)
            for i,y in enumerate(self.p1.yakus()):
                pyxel.text(120,120+i*10,y,0)
            self.draw_hands()
            for i,t in enumerate(self.table.dora_showing_tiles):
                self.draw_tile_only(10+i*11,10,t,0)
            if self.p1.is_riichi:
                for i,t in enumerate(self.table.uradora_showing_tiles):
                    self.draw_tile_only(10+i*10,28,t,0)
            self.draw_players_score()
        elif self.screen == 'finished':
            pyxel.cls(3)
            i_x = [105,165,105,50]
            i_y = [190,125,50,125]
            score_x = [110,210,110,10]
            score_y = [220,130,30,130]
            for i,p in enumerate(self.table.players):
                pyxel.text(score_x[i]-(len(str(p.points))-6)*3,score_y[i],str(p.points),0)
            p_scores = []
            for i in self.table.players:
                p_scores.append(i.points)
            p_scores = sorted(p_scores)[::-1]
            for i,p in enumerate(self.table.players):
                pyxel.bltm(i_x[i],i_y[i],0,(p_scores.index(p.points)+1)*2,22,2,2,7)
                pyxel.bltm(i_x[i]+15,i_y[i],0,18,20,2,2,7)

        elif self.screen == 'ryukyoku':
            pyxel.cls(3)
            pyxel.bltm(100,110,0,4,20,4,2,7)
            pyxel.bltm(70,140,0,self.tenpai_count*2,22,2,2,7)
            pyxel.bltm(90,140,0,8,20,10,2,7)
            self.draw_players_score()
        else:
            pyxel.cls(3)
            pyxel.rect(0,243,242,14,5)
            pyxel.rectb(95,100,54,42,0)
            pyxel.text(10,250,"nokori:"+str(self.table.tiles_left()),0)
            pyxel.text(55,250,self.table.wind+str(self.table.kyoku)+'kyoku',0)
            pyxel.text(100,250,str(self.table.honba)+'honba',0)

            pyxel.bltm(150,244,0,10,22,1,2,7)
            pyxel.bltm(159,244,0,15+self.table.kyoku,22,1,2,7)
            pyxel.bltm(168,244,0,14,22,1,2,7)
            pyxel.bltm(180,244,0,15+self.table.honba,22,1,2,7)
            pyxel.bltm(189,244,0,20,22,2,2,7)

            pyxel.text(50,50,str(self.p1.shanten()),0)
            pyxel.text(50,70,str(self.p1.turn),0)
            if self.p1.is_riichi:
                pyxel.bltm(110,131,0,8,14,2,1,0)
            self.draw_hands()
            for i,t in enumerate(self.table.dora_showing_tiles):
                self.draw_tile_only(10+i*11,10,t,0)
            wind_x = [97, 132, 139, 96]
            wind_y = [125, 132, 101, 102]
            score_x = [108,127,118,98]
            score_y = [135,125,102,112]
            for i,p in enumerate(self.table.players):
                pyxel.text(score_x[i],score_y[i],str(p.points),0)
            for i,p in enumerate(self.table.players):
                self.draw_tile_trans(wind_x[i],wind_y[i],MahjongTile(p.wind),i*90,7)
                #pyxel.text(score_x[i],score_y[i],str(p.points),0)
                self.draw_discards(p, i*90)
            if self.wait_tumo:
                self.draw_button('TUMO','PASS')
            if self.wait_pon or self.wait_chi or self.wait_ron or self.wait_daiminkan:
                index = self.table.players.index(self.prev_player)
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
            if self.wait_daiminkan or self.wait_ankan or self.wait_kakan:
                self.draw_button('KAN','PASS')
            if self.wait_pon:
                self.draw_button('PON','PASS')
            if self.wait_chi:
                self.draw_button('CHI','PASS')
            if self.wait_riichi:
                self.draw_button('RICHI','PASS')
            if self.yakunashi:
                pyxel.text(165,200,'yakunashi',0)
            if self.furiten:
                pyxel.text(165,200,'furiten',0)

    def draw_players_score(self):
        score_diff = []
        if self.table.is_ryukyoku:
            if self.tenpai_count in [0,4]:
                score = {True:'(+0)', False:'(+0)'}
            else:
                score = {True:'(+'+str(int(3000/self.tenpai_count))+')', False:'(-'+str(int(3000/(4-self.tenpai_count)))+')'}
            for i in self.table.players:
                score_diff.append(score[i.is_tenpai()])
        else:
            score_diff = ['(+0)']*4
            payed_score = self.table.win_player.payed_score()
            if self.table.win_player.is_ron:
                score_diff[self.table.players.index(self.table.win_player)] = '(+'+str(self.table.win_player.score())+')'
                score_diff[self.table.players.index(self.table.furikomi_player)] = '(-'+str(payed_score[0])+')'
            elif self.table.win_player.is_tumo:
                for i in self.table.players:
                    if i == self.table.win_player:
                        score_diff[self.table.players.index(i)] = '(+'+str(i.score())+')'
                    elif i.oya:
                        score_diff[self.table.players.index(i)] = '(-'+str(payed_score[1])+')'
                    else:
                        score_diff[self.table.players.index(i)] = '(-'+str(payed_score[2])+')'

        score_x = [110,210,110,10]
        score_y = [190,130,30,130]
        for i,p in enumerate(self.table.players):
            pyxel.text(score_x[i]-(len(str(p.points))-6)*3,score_y[i],str(p.points),0)
            pyxel.text(score_x[i]+8+12-len(score_diff[i])*3,score_y[i]+10,score_diff[i],0)

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
        tiles = self.p1.hands[:]
        melds = self.p1.melds[:]
        minkans = self.p1.minkans[:]
        if self.p1.turn != 0 and self.p1.latest_tile.tile_type is not None and self.p1.latest_tile in tiles:
            tiles.remove(self.p1.latest_tile)
            tiles.append(self.p1.latest_tile)
        for i,t in enumerate(tiles):
            if i == self.selected_tile_index:
                self.draw_tile(33+i*11,215,t)
            else:
                self.draw_tile(33+i*11,225,t)
        melds_padding = []
        tmp_padding = 0
        kan_count = 0
        minkan_judge = False
        for i,m in enumerate(melds):
            padding = 0
            from_tacha_tile = False
            melds_padding.append(tmp_padding)
            if minkan_judge: kan_count += 1
            for j,t in enumerate(m):
                if m.count(t) == 1:  # chi
                    tmp_padding = 0
                    if j == 0:
                        self.draw_tile(204-i*40+j*11+melds_padding[i],233,t,90)
                    else:
                        self.draw_tile(210-i*40+j*11+melds_padding[i],225,t)
                elif any([(t in k) for k in self.p1.minkans]):  # minkan
                    minkan_judge = True
                    tmp_padding = -13*(kan_count+1)
                    minkan_judge = True
                    if t.from_tacha:
                        self.draw_tile(190-i*40+j*11+melds_padding[i],233,t,90)
                        from_tacha_tile = True
                        padding = 7
                    else:
                        if j == 2:
                            self.draw_tile(189-i*40+j*11+padding+melds_padding[i],225,t)
                            if from_tacha_tile:
                                self.draw_tile(189-i*40+(j+1)*11+padding+melds_padding[i],225,t)
                            else:
                                self.draw_tile(190-i*40+(j+1)*11+melds_padding[i],233,t,90)
                        else:
                            self.draw_tile(189-i*40+j*11+padding+melds_padding[i],225,t)
                elif any([(t in k) for k in self.p1.ankans]):  # ankan
                    tmp_padding = -13
                    if j == 0:
                        self.draw_tile_back(199-i*40+j*11+melds_padding[i],225)
                    elif j == 2:
                        self.draw_tile(199-i*40+j*11+melds_padding[i],225,t)
                        self.draw_tile_back(199-i*40+(j+1)*11+melds_padding[i],225)
                    else:
                        self.draw_tile(199-i*40+j*11+melds_padding[i],225,t)
                else:  # pon
                    tmp_padding = 0
                    if t.from_tacha:
                        self.draw_tile(204-i*40+j*11+melds_padding[i],233,t,90)
                        for k in self.kakan_tile:
                            if t == k:
                                self.draw_tile(204-i*40+j*11+melds_padding[i],223,t,90)
                        padding = 7
                    else:
                        self.draw_tile(203-i*40+j*11+padding+melds_padding[i],225,t)

        """
        for i,m in enumerate(minkans): #minkan
            i += len(melds)
            padding = 0
            for j, t in enumerate(m):
                if t.from_tacha:
                    self.draw_tile(229-i*40+j*11,233,t,90)
                    padding = 7
                else:
                    self.draw_tile(228-i*40+j*11+padding,225,t)
        """

    def draw_tile_back(self,x,y):
        pyxel.rect(x,y,8,16,9)
        self.draw_side(x,y)

    def draw_tile_trans(self,x,y,tile,angle,color):
        if angle % 180 == 0:
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
            if angle % 180 == 0:
                tm_x = tile.number-1
            else:
                tm_x = (tile.number-1)*2
        else:
            tm_x = index_x[tile.tile_type]
        if angle == 180:
            tm_x += 9
        elif angle == 270:
            tm_y += 5
        pyxel.bltm(x,y,0,tm_x,tm_y,size_x,size_y,color)

    def draw_tile_only(self, x, y,tile,angle):
        if angle % 180 == 0:
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
            if angle % 180 == 0:
                tm_x = tile.number-1
            else:
                tm_x = (tile.number-1)*2
        else:
            tm_x = index_x[tile.tile_type]
        if angle == 180:
            tm_x += 9
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
        if angle % 180 == 0:
            pyxel.line(x+1,y-1,x+7,y-1,9)
            pyxel.line(x+8,y-1,x+8,y+14,9)
        else:
            pyxel.line(x-1,y-1,x-1,y+6,9)
            pyxel.line(x-1,y-1,x+15,y-1,9)


App()
