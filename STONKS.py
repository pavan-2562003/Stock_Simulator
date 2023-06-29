import pygame
import random
import noise
import math
import time
import json
import os
import platform
import string

GAME_TITLE = "Stocks"

if platform.system() == "Windows":
    ver = platform.release()
    if  ver == "10" or ver == "9":
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()

pygame.mixer.init(44100, -16, 1, 1024)
pygame.init()
pygame.key.set_repeat(500, 25)
pygame.display.set_caption(GAME_TITLE)
CLOCK = pygame.time.Clock()

#### 
#### GLOBAL UTILS
####

## hack for screenshotting
pygame_display_flip = pygame.display.flip
def sshot_hack():
    if pygame.key.get_pressed()[pygame.K_F5]:
        filename = "{0}_{1}.png".format(GAME_TITLE, time.strftime("%Y_%m_%d-%H_%M_%S"))
        pygame.image.save(screen, filename)

    pygame_display_flip()

pygame.display.flip = sshot_hack

def tuplify(l):
    if isinstance(l, list): return tuple(map(tuplify, l))
    if isinstance(l, dict): return {k:tuplify(v) for k,v in l.items()}
    return l

def debug_sshot(state_class):
    pygame.image.save(state_class.screen, "{0}_{1}x{2}.png".format(state_class.__class__.__name__, *state_class.screen.get_size()))

def generate_filename(name):
    fn = ""
    for char in name:
        if char in string.ascii_letters or char in string.digits:
            fn += char
        else:
            fn += "_"

    while os.path.exists(os.path.join(saves_dir, fn+".savegame")):
        fn += "_"
    return fn+".savegame"

def read_json(filename):
    f = open(filename, "r", encoding="utf-8")
    data = json.loads(f.read())
    f.close()
    return data

def scale_(num, h=None):
    global SW
    return math.ceil((num/1280)*SW)

millnames = ['','K','M','B','t', 'q', 'Q', 's', 'S', 'o', 'n', 'd', 'U', 'D', 'T', 'Qt', 'Qd', 'Sd', 'St', 'O', 'N', 'v', 'c']

assets_dir = "./assets/"
sound_dir = os.path.join(assets_dir, "sound")
music_dir = os.path.join(assets_dir, "music")
img_dir = os.path.join(assets_dir, "graphics")
locale_dir = os.path.join(assets_dir, "locale")
settings_path = "settings.json"
saves_dir = "./saves/"

stonks_ico = pygame.image.load(os.path.join(assets_dir, "StonksIco.png"))
main_menu_bg = pygame.image.load(os.path.join(img_dir, "menu_backg.png"))
news_icon = pygame.image.load(os.path.join(img_dir, "news.png"))
warning_picture = pygame.image.load(os.path.join(img_dir, "warning.png"))
stonks_icon = pygame.image.load(os.path.join(img_dir, "stonks.png"))
not_stonks_icon = pygame.image.load(os.path.join(img_dir, "notstonks.png"))
bank_icon = pygame.image.load(os.path.join(img_dir, "bank.png"))
plus_icon = pygame.image.load(os.path.join(img_dir, "plus.png"))
minus_icon = pygame.image.load(os.path.join(img_dir, "minus.png"))
bank_icon = pygame.image.load(os.path.join(img_dir, "bank.png"))
cross_icon = pygame.image.load(os.path.join(img_dir, "cross.png"))
rng_icon = pygame.image.load(os.path.join(img_dir, "rng.png"))

snd_warn = pygame.mixer.Sound(os.path.join(sound_dir, "warn.wav"))
snd_buy = pygame.mixer.Sound(os.path.join(sound_dir, "buy.wav"))
snd_sell = pygame.mixer.Sound(os.path.join(sound_dir, "sell.wav"))
snd_news = pygame.mixer.Sound(os.path.join(sound_dir, "news.wav"))
snd_bank = pygame.mixer.Sound(os.path.join(sound_dir, "bank.wav"))
snd_rng = pygame.mixer.Sound(os.path.join(sound_dir, "rng.wav"))

pygame.display.set_icon(stonks_ico)

snds = [snd_warn,snd_buy,snd_sell,snd_news,snd_bank,snd_rng]
def set_snd_volume(v):
    for snd in snds:
        snd.set_volume(v)

def set_mus_volume(v):
    pygame.mixer.music.set_volume(v)

set_snd_volume(0)

playlist = ["song1.mp3", "song_lose.mp3"]
def play_music(file):
    pygame.mixer.music.fadeout(2)
    pygame.mixer.music.stop()
    pygame.mixer.music.load(os.path.join(music_dir, file))
    pygame.mixer.music.play(-1)

def play_single_song_forever(file):
    pygame.mixer.music.load(os.path.join(music_dir, file))
    pygame.mixer.music.play(-1)

def play_from_playlist(l):
    pygame.mixer.music.load(os.path.join(music_dir, random.choice(l)))
    pygame.mixer.music.play()

    pygame.mixer.music.queue(os.path.join(music_dir, random.choice(l)))


def fetch_locale_options():
    f = open(os.path.join(locale_dir, "locale.json"), "r", encoding="utf-8")
    data = json.loads(f.read())["locale"]

    return data

def get_settings():
    if os.path.exists(settings_path):
        return read_json(settings_path)["StonksSettings"]
    else:
        save_settings()
        return get_settings()

def save_settings(w=1280,h=720,fullscreen=False,music_volume=1.0,sound_volume=1.0,locale="en"):
    f = open(settings_path, "w")
    d = {}

    d["StonksSettings"] = {}
    d["StonksSettings"]["w"] = w
    d["StonksSettings"]["h"] = h
    d["StonksSettings"]["fullscreen"] = fullscreen
    d["StonksSettings"]["music_volume"] = music_volume
    d["StonksSettings"]["sound_volume"] = sound_volume
    d["StonksSettings"]["locale"] = locale

    f.write(json.dumps(d))
    f.close()

def save_settings_dict(settings):
    save_settings(settings["w"], settings["h"], settings["fullscreen"], settings["music_volume"], settings["sound_volume"], settings["locale"])

game_settings = get_settings()
set_snd_volume(game_settings["sound_volume"])
set_mus_volume(game_settings["music_volume"])

SW = game_settings["w"]
SH = game_settings["h"]

game_locale_options = fetch_locale_options()
LANG = read_json(os.path.join(locale_dir, game_settings["locale"] + ".json"))

def reload_locale():
    global LANG
    global game_locale_options
    game_locale_options = fetch_locale_options()
    LANG = read_json(os.path.join(locale_dir, game_settings["locale"] + ".json"))

font,font2,font3,font4,font5,font6,font7 = None,None,None,None,None,None,None

def construct_fonts():
    global font,font2,font3,font4,font5,font6,font7
    font = pygame.font.SysFont("consolas", scale_(45), True)
    font2 = pygame.font.SysFont("consolas", scale_(35), True)
    font3 = pygame.font.SysFont("consolas", scale_(22), True)
    font4 = pygame.font.SysFont("consolas", scale_(50), True)
    font5 = pygame.font.SysFont("consolas", scale_(14), True)
    font6 = pygame.font.SysFont("consolas", scale_(20), True)
    font7 = pygame.font.SysFont("consolas", scale_(72), True)

construct_fonts()

def get_game_info(filename):
    f = open(filename, "r", encoding="utf-8")
    data = json.loads(f.read())

    name = data["Stonks"]["GameName"]
    money = data["Stonks"]["Money"]
    price = data["Stonks"]["Stock"]["val"]
    shares = data["Stonks"]["ShareManager"]["shares_owned"]
    graph_values = data["Stonks"]["Stock"]["history"]
    try:
        last_played = data["Stonks"]["LastPlayed"]
    except:
        last_played = 0

    return name,money,price,shares,graph_values,last_played

def format_num(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                    int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.1f}{}'.format(n / 10**(3 * millidx), millnames[millidx])
    
