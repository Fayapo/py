# Guia de Configuração e Deploy - Sistema de Gerenciamento de Estoque de Joias Cloud

Leia este guia com atenção para configurar o seu painel gerencial! Ele é focado em entregar a melhor solução para que você acesse seus dados sincronizados de múltiplas máquinas (celular, tablet ou PCs) do jeito que solicitou.

### O sistema foi desenvolvido com:
* **Python (Streamlit):** Interface intuitiva e web responsiva, gerida facilmente e com ótimo processamento financeiro.
* **Supabase (PostgreSQL):** Banco de Dados gratuito na nuvem, incrivelmente rápido e robusto. Mantém seus estoques salvos e sincronizados globalmente e sem complicação.

Abaixo, o passo a passo para deixar o projeto no ar em 5-10 minutos!

---

## ☁️ 1. Configurando o Banco de Dados na Nuvem (Supabase)

O primeiro passo é gerar um local gratuito para alocar os dados da estrutura financeira das peças.

1. Acesse **[Supabase.com](https://supabase.com)** e faça login com seu GitHub ou Crie uma Conta Gratuita.
2. Na sua tela inicial, clique em **"New Project"**.
3. Dê um nome para a Database (Exemplo: "estoque-joias") e digite uma senha que se lembrar depois. Deixe os outros ajustes no padrão. Clique em **"Create new project"**.
4. Aguarde o projeto ser provisionado (pode demorar em torno de 2-3 minutos).
5. No menu lateral esquerdo da plataforma do Supabase, vá no ícone de **SQL Editor** e clique em **"New snippet"**.
6. **Escrevendo as regras do estoque (Tabelas e Restrições)**: Cole o código Exato de consulta SQL abaixo e clique no botão verde **"Run"** localizado na parte de baixo do canto direito da tela:

```sql
CREATE TABLE produtos (
  codigo TEXT PRIMARY KEY,
  categoria TEXT CHECK (categoria IN ('Brinco', 'Anel', 'Pulseira', 'Choker', 'Tornozeleira')) NOT NULL,
  custo_fabricacao DECIMAL(10, 2) NOT NULL DEFAULT 0,
  custo_banho DECIMAL(10, 2) NOT NULL DEFAULT 0,
  valor_venda DECIMAL(10, 2) NOT NULL DEFAULT 0,
  estoque INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE vendas (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  codigo_produto TEXT REFERENCES produtos(codigo),
  quantidade INTEGER NOT NULL,
  custo_fabricacao_unitario DECIMAL(10, 2) NOT NULL,
  custo_banho_unitario DECIMAL(10, 2) NOT NULL,
  valor_venda_unitario DECIMAL(10, 2) NOT NULL,
  lucro_real_total DECIMAL(10, 2) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

7. **Pronto! As suas estruturas de banco de dados e regras financeiras estão criadas e perfeitamente amarradas.**
8. Agora, volte para o menu esquerdo e clique no ícone da engrenagem ⚙️ (**Project Settings**). Desça e clique em **API**.
9. Na seção `Project API keys`, você precisará copiar e guardar as seguintes informações:
   - **Project URL**
   - **Project API Keys (A que possui o nome 'anon' / 'public')**

---

## 🚀 2. Hospedando sua Aplicação Oficial (Acesso Remoto Web Grátis)

Com o seu banco de dados na web, o ideal não é rodar localmente limitando a outro PC, mas sim fazer o deploy gratuitamente para a provedora do Streamlit:

1. Suba os dois arquivos essenciais numa pasta (Repositório) na sua conta pessoal do [GitHub](https://github.com/):
   - `app.py`
   - `requirements.txt`
2. Crie uma conta no site **[Streamlit Community Cloud](https://share.streamlit.io/)** autenticando com seu GitHub.
3. No painel, clique em **"New app"** (ou Create App). Selecione o repositório do github que criou com os dois arquivos listados. Verifique se o caminho aponta para `app.py`.
4. 🛑 **MUITO IMPORTANTE:** Antes de clicar em "Deploy", certifique-se de clicar em **"Advanced settings"**!
5. Irá abrir uma tela de credenciais chamada **Secrets**. É lá dentro que colaremos o acesso para conversar com seu banco Supabase. Cole, dentro das aspas, a URL e a Chave `anon` Pública copiadas na etapa anterior:

```toml
SUPABASE_URL = "SUA_PROJECT_URL_COPIADA_AQUI"
SUPABASE_KEY = "SUA_CHAVE_ANON_PUBLIC_COPIADA_AQUI"
```

6. Clique em **Save** e por fim, **Deploy**!
7. Em cerca de 1-3 minutos sua aplicação fará a instalação total, lendo o `requirements.txt` e colocará o catálogo e a conexão de rede simultânea online no link gerado.
* **Nota:** Você pode enviar esse Link/URL para ser acessado pelo celular e computadores do trabalho em tempo real, favoritar e utilizar para as vendas a qualquer instante! Os dados não serão perdidos.

---

## 💻 3. Rodando Localmente (Para testes estritos no Computador / Mac)

Caso antes ou opcionalmente a isso, você sinta vontade de rodar o código desta pasta diretamente do seu computador rodando simultâneamente do banco de dados na nuvem, basta:

1. Ir na pasta `.streamlit` que nós criamos, e renomear o arquivo `secrets.example.toml` para `secrets.toml`.
2. Editar esse arquivo de texto e substituir as variáveis `SUPABASE_URL` e `SUPABASE_KEY` pelo que copiou no seu painel.
3. Abrir o terminal integrado, nesta pasta principal do projeto e baixar as bibliotecas:
   ```bash
   pip install -r requirements.txt
   ```
4. Subir o sistema:
   ```bash
   streamlit run app.py
   ```
5. Acessar `http://localhost:8501` e verificar todas as opções gerenciais como Estoque, Finanças, e Categorias na aba.
