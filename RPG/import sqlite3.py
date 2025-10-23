# sistema_login.py
import pygame
import sys
import os
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime
import subprocess

# Inicialização do Pygame
pygame.init()

# Configurações Globais
SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Crônicas de Eldoria - Login do Herói")
CLOCK = pygame.time.Clock()
FPS = 60

# Paleta Medieval (Cores)
DARK_BROWN = (50, 30, 15)
MEDIEVAL_BROWN = (101, 67, 33)
GOLD_DARK = (139, 105, 0)
GOLD_LIGHT = (200, 160, 0)
PERCHMENT_TEXT = (50, 40, 20)
PERCHMENT_BG = (245, 222, 179)
SHADOW = (10, 10, 10, 100)
SUCCESS_GREEN = (0, 100, 0)
ERROR_RED = (150, 0, 0)
BUTTON_BASE = (101, 67, 33)
BUTTON_HOVER = (139, 115, 85)

# Fontes
def load_font(path, size):
    try:
        return pygame.font.Font(path, size)
    except Exception as e:
        print(f"Aviso: não foi possível carregar '{path}' ({e}). Usando fonte padrão.")
        return pygame.font.SysFont("timesnewroman", size)

font_path = "font/MorrisRomanAlternate-Black.ttf"
title_font = load_font(font_path, 48)
font = load_font(font_path, 28)
small_font = load_font(font_path, 22)

# Música
try:
    musica_fundo = pygame.mixer.music.load('audio/Lightning Traveler - Inspiring Epic.mp3.mp3') 
    pygame.mixer.music.play(-1)
except pygame.error as e:
    print(f"Aviso: Não foi possível carregar a música de fundo: {e}")

# Funções de Ajuda
def load_background_image(path, size):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception as e:
        print(f"Aviso: Imagem de fundo '{path}' não carregada ({e}). Usando cor sólida.")
        s = pygame.Surface(size)
        s.fill(DARK_BROWN)
        return s

BACKGROUND_IMAGE = load_background_image("imagens/tela_fundo.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
PERGAMINO_CONTENT_RECT = pygame.Rect(180, 100, 680, 480)

# CLASSE DATABASE MANAGER
class DatabaseManager:
    def __init__(self):
        self.db_path = 'banco/rpg.db'
        self.conn = None
        self.connect()
        
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
            return True
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco: {e}")
            return False
            
    def close(self):
        if self.conn:
            self.conn.close()
            
    def usuario_existe(self, nome_usuario, email):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1 FROM Jogador WHERE nome_usuario = ? OR email = ?", 
                         (nome_usuario, email))
            return bool(cursor.fetchone())
        except sqlite3.Error as e:
            print(f"Erro ao verificar usuário: {e}")
            return True

    def cadastrar_jogador(self, nome_usuario, email, senha):
        try:
            cursor = self.conn.cursor()
            
            if self.usuario_existe(nome_usuario, email):
                return False, "Usuário ou email já existem!"

            if len(senha) < 6:
                return False, "A senha deve ter pelo menos 6 caracteres!"
            
            hashed_senha = hashlib.sha256(senha.encode()).hexdigest()
            
            cursor.execute(
                "INSERT INTO Jogador (nome_usuario, email, senha) VALUES (?, ?, ?)",
                (nome_usuario, email, hashed_senha)
            )
            
            novo_id = cursor.lastrowid
            self.conn.commit()
            
            cursor.execute(
                "INSERT INTO Sistema_Log (tipo, mensagem) VALUES (?, ?)",
                ("CADASTRO", f"Novo jogador cadastrado: {nome_usuario} (ID: {novo_id})")
            )
            self.conn.commit()
            
            return True, f"Herói criado com sucesso! (ID: {novo_id})"
        
        except sqlite3.IntegrityError:
            return False, "Usuário ou email já existem!"
        except sqlite3.Error as e:
            return False, f"Erro no banco: {e}"

    def fazer_login(self, nome_usuario, senha):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM Jogador WHERE nome_usuario = ?", (nome_usuario,))
            row = cursor.fetchone()

            if not row:
                return False, "Usuário ou senha inválidos!"
            
            hashed_senha = hashlib.sha256(senha.encode()).hexdigest()
            if row['senha'] != hashed_senha:
                return False, "Usuário ou senha inválidos!"
            
            jogador = {
                'id_jogador': row['id_jogador'],
                'nome_usuario': row['nome_usuario'],
                'email': row['email']
            }

            cursor.execute(
                "INSERT INTO Sistema_Log (tipo, mensagem) VALUES (?, ?)",
                ("LOGIN", f"Jogador {nome_usuario} fez login")
            )
            self.conn.commit()
            return True, jogador
        
        except sqlite3.Error as e:
            return False, f"Erro no banco: {e}"

