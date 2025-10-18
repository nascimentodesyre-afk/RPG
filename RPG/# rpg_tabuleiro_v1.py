import pygame
import sys
import os
from collections import deque

pygame.init()
pygame.font.init()

# ---------------------------
# CONFIGURAÇÕES GERAIS
# ---------------------------
SCREEN_W, SCREEN_H = 1280, 720
FPS = 60
ASSETS_DIR = "assets"  # coloque suas imagens aqui: map.png, portrait.png, skill_fire.png etc.

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("RPG de Mesa - Versão Demo")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("dejavusans", 18)
FONT_BIG = pygame.font.SysFont("dejavusans", 24)

# ---------------------------
# UTILITÁRIOS PARA CARREGAR IMAGENS (com fallback)
# ---------------------------
def load_image(name, fallback_size=None):
    path = os.path.join(ASSETS_DIR, name)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert_alpha()
            return img
        except Exception as e:
            print("Erro ao carregar", path, e)
    # fallback: superfície colorida
    if fallback_size is None:
        fallback_size = (64, 64)
    surf = pygame.Surface(fallback_size, pygame.SRCALPHA)
    surf.fill((120, 120, 120, 255))
    pygame.draw.rect(surf, (180, 180, 180), surf.get_rect(), 3)
    return surf

# ---------------------------
# MAPA (fundo rolável)
# ---------------------------
MAP_W, MAP_H = 2400, 1800
map_img = load_image("map.png", fallback_size=(MAP_W, MAP_H))
# if fallback produced small image, expand
if map_img.get_size() != (MAP_W, MAP_H):
    big_map = pygame.Surface((MAP_W, MAP_H))
    big_map.fill((50, 100, 50))  # grama
    # desenha algumas "tiles" e objetos para parecer um tabuleiro
    for x in range(0, MAP_W, 200):
        for y in range(0, MAP_H, 200):
            rect = pygame.Rect(x+10, y+10, 180, 180)
            pygame.draw.rect(big_map, (60, 120, 60), rect, 1)
    # grandes elementos
    pygame.draw.rect(big_map, (120, 85, 15), (500, 400, 320, 200))  # casa
    pygame.draw.circle(big_map, (20, 40, 200), (1500, 1200), 160)  # lago
    map_img = big_map

# ---------------------------
# PERSONAGEM
# ---------------------------
class Ability:
    def __init__(self, name, desc, damage, cooldown, icon_name=None):
        self.name = name
        self.desc = desc
        self.damage = damage
        self.cooldown = cooldown  # segundos
        self.remaining = 0
        self.icon = load_image(icon_name, fallback_size=(64,64)) if icon_name else load_image(None, (64,64))

    def ready(self):
        return self.remaining <= 0

    def use(self):
        if self.ready():
            self.remaining = self.cooldown
            return True
        return False

    def tick(self, dt):
        if self.remaining > 0:
            self.remaining = max(0, self.remaining - dt)

class Character:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 48, 64)
        self.speed = 220  # pixels por segundo
        self.max_hp = 100
        self.hp = 100
        self.max_mp = 50
        self.mp = 50
        self.level = 1
        self.exp = 0
        self.name = "Sir/Aventureiro"
        # portrait
        self.portrait = load_image("portrait.png", fallback_size=(120,120))
        # habilidades
        self.abilities = [
            Ability("Golpe", "Ataque físico rápido.", damage=12, cooldown=1.2, icon_name="skill_sword.png"),
            Ability("Chama", "Magia de fogo com dano maior.", damage=28, cooldown=6.0, icon_name="skill_fire.png"),
            Ability("Cura", "Restaura parte da vida.", damage=-30, cooldown=8.0, icon_name="skill_heal.png"),
        ]

    def update(self, dt):
        for a in self.abilities:
            a.tick(dt)

