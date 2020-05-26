#!/usr/bin/env python
# coding: utf-8

# # Q-Learn para o mundo de grades

# ### Preparando a estrutura do mundo das grades

# **Parâmetros para desenhar o mundo de grades**

# In[1]:


from tkinter import *

master = None
size = 100
player = (0, 1)
max_x = 3
max_y = 2
final = (2,0)
restart = False
board = None
me = None
r = 30
arrow_ids = []


# **Função para desenhar o tabuleiro**

# In[2]:


def create_board():
    global board, me, master, r
    
    # Cria a janela
    master = Tk()
    board = Canvas(master, width=3*size, height=2*size) 

    # Desenha as grades
    for row in range(max_x):
        for column in range(max_y):
            board.create_rectangle(row*size, column*size, (row+1)*size, (column+1)*size, fill="white", width=1)  

    # Desenha o objetivo em verde            
    board.create_rectangle(final[0]*size, final[1]*size, (final[0]+1)*size, (final[1]+1)*size, fill="green", width=1)

    # Define as coordenadas iniciais do agente
    x0 = player[0]*size + size / 2 - r
    y0 = player[1]*size + size / 2 - r
    x1 = player[0]*size + size / 2 + r
    y1 = player[1]*size + size / 2 + r

    # Desenha o agente no tabuleiro
    me = board.create_oval(x0, y0, x1, y1, fill="red", width=1)    


# **Função para movimentar o agente no tabuleiro**

# In[3]:


def move(dx, dy): # Recebe delta X e delta Y
    global player, me, restart, board
    
    # Atualiza as coordenadas temporárias do agente
    new_x = player[0] + dx
    new_y = player[1] + dy
    score = 0 # Define o score inicialmente como zero
    
    # Verifica se a nova posição do agente é válida
    if new_x >= 0 and new_y >= 0 and new_x < max_x and new_y < max_y:
        x0 = new_x*size + size / 2 - r
        y0 = new_y*size + size / 2 - r
        x1 = new_x*size + size / 2 + r
        y1 = new_y*size + size / 2 + r

        board.coords(me, x0, y0, x1, y1)
        player = (new_x, new_y)
    else: # Caso não seja, score será -1
        score = -1
        
    # Caso a nova posição do agente seja o estado final
    if (new_x, new_y) == final:
        score = 1 # Score será +1
        restart = True # Flag para reiniciar a posição do agente
    
    return score # Retorna o valor de score

# Função que inicia o tkinter
def begin():
    global master, board
    create_board()
    board.grid(row=0, column=0)
    master.mainloop()


# **Funções para movimentar o agente no mundo**

# In[4]:


def move_up(event=None):
    return move(0, -1)

def move_down(event=None):
    return move(0, 1)

def move_left(event=None):
    return move(-1, 0)

def move_right(event=None):
    return move(1, 0)


# ### Q-Learning

# **Parâmetros**

# In[5]:


Q = {}
actions = [move_up, move_down, move_left, move_right]
alpha = 1
gamma = 0.9
score = 1
t = 1

from enum import Enum

class Return(Enum):
    ACTION = 0
    VALUE = 1


# **Função Q***

# In[6]:


def Q_optimum(state, return_type):
    global Q
    # Pega as possíveis ações para o estado recebido
    action_values = Q[state] 
    
    # Inicializa o maior valor e a melhor ação
    max_value = None
    best_action = None
    
    # Itera sobre as ações e escolhe a melhor
    for action, action_value in enumerate(action_values):
        if max_value is None or action_value > max_value:
            max_value = action_value
            best_action = action
            
    # Caso o return_type seja Action, retorna a melhor ação    
    if return_type == Return.ACTION:
        return best_action
    # Caso o return_type seja Value, retorna o valor da melhor ação
    elif return_type == Return.VALUE:
        return max_value
    else: # Caso contrário, lança uma exceção
        raise ValueError('Parameter return_type is not defined')


# **Função para atualizar a matriz Q**

# In[7]:


def update_Q(state, new_state, action, reward):
    Q[state][action] = (1-alpha)*Q_optimum(state, Return.VALUE) + alpha*(reward + gamma*Q_optimum(new_state, Return.VALUE))


# **Função para executar uma ação**

# In[8]:


def execute(action):
    # Executando a ação recebida
    reward = actions[action]()
    new_state = player
    
    return new_state, reward


# **Função para inicializar a matriz Q**

# In[9]:


def initialize_Q():
    for x in range(max_x):
        for y in range(max_y):
            Q[(x,y)] = [0.1 for _ in range(len(actions))]


# **Função para desenhar a política no tabuleiro**

# In[10]:


def draw_arrows():
    global board, Q, arrow_ids
    policy = {}
    
    arrows = {
        0: (50,70,50,30), # up
        1: (50,30,50,70), # down
        2: (70,50,30,50), # left
        3: (30,50,70,50)  # right
    }
    
    # Itera sobre todos os estados
    for state, actions in Q.items():
        best_actions = {}
        best_index = None
        
        # Encontra a(s) melhor(es) ações para cada estado
        for index, action in enumerate(actions):
            if len(best_actions) == 0 or action > best_actions[best_index]:
                best_index = index
                best_actions = {}
                best_actions[index] = action
            elif action == best_actions[best_index]:
                best_actions[index] = action
        
        policy[state] = best_actions
        
        # Para cada melhor ação, desenha uma seta indicando a direção
        for action in best_actions:
            if state == final:
                continue
            x0,y0,x1,y1 = arrows[action]
            arrow_id = board.create_line(x0 + size * state[0], 
                                         y0 + size * state[1], 
                                         x1 + size * state[0],
                                         y1 + size * state[1], 
                                         arrow=LAST)
            arrow_ids.append(arrow_id)
    return policy # Retorna a política


# **Função principal**
# 
# Executa o algoritmo Q-Learning

# In[ ]:


import time 
import threading

def main():
    global player, Q, restart, r, me, board, arrow_ids
    
    # Faz a thread dormir por 1 segundo
    time.sleep(1)
    # Executa a função para inicializar Q
    initialize_Q()
    # Inicializa o estado atual com a posição do agente
    state = player
    # Laço sem condição de parada
    while True:
        # Define a melhor ação a ser executada para o estado atual
        action = Q_optimum(state, Return.ACTION)
        # Executa a ação no agente e recebe o novo estado e a recompensa pela ação
        new_state, reward = execute(action)
        # Atualiza a matriz Q com as informações do novo estado e da recompensa
        update_Q(state, new_state, action, reward)
        # Atualiza o estado atual
        state = new_state
        # Desenha a política no tabuleiro
        draw_arrows()
       
        # Se a flag de reinicio estiver ativa reinicia os parâmetros do programa
        if restart:
            time.sleep(.5)
            player = (0,1)
            state = player
            restart = False
            for arrow_id in arrow_ids:
                board.delete(arrow_id)
            arrow_ids = []
            x0 = player[0]*size + size / 2 - r
            y0 = player[1]*size + size / 2 - r
            x1 = player[0]*size + size / 2 + r
            y1 = player[1]*size + size / 2 + r
            board.coords(me, x0, y0, x1, y1)
            
        time.sleep(.2)
        
t = threading.Thread(target=main)
t.daemon = True
t.start()
begin()

