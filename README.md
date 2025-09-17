# 📊 Painel de Acompanhamento de Reports - Streamlit

Um aplicativo web interativo para acompanhar envios de reports dos responsáveis, com análise temporal de julho a setembro de 2025.

## 🚀 Funcionalidades

- ✅ **Upload de planilhas Excel** (.xlsx, .xls)
- ✅ **Processamento automático** de dados
- ✅ **Limpeza de dados** (remove espaços em branco dos nomes)
- ✅ **Análise temporal** completa (3 meses)
- ✅ **Gráficos interativos** com Plotly
- ✅ **Filtros dinâmicos** por categoria de responsável
- ✅ **Métricas em tempo real**
- ✅ **Alertas automáticos** para situações críticas
- ✅ **Tabelas interativas** com todos os dados
- ✅ **Interface responsiva** e profissional

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Conta no GitHub (gratuita)
- Conta no Streamlit Cloud (gratuita)

## 🛠️ Instalação Local

### 1. Clone ou baixe os arquivos
```bash
git clone <seu-repositorio>
cd painel-reports-streamlit
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Execute o aplicativo
```bash
streamlit run app.py
```

### 4. Acesse no navegador
O aplicativo será aberto automaticamente em: `http://localhost:8501`

## 🌐 Publicar no Streamlit Cloud (GRATUITO)

### Passo 1: Preparar arquivos
Certifique-se de ter estes arquivos na pasta:
- `app.py` (código principal)
- `requirements.txt` (dependências)
- `README.md` (este arquivo)
- `.streamlit/config.toml` (configurações)

### Passo 2: Criar repositório no GitHub
1. Acesse [GitHub.com](https://github.com)
2. Clique em "New repository"
3. Nome: `painel-reports-streamlit`
4. Marque "Public"
5. Clique "Create repository"

### Passo 3: Upload dos arquivos
1. Clique em "uploading an existing file"
2. Arraste todos os arquivos (incluindo pasta .streamlit)
3. Commit message: "Initial commit - Painel de Reports"
4. Clique "Commit new files"

### Passo 4: Deploy no Streamlit Cloud
1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique "Sign up" com sua conta GitHub
3. Clique "New app"
4. Selecione:
   - **Repository**: `seu-usuario/painel-reports-streamlit`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: `painel-reports` (ou outro nome único)
5. Clique "Deploy!"

### Passo 5: Aguardar deploy
- O deploy levará 2-5 minutos
- Você receberá uma URL única como: `https://painel-reports.streamlit.app`

## 📱 Como usar o aplicativo

### 1. Upload de dados
- Na barra lateral, clique "Browse files"
- Selecione seu arquivo Excel (`Reports_Geral_Consolidado.xlsx`)
- Os dados serão processados automaticamente

### 2. Visualizar métricas
- **Cards superiores**: Resumo das taxas por mês
- **Alerta crítico**: Situações que precisam atenção
- **Gráficos**: Evolução temporal e distribuição por situação

### 3. Análise detalhada
- **Tabs por mês**: Veja quem enviou/não enviou por mês
- **Filtros**: Filtre por categoria (ativos, parciais, etc.)
- **Tabela**: Status individual de cada responsável

### 4. Atualização dos dados
- Basta fazer novo upload da planilha atualizada
- Todos os gráficos e métricas são atualizados automaticamente

## 🔧 Personalização

### Modificar cores/estilo
Edite a seção CSS no arquivo `app.py`:
```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        # Modifique as cores aqui
    }
</style>
""", unsafe_allow_html=True)
```

### Adicionar novos meses
No arquivo `app.py`, modifique:
```python
# Linha ~87: Adicione novos meses
meses = {7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro'}

# Linha ~55: Modifique o filtro de período
dados_periodo = df[(df['ANO'] == 2025) & (df['MES'] >= 7) & (df['MES'] <= 10)]
```

### Modificar estrutura da planilha
Se sua planilha tiver colunas diferentes, modifique a função `processar_dados()`:
```python
def processar_dados(df):
    # Ajuste os nomes das colunas aqui
    df['RESPONSÁVEL'] = df['SEU_NOME_DA_COLUNA'].str.strip()
    df['DATA'] = pd.to_datetime(df['SUA_COLUNA_DATA'])
    return df
```

## 🆘 Solução de Problemas

### Erro ao fazer upload
- **Problema**: "Error processing file"
- **Solução**: Verifique se o arquivo Excel tem as colunas: `RESPONSÁVEL`, `DATA`

### App não carrega no Streamlit Cloud
- **Problema**: Deploy falhou
- **Solução**: Verifique se `requirements.txt` tem todas as dependências

### Gráficos não aparecem
- **Problema**: Plotly não renderiza
- **Solução**: Recarregue a página ou verifique conexão de internet

### Dados não processam
- **Problema**: Planilha vazia ou formato incorreto
- **Solução**: Verifique se há dados nos meses julho-setembro de 2025

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique as seções acima
2. Teste localmente primeiro (`streamlit run app.py`)
3. Confira se todos os arquivos estão no GitHub
4. Verifique os logs no Streamlit Cloud

## 🔄 Atualizações

Para atualizar o app publicado:
1. Modifique os arquivos localmente
2. Teste com `streamlit run app.py`
3. Faça commit no GitHub
4. O Streamlit Cloud atualizará automaticamente

## 💡 Próximos Passos

Melhorias sugeridas:
- [ ] Adicionar download de relatórios em PDF
- [ ] Implementar notificações por email
- [ ] Criar dashboard executivo
- [ ] Adicionar análise de tendências
- [ ] Implementar autenticação de usuários
- [ ] Conectar com banco de dados

---

🎉 **Parabéns!** Seu painel está pronto para ser usado pelos clientes!

**URL do app**: `https://seu-app.streamlit.app`