player = Character(MAP_W//2, MAP_H//2)

# ---------------------------
# CÂMERA
# ---------------------------
camera_x, camera_y = 0, 0
def update_camera():
    global camera_x, camera_y
    camera_x = int(player.rect.centerx - SCREEN_W//2)
    camera_y = int(player.rect.centery - SCREEN_H//2)
    camera_x = max(0, min(MAP_W - SCREEN_W, camera_x))
    camera_y = max(0, min(MAP_H - SCREEN_H, camera_y))

# ---------------------------
# UI: Caixa de diálogo do Mestre (fila de missões/linhas)
# ---------------------------
class DialogueBox:
    def __init__(self, width, height, x, y):
        self.rect = pygame.Rect(x, y, width, height)
        self.lines = deque()
        self.visible = False
        self.current_text = ""
        self.char_index = 0
        self.timer = 0.0
        self.speed = 0.01  # segundos por caractere
        self.speaker = "Mestre"

    def push(self, text, speaker="Mestre"):
        # quebrou em linhas simples para o demo
        self.lines.append((text, speaker))

    def start_next(self):
        if self.lines:
            self.current_text, self.speaker = self.lines.popleft()
            self.char_index = 0
            self.timer = 0.0
            self.visible = True
        else:
            self.visible = False
            self.current_text = ""
            self.speaker = ""

    def skip(self):
        # mostra tudo
        self.char_index = len(self.current_text)

    def update(self, dt):
        if not self.visible and self.lines:
            self.start_next()
        if self.visible and self.char_index < len(self.current_text):
            self.timer += dt
            while self.timer >= self.speed and self.char_index < len(self.current_text):
                self.char_index += 1
                self.timer -= self.speed

    def draw(self, surf):
        if not self.visible:
            return
        # fundo semitransparente
        s = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        s.fill((10, 10, 10, 200))
        # borda
        pygame.draw.rect(s, (200,200,200), s.get_rect(), 2)
        surf.blit(s, (self.rect.x, self.rect.y))
        # nome do falante
        name_txt = FONT_BIG.render(self.speaker, True, (255, 230, 150))
        surf.blit(name_txt, (self.rect.x + 12, self.rect.y + 8))
        # texto (aparecendo por caractere)
        text_to_show = self.current_text[:self.char_index]
        lines = wrap_text(text_to_show, self.rect.w - 24, FONT)
        for i, line in enumerate(lines[:4]):  # limitar linhas na caixa
            txt = FONT.render(line, True, (230,230,230))
            surf.blit(txt, (self.rect.x + 12, self.rect.y + 40 + i*22))
        # "Next" hint
        next_hint = FONT.render("(Clique em Avançar)", True, (200,200,200))
        surf.blit(next_hint, (self.rect.right - 160, self.rect.bottom - 28))

def wrap_text(text, max_width, font):
    # simples quebra de texto por palavras
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

dialog = DialogueBox(width=SCREEN_W - 40, height=140, x=20, y=SCREEN_H - 160)
# Preencha com algumas missões/textos do mestre
dialog.push("Bem-vindo, aventureiro. Nossa vila precisa de ajuda. Procure pelo lago ao leste e derrote a besta que assombra a noite.")
dialog.push("Missão: 'Besta do Lago' - Vá até o ponto marcado e use suas habilidades sabiamente.")
dialog.push("Dica: A habilidade Chama é forte contra essa criatura, mas tem cooldown alto. Use Golpe para dano rápido.")

# ---------------------------
# BOTÕES DE HABILIDADE (interativos)
# ---------------------------
class Button:
    def __init__(self, rect, text="", icon=None, callback=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.icon = icon
        self.callback = callback
        self.hover = False
        self.active = True

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                if self.callback:
                    self.callback()

    def draw(self, surf):
        color = (40, 40, 40) if not self.hover else (60, 60, 60)
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, (180,180,180), self.rect, 2)
        if self.icon:
            ic = pygame.transform.scale(self.icon, (self.rect.w-8, self.rect.h-28))
            surf.blit(ic, (self.rect.x+4, self.rect.y+4))
        txt = FONT.render(self.text, True, (220,220,220))
        surf.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.bottom - 20))

    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

# cria botões de habilidade automaticamente a partir das abilities do jogador
ability_buttons = []
btn_w, btn_h = 96, 96
padding = 12
start_x = SCREEN_W - (btn_w + padding) - 20
start_y = SCREEN_H - (btn_h + padding) - 180

def make_ability_callback(idx):
    def cb():
        a = player.abilities[idx]
        if a.use():
            # aplica efeito simples: se dano >0, diminui vida de "alvo de demo"; se negativo cura
            if a.damage > 0:
                print(f"Usou {a.name}, dano {a.damage}")
                # efeito demo: reduz HP do player (simulando retorno ou teste)
                player.hp = max(0, player.hp - 0)  # sem efeito no self por enquanto
            else:
                # cura
                player.hp = min(player.max_hp, player.hp - a.damage)  # note: damage negativo -> cura
            # poderia adicionar efeitos no mundo (inimigos) aqui
        else:
            print(f"Habilidade {a.name} em cooldown: {round(a.remaining,1)}s")
    return cb

for i, abil in enumerate(player.abilities):
    x = start_x - i*(btn_w + padding)
    y = start_y
    b = Button((x, y, btn_w, btn_h), text=abil.name, icon=abil.icon, callback=make_ability_callback(i))
    ability_buttons.append(b)

# ---------------------------
# PAINEL DE INFORMAÇÕES E BARRAS
# ---------------------------
def draw_hp_bar(surf, x, y, w, h, cur, maxv):
    # fundo
    pygame.draw.rect(surf, (60,60,60), (x,y,w,h))
    frac = max(0, min(1.0, cur / maxv))
    fill_w = int((w-4) * frac)
    pygame.draw.rect(surf, (180,50,50), (x+2, y+2, fill_w, h-4))
    pygame.draw.rect(surf, (200,200,200), (x,y,w,h), 2)
    txt = FONT.render(f"{cur}/{maxv}", True, (255,255,255))
    surf.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))

