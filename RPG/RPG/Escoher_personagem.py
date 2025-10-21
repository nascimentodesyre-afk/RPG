# player_select.py - RPG-Medieval Style
import pygame
import sys
import random
from pygame import Rect

pygame.init()

# --------------------
# Configurações
# --------------------
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("HERO SELECTION - Medieval RPG")
clock = pygame.time.Clock()

# Tenta carregar a música
try:
    pygame.mixer.music.load('audio/Lightning Traveler - Inspiring Epic.mp3.mp3')
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Aviso: Não foi possível carregar a música de fundo. {e}")

# --------------------
# Paleta de Cores e Estilo
# --------------------
# Paleta Medieval rica e terrosa
BG_DARK = (40, 25, 15)       # Fundo muito escuro/marrom
BG_LIGHT = (80, 50, 30)      # Fundo marrom mais claro
FRAME_COLOR = (139, 69, 19)  # Marrom sela (madeira)
FRAME_INNER = (54, 45, 30)   # Marrom escuro/interior do painel
HEADER_COLOR = (255, 215, 0) # Ouro (Para títulos)
TEXT_COLOR = (222, 184, 135) # Pergaminho (Para texto de valor)
STAT_COLOR = (184, 134, 11)  # Bronze/Ouro Envelhecido (Para labels de stats)
HIGHLIGHT_GOLD = (255, 223, 0, 100) # Ouro com transparência para brilho
SHADOW = (10, 10, 10)        # Sombra

# --------------------
# Fontes (Unificadas)
# --------------------
def load_font(path, size):
    try:
        return pygame.font.Font(path, size)
    except Exception as e:
        print(f"Aviso: não foi possível carregar '{path}' ({e}). Usando fonte padrão.")
        # Usando uma fonte serifada padrão como fallback
        return pygame.font.SysFont("georgia", size)

font_path = "font/MorrisRomanAlternate-Black.ttf"
FONT_TITLE = load_font(font_path, 52)
FONT_HEADER = load_font(font_path, 36)
FONT_BODY = load_font(font_path, 28)
FONT_SMALL = load_font(font_path, 22)

