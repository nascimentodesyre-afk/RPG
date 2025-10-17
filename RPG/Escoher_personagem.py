# player_select.py - RPG-Medieval Style
import pygame
import sys
import random
from pygame import Rect

pygame.init()
pygame.font.init()

# --------------------
# Configurações
# --------------------
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
FPS = 60

musica_fundo = pygame.mixer.music.load('Lightning Traveler - Inspiring Epic.mp3.mp3') 
pygame.mixer.music.play(-1)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("HERO SELECTION - Medieval RPG")

clock = pygame.time.Clock()

# Paleta Medieval RPG (tons de terra, verde-musgo, ouro envelhecido, pergaminho)
# Paleta mais rica e terrosa para o tema medieval
BG_DARK = (40, 25, 15)       # Fundo muito escuro/marrom
BG_LIGHT = (80, 50, 30)      # Fundo marrom mais claro
FRAME_COLOR = (139, 69, 19)  # Marrom sela (madeira)
FRAME_INNER = (54, 45, 30)   # Marrom escuro/interior do painel
HEADER_COLOR = (255, 215, 0) # Ouro (Para títulos)
TEXT_COLOR = (222, 184, 135) # Pergaminho (Para texto de valor)
STAT_COLOR = (184, 134, 11)  # Bronze/Ouro Envelhecido (Para labels de stats)
HIGHLIGHT = (255, 255, 100)  # Brilho forte para seleção
SHADOW = (10, 10, 10)        # Sombra

# Fontes - Usando fontes estilo 'serifa' ou 'gótico' se disponíveis, ou emulando-as.
# No Pygame padrão, usamos tamanhos e cores para sugerir o estilo.
# Se fontes customizadas fossem carregadas:
# title_font = pygame.font.Font("MedievalFont.ttf", 64)
# panel_font = pygame.font.Font("OldBook.ttf", 32)

title_font = pygame.font.Font(None, 64)         # Título grande e impactante
panel_font = pygame.font.Font(None, 34)         # Nomes e rótulos importantes
stat_font = pygame.font.Font(None, 26)          # Stats e valores
pixel_font = pygame.font.Font(None, 22)         # Instruções pequenas