# CLASSES DE INTERFACE
class InputBox:
    def __init__(self, x, y, width, height, text='', placeholder='', is_password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = MEDIEVAL_BROWN
        self.text = text
        self.placeholder = placeholder
        self.is_password = is_password
        self.active = False
        self.cursor_visible = True
        self.timer = 0
        self.update_surface()

    def update_surface(self):
        display_text = '*' * len(self.text) if self.is_password else self.text
        text_color = PERCHMENT_TEXT
        
        if self.active and self.cursor_visible:
            display_text += '|'
            
        if not self.text and not self.active:
            self.txt_surface = font.render(self.placeholder, True, GOLD_DARK)
        else:
            self.txt_surface = font.render(display_text, True, text_color)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.color = GOLD_LIGHT if self.active else MEDIEVAL_BROWN
            self.cursor_visible = True
            self.timer = 0
            self.update_surface()
                
        if event.type == pygame.KEYDOWN:
            if self.active:
                self.cursor_visible = True
                self.timer = 0
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < 30 and event.unicode.isprintable():
                        self.text += event.unicode
                self.update_surface()
                return self.text

    def update(self):
        if self.active:
            self.timer += CLOCK.get_time()
            if self.timer > 500:
                self.cursor_visible = not self.cursor_visible
                self.timer = 0
                self.update_surface()

    def draw(self, screen):
        pygame.draw.rect(screen, PERCHMENT_BG, self.rect)
        pygame.draw.rect(screen, self.color, self.rect, 3, border_radius=5)
        
        text_y = self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2
        screen.blit(self.txt_surface, (self.rect.x + 10, text_y))

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font_size=28):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = load_font(font_path, font_size)
        self.txt_surface = self.font.render(text, True, PERCHMENT_BG)

    def draw(self, screen):
        shadow_rect = self.rect.move(2, 2)
        pygame.draw.rect(screen, SHADOW, shadow_rect, border_radius=8)
        
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, DARK_BROWN, self.rect, 3, border_radius=8)
        
        text_rect = self.txt_surface.get_rect(center=self.rect.center)
        screen.blit(self.txt_surface, text_rect)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

    def handle_event(self, event, callback):
        if event.type == pygame.MOUSEMOTION:
            self.current_color = self.hover_color if self.is_hovered(event.pos) else self.color
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered(event.pos):
                callback()
                return True
        return False

