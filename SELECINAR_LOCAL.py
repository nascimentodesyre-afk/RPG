import pygame
import sys
import math

pygame.init()

# --------------------
# CONFIGURAÇÕES GERAIS
# --------------------
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Seletor de Local - Reinos de Eldoria")

# CORES APERFEIÇOADAS
AZUL_FUNDO = (26, 36, 47)
AZUL_FUNDO_ESCURO = (20, 28, 36)
DOURADO_CLARO = (212, 175, 55)
DOURADO_ESCURO = (184, 134, 11)
DOURADO_BRILLHANTE = (255, 215, 0)
CREME = (248, 240, 220)
CREME_ESCURO = (230, 215, 185)
MARROM_ESCURO = (40, 25, 15)
VERMELHO_ESCURO = (120, 30, 30)
VERDE_BOTAO = (50, 120, 60)
VERDE_BOTAO_HOVER = (70, 150, 80)
BRONZE = (140, 120, 83)

# FONTES
try:
    titulo_font = pygame.font.SysFont("timesnewroman", 72, bold=True)
    sub_font = pygame.font.SysFont("timesnewroman", 32, bold=True)
    desc_font = pygame.font.SysFont("timesnewroman", 22)
    botao_font = pygame.font.SysFont("timesnewroman", 28, bold=True)
except:
    titulo_font = pygame.font.Font(None, 72)
    sub_font = pygame.font.Font(None, 32)
    desc_font = pygame.font.Font(None, 22)
    botao_font = pygame.font.Font(None, 28)

# EFEITOS VISUAIS
class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_particles(self, x, y, color, count=5):
        for _ in range(count):
            self.particles.append({
                'x': x, 'y': y,
                'vx': (pygame.time.get_ticks() % 3 - 1) * 0.5,
                'vy': (pygame.time.get_ticks() % 3 - 1) * 0.5,
                'color': color,
                'life': 30
            })
    
    def update(self):
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        for particle in self.particles:
            alpha = min(255, particle['life'] * 8)
            color = particle['color']
            pygame.draw.circle(surface, color, (int(particle['x']), int(particle['y'])), 2)

# SISTEMA DE PARTÍCULAS
particles = ParticleSystem()

# LOCAIS DETALHADOS
locais = [
    {
        "titulo": "Floresta de Elden",
        "descricao": "Um vasto bosque encantado onde espíritos antigos guardam segredos milenares. As árvores sussurram lendas esquecidas.",
        "detalhes": "Nível de Perigo: Moderado\nRecursos: Ervas raras, Madeira encantada",
        "cor_destaque": (34, 139, 34),
        "imagem": None
    },
    {
        "titulo": "Vila de Norhaven",
        "descricao": "Um pacato vilarejo medieval, conhecido por seu mercado de relíquias mágicas e tavernas aconchegantes.",
        "detalhes": "Nível de Perigo: Baixo\nRecursos: Comércio, Informações",
        "cor_destaque": (139, 69, 19),
        "imagem": None
    },
    {
        "titulo": "Ruínas de Thalor",
        "descricao": "Restos de um antigo império, agora tomado por sombras e ecos do passado. Tesouros aguardam os corajosos.",
        "detalhes": "Nível de Perigo: Alto\nRecursos: Artefatos antigos, Conhecimento perdido",
        "cor_destaque": (128, 128, 128),
        "imagem": None
    },
    {
        "titulo": "Fortaleza de Aegir",
        "descricao": "Uma imponente fortaleza erguida nas montanhas, lar dos guerreiros do norte e bastião contra invasores.",
        "detalhes": "Nível de Perigo: Moderado\nRecursos: Treinamento, Proteção",
        "cor_destaque": (70, 130, 180),
        "imagem": None
    },
    {
        "titulo": "Pântano das Almas",
        "descricao": "Lamasal traiçoeiro onde névoas eternas escondem criaturas ancestrais e mistérios profundos.",
        "detalhes": "Nível de Perigo: Extremo\nRecursos: Poções raras, Segredos ocultos",
        "cor_destaque": (47, 79, 79),
        "imagem": None
    }
]

# --------------------
# FUNÇÕES APERFEIÇOADAS
# --------------------

