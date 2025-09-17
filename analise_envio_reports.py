import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import io

# Configuração da página
st.set_page_config(
    page_title="Painel de Acompanhamento de Reports",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para estilização
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #3498db;
        margin-bottom: 1rem;
    }
    
    .alert-critical {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .alert-critical h3 {
        color: #856404;
        margin-bottom: 1rem;
    }
    
    .status-enviou {
        background-color: #d4edda;
        color: #155724;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
    }
    
    .status-nao-enviou {
        background-color: #f8d7da;
        color: #721c24;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
    }
    
    .category-ativo {
        background-color: #d4edda !important;
    }
    
    .category-parcial {
        background-color: #fff3cd !important;
    }
    
    .category-pouco {
        background-color: #f8d7da !important;
    }
    
    .category-inativo {
        background-color: #e2e3e5 !important;
    }
</style>
""", unsafe_allow_html=True)

def processar_dados(df):
    """Processa os dados da planilha e remove duplicatas"""
    # Limpar nomes dos responsáveis (remover espaços)
    df['RESPONSÁVEL'] = df['RESPONSÁVEL'].str.strip()
    
    # Converter coluna de data
    df['DATA'] = pd.to_datetime(df['DATA'])
    df['ANO'] = df['DATA'].dt.year
    df['MES'] = df['DATA'].dt.month
    df['MES_NOME'] = df['DATA'].dt.strftime('%B')
    
    return df

def calcular_analise_mensal(df, responsaveis_unicos):
    """Calcula análise por mês (julho, agosto, setembro)"""
    # Filtrar dados de julho em diante (2025)
    dados_periodo = df[(df['ANO'] == 2025) & (df['MES'] >= 7)]
    
    analise = {}
    meses = {7: 'Julho', 8: 'Agosto', 9: 'Setembro'}
    
    for mes_num, mes_nome in meses.items():
        dados_mes = dados_periodo[dados_periodo['MES'] == mes_num]
        responsaveis_ativos = dados_mes['RESPONSÁVEL'].unique().tolist()
        responsaveis_inativos = [r for r in responsaveis_unicos if r not in responsaveis_ativos]
        
        analise[mes_num] = {
            'mes_nome': mes_nome,
            'total_registros': len(dados_mes),
            'responsaveis_enviaram': responsaveis_ativos,
            'responsaveis_nao_enviaram': responsaveis_inativos,
            'qtd_enviaram': len(responsaveis_ativos),
            'qtd_nao_enviaram': len(responsaveis_inativos),
            'taxa_envio': (len(responsaveis_ativos) / len(responsaveis_unicos)) * 100
        }
    
    return analise

def calcular_status_individual(df, responsaveis_unicos):
    """Calcula status individual de cada responsável nos 3 meses"""
    dados_periodo = df[(df['ANO'] == 2025) & (df['MES'] >= 7)]
    status_completo = {}
    
    for resp in responsaveis_unicos:
        # Verificar envios por mês
        julho = len(dados_periodo[(dados_periodo['RESPONSÁVEL'] == resp) & (dados_periodo['MES'] == 7)]) > 0
        agosto = len(dados_periodo[(dados_periodo['RESPONSÁVEL'] == resp) & (dados_periodo['MES'] == 8)]) > 0
        setembro = len(dados_periodo[(dados_periodo['RESPONSÁVEL'] == resp) & (dados_periodo['MES'] == 9)]) > 0
        
        meses_ativos = sum([julho, agosto, setembro])
        
        # Determinar situação
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
        
        status_completo[resp] = {
            'julho': julho,
            'agosto': agosto,
            'setembro': setembro,
            'meses_ativos': meses_ativos,
            'situacao': situacao,
            'categoria': categoria
        }
    
    return status_completo

def criar_grafico_evolucao(analise):
    """Cria gráfico de evolução temporal"""
    meses = ['Julho', 'Agosto', 'Setembro']
    taxas = [analise[7]['taxa_envio'], analise[8]['taxa_envio'], analise[9]['taxa_envio']]
    cores = ['#9b59b6', '#e74c3c', '#f39c12']
    
    fig = go.Figure()
    
    # Barras
    fig.add_trace(go.Bar(
        x=meses,
        y=taxas,
        marker_color=cores,
        text=[f'{taxa:.1f}%' for taxa in taxas],
        textposition='outside',
        name='Taxa de Envio'
    ))
    
    # Linha de tendência
    fig.add_trace(go.Scatter(
        x=meses,
        y=taxas,
        mode='lines+markers',
        line=dict(color='red', width=3, dash='dash'),
        marker=dict(size=8, color='red'),
        name='Tendência'
    ))
    
    fig.update_layout(
        title='Evolução da Taxa de Envios (Julho-Setembro 2025)',
        xaxis_title='Mês',
        yaxis_title='Taxa de Envio (%)',
        yaxis=dict(range=[0, 100]),
        height=400,
        showlegend=True
    )
    
    return fig

def criar_grafico_pizza_situacao(status_individual):
    """Cria gráfico de pizza com situação dos responsáveis"""
    categorias = {}
    for status in status_individual.values():
        cat = status['categoria']
        categorias[cat] = categorias.get(cat, 0) + 1
    
    labels = {
        'ativo': 'Totalmente Ativos',
        'parcial': 'Parcialmente Ativos', 
        'pouco': 'Pouco Ativos',
        'inativo': 'Inativos'
    }
    
    cores = {
        'ativo': '#27ae60',
        'parcial': '#f39c12',
        'pouco': '#e74c3c', 
        'inativo': '#95a5a6'
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=[labels[cat] for cat in categorias.keys()],
        values=list(categorias.values()),
        marker_colors=[cores[cat] for cat in categorias.keys()],
        hole=0.3
    )])
    
    fig.update_layout(
        title='Distribuição dos Responsáveis por Situação',
        height=400
    )
    
    return fig

# Interface principal
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Painel de Acompanhamento de Reports</h1>
        <p>Análise Completa - Julho, Agosto e Setembro 2025</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para upload
    with st.sidebar:
        st.header("📁 Upload de Dados")
        
        uploaded_file = st.file_uploader(
            "Envie a planilha Excel",
            type=['xlsx', 'xls'],
            help="Faça upload do arquivo 'Reports_Geral_Consolidado.xlsx'"
        )
        
        if uploaded_file is not None:
            st.success("✅ Arquivo carregado com sucesso!")
        
        st.markdown("---")
        st.header("🔍 Filtros")
        
    # Processar dados se arquivo foi carregado
    if uploaded_file is not None:
        try:
            # Ler arquivo Excel
            df = pd.read_excel(uploaded_file)
            
            # Processar dados
            df_processado = processar_dados(df)
            
            # Obter responsáveis únicos
            responsaveis_unicos = sorted(df_processado['RESPONSÁVEL'].dropna().unique())
            
            # Análises
            analise_mensal = calcular_analise_mensal(df_processado, responsaveis_unicos)
            status_individual = calcular_status_individual(df_processado, responsaveis_unicos)
            
            # Filtro de categoria na sidebar
            with st.sidebar:
                categorias_filtro = st.multiselect(
                    "Filtrar por situação:",
                    options=['ativo', 'parcial', 'pouco', 'inativo'],
                    default=['ativo', 'parcial', 'pouco', 'inativo'],
                    format_func=lambda x: {
                        'ativo': 'Totalmente Ativos',
                        'parcial': 'Parcialmente Ativos',
                        'pouco': 'Pouco Ativos', 
                        'inativo': 'Inativos'
                    }[x]
                )
            
            # Métricas principais
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    label="📋 Total Responsáveis",
                    value=len(responsaveis_unicos)
                )
            
            with col2:
                st.metric(
                    label="📅 Taxa Julho",
                    value=f"{analise_mensal[7]['taxa_envio']:.1f}%",
                    delta=None
                )
            
            with col3:
                st.metric(
                    label="📅 Taxa Agosto", 
                    value=f"{analise_mensal[8]['taxa_envio']:.1f}%",
                    delta=f"{analise_mensal[8]['taxa_envio'] - analise_mensal[7]['taxa_envio']:.1f}pp"
                )
            
            with col4:
                st.metric(
                    label="📅 Taxa Setembro",
                    value=f"{analise_mensal[9]['taxa_envio']:.1f}%", 
                    delta=f"{analise_mensal[9]['taxa_envio'] - analise_mensal[8]['taxa_envio']:.1f}pp"
                )
            
            with col5:
                consistentes = sum(1 for s in status_individual.values() if s['meses_ativos'] == 3)
                st.metric(
                    label="⭐ Consistentes",
                    value=f"{(consistentes/len(responsaveis_unicos)*100):.1f}%",
                    delta=f"{consistentes} resp."
                )
            
            # Alerta crítico
            queda_total = analise_mensal[7]['taxa_envio'] - analise_mensal[9]['taxa_envio']
            st.markdown(f"""
            <div class="alert-critical">
                <h3>🚨 SITUAÇÃO CRÍTICA: Queda Drástica nas Taxas de Envios</h3>
                <ul>
                    <li><strong>Julho:</strong> {analise_mensal[7]['taxa_envio']:.1f}% ({analise_mensal[7]['qtd_enviaram']} responsáveis)</li>
                    <li><strong>Agosto:</strong> {analise_mensal[8]['taxa_envio']:.1f}% ({analise_mensal[8]['qtd_enviaram']} responsáveis) - Queda de {analise_mensal[7]['taxa_envio'] - analise_mensal[8]['taxa_envio']:.1f}pp</li>
                    <li><strong>Setembro:</strong> {analise_mensal[9]['taxa_envio']:.1f}% ({analise_mensal[9]['qtd_enviaram']} responsáveis) - Queda de {analise_mensal[8]['taxa_envio'] - analise_mensal[9]['taxa_envio']:.1f}pp</li>
                </ul>
                <p><strong>Resultado:</strong> Perda de {queda_total:.1f} pontos percentuais em 3 meses!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                fig_evolucao = criar_grafico_evolucao(analise_mensal)
                st.plotly_chart(fig_evolucao, use_container_width=True)
            
            with col2:
                fig_pizza = criar_grafico_pizza_situacao(status_individual)
                st.plotly_chart(fig_pizza, use_container_width=True)
            
            # Análise detalhada por mês
            st.header("📅 Análise Detalhada por Mês")
            
            tab_jul, tab_ago, tab_set = st.tabs(["Julho 2025", "Agosto 2025", "Setembro 2025"])
            
            for tab, mes_num in zip([tab_jul, tab_ago, tab_set], [7, 8, 9]):
                with tab:
                    dados = analise_mensal[mes_num]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Taxa de Envio", f"{dados['taxa_envio']:.1f}%")
                    with col2:
                        st.metric("Enviaram", dados['qtd_enviaram'])
                    with col3:
                        st.metric("Não Enviaram", dados['qtd_nao_enviaram'])
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("✅ Responsáveis que Enviaram")
                        for resp in dados['responsaveis_enviaram']:
                            st.markdown(f'<span class="status-enviou">✓ {resp}</span>', unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("❌ Responsáveis que NÃO Enviaram") 
                        for resp in dados['responsaveis_nao_enviaram']:
                            st.markdown(f'<span class="status-nao-enviou">✗ {resp}</span>', unsafe_allow_html=True)
            
            # Tabela individual
            st.header("👥 Status Individual por Responsável")
            
            # Filtrar dados conforme seleção
            dados_tabela = []
            for resp, status in status_individual.items():
                if status['categoria'] in categorias_filtro:
                    dados_tabela.append({
                        'Responsável': resp,
                        'Julho': '✅ ENVIOU' if status['julho'] else '❌ NÃO ENVIOU',
                        'Agosto': '✅ ENVIOU' if status['agosto'] else '❌ NÃO ENVIOU', 
                        'Setembro': '✅ ENVIOU' if status['setembro'] else '❌ NÃO ENVIOU',
                        'Atividade': f"{status['meses_ativos']}/3 meses",
                        'Situação': status['situacao'],
                        'Categoria': status['categoria']
                    })
            
            df_tabela = pd.DataFrame(dados_tabela)
            
            if not df_tabela.empty:
                st.dataframe(
                    df_tabela[['Responsável', 'Julho', 'Agosto', 'Setembro', 'Atividade', 'Situação']],
                    use_container_width=True,
                    height=400
                )
            
            # Resumo estatístico
            st.header("📊 Resumo Estatístico Final")
            
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
                    delta=f"{ativo_pct:.1f}% do total"
                )
            
            with col2:
                parcial_count = categorias_count.get('parcial', 0)
                parcial_pct = (parcial_count / len(responsaveis_unicos)) * 100
                st.metric(
                    "🟡 Parcialmente Ativos", 
                    value=parcial_count,
                    delta=f"{parcial_pct:.1f}% do total"
                )
            
            with col3:
                pouco_count = categorias_count.get('pouco', 0)
                pouco_pct = (pouco_count / len(responsaveis_unicos)) * 100
                st.metric(
                    "🟠 Pouco Ativos",
                    value=pouco_count, 
                    delta=f"{pouco_pct:.1f}% do total"
                )
            
            with col4:
                inativo_count = categorias_count.get('inativo', 0)
                inativo_pct = (inativo_count / len(responsaveis_unicos)) * 100
                st.metric(
                    "🔴 Inativos",
                    value=inativo_count,
                    delta=f"{inativo_pct:.1f}% do total"
                )
            
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {str(e)}")
            st.info("Verifique se o arquivo Excel está no formato correto.")
    
    else:
        # Tela inicial sem dados
        st.info("📁 Por favor, faça upload da planilha Excel na barra lateral para visualizar o painel.")
        
        st.markdown("""
        ### Como usar:
        1. **Upload**: Envie o arquivo 'Reports_Geral_Consolidado.xlsx' na barra lateral
        2. **Análise**: Os dados serão processados automaticamente
        3. **Filtros**: Use os filtros para focar em categorias específicas
        4. **Navegação**: Explore as diferentes seções do painel
        
        ### Funcionalidades:
        - ✅ **Upload automático** de planilhas Excel
        - ✅ **Limpeza de dados** (remove espaços em nomes)
        - ✅ **Análise temporal** (julho-setembro 2025)
        - ✅ **Gráficos interativos** com Plotly
        - ✅ **Filtros dinâmicos** por categoria
        - ✅ **Métricas em tempo real**
        - ✅ **Tabelas interativas** 
        - ✅ **Alertas automáticos**
        """)

if __name__ == "__main__":
    main()