# TELAS DO JOGO
class TelaLogin:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        
        content_center_x = PERGAMINO_CONTENT_RECT.centerx
        content_top = PERGAMINO_CONTENT_RECT.top

        INPUT_WIDTH = 350
        INPUT_HEIGHT = 45
        
        self.username_box = InputBox(content_center_x - INPUT_WIDTH // 2, content_top + 150, INPUT_WIDTH, INPUT_HEIGHT, placeholder='Nome de Usuário')
        self.password_box = InputBox(content_center_x - INPUT_WIDTH // 2, content_top + 230, INPUT_WIDTH, INPUT_HEIGHT, placeholder='Senha Secreta', is_password=True)
        
        BUTTON_WIDTH = 280
        BUTTON_HEIGHT = 55
        self.login_button = Button(content_center_x - BUTTON_WIDTH // 2, content_top + 320, BUTTON_WIDTH, BUTTON_HEIGHT, "Entrar no Reino", BUTTON_BASE, BUTTON_HOVER)
        self.register_button = Button(content_center_x - BUTTON_WIDTH // 2, content_top + 390, BUTTON_WIDTH, BUTTON_HEIGHT, "Criar Novo Herói", SUCCESS_GREEN, BUTTON_HOVER)
        
        self.message = ""
        self.message_color = ERROR_RED
        self.jogador_logado = None

    def handle_events(self, events):
        for event in events:
            self.username_box.handle_event(event)
            self.password_box.handle_event(event)
            
            if self.login_button.handle_event(event, self.login):
                if self.jogador_logado: 
                    return "game"  # Mudado para "game" para ir para a tela principal
            
            if self.register_button.handle_event(event, self.go_to_register):
                return "register"
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if self.username_box.active or self.password_box.active:
                    if self.login():
                        return "game"
        return "login"

    def login(self):
        username = self.username_box.text.strip()
        password = self.password_box.text.strip()
        
        if not username or not password:
            self.message = "Preencha todos os campos do pergaminho!"
            self.message_color = ERROR_RED
            return False
        
        success, result = self.gerenciador.fazer_login(username, password)
        if success:
            self.message = f"Bem-vindo(a), Cavaleiro(a) {username}!"
            self.message_color = SUCCESS_GREEN
            self.jogador_logado = result
            return True
        else:
            self.message = result
            self.message_color = ERROR_RED
            return False

    def go_to_register(self): 
        return "register"

    def update(self):
        self.username_box.update()
        self.password_box.update()
        
    def draw(self, screen):
        screen.blit(BACKGROUND_IMAGE, (0, 0))

        TITLE_GOLD = (212, 175, 55)
        TITLE_OUTLINE = (60, 40, 10)

        title_text = "CRÔNICAS DE ELDORIA"
        title_surface = title_font.render(title_text, True, TITLE_GOLD)
        shadow_surface = title_font.render(title_text, True, TITLE_OUTLINE)
        title_rect = title_surface.get_rect(center=(PERGAMINO_CONTENT_RECT.centerx, PERGAMINO_CONTENT_RECT.top + 40))

        screen.blit(shadow_surface, (title_rect.x + 3, title_rect.y + 3))
        screen.blit(title_surface, title_rect)

        username_label = small_font.render("Usuário:", True, PERCHMENT_TEXT)
        password_label = small_font.render("Senha:", True, PERCHMENT_TEXT)
    
        screen.blit(username_label, (self.username_box.rect.x, self.username_box.rect.y - 30))
        screen.blit(password_label, (self.password_box.rect.x, self.password_box.rect.y - 30))
    
        self.username_box.draw(screen)
        self.password_box.draw(screen)
        self.login_button.draw(screen)
        self.register_button.draw(screen)

        if self.message:
            msg_surface = small_font.render(self.message, True, self.message_color)
            msg_rect = msg_surface.get_rect(center=(PERGAMINO_CONTENT_RECT.centerx, PERGAMINO_CONTENT_RECT.bottom - 20))
            screen.blit(msg_surface, msg_rect)

class TelaCadastro:
    def __init__(self, gerenciador):
        self.gerenciador = gerenciador
        
        content_center_x = PERGAMINO_CONTENT_RECT.centerx
        content_top = PERGAMINO_CONTENT_RECT.top

        INPUT_WIDTH = 350
        INPUT_HEIGHT = 40
        
        self.username_box = InputBox(content_center_x - INPUT_WIDTH // 2, content_top + 90, INPUT_WIDTH, INPUT_HEIGHT, placeholder='Nome de Herói')
        self.email_box = InputBox(content_center_x - INPUT_WIDTH // 2, content_top + 160, INPUT_WIDTH, INPUT_HEIGHT, placeholder='Email do Reino')
        self.password_box = InputBox(content_center_x - INPUT_WIDTH // 2, content_top + 230, INPUT_WIDTH, INPUT_HEIGHT, placeholder='Crie uma Senha Forte', is_password=True)
        self.confirm_password_box = InputBox(content_center_x - INPUT_WIDTH // 2, content_top + 300, INPUT_WIDTH, INPUT_HEIGHT, placeholder='Confirme a Senha', is_password=True)
        
        BUTTON_WIDTH = 280
        BUTTON_HEIGHT = 50
        self.register_button = Button(content_center_x - BUTTON_WIDTH // 2, content_top + 370, BUTTON_WIDTH, BUTTON_HEIGHT, "Criar Herói", SUCCESS_GREEN, BUTTON_HOVER)
        self.back_button = Button(content_center_x - BUTTON_WIDTH // 2, content_top + 430, BUTTON_WIDTH, BUTTON_HEIGHT, "Voltar ao Portão", BUTTON_BASE, BUTTON_HOVER)
        
        self.message = ""
        self.message_color = ERROR_RED

    def handle_events(self, events):
        for event in events:
            self.username_box.handle_event(event)
            self.email_box.handle_event(event)
            self.password_box.handle_event(event)
            self.confirm_password_box.handle_event(event)
            
            if self.register_button.handle_event(event, self.register):
                pass 
            
            if self.back_button.handle_event(event, self.go_back): 
                return "login"
        
        return "register"

    def register(self):
        username = self.username_box.text.strip()
        email = self.email_box.text.strip()
        password = self.password_box.text.strip()
        confirm_password = self.confirm_password_box.text.strip()
        
        if not all([username, email, password, confirm_password]):
            self.message = "Preencha todos os campos do Cadastro!"
            self.message_color = ERROR_RED
            return False
        
        if password != confirm_password:
            self.message = "As senhas não coincidem. Confirme a sua senha!"
            self.message_color = ERROR_RED
            return False
        
        success, result = self.gerenciador.cadastrar_jogador(username, email, password)
        self.message = result
        self.message_color = SUCCESS_GREEN if success else ERROR_RED
        
        if success: 
            self.limpar_campos()
            
        return success

    def limpar_campos(self):
        for box in [self.username_box, self.email_box, self.password_box, self.confirm_password_box]:
            box.text = ""
            box.active = False
            box.color = MEDIEVAL_BROWN
            box.update_surface()

    def go_back(self): 
        return "login"

    def update(self):
        self.username_box.update()
        self.email_box.update()
        self.password_box.update()
        self.confirm_password_box.update()

    def draw(self, screen):
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        
        title = title_font.render("Criar NOVO HERÓI", True, GOLD_LIGHT)
        title_rect = title.get_rect(center=(PERGAMINO_CONTENT_RECT.centerx, PERGAMINO_CONTENT_RECT.top + 40))
        screen.blit(title, title_rect)
        
        username_label = small_font.render("Usuário:", True, PERCHMENT_TEXT)
        email_label = small_font.render("Email:", True, PERCHMENT_TEXT)
        password_label = small_font.render("Senha:", True, PERCHMENT_TEXT)
        confirm_label = small_font.render("Confirmar:", True, PERCHMENT_TEXT)
        
        screen.blit(username_label, (self.username_box.rect.x, self.username_box.rect.y - 30))
        screen.blit(email_label, (self.email_box.rect.x, self.email_box.rect.y - 30))
        screen.blit(password_label, (self.password_box.rect.x, self.password_box.rect.y - 30))
        screen.blit(confirm_label, (self.confirm_password_box.rect.x, self.confirm_password_box.rect.y - 30))
        
        self.username_box.draw(screen)
        self.email_box.draw(screen)
        self.password_box.draw(screen)
        self.confirm_password_box.draw(screen)
        self.register_button.draw(screen)
        self.back_button.draw(screen)
        
        if self.message:
            msg_surface = small_font.render(self.message, True, self.message_color)
            msg_rect = msg_surface.get_rect(center=(PERGAMINO_CONTENT_RECT.centerx, PERGAMINO_CONTENT_RECT.bottom - 20))
            screen.blit(msg_surface, msg_rect)

class TelaJogo:
    def __init__(self, gerenciador, jogador):
        self.gerenciador = gerenciador
        self.jogador = jogador 
        
        content_center_x = PERGAMINO_CONTENT_RECT.centerx
        content_top = PERGAMINO_CONTENT_RECT.top

        BUTTON_WIDTH = 280
        BUTTON_HEIGHT = 55
        
        self.sair_button = Button(PERGAMINO_CONTENT_RECT.left + 20, PERGAMINO_CONTENT_RECT.top + 20, 100, 50, "Sair", ERROR_RED, BUTTON_HOVER)
        self.criar_personagem_button = Button(content_center_x - BUTTON_WIDTH // 2, content_top + 280, BUTTON_WIDTH, BUTTON_HEIGHT, "Escolher Personagem", SUCCESS_GREEN, BUTTON_HOVER)
        self.selecionar_personagem_button = Button(content_center_x - BUTTON_WIDTH // 2, content_top + 350, BUTTON_WIDTH, BUTTON_HEIGHT, "Selecionar Personagem", BUTTON_BASE, BUTTON_HOVER)
        self.iniciar_jogo_button = Button(content_center_x - BUTTON_WIDTH // 2, content_top + 420, BUTTON_WIDTH, BUTTON_HEIGHT, "Iniciar Jornada", GOLD_DARK, BUTTON_HOVER)

        self.message = ""
        self.message_color = SUCCESS_GREEN

    def criar_personagem(self):
        """Fecha o Pygame atual e abre o seletor de personagens"""
        print(f"Jogador {self.jogador['id_jogador']} está criando um personagem...")
        
        # Salva o ID do jogador em um arquivo temporário para passar para o seletor
        with open('temp_jogador_id.txt', 'w') as f:
            f.write(str(self.jogador['id_jogador']))
        
        # Fecha o Pygame atual
        pygame.quit()
        
        # Importa e executa o seletor de personagens
        try:
            subprocess.run([sys.executable, "Escoher_personagem.py"])
        except Exception as e:
            print(f"Erro ao abrir seletor de personagens: {e}")
        
        # Encerra o programa atual
        sys.exit()

    def selecionar_personagem(self):
        """Lógica para selecionar personagem existente"""
        self.message = "Funcionalidade em desenvolvimento!"
        self.message_color = ERROR_RED

    def iniciar_jogo(self):
        """Lógica para iniciar o jogo"""
        self.message = "Jornada iniciada! Boa sorte, herói!"
        self.message_color = SUCCESS_GREEN
        return True

    def sair(self):
        """Volta para a tela de login"""
        return "login"

    def handle_events(self, events):
        for event in events:
            if self.sair_button.handle_event(event, self.sair): 
                return "login"
            if self.criar_personagem_button.handle_event(event, self.criar_personagem): 
                return "personagem"
            if self.selecionar_personagem_button.handle_event(event, self.selecionar_personagem): 
                pass
            if self.iniciar_jogo_button.handle_event(event, self.iniciar_jogo):
                pass
        return "game"

    def update(self):
        pass

    def draw(self, screen):
        screen.blit(BACKGROUND_IMAGE, (0, 0))
        
        title_text = f"BEM-VINDO(A), {self.jogador['nome_usuario'].upper()}!"
        if len(title_text) > 30:
             title_text = f"BEM-VINDO(A), {self.jogador['nome_usuario'][:20].upper()}..."

        title = title_font.render(title_text, True, GOLD_LIGHT)
        title_rect = title.get_rect(center=(PERGAMINO_CONTENT_RECT.centerx, PERGAMINO_CONTENT_RECT.top + 60))
        screen.blit(title, title_rect)
        
        pygame.draw.line(screen, DARK_BROWN, 
                         (PERGAMINO_CONTENT_RECT.left + 50, PERGAMINO_CONTENT_RECT.top + 120), 
                         (PERGAMINO_CONTENT_RECT.right - 50, PERGAMINO_CONTENT_RECT.top + 120), 2)
        
        info_id = font.render(f"ID do Aventureiro: {self.jogador['id_jogador']}", True, PERCHMENT_TEXT)
        info_email = font.render(f"Conexão do Reino: {self.jogador['email']}", True, PERCHMENT_TEXT)
        
        screen.blit(info_id, info_id.get_rect(center=(PERGAMINO_CONTENT_RECT.centerx, PERGAMINO_CONTENT_RECT.top + 160)))
        screen.blit(info_email, info_email.get_rect(center=(PERGAMINO_CONTENT_RECT.centerx, PERGAMINO_CONTENT_RECT.top + 200)))
        
        self.criar_personagem_button.draw(screen)
        self.selecionar_personagem_button.draw(screen)
        self.iniciar_jogo_button.draw(screen)
        self.sair_button.draw(screen)
        
        if self.message:
            msg_surface = small_font.render(self.message, True, self.message_color)
            msg_rect = msg_surface.get_rect(center=(PERGAMINO_CONTENT_RECT.centerx, PERGAMINO_CONTENT_RECT.bottom - 40))
            screen.blit(msg_surface, msg_rect)
        
        instrucao = small_font.render("O seu destino aguarda no reino de Eldoria!", True, GOLD_DARK)
        instrucao_rect = instrucao.get_rect(center=(PERGAMINO_CONTENT_RECT.centerx, PERGAMINO_CONTENT_RECT.bottom - 80))
        screen.blit(instrucao, instrucao_rect)

# CLASSE PRINCIPAL DO SISTEMA DE LOGIN
class SistemaLogin:
    def __init__(self):
        self.gerenciador = DatabaseManager()
        self.tela_login = TelaLogin(self.gerenciador)
        self.tela_cadastro = TelaCadastro(self.gerenciador)
        self.tela_jogo = None
        self.tela_atual = "login"
        self.executando = True
        self.jogador_logado = None

    def executar(self):
        while self.executando:
            eventos = pygame.event.get()
            for evento in eventos:
                if evento.type == pygame.QUIT:
                    self.executando = False

            if self.tela_atual == "login":
                prox_tela = self.tela_login.handle_events(eventos)
                self.tela_login.update()
                self.tela_login.draw(screen)
                
                if prox_tela == "game" and self.tela_login.jogador_logado:
                    self.jogador_logado = self.tela_login.jogador_logado
                    self.tela_jogo = TelaJogo(self.gerenciador, self.jogador_logado)
                    self.tela_atual = prox_tela
                elif prox_tela == "register":
                    self.tela_atual = prox_tela
                    
            elif self.tela_atual == "register":
                prox_tela = self.tela_cadastro.handle_events(eventos)
                self.tela_cadastro.update()
                self.tela_cadastro.draw(screen)
                
                if prox_tela == "login":
                    if self.tela_cadastro.message_color == SUCCESS_GREEN:
                         self.tela_login.message = "Cadastro feito! Entre no Reino."
                         self.tela_login.message_color = SUCCESS_GREEN
                    else:
                         self.tela_login.message = ""
                    self.tela_atual = prox_tela
                
            elif self.tela_atual == "game" and self.tela_jogo:
                prox_tela = self.tela_jogo.handle_events(eventos)
                self.tela_jogo.update()
                self.tela_jogo.draw(screen)
                
                if prox_tela == "login":
                    self.tela_atual = prox_tela
                    self.jogador_logado = None
                    self.tela_jogo = None

            pygame.display.flip()
            CLOCK.tick(FPS)

        self.gerenciador.close()

if __name__ == "__main__":
    sistema = SistemaLogin()
    sistema.executar()
    pygame.quit()
    sys.exit()