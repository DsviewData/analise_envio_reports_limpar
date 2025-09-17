import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import logging
from typing import Dict, List, Tuple, Optional
import warnings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suprimir warnings desnecessários
warnings.filterwarnings('ignore')

# Imports condicionais para plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly não está disponível. Alguns gráficos podem não funcionar.")

# Configuração da página
st.set_page_config(
    page_title="Painel de Acompanhamento de Reports",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes
MESES_ANALISE = {7: 'Julho', 8: 'Agosto', 9: 'Setembro'}
ANO_ANALISE = 2025
COLUNAS_OBRIGATORIAS = ['RESPONSÁVEL', 'DATA']

# CSS customizado para estilização moderna
st.markdown("""
<style>
    /* Importar fontes do Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Reset e configurações globais */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Fonte global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header principal */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.1;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
        position: relative;
        z-index: 1;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
    }
    
    /* Alertas críticos */
    .alert-critical {
        background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
        border: 2px solid #ffc107;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(255, 193, 7, 0.2);
        position: relative;
    }
    
    .alert-success {
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
        border: 2px solid #4caf50;
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 8px 32px rgba(76, 175, 80, 0.2);
        position: relative;
    }
    
    .alert-critical::before {
        content: '🚨';
        position: absolute;
        top: -10px;
        left: 20px;
        background: #ffc107;
        padding: 8px 12px;
        border-radius: 50%;
        font-size: 1.2rem;
    }
    
    .alert-success::before {
        content: '✅';
        position: absolute;
        top: -10px;
        left: 20px;
        background: #4caf50;
        padding: 8px 12px;
        border-radius: 50%;
        font-size: 1.2rem;
    }
    
    .alert-critical h3, .alert-success h3 {
        margin-bottom: 1.5rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    .alert-critical h3 {
        color: #e65100;
    }
    
    .alert-success h3 {
        color: #2e7d32;
    }
    
    .alert-critical ul, .alert-success ul {
        margin: 1rem 0;
        padding-left: 1.5rem;
    }
    
    .alert-critical li {
        margin-bottom: 0.5rem;
        color: #bf360c;
        font-weight: 500;
    }
    
    .alert-success li {
        margin-bottom: 0.5rem;
        color: #2e7d32;
        font-weight: 500;
    }
    
    /* Status badges */
    .status-enviou {
        background: linear-gradient(135deg, #4caf50, #45a049);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
        margin: 2px;
        display: inline-block;
    }
    
    .status-nao-enviou {
        background: linear-gradient(135deg, #f44336, #d32f2f);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
        margin: 2px;
        display: inline-block;
    }
    
    /* Categorias de responsáveis */
    .category-ativo {
        background: linear-gradient(135deg, #e8f5e8, #c8e6c9) !important;
        border-left: 4px solid #4caf50 !important;
    }
    
    .category-parcial {
        background: linear-gradient(135deg, #fff8e1, #ffecb3) !important;
        border-left: 4px solid #ff9800 !important;
    }
    
    .category-pouco {
        background: linear-gradient(135deg, #ffebee, #ffcdd2) !important;
        border-left: 4px solid #f44336 !important;
    }
    
    .category-inativo {
        background: linear-gradient(135deg, #f5f5f5, #eeeeee) !important;
        border-left: 4px solid #9e9e9e !important;
    }
    
    /* Sidebar customizada */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Tabs customizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #666;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: white !important;
        color: #667eea !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Métricas do Streamlit */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid rgba(0, 0, 0, 0.05);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabelas */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    }
    
    /* Upload de arquivo */
    .uploadedFile {
        border-radius: 12px;
        border: 2px dashed #667eea;
        background: rgba(102, 126, 234, 0.05);
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
    }
    
    /* Selectbox e multiselect */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    .stMultiSelect > div > div {
        border-radius: 12px;
        border: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    /* Rodapé */
    .footer {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        color: white;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.1);
    }
    
    .footer p {
        margin: 0.5rem 0;
        opacity: 0.8;
    }
    
    /* Animações */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in-up {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main-header {
            padding: 2rem 1rem;
        }
        
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            padding: 1.5rem;
        }
        
        .alert-critical, .alert-success {
            padding: 1.5rem;
        }
    }
    
    /* Scrollbar customizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #5a6fd8, #6a4190);
    }
    
    /* Loading spinner */
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

class DataProcessor:
    """Classe para processamento e validação de dados"""
    
    @staticmethod
    def validar_arquivo(df: pd.DataFrame) -> Tuple[bool, str]:
        """Valida se o arquivo possui as colunas necessárias"""
        try:
            colunas_faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in df.columns]
            
            if colunas_faltantes:
                return False, f"Colunas obrigatórias não encontradas: {', '.join(colunas_faltantes)}"
            
            if df.empty:
                return False, "O arquivo está vazio"
            
            if df['RESPONSÁVEL'].isna().all():
                return False, "Coluna RESPONSÁVEL não possui dados válidos"
            
            return True, "Arquivo válido"
            
        except Exception as e:
            logger.error(f"Erro na validação: {str(e)}")
            return False, f"Erro na validação: {str(e)}"
    
    @staticmethod
    def processar_dados(df: pd.DataFrame) -> pd.DataFrame:
        """Processa os dados da planilha com tratamento de erros robusto"""
        try:
            # Criar cópia para não modificar o original
            df_processado = df.copy()
            
            # Limpar nomes dos responsáveis
            df_processado['RESPONSÁVEL'] = df_processado['RESPONSÁVEL'].astype(str).str.strip()
            
            # Remover linhas com responsáveis vazios ou inválidos
            df_processado = df_processado[
                (df_processado['RESPONSÁVEL'].notna()) & 
                (df_processado['RESPONSÁVEL'] != '') &
                (df_processado['RESPONSÁVEL'] != 'nan')
            ]
            
            # Converter coluna de data com tratamento de erros
            try:
                df_processado['DATA'] = pd.to_datetime(df_processado['DATA'], errors='coerce')
            except Exception as e:
                logger.warning(f"Erro ao converter datas: {str(e)}")
                # Tentar diferentes formatos
                for formato in ['%d/%m/%Y', '%Y-%m-%d', '%m/%d/%Y']:
                    try:
                        df_processado['DATA'] = pd.to_datetime(df_processado['DATA'], format=formato, errors='coerce')
                        break
                    except:
                        continue
            
            # Remover linhas com datas inválidas
            df_processado = df_processado[df_processado['DATA'].notna()]
            
            # Adicionar colunas derivadas
            df_processado['ANO'] = df_processado['DATA'].dt.year
            df_processado['MES'] = df_processado['DATA'].dt.month
            df_processado['MES_NOME'] = df_processado['DATA'].dt.strftime('%B')
            df_processado['DIA_SEMANA'] = df_processado['DATA'].dt.day_name()
            
            # Remover duplicatas
            df_processado = df_processado.drop_duplicates(subset=['RESPONSÁVEL', 'DATA'])
            
            logger.info(f"Dados processados: {len(df_processado)} registros válidos")
            return df_processado
            
        except Exception as e:
            logger.error(f"Erro no processamento: {str(e)}")
            raise Exception(f"Erro ao processar dados: {str(e)}")

class AnalyticsEngine:
    """Classe para cálculos e análises"""
    
    @staticmethod
    def calcular_analise_mensal(df: pd.DataFrame, responsaveis_unicos: List[str]) -> Dict:
        """Calcula análise por mês com métricas adicionais"""
        try:
            # Filtrar dados do período de análise
            dados_periodo = df[
                (df['ANO'] == ANO_ANALISE) & 
                (df['MES'].isin(MESES_ANALISE.keys()))
            ]
            
            analise = {}
            
            for mes_num, mes_nome in MESES_ANALISE.items():
                dados_mes = dados_periodo[dados_periodo['MES'] == mes_num]
                responsaveis_ativos = dados_mes['RESPONSÁVEL'].unique().tolist()
                responsaveis_inativos = [r for r in responsaveis_unicos if r not in responsaveis_ativos]
                
                # Calcular métricas adicionais
                total_envios = len(dados_mes)
                media_envios_por_responsavel = total_envios / len(responsaveis_ativos) if responsaveis_ativos else 0
                
                analise[mes_num] = {
                    'mes_nome': mes_nome,
                    'total_registros': total_envios,
                    'responsaveis_enviaram': responsaveis_ativos,
                    'responsaveis_nao_enviaram': responsaveis_inativos,
                    'qtd_enviaram': len(responsaveis_ativos),
                    'qtd_nao_enviaram': len(responsaveis_inativos),
                    'taxa_envio': (len(responsaveis_ativos) / len(responsaveis_unicos)) * 100,
                    'media_envios_por_responsavel': media_envios_por_responsavel,
                    'total_responsaveis': len(responsaveis_unicos)
                }
            
            return analise
            
        except Exception as e:
            logger.error(f"Erro na análise mensal: {str(e)}")
            raise Exception(f"Erro ao calcular análise mensal: {str(e)}")
    
    @staticmethod
    def calcular_status_individual(df: pd.DataFrame, responsaveis_unicos: List[str]) -> Dict:
        """Calcula status individual com métricas detalhadas"""
        try:
            dados_periodo = df[
                (df['ANO'] == ANO_ANALISE) & 
                (df['MES'].isin(MESES_ANALISE.keys()))
            ]
            
            status_completo = {}
            
            for resp in responsaveis_unicos:
                dados_resp = dados_periodo[dados_periodo['RESPONSÁVEL'] == resp]
                
                # Verificar envios por mês
                envios_por_mes = {}
                total_envios = 0
                
                for mes_num in MESES_ANALISE.keys():
                    envios_mes = len(dados_resp[dados_resp['MES'] == mes_num])
                    envios_por_mes[mes_num] = envios_mes > 0
                    total_envios += envios_mes
                
                meses_ativos = sum(envios_por_mes.values())
                
                # Determinar situação e categoria
                if meses_ativos == 3:
                    situacao = 'TOTALMENTE ATIVO'
                    categoria = 'ativo'
                elif meses_ativos == 2:
                    situacao = 'PARCIALMENTE ATIVO'  
                    categoria = 'parcial'
                elif meses_ativos == 1:
                    situacao = 'POUCO ATIVO'
                    categoria = 'pouco'
                else:
                    situacao = 'INATIVO'
                    categoria = 'inativo'
                
                # Calcular consistência (envios regulares)
                consistencia = (meses_ativos / 3) * 100
                
                status_completo[resp] = {
                    'julho': envios_por_mes.get(7, False),
                    'agosto': envios_por_mes.get(8, False),
                    'setembro': envios_por_mes.get(9, False),
                    'meses_ativos': meses_ativos,
                    'total_envios': total_envios,
                    'situacao': situacao,
                    'categoria': categoria,
                    'consistencia': consistencia
                }
            
            return status_completo
            
        except Exception as e:
            logger.error(f"Erro no status individual: {str(e)}")
            raise Exception(f"Erro ao calcular status individual: {str(e)}")
    
    @staticmethod
    def calcular_tendencias(analise_mensal: Dict) -> Dict:
        """Calcula tendências e previsões"""
        try:
            taxas = [analise_mensal[mes]['taxa_envio'] for mes in sorted(MESES_ANALISE.keys())]
            
            # Calcular tendência linear simples
            x = np.array([1, 2, 3])  # Meses
            y = np.array(taxas)
            
            # Regressão linear simples
            coef = np.polyfit(x, y, 1)
            tendencia_mensal = coef[0]  # Coeficiente angular
            
            # Previsão para próximo mês
            previsao_proximo_mes = coef[0] * 4 + coef[1]
            previsao_proximo_mes = max(0, min(100, previsao_proximo_mes))  # Limitar entre 0 e 100
            
            # Classificar tendência
            if tendencia_mensal > 2:
                classificacao_tendencia = "Crescimento Forte"
                emoji_tendencia = "📈"
            elif tendencia_mensal > 0:
                classificacao_tendencia = "Crescimento Leve"
                emoji_tendencia = "📊"
            elif tendencia_mensal > -2:
                classificacao_tendencia = "Estável"
                emoji_tendencia = "➡️"
            elif tendencia_mensal > -5:
                classificacao_tendencia = "Queda Leve"
                emoji_tendencia = "📉"
            else:
                classificacao_tendencia = "Queda Forte"
                emoji_tendencia = "⚠️"
            
            return {
                'tendencia_mensal': tendencia_mensal,
                'previsao_proximo_mes': previsao_proximo_mes,
                'classificacao': classificacao_tendencia,
                'emoji': emoji_tendencia,
                'taxas_historicas': taxas
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo de tendências: {str(e)}")
            return {
                'tendencia_mensal': 0,
                'previsao_proximo_mes': 0,
                'classificacao': "Erro no cálculo",
                'emoji': "❓",
                'taxas_historicas': []
            }

class ChartGenerator:
    """Classe para geração de gráficos"""
    
    @staticmethod
    def criar_grafico_evolucao(analise: Dict, tendencias: Dict) -> Optional[go.Figure]:
        """Cria gráfico de evolução temporal com previsão"""
        if not PLOTLY_AVAILABLE:
            return None
        
        try:
            meses = list(MESES_ANALISE.values())
            taxas = [analise[mes]['taxa_envio'] for mes in sorted(MESES_ANALISE.keys())]
            
            # Adicionar previsão
            meses_com_previsao = meses + ['Outubro (Prev.)']
            taxas_com_previsao = taxas + [tendencias['previsao_proximo_mes']]
            
            # Cores modernas
            cores_barras = ['#667eea', '#f093fb', '#ffeaa7', '#a8e6cf']
            
            fig = go.Figure()
            
            # Barras históricas
            fig.add_trace(go.Bar(
                x=meses,
                y=taxas,
                marker=dict(
                    color=cores_barras[:3],
                    line=dict(color='rgba(255,255,255,0.8)', width=2)
                ),
                text=[f'{taxa:.1f}%' for taxa in taxas],
                textposition='outside',
                textfont=dict(size=14, color='#2c3e50', family='Inter'),
                name='Taxa Histórica',
                hovertemplate='<b>%{x}</b><br>Taxa: %{y:.1f}%<extra></extra>'
            ))
            
            # Barra de previsão
            fig.add_trace(go.Bar(
                x=['Outubro (Prev.)'],
                y=[tendencias['previsao_proximo_mes']],
                marker=dict(
                    color='rgba(168, 230, 207, 0.7)',
                    line=dict(color='#4caf50', width=2, dash='dash')
                ),
                text=[f'{tendencias["previsao_proximo_mes"]:.1f}%'],
                textposition='outside',
                textfont=dict(size=14, color='#2c3e50', family='Inter'),
                name='Previsão',
                hovertemplate='<b>Previsão Outubro</b><br>Taxa: %{y:.1f}%<extra></extra>'
            ))
            
            # Linha de tendência
            fig.add_trace(go.Scatter(
                x=meses_com_previsao,
                y=taxas_com_previsao,
                mode='lines+markers',
                line=dict(color='#e74c3c', width=4, dash='dot'),
                marker=dict(size=12, color='#e74c3c', symbol='diamond'),
                name=f'Tendência {tendencias["emoji"]}',
                hovertemplate='<b>Tendência</b><br>%{x}: %{y:.1f}%<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text=f'📈 Evolução e Previsão - {tendencias["classificacao"]}',
                    font=dict(size=20, color='#2c3e50', family='Inter'),
                    x=0.5
                ),
                xaxis=dict(
                    title='Período',
                    titlefont=dict(size=14, color='#2c3e50'),
                    tickfont=dict(size=12, color='#2c3e50'),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                yaxis=dict(
                    title='Taxa de Envio (%)',
                    titlefont=dict(size=14, color='#2c3e50'),
                    tickfont=dict(size=12, color='#2c3e50'),
                    range=[0, 100],
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                height=450,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter')
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de evolução: {str(e)}")
            return None
    
    @staticmethod
    def criar_grafico_pizza_situacao(status_individual: Dict) -> Optional[go.Figure]:
        """Cria gráfico de pizza com situação dos responsáveis"""
        if not PLOTLY_AVAILABLE:
            return None
        
        try:
            categorias = {}
            for status in status_individual.values():
                cat = status['categoria']
                categorias[cat] = categorias.get(cat, 0) + 1
            
            labels = {
                'ativo': '🟢 Totalmente Ativos',
                'parcial': '🟡 Parcialmente Ativos', 
                'pouco': '🟠 Pouco Ativos',
                'inativo': '🔴 Inativos'
            }
            
            cores = {
                'ativo': '#4caf50',
                'parcial': '#ff9800',
                'pouco': '#f44336', 
                'inativo': '#9e9e9e'
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=[labels[cat] for cat in categorias.keys()],
                values=list(categorias.values()),
                marker=dict(
                    colors=[cores[cat] for cat in categorias.keys()],
                    line=dict(color='white', width=3)
                ),
                hole=0.4,
                textinfo='label+percent+value',
                textfont=dict(size=12, family='Inter'),
                hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                title=dict(
                    text='🎯 Distribuição dos Responsáveis por Situação',
                    font=dict(size=20, color='#2c3e50', family='Inter'),
                    x=0.5
                ),
                height=450,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter'),
                annotations=[dict(
                    text='Status<br>Geral', 
                    x=0.5, y=0.5, 
                    font_size=16, 
                    showarrow=False, 
                    font_color='#2c3e50'
                )]
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de pizza: {str(e)}")
            return None
    
    @staticmethod
    def criar_grafico_heatmap_consistencia(status_individual: Dict) -> Optional[go.Figure]:
        """Cria heatmap de consistência dos responsáveis"""
        if not PLOTLY_AVAILABLE:
            return None
        
        try:
            # Preparar dados para heatmap
            responsaveis = list(status_individual.keys())
            meses = ['Julho', 'Agosto', 'Setembro']
            
            # Matriz de dados (1 = enviou, 0 = não enviou)
            matriz = []
            for resp in responsaveis:
                linha = [
                    1 if status_individual[resp]['julho'] else 0,
                    1 if status_individual[resp]['agosto'] else 0,
                    1 if status_individual[resp]['setembro'] else 0
                ]
                matriz.append(linha)
            
            # Limitar a 20 responsáveis para melhor visualização
            if len(responsaveis) > 20:
                # Ordenar por consistência (mais ativos primeiro)
                responsaveis_ordenados = sorted(
                    responsaveis, 
                    key=lambda x: status_individual[x]['meses_ativos'], 
                    reverse=True
                )
                responsaveis = responsaveis_ordenados[:20]
                matriz = [matriz[responsaveis.index(resp)] for resp in responsaveis]
            
            fig = go.Figure(data=go.Heatmap(
                z=matriz,
                x=meses,
                y=responsaveis,
                colorscale=[[0, '#ffcdd2'], [1, '#c8e6c9']],
                text=[[f'{"✅" if val else "❌"}' for val in linha] for linha in matriz],
                texttemplate="%{text}",
                textfont={"size": 16},
                hovertemplate='<b>%{y}</b><br>%{x}: %{text}<extra></extra>',
                showscale=False
            ))
            
            fig.update_layout(
                title=dict(
                    text='🔥 Mapa de Consistência dos Responsáveis',
                    font=dict(size=18, color='#2c3e50', family='Inter'),
                    x=0.5
                ),
                xaxis=dict(
                    title='Meses',
                    titlefont=dict(size=14, color='#2c3e50'),
                    tickfont=dict(size=12, color='#2c3e50')
                ),
                yaxis=dict(
                    title='Responsáveis',
                    titlefont=dict(size=14, color='#2c3e50'),
                    tickfont=dict(size=10, color='#2c3e50')
                ),
                height=max(400, len(responsaveis) * 25),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family='Inter')
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Erro ao criar heatmap: {str(e)}")
            return None

def exportar_relatorio_excel(analise_mensal: Dict, status_individual: Dict, responsaveis_unicos: List[str]) -> io.BytesIO:
    """Exporta relatório completo para Excel"""
    try:
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Aba 1: Resumo Geral
            resumo_data = []
            for mes_num, dados in analise_mensal.items():
                resumo_data.append({
                    'Mês': dados['mes_nome'],
                    'Taxa de Envio (%)': round(dados['taxa_envio'], 2),
                    'Responsáveis que Enviaram': dados['qtd_enviaram'],
                    'Responsáveis que NÃO Enviaram': dados['qtd_nao_enviaram'],
                    'Total de Registros': dados['total_registros'],
                    'Média Envios/Responsável': round(dados['media_envios_por_responsavel'], 2)
                })
            
            df_resumo = pd.DataFrame(resumo_data)
            df_resumo.to_excel(writer, sheet_name='Resumo Geral', index=False)
            
            # Aba 2: Status Individual
            status_data = []
            for nome, status in status_individual.items():
                status_data.append({
                    'Responsável': nome,
                    'Julho': 'Sim' if status['julho'] else 'Não',
                    'Agosto': 'Sim' if status['agosto'] else 'Não',
                    'Setembro': 'Sim' if status['setembro'] else 'Não',
                    'Meses Ativos': status['meses_ativos'],
                    'Total de Envios': status['total_envios'],
                    'Consistência (%)': round(status['consistencia'], 2),
                    'Situação': status['situacao']
                })
            
            df_status = pd.DataFrame(status_data)
            df_status.to_excel(writer, sheet_name='Status Individual', index=False)
            
            # Aba 3: Análise por Categoria
            categorias_count = {}
            for status in status_individual.values():
                cat = status['categoria']
                categorias_count[cat] = categorias_count.get(cat, 0) + 1
            
            categoria_data = []
            labels_map = {
                'ativo': 'Totalmente Ativos',
                'parcial': 'Parcialmente Ativos',
                'pouco': 'Pouco Ativos',
                'inativo': 'Inativos'
            }
            
            for cat, count in categorias_count.items():
                categoria_data.append({
                    'Categoria': labels_map[cat],
                    'Quantidade': count,
                    'Percentual (%)': round((count / len(responsaveis_unicos)) * 100, 2)
                })
            
            df_categorias = pd.DataFrame(categoria_data)
            df_categorias.to_excel(writer, sheet_name='Análise por Categoria', index=False)
        
        output.seek(0)
        return output
        
    except Exception as e:
        logger.error(f"Erro ao exportar Excel: {str(e)}")
        raise Exception(f"Erro ao exportar relatório: {str(e)}")

# Interface principal
def main():
    # Header moderno
    st.markdown("""
    <div class="main-header fade-in-up">
        <h1>📊 Painel de Acompanhamento de Reports</h1>
        <p>Análise Completa e Inteligente • Julho, Agosto e Setembro 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar aprimorada
    with st.sidebar:
        st.markdown("### 📁 Upload de Dados")
        
        uploaded_file = st.file_uploader(
            "Envie a planilha Excel",
            type=['xlsx', 'xls'],
            help="Faça upload do arquivo 'Reports_Geral_Consolidado.xlsx'",
            accept_multiple_files=False
        )
        
        if uploaded_file is not None:
            st.success("✅ Arquivo carregado com sucesso!")
            st.info(f"📄 **{uploaded_file.name}**")
            st.caption(f"Tamanho: {uploaded_file.size / 1024:.1f} KB")
        
        st.markdown("---")
        st.markdown("### 🔍 Filtros e Configurações")
        
    # Processar dados se arquivo foi carregado
    if uploaded_file is not None:
        try:
            # Ler arquivo Excel
            with st.spinner('🔄 Processando dados...'):
                df = pd.read_excel(uploaded_file)
                
                # Validar arquivo
                valido, mensagem = DataProcessor.validar_arquivo(df)
                if not valido:
                    st.error(f"❌ {mensagem}")
                    st.stop()
                
                # Processar dados
                df_processado = DataProcessor.processar_dados(df)
                
                # Obter responsáveis únicos
                responsaveis_unicos = sorted(df_processado['RESPONSÁVEL'].dropna().unique())
                
                # Análises
                analise_mensal = AnalyticsEngine.calcular_analise_mensal(df_processado, responsaveis_unicos)
                status_individual = AnalyticsEngine.calcular_status_individual(df_processado, responsaveis_unicos)
                tendencias = AnalyticsEngine.calcular_tendencias(analise_mensal)
            
            # Filtro de categoria na sidebar
            with st.sidebar:
                categorias_filtro = st.multiselect(
                    "Filtrar por situação:",
                    options=['ativo', 'parcial', 'pouco', 'inativo'],
                    default=['ativo', 'parcial', 'pouco', 'inativo'],
                    format_func=lambda x: {
                        'ativo': '🟢 Totalmente Ativos',
                        'parcial': '🟡 Parcialmente Ativos',
                        'pouco': '🟠 Pouco Ativos', 
                        'inativo': '🔴 Inativos'
                    }[x]
                )
                
                st.markdown("---")
                st.markdown("### 📋 Resumo Rápido")
                st.metric("Total de Responsáveis", len(responsaveis_unicos))
                st.metric("Período Analisado", "3 meses")
                st.metric("Registros Processados", len(df_processado))
                st.metric("Última Atualização", datetime.now().strftime("%d/%m/%Y %H:%M"))
                
                # Botão de exportação
                st.markdown("---")
                st.markdown("### 📤 Exportar Dados")
                
                try:
                    excel_buffer = exportar_relatorio_excel(analise_mensal, status_individual, responsaveis_unicos)
                    st.download_button(
                        label="📊 Baixar Relatório Excel",
                        data=excel_buffer,
                        file_name=f"relatorio_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Erro ao preparar exportação: {str(e)}")
            
            # Métricas principais com design moderno
            st.markdown("### 📈 Métricas Principais")
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    label="📋 Total Responsáveis",
                    value=len(responsaveis_unicos),
                    help="Número total de responsáveis únicos no sistema"
                )
            
            with col2:
                st.metric(
                    label="📅 Taxa Julho",
                    value=f"{analise_mensal[7]['taxa_envio']:.1f}%",
                    help="Percentual de responsáveis que enviaram reports em julho"
                )
            
            with col3:
                delta_ago = analise_mensal[8]['taxa_envio'] - analise_mensal[7]['taxa_envio']
                st.metric(
                    label="📅 Taxa Agosto", 
                    value=f"{analise_mensal[8]['taxa_envio']:.1f}%",
                    delta=f"{delta_ago:.1f}pp",
                    help="Percentual de responsáveis que enviaram reports em agosto"
                )
            
            with col4:
                delta_set = analise_mensal[9]['taxa_envio'] - analise_mensal[8]['taxa_envio']
                st.metric(
                    label="📅 Taxa Setembro",
                    value=f"{analise_mensal[9]['taxa_envio']:.1f}%", 
                    delta=f"{delta_set:.1f}pp",
                    help="Percentual de responsáveis que enviaram reports em setembro"
                )
            
            with col5:
                consistentes = sum(1 for s in status_individual.values() if s['meses_ativos'] == 3)
                st.metric(
                    label="⭐ Consistentes",
                    value=f"{(consistentes/len(responsaveis_unicos)*100):.1f}%",
                    delta=f"{consistentes} resp.",
                    help="Responsáveis que enviaram reports nos 3 meses"
                )
            
            # Análise de tendência
            st.markdown("### 📊 Análise de Tendência")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label=f"{tendencias['emoji']} Tendência",
                    value=tendencias['classificacao'],
                    delta=f"{tendencias['tendencia_mensal']:.1f}pp/mês",
                    help="Tendência baseada na variação mensal das taxas"
                )
            
            with col2:
                st.metric(
                    label="🔮 Previsão Outubro",
                    value=f"{tendencias['previsao_proximo_mes']:.1f}%",
                    help="Previsão baseada na tendência linear dos últimos 3 meses"
                )
            
            with col3:
                media_geral = np.mean([analise_mensal[mes]['taxa_envio'] for mes in MESES_ANALISE.keys()])
                st.metric(
                    label="📊 Média do Período",
                    value=f"{media_geral:.1f}%",
                    help="Taxa média de envios no período analisado"
                )
            
            # Alerta crítico ou sucesso
            queda_total = analise_mensal[7]['taxa_envio'] - analise_mensal[9]['taxa_envio']
            
            if queda_total > 10:  # Queda significativa
                st.markdown(f"""
                <div class="alert-critical fade-in-up">
                    <h3>🚨 SITUAÇÃO CRÍTICA: Queda Drástica nas Taxas de Envios</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 1rem 0;">
                        <div style="background: rgba(255,255,255,0.7); padding: 1rem; border-radius: 8px;">
                            <strong>📊 Julho:</strong> {analise_mensal[7]['taxa_envio']:.1f}% ({analise_mensal[7]['qtd_enviaram']} responsáveis)
                        </div>
                        <div style="background: rgba(255,255,255,0.7); padding: 1rem; border-radius: 8px;">
                            <strong>📊 Agosto:</strong> {analise_mensal[8]['taxa_envio']:.1f}% ({analise_mensal[8]['qtd_enviaram']} responsáveis)<br>
                            <span style="color: #d32f2f;">↓ Queda de {analise_mensal[7]['taxa_envio'] - analise_mensal[8]['taxa_envio']:.1f}pp</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.7); padding: 1rem; border-radius: 8px;">
                            <strong>📊 Setembro:</strong> {analise_mensal[9]['taxa_envio']:.1f}% ({analise_mensal[9]['qtd_enviaram']} responsáveis)<br>
                            <span style="color: #d32f2f;">↓ Queda de {analise_mensal[8]['taxa_envio'] - analise_mensal[9]['taxa_envio']:.1f}pp</span>
                        </div>
                    </div>
                    <div style="background: rgba(211, 47, 47, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #d32f2f; margin-top: 1rem;">
                        <strong>🎯 Resultado:</strong> Perda total de {queda_total:.1f} pontos percentuais em 3 meses!<br>
                        <strong>🔮 Previsão:</strong> Se a tendência continuar, outubro pode ter {tendencias['previsao_proximo_mes']:.1f}% de taxa de envios.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif queda_total < -5:  # Crescimento significativo
                st.markdown(f"""
                <div class="alert-success fade-in-up">
                    <h3>✅ SITUAÇÃO POSITIVA: Crescimento nas Taxas de Envios</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin: 1rem 0;">
                        <div style="background: rgba(255,255,255,0.7); padding: 1rem; border-radius: 8px;">
                            <strong>📊 Julho:</strong> {analise_mensal[7]['taxa_envio']:.1f}% ({analise_mensal[7]['qtd_enviaram']} responsáveis)
                        </div>
                        <div style="background: rgba(255,255,255,0.7); padding: 1rem; border-radius: 8px;">
                            <strong>📊 Agosto:</strong> {analise_mensal[8]['taxa_envio']:.1f}% ({analise_mensal[8]['qtd_enviaram']} responsáveis)<br>
                            <span style="color: #2e7d32;">↑ Crescimento de {analise_mensal[8]['taxa_envio'] - analise_mensal[7]['taxa_envio']:.1f}pp</span>
                        </div>
                        <div style="background: rgba(255,255,255,0.7); padding: 1rem; border-radius: 8px;">
                            <strong>📊 Setembro:</strong> {analise_mensal[9]['taxa_envio']:.1f}% ({analise_mensal[9]['qtd_enviaram']} responsáveis)<br>
                            <span style="color: #2e7d32;">↑ Crescimento de {analise_mensal[9]['taxa_envio'] - analise_mensal[8]['taxa_envio']:.1f}pp</span>
                        </div>
                    </div>
                    <div style="background: rgba(46, 125, 50, 0.1); padding: 1rem; border-radius: 8px; border-left: 4px solid #2e7d32; margin-top: 1rem;">
                        <strong>🎯 Resultado:</strong> Crescimento total de {abs(queda_total):.1f} pontos percentuais em 3 meses!<br>
                        <strong>🔮 Previsão:</strong> Mantendo a tendência, outubro pode alcançar {tendencias['previsao_proximo_mes']:.1f}% de taxa de envios.
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráficos modernos
            st.markdown("### 📊 Análise Visual")
            
            if PLOTLY_AVAILABLE:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_evolucao = ChartGenerator.criar_grafico_evolucao(analise_mensal, tendencias)
                    if fig_evolucao:
                        st.plotly_chart(fig_evolucao, use_container_width=True)
                
                with col2:
                    fig_pizza = ChartGenerator.criar_grafico_pizza_situacao(status_individual)
                    if fig_pizza:
                        st.plotly_chart(fig_pizza, use_container_width=True)
                
                # Heatmap de consistência
                st.markdown("### 🔥 Mapa de Consistência")
                fig_heatmap = ChartGenerator.criar_grafico_heatmap_consistencia(status_individual)
                if fig_heatmap:
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                else:
                    st.info("Heatmap não disponível para este conjunto de dados.")
            else:
                st.warning("⚠️ Gráficos interativos não disponíveis. Exibindo dados em formato alternativo.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Evolução das Taxas")
                    dados_evolucao = pd.DataFrame({
                        'Mês': list(MESES_ANALISE.values()),
                        'Taxa (%)': [analise_mensal[mes]['taxa_envio'] for mes in sorted(MESES_ANALISE.keys())]
                    })
                    st.bar_chart(dados_evolucao.set_index('Mês'))
                
                with col2:
                    st.subheader("🎯 Situação dos Responsáveis")
                    categorias_count = {}
                    for status in status_individual.values():
                        cat = status['categoria']
                        categorias_count[cat] = categorias_count.get(cat, 0) + 1
                    
                    labels_map = {
                        'ativo': '🟢 Totalmente Ativos',
                        'parcial': '🟡 Parcialmente Ativos',
                        'pouco': '🟠 Pouco Ativos',
                        'inativo': '🔴 Inativos'
                    }
                    
                    dist_df = pd.DataFrame({
                        'Situação': [labels_map[k] for k in categorias_count.keys()],
                        'Quantidade': list(categorias_count.values())
                    })
                    st.bar_chart(dist_df.set_index('Situação'))
            
            # Análise detalhada por mês com design melhorado
            st.markdown("### 📅 Análise Detalhada por Mês")
            
            tab_jul, tab_ago, tab_set = st.tabs(["🌞 Julho 2025", "🌻 Agosto 2025", "🍂 Setembro 2025"])
            
            for tab, mes_num in zip([tab_jul, tab_ago, tab_set], [7, 8, 9]):
                with tab:
                    dados = analise_mensal[mes_num]
                    
                    # Métricas do mês
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📊 Taxa de Envio", f"{dados['taxa_envio']:.1f}%")
                    with col2:
                        st.metric("✅ Enviaram", dados['qtd_enviaram'])
                    with col3:
                        st.metric("❌ Não Enviaram", dados['qtd_nao_enviaram'])
                    with col4:
                        st.metric("📈 Total Registros", dados['total_registros'])
                    
                    # Listas de responsáveis
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### ✅ Responsáveis que Enviaram")
                        if dados['responsaveis_enviaram']:
                            responsaveis_html = ""
                            for resp in sorted(dados['responsaveis_enviaram']):
                                responsaveis_html += f"<span class='status-enviou'>{resp}</span> "
                            st.markdown(responsaveis_html, unsafe_allow_html=True)
                        else:
                            st.info("Nenhum responsável enviou neste mês.")
                    
                    with col2:
                        st.markdown("#### ❌ Responsáveis que NÃO Enviaram")
                        if dados['responsaveis_nao_enviaram']:
                            responsaveis_html = ""
                            for resp in sorted(dados['responsaveis_nao_enviaram']):
                                responsaveis_html += f"<span class='status-nao-enviou'>{resp}</span> "
                            st.markdown(responsaveis_html, unsafe_allow_html=True)
                        else:
                            st.success("Todos os responsáveis enviaram!")
            
            # Status individual dos responsáveis
            st.markdown("### 👥 Status Individual dos Responsáveis")
            
            # Filtrar por categoria selecionada
            responsaveis_filtrados = {
                nome: status for nome, status in status_individual.items() 
                if status['categoria'] in categorias_filtro
            }
            
            if responsaveis_filtrados:
                # Criar DataFrame para exibição
                dados_tabela = []
                for nome, status in responsaveis_filtrados.items():
                    dados_tabela.append({
                        'Responsável': nome,
                        'Julho': '✅' if status['julho'] else '❌',
                        'Agosto': '✅' if status['agosto'] else '❌',
                        'Setembro': '✅' if status['setembro'] else '❌',
                        'Meses Ativos': status['meses_ativos'],
                        'Total Envios': status['total_envios'],
                        'Consistência (%)': f"{status['consistencia']:.1f}%",
                        'Situação': status['situacao']
                    })
                
                df_status = pd.DataFrame(dados_tabela)
                
                # Ordenar por consistência
                df_status = df_status.sort_values('Meses Ativos', ascending=False)
                
                # Exibir tabela com estilo
                st.dataframe(
                    df_status,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Responsável": st.column_config.TextColumn("👤 Responsável", width="medium"),
                        "Julho": st.column_config.TextColumn("📅 Jul", width="small"),
                        "Agosto": st.column_config.TextColumn("📅 Ago", width="small"),
                        "Setembro": st.column_config.TextColumn("📅 Set", width="small"),
                        "Meses Ativos": st.column_config.NumberColumn("📊 Ativos", width="small"),
                        "Total Envios": st.column_config.NumberColumn("📈 Total", width="small"),
                        "Consistência (%)": st.column_config.TextColumn("🎯 Consist.", width="small"),
                        "Situação": st.column_config.TextColumn("🏷️ Situação", width="large")
                    }
                )
            else:
                st.info("Nenhum responsável encontrado com os filtros selecionados.")
            
            # Resumo final por categoria
            st.markdown("### 📋 Resumo por Categoria")
            
            categorias_count = {}
            for status in status_individual.values():
                cat = status['categoria']
                categorias_count[cat] = categorias_count.get(cat, 0) + 1
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ativo_count = categorias_count.get('ativo', 0)
                ativo_pct = (ativo_count / len(responsaveis_unicos)) * 100
                st.metric(
                    "🟢 Totalmente Ativos",
                    value=ativo_count,
                    delta=f"{ativo_pct:.1f}% do total",
                    help="Responsáveis que enviaram reports nos 3 meses"
                )
            
            with col2:
                parcial_count = categorias_count.get('parcial', 0)
                parcial_pct = (parcial_count / len(responsaveis_unicos)) * 100
                st.metric(
                    "🟡 Parcialmente Ativos", 
                    value=parcial_count,
                    delta=f"{parcial_pct:.1f}% do total",
                    help="Responsáveis que enviaram reports em 2 meses"
                )
            
            with col3:
                pouco_count = categorias_count.get('pouco', 0)
                pouco_pct = (pouco_count / len(responsaveis_unicos)) * 100
                st.metric(
                    "🟠 Pouco Ativos",
                    value=pouco_count, 
                    delta=f"{pouco_pct:.1f}% do total",
                    help="Responsáveis que enviaram reports em apenas 1 mês"
                )
            
            with col4:
                inativo_count = categorias_count.get('inativo', 0)
                inativo_pct = (inativo_count / len(responsaveis_unicos)) * 100
                st.metric(
                    "🔴 Inativos",
                    value=inativo_count,
                    delta=f"{inativo_pct:.1f}% do total",
                    help="Responsáveis que não enviaram nenhum report"
                )
            
        except Exception as e:
            logger.error(f"Erro geral na aplicação: {str(e)}")
            st.error(f"❌ Erro ao processar dados: {str(e)}")
            st.info("Verifique se o arquivo Excel está no formato correto e contém as colunas necessárias.")
            
            # Mostrar informações de debug se necessário
            with st.expander("🔍 Informações de Debug"):
                st.text(f"Erro detalhado: {str(e)}")
                if uploaded_file:
                    st.text(f"Nome do arquivo: {uploaded_file.name}")
                    st.text(f"Tamanho: {uploaded_file.size} bytes")
    
    else:
        # Tela inicial sem dados - design melhorado
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 20px; margin: 2rem 0;">
            <h2 style="color: #2c3e50; margin-bottom: 1rem;">📁 Bem-vindo ao Painel de Reports</h2>
            <p style="color: #666; font-size: 1.1rem; margin-bottom: 2rem;">
                Faça upload da planilha Excel na barra lateral para começar a análise
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Instruções em cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin-bottom: 1rem;">🚀 Como usar</h3>
                <ol style="color: #2c3e50; line-height: 1.8;">
                    <li><strong>Upload:</strong> Envie o arquivo Excel na barra lateral</li>
                    <li><strong>Validação:</strong> O sistema verificará a integridade dos dados</li>
                    <li><strong>Processamento:</strong> Os dados serão limpos e organizados automaticamente</li>
                    <li><strong>Análise:</strong> Visualize métricas, gráficos e tendências</li>
                    <li><strong>Filtros:</strong> Use filtros para focar em categorias específicas</li>
                    <li><strong>Exportação:</strong> Baixe relatórios completos em Excel</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #667eea; margin-bottom: 1rem;">✨ Funcionalidades</h3>
                <ul style="color: #2c3e50; line-height: 1.8; list-style: none; padding-left: 0;">
                    <li>✅ <strong>Validação automática</strong> de dados</li>
                    <li>✅ <strong>Limpeza inteligente</strong> de informações</li>
                    <li>✅ <strong>Análise de tendências</strong> com previsões</li>
                    <li>✅ <strong>Gráficos interativos</strong> modernos</li>
                    <li>✅ <strong>Heatmap de consistência</strong></li>
                    <li>✅ <strong>Filtros dinâmicos</strong> avançados</li>
                    <li>✅ <strong>Exportação para Excel</strong></li>
                    <li>✅ <strong>Interface responsiva</strong></li>
                    <li>✅ <strong>Alertas inteligentes</strong></li>
                    <li>✅ <strong>Tratamento robusto de erros</strong></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Requisitos do arquivo
        st.markdown("### 📋 Requisitos do Arquivo")
        st.info("""
        **Colunas obrigatórias:**
        - `RESPONSÁVEL`: Nome do responsável (texto)
        - `DATA`: Data do envio (formato de data válido)
        
        **Formatos suportados:** .xlsx, .xls
        
        **Período analisado:** Julho, Agosto e Setembro de 2025
        """)
    
    # Rodapé moderno
    st.markdown("""
    <div class="footer">
        <h4 style="margin-bottom: 1rem; color: white;">📊 Painel de Acompanhamento de Reports</h4>
        <p>Desenvolvido com ❤️ usando Streamlit, Plotly e Pandas</p>
        <p style="font-size: 0.9rem; opacity: 0.7;">
            Versão 3.0 • Última atualização: """ + datetime.now().strftime("%d/%m/%Y") + """
        </p>
        <p style="font-size: 0.8rem; opacity: 0.6;">
            Recursos: Análise de Tendências • Previsões • Heatmaps • Exportação Excel • Interface Responsiva
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

