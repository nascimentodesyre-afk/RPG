# rpg_tabletop_enhanced.py
# Requisitos: pip install pygame

import pygame
import sys
import os
import random
import math
from collections import deque
from enum import Enum

pygame.init()
pygame.font.init()
pygame.mixer.init()

# ==================== CONFIGURAÇÕES ====================
SCREEN_W, SCREEN_H = 1200, 800
FPS = 60

# Caminhos absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
FONT_DIR = os.path.join(BASE_DIR, "font")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")

# ==================== PALETA DE CORES PREMIUM ====================
COLOR_DEEP_WOOD = (30, 20, 10)
COLOR_RICH_WOOD = (101, 67, 33)
COLOR_GOLDEN_PARCHMENT = (252, 240, 200)
COLOR_AGED_PARCHMENT = (222, 207, 172)
COLOR_DARK_TEXT = (40, 30, 20)
COLOR_BRIGHT_GOLD = (255, 215, 0)
COLOR_WARM_GOLD = (255, 190, 30)
COLOR_DEEP_RED = (170, 30, 30)
COLOR_RICH_RED = (200, 50, 50)
COLOR_MYSTIC_BLUE = (50, 100, 180)
COLOR_DEEP_BLUE = (30, 70, 150)
COLOR_SHADOW = (15, 8, 3)
COLOR_HIGHLIGHT = (255, 255, 200)
COLOR_DARK_BORDER = (15, 10, 5)

# Gradientes para efeitos visuais - CORRIGIDO
def create_gradient(width, height, start_color, end_color):
    gradient = pygame.Surface((width, height))
    for y in range(height):
        ratio = y / height
        # Garantir que as cores não fiquem negativas
        r = max(0, min(255, int(start_color[0] + (end_color[0] - start_color[0]) * ratio)))
        g = max(0, min(255, int(start_color[1] + (end_color[1] - start_color[1]) * ratio)))
        b = max(0, min(255, int(start_color[2] + (end_color[2] - start_color[2]) * ratio)))
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    return gradient

# ==================== INICIALIZAÇÃO ====================
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("RPG de Mesa — O Conclave de Eldoria: Renascimento das Eras")
clock = pygame.time.Clock()

# ==================== SISTEMA DE PARTÍCULAS ====================
class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particles(self, x, y, color, count=5, speed=2, size=3, lifetime=1.0):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            self.particles.append({
                'pos': [x, y],
                'vel': velocity,
                'color': color,
                'size': random.uniform(size * 0.5, size * 1.5),
                'lifetime': lifetime,
                'max_lifetime': lifetime
            })
    
    def update(self, dt):
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['lifetime'] -= dt
            particle['vel'][1] += 0.1  # gravidade
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surf):
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            if alpha > 0:
                color = particle['color']
                size = int(particle['size'] * (particle['lifetime'] / particle['max_lifetime']))
                if size > 0:
                    # Criar surface com alpha para partículas
                    particle_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                    pygame.draw.circle(particle_surf, (*color, alpha), (size, size), size)
                    surf.blit(particle_surf, (int(particle['pos'][0])-size, int(particle['pos'][1])-size))

particle_system = ParticleSystem()

# ==================== ENUMS ====================
class StatusMissao(Enum):
    DISPONIVEL = "Disponível"
    EM_ANDAMENTO = "Em Andamento"
    CONCLUIDA = "Concluída"
    FALHOU = "Falhou"

class TipoPocao(Enum):
    CURA = "Cura"
    VENENO = "Veneno"
    FORCA = "Força"
    MANA = "Mana"

class TipoInimigo(Enum):
    HUMANOIDE = "Humanoide"
    BESTA = "Besta"
    ESPECTRO = "Espectro"
    DRAGAO = "Dragão"
    DEMONIO = "Demônio"