def desenhar_fundo_decorativo():
    # Gradiente de fundo
    for y in range(SCREEN_HEIGHT):
        alpha = y / SCREEN_HEIGHT
        cor = (
            int(AZUL_FUNDO[0] * (1 - alpha) + AZUL_FUNDO_ESCURO[0] * alpha),
            int(AZUL_FUNDO[1] * (1 - alpha) + AZUL_FUNDO_ESCURO[1] * alpha),
            int(AZUL_FUNDO[2] * (1 - alpha) + AZUL_FUNDO_ESCURO[2] * alpha)
        )
        pygame.draw.line(screen, cor, (0, y), (SCREEN_WIDTH, y))
    
    # Estrelas cintilantes (CORRIGIDO)
    tempo = pygame.time.get_ticks() / 1000
    for i in range(30):  # Reduzido para melhor performance
        x = (i * 137) % SCREEN_WIDTH
        y = (i * 89) % 200
        brilho = int((math.sin(tempo * 2 + i) + 1) * 100 + 100)
        brilho = max(50, min(255, brilho))  # Garantir que está entre 50-255
        pygame.draw.circle(screen, (brilho, brilho, brilho), (int(x), int(y)), 1)

def desenhar_borda_medieval():
    # Bordas ornamentadas
    pygame.draw.rect(screen, DOURADO_ESCURO, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 8)
    
    # Cantos decorados
    raio = 15
    pontos = [
        (raio, 0), (SCREEN_WIDTH - raio, 0), 
        (SCREEN_WIDTH, raio), (SCREEN_WIDTH, SCREEN_HEIGHT - raio), 
        (SCREEN_WIDTH - raio, SCREEN_HEIGHT), (raio, SCREEN_HEIGHT), 
        (0, SCREEN_HEIGHT - raio), (0, raio)
    ]
    pygame.draw.lines(screen, DOURADO_CLARO, True, pontos, 4)

