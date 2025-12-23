import pgzrun
import random
import pygame 
from pygame import Rect

# Configurações da Tela
LARGURA = 800
ALTURA = 600
TITULO = "Gameboy Adventure"

# Variáveis Globais 
estado_jogo = 'menu'
som_ligado = True
gravidade = 1

# --- Classes ---
class Entidade(Actor):
    def __init__(self, lista_img_parado, lista_img_movendo, x, y):
        super().__init__(lista_img_parado[0], (x, y))
        self.quadros_parado = lista_img_parado
        self.quadros_movendo = lista_img_movendo
        self.temporizador_quadro = 0
        self.velocidade_animacao = 0.2
        self.dx = 0
        self.dy = 0
        self.olhando_direita = True

    def animar(self, esta_movendo):
        self.temporizador_quadro += self.velocidade_animacao
        quadros = self.quadros_movendo if esta_movendo else self.quadros_parado
        indice = int(self.temporizador_quadro) % len(quadros)
        nome_imagem = quadros[indice]
        self.image = nome_imagem

class Jogador(Entidade):
    def __init__(self):
        super().__init__(
            ['gameboy_parado_1', 'gameboy_parado_2'],
            ['gameboy_correndo_1', 'gameboy_correndo_2'],
            50, 450
        )
        self.forca_pulo = -22 
        self.no_chao = False

    def atualizar_jogador(self, plataformas):
        esta_movendo = False
        if keyboard.left:
            self.dx = -5
            self.olhando_direita = False
            esta_movendo = True
        elif keyboard.right:
            self.dx = 5
            self.olhando_direita = True
            esta_movendo = True
        else:
            self.dx = 0

        if keyboard.up and self.no_chao:
            self.pular()

        self.dy += gravidade
        
        # Movimento Eixo X
        self.x += self.dx
        self.verificar_colisao(plataformas, True)
        
        # Movimento Eixo Y
        self.y += self.dy
        self.verificar_colisao(plataformas, False)

        self.animar(esta_movendo)

        # Limite de queda
        if self.y > ALTURA + 100:
            self.morrer()

    def pular(self):
        self.dy = self.forca_pulo
        self.no_chao = False
        if som_ligado:
            try: sounds.pulo.play()
            except: pass

    def morrer(self):
        # Reinicia posição
        self.pos = (50, 450)
        self.dy = 0
        
    def verificar_colisao(self, plataformas, checar_x):
        for parede in plataformas:
            if self.colliderect(parede):
                if checar_x:
                    if self.dx > 0: self.right = parede.left
                    if self.dx < 0: self.left = parede.right
                else:
                    if self.dy > 0: 
                        self.bottom = parede.top
                        self.dy = 0
                        self.no_chao = True
                    if self.dy < 0: 
                        self.top = parede.bottom
                        self.dy = 0

class Inimigo(Entidade):
    def __init__(self, x, y, limite_esq, limite_dir):
        super().__init__(['inimigo_1', 'inimigo_2'], ['inimigo_1', 'inimigo_2'], x, y)
        self.dx = 2
        self.limite_esq = limite_esq
        self.limite_dir = limite_dir
        self.tamanho_alvo = (60, 60) 

    def animar(self, esta_movendo):
        super().animar(esta_movendo)
        
        self._surf = pygame.transform.scale(self._surf, self.tamanho_alvo)
        self._update_pos()

    def atualizar_inimigo(self):
        self.x += self.dx
        if self.x > self.limite_dir:
            self.dx = -2
            self.olhando_direita = False
        if self.x < self.limite_esq:
            self.dx = 2
            self.olhando_direita = True
        
        self.animar(True)

# --- Setup do Jogo ---
gameboy = Jogador()
plataformas = []

# Chão
bloco_ref = Actor('chao')
largura_bloco = bloco_ref.width
for i in range(0, LARGURA + largura_bloco, largura_bloco):
    p = Actor('chao', bottomleft=(i, ALTURA))
    plataformas.append(p)

# Plataforma
plataformas.append(Actor('chao', topleft=(250, 420)))
plataformas.append(Actor('chao', topleft=(450, 320)))
plataformas.append(Actor('chao', topleft=(650, 220)))

# inimigos
inimigos = [
    Inimigo(400, 500, 300, 600),
    Inimigo(480, 250, 460, 500)
]

# Botões
botao_iniciar = Rect(LARGURA//2 - 100, 200, 200, 50)
botao_som = Rect(LARGURA//2 - 100, 270, 200, 50)
botao_sair = Rect(LARGURA//2 - 100, 340, 200, 50)

# --- Funções PgZero ---
def draw():
    screen.clear()
    screen.fill((100, 200, 255)) 
    
    if estado_jogo == 'menu':
        screen.draw.text("AVENTURA DO GAMEBOY", center=(LARGURA//2, 100), fontsize=60, color="white", shadow=(1,1), scolor="black")
        screen.draw.filled_rect(botao_iniciar, "blue")
        screen.draw.text("Jogar", center=botao_iniciar.center, fontsize=30)
        cor_som = "green" if som_ligado else "red"
        screen.draw.filled_rect(botao_som, cor_som)
        texto_som = f"Som: {'Ligado' if som_ligado else 'Desligado'}"
        screen.draw.text(texto_som, center=botao_som.center, fontsize=30)
        screen.draw.filled_rect(botao_sair, "gray")
        screen.draw.text("Sair", center=botao_sair.center, fontsize=30)

    elif estado_jogo == 'jogando':
        for p in plataformas:
            p.draw()
        for inimigo in inimigos:
            inimigo.draw()
        gameboy.draw()
        screen.draw.text("Setas para Mover | Pule na cabeca para matar", (10, 10), fontsize=20, color="black")
        
        # Mensagem de vitoria
        if not inimigos:
            screen.draw.text("VOCE VENCEU!", center=(LARGURA//2, ALTURA//2), fontsize=80, color="gold", shadow=(2,2), scolor="black")

def update():
    global estado_jogo
    if estado_jogo == 'jogando':
        if som_ligado:
            try:
                if not music.is_playing('tema'): music.play('tema')
            except: pass
        else:
            music.stop()

        gameboy.atualizar_jogador(plataformas)
        
        # --- Lógica de Combate ---
        for inimigo in inimigos[:]:
            inimigo.atualizar_inimigo()
            
            if gameboy.colliderect(inimigo):
                
                pegou_por_cima = gameboy.dy > 0 and gameboy.bottom < inimigo.bottom - 10
                
                if pegou_por_cima:
                    inimigos.remove(inimigo) 
                    gameboy.dy = -15         
                    if som_ligado:
                        try: sounds.pulo.play() 
                        except: pass
                else:
                    gameboy.morrer() 

def on_mouse_down(pos):
    global estado_jogo, som_ligado
    if estado_jogo == 'menu':
        if botao_iniciar.collidepoint(pos):
            estado_jogo = 'jogando'
        elif botao_som.collidepoint(pos):
            som_ligado = not som_ligado
        elif botao_sair.collidepoint(pos):
            exit()

pgzrun.go()