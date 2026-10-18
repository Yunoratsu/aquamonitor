"""
AquaMonitor - Controle de Níveis de Água
Autoria: Nicholas Vieira - Trabalho ETEC Tópico 10
Competência 4: Elaborar sistemas aplicando princípios e paradigmas de programação.

Requisitos da atividade atendidos:
  * Lista com os 5 níveis (situação, mensagem e cor)  -> NIVEIS
  * Biblioteca colorama importada e utilizada          -> exibir_terminal()
  * Função que define a cor conforme o nível           -> definir_cor()
  * Exibição da situação com a cor correspondente      -> GUI + terminal
  * Restauração do estilo padrão do terminal           -> Style.RESET_ALL
Extra: interface gráfica profissional com reservatório animado (tkinter).
"""

import math
import random
import tkinter as tk
from datetime import datetime

try:
    from colorama import Fore, Style, init
except ImportError:  # a GUI continua funcionando sem o colorama
    class _Vazio:
        def __getattr__(self, _):
            return ""
    Fore = Style = _Vazio()

    def init(*_, **__):
        pass

# --------------------------------------------------------------------------
# DADOS: lista com os cinco níveis, do mais baixo ao máximo
# --------------------------------------------------------------------------
NIVEIS = [
    {"nivel": 1, "situacao": "Muito baixo (crítico)", "cor": "#ff4d5e", "fill": 0.10,
     "mensagem": "CRÍTICO! Reservatório quase vazio. Acione o abastecimento imediatamente."},
    {"nivel": 2, "situacao": "Baixo", "cor": "#ffc83d", "fill": 0.30,
     "mensagem": "Atenção: nível baixo. Programe o reabastecimento."},
    {"nivel": 3, "situacao": "Médio", "cor": "#35d07f", "fill": 0.50,
     "mensagem": "Operação normal. Nível adequado de água."},
    {"nivel": 4, "situacao": "Alto", "cor": "#22d3ee", "fill": 0.70,
     "mensagem": "Nível alto. Reduza a entrada de água."},
    {"nivel": 5, "situacao": "Muito alto (alerta)", "cor": "#4f8cff", "fill": 0.90,
     "mensagem": "ALERTA! Risco de transbordamento. Feche a entrada de água."},
]

# --------------------------------------------------------------------------
# FUNÇÕES
# --------------------------------------------------------------------------
def definir_cor(nivel):
    """Retorna a cor colorama correspondente ao nível (1 a 5)."""
    cores = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE]
    return cores[nivel - 1]


def exibir_terminal(nivel):
    """Mostra a situação no terminal com a cor do nível e restaura o estilo."""
    n = NIVEIS[nivel - 1]
    print(f"{definir_cor(nivel)}{Style.BRIGHT}[NÍVEL {nivel}] {n['situacao']} - "
          f"{n['mensagem']}{Style.RESET_ALL}")


def simulacao_terminal():
    """Demonstração inicial no terminal passando pelos cinco níveis."""
    print(f"{Style.BRIGHT}=== AquaMonitor | Simulação no terminal ==={Style.RESET_ALL}")
    for item in NIVEIS:
        exibir_terminal(item["nivel"])
    print(Style.RESET_ALL, end="")