def desenhar_cartao(local, x, y, largura, altura, selecionado=False, hover=False):
    # Sombra
    if selecionado:
        shadow_surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 50))
        screen.blit(shadow_surf, (x + 8, y + 8))
    
    # Fundo do cartão com gradiente
    cor_base = local["cor_destaque"]
    for i in range(altura):
        alpha = i / altura
        cor = (
            int(cor_base[0] * 0.3 + CREME[0] * 0.7),
            int(cor_base[1] * 0.3 + CREME[1] * 0.7),
            int(cor_base[2] * 0.3 + CREME[2] * 0.7)
        )
        pygame.draw.line(screen, cor, (x, y + i), (x + largura, y + i))
    
    # Borda destacada para selecionado/hover
    cor_borda = DOURADO_BRILLHANTE if selecionado else (DOURADO_CLARO if hover else BRONZE)
    espessura_borda = 4 if selecionado else (3 if hover else 2)
    
    pygame.draw.rect(screen, cor_borda, (x, y, largura, altura), espessura_borda, border_radius=12)
    
    # Título com sombra
    titulo_texto = sub_font.render(local["titulo"], True, MARROM_ESCURO)
    titulo_sombra = sub_font.render(local["titulo"], True, (0, 0, 0))
    screen.blit(titulo_sombra, (x + 22, y + 22))
    screen.blit(titulo_texto, (x + 20, y + 20))

    # Área da imagem
    img_rect = pygame.Rect(x + 15, y + 60, largura - 30, 120)
    pygame.draw.rect(screen, local["cor_destaque"], img_rect, border_radius=8)
    pygame.draw.rect(screen, MARROM_ESCURO, img_rect, 2, border_radius=8)
    
    # Ícone representativo
    if selecionado:
        pygame.draw.polygon(screen, DOURADO_CLARO, [
            (x + largura//2, y + 90),
            (x + largura//2 - 20, y + 130),
            (x + largura//2 + 20, y + 130)
        ])

    # Descrição
    descricao = quebrar_texto(local["descricao"], desc_font, largura - 40)
    offset_y = 190
    for linha in descricao:
        texto = desc_font.render(linha, True, MARROM_ESCURO)
        screen.blit(texto, (x + 20, y + offset_y))
        offset_y += 22

    # Detalhes (apenas para selecionado)
    if selecionado:
        detalhes = quebrar_texto(local["detalhes"], desc_font, largura - 40)
        offset_y += 10
        pygame.draw.line(screen, BRONZE, (x + 20, y + offset_y), (x + largura - 20, y + offset_y), 1)
        offset_y += 15
        for linha in detalhes:
            texto = desc_font.render(linha, True, VERMELHO_ESCURO)
            screen.blit(texto, (x + 20, y + offset_y))
            offset_y += 20

def desenhar_botao_start(hover=False):
    x, y = SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100
    largura, altura = 240, 60
    
    # Sombra
    shadow_surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
    shadow_surf.fill((0, 0, 0, 50))
    screen.blit(shadow_surf, (x + 5, y + 5))
    
    # Gradiente do botão
    cor_base = VERDE_BOTAO_HOVER if hover else VERDE_BOTAO
    for i in range(altura):
        alpha = i / altura
        cor = (
            int(cor_base[0] * (1 - alpha) + DOURADO_CLARO[0] * alpha),
            int(cor_base[1] * (1 - alpha) + DOURADO_CLARO[1] * alpha),
            int(cor_base[2] * (1 - alpha) + DOURADO_CLARO[2] * alpha)
        )
        pygame.draw.line(screen, cor, (x, y + i), (x + largura, y + i))
    
    # Borda
    cor_borda = DOURADO_BRILLHANTE if hover else DOURADO_CLARO
    pygame.draw.rect(screen, cor_borda, (x, y, largura, altura), 3, border_radius=15)
    
    # Texto
    texto = botao_font.render("ENTRAR NO LOCAL", True, CREME)
    sombra = botao_font.render("ENTRAR NO LOCAL", True, MARROM_ESCURO)
    screen.blit(sombra, (SCREEN_WIDTH // 2 - texto.get_width() // 2 + 2, y + 22))
    screen.blit(texto, (SCREEN_WIDTH // 2 - texto.get_width() // 2, y + 20))
    
    return pygame.Rect(x, y, largura, altura)

def desenhar_seta_navegacao(x, y, direita=False, ativa=True):
    cor = DOURADO_BRILLHANTE if ativa else BRONZE
    pontos = []
    
    if direita:
        pontos = [(x, y), (x - 30, y - 20), (x - 30, y + 20)]
    else:
        pontos = [(x, y), (x + 30, y - 20), (x + 30, y + 20)]
    
    pygame.draw.polygon(screen, cor, pontos)
    
    # Brilho para setas ativas
    if ativa:
        pygame.draw.polygon(screen, DOURADO_CLARO, pontos, 2)
    
    return pygame.Rect(min(p[0] for p in pontos), y - 20, 30, 40)

def quebrar_texto(texto, fonte, largura_max):
    palavras = texto.split(' ')
    linhas = []
    atual = ""
    for palavra in palavras:
        teste = atual + palavra + " "
        if fonte.size(teste)[0] < largura_max:
            atual = teste
        else:
            linhas.append(atual.strip())
            atual = palavra + " "
    if atual.strip():
        linhas.append(atual.strip())
    return linhas

def desenhar_interface(indice, mouse_pos):
    screen.fill(AZUL_FUNDO)
    
    # Elementos decorativos de fundo
    desenhar_fundo_decorativo()
    
    # Título principal com efeito
    titulo_texto = titulo_font.render("SELETOR DE LOCAL", True, DOURADO_CLARO)
    titulo_sombra = titulo_font.render("SELETOR DE LOCAL", True, MARROM_ESCURO)
    
    screen.blit(titulo_sombra, (SCREEN_WIDTH // 2 - titulo_texto.get_width() // 2 + 3, 53))
    screen.blit(titulo_texto, (SCREEN_WIDTH // 2 - titulo_texto.get_width() // 2, 50))
    
    # Subtítulo
    subtitulo = desc_font.render("Escolha seu destino nos Reinos de Eldoria", True, CREME)
    screen.blit(subtitulo, (SCREEN_WIDTH // 2 - subtitulo.get_width() // 2, 120))
    
    # Cartões com navegação horizontal
    cartao_largura = 280
    cartao_altura = 380
    espacamento = 50
    total_largura = len(locais) * (cartao_largura + espacamento) - espacamento
    start_x = (SCREEN_WIDTH - total_largura) // 2
    
    # Calcular posição base para efeito de parallax suave
    offset_base = -indice * (cartao_largura + espacamento)
    
    retangulos_cartoes = []
    for i, local in enumerate(locais):
        x = start_x + i * (cartao_largura + espacamento) + offset_base
        y = 180
        
        # Efeito de elevação para cartão selecionado
        if i == indice:
            y -= 10
        
        hover = pygame.Rect(x, y, cartao_largura, cartao_altura).collidepoint(mouse_pos)
        desenhar_cartao(local, x, y, cartao_largura, cartao_altura, i == indice, hover)
        retangulos_cartoes.append((pygame.Rect(x, y, cartao_largura, cartao_altura), i))
    
    # Setas de navegação
    seta_esquerda = desenhar_seta_navegacao(80, 370, False, indice > 0)
    seta_direita = desenhar_seta_navegacao(SCREEN_WIDTH - 80, 370, True, indice < len(locais) - 1)
    
    # Indicador de posição
    indicador_y = 580
    for i in range(len(locais)):
        cor = DOURADO_BRILLHANTE if i == indice else BRONZE
        raio = 8 if i == indice else 5
        pygame.draw.circle(screen, cor, (SCREEN_WIDTH // 2 - (len(locais) - 1) * 10 + i * 20, indicador_y), raio)
    
    # Botão START
    botao_start_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 100, 240, 60)
    botao_start = desenhar_botao_start(botao_start_rect.collidepoint(mouse_pos))
    
    # Bordas decorativas
    desenhar_borda_medieval()
    
    # Atualizar e desenhar partículas
    particles.update()
    particles.draw(screen)
    
    return retangulos_cartoes, seta_esquerda, seta_direita, botao_start

# --------------------
# LOOP PRINCIPAL APERFEIÇOADO
# --------------------
indice_local = 0
rodando = True
ultimo_clique = 0

while rodando:
    mouse_pos = pygame.mouse.get_pos()
    tempo_atual = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT and indice_local < len(locais) - 1:
                indice_local += 1
                particles.add_particles(SCREEN_WIDTH - 80, 370, DOURADO_BRILLHANTE)
            
            elif event.key == pygame.K_LEFT and indice_local > 0:
                indice_local -= 1
                particles.add_particles(80, 370, DOURADO_BRILLHANTE)
            
            elif event.key == pygame.K_RETURN:
                if tempo_atual - ultimo_clique > 500:  # Prevenir clique rápido
                    print(f"🎮 Entrando em {locais[indice_local]['titulo']}...")
                    ultimo_clique = tempo_atual
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            retangulos_cartoes, seta_esquerda, seta_direita, botao_start = desenhar_interface(indice_local, mouse_pos)
            
            if seta_esquerda.collidepoint(mouse_pos) and indice_local > 0:
                indice_local -= 1
                particles.add_particles(80, 370, DOURADO_BRILLHANTE, 10)
            
            elif seta_direita.collidepoint(mouse_pos) and indice_local < len(locais) - 1:
                indice_local += 1
                particles.add_particles(SCREEN_WIDTH - 80, 370, DOURADO_BRILLHANTE, 10)
            
            elif botao_start.collidepoint(mouse_pos):
                if tempo_atual - ultimo_clique > 500:
                    print(f"🎮 Entrando em {locais[indice_local]['titulo']}...")
                    ultimo_clique = tempo_atual
            
            # Clique direto nos cartões
            for rect, indice in retangulos_cartoes:
                if rect.collidepoint(mouse_pos) and indice != indice_local:
                    indice_local = indice
                    particles.add_particles(rect.centerx, rect.centery, locais[indice]["cor_destaque"], 15)
    
    # Efeitos de hover contínuos
    if tempo_atual % 2000 < 1000 and indice_local < len(locais):
        particles.add_particles(
            SCREEN_WIDTH // 2, 
            200, 
            locais[indice_local]["cor_destaque"], 
            1
        )
    
    # Desenhar interface
    desenhar_interface(indice_local, mouse_pos)
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()