# ==================== SISTEMA DE IMAGENS SIMPLIFICADO ====================
def create_placeholder_icon(size, color, text=""):
    """Cria ícones placeholder quando as imagens não são encontradas"""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    pygame.draw.rect(surf, color, (0, 0, size[0], size[1]), border_radius=8)
    pygame.draw.rect(surf, COLOR_BRIGHT_GOLD, (0, 0, size[0], size[1]), 2, border_radius=8)
    
    if text:
        font = pygame.font.SysFont("arial", size[1]//3)
        text_surf = font.render(text, True, COLOR_GOLDEN_PARCHMENT)
        surf.blit(text_surf, (size[0]//2 - text_surf.get_width()//2, size[1]//2 - text_surf.get_height()//2))
    
    return surf

def load_image_safe(name, size=None, placeholder_text=""):
    """Carrega imagens com fallback para placeholders"""
    if not name:
        return create_placeholder_icon(size or (64, 64), COLOR_DEEP_WOOD, placeholder_text)

    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        print(f"[AVISO] Imagem não encontrada: {path}, usando placeholder")
        return create_placeholder_icon(size or (64, 64), COLOR_DEEP_WOOD, placeholder_text)

    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except Exception as e:
        print(f"[ERRO] Falha ao carregar imagem '{path}': {e}")
        return create_placeholder_icon(size or (64, 64), COLOR_DEEP_WOOD, placeholder_text)

# ==================== SISTEMA DE FONTES ====================
def load_themed_font(font_name, size):
    font_path = os.path.join(FONT_DIR, font_name)
    if os.path.exists(font_path):
        try:
            return pygame.font.Font(font_path, size)
        except Exception as e:
            print(f"[ERRO] Fonte {font_name} não pôde ser carregada: {e}")
    return pygame.font.SysFont("georgia", size)

# Sistema de fontes hierárquico
FONT_TINY = load_themed_font("MorrisRoman-Black.ttf", 14)
FONT_SMALL = load_themed_font("MorrisRoman-Black.ttf", 18)
FONT_NORMAL = load_themed_font("MorrisRoman-Black.ttf", 22)
FONT_MEDIUM = load_themed_font("MorrisRoman-Black.ttf", 26)
FONT_LARGE = load_themed_font("MorrisRoman-Black.ttf", 32)
FONT_TITLE = load_themed_font("MorrisRoman-Black.ttf", 42)
FONT_HEADER = load_themed_font("MorrisRoman-Black.ttf", 56)

# ==================== SISTEMA DE HABILIDADES ====================
class Ability:
    def __init__(self, name, desc, power, cooldown, cost_mp=0, tipo="Físico", alcance=1, icon_name=None):
        self.name = name
        self.desc = desc
        self.power = power
        self.cooldown = cooldown
        self.remaining = 0.0
        self.cost_mp = cost_mp
        self.alcance = alcance
        self.tipo = tipo
        # Usar sistema seguro de carregamento de imagens
        self.icon = load_image_safe(icon_name, (64, 64), name[:3])
        self.flash_timer = 0.0
        
    def ready(self): 
        return self.remaining <= 0.0
        
    def use(self):
        if self.ready(): 
            self.remaining = self.cooldown
            self.flash_timer = 0.3
            return True
        return False
        
    def tick(self, dt):
        if self.remaining > 0: 
            self.remaining = max(0.0, self.remaining - dt)
        if self.flash_timer > 0:
            self.flash_timer = max(0.0, self.flash_timer - dt)

# ==================== PERSONAGEM DO JOGADOR ====================
class PlayerCharacter:
    def __init__(self, name="Sir Alaric", classe="Guerreiro", level=1, max_hp=120, max_mp=40, forca=18):
        self.name = name
        self.classe = classe
        self.level = level
        self.max_hp = max_hp
        self.hp = max_hp
        self.max_mp = max_mp
        self.mp = max_mp
        self.forca = forca
        self.ponto_fraco = "Magia"
        
        # Criar retrato placeholder baseado na classe
        if classe == "Guerreiro":
            self.color_scheme = COLOR_RICH_RED
            self.portrait = create_placeholder_icon((140, 140), COLOR_RICH_RED, "⚔️")
        elif classe == "Mago":
            self.color_scheme = COLOR_MYSTIC_BLUE
            self.portrait = create_placeholder_icon((140, 140), COLOR_MYSTIC_BLUE, "🔮")
        else:
            self.color_scheme = COLOR_WARM_GOLD
            self.portrait = create_placeholder_icon((140, 140), COLOR_WARM_GOLD, "🧝")
            
        self.abilities = self._load_abilities()
        self.inventory = {
            "Poção de Vida": 3,
            "Poção de Mana": 2,
            "Elixir de Força": 1
        }
        self.exp = 0
        self.exp_to_next = 100
        self.alive = True
        self.damage_flash = 0.0
        
    def _load_abilities(self):
        if self.classe == "Guerreiro":
            return [
                Ability("Corte Certeiro", "Golpe preciso que ignora parte da defesa", 15, 2.0, 0, "Físico", 1, "skill_sword.png"),
                Ability("Investida Heróica", "Avanço rápido com dano aumentado", 12, 4.0, 5, "Físico", 3, "skill_charge.png"),
                Ability("Barreira Impenetrável", "Dobra a defesa por 2 turnos", 0, 8.0, 10, "Defesa", 0, "skill_shield.png"),
                Ability("Fúria do Guerreiro", "Ataque em área com chance de atordoar", 25, 6.0, 15, "Físico", 2, "skill_rage.png")
            ]
        elif self.classe == "Mago":
            return [
                Ability("Bola de Fogo Arcana", "Esfera de fogo que queima múltiplos alvos", 22, 3.0, 12, "Magia", 4, "skill_fireball.png"),
                Ability("Lâmina de Gelo", "Lâminas afiadas de gelo perfuram defesas", 18, 2.5, 8, "Magia", 3, "skill_ice.png"),
                Ability("Cura Celestial", "Restauração poderosa com bônus temporário", -35, 5.0, 15, "Cura", 2, "skill_heal.png"),
                Ability("Névoa Arcana", "Reduz precisão inimiga e aumenta defesa mágica", 0, 6.0, 10, "Suporte", 3, "skill_mist.png")
            ]
        else:
            return [
                Ability("Golpe Rápido", "Ataque veloz com alta precisão", 12, 1.0, 0, "Físico", 1, "skill_quick.png"),
                Ability("Esquiva Tática", "Aumenta evasão e contra-ataque", 0, 4.0, 3, "Defesa", 0, "skill_dodge.png")
            ]
    
    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.damage_flash = 0.5
        if self.hp <= 0:
            self.alive = False
            
    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_next
        self.exp_to_next = int(self.exp_to_next * 1.5)
        self.max_hp += 20
        self.hp = self.max_hp
        self.max_mp += 10
        self.mp = self.max_mp
        self.forca += 2
        
        dialog.push(f"⭐ {self.name} alcançou o nível {self.level}!", "Sistema")
        dialog.push("Pontos de vida e mana aumentados! Força melhorada!", "Sistema")
    
    def update(self, dt):
        for a in self.abilities: 
            a.tick(dt)
        if self.damage_flash > 0:
            self.damage_flash = max(0.0, self.damage_flash - dt)

# ==================== INIMIGO ====================
class GameEnemy:
    def __init__(self, name, max_hp, atk, tipo, fraqueza, color_scheme=None, desc=""):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.atk = atk
        self.tipo = tipo
        self.fraqueza = fraqueza
        self.desc = desc
        self.alive = True
        self.damage_flash = 0.0
        self.color_scheme = color_scheme or COLOR_DEEP_WOOD
        # Criar retrato placeholder para inimigo
        self.portrait = create_placeholder_icon((80, 80), self.color_scheme, "👹")
            
    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)
        self.damage_flash = 0.3
        particle_system.add_particles(
            SCREEN_W//2, 150, 
            self.color_scheme, 
            count=8, speed=3, size=4
        )
        if self.hp <= 0: 
            self.alive = False
            
    def update(self, dt):
        if self.damage_flash > 0:
            self.damage_flash = max(0.0, self.damage_flash - dt)

# ==================== DADOS DE EXEMPLO ====================
# Criar instância do jogador
player = PlayerCharacter("Sir Alaric de Eldoria", "Guerreiro", 1, 120, 40, 18)

# Inimigos para a comunidade
inimigos_comunidade = [
    GameEnemy("Líder dos Assaltantes", 60, 12, "Humanoide", "Luz", COLOR_RICH_RED, "Chefe dos bandidos da região"),
    GameEnemy("Espião do Conselho", 45, 10, "Humanoide", "Verdade", COLOR_MYSTIC_BLUE, "Infiltrado nas altas esferas"),
    GameEnemy("Guarda Corrompido", 55, 14, "Humanoide", "Honra", COLOR_DEEP_RED, "Ex-membro da guarda real")
]

# ==================== SISTEMA DE DIÁLOGO ====================
class DialogueBox:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.queue = deque()
        self.visible, self.text, self.speaker = True, "", "Mestre do Conclave"
        self.char_index, self.timer, self.speed = 0, 0.0, 0.03
        self.portrait = None
        self.shake_timer = 0.0
        
    def push(self, text, speaker="Mestre do Conclave", portrait=None, shake=False):
        self.queue.append((text, speaker, portrait))
        if shake:
            self.shake_timer = 0.5
            
    def start_next(self):
        if self.queue:
            self.text, self.speaker, self.portrait = self.queue.popleft()
            self.char_index, self.timer, self.visible = 0, 0.0, True
        else:
            self.visible, self.text, self.speaker = False, "", ""
            
    def skip(self): 
        self.char_index = len(self.text)
        
    def update(self, dt):
        if not self.visible and self.queue: 
            self.start_next()
        if self.visible and self.char_index < len(self.text):
            self.timer += dt
            while self.timer >= self.speed and self.char_index < len(self.text):
                self.char_index += 1
                self.timer -= self.speed
        if self.shake_timer > 0:
            self.shake_timer = max(0.0, self.shake_timer - dt)
                
    def draw(self, surf):
        if not self.visible: 
            return
            
        # Efeito de shake
        offset_x = 0
        offset_y = 0
        if self.shake_timer > 0:
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-2, 2)
            
        rect = self.rect.move(offset_x, offset_y)
        
        # Fundo com gradiente e borda ornamentada
        pygame.draw.rect(surf, COLOR_DEEP_WOOD, rect.inflate(8, 8), border_radius=12)
        pygame.draw.rect(surf, COLOR_RICH_WOOD, rect, border_radius=10)
        
        # Gradiente interno
        inner_rect = rect.inflate(-8, -8)
        gradient = create_gradient(inner_rect.width, inner_rect.height, COLOR_AGED_PARCHMENT, COLOR_GOLDEN_PARCHMENT)
        surf.blit(gradient, inner_rect.topleft)
        
        # Borda dourada
        pygame.draw.rect(surf, COLOR_BRIGHT_GOLD, rect, 3, border_radius=10)
        
        # Retrato do speaker
        if self.portrait:
            portrait_rect = pygame.Rect(rect.x + 20, rect.y + 20, 80, 80)
            pygame.draw.rect(surf, COLOR_DEEP_WOOD, portrait_rect.inflate(8, 8), border_radius=8)
            pygame.draw.rect(surf, COLOR_BRIGHT_GOLD, portrait_rect.inflate(8, 8), 2, border_radius=8)
            surf.blit(self.portrait, portrait_rect.topleft)
            text_x = portrait_rect.right + 20
        else:
            text_x = rect.x + 20
            
        # Nome do speaker
        name_bg = pygame.Rect(text_x - 10, rect.y + 10, 400, 35)
        pygame.draw.rect(surf, COLOR_DEEP_WOOD, name_bg, border_radius=6)
        pygame.draw.rect(surf, COLOR_BRIGHT_GOLD, name_bg, 2, border_radius=6)
        
        name_txt = FONT_MEDIUM.render(self.speaker, True, COLOR_BRIGHT_GOLD)
        surf.blit(name_txt, (text_x, rect.y + 15))
        
        # Texto do diálogo
        text_to_show = self.text[:self.char_index]
        lines = wrap_text(text_to_show, rect.w - (text_x - rect.x) - 20, FONT_NORMAL)
        
        for i, line in enumerate(lines[:4]):
            y_pos = rect.y + 60 + i * 28
            text_surf = FONT_NORMAL.render(line, True, COLOR_DARK_TEXT)
            surf.blit(text_surf, (text_x, y_pos))
            
        # Indicador de continuação
        if self.char_index >= len(self.text) and self.queue:
            indicator_y = rect.bottom - 35
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.5 + 0.5
            alpha = int(150 + 105 * pulse)
            hint_color = (*COLOR_DARK_TEXT, alpha)
            hint_surf = FONT_SMALL.render("▼ Clique para continuar ▼", True, hint_color)
            # Criar surface com alpha para o hint
            hint_final = pygame.Surface(hint_surf.get_size(), pygame.SRCALPHA)
            hint_final.blit(hint_surf, (0, 0))
            surf.blit(hint_final, (rect.centerx - hint_surf.get_width()//2, indicator_y))

def wrap_text(text, max_width, font):
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines

# ==================== BOTÕES PREMIUM ====================
class Button:
    def __init__(self, rect, label, callback=None, icon=None, tooltip=""):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback
        self.icon = load_image_safe(icon, (32, 32), label[:1])
        self.tooltip = tooltip
        self.hover = False
        self.click_anim = 0.0
        self.pulse = 0.0
        
    def handle_event(self, ev):
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and self.rect.collidepoint(ev.pos):
            self.click_anim = 0.2
            if self.callback: 
                self.callback()
                return True
        return False
        
    def update(self, mouse_pos, dt): 
        self.hover = self.rect.collidepoint(mouse_pos)
        if self.click_anim > 0:
            self.click_anim = max(0.0, self.click_anim - dt)
        if self.hover:
            self.pulse = (self.pulse + dt * 6) % (2 * math.pi)
        
    def draw(self, surf):
        # Efeito de click
        click_offset = int(self.click_anim * 5)
        draw_rect = self.rect.move(0, click_offset)
        
        # Sombra
        shadow_rect = draw_rect.move(3, 3)
        pygame.draw.rect(surf, COLOR_SHADOW, shadow_rect, border_radius=8)
        
        # Gradiente do botão
        if self.hover:
            base_color = COLOR_RICH_WOOD
            border_color = COLOR_BRIGHT_GOLD
            # Efeito de pulsação no hover
            pulse_alpha = int(50 + 30 * math.sin(self.pulse))
            highlight = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            highlight.fill((255, 255, 200, pulse_alpha))
            surf.blit(highlight, draw_rect.topleft)
        else:
            base_color = COLOR_DEEP_WOOD
            border_color = COLOR_WARM_GOLD
            
        pygame.draw.rect(surf, base_color, draw_rect, border_radius=6)
        pygame.draw.rect(surf, border_color, draw_rect, 2, border_radius=6)
        
        # Ícone e texto
        if self.icon:
            icon_rect = self.icon.get_rect(center=(draw_rect.centerx, draw_rect.centery - 8))
            surf.blit(self.icon, icon_rect)
            
        text_color = COLOR_GOLDEN_PARCHMENT if self.hover else COLOR_AGED_PARCHMENT
        label_surf = FONT_SMALL.render(self.label, True, text_color)
        text_y = draw_rect.centery + (15 if self.icon else 0)
        surf.blit(label_surf, (draw_rect.centerx - label_surf.get_width()//2, text_y - label_surf.get_height()//2))
        
        # Tooltip no hover
        if self.hover and self.tooltip:
            tooltip_rect = pygame.Rect(self.rect.x, self.rect.y - 40, 200, 30)
            pygame.draw.rect(surf, COLOR_DEEP_WOOD, tooltip_rect, border_radius=4)
            pygame.draw.rect(surf, COLOR_BRIGHT_GOLD, tooltip_rect, 1, border_radius=4)
            tooltip_text = FONT_TINY.render(self.tooltip, True, COLOR_GOLDEN_PARCHMENT)
            surf.blit(tooltip_text, (tooltip_rect.centerx - tooltip_text.get_width()//2, 
                                   tooltip_rect.centery - tooltip_text.get_height()//2))

# ==================== ÁREAS DO MAPA ====================
class MapArea:
    def __init__(self, name, rect, description, icon=None):
        self.name = name
        self.rect = pygame.Rect(rect)
        self.description = description
        self.icon = load_image_safe(icon, (48, 48), "📍")
        self.hover_anim = 0.0
        self.discovered = True
        
    def update(self, mouse_pos, dt):
        was_hovered = self.rect.collidepoint(mouse_pos)
        if was_hovered:
            self.hover_anim = min(1.0, self.hover_anim + dt * 3)
        else:
            self.hover_anim = max(0.0, self.hover_anim - dt * 2)
        
    def draw(self, surf, mouse_pos):
        hover = self.rect.collidepoint(mouse_pos)
        
        # Sombra
        shadow_rect = self.rect.move(4, 4)
        pygame.draw.rect(surf, COLOR_SHADOW, shadow_rect, border_radius=12)
        
        # Fundo com gradiente
        base_color = COLOR_RICH_WOOD
        border_color = COLOR_WARM_GOLD
            
        pygame.draw.rect(surf, base_color, self.rect, border_radius=10)
        
        # Efeito de hover
        if hover:
            highlight = pygame.Surface(self.rect.size, pygame.SRCALPHA)
            highlight_alpha = int(80 * self.hover_anim)
            highlight.fill((255, 255, 200, highlight_alpha))
            surf.blit(highlight, self.rect.topleft)
            
        # Borda
        border_width = 3
        pygame.draw.rect(surf, border_color, self.rect, border_width, border_radius=10)
        
        # Ícone
        if self.icon:
            icon_rect = self.icon.get_rect(center=(self.rect.centerx, self.rect.centery - 15))
            surf.blit(self.icon, icon_rect)
        
        # Nome
        text_color = COLOR_BRIGHT_GOLD if hover else COLOR_WARM_GOLD
        name_font = FONT_MEDIUM if hover else FONT_NORMAL
            
        name_surf = name_font.render(self.name, True, text_color)
        name_y = self.rect.centery + (25 if self.icon else 0)
        surf.blit(name_surf, (self.rect.centerx - name_surf.get_width()//2, name_y - name_surf.get_height()//2))

# Configuração do mapa - APENAS COMUNIDADE
map_areas = [
    MapArea("Vila de Eldoria", (SCREEN_W//2 - 150, SCREEN_H//2 - 100, 300, 200), 
            "Uma vila próspera com comércio animado e pessoas amigáveis.", "imagens/Scene Overview.png"),
]

# ==================== SISTEMA DE MISSÕES ====================
class Quest:
    def __init__(self, title, description, location_name, reward, story_hook=""):
        self.title = title
        self.description = description
        self.location = location_name
        self.reward = reward
        self.story_hook = story_hook
        self.completed = False
        self.steps_completed = 0
        self.total_steps = random.randint(2, 4)
        
    def complete_step(self):
        self.steps_completed += 1
        if self.steps_completed >= self.total_steps:
            self.completed = True
            return self.reward
        return None
        
    def get_progress(self):
        return f"{self.steps_completed}/{self.total_steps}"

class QuestLog:
    def __init__(self):
        self.quests = []
        self.active_quest = None
        
    def add(self, quest):
        self.quests.append(quest)
        if not self.active_quest:
            self.active_quest = quest
        dialog.push(f"📜 Nova Missão: {quest.title}", "Diário de Aventuras")
        dialog.push(quest.story_hook, "Diário de Aventuras")
        particle_system.add_particles(SCREEN_W//2, SCREEN_H//2, COLOR_BRIGHT_GOLD, count=20, speed=2)
        
    def complete_step(self, quest_title):
        for q in self.quests:
            if q.title == quest_title and not q.completed:
                reward = q.complete_step()
                if reward:
                    dialog.push(f"🎉 Missão Concluída: {q.title}!", "Sistema")
                    dialog.push(f"Recompensa: {reward}", "Sistema")
                    particle_system.add_particles(SCREEN_W//2, SCREEN_H//2, COLOR_BRIGHT_GOLD, count=30, speed=3)
                    # Ativar próxima missão se houver
                    next_quests = [quest for quest in self.quests if not quest.completed]
                    self.active_quest = next_quests[0] if next_quests else None
                else:
                    dialog.push(f"⚡ Progresso em {q.title}: {q.get_progress()}", "Sistema")
                return True
        return False
    
    def get_active(self):
        return [q for q in self.quests if not q.completed]
    
    def get_completed(self):
        return [q for q in self.quests if q.completed]

quest_log = QuestLog()

# Missões para a comunidade
area_quests = {
    "Vila de Eldoria": Quest(
        "Proteger a Vila", 
        "Derrote os bandidos que ameaçam a paz da vila",
        "Vila de Eldoria",
        "100 moedas de ouro e reputação",
        "Bandidos têm aterrorizado os comerciantes. A vila precisa de um herói para restaurar a paz."
    ),
}

# ==================== FUNÇÕES DE USO GERAL ====================
def show_quest_log():
    active = quest_log.get_active()
    completed = quest_log.get_completed()
    
    if not active and not completed:
        dialog.push("Seu diário de aventuras está vazio. Aceite missões para preenchê-lo!", "Diário de Aventuras")
        return
        
    if active:
        dialog.push("📜 MISSÕES ATIVAS:", "Diário de Aventuras")
        for q in active:
            dialog.push(f"• {q.title} [{q.get_progress()}]", "Diário de Aventuras")
            dialog.push(f"  {q.description}", "Diário de Aventuras")
            
    if completed:
        dialog.push("✅ MISSÕES CONCLUÍDAS:", "Diário de Aventuras")
        for q in completed:
            dialog.push(f"• {q.title} - Recompensa: {q.reward}", "Diário de Aventuras")

def use_potion(potion_type):
    if player.inventory.get(potion_type, 0) > 0:
        player.inventory[potion_type] -= 1
        if potion_type == "Poção de Vida":
            player.hp = min(player.max_hp, player.hp + 35)
            dialog.push(f"❤️ {potion_type} restaura 35 de vida!", player.name)
            particle_system.add_particles(SCREEN_W//4, SCREEN_H//2, COLOR_RICH_RED, count=12, speed=2)
        elif potion_type == "Poção de Mana":
            player.mp = min(player.max_mp, player.mp + 25)
            dialog.push(f"💧 {potion_type} restaura 25 de mana!", player.name)
            particle_system.add_particles(SCREEN_W//4, SCREEN_H//2, COLOR_MYSTIC_BLUE, count=12, speed=2)
    else:
        dialog.push(f"❌ Sem {potion_type} no inventário!", "Sistema")

def on_roll():
    result = roll_dice(20)
    dice_anim.start(result)

def accept_mission():
    quest = area_quests.get("Vila de Eldoria")
    if quest and quest.title not in [x.title for x in quest_log.quests]:
        quest_log.add(quest)
    dialog.push("Você aceita o chamado do destino. Que sua lâmina seja rápida e seu coração, corajoso.", "Mestre do Conclave")
    # Escolher inimigo aleatório da comunidade
    enemy = random.choice(inimigos_comunidade)
    start_combat(enemy)

def decline_mission():
    dialog.push("O destino aguarda, mas cada herói escolhe seu próprio caminho. Talvez outra hora...", "Mestre do Conclave")

# ==================== ANIMAÇÃO DE DADOS ====================
class DiceAnimation:
    def __init__(self, x, y, size=140):
        self.rect = pygame.Rect(x, y, size, size)
        self.rolling = False
        self.timer = 0.0
        self.duration = 1.5
        self.result = None
        self.current_value = 1
        self.font = FONT_HEADER
        self.spin_speed = 0.0
        self.particles_emitted = False
        
    def start(self, result, callback=None):
        self.rolling = True
        self.timer = 0.0
        self.result = result
        self.current_value = random.randint(1, 20)
        self.spin_speed = 30.0
        self.particles_emitted = False
        self.callback = callback

    def update(self, dt):
        if not self.rolling:
            return
            
        self.timer += dt
        self.spin_speed = max(5.0, self.spin_speed - dt * 20)
        
        # Rotação durante a animação
        if self.timer < self.duration:
            self.current_value = random.randint(1, 20)
            
            # Emitir partículas no meio da rolagem
            if self.timer > self.duration * 0.7 and not self.particles_emitted:
                particle_system.add_particles(
                    self.rect.centerx, self.rect.centery,
                    COLOR_BRIGHT_GOLD, count=15, speed=4, size=5
                )
                self.particles_emitted = True
        else:
            self.current_value = self.result
            self.rolling = False
            
            # Efeito final baseado no resultado
            if self.result == 20:
                particle_system.add_particles(
                    self.rect.centerx, self.rect.centery,
                    COLOR_BRIGHT_GOLD, count=25, speed=6, size=6, lifetime=2.0
                )
            elif self.result == 1:
                particle_system.add_particles(
                    self.rect.centerx, self.rect.centery,
                    COLOR_DEEP_RED, count=15, speed=4, size=4
                )
                
            narrate_roll_result(self.result)
            if callable(self.callback):
                try:
                    self.callback(self.result)
                except Exception as e:
                    print("[ERRO] callback dice:", e)

    def draw(self, surf):
        if not self.rolling and self.result is None:
            return
            
        # Sombra
        shadow_rect = self.rect.move(6, 6)
        pygame.draw.rect(surf, COLOR_SHADOW, shadow_rect, border_radius=20)
        
        # Cor do dado baseado no valor
        if self.current_value == 20:
            dice_color = COLOR_BRIGHT_GOLD
            border_color = COLOR_BRIGHT_GOLD
        elif self.current_value == 1:
            dice_color = COLOR_DEEP_RED
            border_color = COLOR_RICH_RED
        else:
            dice_color = COLOR_GOLDEN_PARCHMENT
            border_color = COLOR_WARM_GOLD
            
        # Dado
        pygame.draw.rect(surf, dice_color, self.rect, border_radius=15)
        pygame.draw.rect(surf, border_color, self.rect, 4, border_radius=15)
        
        # Número
        num_surf = FONT_HEADER.render(str(self.current_value), True, COLOR_DARK_TEXT)
        surf.blit(num_surf, (self.rect.centerx - num_surf.get_width()//2,
                           self.rect.centery - num_surf.get_height()//2))

dice_anim = DiceAnimation(SCREEN_W//2 - 70, SCREEN_H//2 - 70)

# ==================== SISTEMA DE COMBATE ====================
GAME_STATE = {"mode":"explore"}
current_enemy = None
player_turn = True
combat_log = deque(maxlen=8)
combat_background = None

def create_combat_background():
    bg = pygame.Surface((SCREEN_W, SCREEN_H))
    bg.fill(COLOR_DEEP_WOOD)
    
    # Padrão de batalha
    for i in range(50):
        x = random.randint(0, SCREEN_W)
        y = random.randint(0, SCREEN_H)
        size = random.randint(2, 6)
        color = random.choice([COLOR_RICH_RED, COLOR_DEEP_RED, COLOR_DARK_BORDER])
        pygame.draw.circle(bg, color, (x, y), size)
        
    return bg

def roll_dice(sides=20):
    return random.randint(1, sides)

def narrate_roll_result(result, difficulty=15):
    if result == 20:
        dialog.push("🎯 CRÍTICO! Os deuses sorriem para você!", "Sistema de Dados")
        dialog.push("Seu ataque é devastador! Efeitos dobrados!", "Sistema de Dados")
    elif result >= difficulty:
        dialog.push(f"🎲 Sucesso! {result} supera a dificuldade {difficulty}", "Sistema de Dados")
    elif result == 1:
        dialog.push("💀 FALHA CRÍTICA! O destino se volta contra você!", "Sistema de Dados")
        dialog.push("Algo terrivelmente errado acontece...", "Sistema de Dados")
    else:
        dialog.push(f"🎲 Falha... {result} não é suficiente", "Sistema de Dados")

def start_combat(enemy: GameEnemy):
    GAME_STATE["mode"] = "combat"
    global current_enemy, player_turn, combat_background
    current_enemy, player_turn = enemy, True
    combat_log.clear()
    combat_background = create_combat_background()
    
    dialog.push(f"⚔️ COMBATE INICIADO! {enemy.name} avança!", "Sistema de Batalha")
    dialog.push(f"Tipo: {enemy.tipo} | Fraqueza: {enemy.fraqueza}", "Sistema de Batalha")
    particle_system.add_particles(SCREEN_W//2, 100, enemy.color_scheme, count=20, speed=3)

def enemy_action():
    global current_enemy, player_turn
    if not current_enemy or not current_enemy.alive: 
        return
        
    roll, total = roll_dice(), roll_dice()
    dmg = max(1, current_enemy.atk + (total // 10))
    
    # Dano no jogador com efeito
    player.take_damage(dmg)
    combat_log.appendleft(f"💥 {current_enemy.name} ataca! {dmg} de dano!")
    
    # Efeito visual
    particle_system.add_particles(
        SCREEN_W//4, SCREEN_H//2, 
        COLOR_DEEP_RED, count=12, speed=2
    )
    
    if player.hp <= 0:
        dialog.push("☠️ Você foi derrotado... A escuridão consome seu espírito.", "Sistema de Batalha")
        GAME_STATE["mode"] = "defeated"
    else:
        player_turn = True

def player_use_ability(idx):
    global player_turn, current_enemy
    a = player.abilities[idx]
    
    if not a.ready():
        dialog.push(f"⏳ {a.name} em recarga: {a.remaining:.1f}s", "Sistema")
        return
        
    if player.mp < a.cost_mp:
        dialog.push("💧 Energia mística insuficiente!", "Sistema")
        return
        
    if not a.use():
        return
        
    player.mp -= a.cost_mp
    
    if GAME_STATE["mode"] != "combat":
        # Uso fora de combate
        if a.power < 0:
            heal_amount = -a.power
            player.hp = min(player.max_hp, player.hp + heal_amount)
            dialog.push(f"✨ {a.name} restaura {heal_amount} de vida!", player.name)
            particle_system.add_particles(
                SCREEN_W//4, SCREEN_H//2,
                COLOR_MYSTIC_BLUE, count=15, speed=2
            )
        return
        
    # Em combate
    if not player_turn:
        dialog.push("🛑 Ainda não é sua vez!", "Sistema")
        return
        
    roll, total = roll_dice(), roll_dice()
    hit = (roll + player.level) >= 10  # Dificuldade um pouco maior
    
    if hit:
        dmg = a.power + (player.level // 2) + (total // 12)
        current_enemy.take_damage(dmg)
        combat_log.appendleft(f"⭐ {a.name} acerta! {dmg} de dano em {current_enemy.name}")
        
        # Efeitos especiais por tipo de habilidade
        if a.tipo == "Físico":
            particle_system.add_particles(
                SCREEN_W*3//4, SCREEN_H//2,
                player.color_scheme, count=10, speed=3
            )
        elif a.tipo == "Magia":
            particle_system.add_particles(
                SCREEN_W*3//4, SCREEN_H//2,
                COLOR_MYSTIC_BLUE, count=15, speed=4
            )
    else:
        combat_log.appendleft(f"💫 {a.name} erra! ({roll}+{player.level})")
        
    if not current_enemy.alive:
        victory_sequence()
    else:
        player_turn = False
        pygame.time.set_timer(pygame.USEREVENT + 1, 1200)  # Timer para ação inimiga

def victory_sequence():
    global current_enemy
    exp_gain = current_enemy.max_hp // 3
    gold_gain = random.randint(20, 60)
    
    player.gain_exp(exp_gain)
    dialog.push(f"🎉 Vitória! {current_enemy.name} foi derrotado!", "Sistema de Batalha")
    dialog.push(f"⭐ +{exp_gain} EXP | 💰 +{gold_gain} Moedas", "Sistema de Batalha")
    
    # Efeitos de vitória
    particle_system.add_particles(
        SCREEN_W//2, SCREEN_H//2,
        COLOR_BRIGHT_GOLD, count=40, speed=5, size=6, lifetime=2.0
    )
    
    GAME_STATE["mode"] = "explore"
    current_enemy = None
    
    # Progresso em missões
    if quest_log.active_quest:
        quest_log.complete_step(quest_log.active_quest.title)

# ==================== INTERFACE DO USUÁRIO ====================
buttons = []

# Botões principais
btn_accept = Button((SCREEN_W//2 - 240, SCREEN_H - 200, 220, 50), "Aceitar Destino", accept_mission, "icon_accept.png", "Embarque nesta jornada épica")
btn_decline = Button((SCREEN_W//2 + 20, SCREEN_H - 200, 220, 50), "Recusar Chamado", decline_mission, "icon_decline.png", "Prossiga por outros caminhos")
buttons.extend([btn_accept, btn_decline])

# Botões de habilidade
ability_buttons = []
btn_size = 80
padding = 15
start_x = SCREEN_W - (btn_size + 20)
start_y = SCREEN_H - (btn_size + 20) - 80

for i, ability in enumerate(player.abilities):
    rect = (start_x - i*(btn_size + padding), start_y, btn_size, btn_size)
    callback = lambda idx=i: player_use_ability(idx)
    btn = Button(rect, "", callback, f"skill_{ability.name.lower()}.png", ability.desc)
    ability_buttons.append(btn)
    buttons.append(btn)

# Botões de ação
roll_btn = Button((SCREEN_W - 160, 30, 130, 40), "Rolar d20", on_roll, "icon_dice.png", "Teste sua sorte contra o destino")
buttons.append(roll_btn)

buttons.append(Button((SCREEN_W - 160, 85, 130, 40), "Missões", show_quest_log, "icon_quest.png", "Revise suas missões e progresso"))
buttons.append(Button((SCREEN_W - 160, 140, 130, 40), "Poção Vida", lambda: use_potion("Poção de Vida"), "icon_potion.png", "Restaura 35 pontos de vida"))
buttons.append(Button((SCREEN_W - 160, 195, 130, 40), "Poção Mana", lambda: use_potion("Poção de Mana"), "icon_mana.png", "Restaura 25 pontos de mana"))

# ==================== FUNÇÕES DE DESENHO SIMPLIFICADAS ====================
def draw_panel(surf, rect, color, border_color, shadow_color, border_radius=8):
    # Sombra
    shadow_rect = rect.move(4, 4)
    pygame.draw.rect(surf, shadow_color, shadow_rect, border_radius=border_radius)
    
    # Cor principal
    pygame.draw.rect(surf, color, rect, border_radius=border_radius)
    
    # Borda
    pygame.draw.rect(surf, border_color, rect, 3, border_radius=border_radius)

def draw_bar(surf, x, y, w, h, current, maximum, color, label="", show_numbers=True):
    # Painel de fundo
    bg_rect = pygame.Rect(x, y, w, h)
    draw_panel(surf, bg_rect, COLOR_DEEP_WOOD, COLOR_DARK_BORDER, COLOR_SHADOW, border_radius=6)
    
    # Barra de preenchimento
    if maximum > 0:
        fill_width = max(4, int((w - 6) * (current / maximum)))
        fill_rect = pygame.Rect(x + 3, y + 3, fill_width, h - 6)
        pygame.draw.rect(surf, color, fill_rect, border_radius=4)
    
    # Texto
    if show_numbers:
        text = f"{label}{current}/{maximum}"
        text_surf = FONT_SMALL.render(text, True, COLOR_GOLDEN_PARCHMENT)
        surf.blit(text_surf, (x + w//2 - text_surf.get_width()//2, y + h//2 - text_surf.get_height()//2))

def draw_character_portrait(surf, rect, character, is_flashing=False):
    # Moldura do retrato
    frame_rect = rect.inflate(20, 20)
    draw_panel(surf, frame_rect, COLOR_RICH_WOOD, COLOR_BRIGHT_GOLD, COLOR_SHADOW, border_radius=12)
    
    # Efeito de dano
    if is_flashing:
        flash_overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        flash_overlay.fill((255, 50, 50, 100))
        surf.blit(flash_overlay, rect.topleft)
    
    # Retrato
    if character.portrait:
        surf.blit(character.portrait, rect.topleft)

# ==================== MAPA DE FUNDO SIMPLIFICADO ====================
# Criar mapa procedural
map_img = pygame.Surface((SCREEN_W, SCREEN_H))
# Gradiente de fundo simples
for y in range(SCREEN_H):
    ratio = y / SCREEN_H
    r = max(0, min(255, 20 + int(30 * ratio)))
    g = max(0, min(255, 15 + int(20 * ratio)))
    b = max(0, min(255, 8 + int(15 * ratio)))
    pygame.draw.line(map_img, (r, g, b), (0, y), (SCREEN_W, y))

# ==================== DIÁLOGO INICIAL ====================
dialog = DialogueBox((50, SCREEN_H - 220, SCREEN_W - 100, 180))

# Criar placeholders para os retratos dos NPCs
sage_portrait = create_placeholder_icon((80, 80), COLOR_MYSTIC_BLUE, "🧙")
master_portrait = create_placeholder_icon((80, 80), COLOR_RICH_WOOD, "👑")

# Narrativa introdutória épica
dialog.push(
    "Era o Ano da Serpente Prateada, quando as estrelas se alinhavam para o grande Conclave. "
    "Três luas cheias haviam nascido desde que a Profecia do Renascimento fora revelada...",
    "Crônicas de Eldoria", None, True
)

dialog.push(
    "Você, nobre aventureiro, é convocado para o Conclave de Eldoria. "
    "Seu nome ecoa nas tavernas, suas façanhas são sussurradas nos ventos. "
    "O reino precisa de um herói para desvendar os Mistérios das Eras.",
    "Arquimedes, o Sábio", sage_portrait
)

dialog.push(
    "A Vila de Eldoria clama por ajuda. Bandidos têm aterrorizado os comerciantes e a paz está ameaçada. "
    "Você aceita este chamado do destino?",
    "Mestre do Conclave", master_portrait
)

# ==================== LOOP PRINCIPAL ====================
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    mouse_pos = pygame.mouse.get_pos()

    # Processamento de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and dialog.visible:
                if dialog.char_index < len(dialog.text):
                    dialog.skip()
                else:
                    dialog.start_next()
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Diálogo
            if dialog.visible and dialog.rect.collidepoint(event.pos):
                if dialog.char_index < len(dialog.text):
                    dialog.skip()
                else:
                    dialog.start_next()
                    
            # Mapa (apenas em modo exploração)
            elif GAME_STATE["mode"] == "explore":
                for area in map_areas:
                    if area.rect.collidepoint(event.pos) and area.discovered:
                        dialog.push(f"🏞️ {area.name}", "Exploração")
                        dialog.push(f"{area.description}", "Sistema")
                        # Oferecer missão da comunidade
                        quest = area_quests.get("Vila de Eldoria")
                        if quest and not quest.completed and quest.title not in [q.title for q in quest_log.quests]:
                            dialog.push("💬 O prefeito da vila tem uma missão importante para você.", "Sistema")
                        break
                        
            # Botões
            for button in buttons:
                button.handle_event(event)
                
        elif event.type == pygame.USEREVENT + 1:
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            if GAME_STATE["mode"] == "combat" and current_enemy and current_enemy.alive:
                enemy_action()

    # Atualizações
    player.update(dt)
    particle_system.update(dt)
    dialog.update(dt)
    dice_anim.update(dt)
    
    if current_enemy:
        current_enemy.update(dt)
        
    for button in buttons:
        button.update(mouse_pos, dt)
        
    for area in map_areas:
        area.update(mouse_pos, dt)

    # Renderização
    screen.blit(map_img, (0, 0))
    
    # Modo combate - overlay escuro
    if GAME_STATE["mode"] == "combat":
        combat_overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        combat_overlay.fill((0, 0, 0, 100))
        screen.blit(combat_overlay, (0, 0))
        if combat_background:
            screen.blit(combat_background, (0, 0))
    
    # Áreas do mapa
    for area in map_areas:
        area.draw(screen, mouse_pos)
    
    # Painel do personagem (superior esquerdo)
    panel_rect = pygame.Rect(30, 30, 360, 200)
    draw_panel(screen, panel_rect, COLOR_RICH_WOOD, COLOR_WARM_GOLD, COLOR_SHADOW, border_radius=12)
    
    # Retrato do personagem
    portrait_rect = pygame.Rect(50, 50, 100, 100)
    draw_character_portrait(screen, portrait_rect, player, player.damage_flash > 0)
    
    # Informações do personagem
    info_x = 170
    screen.blit(FONT_LARGE.render(player.name, True, COLOR_BRIGHT_GOLD), (info_x, 45))
    screen.blit(FONT_SMALL.render(f"{player.classe} Nv.{player.level}", True, COLOR_GOLDEN_PARCHMENT), (info_x, 80))
    
    # Barras de status
    draw_bar(screen, info_x, 105, 200, 22, player.hp, player.max_hp, COLOR_RICH_RED, "❤️ ")
    draw_bar(screen, info_x, 132, 200, 18, player.mp, player.max_mp, COLOR_MYSTIC_BLUE, "💧 ")
    
    # Experiência
    exp_ratio = player.exp / player.exp_to_next
    exp_text = f"⭐ EXP: {player.exp}/{player.exp_to_next} ({exp_ratio*100:.1f}%)"
    screen.blit(FONT_TINY.render(exp_text, True, COLOR_GOLDEN_PARCHMENT), (info_x, 155))
    
    # Progresso da experiência
    exp_bar_rect = pygame.Rect(info_x, 170, 200, 8)
    pygame.draw.rect(screen, COLOR_DEEP_WOOD, exp_bar_rect, border_radius=4)
    if exp_ratio > 0:
        exp_fill = pygame.Rect(info_x, 170, int(200 * exp_ratio), 8)
        pygame.draw.rect(screen, COLOR_BRIGHT_GOLD, exp_fill, border_radius=4)
    
    # Missão ativa
    if quest_log.active_quest:
        quest_text = f"🎯 {quest_log.active_quest.title} [{quest_log.active_quest.get_progress()}]"
        screen.blit(FONT_TINY.render(quest_text, True, COLOR_GOLDEN_PARCHMENT), (50, 185))
    
    # Painel de combate
    if GAME_STATE["mode"] == "combat" and current_enemy:
        # Painel do inimigo
        enemy_panel = pygame.Rect(SCREEN_W//2 - 200, 30, 400, 140)
        draw_panel(screen, enemy_panel, COLOR_RICH_WOOD, current_enemy.color_scheme, COLOR_SHADOW, border_radius=12)
        
        # Retrato do inimigo
        enemy_portrait_rect = pygame.Rect(SCREEN_W//2 - 180, 50, 80, 80)
        draw_character_portrait(screen, enemy_portrait_rect, current_enemy, current_enemy.damage_flash > 0)
        
        # Informações do inimigo
        screen.blit(FONT_LARGE.render(current_enemy.name, True, current_enemy.color_scheme), (SCREEN_W//2 - 80, 45))
        screen.blit(FONT_SMALL.render(f"{current_enemy.tipo}", True, COLOR_GOLDEN_PARCHMENT), (SCREEN_W//2 - 80, 80))
        screen.blit(FONT_SMALL.render(f"⚡ Fraqueza: {current_enemy.fraqueza}", True, COLOR_GOLDEN_PARCHMENT), (SCREEN_W//2 - 80, 105))
        
        # Vida do inimigo
        draw_bar(screen, SCREEN_W//2 - 80, 125, 250, 20, current_enemy.hp, current_enemy.max_hp, current_enemy.color_scheme, "❤️ ")
        
        # Indicador de turno
        turn_text = "🎲 SUA VEZ" if player_turn else f"⚡ VEZ DE {current_enemy.name.upper()}"
        turn_color = COLOR_BRIGHT_GOLD if player_turn else current_enemy.color_scheme
        turn_surf = FONT_MEDIUM.render(turn_text, True, turn_color)
        screen.blit(turn_surf, (SCREEN_W//2 - turn_surf.get_width()//2, 170))
        
        # Log de combate
        log_panel = pygame.Rect(SCREEN_W//2 - 300, 200, 600, 120)
        draw_panel(screen, log_panel, COLOR_DEEP_WOOD, COLOR_WARM_GOLD, COLOR_SHADOW, border_radius=10)
        
        for i, entry in enumerate(list(combat_log)[:5]):
            log_surf = FONT_SMALL.render(entry, True, COLOR_GOLDEN_PARCHMENT)
            screen.blit(log_surf, (SCREEN_W//2 - 290, 210 + i * 22))
    
    # Botões
    for button in buttons:
        button.draw(screen)
    
    # Diálogo
    dialog.draw(screen)
    
    # Dados
    dice_anim.draw(screen)
    
    # Partículas (sobre tudo)
    particle_system.draw(screen)
    
    # Efeito de transição suave
    if GAME_STATE["mode"] == "defeated":
        defeat_overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        defeat_overlay.fill((0, 0, 0, 150))
        screen.blit(defeat_overlay, (0, 0))
        
        defeat_text = FONT_HEADER.render("FIM DA JORNADA", True, COLOR_DEEP_RED)
        screen.blit(defeat_text, (SCREEN_W//2 - defeat_text.get_width()//2, SCREEN_H//2 - 50))
        
        restart_text = FONT_MEDIUM.render("Pressione R para recomeçar", True, COLOR_GOLDEN_PARCHMENT)
        screen.blit(restart_text, (SCREEN_W//2 - restart_text.get_width()//2, SCREEN_H//2 + 20))
        
        # Processar restart
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Reiniciar o jogo
            player = PlayerCharacter("Sir Alaric de Eldoria", "Guerreiro", 1, 120, 40, 18)
            GAME_STATE["mode"] = "explore"
            current_enemy = None
            quest_log = QuestLog()
            dialog.queue.clear()
            dialog.push("Uma nova chance surge das cinzas...", "Renascimento")
            dialog.push("O destino oferece outro caminho. Escolha sabiamente.", "Mestre do Conclave")

    pygame.display.flip()

pygame.quit()
sys.exit()