# --------------------
# Carregamento de Recursos
# --------------------
def load_image_safe(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        return None

portrait_left = load_image_safe("imagens/Guerreiro.jpg", (180, 180))
portrait_right = load_image_safe("imagens/Mago.jpg", (180, 180))
bg_image = load_image_safe("imagens/background_medieval.png", (SCREEN_WIDTH, SCREEN_HEIGHT))


# --------------------
# Classes
# --------------------
class PersonagemDados:
    def __init__(self, tipo):
        self.tipo = tipo
        self.id_personagem = random.randint(100, 999)
        self.nivel = 1
        self.forca = random.randint(15, 25)
        self.pontos_vida = random.randint(100, 150)
        self.ponto_fraco = random.choice(["Fogo", "Gelo", "Sombra", "Veneno", "Luz"])
        self.habilidade = random.choice(["Golpe Feroz", "Escudo Divino", "Fúria Cega", "Canto Mortal"])
        self.nome = "—"

        if tipo == "Guerreiro":
            self.defesa = 20
            self.resistencia = 10
            self.arma = "Espada de Batalha"
        elif tipo == "Mago":
            self.tipo = "Feiticeiro" # Nome mais temático
            self.mana = 60
            self.conhecimento = "Arcano"
            self.magia = "Bola de Fogo"
        # Adicione outras classes aqui se desejar

    def atributos_lista(self):
        """Retorna lista de tuplas (label, valor) para exibição."""
        base = [
            ("NOME", getattr(self, "nome", "—")),
            ("CLASSE", self.tipo),
            ("NÍVEL", self.nivel),
            ("FORÇA", self.forca),
            ("VIDA", self.pontos_vida),
            ("FRAQUEZA", self.ponto_fraco),
            ("HABILIDADE", self.habilidade)
        ]
        if self.tipo == "Guerreiro":
            base.extend([
                ("DEFESA", self.defesa),
                ("RESISTÊNCIA", self.resistencia),
                ("ARMA", self.arma)
            ])
        elif self.tipo == "Feiticeiro":
            base.extend([
                ("MANA", self.mana),
                ("CONHECIMENTO", self.conhecimento),
                ("MAGIA", self.magia)
            ])
        return base

# --------------------
# Funções de Desenho Auxiliares
# --------------------
def draw_text(surface, text, font, color, position, align="center"):
    """Desenha texto com alinhamento flexível."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.center = position
    elif align == "topleft":
        text_rect.topleft = position
    elif align == "midleft":
        text_rect.midleft = position
    elif align == "midright":
        text_rect.midright = position
    surface.blit(text_surface, text_rect)

def draw_ornate_border(surface, rect, color, inner_color, shadow_color):
    """Desenha uma borda estilizada com cantos decorativos."""
    # Sombra
    shadow_rect = rect.inflate(8, 8)
    pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=15)
    # Borda externa
    pygame.draw.rect(surface, color, rect, border_radius=12)
    # Painel interno
    inner_rect = rect.inflate(-16, -16)
    pygame.draw.rect(surface, inner_color, inner_rect, border_radius=8)
    # Detalhes nos cantos (simulando metal)
    corner_size = 12
    for corner in (rect.topleft, rect.topright, rect.bottomleft, rect.bottomright):
        pygame.draw.circle(surface, color, corner, corner_size)
        pygame.draw.circle(surface, HEADER_COLOR, corner, corner_size // 2, 2)


# --------------------
# Funções de Desenho Principais
# --------------------
def draw_background():
    """Desenha o fundo com imagem ou uma textura procedural."""
    if bg_image:
        screen.blit(bg_image, (0, 0))
        # Adiciona um vinhete para focar a atenção no centro
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.radial_gradient(vignette, (0,0,0,0), (0,0,0,180), (SCREEN_WIDTH//2, SCREEN_HEIGHT//2), SCREEN_WIDTH//1.5)
        screen.blit(vignette, (0,0))
    else:
        # Fundo com textura de pedra/pergaminho gerada
        screen.fill(BG_LIGHT)
        for _ in range(150): # Mais "manchas" para textura
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(50, 200)
            alpha = random.randint(5, 15)
            s = pygame.Surface((size, size), pygame.SRCALPHA)
            s.fill((BG_DARK[0], BG_DARK[1], BG_DARK[2], alpha))
            screen.blit(s, (x, y))

def draw_header():
    """Desenha o título principal da tela."""
    y_pos = 60
    draw_text(screen, "ESCOLHA SEU HERÓI", FONT_TITLE, SHADOW, (SCREEN_WIDTH // 2 + 3, y_pos + 3))
    draw_text(screen, "ESCOLHA SEU HERÓI", FONT_TITLE, HEADER_COLOR, (SCREEN_WIDTH // 2, y_pos))

    # Linhas decorativas
    line_y = y_pos + 40
    start_x = SCREEN_WIDTH // 2 - 250
    end_x = SCREEN_WIDTH // 2 + 250
    pygame.draw.line(screen, FRAME_COLOR, (start_x, line_y), (end_x, line_y), 3)
    pygame.draw.circle(screen, HEADER_COLOR, (start_x, line_y), 6, 2)
    pygame.draw.circle(screen, HEADER_COLOR, (end_x, line_y), 6, 2)

def draw_panel(rect, data: PersonagemDados, portrait_img, side):
    """Desenha um painel de personagem."""
    draw_ornate_border(screen, rect, FRAME_COLOR, FRAME_INNER, SHADOW)

    # Layout interno
    padding = 25
    inner_rect = rect.inflate(-padding*2, -padding*2)

    # Título da Classe
    draw_text(screen, data.tipo.upper(), FONT_HEADER, HEADER_COLOR, (rect.centerx, rect.y + 35))

    # Retrato
    p_rect = Rect(0, 0, 180, 180)
    p_rect.center = (rect.centerx, rect.y + 160)
    pygame.draw.rect(screen, FRAME_COLOR, p_rect.inflate(10, 10), border_radius=8)
    if portrait_img:
        screen.blit(portrait_img, p_rect.topleft)
    else: # Placeholder mais temático (silhueta)
        pygame.draw.rect(screen, SHADOW, p_rect)
        draw_text(screen, "?", FONT_TITLE, FRAME_COLOR, p_rect.center)

    # Atributos
    y_start = p_rect.bottom + 25
    line_height = 28
    stats_to_show = [item for item in data.atributos_lista() if item[0] not in ("NOME", "CLASSE")]

    for i, (label, val) in enumerate(stats_to_show[:6]): # Limita a 6 para caber bem
        y_pos = y_start + i * line_height
        label_pos = (rect.x + padding + 10, y_pos)
        val_pos = (rect.right - padding - 10, y_pos)
        draw_text(screen, f"{label}:", FONT_BODY, STAT_COLOR, label_pos, "midleft")
        draw_text(screen, str(val), FONT_BODY, TEXT_COLOR, val_pos, "midright")

    # Efeito de Hover/Seleção
    if hover_side == side:
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        s.fill(HIGHLIGHT_GOLD)
        screen.blit(s, rect.topleft)
    if selected_side == side:
        pygame.draw.rect(screen, HEADER_COLOR, rect, 4, border_radius=12)

def draw_name_input_box():
    """Desenha a caixa para inserir o nome do herói."""
    box_w, box_h = 700, 200
    box_rect = Rect((SCREEN_WIDTH - box_w) // 2, (SCREEN_HEIGHT - box_h) // 2, box_w, box_h)

    # Fundo semi-transparente para focar na caixa
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    draw_ornate_border(screen, box_rect, FRAME_COLOR, FRAME_INNER, SHADOW)
    
    # Textos
    prompt_pos = (box_rect.centerx, box_rect.y + 45)
    draw_text(screen, "Dê um nome ao seu campeão", FONT_HEADER, TEXT_COLOR, prompt_pos)

    # Caixa de input
    input_rect = Rect(0, 0, box_w - 100, 50)
    input_rect.center = box_rect.center
    input_rect.y += 20
    
    pygame.draw.rect(screen, SHADOW, input_rect.inflate(4, 4), border_radius=5)
    pygame.draw.rect(screen, BG_DARK, input_rect, border_radius=5)
    pygame.draw.rect(screen, STAT_COLOR, input_rect, 2, border_radius=5)

    # Texto e cursor
    cursor = "|" if pygame.time.get_ticks() % 1000 < 500 else ""
    text_pos = (input_rect.x + 15, input_rect.centery)
    draw_text(screen, typing_name + cursor, FONT_BODY, HEADER_COLOR, text_pos, "midleft")

def draw_final_screen(data: PersonagemDados):
    """Desenha a tela final de confirmação do personagem."""
    panel_w, panel_h = 1000, 600
    rect = Rect((SCREEN_WIDTH - panel_w) // 2, (SCREEN_HEIGHT - panel_h) // 2, panel_w, panel_h)
    
    draw_ornate_border(screen, rect, FRAME_COLOR, FRAME_INNER, SHADOW)

    # Nome e Classe
    draw_text(screen, data.nome.upper(), FONT_TITLE, HEADER_COLOR, (rect.centerx, rect.y + 60))
    draw_text(screen, f"A JORNADA DO {data.tipo.upper()} COMEÇA", FONT_HEADER, STAT_COLOR, (rect.centerx, rect.y + 110))
    pygame.draw.line(screen, FRAME_COLOR, (rect.x + 50, rect.y + 140), (rect.right - 50, rect.y + 140), 3)

    # Retrato Grande
    p_size = 230
    p_rect = Rect(rect.x + 50, rect.y + 170, p_size, p_size)
    pygame.draw.rect(screen, FRAME_COLOR, p_rect.inflate(10, 10), border_radius=8)
    
    portrait_img = portrait_left if data.tipo == "Guerreiro" else portrait_right
    if portrait_img:
        scaled_img = pygame.transform.smoothscale(portrait_img, (p_size, p_size))
        screen.blit(scaled_img, p_rect.topleft)
    else:
        pygame.draw.rect(screen, SHADOW, p_rect)
        draw_text(screen, "?", FONT_TITLE, FRAME_COLOR, p_rect.center)
    
    # --- INÍCIO DA SEÇÃO CORRIGIDA ---
    
    # Lista de Atributos Final
    stats_list = [item for item in data.atributos_lista() if item[0] != "NOME"]
    
    # Define a área total para os atributos e a divide em duas colunas
    stats_area_start_x = p_rect.right + 20
    stats_area_end_x = rect.right - 20
    stats_area_width = stats_area_end_x - stats_area_start_x
    col_width = stats_area_width / 2
    
    col1_x = stats_area_start_x
    col2_x = stats_area_start_x + col_width

    # Define o espaçamento fixo entre o nome do atributo e seu valor
    label_to_value_spacing = 120

    y_start = p_rect.y + 10
    line_height = 50  # Aumentado para mais respiro
    items_per_col = 5

    for i, (label, val) in enumerate(stats_list):
        # Determina em qual coluna e linha o atributo será desenhado
        current_col_x = col1_x if i < items_per_col else col2_x
        row_index = i % items_per_col
        y_pos = y_start + row_index * line_height
        
        # Define a posição do nome e do valor, ambos alinhados à esquerda
        label_pos = (current_col_x, y_pos)
        val_pos = (current_col_x + label_to_value_spacing, y_pos)
        
        draw_text(screen, f"{label}:", FONT_BODY, STAT_COLOR, label_pos, "midleft")
        draw_text(screen, str(val), FONT_BODY, TEXT_COLOR, val_pos, "midleft")

    # --- FIM DA SEÇÃO CORRIGIDA ---

    # Instruções
    note_pos = (rect.centerx, rect.bottom - 40)
    draw_text(screen, "Pressione ENTER para INICIAR ou ESC para retornar", FONT_SMALL, STAT_COLOR, note_pos)

# --------------------
# Estado do Jogo
# --------------------
left_data = PersonagemDados("Guerreiro")
right_data = PersonagemDados("Mago")

selected_side = None
hover_side = None
phase = "select"  # select -> name_input -> final
typing_name = ""
chosen_personagem = None

# Layout
PADDING = 40
panel_w = 420
panel_h = 520
y_pos = (SCREEN_HEIGHT - panel_h) // 2 + 30
left_rect = Rect(SCREEN_WIDTH // 2 - panel_w - PADDING // 2, y_pos, panel_w, panel_h)
right_rect = Rect(SCREEN_WIDTH // 2 + PADDING // 2, y_pos, panel_w, panel_h)


# --------------------
# Loop Principal
# --------------------
running = True
while running:
    clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()

    # --- Gerenciamento de Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if phase == "select":
            if event.type == pygame.MOUSEMOTION:
                hover_side = None
                if left_rect.collidepoint(mouse_pos):
                    hover_side = "left"
                elif right_rect.collidepoint(mouse_pos):
                    hover_side = "right"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hover_side:
                    selected_side = hover_side
                    phase = "name_input"
                    typing_name = ""
        
        elif phase == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    temp_name = typing_name.strip()
                    if temp_name:
                        chosen_personagem = left_data if selected_side == "left" else right_data
                        chosen_personagem.nome = temp_name
                        # Regenera alguns stats para a "rolagem final"
                        chosen_personagem.forca = random.randint(18, 30)
                        chosen_personagem.pontos_vida = random.randint(120, 180)
                        phase = "final"
                elif event.key == pygame.K_BACKSPACE:
                    typing_name = typing_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    selected_side = None
                    phase = "select"
                else:
                    if len(typing_name) < 18 and event.unicode.isprintable():
                        typing_name += event.unicode
        
        elif phase == "final":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    phase = "select"
                    selected_side = None
                    chosen_personagem = None
                elif event.key == pygame.K_RETURN:
                    print(f"Aventura de {chosen_personagem.nome} ({chosen_personagem.tipo}) COMEÇOU!")
                    running = False

    # --- Desenho na Tela ---
    draw_background()

    if phase in ["select", "name_input"]:
        draw_header()
        draw_panel(left_rect, left_data, portrait_left, "left")
        draw_panel(right_rect, right_data, portrait_right, "right")

        if phase == "select":
            instruct_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
            draw_text(screen, "CLIQUE NO HERÓI DESEJADO PARA ESCOLHER SEU DESTINO", FONT_SMALL, STAT_COLOR, instruct_pos)
        elif phase == "name_input":
            draw_name_input_box()

    elif phase == "final" and chosen_personagem:
        draw_final_screen(chosen_personagem)

    pygame.display.flip()

pygame.quit()
sys.exit()