def get_num_range(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                    int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    return millidx                      

def format_num_whole(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                    int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

def put_buttons_in_middle_collumn(buttons, w, h, pad=50, start=None):
    pad = scale_(pad, SH)
    rh = 0
    for button in buttons:
        button.put_in_middle(w, h, y=False)
        rh += button.rect.h + pad
    rh -= pad

    if not start:
        y = (h-rh)/2
        for button in buttons:
            button.set_pos(button.x, y)
            y += button.rect.h + pad
    else:
        y = start
        for button in buttons:
            button.set_pos(button.x, y)
            y += button.rect.h + pad

def center_rect(rect, w, h):
    rect.x = (w-rect.w)/2
    rect.y = (h-rect.h)/2

    return rect

def render_multiline_text(text, font, color, maxw=100, maxh=100):
    words = text.split(' ')
    spacew = font.size(" ")[0]
    x,y = 0,0
    surf = pygame.Surface((maxw, maxh), pygame.SRCALPHA)
    for word in words:
        word_surf = font.render(word, True, color)
        ww, wh = word_surf.get_size()
        if x + ww >= maxw:
            x = 0
            y += wh
        surf.blit(word_surf, (x, y))
        x += ww + spacew

    return surf

#### 
#### STONKS LOGIC
####
        
class Stock():
    ## no iter: when loading game do not iterate (would change RNG state)
    def __init__(self, news_toast_manager, rng, no_iter=False):
        self.rng = rng
        self.news = news_toast_manager
        
        self.val = 0
        self._iter = 0
        self._nxt = 10
        self._target = 0 if no_iter else self.rng.randint(-50, 50)/10
        self.history = []
        
        if not no_iter:
            self.iterate()
        
##    def iterate(self):
##        self._iter += 1
##        self.val += self.val * ((self._target)/100)*(self._iter/self._nxt)
##        self.val += self.val * noise.pnoise1(self._iter/1000) * 2
##        if self._iter >= self._nxt:
##            self._iter = 0
##            self._nxt = self._iter + random.randint(2, 5)
##            self._target = random.randint(-50, 50)/10
##        return self.val

    def iterate(self):
        self._iter += 1
        self.val += noise.pnoise1(self._iter/10)*0.7
        self.val += noise.pnoise1(self._iter/6)*0.4
        self.val += noise.pnoise1(self._iter/20)*0.3
        self.val += noise.pnoise1(self._iter/5)*0.2
        self.val += noise.snoise2(self.val/1000, self._iter/1000)*0.2

        self.val += self.val * ((self._target)/100)*(self._iter/self._nxt)
        if self._iter >= self._nxt:
            self._iter = 0
            self._nxt = self._iter + self.rng.randint(4, 20)
            self._target = self.rng.randint(-18, 18)/10

            if random.randint(1, 40) == 10:
                action = ""
                time = ""
                sentence = [LANG["news01"], LANG["news02"], LANG["news03"], LANG["news04"]]
                ##sentence = ["Experts predict that the $MKSFT stock will", "It is predicted that $MKSFT will", "Experts are certain that $MKSFT is going to", "We think that $MKSFT is heading to"]
                power = ""
                
                if self._nxt < 30:
                    time = LANG["news_time01"]
                elif self._nxt < 70:
                    time = LANG["news_time02"]
                elif self._nxt < 150:
                    time = LANG["news_time03"]
                elif self._nxt < 200:
                    time = LANG["news_time04"]
                
                if self._target >= 0:
                    action = LANG["news_rise"]
                if self._target <= 0:
                    action = LANG["news_fall"]

                pwr = abs(self._target)
                if pwr < 20:
                    power = LANG["news_pwr01"]
                if pwr < 18:
                    power = LANG["news_pwr02"]
                if pwr < 10:
                    power = LANG["news_pwr03"]
                if pwr < 2:
                    power = LANG["news_pwr04"]

                ## font6 h=20 clr=(255, 128, 0)
                ##self.news.add_toast("NEWS: {0} {1} {2} {3}.".format(random.choice(sentence), action, power, time), delay=10, color=(255, 128, 0), font=font6)
                txt = "NEWS: {0} {1} {2} {3}.".format(random.choice(sentence), action, power, time)

                snd_news.play()
                self.news.add_toast(FRender().render_picture(news_icon, h=35).render_text(txt, font6, (255, 128, 0)), delay=10)
        self.history.append(self.val)
        return self.val

    def load_from_json(dta, news):
        data = dta["Stock"]
        rng = random.Random()

        ## data fixer
        try:
            state = data["rng"]
            rng.setstate(tuplify(state))
        except KeyError:
            print("rng not loaded!")
        
        stock = Stock(news, rng, no_iter=True)

        stock.val = data["val"]
        stock._iter = data["iter"]
        stock._nxt = data["nxt"]
        stock._target = data["target"]
        stock.history = data["history"]

        return stock

    def save_to_json(self):
        return {"val": self.val, "iter": self._iter, "nxt": self._nxt, "target": self._target, "history": self.history[-1000:], "rng": self.rng.getstate()}

class ShareManager():
    def __init__(self, stock):
        self.stock = stock
        self.shares_owned = 0
        self.invested = 0
        self.profit_line = 0

    def get_current_price(self, num=1):
        return self.stock.history[-1]*num

    def get_earnings(self):
        total_value = self.shares_owned*self.get_current_price()

        return total_value - self.invested

    def is_profit(self):
        return self.get_earnings() > 0

    def get_num_shares(self):
        return self.shares_owned

    def buy_share(self, num=1):
        self.shares_owned += num
        
        self.invested += self.get_current_price(num)

        self.profit_line = self.invested/self.shares_owned

        snd_buy.play()
        return self.get_current_price()

    def sell_share(self, num=1):
        if num >= self.shares_owned:
            num = self.shares_owned

        if num <= 0:
            return

        if self.shares_owned < 0:
            return

        earned = self.get_current_price()*num
        self.invested -= earned
        if self.invested <= 0:
            self.invested = 0
        self.shares_owned -= num
        snd_sell.play()

        return earned

    def save_to_json(self):
        return {"shares_owned": self.shares_owned, "invested": self.invested}

    def load_from_json(dta, stock):
        data = dta["ShareManager"]

        sm = ShareManager(stock)
        sm.shares_owned = data["shares_owned"]
        sm.invested = data["invested"]

        return sm

class HedgeFundController:
    def __init__(self, buypanel, share_manager, stonks_game):
        self.active = False
        self.buypanel = buypanel
        self.share_manager = share_manager

        self.buyamt = 1
        self.bought = False
        self.val_at_buy = 1000
        self.status = "rising"
        self.game = stonks_game

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def update(self, screen):
        if not self.active:
            return

        self.buyamt = math.floor((self.game.Money)/self.share_manager.get_current_price())
        self.buypanel.num_shares = self.buyamt

        try:
            cur = self.share_manager.stock.history[-1]
        except:
            cur = 0
        try:
            last = self.share_manager.stock.history[-3]
        except:
            last = 0

        if cur >= last:
            if not self.bought:
                self.buypanel.buy_shares()
                self.bought = True
            screen.blit(font.render("rising!", True, (255, 0, 0)), (10, 200))
        else:
            self.buypanel.num_shares = self.share_manager.shares_owned
            self.buypanel.sell_shares()
            self.bought = False
            screen.blit(font.render("dropping!", True, (255, 0, 0)), (10, 200))

        screen.blit(font.render("trading bot active", True, (255, 0, 0)), (10, 150))
     

#### 
#### GUI CLASSES
####

class FRender():
    def __init__(self):
        self.surf = None

    def render_text(self, text, font, color):
        if not self.surf:
            self.surf = font.render(text, True, color)
        else:
            txt = font.render(text, True, color)
            self.clamp_next(txt)

        return self

    def clamp_next(self, next_surf):
        pad = 5
        w,h = self.surf.get_size()
        nw,nh = next_surf.get_size()

        new_width = w+pad+nw
        new_height = max(h, nh)

        tmp = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
        tmp.blit(self.surf, (0, (new_height-h)/2))
        tmp.blit(next_surf, (w+pad, (new_height-nh)/2))

        self.surf = tmp
        
    def render_picture(self, pict, h=None):
        if not h:
            h = pict.get_size()[1]

        h = scale_(h)
        w = pict.get_size()[0]
        
        ratio = h/pict.get_size()[1]
        w *= ratio
        
        pict = pygame.transform.smoothscale(pict, (int(w), int(h)))
        if not self.surf:
            self.surf = pict
        else:
            self.clamp_next(pict)

        return self
    def get(self):
        return self.surf

class Entry():
    def __init__(self, x, y, w, text_pad=10, font=font2, initial_input="", max_chars=-1, enter_confirm=False):
        self.x = x
        self.y = y
        self.font = font
        self.text_pad = text_pad
        self.w = w
        self.h = self.font.render("|", True, (0, 0, 0)).get_size()[1]
        self.i = 0
        self.rect = pygame.Rect((self.x, self.y, self.w, self.h))
        self.cursor = 0
        self.max_chars=max_chars
        self.input_text = initial_input
        self.enter_confirm = enter_confirm

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect((self.x, self.y, self.w, self.h))

    def draw(self, screen):
        pad = scale_(5, SH)
        txt_surf = self.font.render(self.input_text, True, (255, 255, 255))

        screen.fill((255, 255, 255), self.rect.inflate(scale_(5, SH), pad))
        screen.fill((0, 0, 0), self.rect)
        
        screen.blit(txt_surf, (self.x+5, self.y+5))
        ##self.rect.h = txt_surf.get_size()[1]

        if self.i % 20 > 10:
            screen.fill((255, 255, 255), pygame.Rect(self.x+txt_surf.get_size()[0]+pad, self.y+pad, pad, self.h-pad))

        self.i += 1
        
    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                char = event.key
                if char == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif char == pygame.K_LEFT:
                    self.cursor += 1
                elif char == pygame.K_RETURN:
                    if self.enter_confirm:
                        return True
                elif event.unicode:
                    if len(self.input_text) >= self.max_chars and self.max_chars != -1:
                        return
                    char = event.unicode
                    self.input_text += char
                
                    
    def get(self):
        return self.input_text

class NumberEntry(Entry):
    def __init__(self, x, y, w, text_pad=10, font=font2, initial_input="", max_chars=-1):
        super()
        self.x = x
        self.y = y
        self.font = font
        self.text_pad = text_pad
        self.w = w
        self.h = self.font.render("|", True, (0, 0, 0)).get_size()[1]
        self.i = 0
        self.rect = pygame.Rect((self.x, self.y, self.w, self.h))
        self.cursor = 0
        self.max_chars=max_chars
        self.input_text = initial_input

    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                char = event.key
                if char == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif char == pygame.K_LEFT:
                    self.cursor += 1
                elif event.unicode:
                    char = event.unicode
                    if len(self.input_text) >= self.max_chars and self.max_chars != -1:
                        return
                    if char.isdigit():
                        self.input_text += char
                    
class Button():
    def __init__(self, x, y, text, text_pad=10, font=None):
        if not font:
            font = font2
            
        text_pad = scale_(text_pad)
        
        self.x = x
        self.y = y
        self.font = font
        self.text_pad = text_pad
        
        if type(text) == FRender:
            self.text_surf = text.get()
        else:
            self.text_surf = self.font.render(text, True, (255, 255, 255))
            
        w,h = self.text_surf.get_size()
        self.rect = pygame.Rect(self.x, self.y, w+self.text_pad, h+self.text_pad)

    def set_pos(self, x, y):
        self.x = x
        self.y = y

        self.update_rect()

    def update_rect(self):
        w,h = self.text_surf.get_size()
        self.rect = pygame.Rect(self.x, self.y, w+self.text_pad, h+self.text_pad)

    def place_in_border(self, dimensions, border="BR", xpad=0, ypad=0):
        ## TL TR BL BR
        xpad += scale_(5, SH)
        ypad += scale_(5, SH)
        
        if border == "TL":
            self.x = self.rect.w - xpad
            self.y = self.rect.h - ypad
        if border == "TR":
            self.x = dimensions[0] - self.rect.w - xpad
            self.y = ypad
        if border == "BL":
            self.x = xpad
            self.y = dimensions[1] - self.rect.h - ypad
        if border == "BR":
            self.x = dimensions[0] - self.rect.w - xpad
            self.y = dimensions[1] - self.rect.h - ypad

        self.update_rect()

    def put_in_middle(self, w, h, x=True, y=True):
        nx = (w-self.rect.w)/2
        ny = (w-self.rect.w)/2
        if x:
            self.x = nx
        if y:
            self.y = ny

        self.update_rect()

    def get_rect(self):
        return self.rect

    def get_size(self):
        return self.rect.w,self.rect.h

    def draw(self, screen, mouse_pos, overrideX=0, overrideY=0):
        pad = scale_(3, SH)
        clr = (0, 232, 0)
        if self.rect.collidepoint(mouse_pos):
            clr = (232, 0, 0)
        screen.fill((96, 96, 96), self.rect.inflate(pad, pad))
        screen.fill(clr, self.rect)
        screen.blit(self.text_surf, (self.x+self.text_pad/2, self.y+self.text_pad/2))

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.rect.collidepoint(event.pos):
                        return True

class Slider():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class RadioButton(Button):
    def __init__(self, x, y, text, text_pad=10, font=None):
        if not font:
            font = font2
        super()
        self.x = x
        self.y = y
        self.font = font
        self.text_pad = text_pad
        
        if type(text) == FRender:
            self.text_surf = text.get()
        else:
            self.text_surf = self.font.render(text, True, (255, 255, 255))
            
        w,h = self.text_surf.get_size()
        self.rect = pygame.Rect(self.x, self.y, w+self.text_pad, h+self.text_pad)

        self.checked = False

    def update(self, events):
        evt = super().update(events)
        if evt:
            self.checked = not self.checked
        return evt

    def set_custom_rect(self, w=None, h=None):
        if w:
            self.rect.w = w
        if h:
            self.rect.h = h

    def draw(self, screen, mouse_pos, xoff=0, yoff=0):
        pad = scale_(5, SH)
        rect = self.rect.copy()
        rect.x += xoff
        rect.y += yoff
        
        clr = (128, 128, 128)
        if self.rect.collidepoint(mouse_pos):
            clr = (196, 196, 196)

        if self.checked:
            screen.fill((255, 255, 255), rect.inflate(pad, pad))
        else:
            screen.fill((0, 0, 0), rect.inflate(pad, pad))
            
        screen.fill(clr, rect)
        screen.blit(self.text_surf, ((self.x+xoff)+self.text_pad/2, (self.y+yoff)+self.text_pad/2))

class RadioButtonRow:
    def __init__(self, x, y, pad=10):
        pad = scale_(pad, SH)
        self.rect = None
        self.x = x
        self.y = y
        self.pad = pad
        self.btns = []

    def set_pos(self, x, y):
        self.x = x
        self.y = y

        self.update_rect()
        self.place_buttons()

    def put_in_center(self, w, h):
        self.x = (w-self.rect.w)/2
        self.y = (h-self.rect.h)/2

        self.update_rect()
        self.place_buttons()

    def update(self, events):
        for btn in self.btns:
            if btn.update(events):
                for b2 in self.btns:
                    if b2 != btn:
                        b2.checked = False

    def draw(self, screen, mouse_pos):
        for btn in self.btns:
            if not btn.checked:
                btn.draw(screen, mouse_pos)
        for btn in self.btns:
            if btn.checked:
                btn.draw(screen, mouse_pos)

    def update_rect(self):
        w = 0
        heights = []
        for btn in self.btns:
            w += btn.rect.w + self.pad
            heights.append(btn.rect.h)

        self.rect = pygame.Rect(self.x, self.y, w, max(heights))

    def place_buttons(self):
        x = self.x
        y = self.y
        
        widths = []
        for btn in self.btns:
            widths.append(btn.rect.w)
            
        for btn in self.btns:
            btn.set_custom_rect(w=max(widths))
            btn.set_pos(x, self.y + (btn.rect.h-self.rect.h)/2)
            x += btn.rect.w + self.pad

    def add_button(self, text, text_pad=10, font=None):
        if not font:
            font = font2
        text_pad = scale_(text_pad)
        self.btns.append(RadioButton(0, 0, text, text_pad, font))

        if len(self.btns) == 1:
            self.btns[0].checked = True

        self.update_rect()
        self.place_buttons()

    def check_button(self, i):
        for j,btn in enumerate(self.btns):
            btn.checked = False
            if i == j:
                btn.checked = True

    def get_selected_item(self):
        for i,btn in enumerate(self.btns):
            if btn.checked:
                return i
            
class VerticalRadioButtonList(RadioButtonRow):
    def __init__(self, x, y, pad=0):
        super(RadioButtonRow)
        self.rect = None
        self.x = x
        self.y = y
        self.pad = pad
        self.btns = []

    def update_rect(self):
        h = 0
        widths = []
        for btn in self.btns:
            h += btn.rect.h + self.pad
            widths.append(btn.rect.w)
            
        self.rect = pygame.Rect(self.x, self.y, max(widths), h)

    def place_buttons(self):
        x = self.x
        y = self.y
        widths = []
        for btn in self.btns:
            btn.set_pos(x, y)
            y += btn.rect.h + self.pad
            widths.append(btn.rect.w)

        for btn in self.btns:
            btn.set_custom_rect(w=max(widths))

class ScrollRadioButtonList(VerticalRadioButtonList):
    def __init__(self, x, y, w, h, pad=0):
        super(VerticalRadioButtonList)
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.scrollpos = 0
        self.pad = pad
        self.btns = []
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def put_in_center(self, w, h):
        self.x = (w-self.rect.w)/2
        self.y = (h-self.rect.h)/2

        if self.y <= 0:
            self.y = 20

        self.update_rect()
        self.place_buttons()

    def update_rect(self):
        h = 0
        widths = []
        for btn in self.btns:
            h += btn.rect.h + self.pad
            widths.append(btn.rect.w)
            
        self.rect = pygame.Rect(self.x, self.y - self.scrollpos, max(widths), h)

    def place_buttons(self):
        x = self.x
        y = self.y
        y -= self.scrollpos
        widths = []
        for btn in self.btns:
            btn.set_pos(x, y)
            y += btn.rect.h + self.pad
            widths.append(btn.rect.w)

        for btn in self.btns:
            btn.set_custom_rect(w=self.w-10)

    def draw(self, screen, mouse_pos):
        pad = scale_(10)
        tmp = pygame.Surface((self.w+pad, self.h+pad))
        for btn in self.btns:
            if not btn.checked:
                btn.draw(tmp, mouse_pos, xoff=-self.x+pad, yoff=-self.y+pad)
        for btn in self.btns:
            if btn.checked:
                btn.draw(tmp, mouse_pos, xoff=-self.x+pad, yoff=-self.y+pad)

        rect = pygame.Rect(self.x-pad, self.y-pad, self.w+pad, self.h+pad)
        screen.fill((0, 0, 0), rect)
        screen.fill((255, 255, 255), rect.inflate(scale_(5), scale_(5)))

        if len(self.btns) <= 0:
            tmp.blit(font2.render(LANG["list_empty"], True, (255, 255, 255)), (scale_(25), scale_(25)))

        screen.blit(tmp, (self.x-pad, self.y-pad))
        
    def update(self, events):
        if len(self.btns) <= 0:
            return
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 4:
                    self.scrollpos -= self.btns[0].rect.h/2
                if e.button == 5:
                    self.scrollpos += self.btns[0].rect.h/2
                    
                if self.scrollpos <= 0:
                    self.scrollpos = 0
                if self.scrollpos >= self.rect.h:
                    self.scrollpos = self.rect.h
                self.update_rect()
                self.place_buttons()
        
        for btn in self.btns:
            ##btn.set_pos(btn.x, btn.y+self.scrollpos)
            if btn.update(events):
                for b2 in self.btns:
                    if b2 != btn:
                        b2.checked = False
class Graph():
    def __init__(self, values):
        self.values = values

    def update_values(self, values):
        self.values.extend(values)

    def draw(self, w, h, last=1000, draw_lines=True, draw_line=None):
        surf = pygame.Surface((w, h))
        w -= scale_(100)

        if len(self.values) <= 0:
            return surf
        
        values = self.values[-last:]
        numX = len(values)
        ymax = max(values)
        ymin = min(values)
        numY = abs(ymin) + abs(ymax)

        for i in range(len(values)-1):
            p1 = ymax-values[i]
            p2 = ymax-values[i+1]
            pygame.draw.line(surf, (0, 255, 0), ((i/numX)*w, (p1/numY)*h), (((i+1)/numX)*w, (p2/numY)*h), scale_(2))

        step = 15
        for i in range(step):
            c = i/step
            ypos = ((ymax-(c*(ymax)))/numY)*h
            surf.blit(font5.render("{0:.2f}".format(c*ymax), True, (255, 255, 255)), (w, ypos))
            if draw_lines:
                pygame.draw.line(surf, (64, 64, 64), (0, ypos), (w, ypos), 1)

        for j in range(step):
            ## calculate position of every j/step in values (maybe only a part of last)
            c = j/step
            xpos = c*(last/numX)*w
            if draw_lines:
                pygame.draw.line(surf, (64, 64, 64), (xpos, 0), (xpos, (ymax/numY)*h), scale_(1))

        cur = values[-1]
        surf.blit(font3.render("{0:.2f}".format(cur), True, (255, 255, 255), (255, 0, 0)), (w, ((ymax-cur)/numY)*h))

        ## draw line of profit
        if draw_line != None:
            ypos = ((ymax-draw_line)/numY)*h
            pygame.draw.line(surf, (255, 0, 0), (0, ypos), (w, ypos), scale_(2))

        return surf

class Toast():
    def __init__(self, text, delay, color=(255, 0, 0), font=None):
        if not font:
            font = font4
        self.active = True
        self.text = text
        self.target = time.time()+delay
        self.disappear = self.target+2
        self.opacity = 255
        self.color = color

        tmp = None
        if type(self.text) == FRender:
            tmp = self.text.get()
        else:
            tmp = font.render(self.text, True, self.color)

        ##tmp = font.render(self.text, True, self.color)
        self.surf = pygame.Surface(tmp.get_size())
        self.surf.convert_alpha()
        self.surf.blit(tmp, (0, 0))

    def get_size(self):
        return self.surf.get_size()

    def update(self):
        if not self.active:
            return
        
        if time.time() > self.target:
            self.opacity = 255-(time.time()-self.target)/(self.disappear-self.target)*255

        if time.time() >= self.disappear:
            self.active = False

    def draw(self):
        return self.surf

class ToastManager():
    def __init__(self):
        self.toasts = []

    def add_toast(self, text, delay=2, color=(255, 0, 0)):
        self.toasts.append(Toast(text, delay, color))

    def update(self):
        for toast in self.toasts[:]:
            toast.update()
            if not toast.active:
                self.toasts.remove(toast)

    def draw(self, screen, w, h):
        if len(self.toasts) <= 0:
            return
        th = self.toasts[0].get_size()[1]
        y = (h-th)/2
        for toast in self.toasts[::-1]:
            if toast.active:
                surf = toast.draw()
                surf.set_alpha(toast.opacity)
                screen.blit(surf, ((w-surf.get_size()[0])/2, y))
                y += surf.get_size()[1]

class NewsToastManager():
    def __init__(self):
        self.toasts = []

    def add_toast(self, text, delay=2, color=(255, 0, 0), font=None):
        if not font:
            font = font4
        self.toasts.append(Toast(text, delay, color, font=font))

    def update(self):
        for toast in self.toasts[:]:
            toast.update()
            if not toast.active:
                self.toasts.remove(toast)

    def draw(self, screen, w, h):
        if len(self.toasts) <= 0:
            return

        y = h-self.toasts[0].surf.get_size()[1]
        for toast in self.toasts:
            if toast.active:
                surf = toast.draw()
                surf.set_alpha(toast.opacity)
                screen.blit(surf, ((0, y)))
                y -= toast.surf.get_size()[1]

class BankManager():
    def __init__(self, share_manager, game):
        self.share_manager = share_manager
        self.game = game
        self.i = 0
        
        self.lent = False
        self.loanamt = 0
        self.repayments = 0
        self.duration = 0

        self.notice_cant_buy_shares = False
        self.notice_in_debt = False
        self.notice_bankrupt = False
        self.bank_btn = Button(0, 0, FRender().render_picture(bank_icon, h=65))
        self.bank_btn.set_pos(10, (SH-self.bank_btn.rect.h)/2)

        #name, amount, days, minimal_worth
        self.available_loans = [[LANG["bank_loan_small"], 5000, 5, 1000], [LANG["bank_loan_medium"], 100000, 20, 15000], [LANG["bank_loan_big"], 1000000, 50, 50000]]

    def save_to_json(self):
        return {"i": self.i, "lent": self.lent, "loanamt": self.loanamt, "repayments": self.repayments, "duration": self.duration, "notice_cant_buy_shares": self.notice_cant_buy_shares}

    def load_from_json(dta, share_manager, game):
        data = dta["BankManager"]

        bankmanager = BankManager(share_manager, game)
        bankmanager.i = data["i"]
        bankmanager.lent = data["lent"]
        bankmanager.loanamt = data["loanamt"]
        bankmanager.repayments = data["repayments"]
        bankmanager.duration = data["duration"]
        bankmanager.notice_cant_buy_shares = data["notice_cant_buy_shares"]

        return bankmanager

    def add_bank_toast(self, txt):
        snd_bank.play()
        self.game.NewsToastManager.add_toast(FRender().render_picture(bank_icon, h=35).render_text(txt, font6, (255, 128, 0)), delay=10)

    def get_loan(self, amt, duration):
        self.lent = True
        self.loanamt = amt
        self.duration = duration
        self.i = 0
        self.repayments = 0

        self.game.Money += self.loanamt
        self.add_bank_toast(LANG["bank_loan_borrow"].format(format_num(self.loanamt), self.duration))

    def repay_all_now(self):
        if self.lent:
            num = (self.duration-self.repayments)*(self.loanamt/self.duration)*1.25

            if num > self.game.Money:
                notice_dialog(screen, LANG["dialog_error"], screen.copy(), LANG["bank_insufficient_funds_repay"])
                return False
            else:
                self.game.Money -= num
                self.lent = False
                self.add_bank_toast(LANG["bank_repaid_early"].format(format_num(num)))
                return True

    def get_left_to_repay(self):
        if self.lent:
            return (self.duration-self.repayments)*(self.loanamt/self.duration)*1.25

    def get_total_repaid(self):
        if self.lent:
            return (self.repayments)*(self.loanamt/self.duration)*1.25

    def repay_loan_part(self):
        if self.repayments <= self.duration:
            repayamt = (self.loanamt/self.duration)*1.25
            self.game.Money -= repayamt
            self.repayments += 1
            
            if self.repayments >= self.duration:
                self.add_bank_toast(LANG["bank_repaid_fully"].format(format_num(repayamt)))
                self.lent = False
            else:
                self.add_bank_toast(LANG["bank_repaid"].format(format_num(repayamt)))

    def update(self, events, screen):
        self.i += 1
        if self.share_manager.get_current_price() > self.game.Money and not self.game.Money < 0 and self.share_manager.shares_owned == 0 and not self.notice_cant_buy_shares and not self.lent:
            self.add_bank_toast(LANG["bank_advert"])
            self.notice_cant_buy_shares = True

        if self.game.Money < 0 and self.share_manager.shares_owned != 0 and not self.notice_in_debt:
            self.add_bank_toast(LANG["bank_debt"])
            self.notice_in_debt = True

        if self.game.Money < 0 and self.share_manager.shares_owned == 0 and not self.notice_bankrupt:
            self.add_bank_toast(LANG["bank_bankrupt"])
            self.notice_bankrupt = True

        if self.game.Money > 0:
            self.notice_bankrupt = False
            self.notice_in_debt = False

        if self.i%1000 == 0:
            if self.lent:
                self.repay_loan_part()

        if self.bank_btn.update(events):
            self.open_bank_window(screen)

    def draw(self, screen, mouse_pos):
         self.bank_btn.draw(screen, mouse_pos)

    def open_bank_window(self, screen):
        rw,rh = scale_(900),scale_(680)
        menu_rect = center_rect(pygame.Rect(0, 0, rw, rh), *screen.get_size())
        prompt = FRender().render_picture(bank_icon, scale_(100)).render_text(LANG["bank_window_title"], font4, (255, 0, 0)).render_picture(bank_icon, scale_(100)).get()
        
        loan_selector = RadioButtonRow(0, 0)
        btn_OK = Button(0, 0, FRender().render_picture(cross_icon, scale_(50)), font=font4)
        bg = screen.copy().convert()
        bg.set_alpha(150)
        btn_OK.place_in_border((rw, rh), "TR", -menu_rect.x+scale_(20), menu_rect.y+scale_(20))
        btns = [btn_OK]

        btn_repay = Button(0, 0, LANG["bank_window_repay_now"])
        btn_repay.place_in_border((rw, rh), "BR", -menu_rect.x+scale_(20), -menu_rect.y+scale_(20))

        btn_take = Button(0, 0, LANG["bank_window_take_loan"])
        btn_take.place_in_border((rw, rh), "BR", -menu_rect.x+scale_(20), -menu_rect.y+scale_(20))

        for l in self.available_loans:
            loan_selector.add_button(l[0])

        loan_selector.put_in_center(rw, rh)
        loan_selector.set_pos(loan_selector.x+menu_rect.x, menu_rect.y+scale_(200))

        while True:
            ## if lent, show only pay all button and w
            screen.fill((0, 0, 0))
            screen.blit(bg, (0, 0))

            screen.fill((255, 255, 255), menu_rect.inflate(scale_(5), scale_(5)))
            screen.fill((0, 0, 0), menu_rect)

            screen.blit(prompt, ((screen.get_size()[0]-prompt.get_size()[0])/2, menu_rect.y+scale_(10)))

            events = pygame.event.get()
            for btn in btns:
                btn.draw(screen, pygame.mouse.get_pos())
                if btn.update(events):
                    if btn == btn_OK:
                        return

            text_x = menu_rect.x + scale_(20)
            if not self.lent:
                loan_selector.update(events)
                loan_selector.draw(screen, pygame.mouse.get_pos())

                loan_idx = loan_selector.get_selected_item()
                if loan_idx != None:
                    selected_loan = self.available_loans[loan_idx]
                    name,amount,days,minimal_worth = selected_loan
                    
                    screen.blit(FRender().render_text(LANG["bank_window_amount"], font4, (255, 255, 0)).render_text("$" + format_num(amount), font4, (255, 255, 255)).get(), (text_x, scale_(300)))
                    screen.blit(FRender().render_text(LANG["bank_window_days"], font4, (255, 255, 0)).render_text(str(days), font4, (255, 255, 255)).get(), (text_x, scale_(350)))
                    screen.blit(FRender().render_text(LANG["bank_window_minimal_worth"], font4, (255, 255, 0)).render_text("$" + format_num(minimal_worth), font4, (255, 0, 0) if minimal_worth > self.game.Money else (255, 255, 255)).get(), (text_x, scale_(400)))
                    screen.blit(FRender().render_text(LANG["bank_window_total_repayment"], font4, (255, 255, 0)).render_text("$" + format_num(amount*1.25), font4, (255, 255, 255)).get(), (text_x, scale_(450)))

                    btn_take.draw(screen, pygame.mouse.get_pos())
                    if btn_take.update(events):
                        if minimal_worth > self.game.Money:
                            notice_dialog(screen, LANG["dialog_error"], screen.copy(), LANG["bank_not_allowed"])
                        else:
                            self.get_loan(amount, days)
                            return
            else:
                screen.blit(FRender().render_text(LANG["bank_window_lent"], font4, (255, 255, 0)).render_text("$" + format_num(self.loanamt), font4, (255, 255, 255)).get(), (text_x, scale_(200)))
                screen.blit(FRender().render_text(LANG["bank_window_repaid"], font4, (255, 255, 0)).render_text("$" + format_num(self.get_total_repaid()), font4, (255, 255, 255)).get(), (text_x, scale_(250)))
                screen.blit(FRender().render_text(LANG["bank_window_left_to_repay"], font4, (255, 255, 0)).render_text("$" + format_num(self.get_left_to_repay()), font4, (255, 0, 0) if self.get_left_to_repay() > self.game.Money else (255, 255, 255)).get(), (text_x, scale_(300)))
                screen.blit(FRender().render_text(LANG["bank_window_days_left"], font4, (255, 255, 0)).render_text(str(self.duration-self.repayments), font4, (255, 255, 255)).get(), (text_x, scale_(350)))

                btn_repay.draw(screen, pygame.mouse.get_pos())
                if btn_repay.update(events):
                    if self.repay_all_now():
                        return
                
            pygame.display.flip()

class BuyPanel():
    def __init__(self, w, h, share_manager, game):
        self.share_manager = share_manager
        self.num_shares = 10
        
        self.buy_btn = Button(0, 0, LANG["stock_buy"])
        self.sell_btn = Button(0, 0, LANG["stock_sell"])

        self.plus_btn = Button(0, 0, FRender().render_picture(plus_icon, h=scale_(30)))
        self.minus_btn = Button(0, 0, FRender().render_picture(minus_icon, h=scale_(30)))

        self.sell_btn.place_in_border((w, h), "BR", scale_(5), scale_(5))
        self.buy_btn.place_in_border((w, h), "BR", self.sell_btn.get_size()[0]+scale_(15), scale_(5))

        self.plus_btn.place_in_border((w, h), "BR", scale_(120), scale_(70))
        self.minus_btn.place_in_border((w, h), "BR", scale_(25), scale_(70))

        self.plus_btn.set_pos(self.buy_btn.x+(self.buy_btn.rect.w-self.plus_btn.rect.w)/2, self.plus_btn.y)
        self.minus_btn.set_pos(self.sell_btn.x+(self.sell_btn.rect.w-self.minus_btn.rect.w)/2, self.minus_btn.y)

        self.btns = [self.buy_btn, self.sell_btn, self.plus_btn, self.minus_btn]

        self.game = game

    def draw(self, screen, mouse_pos):
        for btn in self.btns:
            btn.draw(screen, mouse_pos)

        amt = font3.render(LANG["stock_amount"].format(format_num_whole(self.num_shares)), True, (255, 0, 0) if self.share_manager.get_current_price(self.num_shares) > self.game.Money else (255, 255, 255))
        screen.blit(amt, (self.buy_btn.x-amt.get_size()[0]-scale_(10), self.plus_btn.y))

        buy_price = font3.render(LANG["stock_buy_price"].format(format_num(self.share_manager.get_current_price(self.num_shares))), True, (0, 255, 255))
        screen.blit(buy_price, (self.buy_btn.x-buy_price.get_size()[0]-scale_(10), self.plus_btn.y+scale_(24)))

        owned = font2.render(LANG["stock_owned"].format(format_num_whole(self.share_manager.get_num_shares())), True, (255, 255, 255))
        screen.blit(owned, (self.buy_btn.x-owned.get_size()[0]-scale_(10), self.buy_btn.y))

        value = font3.render(LANG["stock_owned_value"].format(format_num(self.share_manager.get_current_price(self.share_manager.shares_owned))), True, (0, 255, 255))
        screen.blit(value, (self.buy_btn.x-value.get_size()[0]-scale_(10), self.buy_btn.y+scale_(30)))

        earn = font2.render(LANG["stock_earnings"].format(format_num(self.share_manager.get_earnings())), True, (255, 0, 0))
        screen.blit(earn, (self.buy_btn.x-earn.get_size()[0]-scale_(10), self.plus_btn.y-scale_(50)))

    def add_shares(self, amt):
        ##if self.num_shares >= 10:
        ##    self.num_shares += amt*10
        ##else:
        ##    self.num_shares += amt*1
        ##if self.num_shares <= 0:
        ##    self.num_shares = 0
        keys = pygame.key.get_pressed()
        amt *= 1000**get_num_range(self.num_shares)
        if keys[pygame.K_LCTRL] and keys[pygame.K_LSHIFT]:
            self.num_shares += amt*100
        elif keys[pygame.K_LCTRL]:
            self.num_shares += amt*10
        else:
            self.num_shares += amt*1

        if self.num_shares <= 0:
            self.num_shares = 0
        
    def buy_shares(self):
        price = self.share_manager.get_current_price(self.num_shares)

        if self.num_shares <= 0:
            return

        if price > self.game.Money:
            ##self.game.ToastManager.add_toast("insufficient funds!", 5)
            self.game.ToastManager.add_toast(FRender().render_picture(warning_picture, 50).render_text(LANG["bank_insufficient_funds"], font4, (255, 0, 0)), 5)
            snd_warn.play()
            return
        else:
            self.game.Money -= price
            self.share_manager.buy_share(self.num_shares)
            self.game.ToastManager.add_toast(LANG["toast_bought"].format(format_num_whole(self.num_shares), format_num(price)), 5, (255, 255, 0))

    def sell_shares(self):
        num = self.num_shares
        if num >= self.share_manager.shares_owned:
            num = self.share_manager.shares_owned
        is_profit = self.share_manager.is_profit()
        earned = self.share_manager.sell_share(num)

        if earned != None:
            self.game.Money += earned
            ##self.game.ToastManager.add_toast("sold {0} $MKSFT for ${1}".format(format_num_whole(num), format_num(earned)), 5, (0, 255, 255))
            self.game.ToastManager.add_toast(FRender().render_picture(stonks_icon if is_profit else not_stonks_icon, 50).render_text(LANG["toast_sold"].format(format_num_whole(num), format_num(earned)), font4, (0, 255, 255)), 5)

    def update(self, events):
        for btn in self.btns:
            clicked = btn.update(events)
            if clicked:
                if btn == self.buy_btn:
                    self.buy_shares()
                if btn == self.sell_btn:
                    self.sell_shares()
                if btn == self.plus_btn:
                    self.add_shares(1)
                if btn == self.minus_btn:
                    self.add_shares(-1)

    def save_to_json(self):
        return {"num_shares": self.num_shares}

    def load_from_json(dta, w, h, share_manager, game):
        data = dta["BuyPanel"]
        
        buypanel = BuyPanel(w, h, share_manager, game)
        buypanel.num_shares = data["num_shares"]

        return buypanel
####
#### GUI DIALOGS
####

def make_dialog(screen, prompt, last_frame, rw=640, rh=300):
    rw, rh = scale_(rw), scale_(rh)
    prompt = font4.render(prompt, True, (255, 0, 0))    
    menu_rect = center_rect(pygame.Rect(0, 0, rw, rh), *screen.get_size())

    return prompt,menu_rect

def confirm_dialog(screen, prompt, last_frame, keys_confirm=False):
    snd_warn.play()
    prompt,menu_rect = make_dialog(screen, prompt, last_frame)
    rw,rh = menu_rect.w,menu_rect.h
    
    btn_yes = Button(0, 0, LANG["dialog_yes"], font=font4)
    btn_no = Button(0, 0, LANG["dialog_no"], font=font4)
    bg = last_frame.convert()
    bg.set_alpha(50)

    btn_yes.place_in_border((rw, rh), "BL", menu_rect.x+scale_(100), -menu_rect.y+scale_(50))
    btn_no.place_in_border((rw, rh), "BR", -menu_rect.x+scale_(100), -menu_rect.y+scale_(50))

    btns = [btn_yes, btn_no]
    while True:
        screen.fill((0, 0, 0))
        screen.blit(bg, (0, 0))

        screen.fill((255, 255, 255), menu_rect.inflate(scale_(5), scale_(5)))
        screen.fill((0, 0, 0), menu_rect)

        screen.blit(prompt, ((screen.get_size()[0]-prompt.get_size()[0])/2, menu_rect.y+scale_(10)))
        
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.KEYDOWN:
                if keys_confirm:
                    if e.key == pygame.K_RETURN:
                        return True
                    if e.key == pygame.K_ESCAPE:
                        return False
        for btn in btns:
            btn.draw(screen, pygame.mouse.get_pos())
            if btn.update(events):
                if btn == btn_yes:
                    return True
                if btn == btn_no:
                    return False
                     
        CLOCK.tick(60)
        pygame.display.flip()

def notice_dialog(screen, prompt, last_frame, bottom_text=LANG["dialog_alert"], enter_confirm=True):
    snd_warn.play()
    prompt,menu_rect = make_dialog(screen, prompt, last_frame)
    ##bottom_text_surf = font2.render(bottom_text, True, (255, 0, 0))
    bottom_text_surf = render_multiline_text(bottom_text, font2, (255, 0, 0), maxw=menu_rect.w, maxh=menu_rect.h)
    rw,rh = menu_rect.w,menu_rect.h
    
    btn_ok = Button(0, 0, LANG["dialog_ok"], font=font4)
    bg = last_frame.convert()
    bg.set_alpha(50)

    btn_ok.place_in_border((rw, rh), "BR", -menu_rect.x+scale_(20), -menu_rect.y+scale_(20))

    btns = [btn_ok]
    while True:
        screen.fill((0, 0, 0))
        screen.blit(bg, (0, 0))

        screen.fill((255, 255, 255), menu_rect.inflate(scale_(5), scale_(5)))
        screen.fill((0, 0, 0), menu_rect)

        screen.blit(prompt, ((screen.get_size()[0]-prompt.get_size()[0])/2, menu_rect.y+scale_(10)))
        screen.blit(bottom_text_surf, (menu_rect.x+scale_(20), menu_rect.y+scale_(100)))
        
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_RETURN:
                    return
        for btn in btns:
            btn.draw(screen, pygame.mouse.get_pos())
            if btn.update(events):
                return
                     
        CLOCK.tick(60)
        pygame.display.flip()

def enter_text_dialog(screen, prompt, last_frame, initial_input=""):
    prompt,menu_rect = make_dialog(screen, prompt, last_frame)
    rw,rh = menu_rect.w,menu_rect.h
    
    btn_OK = Button(0, 0, LANG["dialog_ok"], font=font4)
    bg = last_frame.convert()
    bg.set_alpha(50)
    btn_OK.place_in_border((rw, rh), "BR", -menu_rect.x+scale_(20), -menu_rect.y+scale_(20))
    btns = [btn_OK]

    entry = Entry(0, 0, scale_(500), initial_input=initial_input, max_chars=25, enter_confirm=True)
    tmp = center_rect(entry.rect, rw, rh)
    entry.set_pos(menu_rect.x+tmp.x, menu_rect.y+tmp.y)
    while True:
        screen.fill((0, 0, 0))
        screen.blit(bg, (0, 0))

        screen.fill((255, 255, 255), menu_rect.inflate(scale_(5), scale_(5)))
        screen.fill((0, 0, 0), menu_rect)

        screen.blit(prompt, ((screen.get_size()[0]-prompt.get_size()[0])/2, menu_rect.y+scale_(10)))
        
        events = pygame.event.get()
        entry.draw(screen)
        if entry.update(events):
            return entry.get()
        for btn in btns:
            btn.draw(screen, pygame.mouse.get_pos())
            if btn.update(events):
                if btn == btn_OK:
                    return entry.get()
                     
        CLOCK.tick(60)
        pygame.display.flip()

def choose_seed_dialog(screen, prompt, last_frame):
    prompt,menu_rect = make_dialog(screen, prompt, last_frame)
    rw,rh = menu_rect.w,menu_rect.h

    btn_random = Button(0, 0, LANG["dialog_randomize"], font=font4)
    btn_start = Button(0, 0, LANG["dialog_start"], font=font4)
    bg = last_frame.convert()
    bg.set_alpha(50)
    btn_start.place_in_border((rw, rh), "BR", -menu_rect.x+scale_(20), -menu_rect.y+scale_(20))
    btn_random.place_in_border((rw, rh), "BR", -menu_rect.x+btn_start.rect.w+scale_(40), -menu_rect.y+scale_(20))
    btns = [btn_start, btn_random]

    entry = NumberEntry(0, 0, scale_(500), initial_input=str(random.randint(0, 999999)), max_chars=10)
    tmp = center_rect(entry.rect, rw, rh)
    entry.set_pos(menu_rect.x+tmp.x, menu_rect.y+tmp.y)
    while True:
        screen.fill((0, 0, 0))
        screen.blit(bg, (0, 0))

        screen.fill((255, 255, 255), menu_rect.inflate(scale_(5), scale_(5)))
        screen.fill((0, 0, 0), menu_rect)

        screen.blit(prompt, ((screen.get_size()[0]-prompt.get_size()[0])/2, menu_rect.y+scale_(10)))
        
        events = pygame.event.get()
        entry.draw(screen)
        entry.update(events)
        for btn in btns:
            btn.draw(screen, pygame.mouse.get_pos())
            if btn.update(events):
                if btn == btn_start:
                    return int(entry.get())
                if btn == btn_random:
                    entry.input_text = str(random.randint(0, 9999999))
                     
        CLOCK.tick(60)
        pygame.display.flip()

#### 
#### GAME UTILS
####

class StonksGame():
    def __init__(self, sw=1280, sh=720, seed=None):
        if seed == None:
            seed = time.time()
        rng = random.Random(seed)
        
        self.created_at = time.time()
        self.last_played = None
        self.sw = sw
        self.sh = sh

        self.Money = 1000
        self.ToastManager = ToastManager()
        self.NewsToastManager = NewsToastManager()

        self.Graph = Graph([])
        self.Stock = Stock(self.NewsToastManager, rng)
        self.Stock.rng = rng
        self.ShareManager = ShareManager(self.Stock)
        self.BuyPanel = BuyPanel(self.sw, self.sh, self.ShareManager, self)
        self.BankManager = BankManager(self.ShareManager, self)
        self.GameName = None
        self.FileHandle = None

        self.init_cheat_hedgefund()

    def init_cheat_hedgefund(self):
        self.cheat_hedgefund = HedgeFundController(self.BuyPanel, self.ShareManager, self)
        
    def save_game(self):
        print("saving...")
        data = {}

        data["Stonks"] = {}
        data["Stonks"]["LastPlayed"] = time.time()
        data["Stonks"]["CreatedAt"] = self.created_at
        data["Stonks"]["GameName"] = self.GameName
        data["Stonks"]["Stock"] = self.Stock.save_to_json()
        data["Stonks"]["ShareManager"] = self.ShareManager.save_to_json()
        data["Stonks"]["BuyPanel"] = self.BuyPanel.save_to_json()
        data["Stonks"]["Money"] = self.Money
        data["Stonks"]["BankManager"] = self.BankManager.save_to_json()

        return data

    def save_to_disk(self, fn):
        self.ToastManager.add_toast(LANG["toast_game_saved"].format(self.GameName))
        self.FileHandle = fn
        f = open(fn, "w", encoding="utf-8")
        f.write(json.dumps(self.save_game()))

    def load_game(data, FileHandle=None):
        print("loading...")
        try:
            game = StonksGame()

            dta = data["Stonks"]
            game.last_played = dta["LastPlayed"]
            game.created_at = dta["CreatedAt"]
            game.Money = dta["Money"]
            game.Stock = Stock.load_from_json(dta, game.NewsToastManager)
            game.ShareManager = ShareManager.load_from_json(dta, game.Stock)
            game.BuyPanel = BuyPanel.load_from_json(dta, SW, SH, game.ShareManager, game)
            game.Graph = Graph(game.Stock.history[:])   ## bug twice update
            game.GameName = dta["GameName"]
            game.FileHandle = FileHandle
            game.BankManager = BankManager.load_from_json(dta, game.ShareManager, game)

            game.init_cheat_hedgefund()
        except KeyError as e:
            print(e)
            return None

        return game

    def is_bankrupt(self):
        if self.Money <= 0 and self.ShareManager.shares_owned == 0:
            return True
        return False
        
    def update(self, mouse_pos, events, screen, i):
        if i%2 == 0:
        ##for i in range(1337267):
            cur_val = self.Stock.iterate()
            self.Graph.update_values([cur_val])
        self.ToastManager.update()
        self.NewsToastManager.update()
        self.BuyPanel.update(events)
        self.BankManager.update(events, screen)

        self.cheat_hedgefund.update(screen)
        
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_c and e.mod & pygame.KMOD_LCTRL and e.mod & pygame.KMOD_LSHIFT:
                    temp = screen.copy()
                    code = enter_text_dialog(screen, LANG["dialog_secret_cheat"], temp)
                    name = ""

                    ## cheats for monkeys
                    if code == "hedgefund":
                        self.cheat_hedgefund.activate()
                        name = "auto trading bot"
                    elif code == "1929": ## wall street crash
                        self.Stock._nxt = random.randint(100, 500)
                        self.Stock._target = random.randint(0, 10)-25
                        name = "wall street crash of 1929"
                    elif code == "bankrupt":
                        self.Money = 0
                        self.ShareManager.shares_owned = 0
                        name = "force bankruptcy"
                    else:
                        notice_dialog(screen, LANG["dialog_error"], temp, LANG["dialog_secret_cheat_error"])
                        return

                    self.NewsToastManager.add_toast(FRender().render_picture(rng_icon, h=35).render_text("Cheat: " + name, font6, (255, 128, 0)), delay=10)
                    snd_rng.play()
        
    def draw(self, screen, mouse_pos, i):
        screen.blit(self.Graph.draw(self.sw, self.sh, draw_line=self.ShareManager.profit_line if self.ShareManager.shares_owned > 0 else None), (0, 0))
        screen.blit(font.render(LANG["game_stock_value"].format(self.Stock.val), True, (255, 0, 0)), (scale_(10), scale_(10)))
        screen.blit(font.render(LANG["money"].format(format_num(self.Money)), True, (0, 255, 255)), (scale_(10), scale_(50)))
        self.NewsToastManager.draw(screen, self.sw, self.sh)
        self.BuyPanel.draw(screen, mouse_pos)
        self.ToastManager.draw(screen, self.sw, self.sh)
        self.BankManager.draw(screen, mouse_pos)

class GameInfo():
    def __init__(self, filename, name, money, price, shares, last_values, last_played=0):
        self.filename = filename
        self.name = name
        self.money = money
        self.price = price
        self.shares = shares
        self.graph = Graph(last_values)
        self.last_played = last_played

    def load(self):
        f = open(self.filename, "r", encoding="utf-8")
        data = json.loads(f.read())
        gm = StonksGame.load_game(data, self.filename)
        if gm:
            gm.ToastManager.add_toast(LANG["toast_game_loaded"].format(data["Stonks"]["GameName"]))
        return gm

    def rename(self, name):
        f = open(self.filename, "r", encoding="utf-8")
        data = json.loads(f.read())
        data["Stonks"]["GameName"] = name

        f = open(self.filename, "w", encoding="utf-8")
        f.write(json.dumps(data))

    def delete(self):
        os.remove(self.filename)

class GameList():
    def __init__(self):
        self.games = []
        for file in os.listdir(saves_dir):
            if os.path.splitext(file)[1] == ".savegame":
                fn = os.path.join(saves_dir, file)
                self.games.append(GameInfo(fn, *get_game_info(fn)))

        ## sort by last played
        self.games = sorted(self.games, key=lambda x: x.last_played, reverse=True)

#### 
#### GAME STATE LOOPS
####
        
class MainMenu():
    def __init__(self, screen, force_game=None):
        self.running = True
        self.screen = screen
        self.backg_opacity = 0
        self.bg = main_menu_bg.convert()
        self.bg = pygame.transform.smoothscale(self.bg, self.screen.get_size())
        self.new_game_btn = Button(0, 0, LANG["menu_new_game"], font=font7)
        self.load_game_btn = Button(0, 0, LANG["menu_load_game"], font=font7)
        self.settings_btn = Button(0, 0, LANG["menu_settings"], font=font7)
        self.quit_btn = Button(0, 0, LANG["menu_quit"], font=font7)
        ##elf.test_btn = RadioButton(0, 0, "test", font=font7)

        self.btns = [self.new_game_btn, self.load_game_btn, self.settings_btn, self.quit_btn]

        self.w, self.h = screen.get_size()

        ##for btn in self.btns:
        ##    btn.put_in_middle(*screen.get_size(), y=False)

        ##self.RBR = RadioButtonRow(0, 0)
        ##self.RBR.add_button("test")
        ##self.RBR.add_button("test2")
        ##self.RBR.put_in_center(*screen.get_size())
        put_buttons_in_middle_collumn(self.btns, *screen.get_size(), pad=scale_(25), start=scale_(250))

        self.force_game = force_game

    def mainloop(self):
        while self.running:
            if not pygame.mixer.music.get_busy():
                play_single_song_forever("song1.mp3")
            screen.fill((0, 0, 0))
            
            self.bg.set_alpha(self.backg_opacity)
            screen.blit(self.bg, (0, 0))
            events = pygame.event.get()
            
            if not self.backg_opacity >= 255:
                self.backg_opacity += 4

            if type(self.force_game) == StonksGame:
                game = StonksGame.load_game(self.force_game.save_game()) ## ugly hack to fix resolution
                
                HPM = HPunStonksMain(screen, game=game)
                self.force_game = None ## clear this
                status = HPM.mainloop()
                if type(status) == StonksGame:
                    return status

            for btn in self.btns:
                btn.draw(self.screen, pygame.mouse.get_pos())
                if btn.update(events):
                    if btn == self.new_game_btn:
                        seed = choose_seed_dialog(screen, LANG["choose_seed"], screen.copy())
                        HPM = HPunStonksMain(screen, seed=seed)
                        status = HPM.mainloop()
                        if type(status) == StonksGame: ## game wants to reload but continue
                            return status

                    if btn == self.load_game_btn:
                        LOAD = LoadMenuMain(screen)
                        game = LOAD.mainloop()
                        if game:
                            HPM = HPunStonksMain(screen, game)
                            HPM.mainloop()

                    if btn == self.settings_btn:
                        SETTINGS = SettingsMenuMain(screen)
                        if SETTINGS.mainloop(): ## true if settings are changed
                            return False

                    if btn == self.quit_btn:
                        return True
            ###
            ##self.RBR.draw(self.screen, pygame.mouse.get_pos())
            ##self.RBR.update(events)
            ###
            
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False
                    return True
                
            pygame.display.flip()
            CLOCK.tick(60)

class HPunStonksMain():
    def __init__(self, screen, game=None, seed=None):
        self.running = True
        self.screen = screen
        self.bkpt_i = 0
        if game:
            self.game = game
            self.game.sw = screen.get_size()[0]
            self.game.sh = screen.get_size()[1]
        else:
            if seed:
                self.game = StonksGame(*screen.get_size(), seed=seed)
            else:
                self.game = StonksGame(*screen.get_size())

    def mainloop(self):
        i = 0
        while self.running:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                     if confirm_dialog(self.screen, LANG["dialog_exit_without_saving"], self.screen.copy(), keys_confirm=True):
                            self.running = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        PM = PauseMenuMain(self.screen, self.screen.copy(), self.game)
                        result = PM.mainloop()
                        if result == True:
                            self.game = PM.game
                        elif type(result) == StonksGame:
                            self.running = False
                            return self.game
                        else:
                            self.running = False
                            return False
                        
            mouse_pos = pygame.mouse.get_pos()
            
            screen.fill((0, 0, 0))
            self.game.draw(self.screen, mouse_pos, i)
            self.game.update(mouse_pos, events, self.screen, i)
                    
            pygame.display.flip()
            i += 1

            if self.game.is_bankrupt():
                self.bkpt_i += 1
                if self.bkpt_i > 10:
                    bm = BankruptMain(self.screen, self.screen.copy())
                    bm.mainloop()
                    return

            CLOCK.tick(60)
            
class PauseMenuMain():
    def __init__(self, screen, last_frame, game):
        self.running = True
        self.screen = screen
        self.last_frame = last_frame
        self.game = game

        self.last_frame.set_alpha(50)
        self.menu_rect = center_rect(pygame.Rect(0, 0, scale_(640), scale_(640)), *self.screen.get_size())

        self.unpause_btn = Button(0, 0, LANG["pause_back_game"], font=font)
        self.save_game_btn = Button(0, 0, LANG["pause_save"], font=font)
        self.load_game_btn = Button(0, 0, LANG["pause_load"], font=font)
        self.settings_btn = Button(0, 0, LANG["pause_settings"], font=font)
        self.back_btn = Button(0, 0, LANG["pause_back_menu"], font=font)
        self.txt = font7.render(LANG["pause_title"], True, (255, 255, 255))

        self.btns = [self.unpause_btn, self.save_game_btn, self.load_game_btn, self.settings_btn, self.back_btn]
        put_buttons_in_middle_collumn(self.btns, *self.screen.get_size(), pad=scale_(25))

    def mainloop(self):
        while self.running:
            screen.fill((0, 0, 0))
            screen.blit(self.last_frame, (0, 0))

            screen.fill((255, 255, 255), self.menu_rect.inflate(scale_(5), scale_(5)))
            screen.fill((0, 0, 0), self.menu_rect)
                
            screen.blit(self.txt, ((self.screen.get_size()[0]-self.txt.get_size()[0])/2, scale_(50)))
            
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False

                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.running = False

            for btn in self.btns:
                btn.draw(self.screen, pygame.mouse.get_pos())
                if btn.update(events):
                    if btn == self.load_game_btn:
                        LM = LoadMenuMain(self.screen, self.game)
                        game = LM.mainloop()
                        if game:
                            self.game = game
                            return True
                        
                    if btn == self.back_btn:
                        if confirm_dialog(self.screen, LANG["dialog_exit_without_saving"], self.screen.copy(), keys_confirm=True):
                            return False
                        else:
                            SM = SaveMenuMain(self.screen, self.game)
                            if SM.mainloop():
                                return True

                    if btn == self.save_game_btn:
                        SM = SaveMenuMain(self.screen, self.game)
                        if SM.mainloop():
                            return True
                        
                    if btn == self.settings_btn:
                        SETTINGS = SettingsMenuMain(self.screen)
                        if SETTINGS.mainloop(): ## true if settings are changed
                            return self.game

                    if btn == self.unpause_btn:
                        self.running = False
                    
            pygame.display.flip()
            CLOCK.tick(60)

        return True

class SaveMenuMain():
    def __init__(self, screen, game):
        self.game = game
        self.running = True
        self.screen = screen

        sw,sh = self.screen.get_size()
        list_pos = (scale_(20), scale_(100))
        self.save_list = ScrollRadioButtonList(*list_pos, scale_(500), self.screen.get_size()[1]-list_pos[1]-scale_(20))
        self.games = GameList()

        self.save_list.add_button(FRender().render_picture(plus_icon, 50).render_text(LANG["save_menu_save_new_file"], font2, (255, 255, 255)))
        select = 0
        for i,game in enumerate(self.games.games):
            self.save_list.add_button(game.name)

            if self.game != None and self.game.FileHandle == game.filename:
                select = i+1
        self.save_list.check_button(select)

        self.save_btn = Button(0, 0, LANG["save_menu_save"])
        self.save_btn.place_in_border((sw, sh), "BR", scale_(5), scale_(5))

        self.back_btn = Button(0, 0, LANG["menu_back"])
        self.back_btn.place_in_border((sw, sh), "TR", scale_(5), scale_(5))

        self.action_btns = [self.save_btn]
        self.perm_btns = [self.back_btn]

    def mainloop(self):
        while self.running:
            screen.fill((0, 0, 0))

            self.screen.blit(font7.render(LANG["save_menu_title"], True, (255, 0, 0)), (scale_(20), scale_(10)))
            
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.running = False

            self.save_list.draw(self.screen, pygame.mouse.get_pos())
            self.save_list.update(events)

            for btn in self.perm_btns:
                    btn.draw(screen, pygame.mouse.get_pos())
                    if btn.update(events):
                        if btn == self.back_btn:
                            return
                        
            cur_id = self.save_list.get_selected_item()
            if cur_id != None:
                for btn in self.action_btns:
                    btn.draw(screen, pygame.mouse.get_pos())
                    if btn.update(events):
                        if btn == self.save_btn:
                            ## saving into new position
                            if cur_id == 0:
                                game_name = enter_text_dialog(self.screen, LANG["dialog_enter_game_name"], self.screen.copy(), initial_input="My Game")
                                self.game.GameName = game_name
                                self.game.save_to_disk(os.path.join(saves_dir, generate_filename(game_name)))
                                return True
                            else:
                                game_id = cur_id-1
                                selected_game = self.games.games[game_id]
                                self.game.GameName = selected_game.name
                                self.game.save_to_disk(selected_game.filename)
                                return True
    
            pygame.display.flip()
    
class LoadMenuMain():
    def __init__(self, screen, game=None):
        self.running = True
        self.screen = screen
        self.game = game

        sw,sh = self.screen.get_size()
        self.update_save_list()
        
        self.load_btn = Button(0, 0, LANG["load_menu_load"])
        self.load_btn.place_in_border((sw, sh), "BR", scale_(5), scale_(5))

        self.delete_btn = Button(0, 0, LANG["load_menu_delete"])
        self.delete_btn.place_in_border((sw, sh), "BR", 5+self.load_btn.rect.w+scale_(15), scale_(5))

        self.rename_btn = Button(0, 0, LANG["load_menu_rename"])
        self.rename_btn.place_in_border((sw, sh), "BR", 5+self.load_btn.rect.w+15+self.delete_btn.rect.w+scale_(15), scale_(5))

        self.back_btn = Button(0, 0, LANG["menu_back"])
        self.back_btn.place_in_border((sw, sh), "TR", scale_(5), scale_(5))
            
        self.action_buttons = [self.load_btn, self.delete_btn, self.rename_btn]
        self.perm_buttons = [self.back_btn]

    def update_save_list(self):
        list_pos = (scale_(20), scale_(100))
        self.save_list = ScrollRadioButtonList(*list_pos, scale_(500), self.screen.get_size()[1]-list_pos[1]-scale_(20))

        self.games = GameList()
        select = 0
        for i,game in enumerate(self.games.games):
            self.save_list.add_button(game.name)

            if self.game != None and self.game.FileHandle == game.filename:
                select = i

        self.save_list.check_button(select)

    def mainloop(self):
        sw,sh = self.screen.get_size()
        gw, gh = scale_(500), scale_(325)
        while self.running:
            self.screen.fill((0, 0, 0))

            self.screen.blit(font7.render(LANG["load_menu_title"], True, (255, 0, 0)), (scale_(10), scale_(10)))
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        self.running = False

            self.save_list.draw(self.screen, pygame.mouse.get_pos())
            self.save_list.update(events)

            if len(self.games.games) <= 0:
                self.screen.blit(FRender().render_picture(warning_picture, 50).render_text(LANG["load_menu_no_games"], font4, (255, 255, 0)).get(), (scale_(530), scale_(100)))

            cur_id = self.save_list.get_selected_item()
            if cur_id != None:
                gx,gy = sw-gw-scale_(5),sh-gh-scale_(95)
            
                cur_game = self.games.games[cur_id]

                graph = cur_game.graph.draw(gw, gh)
                rect = graph.get_rect()
                rect.x,rect.y = gx,gy
                screen.fill((255, 255, 255), rect.inflate(5, 5))
                screen.blit(graph, (gx, gy))
                
                ##self.screen.blit(font4.render("Name: " + cur_game.name, True, (255, 255, 0)), (530, 100))
                self.screen.blit(FRender().render_text(LANG["load_menu_name"], font4, (255, 255, 0)).render_text(cur_game.name, font4, (255, 255, 255)).get(), (scale_(530), scale_(100)))
                self.screen.blit(FRender().render_text(LANG["load_menu_money"], font4, (255, 255, 0)).render_text("$" + format_num(cur_game.money), font4, (255, 255, 255)).get(), (scale_(530), scale_(150)))
                self.screen.blit(FRender().render_text(LANG["load_menu_shares"], font4, (255, 255, 0)).render_text(format_num_whole(cur_game.shares), font4, (255, 255, 255)).get(), (scale_(530), scale_(200)))
                self.screen.blit(FRender().render_text(LANG["load_menu_value"], font4, (255, 255, 0)).render_text("$" + format_num(cur_game.price), font4, (255, 255, 255)).get(), (scale_(530), scale_(250)))

                for btn in self.action_buttons:
                    btn.draw(screen, pygame.mouse.get_pos())
                    
            for btn in self.perm_buttons:
                btn.draw(screen, pygame.mouse.get_pos())
                if btn.update(events):
                    if btn == self.back_btn:
                        self.running = False

            if cur_id != None:
                for btn in self.action_buttons:
                    if btn.update(events):
                        if btn == self.load_btn:
                            game = cur_game.load()
                            if game == None:
                                notice_dialog(self.screen, LANG["dialog_load_failed_title"], self.screen.copy(), LANG["dialog_load_failed"])
                                break
                            game.sw,game.sh = screen.get_size()
                            return game
                        if btn == self.delete_btn:
                            pygame.display.flip()
                            if confirm_dialog(self.screen, LANG["dialog_delete_confirm"], self.screen.copy(), keys_confirm=True):
                                cur_game.delete()
                                self.update_save_list()
                        if btn == self.rename_btn:
                            new_name = enter_text_dialog(self.screen, LANG["dialog_enter_game_name_new"], self.screen.copy(), initial_input=cur_game.name)
                            cur_game.rename(new_name)
                            self.update_save_list()
                                
            pygame.display.flip()
            CLOCK.tick(60)

class SettingsMenuMain():
    def __init__(self, screen):
        self.running = True
        self.screen = screen

        self.resolution_text = font.render(LANG["settings_resolution"], True, (255, 0, 0))
        self.fullscreen_text = font.render(LANG["settings_fullscreen"], True, (255, 0, 0))
        self.snd_volume_text = font.render(LANG["settings_sound_volume"], True, (255, 0, 0))
        self.mus_volume_text = font.render(LANG["settings_music_volume"], True, (255, 0, 0))
        self.locale_text     = font.render(LANG["settings_language"], True, (255, 0, 0))

        h_pad = 25

        self.resolutions = [[1920, 1080], [1600, 900], [1280, 720], [1024, 576]]
        self.resolution_selector = RadioButtonRow(self.resolution_text.get_size()[0]+scale_(h_pad), scale_(150))

        self.fullscreen_toggle = RadioButtonRow(self.fullscreen_text.get_size()[0]+scale_(h_pad), scale_(220))
        self.fullscreen_toggle.add_button(LANG["settings_on"])
        self.fullscreen_toggle.add_button(LANG["settings_off"])

        self.volumes = [0, 25, 50, 75, 100]
        self.snd_vol_selector = RadioButtonRow(self.snd_volume_text.get_size()[0]+scale_(h_pad), scale_(300))
        self.mus_vol_selector = RadioButtonRow(self.mus_volume_text.get_size()[0]+scale_(h_pad), scale_(380))

        self.langs = list(game_locale_options.keys())
        self.language_selector = RadioButtonRow(self.locale_text.get_size()[0]+scale_(h_pad), scale_(450))

        self.apply_btn = Button(0, 0, LANG["settings_apply"])
        self.apply_btn.place_in_border((SW, SH), "BR", scale_(5), scale_(5))

        self.btns = [self.apply_btn]

        for res in self.resolutions:
            self.resolution_selector.add_button("{0}x{1}".format(*res))

        for vol in self.volumes:
            self.snd_vol_selector.add_button("{0}%".format(vol))
            self.mus_vol_selector.add_button("{0}%".format(vol))

        for lang in self.langs:
            self.language_selector.add_button(game_locale_options[lang])

        screen_size = list(screen.get_size())
        if screen_size in self.resolutions:
            self.resolution_selector.check_button(self.resolutions.index(screen_size))

        self.fullscreen_toggle.check_button(1)
        if game_settings["fullscreen"] == True:
            self.fullscreen_toggle.check_button(0)

        self.language_selector.check_button(self.langs.index(game_settings["locale"]))

        sound_volume = game_settings["sound_volume"]
        music_volume = game_settings["music_volume"]
        self.snd_vol_selector.check_button(math.floor(sound_volume*4))
        self.mus_vol_selector.check_button(math.floor(music_volume*4))

    def mainloop(self):
        while self.running:
            screen.fill((0, 0, 0))
            self.screen.blit(font7.render(LANG["settings_title"], True, (255, 0, 0)), (scale_(20), scale_(20)))
            mouse_pos = pygame.mouse.get_pos()
            
            events = pygame.event.get()
           
            screen.blit(self.resolution_text, (scale_(20), scale_(150)))
            screen.blit(self.fullscreen_text, (scale_(20), scale_(220)))
            screen.blit(self.snd_volume_text, (scale_(20), scale_(290)))
            screen.blit(self.mus_volume_text, (scale_(20), scale_(360)))
            screen.blit(self.locale_text, (scale_(20), scale_(430)))
    
            self.resolution_selector.update(events)
            self.resolution_selector.draw(screen, mouse_pos)

            self.fullscreen_toggle.update(events)
            self.fullscreen_toggle.draw(screen, mouse_pos)

            self.snd_vol_selector.update(events)
            self.snd_vol_selector.draw(self.screen, mouse_pos)

            self.mus_vol_selector.update(events)
            self.mus_vol_selector.draw(self.screen, mouse_pos)

            self.language_selector.update(events)
            self.language_selector.draw(self.screen, mouse_pos)

            for btn in self.btns:
                btn.draw(screen, mouse_pos)
                if btn.update(events):
                    if btn == self.apply_btn:
                        global SW, SH
                        resolution_idx = self.resolution_selector.get_selected_item()
                        fullscreen_idx = self.fullscreen_toggle.get_selected_item()
                        snd_vol_idx = self.snd_vol_selector.get_selected_item()
                        mus_vol_idx = self.mus_vol_selector.get_selected_item()
                        language_idx = self.language_selector.get_selected_item()

                        if resolution_idx == None and fullscreen_idx == None and snd_vol_idx == None and mus_vol_idx == None and language_idx == None:
                            notice_dialog(screen, LANG["dialog_settings_fuck_you_title"], screen.copy(), LANG["dialog_settings_fuck_you"])
                            break
                        
                        if resolution_idx == None:
                            notice_dialog(screen, LANG["dialog_warning"], screen.copy(), LANG["dialog_settings_no_resolution"])
                            break
                        if fullscreen_idx == None:
                            notice_dialog(screen, LANG["dialog_warning"], screen.copy(), LANG["dialog_settings_no_fullscreen"])
                            break
                        if snd_vol_idx == None:
                            notice_dialog(screen, LANG["dialog_warning"], screen.copy(), LANG["dialog_settings_no_sound"])
                            break
                        if mus_vol_idx == None:
                            notice_dialog(screen, LANG["dialog_warning"], screen.copy(), LANG["dialog_settings_no_music"])
                            break
                        if language_idx == None:
                            notice_dialog(screen, LANG["dialog_warning"], screen.copy(), LANG["dialog_settings_no_language"])
                            break

                        new_resolution = self.resolutions[resolution_idx]
                        cur_resolution = list(self.screen.get_size())
                        new_fullscreen = True if fullscreen_idx == 0 else False
                        new_lang = self.langs[language_idx]

                        if new_resolution != cur_resolution or game_settings["fullscreen"] != new_fullscreen or new_lang != game_settings["locale"]:
                            notice_dialog(screen, LANG["dialog_warning"], screen.copy(), LANG["dialog_settings_reload"])

                            if new_fullscreen:
                                self.screen = pygame.display.set_mode(new_resolution, pygame.FULLSCREEN)
                            else:
                                self.screen = pygame.display.set_mode(new_resolution)
                            SW,SH = new_resolution

                            
                        game_settings["w"] = new_resolution[0]
                        game_settings["h"] = new_resolution[1]
                        game_settings["fullscreen"] = new_fullscreen
                        game_settings["music_volume"] = mus_vol_idx/4
                        game_settings["sound_volume"] = snd_vol_idx/4
                        game_settings["locale"] = new_lang
                        save_settings_dict(game_settings)

                        reload_locale()

                        return True
                    
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False

            pygame.display.flip()

class BankruptMain():
    def __init__(self, screen, last_frame):
        self.screen = screen
        self.last_frame = last_frame
        
    def mainloop(self):
        play_music("song_lose.mp3")
        i = 0

        lw, lh = self.last_frame.get_size()
        sw,sh = self.screen.get_size()
        bankrupt_txt = font7.render(LANG["bankrupt_title"], True, (255, 255, 255))
        bw,bh = bankrupt_txt.get_size()

        target = 2000
        while True:
            self.screen.fill((abs(math.cos(i/25))*120, abs(math.cos(i/50))*20, abs(math.cos(i/50))*20))

            val = 1-i/5000

            frame = pygame.transform.scale(self.last_frame, (int(lw*val), int(lh*val)))
            fw,fh = frame.get_size()

            fx,fy = (sw-fw)/2, (sh-fh)/2
            screen.blit(bankrupt_txt, ((sw-bw)/2, scale_(50)))
            frect = frame.get_rect()
            frect.x = fx
            frect.y = fy
            screen.fill((255, 255, 255), frect.inflate(abs(math.cos(i/50))*10, abs(math.cos(i/50))*10))
            screen.blit(frame, (fx, fy))
            pygame.display.flip()

            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    pygame.mixer.music.stop()
                    return

            if i >= target:
                screen.fill((0, 0, 0))
                tmp = screen.copy().convert_alpha()
                tmp.set_alpha(int(((i-target)/250)*255))
                screen.blit(tmp, (0, 0))

            if i >= target+250:
                pygame.mixer.music.fadeout(2000)
                return

            i += 1
            CLOCK.tick(60)
            
#### 
#### MAIN
####
if game_settings["fullscreen"]:
    screen = pygame.display.set_mode((SW, SH), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((SW, SH))

##

##

main = MainMenu(screen)
## main menu loop returns true when its gracefully exited
result = False
while result != True:
    result = main.mainloop()
    del main
    construct_fonts()
    set_snd_volume(game_settings["sound_volume"])
    set_mus_volume(game_settings["music_volume"])
    if type(result) == StonksGame:
        main = MainMenu(screen, force_game=result)
    else:
        main = MainMenu(screen)

pygame.quit()