def mix(c1, c2, t):
    """Mistura duas cores hexadecimais (t = 0 -> c1, t = 1 -> c2)."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# --------------------------------------------------------------------------
# INTERFACE
# --------------------------------------------------------------------------
BG, PANEL, CARD, TEXT, MUTED = "#0b1020", "#121a30", "#18223e", "#e8ecf8", "#8a96b8"
TX0, TX1, TY0, TY1 = 60, 300, 50, 480  # geometria do reservatório


class AquaMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AquaMonitor - Controle de Níveis de Água")
        self.geometry("980x620")
        self.resizable(False, False)
        self.configure(bg=BG)

        self.nivel = 3
        self.fill = 0.0
        self.fase = 0.0
        self.cor_atual = NIVEIS[2]["cor"]
        self.bolhas = []
        self.auto = False
        self.botoes = []

        self._montar_ui()
        self.set_nivel(3, "Inicialização do sistema")
        self._animar()
        self.protocol("WM_DELETE_WINDOW", self._fechar)

    # ---------------- construção da interface ----------------
    def _botao(self, pai, texto, comando, **kw):
        b = tk.Label(pai, text=texto, bg=CARD, fg=TEXT, cursor="hand2",
                     font=("Segoe UI", 10, "bold"), pady=10, **kw)
        b.bind("<Button-1>", lambda e: comando())
        return b

    def _montar_ui(self):
        # reservatório (esquerda)
        esq = tk.Frame(self, bg=PANEL)
        esq.pack(side="left", fill="y", padx=(20, 10), pady=20)
        self.canvas = tk.Canvas(esq, width=360, height=540, bg=PANEL, highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)

        # painel de controle (direita)
        dir_ = tk.Frame(self, bg=BG)
        dir_.pack(side="left", fill="both", expand=True, padx=(10, 20), pady=20)

        tk.Label(dir_, text="AQUAMONITOR", bg=BG, fg=TEXT,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w")
        tk.Label(dir_, text="Sistema de monitoramento de reservatório de água",
                 bg=BG, fg=MUTED, font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 14))

        # cartão de status
        card = tk.Frame(dir_, bg=CARD)
        card.pack(fill="x")
        self.barra = tk.Frame(card, bg=self.cor_atual, width=8)
        self.barra.pack(side="left", fill="y")
        corpo = tk.Frame(card, bg=CARD)
        corpo.pack(side="left", fill="both", expand=True, padx=18, pady=14)
        tk.Label(corpo, text="STATUS ATUAL", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.lbl_nivel = tk.Label(corpo, bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold"))
        self.lbl_nivel.pack(anchor="w", pady=(4, 0))
        self.lbl_sit = tk.Label(corpo, bg=CARD, font=("Segoe UI", 26, "bold"))
        self.lbl_sit.pack(anchor="w")
        self.lbl_msg = tk.Label(corpo, bg=CARD, fg=TEXT, font=("Segoe UI", 11),
                                wraplength=480, justify="left")
        self.lbl_msg.pack(anchor="w", pady=(4, 0))

        # seletor de níveis
        tk.Label(dir_, text="SIMULAR NÍVEL DO RESERVATÓRIO", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(18, 6))
        linha = tk.Frame(dir_, bg=BG)
        linha.pack(fill="x")
        for i in range(1, 6):
            b = self._botao(linha, f"Nível {i}", lambda i=i: self.set_nivel(i, "Simulação manual"))
            b.pack(side="left", expand=True, fill="x", padx=(0 if i == 1 else 6, 0))
            self.botoes.append(b)

        self.btn_auto = self._botao(dir_, "Iniciar simulação automática", self._alternar_auto)
        self.btn_auto.pack(fill="x", pady=(10, 0))

        # registro de eventos
        tk.Label(dir_, text="REGISTRO DE EVENTOS", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(18, 6))
        self.log = tk.Text(dir_, height=8, bg=CARD, fg=TEXT, relief="flat", bd=0,
                           font=("Consolas", 10), padx=12, pady=10, state="disabled")
        self.log.pack(fill="both", expand=True)
        for item in NIVEIS:
            self.log.tag_configure(f"n{item['nivel']}", foreground=item["cor"])
        self.log.tag_configure("hora", foreground=MUTED)

        tk.Label(dir_, text="Desenvolvido por Nicholas Vieira  •  ETEC  •  Trabalho Tópico 10",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="e", pady=(10, 0))

    # ---------------- lógica ----------------
    def set_nivel(self, nivel, origem):
        self.nivel = nivel
        n = NIVEIS[nivel - 1]
        self.lbl_nivel.config(text=f"NÍVEL {nivel} DE 5")
        self.lbl_sit.config(text=n["situacao"])
        self.lbl_msg.config(text=n["mensagem"])
        for i, b in enumerate(self.botoes, 1):
            ativo = i == nivel
            b.config(bg=NIVEIS[i - 1]["cor"] if ativo else CARD, fg=BG if ativo else TEXT)
        self.log.config(state="normal")
        self.log.insert("end", datetime.now().strftime("%H:%M:%S  "), "hora")
        self.log.insert("end", f"Nível {nivel} - {n['situacao']}  ", f"n{nivel}")
        self.log.insert("end", f"({origem})\n", "hora")
        self.log.see("end")
        self.log.config(state="disabled")
        exibir_terminal(nivel)

    def _alternar_auto(self):
        self.auto = not self.auto
        self.btn_auto.config(text="Pausar simulação automática" if self.auto
                             else "Iniciar simulação automática")
        if self.auto:
            self._passo_auto()

    def _passo_auto(self):
        if not self.auto:
            return
        novo = min(5, max(1, self.nivel + random.choice([-1, 1])))
        if novo != self.nivel:
            self.set_nivel(novo, "Simulação automática")
        self.after(2500, self._passo_auto)

    # ---------------- animação ----------------
    def _animar(self):
        alvo = NIVEIS[self.nivel - 1]
        self.fill += (alvo["fill"] - self.fill) * 0.05
        self.fase += 0.12
        self.cor_atual = mix(self.cor_atual, alvo["cor"], 0.12)

        pulso = 0.0
        if self.nivel in (1, 5):  # níveis de alerta pulsam
            pulso = 0.35 * (0.5 + 0.5 * math.sin(self.fase * 0.8))
        cor_alerta = mix(self.cor_atual, BG, pulso)
        self.barra.config(bg=cor_alerta)
        self.lbl_sit.config(fg=cor_alerta)

        self._desenhar()
        self.after(33, self._animar)

    def _desenhar(self):
        c = self.canvas
        c.delete("all")
        altura = TY1 - TY0
        topo = TY1 - self.fill * altura

        c.create_rectangle(TX0, TY0, TX1, TY1, fill="#0d1428", outline="")

        if self.fill > 0.01:
            for cor, amp, deslocamento in ((mix(self.cor_atual, "#ffffff", 0.25), 7, 1.6),
                                           (self.cor_atual, 5, 0.0)):
                pts = []
                for x in range(TX0 + 2, TX1 - 1, 4):
                    pts += [x, topo + math.sin(x * 0.045 + self.fase + deslocamento) * amp]
                pts += [TX1 - 2, TY1 - 2, TX0 + 2, TY1 - 2]
                c.create_polygon(pts, fill=cor, outline="")

            if random.random() < 0.25:
                self.bolhas.append([random.randint(TX0 + 12, TX1 - 12), TY1 - 10,
                                    random.randint(2, 5), random.uniform(0.8, 2.2)])
            vivas = []
            for b in self.bolhas:
                b[1] -= b[3]
                if b[1] > topo + 8:
                    c.create_oval(b[0] - b[2], b[1] - b[2], b[0] + b[2], b[1] + b[2],
                                  outline=mix(self.cor_atual, "#ffffff", 0.6))
                    vivas.append(b)
            self.bolhas = vivas

        # estrutura do tanque e brilho de vidro
        c.create_rectangle(TX0, TY0, TX1, TY1, outline="#3b4a6b", width=3)
        c.create_line(TX0 + 14, TY0 + 14, TX0 + 14, TY1 - 14, fill="#2a3552", width=4)
        c.create_text((TX0 + TX1) / 2, (TY0 + TY1) / 2, text=f"{round(self.fill * 100)}%",
                      fill="#ffffff", font=("Segoe UI", 38, "bold"))
        c.create_text((TX0 + TX1) / 2, (TY0 + TY1) / 2 + 40, text="CAPACIDADE",
                      fill="#dfe6ff", font=("Segoe UI", 9, "bold"))

        # escala de níveis
        for item in NIVEIS:
            y = TY1 - item["fill"] * altura
            ativo = item["nivel"] == self.nivel
            c.create_line(TX1, y, TX1 + 12, y, fill=item["cor"], width=3 if ativo else 1)
            c.create_text(TX1 + 18, y, anchor="w", text=f"N{item['nivel']}",
                          fill=item["cor"] if ativo else MUTED,
                          font=("Segoe UI", 11 if ativo else 9, "bold"))

    def _fechar(self):
        print(Style.RESET_ALL, end="")  # restaura o estilo padrão do terminal
        self.destroy()


if __name__ == "__main__":
    init()
    simulacao_terminal()
    AquaMonitor().mainloop()
