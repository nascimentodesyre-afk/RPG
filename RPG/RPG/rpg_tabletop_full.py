# rpg_tabletop_full.py
# Requisitos: pip install pygame

import pygame, sys, os, random
from collections import deque

pygame.init()
pygame.font.init()
pygame.mixer.init()

# -------------------------
# CONFIG - ESTILO MEDIEVAL
# -------------------------
SCREEN_W, SCREEN_H = 1100, 700
FPS = 60

# Caminhos absolutos seguros
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONT_DIR = os.path.join(BASE_DIR, "font")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# --- PALETA DE CORES MEDIEVAL ---
COLOR_WOOD_DARK = (48, 32, 20)
COLOR_WOOD_LIGHT = (111, 77, 46)
COLOR_PARCHMENT = (245, 222, 179)
COLOR_TEXT_DARK = (50, 40, 30)
COLOR_GOLD = (255, 190, 30)
COLOR_SHADOW = (20, 12, 5, 200)
COLOR_HP_RED = (190, 40, 40)
COLOR_MP_BLUE = (40, 90, 180)
COLOR_BORDER = (20, 12, 5)

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("RPG de Mesa — Conclave de Eldoria")
clock = pygame.time.Clock()

# -------------------------
# FONTES MEDIEVAIS (fallback seguro)
# -------------------------
def load_themed_font(font_name, size):
    font_path = os.path.join(FONT_DIR, font_name)
    if os.path.exists(font_path):
        try:
            return pygame.font.Font(font_path, size)
        except Exception as e:
            print(f"[ERRO] Fonte {font_name} não pôde ser carregada: {e}")
    print(f"[AVISO] Fonte {font_name} não encontrada, usando fonte padrão.")
    return pygame.font.SysFont("georgia", size)

# Ajuste aqui o nome do arquivo TTF dentro da pasta font/
FONT = load_themed_font("MorrisRoman-Black.ttf", 20)
FONT_BIG = load_themed_font("MorrisRoman-Black.ttf", 24)
FONT_TITLE = load_themed_font("MorrisRoman-Black.ttf", 32)

# -------------------------
# FUNÇÃO DE IMAGEM
# -------------------------
def load_image(name, size=None):
    """Carrega uma imagem do diretório assets com fallback de segurança."""
    if not name:
        surf = pygame.Surface(size or (64,64), pygame.SRCALPHA)
        surf.fill((100,100,100,255))
        pygame.draw.rect(surf, (180,180,180), surf.get_rect(), 2)
        return surf

    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        print(f"[AVISO] Imagem não encontrada: {path}")
        surf = pygame.Surface(size or (64,64), pygame.SRCALPHA)
        surf.fill((100,100,100,255))
        pygame.draw.rect(surf, (180,180,180), surf.get_rect(), 2)
        return surf

    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception as e:
        print(f"[ERRO] Falha ao carregar imagem '{path}': {e}")
        surf = pygame.Surface(size or (64,64), pygame.SRCALPHA)
        surf.fill((100,100,100,255))
        return surf

# -------------------------
# SONS (fallbacks)
# -------------------------
try:
    dice_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "dice_roll.wav"))
except Exception:
    dice_sound = None
    print("[AVISO] dice_roll.wav não encontrado ou falha ao carregar.")

try:
    dice_end_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "dice_stop.wav"))
except Exception:
    dice_end_sound = None
    print("[AVISO] dice_stop.wav não encontrado ou falha ao carregar.")

# -------------------------
# MAPA / FUNDO com fallback
# -------------------------
map_img = load_image("Scene Overview.png", (SCREEN_W, SCREEN_H))
# se falhar, gera textura simples
if map_img.get_width() < SCREEN_W:
    map_img = pygame.Surface((SCREEN_W, SCREEN_H))
    map_img.fill(COLOR_WOOD_DARK)
    for _ in range(500):
        x1, y1 = random.randint(0, SCREEN_W), random.randint(0, SCREEN_H)
        x2, y2 = x1 + random.randint(-50, 50), y1 + random.randint(-50, 50)
        pygame.draw.line(map_img, (80,60,40,50), (x1, y1), (x2, y2), 2)

