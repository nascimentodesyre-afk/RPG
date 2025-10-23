# Escoher_personagem.py - RPG-Medieval Style (Integrado com Banco de Dados)
import pygame
import sys
import random
import sqlite3
import os
import subprocess
from pygame import Rect

# --------------------
# Verifica se há um ID de jogador salvo
# --------------------
def carregar_id_jogador():
    """Carrega o ID do jogador do arquivo temporário"""
    try:
        if os.path.exists('temp_jogador_id.txt'):
            with open('temp_jogador_id.txt', 'r') as f:
                id_jogador = int(f.read().strip())
            # Remove o arquivo temporário após ler
            os.remove('temp_jogador_id.txt')
            return id_jogador
        else:
            print("AVISO: Nenhum ID de jogador encontrado. Usando ID 1 para teste.")
            return 1
    except Exception as e:
        print(f"Erro ao carregar ID do jogador: {e}")
        return 1

def finalizar_e_retornar():
    """Fecha o seletor e retorna ao sistema de login"""
    pygame.quit()
    try:
        subprocess.run([sys.executable, "sistema_login.py"])  # Substitua pelo nome correto do seu arquivo
    except Exception as e:
        print(f"Erro ao retornar ao sistema de login: {e}")
    sys.exit()

# Carrega o ID do jogador no início
id_jogador_atual = carregar_id_jogador()

pygame.init()