def draw_mp_bar(surf, x, y, w, h, cur, maxv):
    pygame.draw.rect(surf, (60,60,60), (x,y,w,h))
    frac = max(0, min(1.0, cur / maxv))
    fill_w = int((w-4) * frac)
    pygame.draw.rect(surf, (50,120,200), (x+2, y+2, fill_w, h-4))
    pygame.draw.rect(surf, (200,200,200), (x,y,w,h), 2)
    txt = FONT.render(f"{cur}/{maxv}", True, (255,255,255))
    surf.blit(txt, (x + w//2 - txt.get_width()//2, y + h//2 - txt.get_height()//2))

# ---------------------------
# SIMULAÇÃO DE "PONTO DE MISSÃO" no mapa
# ---------------------------
mission_point = pygame.Rect(1500, 1150, 40, 40)
mission_reached = False

# ---------------------------
# LÓGICA PRINCIPAL
# ---------------------------
running = True
dt = 0.0

while running:
    dt = clock.tick(FPS) / 1000.0  # segundos
    mouse_pos = pygame.mouse.get_pos()

    # eventos
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            if dialog.visible:
                # se clicar na caixa de diálogo - avança
                if dialog.rect.collidepoint(ev.pos):
                    # se texto ainda digitando -> skip, senão próxima frase
                    if dialog.char_index < len(dialog.current_text):
                        dialog.skip()
                    else:
                        dialog.start_next()
            # repassa aos botões
            for b in ability_buttons:
                b.handle_event(ev)
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_SPACE:
                # espaço mostra/avança diálogo manual
                if dialog.visible:
                    if dialog.char_index < len(dialog.current_text):
                        dialog.skip()
                    else:
                        dialog.start_next()

    # movimento (WASD + setas) - movimento com velocidade por segundo
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        dy -= 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        dy += 1
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        dx -= 1
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        dx += 1
    # normaliza
    if dx != 0 or dy != 0:
        import math
        n = math.hypot(dx, dy)
        dx /= n
        dy /= n
        player.rect.x += int(dx * player.speed * dt)
        player.rect.y += int(dy * player.speed * dt)
    # limites do mapa
    player.rect.x = max(0, min(MAP_W - player.rect.w, player.rect.x))
    player.rect.y = max(0, min(MAP_H - player.rect.h, player.rect.y))

    # atualiza câmera
    update_camera()

    # atualiza jogador (cooldowns)
    player.update(dt)

    # atualiza diálogo
    dialog.update(dt)

    # atualiza botões hover
    for b in ability_buttons:
        b.update(mouse_pos)

    # detecta chegada na missão
    if not mission_reached and player.rect.colliderect(mission_point):
        mission_reached = True
        dialog.push("Você chegou ao ponto da missão! Prepare-se para enfrentar a Besta do Lago.")
        dialog.push("A besta é poderosa; use Chama quando o tempo permitir e Cura se estiver fraco.")
        dialog.start_next()

    # ---------------------------
    # DESENHO
    # ---------------------------
    # mapa (com offset da câmera)
    screen.fill((0,0,0))
    screen.blit(map_img, (-camera_x, -camera_y))

    # desenha ponto de missão no mundo (transforma coords para tela)
    mp_rect_screen = mission_point.move(-camera_x, -camera_y)
    pygame.draw.rect(screen, (255, 200, 0), mp_rect_screen)
    pygame.draw.rect(screen, (200,120,0), mp_rect_screen, 2)

    # personagem (desenhado no mapa)
    player_on_screen = player.rect.move(-camera_x, -camera_y)
    pygame.draw.rect(screen, (180, 30, 30), player_on_screen)  # placeholder do sprite
    # desenho do "head" - opcional
    pygame.draw.ellipse(screen, (100, 20, 20), (player_on_screen.x+6, player_on_screen.y-8, 36, 28))

    # ---------------------------
    # PAINEL LATERAL (INFO do personagem)
    # ---------------------------
    panel_w = 300
    panel_h = 220
    panel_x = 20
    panel_y = 20
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    s_panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    s_panel.fill((10,10,10,190))
    pygame.draw.rect(s_panel, (200,200,200), s_panel.get_rect(), 2)
    # portrait
    portrait_scaled = pygame.transform.scale(player.portrait, (120,120))
    s_panel.blit(portrait_scaled, (10, 10))
    # barras
    draw_hp_bar(s_panel, 140, 20, 140, 24, player.hp, player.max_hp)
    draw_mp_bar(s_panel, 140, 52, 140, 20, player.mp, player.max_mp)
    # textos
    name_txt = FONT_BIG.render(player.name, True, (255,255,220))
    s_panel.blit(name_txt, (140, 80))
    lvl_txt = FONT.render(f"Nível: {player.level}   EXP: {player.exp}", True, (220,220,220))
    s_panel.blit(lvl_txt, (140, 110))
    # stats adicionais
    atk_txt = FONT.render(f"Força: 12   Defesa: 8   Vel: {int(player.speed)}", True, (220,220,220))
    s_panel.blit(atk_txt, (10, 140))
    instr_txt = FONT.render("Espaço: avançar diálogo", True, (200,200,200))
    s_panel.blit(instr_txt, (10, 170))

    screen.blit(s_panel, (panel_x, panel_y))

    # ---------------------------
    # HABILIDADES (botões)
    # ---------------------------
    for i, b in enumerate(ability_buttons):
        # desenha cooldown overlay
        b.draw(screen)
        abil = player.abilities[i]
        if abil.remaining > 0:
            # overlay semitransparente mostrando tempo
            overlay = pygame.Surface((b.rect.w, b.rect.h), pygame.SRCALPHA)
            frac = abil.remaining / max(abil.cooldown, 0.0001)
            # desenha uma barra de cooldown vertical
            hfilled = int(b.rect.h * (1 - frac))
            pygame.draw.rect(overlay, (0,0,0,160), (0,0,b.rect.w,b.rect.h))
            pygame.draw.rect(overlay, (0,0,0,0), (0,0,b.rect.w,b.rect.h))
            pygame.draw.rect(overlay, (80,80,80,180), (0,0,b.rect.w,hfilled))
            screen.blit(overlay, (b.rect.x, b.rect.y))
            # tempo restante
            ttxt = FONT.render(f"{round(abil.remaining,1)}s", True, (255,255,255))
            screen.blit(ttxt, (b.rect.centerx - ttxt.get_width()//2, b.rect.centery - ttxt.get_height()//2))

    # ---------------------------
    # CAIXA DE DIÁLOGO (MESTRE)
    # ---------------------------
    dialog.draw(screen)

    # ---------------------------
    # OVERLAY: Tooltip das habilidades ao passar o mouse
    # ---------------------------
    for i, b in enumerate(ability_buttons):
        if b.hover:
            abil = player.abilities[i]
            # tooltip box
            tw, th = 260, 100
            tx, ty = mouse_pos[0]+16, mouse_pos[1]+16
            tooltip = pygame.Surface((tw, th), pygame.SRCALPHA)
            tooltip.fill((20,20,20,230))
            pygame.draw.rect(tooltip, (200,200,200), tooltip.get_rect(), 1)
            title = FONT_BIG.render(abil.name, True, (255,235,180))
            tooltip.blit(title, (8,6))
            desc_lines = wrap_text(abil.desc, tw-16, FONT)
            for li, line in enumerate(desc_lines[:3]):
                tooltip.blit(FONT.render(line, True, (230,230,230)), (8, 34 + li*20))
            cdtxt = FONT.render(f"Cooldown: {abil.cooldown}s", True, (200,200,200))
            tooltip.blit(cdtxt, (8, th-28))
            screen.blit(tooltip, (tx, ty))

    # ---------------------------
    # HUD: Mini-instruções
    # ---------------------------
    hud = FONT.render("WASD / Setas: mover  •  Clique nas habilidades para usar", True, (220,220,220))
    screen.blit(hud, (20, SCREEN_H - 28))

    pygame.display.flip()

pygame.quit()
sys.exit()

