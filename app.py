import streamlit as st
import requests
import pandas as pd
import base64
from datetime import datetime

st.set_page_config(page_title="Rosemie - Gestão Joias", layout="wide", page_icon="🌹")

# --- CUSTOM CSS (Rosemie Elegance) ---
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; }
    h1, h2, h3 { color: #8C6A5D; font-family: 'Optima', 'Georgia', serif; font-weight: 500;}
    .stButton>button { border-color: #D4B2A7; color: #8C6A5D; }
    .stButton>button:hover { background-color: #F8F4F1; border-color: #8C6A5D; color: #5C433A;}
    </style>
""", unsafe_allow_html=True)

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

url_base_global, headers_global = init_headers()

if not url_base_global or not headers_global:
    st.error("⚠️ Banco de dados não configurado ou credenciais inválidas. Verifique o seu `.streamlit/secrets.toml` (local) ou o painel 'Secrets' (no Cloud). Atenção: A URL deve começar com https:// e a KEY não pode ser a de exemplo.")
    st.stop()

def get_image_base64(uploaded_file):
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        mime_type = uploaded_file.type
        encoded = base64.b64encode(file_bytes).decode()
        return f"data:{mime_type};base64,{encoded}"
    return ""

# Helper Functions via Requests
def get_produtos():
    url_base, headers = init_headers()
    try:
        response = requests.get(f"{url_base}/produtos?select=*", headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro de conexão (Produtos): {e}")
        return []

def get_vendas():
    url_base, headers = init_headers()
    try:
        response = requests.get(f"{url_base}/vendas?select=*", headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro de conexão (Vendas): {e}")
        return []

def update_produto(codigo, dados):
    url_base, headers = init_headers()
    try:
        response = requests.patch(f"{url_base}/produtos?codigo=eq.{codigo}", headers=headers, json=dados, timeout=15)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        st.error(f"Erro ao atualizar: {response.text}")
        return False
    except Exception as e:
        st.error(f"Erro de conexão ao atualizar: {e}")
        return False

def delete_produto(codigo):
    url_base, headers = init_headers()
    try:
        response = requests.delete(f"{url_base}/produtos?codigo=eq.{codigo}", headers=headers, timeout=15)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        st.error(f"Erro do Banco (Remoção): {response.text}")
        return False
    except Exception as e:
        st.error(f"Erro de conexão (Remoção): {e}")
        return False

def insert_produto(dados):
    url_base, headers = init_headers()
    try:
        response = requests.post(f"{url_base}/produtos", headers=headers, json=dados, timeout=15)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        st.error(f"Erro do Banco (Cadastro): {response.text}")
        return False
    except Exception as e:
        st.error(f"Erro de conexão (Cadastro): {e}")
        return False

def insert_venda(dados):
    url_base, headers = init_headers()
    try:
        response = requests.post(f"{url_base}/vendas", headers=headers, json=dados, timeout=15)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        st.error(f"Erro do Banco (Venda): {response.text}")
        return False
    except Exception as e:
        st.error(f"Erro de conexão (Venda): {e}")
        return False

def update_venda(id_venda, dados):
    url_base, headers = init_headers()
    try:
        response = requests.patch(f"{url_base}/vendas?id=eq.{id_venda}", headers=headers, json=dados, timeout=15)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        st.error(f"Erro ao atualizar: {response.text}")
        return False
    except Exception as e:
        st.error(f"Erro de conexão ao atualizar: {e}")
        return False

CATEGORIAS = ["Brinco", "Anel", "Pulseira", "Choker", "Tornozeleira"]

st.sidebar.title("🌹 Rosemie - Painel")
page = st.sidebar.radio("Navegação", ["📊 Dashboard Financeiro", "📦 Produtos e Custos", "🛒 Registro de Vendas", "👥 Área de Clientes"])

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
            
            # Filtro por Categoria
            filtro_cat = st.multiselect("Filtrar por Categoria", CATEGORIAS, help="Deixe vazio para mostrar todas as categorias.")
            df_filtrado = df.copy()
            if filtro_cat:
                df_filtrado = df_filtrado[df_filtrado['categoria'].isin(filtro_cat)]
                
            if df_filtrado.empty:
                st.info("Nenhum produto encontrado para o filtro selecionado.")
            else:
                df_filtrado['Custo Total'] = df_filtrado['custo_fabricacao'] + df_filtrado['custo_banho']
                # Evita divisão por zero
                df_filtrado['Margem Lucro (%)'] = df_filtrado.apply(lambda row: ((row['valor_venda'] - row['Custo Total']) / row['Custo Total'] * 100) if row['Custo Total'] > 0 else 0, axis=1)
                
                if 'foto_url' in df_filtrado.columns:
                    df_display = df_filtrado[['codigo', 'foto_url', 'categoria', 'estoque', 'custo_fabricacao', 'custo_banho', 'Custo Total', 'valor_venda', 'Margem Lucro (%)']]
                else:
                    df_display = df_filtrado[['codigo', 'categoria', 'estoque', 'custo_fabricacao', 'custo_banho', 'Custo Total', 'valor_venda', 'Margem Lucro (%)']]
                    
                config_fmt = {
                    'custo_fabricacao': 'R$ {:.2f}',
                    'custo_banho': 'R$ {:.2f}',
                    'Custo Total': 'R$ {:.2f}',
                    'valor_venda': 'R$ {:.2f}',
                    'Margem Lucro (%)': '{:.1f}%'
                }
                
                if 'foto_url' in df_filtrado.columns:
                    st.dataframe(df_display.style.format(config_fmt), column_config={"foto_url": st.column_config.ImageColumn("Foto / Imagem")}, use_container_width=True)
                else:
                    st.dataframe(df_display.style.format(config_fmt), use_container_width=True)
            
            st.divider()
            st.subheader("Opções de Produto: Editar, Alterar Código ou Remover")
            st.write("Atualize propriedades do produto. A margem de lucro será recalculada.")
            
            cod_edit = st.selectbox("Selecione pela Referência/Código:", df['codigo'].tolist())
            if cod_edit:
                p_edit = next(p for p in produtos if p['codigo'] == cod_edit)
                
                with st.form("form_edit"):
                    st.write("**Edição de Dados**")
                    novo_codigo_edit = st.text_input("Código do Produto (Permite alterar)", value=p_edit['codigo'])
                    c1, c2 = st.columns(2)
                    cat_edit = c1.selectbox("Categoria Obrigatória", CATEGORIAS, index=CATEGORIAS.index(p_edit['categoria']) if p_edit['categoria'] in CATEGORIAS else 0)
                    estoque_edit = c2.number_input("Estoque", value=int(p_edit['estoque']), step=1, min_value=0)
                    
                    st.write("**Atualizar Imagem da Peça (Opcional)**")
                    foto_upload_edit = st.file_uploader("Envie a Foto do seu computador ou celular", type=["png", "jpg", "jpeg", "webp"], key=f"up_{cod_edit}")
                    foto_edit = st.text_input("Ou cole a URL direta da Foto", value=p_edit.get('foto_url', ''), help="Use o Envio de Foto acima OU cole um link aqui.", key=f"url_{cod_edit}")
                    
                    cf_edit = c1.number_input("Custo de Fabricação (R$)", value=float(p_edit['custo_fabricacao']), step=0.1, help="Fundição, metal, cravação, confecção bruta da peça.")
                    cb_edit = c2.number_input("Custo de Banho (R$)", value=float(p_edit['custo_banho']), step=0.1)
                    
                    custo_total_edit = cf_edit + cb_edit
                    st.write(f"**Custo Total (Fabricação + Banho):** R$ {custo_total_edit:.2f}")
                    
                    vv_edit = st.number_input("Valor de Venda Atualizado (R$)", value=float(p_edit['valor_venda']), step=0.1)
                    margem = ((vv_edit - custo_total_edit) / custo_total_edit * 100) if custo_total_edit > 0 else 0
                    st.write(f"**Nova Margem de Lucro Projetada:** {margem:.1f}%")
                    
                    if st.form_submit_button("Salvar Edição", type="primary"):
                        if not novo_codigo_edit:
                            st.error("O código não pode ficar vazio.")
                        else:
                            url_base, headers = init_headers()
                            if novo_codigo_edit != cod_edit:
                                existe = requests.get(f"{url_base}/produtos?codigo=eq.{novo_codigo_edit}&select=codigo", headers=headers, timeout=15).json()
                                if existe:
                                    st.error("O novo código informado já existe em outro produto!")
                                    st.stop()
                                    
                            final_foto_url = foto_edit
                            if foto_upload_edit is not None:
                                final_foto_url = get_image_base64(foto_upload_edit)
                                
                            sucesso = update_produto(cod_edit, {
                                "codigo": novo_codigo_edit,
                                "categoria": cat_edit,
                                "foto_url": final_foto_url,
                                "estoque": estoque_edit,
                                "custo_fabricacao": cf_edit,
                                "custo_banho": cb_edit,
                                "valor_venda": vv_edit
                            })
                            if sucesso:
                                st.success("Produto atualizado com sucesso!")
                                st.rerun()
                                
                st.write("**Remover Produto**")
                with st.form("form_delete"):
                    st.warning(f"Tem certeza que deseja remover o produto **{cod_edit}** do catálogo? Esta ação não pode ser desfeita.")
                    if st.form_submit_button("❌ Remover Produto"):
                        if delete_produto(cod_edit):
                            st.success(f"Produto {cod_edit} removido com sucesso!")
                            st.rerun()
        else:
            st.info("Nenhum produto cadastrado no banco de dados.")
            
    with tab2:
        st.subheader("Cadastrar Novo Produto")
        with st.form("form_novo"):
            codigo = st.text_input("Código do Produto (ID Único)")
            categoria = st.selectbox("Categoria Rigorosa (Obrigatória)", CATEGORIAS)
            
            st.divider()
            st.write("**Imagem do Produto** (Opcional)")
            foto_upload = st.file_uploader("Fazer Upload da Foto", type=["png", "jpg", "jpeg", "webp"])
            foto_url = st.text_input("Ou cole um URL válido da internet caso a foto já esteja online")
            st.divider()
            
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
                    url_base, headers = init_headers()
                    existe = requests.get(f"{url_base}/produtos?codigo=eq.{codigo}&select=codigo", headers=headers, timeout=15).json()
                    if existe:
                        st.error("Um produto com este mesmo código já foi cadastrado no sistema.")
                    else:
                        final_foto_url = foto_url
                        if foto_upload is not None:
                            final_foto_url = get_image_base64(foto_upload)
                            
                        sucesso = insert_produto({
                            "codigo": codigo,
                            "categoria": categoria,
                            "foto_url": final_foto_url,
                            "custo_fabricacao": custo_fab,
                            "custo_banho": custo_banho,
                            "valor_venda": valor_venda,
                            "estoque": estoque
                        })
                        if sucesso:
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
                
                st.divider()
                st.write("Dados do Cliente e Pagamento")
                cliente_nome = st.text_input("Nome do Cliente", help="Nome do cliente para registrar histórico e garantia.")
                data_compra = st.date_input("Data da Compra", value=datetime.today())
                tipo_pagamento = st.selectbox("Forma de Pagamento", ["PIX", "Cartão de Crédito", "Cartão de Débito", "Dinheiro"])
                status_pagamento = st.selectbox("Status do Pagamento", ["Pago", "Pendente"])
                
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
                        "lucro_real_total": lucro_real,
                        "cliente_nome": cliente_nome,
                        "data_compra": data_compra.strftime("%Y-%m-%d"),
                        "tipo_pagamento": tipo_pagamento,
                        "status_pagamento": status_pagamento
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

elif page == "👥 Área de Clientes":
    st.title("👥 Área de Clientes e Garantia")
    
    vendas = get_vendas()
    if not vendas:
        st.info("Nenhuma venda registrada ainda.")
    else:
        df_vendas = pd.DataFrame(vendas)
        
        if 'cliente_nome' not in df_vendas.columns:
            st.warning("Ainda não há clientes com nomes registrados nas vendas. Registre uma nova venda para criar a base ou atualize as colunas no banco de dados.")
        else:
            # Filtra vendas que têm nome de cliente válido
            df_clientes = df_vendas[df_vendas['cliente_nome'].notna() & (df_vendas['cliente_nome'] != '')]
            
            if df_clientes.empty:
                st.info("Nenhum cliente registrado por nome nas vendas.")
            else:
                clientes_unicos = df_clientes['cliente_nome'].unique()
                cliente_selecionado = st.selectbox("Selecione o Cliente para Buscar", sorted(clientes_unicos))
                
                vendas_cliente = df_clientes[df_clientes['cliente_nome'] == cliente_selecionado].copy()
                
                # Calcular métricas (receita gerada pelas compras do cliente)
                vendas_cliente['valor_venda_unitario'] = vendas_cliente['valor_venda_unitario'].astype(float)
                vendas_cliente['quantidade'] = vendas_cliente['quantidade'].astype(int)
                
                total_gasto = (vendas_cliente['valor_venda_unitario'] * vendas_cliente['quantidade']).sum()
                
                col1, col2 = st.columns(2)
                col1.metric("Total Gasto pelo Cliente", f"R$ {total_gasto:,.2f}")
                col2.metric("Quantidade de Peças Compradas", f"{vendas_cliente['quantidade'].sum()} peça(s)")
                
                st.divider()
                st.subheader("Histórico de Compras e Garantia")
                st.write("Verifique abaixo as peças adquiridas, data da compra (garantia de 6 meses) e o status do pagamento.")
                
                if 'data_compra' in vendas_cliente.columns:
                    vendas_cliente['data_ordem'] = vendas_cliente['data_compra'].fillna(vendas_cliente['created_at'])
                    vendas_cliente = vendas_cliente.sort_values(by="data_ordem", ascending=False)

                for _, venda in vendas_cliente.iterrows():
                    venda_id = venda.get('id', None)
                    cod_prod = venda.get('codigo_produto', 'Produto Desconhecido')
                    
                    dt_compra = venda.get('data_compra')
                    if pd.isna(dt_compra) or not dt_compra:
                        dt_compra = str(venda.get('created_at', 'Sem Data'))[:10]
                    else:
                        dt_compra = str(dt_compra)[:10]
                        
                    qtd = int(venda.get('quantidade', 0))
                    vv_unit = float(venda.get('valor_venda_unitario', 0))
                    
                    tipo_pag = venda.get('tipo_pagamento')
                    if pd.isna(tipo_pag) or not tipo_pag: tipo_pag = "Não Informado"
                        
                    status_pag = venda.get('status_pagamento')
                    if pd.isna(status_pag) or not status_pag: status_pag = "Não Informado"
                    
                    valor_total = vv_unit * qtd
                    
                    garantia_icone = "✅"
                    try:
                        dt_obj = datetime.strptime(dt_compra, "%Y-%m-%d")
                        dias_passados = (datetime.today() - dt_obj).days
                        if dias_passados > 180: # 6 meses = ~180 dias
                            garantia_icone = "❌ (Expirada)"
                        else:
                            garantia_icone = f"✅ (Válida - Falta(m) {180 - dias_passados} dia(s))"
                    except:
                        pass
                    
                    with st.expander(f"🛒 **{qtd}x {cod_prod}** | Compra: {dt_compra} | {tipo_pag} | Status: {status_pag}"):
                        st.write(f"**Referência do Produto:** {cod_prod}")
                        st.write(f"**Quantidade Adquirida:** {qtd}")
                        st.write(f"**Valor Total da Operação:** R$ {valor_total:.2f}")
                        st.write(f"**Data da Compra:** {dt_compra}")
                        st.write(f"**Garantia (6 meses):** {garantia_icone}")
                        st.write(f"**Modalidade de Pagamento:** {tipo_pag}")
                        
                        if status_pag == "Pendente":
                            st.warning("O status atual é: **Pendente**")
                            if venda_id:
                                if st.button(f"💰 Marcar como Pago", key=f"pago_{venda_id}"):
                                    if update_venda(venda_id, {"status_pagamento": "Pago"}):
                                        st.success("Status atualizado com sucesso para Pago!")
                                        st.rerun()
                            else:
                                st.error("Esta venda antiga não possui um ID para atualização direta.")
                        elif status_pag == "Pago":
                            st.success("O status atual é: **Pago**")
                        else:
                            st.info(f"O status atual é: **{status_pag}**")