# -------------------------
# CLASSES (Ability, Character, Enemy)
# -------------------------
class Ability:
    def __init__(self, name, desc, power, cooldown, icon=None, cost_mp=0):
        self.name, self.desc, self.power = name, desc, power
        self.cooldown, self.remaining = cooldown, 0.0
        self.icon = load_image(icon, (56,56)) if icon else None
        self.cost_mp = cost_mp
    def ready(self): return self.remaining <= 0.0
    def use(self):
        if self.ready(): self.remaining = self.cooldown; return True
        return False
    def tick(self, dt):
        if self.remaining > 0: self.remaining = max(0.0, self.remaining - dt)

class Character:
    def __init__(self):
        self.name, self.level = "Sir Alaric", 1
        self.max_hp, self.hp = 100, 100
        self.max_mp, self.mp = 40, 40
        self.portrait = load_image("portrait.png", (120,120))
        self.abilities = [
            Ability("Golpe", "Ataque físico preciso.", 8, 1.5, "skill_sword.png"),
            Ability("Chama", "Magia de fogo potente.", 24, 6.0, "skill_fire.png", 10),
            Ability("Cura", "Restaura parte da vida.", -22, 8.0, "skill_heal.png", 8),
        ]
        self.inventory = {"Poção de Vida": 2}
        self.exp, self.alive = 0, True
    def update(self, dt):
        for a in self.abilities: a.tick(dt)
        if self.hp <= 0: self.alive = False

player = Character()

class Enemy:
    def __init__(self, name, hp, atk, desc=""):
        self.name, self.max_hp, self.hp, self.atk = name, hp, hp, atk
        self.desc, self.alive = desc, True
    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)
        if self.hp <= 0: self.alive = False

# -------------------------
# DIALOGUE BOX (Mestre)
# -------------------------
class DialogueBox:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.queue = deque()
        self.visible, self.text, self.speaker = True, "", "Mestre"
        self.char_index, self.timer, self.speed = 0, 0.0, 0.02
    def push(self, text, speaker="Mestre"):
        self.queue.append((text, speaker))
    def start_next(self):
        if self.queue:
            self.text, self.speaker = self.queue.popleft()
            self.char_index, self.timer, self.visible = 0, 0.0, True
        else:
            self.visible, self.text, self.speaker = False, "", ""
    def skip(self): self.char_index = len(self.text)
    def update(self, dt):
        if not self.visible and self.queue: self.start_next()
        if self.visible and self.char_index < len(self.text):
            self.timer += dt
            while self.timer >= self.speed and self.char_index < len(self.text):
                self.char_index += 1
                self.timer -= self.speed
    def draw(self, surf):
        if not self.visible: return
        pygame.draw.rect(surf, COLOR_PARCHMENT, self.rect, border_radius=5)
        pygame.draw.rect(surf, COLOR_WOOD_DARK, self.rect, 2, border_radius=5)
        name_txt = FONT_BIG.render(self.speaker, True, COLOR_TEXT_DARK)
        surf.blit(name_txt, (self.rect.x + 15, self.rect.y + 10))
        text_to_show = self.text[:self.char_index]
        lines = wrap_text(text_to_show, self.rect.w - 30, FONT)
        for i, l in enumerate(lines[:4]):
            surf.blit(FONT.render(l, True, COLOR_TEXT_DARK), (self.rect.x + 15, self.rect.y + 45 + i*24))
        hint = FONT.render("(Clique / Espaço para avançar)", True, (100, 80, 60))
        surf.blit(hint, (self.rect.right - hint.get_width() - 15, self.rect.bottom - 30))

def wrap_text(text, w, font):
    words, lines, cur = text.split(" "), [], ""
    for w0 in words:
        test = (cur + " " + w0).strip()
        if font.size(test)[0] <= w:
            cur = test
        else:
            lines.append(cur); cur = w0
    if cur: lines.append(cur)
    return lines

# diálogo inicial
dialog = DialogueBox((20, SCREEN_H - 180, SCREEN_W - 40, 160))
dialog.push("Saudações, nobre aventureiro. Bem-vindo à mesa do Conclave de Eldoria.")
dialog.push("Você é um herói do reino, e suas decisões ditarão o destino desta saga.")
dialog.push("Missão inicial: a Fera do Pântano tem aterrorizado a vila. Aceita o chamado?")

