import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Sistema de Estoque e Vendas", layout="wide", page_icon="💎")

# --- CONEXÃO REST PURA (À prova de travamentos/hangs no Streamlit) ---
def init_headers():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    
    if "SUA_" in url or "SUA_" in key or not url.startswith("http"):
        return None, None
        
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    # O REST do Supabase roda na rota /rest/v1/ do seu URL base.
    base_url = f"{url}/rest/v1"
    
    return base_url, headers

url_base, headers = init_headers()

if not url_base or not headers:
    st.error("⚠️ Banco de dados não configurado ou credenciais inválidas. Verifique o seu `.streamlit/secrets.toml` (local) ou o painel 'Secrets' (no Cloud). Atenção: A URL deve começar com https:// e a KEY não pode ser a de exemplo.")
    st.stop()

# Helper Functions via Requests
def get_produtos():
    try:
        response = requests.get(f"{url_base}/produtos?select=*", headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro de conexão (Produtos): {e}")
        return []

def get_vendas():
    try:
        response = requests.get(f"{url_base}/vendas?select=*", headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro de conexão (Vendas): {e}")
        return []

def update_produto(codigo, dados):
    requests.patch(f"{url_base}/produtos?codigo=eq.{codigo}", headers=headers, json=dados, timeout=5)

def insert_produto(dados):
    requests.post(f"{url_base}/produtos", headers=headers, json=dados, timeout=5)

def insert_venda(dados):
    requests.post(f"{url_base}/vendas", headers=headers, json=dados, timeout=5)

CATEGORIAS = ["Brinco", "Anel", "Pulseira", "Choker", "Tornozeleira"]

st.sidebar.title("💎 Gestão de Joias")
page = st.sidebar.radio("Navegação", ["📊 Dashboard Financeiro", "📦 Produtos e Custos", "🛒 Registro de Vendas"])

if page == "📊 Dashboard Financeiro":
    st.title("Dashboard Financeiro")
    
    produtos = get_produtos()
    vendas = get_vendas()
    
    if not produtos:
        st.info("Nenhum produto em estoque.")
    else:
        df_produtos = pd.DataFrame(produtos)
        df_produtos['custo_total'] = df_produtos['custo_fabricacao'] + df_produtos['custo_banho']
        
        # Finance metrics
        valor_investido = (df_produtos['custo_total'] * df_produtos['estoque']).sum()
        receita_esperada = (df_produtos['valor_venda'] * df_produtos['estoque']).sum()
        lucro_projetado_estoque = receita_esperada - valor_investido
        
        lucro_real_total = 0.0
        receita_real_total = 0.0
        
        if vendas:
            df_vendas = pd.DataFrame(vendas)
            lucro_real_total = df_vendas['lucro_real_total'].sum()
            receita_real_total = (df_vendas['valor_venda_unitario'] * df_vendas['quantidade']).sum()
            
        col1, col2, col3 = st.columns(3)
        col1.info(f"**Valor Investido em Estoque**\n\nR$ {valor_investido:,.2f}")
        col2.info(f"**Expectativa de Receita (Vendas)**\n\nR$ {receita_esperada:,.2f}")
        col3.success(f"**Lucro Projetado (Estoque)**\n\nR$ {lucro_projetado_estoque:,.2f}")
        
        st.divider()
        st.subheader("Performance Real (Vendas Realizadas)")
        col4, col5 = st.columns(2)
        col4.metric("Receita Total de Vendas", f"R$ {receita_real_total:,.2f}")
        col5.metric("Lucro Real Total (Realizado)", f"R$ {lucro_real_total:,.2f}")

elif page == "📦 Produtos e Custos":
    st.title("Gerenciamento de Produtos")
    
    tab1, tab2, tab3 = st.tabs(["Lista e Edição", "Cadastrar Novo", "Calculadora de Banho"])
    
    with tab1:
        st.subheader("Estoque Atual")
        produtos = get_produtos()
        if produtos:
            df = pd.DataFrame(produtos)
            df['Custo Total'] = df['custo_fabricacao'] + df['custo_banho']
            # Evita divisão por zero
            df['Margem Lucro (%)'] = df.apply(lambda row: ((row['valor_venda'] - row['Custo Total']) / row['Custo Total'] * 100) if row['Custo Total'] > 0 else 0, axis=1)
            
            df_display = df[['codigo', 'categoria', 'estoque', 'custo_fabricacao', 'custo_banho', 'Custo Total', 'valor_venda', 'Margem Lucro (%)']]
            st.dataframe(df_display.style.format({
                'custo_fabricacao': 'R$ {:.2f}',
                'custo_banho': 'R$ {:.2f}',
                'Custo Total': 'R$ {:.2f}',
                'valor_venda': 'R$ {:.2f}',
                'Margem Lucro (%)': '{:.1f}%'
            }), use_container_width=True)
            
            st.divider()
            st.subheader("Editar Valores ou Estoque")
            st.write("Atualize custos dinamicamente. A margem de lucro será recalculada.")
            
            cod_edit = st.selectbox("Selecione pela Referência/Código:", df['codigo'].tolist())
            if cod_edit:
                p_edit = next(p for p in produtos if p['codigo'] == cod_edit)
                with st.form("form_edit"):
                    c1, c2 = st.columns(2)
                    cat_edit = c1.selectbox("Categoria Obrigatória", CATEGORIAS, index=CATEGORIAS.index(p_edit['categoria']) if p_edit['categoria'] in CATEGORIAS else 0)
                    estoque_edit = c2.number_input("Estoque", value=int(p_edit['estoque']), step=1, min_value=0)
                    
                    cf_edit = c1.number_input("Custo de Fabricação (R$)", value=float(p_edit['custo_fabricacao']), step=0.1, help="Fundição, metal, cravação, confecção bruta da peça.")
                    cb_edit = c2.number_input("Custo de Banho (R$)", value=float(p_edit['custo_banho']), step=0.1)
                    
                    custo_total_edit = cf_edit + cb_edit
                    st.write(f"**Custo Total (Fabricação + Banho):** R$ {custo_total_edit:.2f}")
                    
                    vv_edit = st.number_input("Valor de Venda Atualizado (R$)", value=float(p_edit['valor_venda']), step=0.1)
                    margem = ((vv_edit - custo_total_edit) / custo_total_edit * 100) if custo_total_edit > 0 else 0
                    st.write(f"**Nova Margem de Lucro Projetada:** {margem:.1f}%")
                    
                    if st.form_submit_button("Salvar Edição"):
                        update_produto(cod_edit, {
                            "categoria": cat_edit,
                            "estoque": estoque_edit,
                            "custo_fabricacao": cf_edit,
                            "custo_banho": cb_edit,
                            "valor_venda": vv_edit
                        })
                        st.success("Valores atualizados com sucesso!")
                        st.rerun()
        else:
            st.info("Nenhum produto cadastrado no banco de dados.")
            
    with tab2:
        st.subheader("Cadastrar Novo Produto")
        with st.form("form_novo"):
            codigo = st.text_input("Código do Produto (ID Único)")
            categoria = st.selectbox("Categoria Rigorosa (Obrigatória)", CATEGORIAS)
            
            st.write("Composição de Custos:")
            col1, col2 = st.columns(2)
            custo_fab = col1.number_input("Custo de Fabricação (R$)", min_value=0.0, step=0.1, help="Gasto na confecção bruta (fundição, cravação, modelagem, etc)")
            custo_banho = col2.number_input("Custo de Banho (R$)", min_value=0.0, step=0.1, help="Cálculo do banho a ser adicionado")
            
            valor_venda = st.number_input("Valor de Venda (Preço Final) (R$)", min_value=0.0, step=0.1)
            estoque = st.number_input("Quantidade Inicial em Estoque", min_value=0, step=1)
            
            if st.form_submit_button("Realizar Cadastro do Produto"):
                if not codigo:
                    st.error("Insira um código identificador válido do produto.")
                else:
                    existe = requests.get(f"{url_base}/produtos?codigo=eq.{codigo}&select=codigo", headers=headers).json()
                    if existe:
                        st.error("Um produto com este mesmo código já foi cadastrado no sistema.")
                    else:
                        insert_produto({
                            "codigo": codigo,
                            "categoria": categoria,
                            "custo_fabricacao": custo_fab,
                            "custo_banho": custo_banho,
                            "valor_venda": valor_venda,
                            "estoque": estoque
                        })
                        st.success("Produto adicionado com sucesso ao catálogo!")
                        st.rerun()

    with tab3:
        st.subheader("Calculadora de Custo de Banho")
        st.write("Utilize este módulo para descobrir e estipular o custo do banho a ser repassado.")
        
        tipo_calc = st.radio("Selecione o Método", ["Por Peso (Grama)", "Por Milésimo (Peça + Camada)"])
        peso = st.number_input("Peso Total da Peça ou Lote (em gramas)", min_value=0.0, step=0.1)
        
        custo_final = 0.0
        if tipo_calc == "Por Peso (Grama)":
            valor_grama = st.number_input("Valor cobrado pela galvanoplastia por Grama (R$)", min_value=0.0, step=0.1)
            custo_final = peso * valor_grama
        else:
            milesimos = st.number_input("Quantidade de Milésimos", min_value=0.0, step=1.0)
            valor_mil = st.number_input("Valor cobrado por Milésimo aplicado na peça (R$)", min_value=0.0, step=0.1)
            custo_final = peso * milesimos * valor_mil
            
        st.info(f"O **custo total do banho calculado** para este orçamento é: **R$ {custo_final:.2f}**")
        st.caption("Atenção: A calculadora é uma ferramenta auxiliar. Você pode inserir o resultado equivalente de forma manual no campo de Custo de Banho, na tela de edição ou cadastro do produto.")

elif page == "🛒 Registro de Vendas":
    st.title("Registrar Nova Venda")
    
    produtos = get_produtos()
    if not produtos:
        st.warning("Seu catálogo está vazio. Cadastre novos produtos primeiro.")
    else:
        df_produtos = pd.DataFrame(produtos)
        disp = df_produtos[df_produtos['estoque'] > 0]
        
        st.write("Efetue a venda para deduzir automaticamente o estoque e contabilizar o Lucro Real.")
        
        with st.form("form_venda"):
            if disp.empty:
                st.error("Você não possui produtos com disponibilidade de estoque no sistema!")
            else:
                cod_venda = st.selectbox("Busque e Selecione o Produto para Compra", disp['codigo'].tolist())
                prod = disp[disp['codigo'] == cod_venda].iloc[0]
                
                qtd_venda = st.number_input("Quantidade a Ser Vendida", min_value=1, max_value=int(prod['estoque']), step=1)
                
                cf, cb, vv = float(prod['custo_fabricacao']), float(prod['custo_banho']), float(prod['valor_venda'])
                
                st.write(f"🏷️ **Preço de Venda Unitário Total:** R$ {vv:.2f}")
                
                desconto = st.number_input("Desconto Concedido nesta Operação (R$)", min_value=0.0, step=0.1, value=0.0, help="Valor bruto de desconto que diminui a receita desta venda e o lucro final.")
                
                if st.form_submit_button("Confirmar Venda e Dar Baixa de Estoque"):
                    custo_total_operacao = (cf + cb) * qtd_venda
                    receita_venda = (vv * qtd_venda) - desconto
                    lucro_real = receita_venda - custo_total_operacao
                    
                    novo_estoque = int(prod['estoque']) - qtd_venda
                    # Dar baixa no estoque da tabela de produtos (sincronizado automaticamente)
                    update_produto(cod_venda, {"estoque": novo_estoque})
                    
                    # Registrar log/transação de Venda
                    insert_venda({
                        "codigo_produto": cod_venda,
                        "quantidade": int(qtd_venda),
                        "custo_fabricacao_unitario": cf,
                        "custo_banho_unitario": cb,
                        "valor_venda_unitario": vv - (desconto/qtd_venda if qtd_venda > 0 else 0), # Ajusta métricas se tiver desconto
                        "lucro_real_total": lucro_real
                    })
                    
                    st.success(f"Venda registrada com sucesso! Seu estoque foi atualizado para {novo_estoque} peças. O seu Lucro Real contabilizado foi de R$ {lucro_real:.2f}.")
                    st.rerun()
                    
        st.divider()
        st.subheader("Histórico do Desempenho de Vendas")
        vendas = get_vendas()
        if vendas:
            df_v = pd.DataFrame(vendas)
            df_v = df_v.sort_values(by="created_at", ascending=False)
            
            # Formatação apropriada de datas
            # Note: The database times are timezone aware (UTC text usually).
            # Convert to Pandas Datetime standard.
            df_v['criado_em'] = pd.to_datetime(df_v['created_at']).dt.strftime('%d/%m/%Y %H:%M')
            
            df_v_display = df_v[['criado_em', 'codigo_produto', 'quantidade', 'lucro_real_total']].rename(columns={
                'criado_em': 'Data da Venda (UTC)',
                'codigo_produto': 'Cód. Venda/Produto',
                'quantidade': 'Qtd. de Peças',
                'lucro_real_total': 'Lucro Real Líquido (R$)'
            })
            st.dataframe(df_v_display.style.format({'Lucro Real Líquido (R$)': 'R$ {:.2f}'}), use_container_width=True)