# --------------------
# Configurações
# --------------------
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("HERO SELECTION - Medieval RPG")
clock = pygame.time.Clock()  # CORREÇÃO: Definindo o clock aqui

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
# CLASSE GERENCIADOR DO BANCO DE DADOS
# --------------------
class GerenciadorBanco:
    def __init__(self):
        self.db_path = 'banco/rpg.db'
    
    def get_connection(self):
        """Cria e retorna uma conexão com o banco de dados."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None
    
    def criar_personagem(self, id_jogador, nome, classe):
        """Cria um novo personagem no banco de dados."""
        conn = self.get_connection()
        if not conn: 
            return False, "Erro ao conectar ao banco"
        
        try:
            cursor = conn.cursor()
            
            # Verifica se o jogador já tem um personagem com esse nome
            cursor.execute("SELECT 1 FROM Personagem WHERE id_jogador = ? AND nome = ?", (id_jogador, nome))
            if cursor.fetchone():
                return False, "Já existe um personagem com este nome"
            
            # Define atributos base baseado na classe
            if classe == "Guerreiro":
                forca = random.randint(18, 25)
                destreza = random.randint(10, 15)
                constituicao = random.randint(15, 20)
                inteligencia = random.randint(8, 12)
                pontos_vida = random.randint(120, 160)
                pontos_mana = random.randint(20, 40)
                ponto_fraco = random.choice(["Magia", "Veneno", "Fogo"])
            else:  # Mago
                forca = random.randint(8, 12)
                destreza = random.randint(12, 16)
                constituicao = random.randint(10, 14)
                inteligencia = random.randint(18, 25)
                pontos_vida = random.randint(80, 120)
                pontos_mana = random.randint(80, 120)
                ponto_fraco = random.choice(["Físico", "Sombra", "Gelo"])
            
            # Insere o personagem
            cursor.execute("""
                INSERT INTO Personagem (id_jogador, nome, classe, nivel, forca, destreza, constituicao, 
                                      inteligencia, pontos_vida, pontos_vida_max, pontos_mana, pontos_mana_max,
                                      ponto_fraco, experiencia, experiencia_proximo_nivel)
                VALUES (?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 100)
            """, (id_jogador, nome, classe, forca, destreza, constituicao, inteligencia, 
                  pontos_vida, pontos_vida, pontos_mana, pontos_mana, ponto_fraco))
            
            personagem_id = cursor.lastrowid
            
            # Cria o inventário do personagem
            cursor.execute("INSERT INTO Inventario (id_personagem, capacidade) VALUES (?, 20)", (personagem_id,))
            
            # Adiciona habilidades base da classe
            cursor.execute("SELECT id_habilidade FROM Habilidade WHERE classe = ?", (classe,))
            habilidades_classe = cursor.fetchall()
            
            for habilidade in habilidades_classe:
                cursor.execute("""
                    INSERT INTO Personagem_Habilidade (id_personagem, id_habilidade, tempo_recarga_restante)
                    VALUES (?, ?, 0)
                """, (personagem_id, habilidade['id_habilidade']))
            
            # Adiciona itens iniciais
            itens_iniciais = self._obter_itens_iniciais(classe)
            for item_id in itens_iniciais:
                cursor.execute("""
                    INSERT INTO Inventario_Item (id_inventario, id_item, quantidade)
                    SELECT id_inventario, ?, 1 FROM Inventario WHERE id_personagem = ?
                """, (item_id, personagem_id))
            
            conn.commit()
            return True, f"Personagem {nome} criado com sucesso! ID: {personagem_id}"
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Erro ao criar personagem: {e}")
            return False, f"Erro no banco: {e}"
        finally:
            if conn: 
                conn.close()
    
    def _obter_itens_iniciais(self, classe):
        """Retorna IDs dos itens iniciais baseado na classe."""
        conn = self.get_connection()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            if classe == "Guerreiro":
                cursor.execute("SELECT id_item FROM Item WHERE nome IN ('Espada Longa', 'Armadura de Couro')")
            else:  # Mago
                cursor.execute("SELECT id_item FROM Item WHERE nome IN ('Cajado Arcano', 'Poção de Mana')")
            
            return [row['id_item'] for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Erro ao obter itens iniciais: {e}")
            return []
        finally:
            if conn: conn.close()
    
    def obter_habilidades_classe(self, classe):
        """Obtém as habilidades disponíveis para uma classe."""
        conn = self.get_connection()
        if not conn: return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT nome, descricao, dano, custo FROM Habilidade WHERE classe = ?", (classe,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao obter habilidades: {e}")
            return []
        finally:
            if conn: conn.close()

# --------------------
# Classes CORRIGIDAS para alinhar com SQL
# --------------------
class PersonagemDados:
    def __init__(self, tipo, gerenciador_db):
        self.tipo = tipo
        self.gerenciador_db = gerenciador_db
        self.id_personagem = random.randint(100, 999)
        self.nivel = 1
        self.forca = random.randint(15, 25)
        self.destreza = random.randint(10, 18)
        self.constituicao = random.randint(12, 20)
        self.inteligencia = random.randint(10, 20)
        self.pontos_vida = random.randint(100, 150)
        self.pontos_vida_max = self.pontos_vida
        self.pontos_mana = random.randint(50, 100)
        self.pontos_mana_max = self.pontos_mana
        self.ponto_fraco = random.choice(["Fogo", "Gelo", "Sombra", "Veneno", "Luz"])
        
        # Carrega habilidades do banco
        self.habilidades = self.gerenciador_db.obter_habilidades_classe(tipo)
        self.habilidade_principal = self.habilidades[0]['nome'] if self.habilidades else "Habilidade Básica"

        if tipo == "Guerreiro":
            self.defesa = random.randint(15, 22)
            self.resistencia = random.randint(8, 15)
            self.arma = "Espada de Batalha"
        elif tipo == "Mago":
            self.poder_magico = random.randint(18, 25)
            self.sabedoria = random.randint(16, 22)
            self.tempo_recarga = round(random.uniform(1.5, 4.0), 2)
            self.magia = self.habilidade_principal

        self.nome = "—"

    def atributos_lista(self):
        """Retorna lista de tuplas (label, valor) para exibição."""
        base = [
            ("NOME", getattr(self, "nome", "—")),
            ("CLASSE", self.tipo),
            ("NÍVEL", self.nivel),
            ("FORÇA", self.forca),
            ("DESTREZA", self.destreza),
            ("CONSTITUIÇÃO", self.constituicao),
            ("INTELIGÊNCIA", self.inteligencia),
            ("VIDA", f"{self.pontos_vida}/{self.pontos_vida_max}"),
            ("MANA", f"{self.pontos_mana}/{self.pontos_mana_max}"),
            ("FRAQUEZA", self.ponto_fraco),
            ("HABILIDADE", self.habilidade_principal)
        ]
        if self.tipo == "Guerreiro":
            base.extend([
                ("DEFESA", self.defesa),
                ("RESISTÊNCIA", self.resistencia),
                ("ARMA", self.arma)
            ])
        elif self.tipo == "Mago":
            base.extend([
                ("PODER MÁGICO", self.poder_magico),
                ("SABEDORIA", self.sabedoria),
                ("RECARGA", f"{self.tempo_recarga}s"),
                ("MAGIA", self.magia)
            ])
        return base

    def salvar_no_banco(self, id_jogador):
        """Salva o personagem no banco de dados."""
        return self.gerenciador_db.criar_personagem(id_jogador, self.nome, self.tipo)

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

    # Instruções
    note_pos = (rect.centerx, rect.bottom - 40)
    draw_text(screen, "Pressione ENTER para CONFIRMAR ou ESC para retornar", FONT_SMALL, STAT_COLOR, note_pos)

def draw_message_box(message, is_success=True):
    """Desenha uma caixa de mensagem."""
    box_w, box_h = 600, 150
    box_rect = Rect((SCREEN_WIDTH - box_w) // 2, (SCREEN_HEIGHT - box_h) // 2, box_w, box_h)
    
    # Fundo semi-transparente
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    draw_ornate_border(screen, box_rect, FRAME_COLOR, FRAME_INNER, SHADOW)
    
    # Cor baseada no tipo de mensagem
    color = HEADER_COLOR if is_success else (255, 50, 50)
    
    # Mensagem
    msg_pos = (box_rect.centerx, box_rect.centery - 15)
    draw_text(screen, message, FONT_HEADER, color, msg_pos)
    
    # Instrução
    inst_pos = (box_rect.centerx, box_rect.centery + 25)
    draw_text(screen, "Pressione qualquer tecla para continuar", FONT_SMALL, TEXT_COLOR, inst_pos)

# --------------------
# Estado do Jogo
# --------------------
gerenciador_db = GerenciadorBanco()
left_data = PersonagemDados("Guerreiro", gerenciador_db)
right_data = PersonagemDados("Mago", gerenciador_db)

selected_side = None
hover_side = None
phase = "select"  # select -> name_input -> final -> saving -> saved
typing_name = ""
chosen_personagem = None
message_text = ""
message_success = True

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
    clock.tick(FPS)  # AGORA CORRETO: clock está definido
    mouse_pos = pygame.mouse.get_pos()

    # --- Gerenciamento de Eventos ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finalizar_e_retornar()

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
                        chosen_personagem.pontos_vida_max = chosen_personagem.pontos_vida
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
                    # Salva no banco de dados
                    success, message = chosen_personagem.salvar_no_banco(id_jogador_atual)
                    message_text = message
                    message_success = success
                    phase = "saving"
        
        elif phase == "saving":
            if event.type == pygame.KEYDOWN:
                if message_success:
                    phase = "saved"
                else:
                    phase = "final"  # Volta para corrigir

        elif phase == "saved":
            if event.type == pygame.KEYDOWN:
                print(f"Personagem {chosen_personagem.nome} criado com sucesso!")
                finalizar_e_retornar()

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
    
    elif phase == "saving":
        draw_final_screen(chosen_personagem)
        draw_message_box("Salvando personagem no banco de dados...", True)
    
    elif phase == "saved" and chosen_personagem:
        draw_final_screen(chosen_personagem)
        draw_message_box(message_text, message_success)

    pygame.display.flip()

pygame.quit()
sys.exit()