# -------------------------
# UI: Botão Medieval
# -------------------------
class Button:
    def __init__(self, rect, label, callback=None):
        self.rect, self.label, self.callback = pygame.Rect(rect), label, callback
        self.hover = False
    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.rect.collidepoint(ev.pos):
            if self.callback: self.callback()
    def update(self, mouse_pos): self.hover = self.rect.collidepoint(mouse_pos)
    def draw(self, surf):
        # sombra
        shadow_rect = self.rect.move(2, 2)
        pygame.draw.rect(surf, COLOR_SHADOW, shadow_rect, border_radius=4)
        base_color = COLOR_WOOD_LIGHT if self.hover else COLOR_WOOD_DARK
        pygame.draw.rect(surf, base_color, self.rect, border_radius=4)
        pygame.draw.rect(surf, COLOR_GOLD, self.rect, 2, border_radius=4)
        txt = FONT.render(self.label, True, COLOR_PARCHMENT)
        surf.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

# -------------------------
# MAP AREAS & INTERACTIVE
# -------------------------
class MapArea:
    def __init__(self, name, rect, description):
        self.name = name
        self.rect = pygame.Rect(rect)
        self.description = description
    def draw(self, surf, hover=False):
        # semi highlight
        if hover:
            s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            s.fill((255, 215, 100, 60))
            surf.blit(s, self.rect.topleft)
        label = FONT_BIG.render(self.name, True, COLOR_GOLD if hover else COLOR_PARCHMENT)
        surf.blit(label, (self.rect.centerx - label.get_width() // 2, self.rect.centery - 12))

# define áreas (ajuste coordenadas conforme seu mapa)
map_areas = [
    MapArea("Floresta Sombria", (140, 220, 180, 120),
            "A Floresta Sombria é densa e silenciosa. Sombras se movem entre as árvores..."),
    MapArea("Vila de Elden", (460, 480, 200, 140),
            "A Vila de Elden é o coração do reino, onde os camponeses rezam por paz."),
    MapArea("Torre Arcana", (830, 180, 200, 180),
            "A Torre Arcana emite uma energia estranha. O ar vibra com poder."),
    MapArea("Taverna do Grifo Dourado", (400, 600, 250, 80),
            "A taverna é repleta de risadas, bardos e intrigas."),
    MapArea("Montanha do Eco", (60, 80, 250, 120),
            "As Montanhas do Eco abrigam antigas ruínas e segredos esquecidos."),
]

# tokens (visuais)
player_tokens = [
    {"name":"Sir Alaric","pos":(350, 400)},
    {"name":"Mage Lyria","pos":(400, 420)},
]

def draw_tokens(surf):
    for p in player_tokens:
        pygame.draw.circle(surf, COLOR_MP_BLUE, p["pos"], 16)
        pygame.draw.circle(surf, COLOR_BORDER, p["pos"], 16, 2)
        txt = FONT.render(p["name"], True, COLOR_PARCHMENT)
        surf.blit(txt, (p["pos"][0] - txt.get_width() // 2, p["pos"][1] - 30))

# -------------------------
# SISTEMA DE MISSÕES (Quests)
# -------------------------
class Quest:
    def __init__(self, title, description, location, reward):
        self.title = title
        self.description = description
        self.location = location
        self.reward = reward
        self.completed = False
    def complete(self):
        self.completed = True
        return self.reward

class QuestLog:
    def __init__(self):
        self.quests = []
    def add(self, quest):
        self.quests.append(quest)
        dialog.push(f"Nova missão adicionada: {quest.title}", "Diário")
        dialog.push(quest.description, "Diário")
    def mark_completed(self, quest_title):
        for q in self.quests:
            if q.title == quest_title and not q.completed:
                q.complete()
                dialog.push(f"Missão concluída: {q.title}! Recompensa: {q.reward}", "Diário")
                return True
        return False
    def get_active(self):
        return [q for q in self.quests if not q.completed]
    def get_completed(self):
        return [q for q in self.quests if q.completed]

quest_log = QuestLog()

area_quests = {
    "Floresta Sombria": Quest("A Fera do Pântano", "Derrote a criatura que assombra a floresta.", "Floresta Sombria", "Espada Encantada"),
    "Vila de Elden": Quest("Ajuda ao Ferreiro", "Leve ferro puro da montanha até o ferreiro da vila.", "Vila de Elden", "50 moedas de ouro"),
    "Torre Arcana": Quest("O Grimório Perdido", "Recupere o grimório antigo roubado por um espírito.", "Torre Arcana", "Amuleto Arcano"),
    "Taverna do Grifo Dourado": Quest("Canção Interrompida", "Ajude o bardo a recuperar sua inspiração perdida.", "Taverna do Grifo Dourado", "Lira de Prata"),
    "Montanha do Eco": Quest("Eco das Ruínas", "Investigue as vozes misteriosas vindas das ruínas antigas.", "Montanha do Eco", "Joia Ancestral"),
}

# -------------------------
# SISTEMA DE DADOS e NARRAÇÃO
# -------------------------
def roll_dice(sides=20):
    return random.randint(1, sides)

def narrate_roll_result(result, difficulty=15):
    if result == 20:
        dialog.push(f"🎯 Rolou {result} — SUCESSO CRÍTICO! A sorte divina o favorece!", "Sistema")
    elif result >= difficulty:
        dialog.push(f"🎲 Rolou {result} — sucesso! Você realiza sua ação com êxito.", "Sistema")
    elif result == 1:
        dialog.push(f"💀 Rolou {result} — FALHA CRÍTICA! Algo terrível acontece...", "Sistema")
    else:
        dialog.push(f"🎲 Rolou {result} — falha. Sua tentativa não foi bem-sucedida.", "Sistema")

# -------------------------
# DICE ANIMATION (com callback)
# -------------------------
class DiceAnimation:
    def __init__(self, x, y, size=120):
        self.rect = pygame.Rect(x, y, size, size)
        self.rolling = False
        self.timer = 0.0
        self.duration = 1.2  # segundos de animação
        self.result = None
        self.current_value = 1
        self.font = FONT_TITLE
        self.sound_playing = False
        self.callback = None  # função para executar ao terminar: callback(result)

    def start(self, result, callback=None):
        self.rolling = True
        self.timer = 0.0
        self.result = result
        self.current_value = random.randint(1, 20)
        self.sound_playing = False
        self.callback = callback

    def update(self, dt):
        if not self.rolling:
            return
        self.timer += dt

        global dice_sound, dice_end_sound
        if not self.sound_playing and dice_sound:
            try:
                dice_sound.play(-1)
            except:
                pass
            self.sound_playing = True

        # alterna valores para simular giro
        if self.timer < self.duration:
            if int(self.timer * 25) % 2 == 0:
                self.current_value = random.randint(1, 20)
        else:
            self.current_value = self.result
            self.rolling = False
            # parar som e tocar som final
            if dice_sound:
                try: dice_sound.stop()
                except: pass
            if dice_end_sound:
                try: dice_end_sound.play()
                except: pass
            # narração + callback
            narrate_roll_result(self.result)
            if callable(self.callback):
                try:
                    self.callback(self.result)
                except Exception as e:
                    print("[ERRO] callback dice:", e)

    def draw(self, surf):
        if not self.rolling and self.result is None:
            return
        pygame.draw.rect(surf, COLOR_WOOD_LIGHT, self.rect, border_radius=10)
        pygame.draw.rect(surf, COLOR_GOLD, self.rect, 3, border_radius=10)
        num_surf = self.font.render(str(self.current_value), True, COLOR_PARCHMENT)
        surf.blit(num_surf, (self.rect.centerx - num_surf.get_width()//2,
                             self.rect.centery - num_surf.get_height()//2))

dice_anim = DiceAnimation(SCREEN_W//2 - 60, SCREEN_H//2 - 60)

# -------------------------
# INTERAÇÃO MAPA + MISSÕES
# -------------------------
def handle_area_quest(area_name):
    quest = area_quests.get(area_name)
    if not quest:
        dialog.push(f"Nenhuma missão disponível em {area_name}.", "Sistema")
        return

    if quest.completed:
        dialog.push(f"Você já concluiu a missão '{quest.title}'.", "Sistema")
        return

    active_titles = [q.title for q in quest_log.get_active()]

    if quest.title not in active_titles:
        quest_log.add(quest)
        return

    # Se já tem a missão: iniciar rolagem animada para tentar concluir
    result = roll_dice(20)
    # callback para processar o resultado depois da animação
    def after_roll(res):
        # dificuldade aqui padrão 15; pode ajustar por area/quest
        if res >= 15:
            quest_log.mark_completed(quest.title)
        else:
            dialog.push(f"A missão '{quest.title}' ainda não foi concluída. Tente novamente mais tarde.", "Sistema")
    dice_anim.start(result, callback=after_roll)

def handle_map_click(pos):
    for area in map_areas:
        if area.rect.collidepoint(pos):
            dialog.push(f"Você chega à {area.name}. {area.description}", "Mestre")
            dialog.push("O que você deseja fazer aqui?", "Mestre")
            handle_area_quest(area.name)
            dialog.start_next()
            return True
    return False

# -------------------------
# FUNÇÕES UI: QUEST LOG e ROLL manual
# -------------------------
def show_quest_log():
    active = quest_log.get_active()
    completed = quest_log.get_completed()
    if not active and not completed:
        dialog.push("Seu diário está vazio por enquanto.", "Diário"); return
    if active:
        dialog.push("📜 Missões Ativas:", "Diário")
        for q in active:
            dialog.push(f"- {q.title}: {q.description}", "Diário")
    if completed:
        dialog.push("✅ Missões Concluídas:", "Diário")
        for q in completed:
            dialog.push(f"- {q.title} (Recompensa: {q.reward})", "Diário")
    dialog.start_next()

def roll_d20_manual():
    result = roll_dice(20)
    # se quiser apenas narrar sem callback:
    dice_anim.start(result, callback=None)

# -------------------------
# JOGO: estados e combate (mantive seu sistema)
# -------------------------
GAME_STATE = {"mode":"explore"}
current_enemy, player_turn = None, True
combat_log = deque(maxlen=6)

def roll_d20(mod=0):
    return random.randint(1,20) + mod, random.randint(1,20)

def start_combat(enemy: Enemy):
    GAME_STATE["mode"] = "combat"
    global current_enemy, player_turn
    current_enemy, player_turn = enemy, True
    combat_log.clear()
    dialog.push(f"Iniciando combate: {enemy.name} apareceu!", "Sistema")
    dialog.start_next()

def enemy_action():
    global current_enemy, player_turn
    if not current_enemy or not current_enemy.alive: return
    r, t = roll_d20()
    dmg = max(1, current_enemy.atk + (t//10))
    player.hp = max(0, player.hp - dmg)
    combat_log.appendleft(f"{current_enemy.name} atacou e causou {dmg} de dano.")
    if player.hp <= 0:
        dialog.push("Você foi derrotado... O Mestre lamenta.", "Sistema")
        GAME_STATE["mode"] = "finished"
    else:
        player_turn = True

def player_use_ability(idx):
    global player_turn, current_enemy
    a = player.abilities[idx]
    if not a.use():
        dialog.push(f"{a.name} ainda em recarga ({round(a.remaining,1)}s).", "Sistema")
        return
    if player.mp < a.cost_mp:
        dialog.push("Energia mística insuficiente!", "Sistema"); return
    player.mp -= a.cost_mp
    if GAME_STATE["mode"] != "combat":
        if a.power < 0:
            player.hp = min(player.max_hp, player.hp - a.power)
            dialog.push(f"Você usa {a.name} e recupera {-a.power} de vida.", "Jogador")
        else:
            dialog.push(f"Você usa {a.name}. O mestre descreve o efeito.", "Jogador")
        dialog.start_next(); return
    # Em combate
    if not player_turn:
        dialog.push("Ainda não é sua vez!", "Sistema"); return
    roll, total = roll_d20()
    hit = (roll + player.level) >= 8
    if hit:
        dmg = a.power + (player.level // 2)
        current_enemy.take_damage(dmg)
        combat_log.appendleft(f"Você usou {a.name} ({roll}) e causou {dmg} de dano.")
    else:
        combat_log.appendleft(f"Você usou {a.name} ({roll}) e errou.")
    if not current_enemy.alive:
        dialog.push(f"A {current_enemy.name} foi derrotada! Missão cumprida.", "Sistema")
        GAME_STATE["mode"] = "explore"
        quest_log.quests.append(Quest("Batalha", "Vitória contra inimigo.", "Combate", "EXP"))
        player.exp += 30
        dialog.push("Você recebeu 30 de EXP.", "Sistema")
    else:
        player_turn = False
        pygame.time.set_timer(pygame.USEREVENT + 1, 900)

# -------------------------
# BOTÕES e UI iniciais
# -------------------------
buttons = []

def accept_mission():
    # exemplo: aceita missão padrão da primeira área
    q = area_quests.get("Floresta Sombria")
    if q and q.title not in [x.title for x in quest_log.get_active()]:
        quest_log.add(q)
    dialog.push("Você aceitou. O Mestre narra sua jornada até o covil da criatura.", "Sistema")
    enemy = Enemy("Fera do Pântano", hp=60, atk=10, desc="Uma criatura de lodo e fúria.")
    start_combat(enemy)

def decline_mission():
    dialog.push("Você recusou a missão. O Mestre observa em silêncio.", "Sistema")

btn_accept = Button((SCREEN_W//2 - 220, SCREEN_H - 230, 200, 44), "Aceitar Missão", accept_mission)
btn_decline = Button((SCREEN_W//2 + 20, SCREEN_H - 230, 200, 44), "Recusar Missão", decline_mission)
buttons += [btn_accept, btn_decline]

ability_buttons = []
btn_w, btn_h, pad = 96, 96, 12
start_x, start_y = SCREEN_W - (96 + 20), SCREEN_H - (96 + 20) - 60
for i, a in enumerate(player.abilities):
    rect = (start_x - i*(btn_w + pad), start_y, btn_w, btn_h)
    def make_cb(i0): return lambda: player_use_ability(i0)
    b = Button(rect, "", make_cb(i))
    ability_buttons.append(b)
    buttons.append(b)

def on_roll():
    result = roll_dice(20)
    dice_anim.start(result)

roll_btn = Button((SCREEN_W - 140, 20, 120, 36), "Rolar d20", on_roll)
buttons.append(roll_btn)

buttons.append(Button((SCREEN_W - 140, 62, 120, 36), "Missões", show_quest_log))
buttons.append(Button((SCREEN_W - 140, 104, 120, 36), "Usar Poção", lambda: use_potion() if True else None))

def use_potion():
    if player.inventory.get("Poção de Vida",0) > 0:
        player.inventory["Poção de Vida"] -= 1
        player.hp = min(player.max_hp, player.hp + 35)
        dialog.push(f"Você bebe uma poção e recupera 35 HP.", "Jogador")
    else:
        dialog.push("Sem poções!", "Sistema")

# -------------------------
# DESENHO: UI helpers
# -------------------------
def draw_panel_background(surf, rect, color, border_color, shadow_color):
    pygame.draw.rect(surf, shadow_color, (rect.x+4, rect.y+4, rect.w, rect.h), border_radius=5)
    pygame.draw.rect(surf, color, rect, border_radius=5)
    pygame.draw.rect(surf, border_color, rect, 3, border_radius=5)

def draw_bar(surf, x, y, w, h, cur, mx, bar_color, text_prefix=""):
    draw_panel_background(surf, pygame.Rect(x,y,w,h), COLOR_WOOD_DARK, COLOR_BORDER, COLOR_SHADOW)
    frac = max(0.0, min(1.0, cur/mx)) if mx != 0 else 0
    fill_rect = pygame.Rect(x+3,y+3,int((w-6)*frac),h-6)
    pygame.draw.rect(surf, bar_color, fill_rect)
    txt_str = f"{text_prefix}{cur}/{mx}"
    txt = FONT.render(txt_str, True, COLOR_PARCHMENT)
    surf.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))

# -------------------------
# LOOP PRINCIPAL
# -------------------------
running = True
while running:
    dt = clock.tick(FPS)/1000.0
    mouse = pygame.mouse.get_pos()

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
            if dialog.visible:
                if dialog.char_index < len(dialog.text):
                    dialog.skip()
                else:
                    dialog.start_next()
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            # clique no diálogo
            if dialog.visible and dialog.rect.collidepoint(ev.pos):
                if dialog.char_index < len(dialog.text):
                    dialog.skip()
                else:
                    dialog.start_next()
            # clique em áreas do mapa
            if handle_map_click(ev.pos):
                pass
            # botões
            for b in buttons:
                b.handle_event(ev)
        elif ev.type == pygame.USEREVENT + 1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            if GAME_STATE["mode"] == "combat" and current_enemy and current_enemy.alive:
                enemy_action()

    # atualizações
    player.update(dt)
    dialog.update(dt)
    dice_anim.update(dt)
    for b in buttons:
        b.update(mouse)

    # desenho da cena
    screen.blit(map_img, (0,0))
    # desenha áreas e hover
    hovered = None
    for area in map_areas:
        if area.rect.collidepoint(mouse):
            hovered = area
        area.draw(screen, hover=(area == hovered))
    draw_tokens(screen)

    # Painel do personagem
    panel_rect = pygame.Rect(20, 20, 340, 240)
    draw_panel_background(screen, panel_rect, COLOR_WOOD_LIGHT, COLOR_BORDER, COLOR_SHADOW)
    portrait = player.portrait or load_image(None, (120,120))
    screen.blit(portrait, (panel_rect.x + 12, panel_rect.y + 12))
    pygame.draw.rect(screen, COLOR_BORDER, (panel_rect.x+10, panel_rect.y+10, 124, 124), 3)
    screen.blit(FONT_TITLE.render(player.name, True, COLOR_TEXT_DARK), (panel_rect.x + 145, panel_rect.y + 12))
    screen.blit(FONT.render(f"Nível: {player.level}   EXP: {player.exp}", True, COLOR_TEXT_DARK), (panel_rect.x + 145, panel_rect.y + 50))
    draw_bar(screen, panel_rect.x + 145, panel_rect.y + 78, 180, 28, player.hp, player.max_hp, COLOR_HP_RED, "HP: ")
    draw_bar(screen, panel_rect.x + 145, panel_rect.y + 112, 180, 24, player.mp, player.max_mp, COLOR_MP_BLUE, "MP: ")
    screen.blit(FONT_BIG.render("Inventário:", True, COLOR_TEXT_DARK), (panel_rect.x + 12, panel_rect.y + 145))
    inv_items = ", ".join([f"{k}x{v}" for k,v in player.inventory.items()]) or "Vazio"
    screen.blit(FONT.render(inv_items, True, COLOR_TEXT_DARK), (panel_rect.x + 12, panel_rect.y + 175))

    # Botões e ícones de habilidade
    for b in buttons:
        b.draw(screen)
    for i, b in enumerate(ability_buttons):
        a = player.abilities[i]
        if a.icon:
            screen.blit(a.icon, (b.rect.centerx - 28, b.rect.centery - 28))
        if not a.ready():
            s = pygame.Surface(b.rect.size, pygame.SRCALPHA)
            s.fill((0,0,0,180))
            cd_text = FONT_BIG.render(f"{int(a.remaining)+1}", True, COLOR_GOLD)
            s.blit(cd_text, (s.get_width()//2 - cd_text.get_width()//2, s.get_height()//2 - cd_text.get_height()//2))
            screen.blit(s, b.rect.topleft)

    # diálogo
    dialog.draw(screen)

    # painel inimigo (em combate)
    if GAME_STATE["mode"] == "combat" and current_enemy:
        e_panel_rect = pygame.Rect(SCREEN_W//2 - 180, 20, 360, 120)
        draw_panel_background(screen, e_panel_rect, COLOR_WOOD_LIGHT, COLOR_BORDER, COLOR_SHADOW)
        screen.blit(FONT_TITLE.render(current_enemy.name, True, COLOR_TEXT_DARK), (e_panel_rect.x + 15, e_panel_rect.y + 10))
        draw_bar(screen, e_panel_rect.x + 15, e_panel_rect.y + 50, 330, 32, current_enemy.hp, current_enemy.max_hp, COLOR_HP_RED)
        turn_txt_surf = FONT_BIG.render("Sua vez" if player_turn else f"Vez de {current_enemy.name}", True, COLOR_GOLD)
        screen.blit(turn_txt_surf, (e_panel_rect.centerx - turn_txt_surf.get_width()//2, e_panel_rect.bottom + 10))
        # log de combate
        log_bg_rect = pygame.Rect(0,0, 600, 150)
        log_bg_rect.midtop = (e_panel_rect.centerx, e_panel_rect.bottom + 50)
        log_surf = pygame.Surface(log_bg_rect.size, pygame.SRCALPHA)
        log_surf.fill((245, 222, 179, 150))
        pygame.draw.rect(log_surf, COLOR_WOOD_DARK, log_surf.get_rect(), 2, 4)
        for i, msg in enumerate(list(combat_log)):
            log_surf.blit(FONT.render(msg, True, COLOR_TEXT_DARK), (15, 10 + i*22))
        screen.blit(log_surf, log_bg_rect)

    # animação do dado (desenhada por cima)
    dice_anim.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
