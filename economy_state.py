# economy_state.py
import random
import collections

class EstadoEconomia:
    def __init__(self, cenario_inicial=None):
        self.mes_atual = 1
        self.ano_atual = 2024
        
        tipos_governo_possiveis = ["Liberal", "Desenvolvimentista", "Pragmatico"]
        self.tipo_governo = random.choice(tipos_governo_possiveis)
        self.tipo_ministro_fazenda = self.tipo_governo

        if self.tipo_governo == "Liberal":
            self.meta_inflacao_anual = round(random.uniform(2.5, 3.0), 1)
            self.banda_inflacao_anual = round(random.uniform(0.75, 1.25), 2)
            self.meta_pib_anual = round(random.uniform(1.8, 2.5), 1)
            self.banda_pib_anual = round(random.uniform(0.75, 1.25), 2)
        elif self.tipo_governo == "Desenvolvimentista":
            self.meta_inflacao_anual = round(random.uniform(3.5, 4.5), 1)
            self.banda_inflacao_anual = round(random.uniform(1.25, 1.75), 2)
            self.meta_pib_anual = round(random.uniform(3.0, 4.5), 1)
            self.banda_pib_anual = round(random.uniform(1.0, 1.75), 2)
        else: # Pragmatico (ou Default)
            self.meta_inflacao_anual = round(random.uniform(3.0, 3.5), 1)
            self.banda_inflacao_anual = round(random.uniform(1.0, 1.5), 2)
            self.meta_pib_anual = round(random.uniform(2.2, 3.0), 1)
            self.banda_pib_anual = round(random.uniform(0.75, 1.25), 2)
        
        self.banda_inflacao_original = self.banda_inflacao_anual

        inflacao_anual_inicial_base = self.meta_inflacao_anual + random.uniform(-1.5, 2.5)
        self.inflacao_atual_mensal = round(max(1.0, min(10.0, inflacao_anual_inicial_base)) / 12, 6)

        pib_anual_inicial_base = self.meta_pib_anual + random.uniform(-2.0, 1.0)
        self.pib_crescimento_atual_mensal = round(max(-3.0, min(5.0, pib_anual_inicial_base)) / 12, 6)

        premio_selic_sobre_inflacao_atual = random.uniform(1.0, 4.0)
        selic_calculada = (self.inflacao_atual_mensal * 12) + premio_selic_sobre_inflacao_atual
        self.selic_anual = round(max(2.0, min(20.0, selic_calculada)) * 4) / 4
        self.selic_anterior_anual = self.selic_anual

        self.expectativa_inflacao_mercado_mensal = (self.inflacao_atual_mensal * 0.6) + ((self.meta_inflacao_anual / 12) * 0.4) + random.uniform(-0.1/12, 0.15/12)
        self.expectativa_inflacao_mercado_mensal = max(0.5/12, self.expectativa_inflacao_mercado_mensal)

        self.expectativa_juros_longo_prazo_anual = self.selic_anual + random.uniform(0.1, 1.5)
        self.expectativa_juros_longo_prazo_anual = round(self.expectativa_juros_longo_prazo_anual, 2)

        self.credibilidade_bc = random.randint(45, 75)
        self.pressao_politica = random.randint(20, 55)

        self.cambio_atual = random.uniform(4.70, 5.70)
        self.taxa_desemprego_atual = random.uniform(6.0, 12.0)

        self.taxa_deposito_compulsorio = round(random.uniform(0.18, 0.28), 2)
        self.cooldown_deposito_compulsorio = 0

        self.fator_liquidez_bancaria = 1.0
        self.alvo_fator_liquidez_bancaria = 1.0

        self.mudancas_selic_este_mes = 0
        self.eventos_consecutivos = 0
        self.meses_sem_evento_forçado = 0
        self.evento_ocorrido_este_mes = False
        self.meses_apos_evento_negativo_grande = 0

        self.cooldown_comunicado_meta = 0
        self.cooldown_discurso_publico = 0
        self.cooldown_reuniao_fechada = 0
        self.cooldown_flexibilizar_meta = 0
        self.meses_banda_flexibilizada = 0

        self.historico_noticias = [] 
        self.historico_inflacao = []
        self.historico_pib = []
        self.historico_credibilidade = []
        self.historico_pressao_politica = []
        self.historico_selic = []
        self.historico_cambio = []
        self.historico_desemprego = []
        self.historico_expectativa_inflacao = []
        self.historico_juros_longo_prazo = []
        self.historico_compulsorio = []
        self.historico_ultimas_selic_mudancas = []
        self.historico_divida_pib = []
        self.historico_reservas_internacionais = []

        self.meses_inflacao_fora_meta = 0
        self.meses_pib_fora_meta = 0
        self.meses_desemprego_alto = 0

        self.tolerancia_pressao_politica = 75
        self.tolerancia_credibilidade_mercado = 35

        self.activity_log = collections.deque(maxlen=30)

        self.mandato_anos = 4
        self.anos_restantes_mandato = self.mandato_anos
        self.mandate_goals = {
            "reduzir_desemprego": False,
            "estabilidade_cambial": False,
            "aumentar_investimento": False
        }
        self.consecutive_stable_currency_months = 0
        self.consecutive_low_unemployment_months = 0

        self.cambio_crise_limiar = 6.80
        self.cambio_crise_meses = 3
        self.cambio_crise_contador = 0

        self.divida_publica_pib = random.uniform(50.0, 70.0)
        self.governo_postura_fiscal = "neutra"
        self.ultimo_anuncio_fiscal_valor = 0.0
        self.mes_ultimo_anuncio_fiscal = 0
        self.cooldown_reuniao_ministro = 0
        self.cooldown_anuncio_fiscal_governo = 0
        
        self.governo_postura_fiscal_influencia = None 
        self.influencia_duracao = 0
        
        self.reservas_internacionais = round(random.uniform(280.0, 420.0), 1)
        self.cooldown_intervencao_cambial = 0
        self.intervencao_cambial_este_mes_tipo = None 
        self.intervencao_cambial_este_mes_magnitude = 0.0

        self.alvo_inflacao_mensal = self.inflacao_atual_mensal
        self.alvo_pib_crescimento_mensal = self.pib_crescimento_atual_mensal
        self.alvo_cambio_atual = self.cambio_atual
        self.alvo_credibilidade_bc = self.credibilidade_bc
        self.alvo_pressao_politica = self.pressao_politica
        
        # --- NOVO ATRIBUTO PARA A IA DIRETORA ---
        self.historico_acoes = collections.deque(maxlen=12)

    def add_log_entry(self, message, color=(255,255,255)):
        if self.activity_log and \
           self.activity_log[-1]["month"] == self.mes_atual and \
           self.activity_log[-1]["year"] == self.ano_atual:
            self.activity_log[-1]["messages"].append({"text": message, "color": color})
        else:
            self.activity_log.append({
                "month": self.mes_atual,
                "year": self.ano_atual,
                "messages": [{"text": message, "color": color}]
            })
        self.alvo_credibilidade_bc = self.credibilidade_bc
        self.alvo_pressao_politica = self.pressao_politica
        
        self.historico_acoes = collections.deque(maxlen=12)

        # --- NOVO ATRIBUTO PARA A IA DIRETORA ---
        self.meses_sem_acao_significativa = 0