# Try to load portraits (optional). If missing, placeholders will be drawn.
def load_image_safe(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        # Transformação para manter a proporção e ajuste fino para o tema
        # No RPG-Medieval, podemos preferir um estilo mais áspero/pixelado
        img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None

portrait_left = load_image_safe("Guerreiro.jpg", (180, 180))
portrait_right = load_image_safe("Mago.jpg", (180, 180))
# optional background image (if you place it in folder)
bg_image = load_image_safe("background_medieval.png", (SCREEN_WIDTH, SCREEN_HEIGHT))

# --------------------
# Classes / Helpers
# --------------------
class PersonagemDados:
    def __init__(self, tipo):
        self.tipo = tipo
        self.id_personagem = random.randint(100, 999)
        self.nivel = 1
        self.forca = random.randint(15, 25) # Stats levemente aumentados
        self.pontos_vida = random.randint(100, 150)
        self.ponto_fraco = random.choice(["Fogo", "Gelo", "Sombra", "Veneno", "Maldade"])
        self.habilidade = random.choice(["Golpe do Dragão", "Escudo Divino", "Fúria Bárbara", "Canto da Sereia"])
        self.nome = "—" # Adicionado nome padrão para evitar erro no display
        
        # atributos específicos
        if tipo == "Guerreiro":
            self.defesa = 20
            self.resistencia = 10
            self.arma = "Espada de Batalha"
        elif tipo == "Cavalheiro":
            self.honra = 30
            self.montaria = "Corcel Real"
            self.arma = "Lança Sagrada"
        else: # Assumindo "Mago" ou "Ladrão" para o terceiro tipo implícito
            self.tipo = "Feiticeiro" # Tipo mais temático
            self.conoenergia = 60
            self.memoria_universal = "Rúnica"
            self.magia = "Bola de Fogo"

    def atributos_lista(self):
        """Retorna lista de tuplas (label, valor) para exibição, com labels em Português-BR."""
        base = [
            ("NOME", getattr(self, "nome", "—")),
            ("CLASSE", self.tipo),
            ("NÍVEL", self.nivel),
            ("FORÇA", self.forca),
            ("VIDA", self.pontos_vida),
            ("FRAQUEZA", self.ponto_fraco),
            ("HABILIDADE", self.habilidade)
        ]
        # acrescenta atributos por tipo
        if self.tipo == "Guerreiro":
            base.append(("DEFESA", self.defesa))
            base.append(("RESISTÊNCIA", self.resistencia))
            base.append(("ARMA", self.arma))
        elif self.tipo == "Cavalheiro":
            base.append(("HONRA", self.honra))
            base.append(("MONTARIA", self.montaria))
            base.append(("ARMA", self.arma))
        else:
            base.append(("MANA", self.conoenergia))
            base.append(("MEMÓRIA", self.memoria_universal))
            base.append(("MAGIA", self.magia))
        return base

# Dados dos dois personagens (tipos fixos para esta tela)
left_type = "Guerreiro"
right_type = "Mago"
left_data = PersonagemDados(left_type)
right_data = PersonagemDados(right_type)

# Estados
selected_side = None      # "left" ou "right" quando confirmado
hover_side = None
phase = "select"          # select -> name_input -> final
typing_name = ""
chosen_personagem = None

# Rects para layout (centralizados e com mais espaço vertical)
PADDING = 40
panel_w = 400
panel_h = 460 # Aumentado para mais espaço para stats
left_rect = Rect(SCREEN_WIDTH//2 - panel_w - PADDING//2, 100, panel_w, panel_h)
right_rect = Rect(SCREEN_WIDTH//2 + PADDING//2, 100, panel_w, panel_h)

# Portrait rects inside panels
portrait_size = (190, 190) # Ligeiramente maior
portrait_rect_left = Rect(left_rect.x + 24, left_rect.y + 40, portrait_size[0], portrait_size[1])
portrait_rect_right = Rect(right_rect.x + 24, right_rect.y + 40, portrait_size[0], portrait_size[1])

def draw_gradient_background():
    if bg_image:
        screen.blit(bg_image, (0,0))
        return
    # Vertical gradient Marrom Escuro
    for i in range(SCREEN_HEIGHT):
        t = i / SCREEN_HEIGHT
        r = int(BG_DARK[0] * (1 - t) + BG_LIGHT[0] * t)
        g = int(BG_DARK[1] * (1 - t) + BG_LIGHT[1] * t)
        b = int(BG_DARK[2] * (1 - t) + BG_LIGHT[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

def draw_header():
    # Título principal
    header_surf = title_font.render("HERO SELECTION", True, HEADER_COLOR)
    # Título com sombra
    shadow_surf = title_font.render("HERO SELECTION", True, SHADOW)
    screen.blit(shadow_surf, ((SCREEN_WIDTH - header_surf.get_width())//2 + 3, 36 + 3))
    screen.blit(header_surf, ((SCREEN_WIDTH - header_surf.get_width())//2, 36))
    
    # Detalhes decorativos laterais
    bar_w = 180
    bar_h = 10
    bar_color = FRAME_COLOR
    bar_y = 50
    
    # Barra Esquerda (simulando madeira entalhada)
    left_bar = Rect((SCREEN_WIDTH//2) - header_surf.get_width()//2 - bar_w - 20, bar_y, bar_w, bar_h)
    pygame.draw.rect(screen, bar_color, left_bar, border_radius=3)
    # Detalhe de ponta
    pygame.draw.circle(screen, bar_color, (left_bar.right + 5, bar_y + bar_h//2), 8)
    
    # Barra Direita
    right_bar = Rect((SCREEN_WIDTH//2) + header_surf.get_width()//2 + 20, bar_y, bar_w, bar_h)
    pygame.draw.rect(screen, bar_color, right_bar, border_radius=3)
    # Detalhe de ponta
    pygame.draw.circle(screen, bar_color, (right_bar.left - 5, bar_y + bar_h//2), 8)

def draw_panel(rect, data: PersonagemDados, portrait_img, side):
    # Outer frame (Madeira Escura)
    pygame.draw.rect(screen, SHADOW, rect.inflate(10,10)) 
    pygame.draw.rect(screen, FRAME_COLOR, rect, border_radius=12) # Borda mais arredondada/suave
    inner = rect.inflate(-18, -18) # Borda mais grossa
    pygame.draw.rect(screen, FRAME_INNER, inner, border_radius=8) # Interior do Painel

    # Title (TYPE) - Maior e em cima
    title_text = f"CLASSE: {data.tipo.upper()}"
    title = panel_font.render(title_text, True, HEADER_COLOR)
    screen.blit(title, (rect.x + 20, rect.y + 10))

    # Área do portrait
    p_rect = portrait_rect_left if side == "left" else portrait_rect_right
    
    # Borda do retrato - Estilo Placa de Madeira/Metal
    frame_outer = p_rect.inflate(16, 16)
    pygame.draw.rect(screen, FRAME_COLOR, frame_outer, border_radius=8) # Borda externa
    frame_inner_p = p_rect.inflate(8, 8)
    pygame.draw.rect(screen, FRAME_INNER, frame_inner_p, border_radius=6) # Borda interna

    # portrait (image or pixel placeholder)
    if portrait_img:
        screen.blit(portrait_img, p_rect.topleft)
    else:
        # Placeholder (mais cores terrosas)
        cell = 15
        for y in range(p_rect.y, p_rect.y + p_rect.h, cell):
            for x in range(p_rect.x, p_rect.x + p_rect.w, cell):
                shade = ((x // cell) + (y // cell)) % 3
                color = [(60 - shade*10), (40 - shade*10), (20 - shade*10)]
                pygame.draw.rect(screen, color, (x, y, cell - 1, cell - 1))

    # Attributes block (Lista de Stats)
    list_x = p_rect.right + 20
    list_y = p_rect.y - 10
    
    # Desenha uma linha separadora vertical
    pygame.draw.line(screen, FRAME_COLOR, (p_rect.right + 10, list_y), (p_rect.right + 10, p_rect.bottom + 10), 2)
    
    # Coloca os atributos em duas colunas, se possível, para preencher melhor
    # Usando a coluna única no momento para simplicidade de refatoração, mas com espaçamento maior
    line_height = 30
    for idx, (label, val) in enumerate(data.atributos_lista()):
        label_s = stat_font.render(f"{label}:", True, STAT_COLOR)
        val_s = stat_font.render(str(val), True, TEXT_COLOR)
        
        # Nome e Classe (primeiros itens) ficam abaixo do retrato
        if idx in (0, 1):
            y_pos = p_rect.bottom + 10 + (idx * line_height)
            x_pos_label = rect.x + 20
            x_pos_val = rect.x + 180
            # Adiciona uma linha divisória para o nome/classe
            if idx == 0:
                 pygame.draw.line(screen, FRAME_COLOR, (rect.x + 15, y_pos - 4), (p_rect.right + 5, y_pos - 4), 1)
        else:
            y_pos = list_y + (idx - 2) * line_height # Ajusta o índice
            x_pos_label = list_x
            x_pos_val = list_x + 160
            
        screen.blit(label_s, (x_pos_label, y_pos))
        screen.blit(val_s, (x_pos_val, y_pos))

    # highlight on hover or selection (Efeito de Brilho Medieval/Aura)
    if hover_side == side:
        # Borda suave de ouro
        pygame.draw.rect(screen, (HIGHLIGHT[0], HIGHLIGHT[1], HIGHLIGHT[2], 80), rect, width=4, border_radius=12)
        pygame.draw.rect(screen, HIGHLIGHT, rect, width=2, border_radius=12)
    if selected_side == side:
        # Brilho forte de seleção
        pygame.draw.rect(screen, (HIGHLIGHT[0], HIGHLIGHT[1], HIGHLIGHT[2], 120), rect.inflate(8,8), width=6, border_radius=14)
        pygame.draw.rect(screen, (255, 240, 160), rect, width=4, border_radius=12)

def draw_name_input_box():
    # Painel de Pergaminho/Caixa de Diálogo
    s = pygame.Surface((600, 150), pygame.SRCALPHA)
    s.fill((30, 20, 15, 240)) # Fundo quase preto
    rect = s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    
    # Borda de Madeira
    pygame.draw.rect(s, FRAME_COLOR, (0,0,rect.w, rect.h), 8, border_radius=10)
    
    screen.blit(s, rect.topleft)
    
    prompt = panel_font.render("INSIRA O NOME DO HERÓI (MAX 18):", True, TEXT_COLOR)
    screen.blit(prompt, (rect.x + 30, rect.y + 20))
    
    # Campo de Texto
    input_box_rect = Rect(rect.x + 30, rect.y + 70, rect.w - 60, 50)
    pygame.draw.rect(screen, FRAME_INNER, input_box_rect)
    pygame.draw.rect(screen, STAT_COLOR, input_box_rect, 2)
    
    # Cursor piscando
    cursor = ("|" if pygame.time.get_ticks() % 1000 < 500 else "")
    name_surf = panel_font.render(typing_name + cursor, True, HEADER_COLOR)
    
    # Centraliza o texto na caixa
    text_x = input_box_rect.x + 10
    text_y = input_box_rect.y + (input_box_rect.height - name_surf.get_height()) // 2
    screen.blit(name_surf, (text_x, text_y))

def draw_final_screen(data: PersonagemDados):
    # Painel Principal, Estilo "Tabela de Stats de Livro Antigo"
    panel_w = 880
    panel_h = 580
    rect = Rect((SCREEN_WIDTH - panel_w)//2, (SCREEN_HEIGHT - panel_h)//2, panel_w, panel_h)
    
    # Frame principal (Madeira)
    pygame.draw.rect(screen, SHADOW, rect.inflate(10,10), border_radius=16)
    pygame.draw.rect(screen, FRAME_COLOR, rect, border_radius=12)
    inner = rect.inflate(-20, -20)
    pygame.draw.rect(screen, FRAME_INNER, inner, border_radius=8)
    
    # Title (Nome e Classe)
    title = title_font.render(f"{data.nome.upper()}", True, HEADER_COLOR)
    subtitle = panel_font.render(f"CLASSE: {data.tipo.upper()}", True, STAT_COLOR)
    
    title_x = inner.x + (inner.width - title.get_width()) // 2
    subtitle_x = inner.x + (inner.width - subtitle.get_width()) // 2
    screen.blit(title, (title_x, inner.y + 20))
    screen.blit(subtitle, (subtitle_x, inner.y + 80))
    
    # Linha divisória
    pygame.draw.line(screen, FRAME_COLOR, (inner.x + 20, inner.y + 120), (inner.right - 20, inner.y + 120), 3)

    # Grande Portrait Esquerda
    p_rect = Rect(inner.x + 30, inner.y + 150, 260, 260)
    pygame.draw.rect(screen, FRAME_COLOR, p_rect.inflate(12,12), border_radius=8)
    pygame.draw.rect(screen, FRAME_INNER, p_rect, border_radius=4)
    
    # Portrait ou Placeholder
    portrait_img = None
    if selected_side == "left":
        portrait_img = portrait_left
    elif selected_side == "right":
        portrait_img = portrait_right

    if portrait_img:
        # Aumenta a imagem para caber no grande p_rect
        scaled_img = pygame.transform.smoothscale(portrait_img, (260, 260))
        screen.blit(scaled_img, p_rect.topleft)
    else:
        # Placeholder em um estilo mais denso/detalhado
        cell = 18
        for y in range(p_rect.y, p_rect.y + p_rect.h, cell):
            for x in range(p_rect.x, p_rect.x + p_rect.w, cell):
                shade = (x // cell) % 4
                color = [40 + shade*10, 30 + shade*8, 20 + shade*5]
                pygame.draw.rect(screen, color, (x, y, cell - 1, cell - 1))

    # Stats em Duas Colunas
    sx_col1 = p_rect.right + 40
    sx_col2 = sx_col1 + 250 
    sy = p_rect.y
    col_max_items = 7 # Quantos itens por coluna
    
    stats_list = [item for item in data.atributos_lista() if item[0] not in ("NOME", "CLASSE")] # Exclui Nome/Classe
    
    for idx, (label, val) in enumerate(stats_list):
        lbl = stat_font.render(f"{label}:", True, STAT_COLOR)
        val_s = stat_font.render(str(val), True, TEXT_COLOR)
        
        # Determina a coluna
        if idx < col_max_items:
            current_x = sx_col1
        else:
            current_x = sx_col2
            idx -= col_max_items # Ajusta o índice para a coluna 2

        current_y = sy + idx * 34
        
        screen.blit(lbl, (current_x, current_y))
        screen.blit(val_s, (current_x + 120, current_y))
        
    note = pixel_font.render("Pressione ESC para voltar à seleção ou ENTER para INICIAR AVENTURA", True, STAT_COLOR)
    screen.blit(note, (inner.x + 30, inner.bottom - 40))

# --------------------
# Loop principal
# --------------------
while True:
    dt = clock.tick(FPS)
    mouse = pygame.mouse.get_pos()
    mx, my = mouse

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if phase == "select":
            if event.type == pygame.MOUSEMOTION:
                hover_side = None
                if left_rect.collidepoint(mouse):
                    hover_side = "left"
                elif right_rect.collidepoint(mouse):
                    hover_side = "right"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if left_rect.collidepoint(mouse) or right_rect.collidepoint(mouse):
                    if left_rect.collidepoint(mouse):
                        selected_side = "left"
                    else:
                        selected_side = "right"
                    phase = "name_input"
                    typing_name = ""
        elif phase == "name_input":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Finaliza nome e cria chosen_personagem
                    temp_name = typing_name.strip()
                    if temp_name != "":
                        if selected_side == "left":
                            chosen_personagem = left_data
                        else:
                            chosen_personagem = right_data
                            
                        chosen_personagem.nome = temp_name
                        
                        # Regenera alguns valores para a sensação de 'rolagem de dado' final
                        chosen_personagem.forca = random.randint(18, 30) 
                        chosen_personagem.pontos_vida = random.randint(120, 180)
                        
                        phase = "final"
                        
                elif event.key == pygame.K_BACKSPACE:
                    typing_name = typing_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    # Cancela seleção
                    selected_side = None
                    phase = "select"
                    typing_name = ""
                else:
                    # Aceita caracteres imprimíveis, limite de 18
                    if len(typing_name) < 18 and event.unicode.isprintable():
                        typing_name += event.unicode
        elif phase == "final":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Voltar para seleção
                    phase = "select"
                    selected_side = None
                    chosen_personagem = None
                elif event.key == pygame.K_RETURN:
                    # Simular início do jogo
                    print(f"Aventura de {chosen_personagem.nome} ({chosen_personagem.tipo}) COMEÇOU!")
                    pygame.quit()
                    sys.exit()

    # Desenho
    draw_gradient_background()
    
    if phase == "select" or phase == "name_input":
        draw_header()
        draw_panel(left_rect, left_data, portrait_left, "left")
        draw_panel(right_rect, right_data, portrait_right, "right")

        if phase == "select":
            instruct = pixel_font.render("CLIQUE NO HERÓI DESEJADO PARA ESCOLHER SEU DESTINO", True, STAT_COLOR)
            screen.blit(instruct, ((SCREEN_WIDTH - instruct.get_width())//2, SCREEN_HEIGHT - 40))
        elif phase == "name_input":
            draw_name_input_box()
            
    elif phase == "final" and chosen_personagem:
        draw_final_screen(chosen_personagem)

    pygame.display.flip()
