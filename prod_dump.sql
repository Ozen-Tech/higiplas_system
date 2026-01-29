--
-- PostgreSQL database dump
--

\restrict 8IPyZOu44PUqGborIehZ8EGWhmHt7GZGOjuslWmk34QyjFzHOI3cgPMdTjQ7ub3

-- Dumped from database version 16.11 (Debian 16.11-1.pgdg12+1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION pg_stat_statements IS 'track planning and execution statistics of all SQL statements executed';


--
-- Name: empresa_vinculada_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.empresa_vinculada_enum AS ENUM (
    'HIGIPLAS',
    'HIGITEC'
);


--
-- Name: motivo_movimentacao_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.motivo_movimentacao_enum AS ENUM (
    'CARREGAMENTO',
    'DEVOLUCAO',
    'AJUSTE_FISICO',
    'PERDA_AVARIA',
    'TRANSFERENCIA_INTERNA'
);


--
-- Name: origem_movimentacao_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.origem_movimentacao_enum AS ENUM (
    'VENDA',
    'DEVOLUCAO',
    'CORRECAO_MANUAL',
    'COMPRA',
    'AJUSTE',
    'OUTRO'
);


--
-- Name: status_movimentacao_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.status_movimentacao_enum AS ENUM (
    'PENDENTE',
    'CONFIRMADO',
    'REJEITADO'
);


--
-- Name: status_pagamento_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.status_pagamento_enum AS ENUM (
    'BOM_PAGADOR',
    'MAU_PAGADOR'
);


--
-- Name: status_pagamento_historico_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.status_pagamento_historico_enum AS ENUM (
    'PAGO',
    'PENDENTE',
    'ATRASADO'
);


--
-- Name: tipo_arquivo_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.tipo_arquivo_enum AS ENUM (
    'PDF',
    'XML'
);


--
-- Name: tipo_mov_arquivo_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.tipo_mov_arquivo_enum AS ENUM (
    'ENTRADA',
    'SAIDA'
);


--
-- Name: tipo_movimentacao_enum; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.tipo_movimentacao_enum AS ENUM (
    'ENTRADA',
    'SAIDA'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: arquivos_processados; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.arquivos_processados (
    id integer NOT NULL,
    nome_arquivo character varying NOT NULL,
    hash_arquivo character varying NOT NULL,
    nota_fiscal character varying,
    tipo_arquivo public.tipo_arquivo_enum NOT NULL,
    tipo_movimentacao public.tipo_mov_arquivo_enum NOT NULL,
    data_processamento timestamp with time zone DEFAULT now() NOT NULL,
    usuario_id integer NOT NULL,
    empresa_id integer NOT NULL,
    total_produtos integer DEFAULT 0 NOT NULL,
    total_movimentacoes integer DEFAULT 0 NOT NULL
);


--
-- Name: arquivos_processados_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.arquivos_processados_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: arquivos_processados_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.arquivos_processados_id_seq OWNED BY public.arquivos_processados.id;


--
-- Name: clientes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clientes (
    id integer NOT NULL,
    razao_social character varying NOT NULL,
    cnpj character varying,
    endereco character varying,
    email character varying,
    telefone character varying,
    empresa_vinculada public.empresa_vinculada_enum NOT NULL,
    status_pagamento public.status_pagamento_enum,
    data_criacao timestamp with time zone DEFAULT now(),
    empresa_id integer,
    observacoes character varying(500),
    referencia_localizacao character varying(200),
    vendedor_id integer,
    criado_em timestamp with time zone,
    atualizado_em timestamp with time zone
);


--
-- Name: clientes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.clientes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: clientes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.clientes_id_seq OWNED BY public.clientes.id;


--
-- Name: empresas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.empresas (
    id integer NOT NULL,
    nome character varying,
    cnpj character varying,
    data_criacao timestamp without time zone
);


--
-- Name: empresas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.empresas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empresas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.empresas_id_seq OWNED BY public.empresas.id;


--
-- Name: fichas_tecnicas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fichas_tecnicas (
    id integer NOT NULL,
    produto_id integer,
    nome_produto character varying NOT NULL,
    dilucao_recomendada character varying,
    dilucao_numerador double precision,
    dilucao_denominador double precision,
    rendimento_litro double precision,
    modo_uso character varying,
    arquivo_pdf_path character varying,
    observacoes character varying,
    data_atualizacao timestamp with time zone DEFAULT now(),
    data_criacao timestamp with time zone DEFAULT now()
);


--
-- Name: fichas_tecnicas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fichas_tecnicas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fichas_tecnicas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fichas_tecnicas_id_seq OWNED BY public.fichas_tecnicas.id;


--
-- Name: fornecedores; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.fornecedores (
    id integer NOT NULL,
    nome character varying NOT NULL,
    cnpj character varying,
    contato_email character varying,
    contato_telefone character varying,
    empresa_id integer
);


--
-- Name: fornecedores_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.fornecedores_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: fornecedores_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.fornecedores_id_seq OWNED BY public.fornecedores.id;


--
-- Name: historico_pagamentos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.historico_pagamentos (
    id integer NOT NULL,
    cliente_id integer NOT NULL,
    data_pagamento date NOT NULL,
    valor double precision NOT NULL,
    status public.status_pagamento_historico_enum NOT NULL,
    observacoes character varying
);


--
-- Name: historico_pagamentos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.historico_pagamentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: historico_pagamentos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.historico_pagamentos_id_seq OWNED BY public.historico_pagamentos.id;


--
-- Name: historico_preco_produto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.historico_preco_produto (
    id integer NOT NULL,
    produto_id integer NOT NULL,
    preco_unitario double precision NOT NULL,
    quantidade double precision NOT NULL,
    valor_total double precision NOT NULL,
    nota_fiscal character varying,
    data_venda timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    empresa_id integer NOT NULL,
    cliente_id integer,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: historico_preco_produto_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.historico_preco_produto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: historico_preco_produto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.historico_preco_produto_id_seq OWNED BY public.historico_preco_produto.id;


--
-- Name: historico_vendas_cliente; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.historico_vendas_cliente (
    id integer NOT NULL,
    vendedor_id integer NOT NULL,
    cliente_id integer NOT NULL,
    produto_id integer NOT NULL,
    orcamento_id integer NOT NULL,
    empresa_id integer NOT NULL,
    quantidade_vendida integer NOT NULL,
    preco_unitario_vendido double precision NOT NULL,
    valor_total double precision NOT NULL,
    data_venda timestamp with time zone DEFAULT now() NOT NULL,
    criado_em timestamp with time zone DEFAULT now()
);


--
-- Name: historico_vendas_cliente_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.historico_vendas_cliente_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: historico_vendas_cliente_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.historico_vendas_cliente_id_seq OWNED BY public.historico_vendas_cliente.id;


--
-- Name: movimentacoes_estoque; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.movimentacoes_estoque (
    id integer NOT NULL,
    tipo_movimentacao public.tipo_movimentacao_enum NOT NULL,
    quantidade integer NOT NULL,
    observacao character varying,
    data_movimentacao timestamp with time zone DEFAULT now(),
    produto_id integer NOT NULL,
    usuario_id integer NOT NULL,
    origem public.origem_movimentacao_enum,
    quantidade_antes integer,
    quantidade_depois integer,
    status public.status_movimentacao_enum DEFAULT 'CONFIRMADO'::public.status_movimentacao_enum NOT NULL,
    aprovado_por_id integer,
    data_aprovacao timestamp with time zone,
    motivo_rejeicao character varying,
    motivo_movimentacao public.motivo_movimentacao_enum,
    observacao_motivo character varying,
    dados_antes_edicao json,
    dados_depois_edicao json,
    reversao_de_id integer,
    revertida boolean DEFAULT false NOT NULL,
    data_reversao timestamp with time zone,
    revertida_por_id integer
);


--
-- Name: movimentacoes_estoque_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.movimentacoes_estoque_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: movimentacoes_estoque_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.movimentacoes_estoque_id_seq OWNED BY public.movimentacoes_estoque.id;


--
-- Name: orcamento_itens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orcamento_itens (
    id integer NOT NULL,
    quantidade integer NOT NULL,
    preco_unitario_congelado double precision NOT NULL,
    orcamento_id integer,
    produto_id integer
);


--
-- Name: orcamento_itens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orcamento_itens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: orcamento_itens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orcamento_itens_id_seq OWNED BY public.orcamento_itens.id;


--
-- Name: orcamentos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orcamentos (
    id integer NOT NULL,
    status character varying,
    data_criacao timestamp with time zone DEFAULT now(),
    data_validade date,
    usuario_id integer,
    condicao_pagamento character varying,
    preco_minimo double precision,
    preco_maximo double precision,
    numero_nf character varying,
    cliente_id integer,
    token_compartilhamento character varying
);


--
-- Name: orcamentos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orcamentos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: orcamentos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orcamentos_id_seq OWNED BY public.orcamentos.id;


--
-- Name: ordens_compra; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ordens_compra (
    id integer NOT NULL,
    fornecedor_id integer,
    usuario_id integer,
    status character varying,
    data_criacao timestamp with time zone DEFAULT now(),
    data_recebimento timestamp with time zone
);


--
-- Name: ordens_compra_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ordens_compra_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ordens_compra_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ordens_compra_id_seq OWNED BY public.ordens_compra.id;


--
-- Name: ordens_compra_itens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ordens_compra_itens (
    id integer NOT NULL,
    ordem_id integer,
    produto_id integer,
    quantidade_solicitada integer NOT NULL,
    custo_unitario_registrado double precision NOT NULL
);


--
-- Name: ordens_compra_itens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ordens_compra_itens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ordens_compra_itens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ordens_compra_itens_id_seq OWNED BY public.ordens_compra_itens.id;


--
-- Name: precos_cliente_produto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.precos_cliente_produto (
    id integer NOT NULL,
    cliente_id integer NOT NULL,
    produto_id integer NOT NULL,
    preco_padrao double precision NOT NULL,
    preco_minimo double precision,
    preco_maximo double precision,
    preco_medio double precision,
    total_vendas integer,
    data_ultima_venda timestamp with time zone,
    data_criacao timestamp with time zone DEFAULT now() NOT NULL,
    data_atualizacao timestamp with time zone DEFAULT now()
);


--
-- Name: precos_cliente_produto_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.precos_cliente_produto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: precos_cliente_produto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.precos_cliente_produto_id_seq OWNED BY public.precos_cliente_produto.id;


--
-- Name: produtos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.produtos (
    id integer NOT NULL,
    nome character varying,
    codigo character varying,
    categoria character varying,
    descricao character varying,
    preco_custo double precision,
    preco_venda double precision,
    unidade_medida character varying,
    estoque_minimo integer,
    data_validade date,
    quantidade_em_estoque integer,
    empresa_id integer,
    fornecedor_id integer,
    data_criacao timestamp with time zone DEFAULT now()
);


--
-- Name: produtos_concorrentes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.produtos_concorrentes (
    id integer NOT NULL,
    nome character varying NOT NULL,
    marca character varying,
    preco_medio double precision,
    rendimento_litro double precision,
    dilucao character varying,
    dilucao_numerador double precision,
    dilucao_denominador double precision,
    categoria character varying,
    observacoes character varying,
    ativo boolean DEFAULT true,
    data_criacao timestamp with time zone DEFAULT now(),
    data_atualizacao timestamp with time zone DEFAULT now()
);


--
-- Name: produtos_concorrentes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.produtos_concorrentes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: produtos_concorrentes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.produtos_concorrentes_id_seq OWNED BY public.produtos_concorrentes.id;


--
-- Name: produtos_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.produtos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: produtos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.produtos_id_seq OWNED BY public.produtos.id;


--
-- Name: propostas_detalhadas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.propostas_detalhadas (
    id integer NOT NULL,
    orcamento_id integer,
    cliente_id integer NOT NULL,
    vendedor_id integer NOT NULL,
    produto_id integer NOT NULL,
    ficha_tecnica_id integer,
    quantidade_produto double precision NOT NULL,
    dilucao_aplicada character varying,
    dilucao_numerador double precision,
    dilucao_denominador double precision,
    rendimento_total_litros double precision,
    preco_produto double precision,
    custo_por_litro_final double precision,
    concorrente_id integer,
    economia_vs_concorrente double precision,
    economia_percentual double precision,
    economia_valor double precision,
    observacoes character varying,
    compartilhavel boolean DEFAULT false,
    token_compartilhamento character varying,
    data_criacao timestamp with time zone DEFAULT now(),
    data_atualizacao timestamp with time zone DEFAULT now()
);


--
-- Name: propostas_detalhadas_concorrentes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.propostas_detalhadas_concorrentes (
    id integer NOT NULL,
    proposta_id integer NOT NULL,
    nome character varying NOT NULL,
    rendimento_litro double precision,
    custo_por_litro double precision,
    observacoes character varying,
    ordem integer,
    data_criacao timestamp with time zone DEFAULT now() NOT NULL,
    data_atualizacao timestamp with time zone DEFAULT now()
);


--
-- Name: propostas_detalhadas_concorrentes_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.propostas_detalhadas_concorrentes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: propostas_detalhadas_concorrentes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.propostas_detalhadas_concorrentes_id_seq OWNED BY public.propostas_detalhadas_concorrentes.id;


--
-- Name: propostas_detalhadas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.propostas_detalhadas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: propostas_detalhadas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.propostas_detalhadas_id_seq OWNED BY public.propostas_detalhadas.id;


--
-- Name: propostas_detalhadas_itens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.propostas_detalhadas_itens (
    id integer NOT NULL,
    proposta_id integer NOT NULL,
    produto_id integer NOT NULL,
    quantidade_produto double precision NOT NULL,
    dilucao_aplicada character varying,
    dilucao_numerador double precision,
    dilucao_denominador double precision,
    rendimento_total_litros double precision,
    preco_produto double precision,
    custo_por_litro_final double precision,
    observacoes character varying,
    ordem integer,
    concorrente_nome_manual character varying,
    concorrente_rendimento_manual double precision,
    concorrente_custo_por_litro_manual double precision,
    data_criacao timestamp with time zone DEFAULT now() NOT NULL,
    data_atualizacao timestamp with time zone DEFAULT now(),
    concorrente_quantidade double precision,
    concorrente_dilucao_numerador double precision,
    concorrente_dilucao_denominador double precision
);


--
-- Name: propostas_detalhadas_itens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.propostas_detalhadas_itens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: propostas_detalhadas_itens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.propostas_detalhadas_itens_id_seq OWNED BY public.propostas_detalhadas_itens.id;


--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.refresh_tokens (
    id integer NOT NULL,
    token character varying NOT NULL,
    usuario_id integer NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    revoked boolean DEFAULT false NOT NULL
);


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.refresh_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    nome character varying,
    email character varying,
    hashed_password character varying,
    empresa_id integer,
    perfil character varying NOT NULL,
    is_active boolean,
    data_criacao timestamp with time zone DEFAULT now(),
    xp integer DEFAULT 0 NOT NULL,
    level integer DEFAULT 1 NOT NULL,
    foto_perfil character varying
);


--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: vendas_historicas; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vendas_historicas (
    id integer NOT NULL,
    ident_antigo integer,
    descricao character varying,
    quantidade_vendida_total double precision,
    custo_compra_total double precision,
    valor_vendido_total double precision,
    lucro_bruto_total double precision,
    margem_lucro_percentual double precision,
    produto_atual_id integer
);


--
-- Name: vendas_historicas_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vendas_historicas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vendas_historicas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vendas_historicas_id_seq OWNED BY public.vendas_historicas.id;


--
-- Name: visitas_vendedor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.visitas_vendedor (
    id integer NOT NULL,
    vendedor_id integer NOT NULL,
    cliente_id integer,
    data_visita timestamp with time zone DEFAULT now() NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    endereco_completo character varying,
    motivo_visita character varying,
    observacoes character varying,
    foto_comprovante character varying,
    confirmada boolean DEFAULT false NOT NULL,
    empresa_id integer NOT NULL,
    criado_em timestamp with time zone DEFAULT now(),
    atualizado_em timestamp with time zone DEFAULT now()
);


--
-- Name: visitas_vendedor_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.visitas_vendedor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: visitas_vendedor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.visitas_vendedor_id_seq OWNED BY public.visitas_vendedor.id;


--
-- Name: arquivos_processados id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.arquivos_processados ALTER COLUMN id SET DEFAULT nextval('public.arquivos_processados_id_seq'::regclass);


--
-- Name: clientes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clientes ALTER COLUMN id SET DEFAULT nextval('public.clientes_id_seq'::regclass);


--
-- Name: empresas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresas ALTER COLUMN id SET DEFAULT nextval('public.empresas_id_seq'::regclass);


--
-- Name: fichas_tecnicas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fichas_tecnicas ALTER COLUMN id SET DEFAULT nextval('public.fichas_tecnicas_id_seq'::regclass);


--
-- Name: fornecedores id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fornecedores ALTER COLUMN id SET DEFAULT nextval('public.fornecedores_id_seq'::regclass);


--
-- Name: historico_pagamentos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_pagamentos ALTER COLUMN id SET DEFAULT nextval('public.historico_pagamentos_id_seq'::regclass);


--
-- Name: historico_preco_produto id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_preco_produto ALTER COLUMN id SET DEFAULT nextval('public.historico_preco_produto_id_seq'::regclass);


--
-- Name: historico_vendas_cliente id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_vendas_cliente ALTER COLUMN id SET DEFAULT nextval('public.historico_vendas_cliente_id_seq'::regclass);


--
-- Name: movimentacoes_estoque id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimentacoes_estoque ALTER COLUMN id SET DEFAULT nextval('public.movimentacoes_estoque_id_seq'::regclass);


--
-- Name: orcamento_itens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orcamento_itens ALTER COLUMN id SET DEFAULT nextval('public.orcamento_itens_id_seq'::regclass);


--
-- Name: orcamentos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orcamentos ALTER COLUMN id SET DEFAULT nextval('public.orcamentos_id_seq'::regclass);


--
-- Name: ordens_compra id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordens_compra ALTER COLUMN id SET DEFAULT nextval('public.ordens_compra_id_seq'::regclass);


--
-- Name: ordens_compra_itens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordens_compra_itens ALTER COLUMN id SET DEFAULT nextval('public.ordens_compra_itens_id_seq'::regclass);


--
-- Name: precos_cliente_produto id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.precos_cliente_produto ALTER COLUMN id SET DEFAULT nextval('public.precos_cliente_produto_id_seq'::regclass);


--
-- Name: produtos id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.produtos ALTER COLUMN id SET DEFAULT nextval('public.produtos_id_seq'::regclass);


--
-- Name: produtos_concorrentes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.produtos_concorrentes ALTER COLUMN id SET DEFAULT nextval('public.produtos_concorrentes_id_seq'::regclass);


--
-- Name: propostas_detalhadas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas ALTER COLUMN id SET DEFAULT nextval('public.propostas_detalhadas_id_seq'::regclass);


--
-- Name: propostas_detalhadas_concorrentes id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas_concorrentes ALTER COLUMN id SET DEFAULT nextval('public.propostas_detalhadas_concorrentes_id_seq'::regclass);


--
-- Name: propostas_detalhadas_itens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas_itens ALTER COLUMN id SET DEFAULT nextval('public.propostas_detalhadas_itens_id_seq'::regclass);


--
-- Name: refresh_tokens id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Name: vendas_historicas id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendas_historicas ALTER COLUMN id SET DEFAULT nextval('public.vendas_historicas_id_seq'::regclass);


--
-- Name: visitas_vendedor id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visitas_vendedor ALTER COLUMN id SET DEFAULT nextval('public.visitas_vendedor_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
add_data_criacao_foto_perfil_001
\.


--
-- Data for Name: arquivos_processados; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.arquivos_processados (id, nome_arquivo, hash_arquivo, nota_fiscal, tipo_arquivo, tipo_movimentacao, data_processamento, usuario_id, empresa_id, total_produtos, total_movimentacoes) FROM stdin;
\.


--
-- Data for Name: clientes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.clientes (id, razao_social, cnpj, endereco, email, telefone, empresa_vinculada, status_pagamento, data_criacao, empresa_id, observacoes, referencia_localizacao, vendedor_id, criado_em, atualizado_em) FROM stdin;
24	COLEGIO EDUCALLIS FIGUEIREDO	53512697000146	RUA ANTONIO RAPOSO/AVN.JOAO PESSOA, C, 437, SANTA CRUZ, CEP 65045-215, 0921 - MA, São Luís	LEVI.FIGUEIREDO@EDUCALLIS.COM.VC	98938787878	HIGIPLAS	BOM_PAGADOR	2025-11-07 03:10:33.103431+00	1	\N	\N	7	2025-11-07 03:10:33.10301+00	\N
25	TOYOLEX AUTOS S/A	07234453001799	AVENIDA ENGENHEIRO EMILIANO MACIEIRA, 1 : BR 135; : KM 01; BLOCO: B2;, TIRIRICAL, São Luís	CARTEIRAFISCALPARVI@PARVI.COM.BR	98932172850	HIGIPLAS	BOM_PAGADOR	2025-11-07 03:13:46.994267+00	1	\N	\N	7	2025-11-07 03:13:46.993674+00	\N
26	COLEGIO MARISTA DO ARACAGY	10847382002190	ESTRADA ESTRADA DO ARACAGY, 48, ARACAGY, São Luís	vlisboa@marista.edu.br	98921022191	HIGIPLAS	BOM_PAGADOR	2025-11-07 03:15:33.584395+00	1	\N	\N	7	2025-11-07 03:15:33.583768+00	\N
27	BREMEN VEICULOS S.A	16355380001431	AVENIDA ENGENHEIRO EMILIANO MACIEIRA, 01 : RODOVIA BR 135; BLOCO: D; SALA: 01;, TIRIRICAL, São Luís	CARTEIRAFISCALPARVI@PARVI.COM.BR	98932693300	HIGIPLAS	BOM_PAGADOR	2025-11-07 03:17:02.372774+00	1	\N	\N	7	2025-11-07 03:17:02.372288+00	\N
28	LENCOIS MARANHENSES LAVANDERIA INDUSTRIAL E HOSPITALAR LTDA	10861126000104	RUA NETUNO, 15, RECANTO DOS VINHAIS, São Luís	COMERCIAL@LENCOISLAVANDERIA.COM.BR	98931996270	HIGIPLAS	BOM_PAGADOR	2025-11-07 03:18:42.652853+00	1	\N	\N	7	2025-11-07 03:18:42.652025+00	\N
29	HIGIMAR EMPREENDIMENTOS	45891329000128	AVENIDA SAO LUIS REI DE FRANCA, SALA 10, 412 SALA 10, JARDIM ATLANTICO, São Luís	CONTABIL.WEB@HOMAIL.COM	98984335166	HIGIPLAS	BOM_PAGADOR	2025-11-07 03:20:05.607133+00	1	\N	\N	7	2025-11-07 03:20:05.613732+00	\N
30	COND. DUNAS DO LITORAL	32271164000140	Vinhais, São luís	parquedunasdolitoral@gmail.com	98987072417	HIGIPLAS	BOM_PAGADOR	2025-11-12 12:40:02.007664+00	1	\N	\N	7	2025-11-12 12:40:02.01532+00	\N
31	Cond.parque Dunas litoral 	65074863	R dez 200 planalto Vinhais, São Luís ma	\N	98988167268	HIGIPLAS	BOM_PAGADOR	2025-11-12 19:12:26.113244+00	1	\N	\N	9	2025-11-12 19:12:26.11892+00	\N
22	teste ckiente	31802290000110	bairro h, cidade y	teste123123@gmail.com	98999998999	HIGIPLAS	MAU_PAGADOR	2025-11-07 00:33:34.885043+00	1	\N	\N	7	2025-11-07 00:33:34.888639+00	2025-11-14 00:39:59.773871+00
20	Cedro	\N	bairro x, cidade y	\N	98981616690	HIGIPLAS	MAU_PAGADOR	2025-10-07 12:20:36.824332+00	1	\N	\N	1	2025-10-07 12:20:36.826839+00	2025-11-14 12:26:55.360197+00
17	Cliente Completo 193614	12345678919	\N	\N	98888771936	HIGIPLAS	MAU_PAGADOR	2025-10-05 22:36:14.788367+00	1	\N	\N	\N	\N	2025-11-14 00:40:20.42994+00
18	Cliente Completo 200216	12345678920	\N	\N	98888772002	HIGIPLAS	MAU_PAGADOR	2025-10-05 23:02:17.482135+00	1	\N	\N	\N	\N	2025-11-14 00:40:27.866173+00
15	Cliente teste	12345678911	Rua y, 123, apto, bairro x, cidade z, MA, 65000000	email@deexemplo.com	98999999999	HIGIPLAS	MAU_PAGADOR	2025-10-04 19:38:38.047795+00	1	\N	\N	\N	\N	2025-11-14 00:41:04.276779+00
12	Cliente Teste Final 1755058592	01755058592000192	\N	teste.final1755058592@exemplo.com	(11) 99999-9999	HIGIPLAS	MAU_PAGADOR	2025-08-13 04:16:33.430842+00	1	\N	\N	\N	\N	2025-11-14 00:41:09.822546+00
13	Cliente Teste Final 1755058871	01755058871000171	\N	teste.final1755058871@exemplo.com	(11) 99999-9999	HIGIPLAS	MAU_PAGADOR	2025-08-13 04:21:13.034464+00	1	\N	\N	\N	\N	2025-11-14 00:41:16.696832+00
32	teste771	09897687677	teste 4, teste 5	teste@teste.com	98998765432	HIGIPLAS	MAU_PAGADOR	2025-11-13 16:14:49.05675+00	1	\N	\N	11	2025-11-13 16:14:49.065131+00	2025-11-14 00:41:27.974459+00
19	teste	60871991365	\N	\N	98999068855	HIGIPLAS	MAU_PAGADOR	2025-10-06 01:02:52.276584+00	1	\N	\N	\N	\N	2025-11-14 00:41:32.139798+00
16	teste	12345678910	rua zeta, 123, apto, cidade y, MA, 65070011	teste@gmail.com	98999068855	HIGIPLAS	MAU_PAGADOR	2025-10-04 19:49:23.199817+00	1	\N	\N	\N	\N	2025-11-14 00:41:38.823956+00
51	AD7 ALIMENTAÇÃO INTELIGENTE LTDA	37454541000108	Rua carcarás 7 quadra 7 bairro olho d'água, São Luís ma	\N	98988628421	HIGIPLAS	BOM_PAGADOR	2025-12-03 19:05:12.684126+00	1	\N	\N	11	2025-12-03 19:05:12.687884+00	\N
38	shopping passeio	236322880000112	COHATRAC IV, são luis MA	passeio.adm@gmail.com	98985118345	HIGIPLAS	BOM_PAGADOR	2025-11-27 12:37:24.582561+00	1	\N	\N	9	2025-11-27 12:37:24.586266+00	\N
39	HOSPITAL SAUDE DOS OLHOS	318163890000171	SÃO BERNADO, são luis MA	financeiro@saudedosolhos.med.br	98984427458	HIGIPLAS	BOM_PAGADOR	2025-11-27 14:24:29.288709+00	1	\N	\N	9	2025-11-27 14:24:29.291227+00	\N
40	ABREU E ALBURQUERQUE LTDA	357490030000107	PARQUE UNIVERSITARIO, são luis MA	financeiro.bemvista@gmail.com	98981442542	HIGIPLAS	BOM_PAGADOR	2025-11-27 18:09:04.368712+00	1	\N	\N	9	2025-11-27 18:09:04.370809+00	\N
41	OFTALMOCLINICA DO MARANHÃO	028245080000130	MAIOBÃO, PAÇO DE LUMIAR	tatianesuzany@gmail.com	98985195711	HIGIPLAS	BOM_PAGADOR	2025-12-01 18:39:48.022095+00	1	\N	\N	9	2025-12-01 18:39:48.027501+00	\N
42	Linhares e Castro ltda	08830153000178	Lagoa da Jansen, São Luís Ma	ana.amorim@linharesfacilities.com.br	9821092502	HIGIPLAS	BOM_PAGADOR	2025-12-01 19:08:05.23952+00	1	\N	\N	11	2025-12-01 19:08:05.317904+00	\N
43	L M BERTI SERVIRÇOS EIRELI	30726808000111	VINHAIS, SÃO LUIS MA	lucfema36@gmail.com	9832353046	HIGIPLAS	BOM_PAGADOR	2025-12-02 14:20:17.767514+00	1	\N	\N	9	2025-12-02 14:20:17.773317+00	\N
44	ILHA SUPERMERCADOS LTDA	220591486000134	PARQUE VITÓRIA, SÃO JOSÉ DE RIBAMAR MA	\N	9832457338	HIGIPLAS	BOM_PAGADOR	2025-12-02 14:29:46.265659+00	1	\N	\N	9	2025-12-02 14:29:46.269857+00	\N
45	UDI HOSPITAL ESPERANCA SA	02284062001170	JARACATY, SÃO LUIS -MA	paula.Imassula@udihospital.com.br	9832167979	HIGIPLAS	BOM_PAGADOR	2025-12-02 14:41:50.354739+00	1	\N	\N	9	2025-12-02 14:41:50.360566+00	\N
46	SENAC- SERVIÇO NACIONAL DE APRENDIZAGEM COMERCIAL	03760035000206	CENTRO, SÃO LUIS-MA	re,gerencis@ma.senac.br	9831981100	HIGIPLAS	BOM_PAGADOR	2025-12-02 14:51:42.16074+00	1	\N	\N	9	2025-12-02 14:51:42.165179+00	\N
47	Saam towage Brasil s.a	05436047001945	Porto do itaqui, São Luís ma	drielly.avelar@saamtowage.com	9833115000	HIGIPLAS	BOM_PAGADOR	2025-12-02 17:38:36.491815+00	1	\N	\N	11	2025-12-02 17:38:36.495178+00	\N
48	BITAL AMBIENTAL LTDA	13319493000179	MARACANA, SÃO LUIS-MA	\N	9893227385	HIGIPLAS	BOM_PAGADOR	2025-12-02 18:30:19.922555+00	1	\N	\N	9	2025-12-02 18:30:19.925329+00	\N
49	Equatorial telecomunicações s.a	10995526000102	Alameda A 3 loteamento quitandinha/ alto do calhal, São Luís MA	ramon.nunes@equatorialtelecon.com.br	98988804400	HIGIPLAS	BOM_PAGADOR	2025-12-03 13:20:52.23014+00	1	\N	\N	11	2025-12-03 13:20:52.238156+00	\N
50	Equatorial serviços s.a 	09347229000171	Rua alto do calhau 100 alameda A quadra SQS ANEXO A CALHAL, São Luís MA	andressa.soares@equatorialtelecom.com.br	98988806472	HIGIPLAS	BOM_PAGADOR	2025-12-03 17:47:51.770036+00	1	\N	\N	11	2025-12-03 17:47:51.77181+00	\N
53	VAN OORD SERVIÇOS DE OPERAÇÕES MARITIMAS LTDA	30276927000896	Rua dos azulejos 1 sala 1111 bairro renascença, São Luís MA	\N	9832352447	HIGIPLAS	BOM_PAGADOR	2025-12-04 19:44:19.411411+00	1	\N	\N	11	2025-12-04 19:44:19.415285+00	\N
54	CLINICA DE SERVIÇOS MEDICOS GERAIS LTDA	01192155000210	COHAB ANIL, SÃO LUIS /MA	compras@oftalmo-ma.com.br	98985383365	HIGIPLAS	BOM_PAGADOR	2025-12-10 12:09:07.929373+00	1	\N	\N	9	2025-12-10 12:09:07.930488+00	\N
55	CRISTAIS SOLUCOES AMBIENTAIS E GESTAO DE RESIDUOS LTDA	24024586000192	Rua doze,04 QD-F LOTE 04 DISTRITO INDUSTRIAL, São Luís MA	adm@cristais.eco.br	98989023022	HIGIPLAS	BOM_PAGADOR	2025-12-18 13:01:14.129469+00	1	\N	\N	11	2025-12-18 13:01:14.129066+00	\N
56	VALPARAISO COMPLEXO TURISTICO LTDA	07553463000120	PINDOA, PAÇO DO LUMIAR MA	ALMOXERIFADO@VALPARAISOADVENTUREPARK	98991178585	HIGIPLAS	BOM_PAGADOR	2025-12-18 17:21:57.174961+00	1	\N	\N	9	2025-12-18 17:21:57.176846+00	\N
57	ELO CONTACT CENTER SERVICOS LTDA	15729974000340	Av Lourenço vieira da Silva 96 QD 53 Al 1-2 QD 53 L 1-2-5-6 jardim São Cristóvão 2, São Luís MA	compras@grupoelo.com	9832211618	HIGIPLAS	BOM_PAGADOR	2025-12-19 11:21:29.014832+00	1	\N	\N	11	2025-12-19 11:21:29.017348+00	\N
58	Supermix Concreto S/A	34230979010845	Vila mocajituba, Paço de Lumiar-MA	saoluis@supermix.com.br	9832481661	HIGIPLAS	BOM_PAGADOR	2026-01-06 13:33:47.309001+00	1	\N	\N	9	2026-01-06 13:33:47.312386+00	\N
21	Frete por Conta C	01611866001254	Areinha, São Luís	compras@pjrefeicoes.com.br	84999380099	HIGIPLAS	BOM_PAGADOR	2025-10-14 12:58:11.76783+00	1	\N	\N	1	2025-10-14 12:58:11.773554+00	2026-01-16 01:14:23.91507+00
52	Frete por Conta C	15375357000121	Av colares Moreira 1 loteamento CALHAL bairro calhal, São Luís MA	compras.saoluis@cocobambu.com	98991013670	HIGIPLAS	BOM_PAGADOR	2025-12-03 19:18:10.407734+00	1	\N	\N	11	2025-12-03 19:18:10.410192+00	2026-01-26 13:58:19.893142+00
59	AVR SERVICOS LTDA	26552611000136	Rua dos gaviões ponta do farol, São Luís ma	REINALDO.LINHARES@LINHARESFACILITIES.COM.BR	98987401578	HIGIPLAS	BOM_PAGADOR	2026-01-07 14:33:28.414406+00	1	\N	\N	11	2026-01-07 14:33:28.461579+00	\N
60	Renato Martins pereira 	03802154380	Fátima, São Luís MA	\N	98988222228	HIGIPLAS	BOM_PAGADOR	2026-01-13 10:58:53.416121+00	1	\N	\N	11	2026-01-13 10:58:53.422386+00	\N
61	Frete por Conta C	31816389000171	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-16 01:16:17.801303+00	1	\N	\N	\N	\N	\N
62	Frete por Conta C	35280225000123	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-16 13:21:20.111993+00	1	\N	\N	\N	\N	\N
63	BRAGANCA GASTRONOMIA LTDA	45904601000167	RUA 11 Q 5 N 20 LOTE 20 -B-CONJUNTO VINHAIS, SÃ0 LUIS MA	financeiro@igasaoluis.com.br	989999999999	HIGIPLAS	BOM_PAGADOR	2026-01-16 16:14:36.576767+00	1	\N	\N	9	2026-01-16 16:14:36.580869+00	\N
65	Frete por Conta C	39988896000102	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-19 18:36:00.501232+00	1	\N	\N	\N	\N	\N
66	FRETE POR CONTA C	22599389000176	BAIRRO / DISTRITO	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-22 10:13:15.254311+00	1	\N	\N	\N	\N	\N
23	Frete por Conta C	35357138000127	AVENIDA BAHIA, 667, CHACARA BRASIL, CEP 65066-659, 0921 - MA, São Luís	RNCONTABILIDADE1@HOTMAIL.COM	98985359215	HIGIPLAS	BOM_PAGADOR	2025-11-07 03:07:02.692909+00	1	\N	\N	7	2025-11-07 03:07:02.693338+00	2026-01-22 10:26:47.866208+00
67	Frete por Conta C	07172372003593	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-26 13:55:18.200271+00	1	\N	\N	\N	\N	\N
64	Frete por Conta C	10187537000166	AV.14,QDRA 02,LOTE 18 E 19 MAIOBÃO, PAÇO LUMIAR - MA	\N	9832743204	HIGIPLAS	BOM_PAGADOR	2026-01-17 12:32:17.295767+00	1	\N	\N	9	2026-01-17 12:32:17.298121+00	2026-01-26 13:57:04.954693+00
68	Frete por Conta C	05517765000117	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-26 13:57:57.500097+00	1	\N	\N	\N	\N	\N
69	Frete por Conta C	00159120000136	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-26 13:58:37.551802+00	1	\N	\N	\N	\N	\N
70	Frete por Conta C	69420156000128	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-27 19:00:06.961996+00	1	\N	\N	\N	\N	\N
71	CONDOMINIO GRAN VILLAGE ARAÇAGY IV	55864479000104	ARAÇAGY, SÃO JOSÉ DE RIBAMAR MA	\N	98987888401	HIGIPLAS	BOM_PAGADOR	2026-01-29 18:25:36.816592+00	1	\N	\N	9	2026-01-29 18:25:36.81887+00	\N
72	Frete por Conta C	25136323000219	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-29 19:01:22.494099+00	1	\N	\N	\N	\N	\N
73	Frete por Conta C	27096507000490	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-29 19:01:44.95612+00	1	\N	\N	\N	\N	\N
74	Frete por Conta C	38090597000266	Bairro/Distrito	\N	\N	HIGIPLAS	BOM_PAGADOR	2026-01-29 19:02:19.534974+00	1	\N	\N	\N	\N	\N
\.


--
-- Data for Name: empresas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.empresas (id, nome, cnpj, data_criacao) FROM stdin;
1	HIGIPLAS	\N	2025-07-07 03:49:22.734175
2	Empresa Padrão Higiplas	\N	2025-08-13 01:07:27.624693
\.


--
-- Data for Name: fichas_tecnicas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fichas_tecnicas (id, produto_id, nome_produto, dilucao_recomendada, dilucao_numerador, dilucao_denominador, rendimento_litro, modo_uso, arquivo_pdf_path, observacoes, data_atualizacao, data_criacao) FROM stdin;
\.


--
-- Data for Name: fornecedores; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.fornecedores (id, nome, cnpj, contato_email, contato_telefone, empresa_id) FROM stdin;
\.


--
-- Data for Name: historico_pagamentos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.historico_pagamentos (id, cliente_id, data_pagamento, valor, status, observacoes) FROM stdin;
\.


--
-- Data for Name: historico_preco_produto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.historico_preco_produto (id, produto_id, preco_unitario, quantidade, valor_total, nota_fiscal, data_venda, empresa_id, cliente_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: historico_vendas_cliente; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.historico_vendas_cliente (id, vendedor_id, cliente_id, produto_id, orcamento_id, empresa_id, quantidade_vendida, preco_unitario_vendido, valor_total, data_venda, criado_em) FROM stdin;
1	3	56	1103	64	1	5	263.2	1316	2025-12-18 17:41:26.341998+00	2025-12-22 13:17:47.379102+00
2	3	50	1087	69	1	120	5.33	639.6	2025-12-22 12:12:23.476346+00	2025-12-29 14:20:10.878542+00
3	3	50	1104	69	1	280	22.39	6269.2	2025-12-22 12:12:23.476346+00	2025-12-29 14:20:10.878542+00
4	1	44	1022	71	1	1	332.9	332.9	2025-12-23 19:24:56.586494+00	2025-12-29 14:41:40.076204+00
5	1	44	1022	71	1	1	332.9	332.9	2025-12-23 19:24:56.586494+00	2025-12-29 14:42:06.58343+00
6	1	53	1106	72	1	1	523.5	523.5	2025-12-29 14:59:22.336292+00	2025-12-29 15:05:32.288028+00
7	1	53	1107	72	1	1	523.5	523.5	2025-12-29 14:59:22.336292+00	2025-12-29 15:05:32.288028+00
21	1	40	817	73	1	25	6.32	158	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
22	1	40	920	73	1	2	165.94	331.88	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
23	1	40	931	73	1	1	77.3	77.3	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
24	1	40	925	73	1	6	7.69	46.14	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
25	1	40	951	73	1	3	139.4	418.20000000000005	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
26	1	40	839	73	1	2	0.97	1.94	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
27	1	40	850	73	1	3	2.91	8.73	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
28	1	40	802	73	1	1	14.92	14.92	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
29	1	40	984	73	1	1	24.92	24.92	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
30	1	40	960	73	1	1	20	20	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
31	1	40	1045	73	1	1	15.51	15.51	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
32	1	40	836	73	1	1	10.5	10.5	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
33	1	40	825	73	1	6	2.91	17.46	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00
34	1	53	1106	72	1	1	523.5	523.5	2025-12-29 14:59:22.336292+00	2026-01-06 13:44:30.682181+00
35	1	53	1107	72	1	1	523.5	523.5	2025-12-29 14:59:22.336292+00	2026-01-06 13:44:30.682181+00
36	1	44	1022	71	1	1	332.9	332.9	2025-12-23 19:24:56.586494+00	2026-01-06 13:44:36.224049+00
37	1	44	824	70	1	2	136.22	272.44	2025-12-23 11:36:32.814172+00	2026-01-06 13:44:39.303214+00
38	1	44	874	70	1	2	100.79	201.58	2025-12-23 11:36:32.814172+00	2026-01-06 13:44:39.303214+00
39	1	44	966	70	1	2	154.8	309.6	2025-12-23 11:36:32.814172+00	2026-01-06 13:44:39.303214+00
40	1	50	1087	69	1	120	5.33	639.6	2025-12-22 12:12:23.476346+00	2026-01-06 13:44:42.166297+00
41	1	50	1104	69	1	280	22.39	6269.2	2025-12-22 12:12:23.476346+00	2026-01-06 13:44:42.166297+00
42	1	49	1087	68	1	30	5.33	159.9	2025-12-22 12:08:21.573751+00	2026-01-06 13:44:44.581962+00
43	1	49	1104	68	1	40	22.39	895.6	2025-12-22 12:08:21.573751+00	2026-01-06 13:44:44.581962+00
44	1	57	1025	67	1	42	27.1	1138.2	2025-12-19 12:44:37.529456+00	2026-01-06 13:44:47.056029+00
45	1	57	856	67	1	1	128.11	128.11	2025-12-19 12:44:37.529456+00	2026-01-06 13:44:47.056029+00
46	1	57	789	66	1	12	41.58	498.96	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
47	1	57	850	66	1	36	2.91	104.76	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
48	1	57	926	66	1	20	4.34	86.8	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
49	1	57	848	66	1	10	3.12	31.200000000000003	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
50	1	57	868	66	1	5	3.15	15.75	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
51	1	57	839	66	1	10	0.97	9.7	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
52	1	57	977	66	1	35	4.5	157.5	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
53	1	57	787	66	1	5	5.37	26.85	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
54	1	57	1002	66	1	10	20.25	202.5	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
55	1	57	990	66	1	15	38.7	580.5	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
56	1	57	1016	66	1	3	125.48	376.44	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
57	1	57	920	66	1	2	136.39	272.78	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
58	1	57	1035	66	1	7	73.66	515.62	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
59	1	57	1036	66	1	7	73.66	515.62	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
60	1	57	827	66	1	1	35	35	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
61	1	57	976	66	1	10	16.8	168	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00
62	1	21	853	65	1	1	46.26	46.26	2025-12-18 20:37:15.108323+00	2026-01-06 13:45:04.000767+00
63	1	21	855	65	1	1	27.39	27.39	2025-12-18 20:37:15.108323+00	2026-01-06 13:45:04.000767+00
64	1	21	856	65	1	1	158.13	158.13	2025-12-18 20:37:15.108323+00	2026-01-06 13:45:04.000767+00
65	1	56	1103	64	1	5	263.2	1316	2025-12-18 17:41:26.341998+00	2026-01-06 13:45:06.652411+00
66	1	55	985	63	1	20	52.95	1059	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00
67	1	55	977	63	1	10	4.5	45	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00
68	1	55	839	63	1	10	0.97	9.7	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00
69	1	55	966	63	1	2	154.8	309.6	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00
70	1	55	825	63	1	10	2.91	29.1	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00
71	1	21	1001	62	1	1	14.55	14.55	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00
72	1	21	993	62	1	7	51.9	363.3	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00
73	1	21	894	62	1	1	27	27	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00
74	1	21	893	62	1	12	24.4	292.79999999999995	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00
75	1	21	1041	62	1	2	15.34	30.68	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00
76	1	21	788	61	1	88	3.29	289.52	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
77	1	21	787	61	1	12	5.37	64.44	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
78	1	21	791	61	1	80	11.7	936	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
79	1	21	1010	61	1	1	95.05	95.05	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
80	1	21	874	61	1	5	90.31	451.55	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
81	1	21	824	61	1	3	131.29	393.87	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
82	1	21	876	61	1	4	120.81	483.24	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
83	1	21	966	61	1	3	156.07	468.21	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
84	1	21	822	61	1	3	112.79	338.37	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
85	1	21	1035	61	1	2	89.6	179.2	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
86	1	21	1024	61	1	4	176.82	707.28	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
87	1	21	884	61	1	12	5.87	70.44	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
88	1	21	847	61	1	30	1.5	45	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
89	1	21	848	61	1	80	3.12	249.60000000000002	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
90	1	21	883	61	1	12	5.87	70.44	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
91	1	21	928	61	1	2	111.51	223.02	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
92	1	21	804	61	1	30	2.93	87.9	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
93	1	21	935	61	1	8	57.68	461.44	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00
94	1	21	788	60	1	60	3.29	197.4	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
95	1	21	787	60	1	12	5.37	64.44	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
96	1	21	791	60	1	24	11.7	280.79999999999995	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
97	1	21	874	60	1	3	90.31	270.93	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
98	1	21	966	60	1	2	156.07	312.14	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
99	1	21	1036	60	1	2	89.6	179.2	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
100	1	21	1024	60	1	1	176.82	176.82	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
101	1	21	879	60	1	12	3.43	41.160000000000004	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
102	1	21	928	60	1	2	111.51	223.02	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
103	1	21	804	60	1	30	2.93	87.9	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
104	1	21	935	60	1	8	57.68	461.44	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00
105	1	43	1021	59	1	2	138.5	277	2025-12-15 11:44:13.958357+00	2026-01-06 13:45:30.500276+00
106	1	42	1048	58	1	1	72.65	72.65	2025-12-15 11:42:07.060514+00	2026-01-06 13:45:33.586767+00
107	1	23	788	29	1	5	3.29	16.45	2025-11-25 12:14:35.002568+00	2026-01-06 13:45:40.57561+00
108	1	23	789	29	1	2	47.09	94.18	2025-11-25 12:14:35.002568+00	2026-01-06 13:45:40.57561+00
109	1	23	791	29	1	2	11.7	23.4	2025-11-25 12:14:35.002568+00	2026-01-06 13:45:40.57561+00
110	1	23	792	29	1	2	148.53	297.06	2025-11-25 12:14:35.002568+00	2026-01-06 13:45:40.57561+00
111	1	27	980	30	1	2	101.4	202.8	2025-11-25 12:40:58.790031+00	2026-01-06 13:45:44.960422+00
112	1	27	862	30	1	3	213.53	640.59	2025-11-25 12:40:58.790031+00	2026-01-06 13:45:44.960422+00
113	1	30	861	31	1	12	0	0	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00
114	1	30	792	31	1	1	148.53	148.53	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00
115	1	30	1074	31	1	1	20	20	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00
116	1	30	829	31	1	1	32.2	32.2	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00
117	1	30	835	31	1	1	41.3	41.3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00
118	1	30	889	31	1	1	30	30	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00
119	1	30	875	31	1	1	0	0	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00
120	1	30	952	31	1	1	385.5	385.5	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00
121	1	30	1016	31	1	1	123.45	123.45	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00
122	1	23	809	32	1	4	24.56	98.24	2025-11-26 00:18:46.660313+00	2026-01-06 13:46:03.044612+00
123	1	23	968	32	1	4	36.48	145.92	2025-11-26 00:18:46.660313+00	2026-01-06 13:46:03.044612+00
124	1	38	1015	33	1	2	132.5	265	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
125	1	38	845	33	1	10	3.36	33.6	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
126	1	38	788	33	1	36	3.29	118.44	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
127	1	38	921	33	1	3	45.77	137.31	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
128	1	38	839	33	1	19	0.97	18.43	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
129	1	38	931	33	1	30	77.3	2319	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
130	1	38	990	33	1	5	38.7	193.5	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
131	1	38	946	33	1	2	132.54	265.08	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
132	1	38	925	33	1	10	7.69	76.9	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
133	1	38	1048	33	1	2	83.84	167.68	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
134	1	38	1002	33	1	5	20.25	101.25	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
135	1	38	1016	33	1	2	132.5	265	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
136	1	38	827	33	1	6	38.2	229.20000000000002	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
137	1	38	937	33	1	8	102.9	823.2	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00
138	1	39	931	34	1	5	77.3	386.5	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
139	1	39	940	34	1	48	19.3	926.4000000000001	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
140	1	39	984	34	1	2	24.92	49.84	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
141	1	39	983	34	1	4	17.92	71.68	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
142	1	39	991	34	1	4	70.5	282	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
143	1	39	951	34	1	1	139.04	139.04	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
144	1	39	789	34	1	2	47.09	94.18	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
145	1	39	824	34	1	1	121.9	121.9	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
146	1	39	825	34	1	10	2.91	29.1	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
147	1	39	839	34	1	12	0.97	11.64	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
148	1	39	817	34	1	75	6.32	474	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
149	1	39	819	34	1	50	3.99	199.5	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
150	1	39	1062	34	1	1	58.8	58.8	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
151	1	39	853	34	1	2	34.59	69.18	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
152	1	39	976	34	1	5	16.8	84	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
153	1	39	850	34	1	4	2.91	11.64	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
154	1	39	890	34	1	1	11.05	11.05	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
155	1	39	881	34	1	4	24.33	97.32	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00
156	1	40	925	35	1	6	7.69	46.14	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
157	1	40	1062	35	1	2	58.8	117.6	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
158	1	40	802	35	1	2	14.92	29.84	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
159	1	40	920	35	1	2	165.94	331.88	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
160	1	40	951	35	1	2	139.04	278.08	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
161	1	40	931	35	1	1	77.3	77.3	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
162	1	40	940	35	1	6	18.13	108.78	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
163	1	40	850	35	1	4	2.91	11.64	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
164	1	40	823	35	1	4	2.7	10.8	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
165	1	40	960	35	1	1	20.3	20.3	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00
166	1	40	925	36	1	6	7.69	46.14	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
167	1	40	1062	36	1	2	58.8	117.6	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
168	1	40	802	36	1	2	14.92	29.84	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
169	1	40	920	36	1	2	165.94	331.88	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
170	1	40	951	36	1	2	139.4	278.8	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
171	1	40	931	36	1	1	77.3	77.3	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
172	1	40	940	36	1	6	19.3	115.80000000000001	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
173	1	40	850	36	1	4	2.91	11.64	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
174	1	40	825	36	1	4	2.91	11.64	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
175	1	40	960	36	1	1	20.3	20.3	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:24.636252+00
176	1	42	812	37	1	1	226.8	226.8	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00
177	1	42	827	37	1	5	38.2	191	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00
178	1	42	828	37	1	5	36.12	180.6	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00
179	1	42	848	37	1	10	3.12	31.200000000000003	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00
180	1	42	1038	37	1	1	27.93	27.93	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00
181	1	42	809	37	1	1	24.38	24.38	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00
182	1	40	1078	38	1	1	4	4	2025-12-02 02:54:04.748134+00	2026-01-06 13:46:35.145866+00
183	1	47	918	39	1	1	165.94	165.94	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00
184	1	47	1001	39	1	10	14.55	145.5	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00
185	1	47	940	39	1	40	18.78	751.2	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00
186	1	47	1003	39	1	10	98.55	985.5	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00
187	1	47	1035	39	1	9	95.42	858.78	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00
188	1	47	1019	39	1	1	95.79	95.79	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00
189	1	47	1048	39	1	1	84.35	84.35	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00
190	1	21	788	40	1	60	3.29	197.4	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
191	1	21	791	40	1	60	11.7	702	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
192	1	21	873	40	1	10	90.31	903.1	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
193	1	21	966	40	1	5	156.07	780.3499999999999	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
194	1	21	822	40	1	10	112.69	1126.9	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
195	1	21	1032	40	1	10	89.7	897	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
196	1	21	882	40	1	12	6.13	73.56	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
197	1	21	881	40	1	12	6.13	73.56	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
198	1	21	848	40	1	60	3.12	187.20000000000002	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
199	1	21	928	40	1	2	111.51	223.02	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
200	1	21	933	40	1	8	59.7	477.6	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00
201	1	49	926	41	1	3	4.34	13.02	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00
202	1	49	977	41	1	3	4.5	13.5	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00
203	1	49	990	41	1	4	38.7	154.8	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00
204	1	49	983	41	1	5	17.92	89.60000000000001	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00
205	1	49	839	41	1	8	0.97	7.76	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00
206	1	49	1035	41	1	3	89.6	268.79999999999995	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00
207	1	49	788	42	1	6	3.29	19.740000000000002	2025-12-03 13:36:18.342198+00	2026-01-06 13:46:51.703577+00
208	1	49	792	42	1	6	143.87	863.22	2025-12-03 13:36:18.342198+00	2026-01-06 13:46:51.703577+00
209	1	49	1086	42	1	3	9.99	29.97	2025-12-03 13:36:18.342198+00	2026-01-06 13:46:51.703577+00
210	1	49	1079	47	1	3	5.32	15.96	2025-12-03 17:33:05.076741+00	2026-01-06 13:47:00.095094+00
211	1	49	1087	47	1	10	5.33	53.3	2025-12-03 17:33:05.076741+00	2026-01-06 13:47:00.095094+00
212	1	49	817	47	1	50	6.32	316	2025-12-03 17:33:05.076741+00	2026-01-06 13:47:00.095094+00
213	1	49	931	48	1	15	77.3	1159.5	2025-12-03 17:41:43.928426+00	2026-01-06 13:47:03.951757+00
214	1	49	937	48	1	15	103.21	1548.1499999999999	2025-12-03 17:41:43.928426+00	2026-01-06 13:47:03.951757+00
215	1	50	993	49	1	5	51.9	259.5	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
216	1	50	1002	49	1	4	20.25	81	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
217	1	50	990	49	1	6	38.7	232.20000000000002	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
218	1	50	1001	49	1	8	14.55	116.4	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
219	1	50	1036	49	1	4	89.6	358.4	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
220	1	50	804	49	1	2	2.93	5.86	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
221	1	50	977	49	1	5	4.5	22.5	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
222	1	50	791	49	1	10	11.7	117	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
223	1	50	943	49	1	20	3.12	62.400000000000006	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
224	1	50	839	49	1	30	0.97	29.099999999999998	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
225	1	50	890	49	1	3	11.05	33.150000000000006	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
226	1	50	884	49	1	4	5.87	23.48	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
227	1	50	1088	49	1	5	4.5	22.5	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00
228	1	50	1079	50	1	8	5.32	42.56	2025-12-03 18:20:58.652012+00	2026-01-06 13:47:13.510449+00
229	1	50	1087	50	1	30	5.33	159.9	2025-12-03 18:20:58.652012+00	2026-01-06 13:47:13.510449+00
230	1	50	937	51	1	10	103.21	1032.1	2025-12-03 18:24:36.954897+00	2026-01-06 13:47:16.9651+00
231	1	50	931	51	1	8	77.3	618.4	2025-12-03 18:24:36.954897+00	2026-01-06 13:47:16.9651+00
232	1	51	873	52	1	24	68.91	1653.84	2025-12-03 19:13:13.32693+00	2026-01-06 13:47:22.224555+00
233	1	51	820	52	1	12	181.81	2181.7200000000003	2025-12-03 19:13:13.32693+00	2026-01-06 13:47:22.224555+00
234	1	51	966	52	1	8	149.31	1194.48	2025-12-03 19:13:13.32693+00	2026-01-06 13:47:22.224555+00
235	1	51	1024	52	1	1	189.42	189.42	2025-12-03 19:13:13.32693+00	2026-01-06 13:47:22.224555+00
236	1	52	874	53	1	25	110.5	2762.5	2025-12-03 19:22:58.797409+00	2026-01-06 13:47:26.741379+00
237	1	52	822	53	1	3	101.17	303.51	2025-12-03 19:22:58.797409+00	2026-01-06 13:47:26.741379+00
238	1	52	1030	53	1	6	31.22	187.32	2025-12-03 19:22:58.797409+00	2026-01-06 13:47:26.741379+00
239	1	53	1089	54	1	1	559.17	559.17	2025-12-04 19:50:56.242986+00	2026-01-06 13:47:31.401399+00
240	1	53	1090	54	1	1	559.17	559.17	2025-12-04 19:50:56.242986+00	2026-01-06 13:47:31.401399+00
241	1	53	1091	54	1	1	559.17	559.17	2025-12-04 19:50:56.242986+00	2026-01-06 13:47:31.401399+00
242	1	53	1092	54	1	1	559.17	559.17	2025-12-04 19:50:56.242986+00	2026-01-06 13:47:31.401399+00
243	1	21	788	55	1	72	3.29	236.88	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
244	1	21	787	55	1	12	5.37	64.44	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
245	1	21	1062	55	1	20	58.8	1176	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
246	1	21	1015	55	1	1	123.15	123.15	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
247	1	21	874	55	1	6	100.79	604.74	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
248	1	21	824	55	1	2	131.29	262.58	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
249	1	21	876	55	1	12	370.18	4442.16	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
250	1	21	966	55	1	3	162.22	486.65999999999997	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
251	1	21	821	55	1	3	1	3	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
252	1	21	1035	55	1	2	89.6	179.2	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
253	1	21	1028	55	1	2	89.6	179.2	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
254	1	21	928	55	1	2	111.51	223.02	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00
255	1	49	1095	57	1	2	43.5	87	2025-12-12 14:11:17.569806+00	2026-01-06 13:47:40.59687+00
256	1	54	1071	56	1	3	46.67	140.01	2025-12-10 12:15:19.558744+00	2026-01-06 13:47:43.381975+00
257	1	54	904	56	1	2	293.63	587.26	2025-12-10 12:15:19.558744+00	2026-01-06 13:47:43.381975+00
\.


--
-- Data for Name: movimentacoes_estoque; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.movimentacoes_estoque (id, tipo_movimentacao, quantidade, observacao, data_movimentacao, produto_id, usuario_id, origem, quantidade_antes, quantidade_depois, status, aprovado_por_id, data_aprovacao, motivo_rejeicao, motivo_movimentacao, observacao_motivo, dados_antes_edicao, dados_depois_edicao, reversao_de_id, revertida, data_reversao, revertida_por_id) FROM stdin;
2	SAIDA	60	\N	2025-07-15 19:20:12.482199+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3	SAIDA	3	\N	2025-07-15 19:20:53.686504+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
4	SAIDA	7	\N	2025-07-15 19:21:27.602807+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
5	SAIDA	5	\N	2025-07-15 19:21:49.331494+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
6	SAIDA	3	\N	2025-07-15 19:22:05.472954+00	992	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
7	SAIDA	1	\N	2025-07-15 19:23:16.566854+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
8	SAIDA	5	\N	2025-07-15 19:23:39.497322+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
9	SAIDA	3	\N	2025-07-15 19:23:56.085508+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
10	SAIDA	1	\N	2025-07-15 19:24:11.411744+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
11	SAIDA	1	\N	2025-07-15 19:24:34.572292+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
12	SAIDA	20	\N	2025-07-15 19:25:00.604185+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
13	SAIDA	1	\N	2025-07-15 19:28:36.569111+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
14	SAIDA	1	\N	2025-07-15 19:28:53.156814+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
15	SAIDA	5	\N	2025-07-15 19:29:16.607149+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
16	SAIDA	2	\N	2025-07-15 19:29:49.811438+00	908	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
17	SAIDA	4	\N	2025-07-15 19:30:13.414096+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
18	SAIDA	2	\N	2025-07-15 19:30:27.912534+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
19	SAIDA	2	\N	2025-07-15 19:30:41.266077+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
20	SAIDA	2	\N	2025-07-16 11:00:16.863715+00	840	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
21	SAIDA	1	\N	2025-07-16 14:07:24.93749+00	813	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
22	SAIDA	1	\N	2025-07-16 14:07:37.014815+00	963	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
23	SAIDA	1	\N	2025-07-17 12:25:33.245215+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
24	SAIDA	1	\N	2025-07-17 12:25:47.799418+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
25	SAIDA	2	\N	2025-07-17 12:26:00.450427+00	1021	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
26	SAIDA	14	\N	2025-07-17 12:26:25.979474+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
27	ENTRADA	10	\N	2025-07-17 12:26:40.725988+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
28	SAIDA	2	\N	2025-07-17 12:27:08.98447+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
29	SAIDA	1	\N	2025-07-17 12:27:21.762183+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
30	SAIDA	5	\N	2025-07-17 12:28:36.1516+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
31	SAIDA	15	\N	2025-07-18 11:22:59.73144+00	787	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
32	SAIDA	4	\N	2025-07-18 18:19:32.231875+00	896	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
33	SAIDA	4	\N	2025-07-18 18:19:32.513939+00	896	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
34	SAIDA	4	\N	2025-07-18 18:19:58.610476+00	890	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
35	SAIDA	2	\N	2025-07-18 18:42:41.029846+00	796	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
36	ENTRADA	3	\N	2025-07-18 18:42:58.852486+00	793	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
37	SAIDA	2	\N	2025-07-18 18:43:20.198052+00	863	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
38	SAIDA	8	\N	2025-07-18 18:44:26.109198+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
39	SAIDA	4	\N	2025-07-18 18:45:12.101926+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
40	SAIDA	6	\N	2025-07-18 18:45:38.086165+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
41	SAIDA	3	\N	2025-07-18 18:45:57.626572+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
42	SAIDA	1	\N	2025-07-18 18:46:16.191855+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
43	SAIDA	24	\N	2025-07-18 18:46:35.616548+00	884	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
44	SAIDA	2	\N	2025-07-18 18:46:58.256521+00	863	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
45	SAIDA	9	\N	2025-07-18 18:48:27.832915+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
46	SAIDA	9	\N	2025-07-18 18:48:52.321675+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
47	ENTRADA	30	\N	2025-07-18 18:58:20.282657+00	931	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
48	ENTRADA	20	\N	2025-07-18 18:58:42.59103+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
49	ENTRADA	15	\N	2025-07-18 18:59:02.947611+00	928	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
50	ENTRADA	30	\N	2025-07-18 18:59:21.915535+00	1038	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
51	ENTRADA	30	\N	2025-07-18 19:11:06.272801+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
52	ENTRADA	10	\N	2025-07-18 19:11:24.919537+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
53	ENTRADA	200	\N	2025-07-18 19:15:53.251544+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
54	SAIDA	16	\N	2025-07-21 19:22:24.591399+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
55	SAIDA	8	\N	2025-07-21 19:22:46.542565+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
56	SAIDA	1	\N	2025-07-21 19:23:01.816065+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
57	SAIDA	1	\N	2025-07-21 19:23:17.366032+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
58	SAIDA	9	\N	2025-07-21 19:23:42.64669+00	1003	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
59	SAIDA	80	\N	2025-07-21 19:24:12.521815+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
60	SAIDA	2	\N	2025-07-21 19:24:27.107534+00	818	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
61	SAIDA	2	\N	2025-07-21 19:24:27.557526+00	818	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
62	SAIDA	2	\N	2025-07-21 19:25:04.177393+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
63	SAIDA	15	\N	2025-07-21 19:25:29.434397+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
64	SAIDA	6	\N	2025-07-21 19:25:52.110049+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
65	SAIDA	8	\N	2025-07-21 19:26:07.532763+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
66	SAIDA	2	\N	2025-07-21 19:26:30.998801+00	1038	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
67	SAIDA	1	\N	2025-07-21 19:26:45.247048+00	837	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
68	ENTRADA	2	\N	2025-07-21 19:28:05.635034+00	787	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
69	SAIDA	1	\N	2025-07-21 19:28:37.057207+00	906	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
70	SAIDA	2	\N	2025-07-21 19:28:58.952245+00	976	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
71	SAIDA	6	\N	2025-07-21 19:29:41.512598+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
72	SAIDA	20	\N	2025-07-21 19:30:04.610956+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
73	SAIDA	10	\N	2025-07-21 19:30:24.567218+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
74	SAIDA	20	\N	2025-07-21 19:30:38.834998+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
75	SAIDA	30	\N	2025-07-21 19:30:54.265347+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
76	SAIDA	15	\N	2025-07-21 19:31:30.22922+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
77	SAIDA	6	\N	2025-07-21 19:32:01.512439+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
78	SAIDA	6	\N	2025-07-21 19:32:01.949207+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
79	SAIDA	4	\N	2025-07-21 19:40:55.560159+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
80	SAIDA	3	\N	2025-07-21 19:41:16.575242+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
81	SAIDA	12	\N	2025-07-21 19:41:33.033718+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
82	SAIDA	12	\N	2025-07-21 19:41:33.267474+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
83	SAIDA	2	\N	2025-07-21 19:41:56.144777+00	972	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
84	SAIDA	2	\N	2025-07-21 19:41:58.378842+00	972	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
85	SAIDA	2	\N	2025-07-21 19:43:29.94331+00	809	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
86	SAIDA	5	\N	2025-07-21 19:43:49.314435+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
87	SAIDA	5	\N	2025-07-21 19:43:50.04345+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
88	ENTRADA	1	\N	2025-07-21 19:44:10.440278+00	1038	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
89	SAIDA	10	\N	2025-07-21 19:44:33.292833+00	868	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
90	SAIDA	36	\N	2025-07-21 19:45:03.424078+00	850	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
91	SAIDA	4	\N	2025-07-21 19:45:24.69421+00	976	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
92	ENTRADA	240	\N	2025-07-22 16:52:22.675578+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
93	ENTRADA	7	\N	2025-07-22 16:53:01.32742+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
94	ENTRADA	3	\N	2025-07-22 16:53:18.27074+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
95	SAIDA	65	\N	2025-07-22 16:54:04.924487+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
96	SAIDA	2	\N	2025-07-22 16:54:15.90284+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
97	SAIDA	6	\N	2025-07-22 16:55:01.012853+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
98	SAIDA	2	\N	2025-07-22 16:55:12.843831+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
99	SAIDA	5	\N	2025-07-22 16:55:44.115307+00	992	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
100	SAIDA	3	\N	2025-07-22 16:56:43.478382+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
101	SAIDA	3	\N	2025-07-22 16:57:21.211414+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
102	SAIDA	7	\N	2025-07-22 16:57:37.790345+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
103	SAIDA	3	\N	2025-07-22 16:57:54.08352+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
104	SAIDA	3	\N	2025-07-22 16:58:06.31162+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
105	SAIDA	7	\N	2025-07-22 16:58:39.267599+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
106	SAIDA	2	\N	2025-07-22 16:58:51.412438+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
107	SAIDA	2	\N	2025-07-22 16:59:17.306327+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
108	SAIDA	2	\N	2025-07-22 16:59:33.243109+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
109	SAIDA	1	\N	2025-07-22 16:59:47.576221+00	859	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
110	SAIDA	2	\N	2025-07-22 17:00:02.087837+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
111	ENTRADA	2	\N	2025-07-22 17:00:17.006247+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
112	SAIDA	2	\N	2025-07-22 17:00:25.942749+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
113	SAIDA	4	\N	2025-07-22 17:00:55.326756+00	963	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
114	SAIDA	4	\N	2025-07-22 17:01:18.90489+00	813	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
115	ENTRADA	4	\N	2025-07-22 17:03:16.458591+00	856	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
116	ENTRADA	12	\N	2025-07-22 17:03:34.751407+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
117	ENTRADA	72	\N	2025-07-22 17:04:20.714191+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
118	ENTRADA	4	\N	2025-07-22 17:06:00.170622+00	1012	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
119	ENTRADA	4	\N	2025-07-22 18:37:29.606982+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
120	ENTRADA	4	\N	2025-07-22 18:37:50.225632+00	1014	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
121	ENTRADA	12	\N	2025-07-22 18:38:07.644215+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
122	ENTRADA	12	\N	2025-07-22 18:38:25.90822+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
123	ENTRADA	4	\N	2025-07-22 18:38:41.162414+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
124	ENTRADA	18	\N	2025-07-22 18:39:00.364873+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
125	ENTRADA	12	\N	2025-07-22 18:39:28.214267+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
126	ENTRADA	12	\N	2025-07-22 18:39:46.650843+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
127	ENTRADA	4	\N	2025-07-22 18:39:56.593312+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
128	ENTRADA	12	\N	2025-07-22 18:40:31.017702+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
129	ENTRADA	4	\N	2025-07-22 18:45:26.445165+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
130	ENTRADA	4	\N	2025-07-22 18:45:44.656973+00	908	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
131	ENTRADA	8	\N	2025-07-22 18:46:00.915083+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
132	ENTRADA	8	\N	2025-07-22 18:46:10.690502+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
133	ENTRADA	8	\N	2025-07-22 18:46:29.084521+00	1010	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
134	ENTRADA	4	\N	2025-07-22 18:46:43.759509+00	1013	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
135	ENTRADA	7	\N	2025-07-22 18:46:58.295303+00	840	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
136	SAIDA	4	\N	2025-07-22 20:05:07.383933+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
137	SAIDA	4	\N	2025-07-22 20:05:29.978733+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
139	SAIDA	35	\N	2025-07-22 20:06:25.423841+00	997	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
141	SAIDA	22	\N	2025-07-22 20:07:18.866121+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
143	ENTRADA	3	\N	2025-07-22 20:07:55.184471+00	997	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
145	SAIDA	2	\N	2025-07-22 20:09:01.633147+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
147	SAIDA	1	\N	2025-07-22 20:09:32.730557+00	949	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
149	SAIDA	5	\N	2025-07-22 20:10:10.263768+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
151	SAIDA	3	\N	2025-07-22 20:10:53.036332+00	999	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
153	SAIDA	2	\N	2025-07-22 20:11:41.189533+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
155	SAIDA	1	\N	2025-07-22 20:12:17.268574+00	837	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
157	SAIDA	5	\N	2025-07-22 20:12:48.55984+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
159	SAIDA	2	\N	2025-07-22 20:13:19.371448+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
161	SAIDA	5	\N	2025-07-22 20:14:08.190168+00	937	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
163	SAIDA	3	\N	2025-07-23 17:08:48.079575+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
166	SAIDA	7	\N	2025-07-25 11:52:03.244979+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1221	SAIDA	2	Importação automática - NF: 0000001182	2025-10-07 14:03:31.073841+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1222	SAIDA	2	Importação automática - NF: 0000001182	2025-10-07 14:03:31.073841+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1223	SAIDA	1	Importação automática - NF: 0000001182	2025-10-07 14:03:31.073841+00	963	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1232	SAIDA	4	Importação automática - NF: 0000001185	2025-10-07 14:11:13.423409+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1233	SAIDA	1	Importação automática - NF: 0000001185	2025-10-07 14:11:13.423409+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1234	SAIDA	1	Importação automática - NF: 0000001185	2025-10-07 14:11:13.423409+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1235	SAIDA	24	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	850	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1236	SAIDA	30	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	926	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1237	SAIDA	20	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1238	SAIDA	10	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1239	SAIDA	10	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	787	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1240	SAIDA	10	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1241	SAIDA	28	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1242	SAIDA	2	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	827	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1243	SAIDA	5	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1244	SAIDA	6	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	1045	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1245	SAIDA	7	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	976	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1246	SAIDA	2	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	836	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1247	SAIDA	6	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	868	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1248	SAIDA	1	Importação automática - NF: 0000004648	2025-10-08 13:53:18.262763+00	902	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1249	SAIDA	15	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	926	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1250	SAIDA	10	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1251	SAIDA	15	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1252	SAIDA	20	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1253	SAIDA	8	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1254	SAIDA	15	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1255	SAIDA	2	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	827	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1256	SAIDA	2	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1257	SAIDA	4	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	976	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1258	SAIDA	1	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	809	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1259	SAIDA	1	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	958	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1260	SAIDA	12	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	850	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1261	SAIDA	5	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	868	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1262	SAIDA	1	Importação automática - NF: 0000004647	2025-10-08 13:56:35.639252+00	798	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1270	SAIDA	80	Importação automática - NF: 0000004643	2025-10-08 14:13:47.834256+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1447	SAIDA	5	\N	2025-10-22 13:06:19.252568+00	902	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1452	SAIDA	5	\N	2025-10-22 13:10:24.778367+00	1038	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1457	SAIDA	2	\N	2025-10-22 13:13:41.250549+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1459	SAIDA	4	Importação automática - NF: 0000004661	2025-10-22 13:30:10.311537+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1460	SAIDA	4	Importação automática - NF: 0000004661	2025-10-22 13:30:10.311537+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1461	SAIDA	1	Importação automática - NF: 0000004661	2025-10-22 13:30:10.311537+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1462	SAIDA	2	Importação automática - NF: 0000004660	2025-10-22 13:31:16.538503+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1463	SAIDA	1	Importação automática - NF: 0000004660	2025-10-22 13:31:16.538503+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1464	SAIDA	1	Importação automática - NF: 0000004660	2025-10-22 13:31:16.538503+00	1021	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1465	SAIDA	12	Importação automática - NF: 0000001199	2025-10-22 13:32:02.173775+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1466	SAIDA	2	Importação automática - NF: 0000001199	2025-10-22 13:32:02.173775+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1467	SAIDA	1	Importação automática - NF: 0000001199	2025-10-22 13:32:02.173775+00	863	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1473	SAIDA	2	Importação automática - NF: 0000004663	2025-10-22 13:39:41.552907+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1474	SAIDA	2	Importação automática - NF: 0000004663	2025-10-22 13:39:41.552907+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1475	SAIDA	1	Importação automática - NF: 0000004663	2025-10-22 13:39:41.552907+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1476	SAIDA	5	Importação automática - NF: 0000004663	2025-10-22 13:39:41.552907+00	932	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1477	SAIDA	2	Importação automática - NF: 0000004663	2025-10-22 13:39:41.552907+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1478	SAIDA	1	Importação automática - NF: 0000001200	2025-10-22 13:40:20.607886+00	813	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1479	SAIDA	1	Importação automática - NF: 0000001200	2025-10-22 13:40:20.607886+00	963	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1480	SAIDA	3	Importação automática - NF: 0000001200	2025-10-22 13:40:20.607886+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1481	SAIDA	2	Importação automática - NF: 0000001201	2025-10-22 13:41:17.553795+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1482	SAIDA	2	Importação automática - NF: 0000001201	2025-10-22 13:41:17.553795+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1483	SAIDA	1	Importação automática - NF: 0000001201	2025-10-22 13:41:17.553795+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1494	SAIDA	45	\N	2025-10-23 12:08:05.08681+00	1068	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1498	SAIDA	13	\N	2025-10-24 12:26:37.999931+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1500	ENTRADA	16	\N	2025-10-24 12:35:26.993641+00	919	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1509	ENTRADA	8	\N	2025-10-24 12:37:45.031629+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1514	ENTRADA	3	\N	2025-10-24 12:40:24.353274+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1554	SAIDA	8	\N	2025-10-28 12:58:22.674425+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1570	ENTRADA	12	\N	2025-10-28 13:30:34.624041+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1572	ENTRADA	16	\N	2025-10-28 13:31:02.716943+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1574	ENTRADA	20	\N	2025-10-28 13:31:23.885118+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1576	ENTRADA	6	\N	2025-10-28 13:31:58.48116+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1578	ENTRADA	8	\N	2025-10-28 14:48:55.001836+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1580	ENTRADA	4	\N	2025-10-28 14:49:39.526208+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1582	ENTRADA	10	\N	2025-10-28 19:22:30.996582+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1584	ENTRADA	600	\N	2025-10-28 19:22:46.904549+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1585	SAIDA	1	THIAGO	2025-10-29 14:28:09.40734+00	853	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1586	ENTRADA	1	\N	2025-10-29 17:14:58.560131+00	939	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1588	ENTRADA	120	\N	2025-10-29 17:21:52.541119+00	1040	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1589	ENTRADA	60	\N	2025-10-29 17:27:36.664224+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1591	ENTRADA	240	\N	2025-10-29 17:28:13.900001+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
138	SAIDA	4	\N	2025-07-22 20:05:50.954655+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
140	SAIDA	33	\N	2025-07-22 20:06:49.627788+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
142	SAIDA	14	\N	2025-07-22 20:07:36.888686+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
144	SAIDA	3	\N	2025-07-22 20:08:44.27216+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
146	SAIDA	3	\N	2025-07-22 20:09:18.428106+00	946	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
148	SAIDA	12	\N	2025-07-22 20:09:50.492857+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
150	SAIDA	3	\N	2025-07-22 20:10:31.832974+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
152	SAIDA	2	\N	2025-07-22 20:11:16.647031+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
154	SAIDA	8	\N	2025-07-22 20:12:04.798825+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
156	SAIDA	2	\N	2025-07-22 20:12:28.652936+00	827	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
158	SAIDA	24	\N	2025-07-22 20:13:05.666419+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
160	SAIDA	30	\N	2025-07-22 20:13:47.802086+00	931	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
162	SAIDA	5	\N	2025-07-23 17:08:05.332134+00	937	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
164	ENTRADA	3	\N	2025-07-23 17:09:18.288567+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
165	SAIDA	10	\N	2025-07-25 11:51:41.946273+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
167	ENTRADA	1	\N	2025-07-25 12:44:10.571629+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
168	ENTRADA	87	\N	2025-07-25 12:44:56.189422+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
169	ENTRADA	29	\N	2025-07-25 12:45:33.849917+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
170	ENTRADA	30	\N	2025-07-25 13:07:33.124708+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
171	ENTRADA	1	\N	2025-07-25 13:08:20.136102+00	1003	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
172	SAIDA	10	\N	2025-07-25 13:11:51.722455+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
173	ENTRADA	19	\N	2025-07-25 13:12:17.232172+00	1003	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
174	ENTRADA	22	\N	2025-07-25 13:18:22.542786+00	787	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
175	SAIDA	1	\N	2025-07-25 16:19:33.435053+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
176	SAIDA	41	\N	2025-07-25 16:20:02.346336+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
177	SAIDA	24	\N	2025-07-25 16:20:39.760453+00	884	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
178	SAIDA	27	\N	2025-07-25 16:21:04.982433+00	847	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
179	ENTRADA	10	\N	2025-07-25 16:21:24.244524+00	847	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
180	SAIDA	3	\N	2025-07-25 16:21:47.036406+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
181	SAIDA	24	\N	2025-07-25 16:22:05.310427+00	883	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
182	SAIDA	8	\N	2025-07-25 16:22:23.528765+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
183	SAIDA	20	\N	2025-07-25 16:22:54.708184+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
184	SAIDA	20	\N	2025-07-25 16:23:12.102253+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
185	SAIDA	8	\N	2025-07-25 16:23:31.078037+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
186	SAIDA	5	\N	2025-07-25 16:24:04.229962+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
187	SAIDA	4	\N	2025-07-25 16:27:12.638009+00	1010	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
188	SAIDA	3	\N	2025-07-25 16:27:21.233115+00	1012	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
189	SAIDA	20	\N	2025-07-25 16:27:40.111246+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
190	SAIDA	4	\N	2025-07-25 16:28:09.321204+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
191	SAIDA	4	\N	2025-07-25 16:28:23.442026+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
192	SAIDA	2	\N	2025-07-25 16:29:10.508433+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
193	SAIDA	1	\N	2025-07-25 16:29:29.835065+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
194	SAIDA	1	\N	2025-07-25 16:30:01.227583+00	1004	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
195	SAIDA	1	\N	2025-07-25 16:30:12.120608+00	1003	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
196	SAIDA	1	\N	2025-07-25 16:30:26.582441+00	965	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
197	SAIDA	1	\N	2025-07-25 16:30:36.634866+00	962	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
198	SAIDA	50	\N	2025-07-29 18:59:56.064283+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
199	ENTRADA	32	\N	2025-07-30 18:19:40.114195+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
200	ENTRADA	32	\N	2025-07-30 18:20:00.837555+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
201	ENTRADA	8	\N	2025-07-30 18:20:21.011683+00	860	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
202	ENTRADA	4	\N	2025-07-30 18:20:34.260324+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
203	ENTRADA	16	\N	2025-07-30 18:20:54.349926+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
204	ENTRADA	52	\N	2025-07-30 18:21:20.557224+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
205	ENTRADA	4	\N	2025-07-30 18:21:35.366666+00	952	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
206	ENTRADA	12	\N	2025-07-30 18:21:47.961141+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
207	ENTRADA	20	\N	2025-07-30 18:22:16.641223+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
208	ENTRADA	12	\N	2025-07-30 18:22:31.93649+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
209	ENTRADA	7	\N	2025-07-30 18:22:48.506829+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
210	ENTRADA	32	\N	2025-07-30 18:22:58.073765+00	919	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
211	ENTRADA	4	\N	2025-07-30 18:23:08.803036+00	813	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
212	ENTRADA	80	\N	2025-07-30 18:23:25.53033+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
213	ENTRADA	2	\N	2025-07-30 18:23:36.041135+00	866	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
214	SAIDA	8	\N	2025-07-30 18:24:50.687837+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
215	SAIDA	4	\N	2025-07-30 18:25:03.573883+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
216	ENTRADA	2	\N	2025-07-30 18:25:21.816726+00	860	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
217	SAIDA	32	\N	2025-07-30 18:25:35.310241+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
218	SAIDA	2	\N	2025-07-30 18:26:03.417426+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
219	SAIDA	3	\N	2025-07-30 18:26:20.972709+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
220	SAIDA	65	\N	2025-07-30 18:26:55.047949+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
221	SAIDA	2	\N	2025-07-30 18:28:02.382258+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
222	SAIDA	6	\N	2025-07-30 18:28:14.672281+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
223	SAIDA	8	\N	2025-07-30 18:28:34.022745+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
224	SAIDA	48	\N	2025-07-30 18:29:14.976949+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
225	SAIDA	2	\N	2025-07-30 18:29:27.851434+00	856	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
226	SAIDA	3	\N	2025-07-30 18:30:12.912417+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
227	SAIDA	2	\N	2025-07-30 18:30:25.373429+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
228	SAIDA	1	\N	2025-07-30 18:31:21.297547+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
229	SAIDA	6	\N	2025-07-30 18:31:39.664416+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
230	SAIDA	6	\N	2025-07-30 18:32:17.832167+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
231	SAIDA	1	\N	2025-07-30 18:32:35.440791+00	933	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
232	SAIDA	1	\N	2025-07-30 18:32:49.346526+00	937	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
233	SAIDA	5	\N	2025-07-30 18:33:04.529432+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
234	SAIDA	5	\N	2025-07-30 18:33:49.304175+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
235	SAIDA	1	\N	2025-07-30 18:34:04.149625+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
236	SAIDA	6	\N	2025-07-30 18:34:18.34944+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
237	SAIDA	1	\N	2025-07-30 18:34:31.662297+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
238	SAIDA	1	\N	2025-07-30 18:35:40.493939+00	927	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
239	SAIDA	2	\N	2025-07-30 18:36:01.272698+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
240	SAIDA	1	\N	2025-07-30 18:36:12.374334+00	804	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
241	SAIDA	3	\N	2025-07-30 18:36:24.724135+00	895	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
242	SAIDA	4	\N	2025-07-30 18:36:34.79859+00	1045	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
243	SAIDA	56	\N	2025-07-31 14:18:33.669126+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
244	SAIDA	55	\N	2025-07-31 14:18:50.807715+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
245	SAIDA	27	\N	2025-07-31 14:19:14.813555+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
246	SAIDA	30	\N	2025-07-31 14:19:37.33215+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
247	SAIDA	2	\N	2025-07-31 14:19:56.933395+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
248	SAIDA	6	\N	2025-07-31 14:20:17.150184+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
249	SAIDA	45	\N	2025-07-31 14:39:00.153625+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
250	SAIDA	10	\N	2025-08-01 13:18:17.338971+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
251	SAIDA	10	\N	2025-08-01 13:22:51.529147+00	844	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
252	SAIDA	10	\N	2025-08-01 13:22:59.105802+00	843	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
253	SAIDA	1	\N	2025-08-01 13:23:19.634647+00	995	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
254	SAIDA	1	\N	2025-08-01 13:23:39.067417+00	1038	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
255	SAIDA	1	\N	2025-08-01 13:23:58.174405+00	808	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
256	SAIDA	3	\N	2025-08-01 13:24:28.458428+00	1038	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
257	SAIDA	3	\N	2025-08-01 13:24:44.747637+00	972	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
258	SAIDA	3	\N	2025-08-01 13:24:58.075478+00	808	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
259	SAIDA	5	\N	2025-08-01 13:25:19.473208+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
260	SAIDA	5	\N	2025-08-01 13:25:40.457696+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
261	SAIDA	2	\N	2025-08-01 13:25:56.895597+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
262	SAIDA	2	\N	2025-08-01 13:26:13.657114+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
263	SAIDA	2	\N	2025-08-01 13:26:57.286169+00	880	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
264	SAIDA	1	\N	2025-08-01 13:27:13.940436+00	916	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
265	SAIDA	1	\N	2025-08-01 13:27:14.247927+00	916	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
266	SAIDA	8	\N	2025-08-01 13:27:31.915223+00	1040	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
267	SAIDA	25	\N	2025-08-01 13:27:54.336648+00	817	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
268	SAIDA	25	\N	2025-08-01 13:27:54.588818+00	817	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
269	SAIDA	2	\N	2025-08-01 13:28:11.183717+00	934	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
270	SAIDA	3	\N	2025-08-01 13:28:31.652238+00	833	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
271	SAIDA	4	\N	2025-08-01 13:28:49.32665+00	834	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
272	SAIDA	3	\N	2025-08-01 13:34:27.422088+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
273	ENTRADA	4	\N	2025-08-01 13:34:45.856953+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
274	SAIDA	10	\N	2025-08-01 13:37:52.467544+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
275	SAIDA	21	\N	2025-08-01 13:38:12.647878+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
276	SAIDA	2	\N	2025-08-01 13:38:27.972636+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
277	SAIDA	2	\N	2025-08-01 13:38:41.464185+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
278	SAIDA	1	\N	2025-08-01 13:39:23.113067+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
279	SAIDA	1	\N	2025-08-01 13:39:31.412426+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
280	SAIDA	6	\N	2025-08-01 13:41:53.125577+00	1026	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
281	SAIDA	1	\N	2025-08-01 13:42:20.089929+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
283	ENTRADA	4	\N	2025-08-01 13:47:55.609374+00	1031	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
284	SAIDA	5	\N	2025-08-01 13:57:21.729816+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
285	ENTRADA	290	\N	2025-08-05 18:25:34.198236+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
286	ENTRADA	4	\N	2025-08-05 18:25:44.158948+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
287	ENTRADA	15	\N	2025-08-05 18:25:52.069855+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
288	ENTRADA	132	\N	2025-08-05 18:29:04.370269+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
289	ENTRADA	100	\N	2025-08-05 18:29:21.21894+00	1041	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
290	ENTRADA	48	\N	2025-08-05 18:29:30.259181+00	1040	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
291	ENTRADA	40	\N	2025-08-05 18:29:43.256534+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
292	ENTRADA	200	\N	2025-08-05 18:31:50.452852+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
293	ENTRADA	6	zerando o estoque	2025-08-15 12:53:01.861093+00	851	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
294	SAIDA	5	\N	2025-08-18 11:33:35.900172+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
295	SAIDA	6	\N	2025-08-18 11:34:00.32012+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
296	SAIDA	1	\N	2025-08-18 11:34:15.77104+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
297	SAIDA	4	\N	2025-08-18 12:21:59.617551+00	822	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
298	SAIDA	6	\N	2025-08-18 12:22:39.19593+00	1030	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
299	SAIDA	1	\N	2025-08-18 12:23:11.644676+00	1006	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
300	SAIDA	1	\N	2025-08-18 12:23:53.424359+00	820	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
301	SAIDA	5	\N	2025-08-18 12:24:07.377206+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
302	SAIDA	3	\N	2025-08-18 12:24:22.504142+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
303	SAIDA	1	\N	2025-08-18 12:24:39.571473+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
304	SAIDA	20	\N	2025-08-18 12:24:52.915673+00	936	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
305	SAIDA	1	\N	2025-08-18 12:25:06.27847+00	935	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
306	SAIDA	1	\N	2025-08-18 12:25:26.138811+00	791	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
307	SAIDA	1	\N	2025-08-18 12:25:52.09425+00	1033	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
308	SAIDA	3	\N	2025-08-18 12:26:12.959543+00	1030	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
309	ENTRADA	19	\N	2025-08-18 17:53:21.175083+00	858	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
310	ENTRADA	8	\N	2025-08-18 17:53:32.919456+00	857	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
311	ENTRADA	115	\N	2025-08-19 14:19:18.116633+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
312	ENTRADA	61	\N	2025-08-19 14:21:13.251016+00	889	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
313	SAIDA	14	\N	2025-08-19 14:24:15.399212+00	1040	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
314	ENTRADA	45	total 60 (quando entrar tirar o excedente de "15")	2025-08-19 18:38:36.880784+00	1025	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
315	SAIDA	90	quando entrar novo estoque remover o excedente de 15	2025-08-19 18:39:00.26797+00	1025	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
316	SAIDA	20	\N	2025-08-19 18:39:32.239066+00	897	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
317	SAIDA	40	\N	2025-08-19 18:40:16.916718+00	1040	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
318	SAIDA	2	\N	2025-08-19 18:40:55.768221+00	1036	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
319	SAIDA	26	quando entrar produto retirar excedente de 10	2025-08-19 18:42:39.192025+00	787	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
320	SAIDA	15	retirar mais 10 ao chegar produto	2025-08-19 18:45:16.80382+00	857	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
321	SAIDA	15	\N	2025-08-19 18:45:33.184337+00	858	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
322	ENTRADA	4	\N	2025-08-19 18:45:47.589152+00	963	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
323	SAIDA	8	\N	2025-08-19 18:46:02.569679+00	963	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
324	ENTRADA	112	entrada girassol	2025-08-19 18:46:55.166878+00	789	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
325	ENTRADA	2	nf girassol	2025-08-19 18:47:23.46599+00	860	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
326	ENTRADA	14	nf girassol	2025-08-19 18:48:06.45191+00	860	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
327	ENTRADA	32	\N	2025-08-19 18:49:44.860853+00	789	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
328	ENTRADA	12	\N	2025-08-19 18:50:17.269426+00	792	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
329	ENTRADA	52	\N	2025-08-19 18:50:44.721256+00	820	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
330	ENTRADA	100	\N	2025-08-19 18:51:00.477443+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
331	ENTRADA	12	\N	2025-08-19 18:51:16.497698+00	873	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
332	ENTRADA	95	\N	2025-08-19 18:51:28.029622+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
333	ENTRADA	5	\N	2025-08-19 18:51:40.398542+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
334	ENTRADA	52	\N	2025-08-19 18:52:10.70193+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
335	ENTRADA	4	\N	2025-08-19 18:53:24.404603+00	903	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
336	ENTRADA	4	\N	2025-08-19 18:54:24.416097+00	907	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
337	ENTRADA	24	\N	2025-08-19 18:55:30.023677+00	1030	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
338	ENTRADA	8	\N	2025-08-19 18:56:25.487024+00	1033	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
339	ENTRADA	5	\N	2025-08-19 18:58:00.722292+00	863	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
340	ENTRADA	4	\N	2025-08-19 18:58:25.696851+00	870	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
341	ENTRADA	4	\N	2025-08-19 18:58:42.741487+00	952	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
342	ENTRADA	4	\N	2025-08-19 18:59:01.98608+00	856	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
343	ENTRADA	4	\N	2025-08-19 19:00:18.698756+00	856	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
344	ENTRADA	1	\N	2025-08-19 19:00:49.194096+00	919	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
345	ENTRADA	23	\N	2025-08-19 19:01:10.727311+00	919	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
346	ENTRADA	8	\N	2025-08-19 19:02:01.565916+00	951	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
347	ENTRADA	8	\N	2025-08-19 19:02:32.301111+00	1010	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
348	ENTRADA	16	\N	2025-08-19 19:03:59.079899+00	1015	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
349	ENTRADA	16	\N	2025-08-19 19:04:12.473232+00	1016	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
350	ENTRADA	4	\N	2025-08-19 19:04:41.098413+00	1021	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
351	ENTRADA	4	\N	2025-08-19 19:05:32.37977+00	1007	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
352	SAIDA	98	cedro	2025-08-19 19:08:58.980767+00	789	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
353	ENTRADA	10	\N	2025-08-19 19:09:15.310882+00	860	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
354	SAIDA	2	FITNESS CLUB LTDA	2025-08-19 19:10:11.630923+00	904	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
355	SAIDA	2	L & S RESTAURANTE LTDA	2025-08-19 19:10:45.629735+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
356	SAIDA	1	L & S RESTAURANTE LTDA	2025-08-19 19:11:09.608737+00	822	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
357	SAIDA	1	L & S RESTAURANTE LTDA	2025-08-19 19:12:33.580212+00	887	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
358	SAIDA	10	L & S RESTAURANTE LTDA	2025-08-19 19:14:30.016628+00	845	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
359	SAIDA	1	J S GONDIM LINHARES FILHO	2025-08-19 19:15:16.242401+00	1038	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
360	SAIDA	1	J S GONDIM LINHARES FILHO	2025-08-19 19:16:47.489513+00	809	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
361	SAIDA	55	J S GONDIM LINHARES FILHO	2025-08-19 19:17:10.628768+00	936	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
362	SAIDA	3	J S GONDIM LINHARES FILHO	2025-08-19 19:18:28.009902+00	992	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
363	SAIDA	3	J S GONDIM LINHARES FILHO	2025-08-19 19:19:17.620822+00	996	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
364	SAIDA	3	J S GONDIM LINHARES FILHO	2025-08-19 19:20:15.174881+00	935	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
365	SAIDA	3	L A F COSTA ESCOLA LTDA	2025-08-19 19:20:53.547899+00	802	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
366	SAIDA	6	L A F COSTA ESCOLA LTDA	2025-08-19 19:21:40.405901+00	931	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
367	SAIDA	30	L A F COSTA ESCOLA LTDA	2025-08-19 19:24:12.113146+00	941	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
368	SAIDA	3	L A F COSTA ESCOLA LTDA	2025-08-19 19:24:30.935638+00	825	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
369	SAIDA	2	L A F COSTA ESCOLA LTDA	2025-08-19 19:24:50.654898+00	839	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
370	SAIDA	3	L A F COSTA ESCOLA LTDA	2025-08-19 19:25:32.256876+00	925	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
371	SAIDA	12	L A F COSTA ESCOLA LTDA	2025-08-19 19:26:16.951593+00	788	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
372	SAIDA	3	L A F COSTA ESCOLA LTDA	2025-08-19 19:26:40.715651+00	977	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
373	SAIDA	12	MEGA SERVICOS E ALIMENTOS LTDA	2025-08-19 19:32:48.389679+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1448	SAIDA	5	\N	2025-10-22 13:07:46.741844+00	968	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
375	SAIDA	5	\N	2025-08-21 12:34:28.487621+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
376	SAIDA	10	\N	2025-08-21 13:16:47.751083+00	889	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
377	SAIDA	50	\N	2025-08-21 13:16:57.080348+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
378	SAIDA	56	\N	2025-08-21 13:17:16.208634+00	895	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
379	SAIDA	8	\N	2025-08-21 13:18:32.741641+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
380	SAIDA	4	\N	2025-08-21 13:18:41.373874+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
381	SAIDA	24	Associação manual - Código PDF: 734	2025-08-21 14:44:07.009593+00	883	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
382	SAIDA	3	Associação manual - Código PDF: 518	2025-08-21 14:44:26.997492+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
383	SAIDA	5	Associação manual - Código PDF: 215	2025-08-21 14:44:29.034525+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
384	SAIDA	24	Associação manual - Código PDF: 734	2025-08-21 14:44:31.785819+00	883	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
385	SAIDA	5	Associação manual - Código PDF: 215	2025-08-21 15:07:20.36768+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
386	SAIDA	3	Associação manual - Código PDF: 518	2025-08-21 15:08:46.84278+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
387	ENTRADA	10	\N	2025-08-21 15:10:10.191249+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
388	ENTRADA	6	\N	2025-08-21 15:10:38.962587+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
389	SAIDA	3	Associação manual - Código PDF: 518	2025-08-21 15:11:20.696108+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
390	SAIDA	24	Associação manual - Código PDF: 734	2025-08-21 15:12:01.825899+00	884	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
391	ENTRADA	24	\N	2025-08-21 15:12:43.684289+00	884	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
392	SAIDA	3	P J REFEICOES COLETIVAS LTDA	2025-08-21 15:18:56.968172+00	993	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
393	SAIDA	50	Associação manual - Código PDF: 835	2025-08-21 15:21:15.737941+00	886	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
394	ENTRADA	50	\N	2025-08-21 16:03:15.24574+00	886	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
395	SAIDA	7	troca - mega	2025-08-21 17:13:09.316973+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
396	ENTRADA	132	\N	2025-08-21 18:48:28.797666+00	787	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
397	ENTRADA	106	\N	2025-08-21 18:49:06.420454+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
398	SAIDA	4	EXPRESSO - NF 1128	2025-08-22 17:48:57.776766+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
399	SAIDA	2	EXPRESSO - NF 1128	2025-08-22 17:49:12.92258+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
400	SAIDA	2	EXPRESSO - NF 1128	2025-08-22 17:49:36.45514+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
401	SAIDA	8	Importação automática - NF: 0000004544	2025-08-22 18:34:39.64203+00	1007	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
402	SAIDA	50	Importação automática - NF: 0000004544	2025-08-22 18:34:39.64203+00	886	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
403	SAIDA	10	Importação automática - NF: 0000004544	2025-08-22 18:34:39.64203+00	889	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
404	ENTRADA	8	\N	2025-08-22 18:35:35.989526+00	1007	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
405	ENTRADA	50	\N	2025-08-22 18:36:07.606113+00	886	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
406	ENTRADA	5	\N	2025-08-22 18:39:31.898519+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
407	SAIDA	12	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
408	SAIDA	30	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	926	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
409	SAIDA	20	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
410	SAIDA	30	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
411	SAIDA	1	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
412	SAIDA	1	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
413	SAIDA	1	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
414	SAIDA	1	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	909	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
415	SAIDA	10	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
416	SAIDA	2	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	827	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
417	SAIDA	4	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
418	SAIDA	5	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	868	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
419	SAIDA	2	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
420	SAIDA	1	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	906	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
421	SAIDA	8	Importação automática - NF: 0000004545	2025-08-25 13:32:11.786465+00	976	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
422	SAIDA	10	alley 4545	2025-08-25 13:33:17.09889+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
423	SAIDA	10	alley 4545	2025-08-25 13:33:50.957336+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
424	SAIDA	18	\N	2025-08-25 13:34:11.173128+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
425	SAIDA	6	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
426	SAIDA	15	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	926	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
427	SAIDA	10	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
428	SAIDA	3	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	868	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
429	SAIDA	1	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
430	SAIDA	1	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
431	SAIDA	8	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
432	SAIDA	8	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
433	SAIDA	6	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
434	SAIDA	4	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	976	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
435	SAIDA	10	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	850	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
436	SAIDA	10	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
437	SAIDA	20	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
438	SAIDA	20	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	787	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
439	SAIDA	1	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	827	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
440	SAIDA	2	Importação automática - NF: 0000004546	2025-08-25 13:37:57.444772+00	1045	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
441	SAIDA	5	alley 4546	2025-08-25 13:38:26.736242+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
442	SAIDA	12	4546	2025-08-25 13:38:46.606006+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
443	SAIDA	6	4546	2025-08-25 13:39:04.768461+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
444	ENTRADA	6	125367	2025-08-26 14:18:14.045632+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
445	SAIDA	3	Importação automática - NF: 0000004547	2025-08-26 19:18:54.250695+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
446	SAIDA	2	Importação automática - NF: 0000004547	2025-08-26 19:18:54.250695+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
447	SAIDA	3	Importação automática - NF: 0000004547	2025-08-26 19:18:54.250695+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
448	SAIDA	2	Importação automática - NF: 0000004548	2025-08-26 19:19:47.657241+00	796	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
449	SAIDA	2	Importação automática - NF: 0000004548	2025-08-26 19:19:47.657241+00	793	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
450	SAIDA	3	Importação automática - NF: 0000004548	2025-08-26 19:19:47.657241+00	863	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
451	SAIDA	1	Importação automática - NF: 0000004549	2025-08-26 19:20:28.784727+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
452	SAIDA	1	Importação automática - NF: 0000004549	2025-08-26 19:20:28.784727+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
453	SAIDA	2	Importação automática - NF: 0000001130	2025-08-26 19:29:52.636586+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
454	SAIDA	2	Importação automática - NF: 0000001130	2025-08-26 19:29:52.636586+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
455	SAIDA	4	Importação automática - NF: 0000001130	2025-08-26 19:29:52.636586+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
456	SAIDA	1	Importação automática - NF: 0000001130	2025-08-26 19:29:52.636586+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
457	SAIDA	2	1130	2025-08-26 19:30:12.600273+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
458	ENTRADA	3	\N	2025-08-26 19:31:02.709939+00	1063	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
459	SAIDA	66	\N	2025-08-27 17:47:00.449905+00	850	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
460	SAIDA	12	Importação automática - NF: 0000001129	2025-08-27 19:19:12.390448+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
461	SAIDA	2	Importação automática - NF: 0000001129	2025-08-27 19:19:12.390448+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
462	SAIDA	3	Importação automática - NF: 0000001129	2025-08-27 19:19:12.390448+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
463	SAIDA	3	Importação automática - NF: 0000001129	2025-08-27 19:19:12.390448+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
464	SAIDA	2	Importação automática - NF: 0000001129	2025-08-27 19:19:12.390448+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
465	SAIDA	2	1129	2025-08-27 19:20:03.693087+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
466	SAIDA	12	1129	2025-08-27 19:20:26.201617+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
467	SAIDA	5	Importação automática - NF: 0000001132	2025-08-27 19:21:39.298914+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
468	SAIDA	1	Importação automática - NF: 0000001132	2025-08-27 19:21:39.298914+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
469	SAIDA	5	Importação automática - NF: 0000001132	2025-08-27 19:21:39.298914+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
470	SAIDA	4	Importação automática - NF: 0000001132	2025-08-27 19:21:39.298914+00	951	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
471	SAIDA	6	Importação automática - NF: 0000001132	2025-08-27 19:21:39.298914+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
472	SAIDA	15	Importação automática - NF: 0000001131	2025-08-27 19:23:32.090218+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
473	SAIDA	10	Importação automática - NF: 0000001131	2025-08-27 19:23:32.090218+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
474	SAIDA	20	Importação automática - NF: 0000001131	2025-08-27 19:23:32.090218+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
475	SAIDA	2	Importação automática - NF: 0000001131	2025-08-27 19:23:32.090218+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
476	SAIDA	20	Importação automática - NF: 0000001131	2025-08-27 19:23:32.090218+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
477	SAIDA	15	Importação automática - NF: 0000001131	2025-08-27 19:23:32.090218+00	877	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
478	SAIDA	5	Importação automática - NF: 0000001131	2025-08-27 19:23:32.090218+00	957	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
479	SAIDA	5	Importação automática - NF: 0000001131	2025-08-27 19:23:32.090218+00	798	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
480	SAIDA	5	Importação automática - NF: 0000001131	2025-08-27 19:23:32.090218+00	797	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
481	SAIDA	10	1131	2025-08-27 19:24:04.673505+00	878	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
482	SAIDA	10	1131	2025-08-27 19:24:18.518327+00	880	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
483	SAIDA	10	1131	2025-08-27 19:24:31.540503+00	879	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1224	SAIDA	16	Importação automática - NF: 0000001184	2025-10-07 14:06:42.044883+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
485	SAIDA	2	Importação automática - NF: 0000004550	2025-08-27 19:26:19.329713+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
486	SAIDA	3	Importação automática - NF: 0000004550	2025-08-27 19:26:19.329713+00	922	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
487	SAIDA	2	4550	2025-08-27 19:27:29.757902+00	992	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
488	SAIDA	2	Importação automática - NF: 0000001135	2025-08-27 19:28:09.73365+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
489	SAIDA	2	Importação automática - NF: 0000001135	2025-08-27 19:28:09.73365+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
490	SAIDA	1	Importação automática - NF: 0000001135	2025-08-27 19:28:09.73365+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
491	SAIDA	4	Importação automática - NF: 0000001133	2025-08-27 19:28:58.804876+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
492	SAIDA	2	Importação automática - NF: 0000001133	2025-08-27 19:28:58.804876+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
493	SAIDA	12	\N	2025-08-27 19:29:19.830579+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
495	SAIDA	2	Importação automática - NF: 0000001137	2025-08-27 19:30:08.578722+00	866	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
496	SAIDA	20	Importação automática - NF: 0000004551	2025-08-27 19:30:44.678959+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
497	SAIDA	8	Importação automática - NF: 0000004551	2025-08-27 19:30:44.678959+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
498	SAIDA	2	Importação automática - NF: 0000004553	2025-08-27 19:31:24.134566+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
499	SAIDA	1	Importação automática - NF: 0000004553	2025-08-27 19:31:24.134566+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
500	SAIDA	1	Importação automática - NF: 0000004553	2025-08-27 19:31:24.134566+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
501	SAIDA	5	Importação automática - NF: 0000004553	2025-08-27 19:31:24.134566+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
514	ENTRADA	5	125429	2025-08-27 19:35:06.362158+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
517	ENTRADA	24	125429	2025-08-27 19:37:58.603342+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
519	ENTRADA	6	125429	2025-08-27 19:38:24.290864+00	853	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
521	ENTRADA	8	125429	2025-08-27 19:39:09.967451+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
522	ENTRADA	28	125429	2025-08-27 19:40:24.76646+00	919	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
524	ENTRADA	4	125429	2025-08-27 19:41:15.635553+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
526	ENTRADA	8	125429	2025-08-27 19:41:57.112019+00	1013	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
528	ENTRADA	4	\N	2025-08-27 19:42:21.773717+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
530	ENTRADA	8	\N	2025-08-27 19:42:42.859275+00	813	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
532	ENTRADA	20	\N	2025-08-27 19:48:43.590678+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
534	ENTRADA	10	\N	2025-08-27 19:49:07.085424+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
536	ENTRADA	20	\N	2025-08-27 19:49:31.556632+00	989	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
538	ENTRADA	10	\N	2025-08-27 19:49:59.28424+00	1003	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
539	SAIDA	1	ajustando estoque	2025-08-28 11:19:09.935618+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
540	SAIDA	2	marista	2025-08-28 11:21:25.95626+00	957	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
541	SAIDA	1	\N	2025-08-28 11:40:18.508385+00	1031	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
542	SAIDA	4	ajuste	2025-08-28 11:50:05.872243+00	1010	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
544	SAIDA	1	ajuste	2025-08-28 11:50:49.350764+00	1014	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
546	ENTRADA	4	\N	2025-08-28 11:55:07.915921+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
547	SAIDA	21	ajuste	2025-08-28 11:56:26.60332+00	860	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
548	SAIDA	2	AJUSTE	2025-08-28 17:39:35.738745+00	999	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
550	SAIDA	30	4555	2025-08-28 18:54:31.690121+00	931	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
552	SAIDA	12	\N	2025-08-28 18:56:51.887108+00	884	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
556	SAIDA	10	ERRO	2025-08-28 18:58:42.863097+00	880	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1225	SAIDA	16	Importação automática - NF: 0000001184	2025-10-07 14:06:42.044883+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1226	SAIDA	8	Importação automática - NF: 0000001184	2025-10-07 14:06:42.044883+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1227	SAIDA	3	Importação automática - NF: 0000004642	2025-10-07 14:09:34.044927+00	790	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1228	SAIDA	36	Importação automática - NF: 0000004642	2025-10-07 14:09:34.044927+00	787	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1229	SAIDA	30	Importação automática - NF: 0000004642	2025-10-07 14:09:34.044927+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1230	SAIDA	15	Importação automática - NF: 0000004642	2025-10-07 14:09:34.044927+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1231	SAIDA	35	\N	2025-10-07 14:09:51.213977+00	1040	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1263	SAIDA	3	Importação automática - NF: 0000004646	2025-10-08 14:13:10.284068+00	1038	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1264	SAIDA	3	Importação automática - NF: 0000004646	2025-10-08 14:13:10.284068+00	809	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1265	SAIDA	20	Importação automática - NF: 0000004646	2025-10-08 14:13:10.284068+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1266	SAIDA	60	Importação automática - NF: 0000004646	2025-10-08 14:13:10.284068+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1267	SAIDA	2	Importação automática - NF: 0000004646	2025-10-08 14:13:10.284068+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1268	SAIDA	8	Importação automática - NF: 0000004646	2025-10-08 14:13:10.284068+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1269	SAIDA	3	Importação automática - NF: 0000004646	2025-10-08 14:13:10.284068+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1449	SAIDA	5	\N	2025-10-22 13:07:59.969729+00	808	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1454	SAIDA	1	\N	2025-10-22 13:12:42.05326+00	929	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1501	ENTRADA	27	\N	2025-10-24 12:35:54.343756+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1505	ENTRADA	32	\N	2025-10-24 12:37:02.790196+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1510	ENTRADA	52	\N	2025-10-24 12:37:55.695884+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1515	ENTRADA	32	\N	2025-10-24 12:40:34.480926+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1555	ENTRADA	20	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1556	ENTRADA	1	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1557	ENTRADA	3	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1558	ENTRADA	23	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1559	ENTRADA	29	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1560	ENTRADA	24	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1561	ENTRADA	6	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1562	ENTRADA	58	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1563	ENTRADA	4	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	856	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1564	ENTRADA	60	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1565	ENTRADA	4	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	908	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1566	ENTRADA	1	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1567	ENTRADA	15	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1568	ENTRADA	20	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1569	ENTRADA	28	Importação automática - NF: 0	2025-10-28 13:30:20.765076+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1571	ENTRADA	8	\N	2025-10-28 13:30:45.807103+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1573	SAIDA	1	\N	2025-10-28 13:31:10.9228+00	1008	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1575	ENTRADA	4	\N	2025-10-28 13:31:47.488561+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1577	ENTRADA	8	\N	2025-10-28 14:48:51.634468+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1579	ENTRADA	24	\N	2025-10-28 14:49:28.89816+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1581	ENTRADA	20	\N	2025-10-28 14:49:48.995153+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1583	ENTRADA	2	\N	2025-10-28 19:22:36.183933+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1587	ENTRADA	4	\N	2025-10-29 17:16:59.518655+00	928	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1590	ENTRADA	100	\N	2025-10-29 17:27:50.14938+00	1041	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1592	ENTRADA	100	\N	2025-10-29 17:28:22.509785+00	889	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
494	SAIDA	2	Importação automática - NF: 0000004552	2025-08-27 19:29:44.256336+00	815	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
502	ENTRADA	19	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
503	ENTRADA	21	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
504	ENTRADA	40	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
505	ENTRADA	57	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
506	ENTRADA	6	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
507	ENTRADA	57	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
508	ENTRADA	94	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
509	ENTRADA	26	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
510	ENTRADA	1	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	962	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
511	ENTRADA	1	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	965	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
512	ENTRADA	20	Importação automática - NF: 6	2025-08-27 19:33:29.418374+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
513	ENTRADA	6	125429	2025-08-27 19:34:51.650578+00	1023	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
515	ENTRADA	20	125429	2025-08-27 19:35:34.14029+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
516	ENTRADA	24	125429	2025-08-27 19:37:38.104126+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
518	ENTRADA	24	125429	2025-08-27 19:38:05.253881+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
520	ENTRADA	8	125429\navaria e devendo (24)	2025-08-27 19:38:54.306167+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
523	ENTRADA	4	125429	2025-08-27 19:40:38.093243+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
525	ENTRADA	8	\N	2025-08-27 19:41:31.91947+00	1012	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
527	ENTRADA	4	125429	2025-08-27 19:42:08.548241+00	1014	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
529	ENTRADA	9	125429	2025-08-27 19:42:31.896521+00	840	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
531	ENTRADA	17	\N	2025-08-27 19:48:30.557895+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
533	ENTRADA	20	\N	2025-08-27 19:48:55.705487+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
535	ENTRADA	10	\N	2025-08-27 19:49:19.230753+00	997	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
537	ENTRADA	20	\N	2025-08-27 19:49:43.791992+00	985	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
543	SAIDA	4	ajuste	2025-08-28 11:50:25.253902+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
545	ENTRADA	4	ajuste	2025-08-28 11:51:05.528232+00	1019	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
549	SAIDA	3	4555	2025-08-28 18:54:09.004145+00	937	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
551	SAIDA	2	NOTA P J	2025-08-28 18:56:33.322823+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
553	SAIDA	12	P J	2025-08-28 18:57:05.665016+00	879	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
554	SAIDA	2	12 - P J	2025-08-28 18:57:34.747191+00	880	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
555	ENTRADA	12	ERRADA	2025-08-28 18:57:57.67836+00	880	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
557	ENTRADA	48	asl - 920	2025-08-28 19:14:26.70119+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
558	ENTRADA	108	asl - 920	2025-08-28 19:14:52.428696+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
559	ENTRADA	60	asl - 920	2025-08-28 19:15:07.325978+00	976	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
560	ENTRADA	240	joselandia	2025-08-28 19:15:43.156838+00	850	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
561	ENTRADA	4	\N	2025-08-28 19:15:57.874273+00	1046	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
562	SAIDA	4	\N	2025-08-28 19:18:23.882889+00	1046	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
563	ENTRADA	48	\N	2025-08-28 19:18:38.123571+00	1046	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
564	SAIDA	8	1136	2025-08-28 19:31:43.117871+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
565	ENTRADA	300	9493	2025-08-29 13:39:50.783639+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
566	SAIDA	2	pré venda	2025-09-01 17:25:33.855151+00	1021	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
567	SAIDA	1	pré venda	2025-09-01 17:25:48.087937+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
568	SAIDA	1	pré venda	2025-09-01 17:25:58.941224+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
569	SAIDA	5	pré venda	2025-09-01 17:26:19.270547+00	848	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
570	SAIDA	30	4558	2025-09-01 17:28:19.589748+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
571	SAIDA	6	4558	2025-09-01 17:29:07.786415+00	933	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
572	SAIDA	12	4558	2025-09-01 17:31:10.320518+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
573	SAIDA	3	4558	2025-09-01 17:31:28.930779+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
574	SAIDA	3	Importação automática - NF: 0000004539	2025-09-01 19:51:01.005364+00	993	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
575	ENTRADA	3	corrigindo importação teste	2025-09-01 19:51:32.270247+00	993	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
576	SAIDA	4	Importação automática - NF: 0000004564	2025-09-02 12:02:11.367759+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
577	SAIDA	3	Importação automática - NF: 0000004564	2025-09-02 12:02:11.367759+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
578	SAIDA	3	Importação automática - NF: 0000004564	2025-09-02 12:02:11.367759+00	853	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
579	SAIDA	1	Importação automática - NF: 0000004564	2025-09-02 12:02:11.367759+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
580	SAIDA	25	Importação automática - NF: 0000004564	2025-09-02 12:02:11.367759+00	817	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
581	SAIDA	3	Importação automática - NF: 0000004564	2025-09-02 12:02:11.367759+00	983	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
582	SAIDA	1	Importação automática - NF: 0000004564	2025-09-02 12:02:11.367759+00	946	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
583	SAIDA	5	Importação automática - NF: 0000004564	2025-09-02 12:02:11.367759+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
584	SAIDA	1	Importação automática - NF: 0000004564	2025-09-02 12:02:11.367759+00	804	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2910	ENTRADA	20	\N	2026-01-21 18:34:39.351103+00	1094	3	\N	0	20	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
585	SAIDA	3	Importação automática - NF: 0000004563	2025-09-02 12:04:12.524918+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
586	SAIDA	6	Importação automática - NF: 0000004563	2025-09-02 12:04:12.524918+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
587	SAIDA	1	Importação automática - NF: 0000004563	2025-09-02 12:04:12.524918+00	960	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
588	SAIDA	1	Importação automática - NF: 0000004563	2025-09-02 12:04:12.524918+00	1014	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
589	SAIDA	6	Importação automática - NF: 0000004563	2025-09-02 12:04:12.524918+00	801	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
590	SAIDA	8	Importação automática - NF: 0000004563	2025-09-02 12:04:12.524918+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
591	SAIDA	1	Importação automática - NF: 0000004563	2025-09-02 12:04:12.524918+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
592	SAIDA	80	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
593	SAIDA	1	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
594	SAIDA	2	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	984	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
595	SAIDA	14	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
596	SAIDA	17	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
597	SAIDA	7	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	976	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
598	SAIDA	5	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
599	SAIDA	75	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	817	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
600	SAIDA	11	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
601	SAIDA	1	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
602	SAIDA	5	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
603	SAIDA	1	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	837	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
604	SAIDA	4	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	892	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
605	SAIDA	2	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	890	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
606	SAIDA	6	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	853	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
607	SAIDA	8	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
608	SAIDA	1	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	835	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
609	SAIDA	10	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	802	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
610	SAIDA	7	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
611	SAIDA	1	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	947	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
612	SAIDA	2	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	1045	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
613	SAIDA	1	Importação automática - NF: 0000004562	2025-09-02 12:09:36.529944+00	904	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
614	SAIDA	3	Importação automática - NF: 0000004558	2025-09-02 12:10:51.65088+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
615	SAIDA	1	Importação automática - NF: 0000004558	2025-09-02 12:10:51.65088+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
616	SAIDA	3	Importação automática - NF: 0000004558	2025-09-02 12:10:51.65088+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
617	SAIDA	3	Importação automática - NF: 0000004558	2025-09-02 12:10:51.65088+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
618	SAIDA	4	Importação automática - NF: 0000004558	2025-09-02 12:10:51.65088+00	802	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
885	SAIDA	5	1159	2025-09-12 19:46:43.627344+00	1067	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
619	SAIDA	2	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
620	SAIDA	2	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
621	SAIDA	1	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
622	SAIDA	10	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	807	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
623	SAIDA	10	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	850	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
624	SAIDA	5	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
625	SAIDA	3	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
626	SAIDA	36	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
627	SAIDA	4	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
628	SAIDA	3	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
629	SAIDA	1	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
630	SAIDA	3	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	921	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
631	SAIDA	2	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	902	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
632	SAIDA	27	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
633	SAIDA	2	Importação automática - NF: 0000004554	2025-09-02 12:20:07.67357+00	806	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
645	ENTRADA	16	AJUSTE	2025-09-02 12:30:29.466726+00	1065	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
647	SAIDA	1	AJUSTE	2025-09-02 12:36:47.99185+00	947	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
649	SAIDA	4	AJUSTE	2025-09-02 12:37:39.634987+00	1010	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
650	SAIDA	8	AJUSTE	2025-09-02 12:47:33.859461+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
652	SAIDA	4	AJUSTE	2025-09-02 12:48:19.555894+00	1012	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
655	SAIDA	6	\N	2025-09-02 12:52:50.170599+00	903	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
657	SAIDA	9	\N	2025-09-02 14:53:33.678307+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
658	SAIDA	80	\N	2025-09-02 17:39:14.986905+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
661	SAIDA	10	Importação automática - NF: 0000001139	2025-09-02 19:49:50.109729+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
662	SAIDA	6	Importação automática - NF: 0000001139	2025-09-02 19:49:50.109729+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
663	SAIDA	5	Importação automática - NF: 0000001139	2025-09-02 19:49:50.109729+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
664	SAIDA	5	Importação automática - NF: 0000001139	2025-09-02 19:49:50.109729+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
669	ENTRADA	3	\N	2025-09-02 20:01:47.875484+00	937	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
670	SAIDA	3	4569	2025-09-03 13:41:50.789091+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
671	SAIDA	7	4569	2025-09-03 13:42:02.249849+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
672	SAIDA	7	4569	2025-09-03 13:42:15.536673+00	1008	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
680	SAIDA	5	Importação automática - NF: 0000004539	2025-09-04 11:54:45.630177+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
681	ENTRADA	5	corrigindo teste	2025-09-04 11:55:15.539705+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1271	SAIDA	2	Importação automática - NF: 0000001186	2025-10-08 14:14:37.413093+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1272	SAIDA	2	Importação automática - NF: 0000001186	2025-10-08 14:14:37.413093+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1273	SAIDA	1	Importação automática - NF: 0000001186	2025-10-08 14:14:37.413093+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1274	SAIDA	1	Importação automática - NF: 0000001186	2025-10-08 14:14:37.413093+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1276	ENTRADA	4	\N	2025-10-08 18:28:22.729944+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1278	ENTRADA	14	\N	2025-10-08 18:28:47.828549+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1280	SAIDA	69	\N	2025-10-09 14:21:13.576583+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1282	ENTRADA	240	\N	2025-10-09 14:22:00.566835+00	868	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1284	ENTRADA	36	\N	2025-10-09 14:22:36.743187+00	868	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1286	SAIDA	12	\N	2025-10-09 14:23:15.208261+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1288	SAIDA	15	\N	2025-10-09 14:44:57.202229+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1290	SAIDA	2	\N	2025-10-09 19:06:34.222822+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1308	SAIDA	13	\N	2025-10-09 19:13:56.396763+00	823	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1310	ENTRADA	2	\N	2025-10-10 13:32:33.256803+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1312	SAIDA	2	\N	2025-10-10 13:34:57.769412+00	963	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1314	SAIDA	1	\N	2025-10-10 13:38:55.472671+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1316	SAIDA	2	\N	2025-10-10 13:39:56.645791+00	1018	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1318	SAIDA	2	\N	2025-10-10 13:41:42.880853+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1320	ENTRADA	7	\N	2025-10-10 13:44:39.036424+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1322	SAIDA	1	\N	2025-10-10 13:46:16.968333+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1324	SAIDA	1	\N	2025-10-10 14:14:50.664195+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1326	SAIDA	4	\N	2025-10-10 14:15:14.754161+00	949	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1328	SAIDA	1	\N	2025-10-10 14:15:59.035444+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1329	SAIDA	30	Importação automática - NF: 0000001191	2025-10-13 12:28:12.294912+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1330	SAIDA	20	Importação automática - NF: 0000001191	2025-10-13 12:28:12.294912+00	926	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1331	SAIDA	10	Importação automática - NF: 0000001191	2025-10-13 12:28:12.294912+00	881	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1332	SAIDA	10	Importação automática - NF: 0000001191	2025-10-13 12:28:12.294912+00	837	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1333	SAIDA	2	Importação automática - NF: 0000004651	2025-10-13 12:33:08.184456+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1334	SAIDA	2	Importação automática - NF: 0000004651	2025-10-13 12:33:08.184456+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1335	SAIDA	2	Importação automática - NF: 0000004651	2025-10-13 12:33:08.184456+00	1046	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1336	SAIDA	10	Importação automática - NF: 0000004651	2025-10-13 12:33:08.184456+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1337	SAIDA	18	Importação automática - NF: 0000004649	2025-10-13 12:40:24.128472+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1338	SAIDA	2	Importação automática - NF: 0000004649	2025-10-13 12:40:24.128472+00	929	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1339	SAIDA	6	Importação automática - NF: 0000004649	2025-10-13 12:40:24.128472+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1340	SAIDA	1	Importação automática - NF: 0000004649	2025-10-13 12:40:24.128472+00	791	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1341	SAIDA	10	Importação automática - NF: 0000004650	2025-10-13 12:42:17.806005+00	1068	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1342	SAIDA	25	Importação automática - NF: 0000004650	2025-10-13 12:42:17.806005+00	818	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1343	SAIDA	1	Importação automática - NF: 0000004650	2025-10-13 12:42:17.806005+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1344	SAIDA	1	Importação automática - NF: 0000004650	2025-10-13 12:42:17.806005+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1345	SAIDA	4	Importação automática - NF: 0000004650	2025-10-13 12:42:17.806005+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1346	SAIDA	1	Importação automática - NF: 0000004650	2025-10-13 12:42:17.806005+00	1042	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1347	SAIDA	3	Importação automática - NF: 0000004650	2025-10-13 12:42:17.806005+00	934	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1348	SAIDA	2	Importação automática - NF: 0000004650	2025-10-13 12:42:17.806005+00	877	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1350	SAIDA	5	\N	2025-10-13 15:14:03.449445+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1450	SAIDA	5	\N	2025-10-22 13:08:22.382903+00	1039	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1455	SAIDA	1	\N	2025-10-22 13:13:05.316417+00	931	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1468	SAIDA	2	\N	2025-10-22 13:32:23.094214+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1484	SAIDA	6	Importação automática - NF: 0000004665	2025-10-22 13:41:50.354377+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1485	SAIDA	4	Importação automática - NF: 0000004665	2025-10-22 13:41:50.354377+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1502	ENTRADA	24	\N	2025-10-24 12:35:59.100672+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1506	ENTRADA	24	\N	2025-10-24 12:37:09.963779+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1511	ENTRADA	4	\N	2025-10-24 12:38:08.276962+00	903	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1516	ENTRADA	8	\N	2025-10-24 12:40:46.918807+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1593	ENTRADA	1	teste (1 a mais)	2025-10-30 03:46:21.260514+00	837	1	\N	19	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1595	SAIDA	1	THIAGO	2025-10-30 11:28:22.719731+00	824	3	\N	203	202	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1597	SAIDA	19	16 - pendência Elo\n3 - avaria	2025-10-30 14:01:42.283488+00	1025	3	\N	131	112	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1598	SAIDA	1	Importação automática - NF: 0000001209	2025-10-30 16:59:22.733818+00	866	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
634	SAIDA	2	Importação automática - NF: 0000004557	2025-09-02 12:22:20.02293+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
635	SAIDA	12	Importação automática - NF: 0000004557	2025-09-02 12:22:20.02293+00	884	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
636	SAIDA	12	Importação automática - NF: 0000001138	2025-09-02 12:23:28.232272+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
637	SAIDA	12	Importação automática - NF: 0000001138	2025-09-02 12:23:28.232272+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
638	SAIDA	20	Importação automática - NF: 0000001138	2025-09-02 12:23:28.232272+00	919	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
639	SAIDA	6	Importação automática - NF: 0000001138	2025-09-02 12:23:28.232272+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
640	SAIDA	16	Importação automática - NF: 0000001140	2025-09-02 12:24:22.164585+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
641	SAIDA	16	Importação automática - NF: 0000001140	2025-09-02 12:24:22.164585+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
642	SAIDA	16	Importação automática - NF: 0000001140	2025-09-02 12:24:22.164585+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
643	SAIDA	16	Importação automática - NF: 0000001140	2025-09-02 12:24:22.164585+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
644	SAIDA	6	4562	2025-09-02 12:27:07.97354+00	850	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
646	SAIDA	1	\N	2025-09-02 12:30:44.046922+00	801	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
648	SAIDA	1	AJUSTE	2025-09-02 12:37:03.868256+00	949	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
651	SAIDA	4	AJUSTE	2025-09-02 12:47:54.178034+00	1013	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
653	SAIDA	1	\N	2025-09-02 12:51:16.43986+00	999	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
654	SAIDA	6	\N	2025-09-02 12:52:35.038874+00	904	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
656	SAIDA	8	\N	2025-09-02 14:50:35.96995+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
659	SAIDA	10	\N	2025-09-02 17:39:20.732952+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
660	SAIDA	8	\N	2025-09-02 19:18:44.850461+00	978	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
665	SAIDA	16	Importação automática - NF: 0000001141	2025-09-02 19:50:32.297104+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
666	SAIDA	15	Importação automática - NF: 0000001141	2025-09-02 19:50:32.297104+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
667	SAIDA	15	Importação automática - NF: 0000001141	2025-09-02 19:50:32.297104+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
668	SAIDA	3	Importação automática - NF: 0000004555	2025-09-02 20:01:06.780228+00	937	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
673	SAIDA	50	4567	2025-09-03 18:56:03.800875+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
674	SAIDA	15	4567	2025-09-03 18:56:23.199455+00	889	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
675	SAIDA	8	4565	2025-09-03 19:10:38.639606+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
676	SAIDA	5	1145	2025-09-03 19:11:02.533439+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
677	SAIDA	3	4566	2025-09-03 19:12:32.761827+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
678	SAIDA	2	4566	2025-09-03 19:12:44.857832+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
679	SAIDA	3	4566	2025-09-03 19:12:55.959441+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
682	SAIDA	1	Importação automática - NF: 0000001151	2025-09-04 14:17:49.337104+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
683	SAIDA	3	Importação automática - NF: 0000001151	2025-09-04 14:17:49.337104+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
684	SAIDA	1	Importação automática - NF: 0000001151	2025-09-04 14:17:49.337104+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2759	SAIDA	1	Importação automática - NF: 0000004810 | Produto NF: PAPEL HIG. CAI CAI C/9000FLS 20X10 CM F. DUPLA	2026-01-09 14:13:24.884838+00	929	3	VENDA	10	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
686	SAIDA	2	Importação automática - NF: 0000004560	2025-09-04 14:18:42.34021+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
687	SAIDA	5	Importação automática - NF: 0000004560	2025-09-04 14:18:42.34021+00	997	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
688	SAIDA	2	Importação automática - NF: 0000004560	2025-09-04 14:18:42.34021+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
690	ENTRADA	16	\N	2025-09-04 14:23:09.862395+00	1066	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
691	SAIDA	1	Importação automática - NF: 0000004561	2025-09-04 14:32:34.291877+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
692	SAIDA	5	Importação automática - NF: 0000004561	2025-09-04 14:32:34.291877+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
693	SAIDA	3	Importação automática - NF: 0000004561	2025-09-04 14:32:34.291877+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
694	SAIDA	1	Importação automática - NF: 0000004561	2025-09-04 14:32:34.291877+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
695	SAIDA	1	Importação automática - NF: 0000004561	2025-09-04 14:32:34.291877+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
696	SAIDA	1	Importação automática - NF: 0000004561	2025-09-04 14:32:34.291877+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
697	SAIDA	5	Importação automática - NF: 0000004561	2025-09-04 14:32:34.291877+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
698	SAIDA	4	Importação automática - NF: 0000001144	2025-09-04 14:33:02.22527+00	963	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
699	SAIDA	40	Importação automática - NF: 0000001147	2025-09-04 14:34:06.956676+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
700	SAIDA	40	Importação automática - NF: 0000001147	2025-09-04 14:34:06.956676+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
701	SAIDA	20	Importação automática - NF: 0000001147	2025-09-04 14:34:06.956676+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
702	SAIDA	1	Importação automática - NF: 0000001147	2025-09-04 14:34:06.956676+00	1022	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
703	SAIDA	20	1147	2025-09-04 14:35:32.408941+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
704	SAIDA	80	Importação automática - NF: 0000001146	2025-09-04 14:36:09.318236+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
705	SAIDA	40	Importação automática - NF: 0000001146	2025-09-04 14:36:09.318236+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
706	SAIDA	40	Importação automática - NF: 0000001146	2025-09-04 14:36:09.318236+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
707	SAIDA	3	\N	2025-09-04 14:37:16.24539+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
708	ENTRADA	20	\N	2025-09-04 18:30:17.757024+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
709	ENTRADA	10	\N	2025-09-04 18:30:51.14081+00	999	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
710	ENTRADA	7	\N	2025-09-04 19:43:32.370167+00	895	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
711	ENTRADA	12	\N	2025-09-04 19:43:48.002265+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
712	SAIDA	20	Importação automática - NF: 0000004571	2025-09-05 11:29:51.271454+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
713	SAIDA	1	Importação automática - NF: 0000004571	2025-09-05 11:29:51.271454+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
714	SAIDA	40	Importação automática - NF: 0000004571	2025-09-05 11:29:51.271454+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
715	SAIDA	1	Importação automática - NF: 0000004571	2025-09-05 11:29:51.271454+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
716	SAIDA	1	Importação automática - NF: 0000004571	2025-09-05 11:29:51.271454+00	997	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
717	SAIDA	1	Importação automática - NF: 0000004571	2025-09-05 11:29:51.271454+00	985	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
718	SAIDA	2	Importação automática - NF: 0000004571	2025-09-05 11:29:51.271454+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
719	SAIDA	2	Importação automática - NF: 0000004571	2025-09-05 11:29:51.271454+00	989	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
720	SAIDA	2	Importação automática - NF: 0000001150	2025-09-05 11:31:40.489736+00	952	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
721	SAIDA	2	Importação automática - NF: 0000001150	2025-09-05 11:31:40.489736+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
722	SAIDA	1	Importação automática - NF: 0000001150	2025-09-05 11:31:40.489736+00	905	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
723	SAIDA	1	Importação automática - NF: 0000001150	2025-09-05 11:31:40.489736+00	908	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
724	SAIDA	1	Importação automática - NF: 0000001150	2025-09-05 11:31:40.489736+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
725	SAIDA	1	Importação automática - NF: 0000001150	2025-09-05 11:31:40.489736+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
726	SAIDA	1	Importação automática - NF: 0000001150	2025-09-05 11:31:40.489736+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
727	SAIDA	3	1150	2025-09-05 11:32:03.059339+00	856	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
728	SAIDA	3	Importação automática - NF: 0000001149	2025-09-05 11:32:31.590763+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
729	SAIDA	1	Importação automática - NF: 0000001148	2025-09-05 11:32:54.815765+00	908	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
730	ENTRADA	2	\N	2025-09-05 11:52:03.82603+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
731	ENTRADA	2	\N	2025-09-05 18:02:07.317274+00	929	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
732	ENTRADA	102	\N	2025-09-05 18:02:22.982473+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
733	ENTRADA	100	\N	2025-09-05 18:03:13.297489+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
734	ENTRADA	24	\N	2025-09-05 18:07:37.133042+00	1040	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
735	ENTRADA	40	\N	2025-09-05 18:08:24.215585+00	931	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
736	ENTRADA	14	\N	2025-09-05 18:08:42.300174+00	957	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
737	ENTRADA	18	\N	2025-09-05 18:09:01.181421+00	835	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
738	SAIDA	2	\N	2025-09-05 18:09:12.771931+00	834	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
739	SAIDA	1	\N	2025-09-09 17:17:47.00629+00	881	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
740	ENTRADA	1	\N	2025-09-09 17:17:51.981871+00	881	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
741	SAIDA	1	\N	2025-09-09 17:17:55.596096+00	882	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
742	ENTRADA	12	\N	2025-09-09 17:18:24.150014+00	1040	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
743	SAIDA	6	Importação automática - NF: 0000004577	2025-09-09 19:24:33.032821+00	1065	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
744	SAIDA	6	Importação automática - NF: 0000004577	2025-09-09 19:24:33.032821+00	902	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
745	SAIDA	2	Importação automática - NF: 0000004577	2025-09-09 19:24:33.032821+00	978	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
746	SAIDA	2	Importação automática - NF: 0000001153	2025-09-09 19:25:08.033566+00	866	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
887	ENTRADA	25	\N	2025-09-16 17:49:31.632611+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
747	SAIDA	18	Importação automática - NF: 0000004581	2025-09-09 19:26:08.671981+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
748	SAIDA	1	Importação automática - NF: 0000004581	2025-09-09 19:26:08.671981+00	929	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
749	SAIDA	2	Importação automática - NF: 0000004581	2025-09-09 19:26:08.671981+00	858	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
750	SAIDA	2	Importação automática - NF: 0000004579	2025-09-09 19:27:39.288559+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
751	SAIDA	2	Importação automática - NF: 0000004579	2025-09-09 19:27:39.288559+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
752	SAIDA	2	Importação automática - NF: 0000004579	2025-09-09 19:27:39.288559+00	813	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
753	SAIDA	1	Importação automática - NF: 0000004579	2025-09-09 19:27:39.288559+00	1021	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
754	SAIDA	4	4579	2025-09-09 19:27:56.305034+00	1066	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
756	SAIDA	1	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	1017	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
757	SAIDA	1	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	860	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
758	SAIDA	1	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
759	SAIDA	2	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	895	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
760	SAIDA	3	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
761	SAIDA	4	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	988	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
762	SAIDA	3	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	928	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
763	SAIDA	3	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	1041	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
764	SAIDA	2	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	1017	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
765	SAIDA	2	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	928	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
766	SAIDA	3	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
767	SAIDA	6	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
768	SAIDA	3	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
769	SAIDA	2	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
770	SAIDA	1	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
771	SAIDA	8	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	989	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
772	SAIDA	1	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	985	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
773	SAIDA	30	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
774	SAIDA	10	Importação automática - NF: 0000004570	2025-09-09 19:39:21.497168+00	902	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
775	SAIDA	1	4570	2025-09-09 19:39:49.607132+00	856	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
777	SAIDA	3	4570	2025-09-09 19:40:44.019931+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
788	SAIDA	4	Importação automática - NF: 0000004572	2025-09-10 14:45:22.149399+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
789	SAIDA	3	Importação automática - NF: 0000004572	2025-09-10 14:45:22.149399+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
790	SAIDA	12	Importação automática - NF: 0000004572	2025-09-10 14:45:22.149399+00	881	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
791	SAIDA	1	Importação automática - NF: 0000004575	2025-09-10 14:45:50.079099+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
792	SAIDA	6	Importação automática - NF: 0000004575	2025-09-10 14:45:50.079099+00	1065	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
793	SAIDA	1	4574	2025-09-10 14:46:15.651137+00	978	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
796	SAIDA	4	\N	2025-09-10 14:47:40.678319+00	1065	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
798	SAIDA	4	\N	2025-09-10 14:49:22.348659+00	997	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
811	SAIDA	2	Importação automática - NF: 0000001156	2025-09-10 14:52:46.052333+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
812	SAIDA	2	Importação automática - NF: 0000001156	2025-09-10 14:52:46.052333+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
813	SAIDA	1	Importação automática - NF: 0000001156	2025-09-10 14:52:46.052333+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
814	SAIDA	2	Importação automática - NF: 0000004583	2025-09-10 14:53:23.904539+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2760	SAIDA	7	Importação automática - NF: 0000004810 | Produto NF: S P A LA C S O T P IC / LIXO 60X70X0,025 - PRETO 60LT BETA	2026-01-09 14:13:24.884838+00	1002	3	VENDA	53	46	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
816	SAIDA	3	\N	2025-09-10 14:53:44.840332+00	1066	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
817	ENTRADA	9	\N	2025-09-10 14:59:12.978287+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1275	ENTRADA	4	\N	2025-10-08 18:28:12.365924+00	997	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1277	SAIDA	11	\N	2025-10-08 18:28:33.750905+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1279	ENTRADA	8	\N	2025-10-08 18:29:39.141857+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1281	ENTRADA	237	\N	2025-10-09 14:21:19.596916+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1283	SAIDA	240	\N	2025-10-09 14:22:25.384038+00	868	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1285	ENTRADA	230	\N	2025-10-09 14:23:03.01856+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1287	SAIDA	1	\N	2025-10-09 14:42:16.296076+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1289	SAIDA	4	\N	2025-10-09 19:06:20.558999+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1291	SAIDA	4	\N	2025-10-09 19:06:52.337092+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1293	SAIDA	6	\N	2025-10-09 19:07:51.086147+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1294	SAIDA	2	Importação automática - NF: 0000001189	2025-10-09 19:09:49.292299+00	905	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1295	SAIDA	1	Importação automática - NF: 0000001189	2025-10-09 19:09:49.292299+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1296	SAIDA	1	Importação automática - NF: 0000001189	2025-10-09 19:09:49.292299+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1297	SAIDA	3	Importação automática - NF: 0000001189	2025-10-09 19:09:49.292299+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1298	SAIDA	2	Importação automática - NF: 0000001189	2025-10-09 19:09:49.292299+00	952	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1299	SAIDA	2	Importação automática - NF: 0000001188	2025-10-09 19:10:38.113258+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1300	SAIDA	1	Importação automática - NF: 0000001188	2025-10-09 19:10:38.113258+00	952	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1301	SAIDA	4	Importação automática - NF: 0000001190	2025-10-09 19:12:27.763939+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1302	SAIDA	4	Importação automática - NF: 0000001190	2025-10-09 19:12:27.763939+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1303	SAIDA	6	Importação automática - NF: 0000001190	2025-10-09 19:12:27.763939+00	934	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1304	SAIDA	2	Importação automática - NF: 0000001190	2025-10-09 19:12:27.763939+00	800	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1305	SAIDA	8	Importação automática - NF: 0000001190	2025-10-09 19:12:27.763939+00	943	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1306	SAIDA	10	Importação automática - NF: 0000001190	2025-10-09 19:12:27.763939+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1307	SAIDA	3	\N	2025-10-09 19:12:41.553598+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1309	SAIDA	7	\N	2025-10-09 19:14:06.869391+00	825	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1311	SAIDA	3	\N	2025-10-10 13:32:52.024284+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1313	SAIDA	3	\N	2025-10-10 13:35:10.370131+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1315	SAIDA	1	\N	2025-10-10 13:39:33.769014+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1317	SAIDA	4	\N	2025-10-10 13:40:45.54637+00	903	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1319	SAIDA	8	\N	2025-10-10 13:42:01.514756+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1321	ENTRADA	1	\N	2025-10-10 13:45:37.735086+00	859	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1323	SAIDA	3	\N	2025-10-10 14:14:30.659079+00	856	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1325	SAIDA	1	\N	2025-10-10 14:14:54.701767+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1327	SAIDA	1	\N	2025-10-10 14:15:31.897029+00	951	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1349	ENTRADA	3	\N	2025-10-13 15:13:21.651554+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1451	SAIDA	10	\N	2025-10-22 13:10:03.265103+00	846	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1456	SAIDA	2	\N	2025-10-22 13:13:28.233884+00	1068	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1487	ENTRADA	1	\N	2025-10-23 11:56:18.772302+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1488	SAIDA	2	Importação automática - NF: 0000004666	2025-10-23 11:59:31.314383+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1496	SAIDA	4	\N	2025-10-23 12:13:01.368906+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1503	ENTRADA	20	\N	2025-10-24 12:36:20.481462+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1507	ENTRADA	32	\N	2025-10-24 12:37:27.444628+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1512	SAIDA	3	\N	2025-10-24 12:40:04.426158+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1517	ENTRADA	6	\N	2025-10-24 12:41:04.063317+00	1026	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1594	SAIDA	1	teste (normalizando)	2025-10-30 03:47:27.627798+00	837	1	\N	20	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1596	SAIDA	1	THIAGO	2025-10-30 11:28:41.359923+00	870	3	\N	16	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
755	SAIDA	8	Importação automática - NF: 0000001152	2025-09-09 19:28:48.319114+00	860	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
776	SAIDA	2	4570	2025-09-09 19:40:11.284338+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
778	ENTRADA	50	\N	2025-09-09 19:42:42.653888+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
779	SAIDA	1	Importação automática - NF: 0000004573	2025-09-10 14:44:15.172879+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
780	SAIDA	1	Importação automática - NF: 0000004573	2025-09-10 14:44:15.172879+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
781	SAIDA	1	Importação automática - NF: 0000004573	2025-09-10 14:44:15.172879+00	951	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
782	SAIDA	5	Importação automática - NF: 0000004573	2025-09-10 14:44:15.172879+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
783	SAIDA	2	Importação automática - NF: 0000004573	2025-09-10 14:44:15.172879+00	879	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
784	SAIDA	1	Importação automática - NF: 0000004573	2025-09-10 14:44:15.172879+00	928	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
785	SAIDA	6	Importação automática - NF: 0000004573	2025-09-10 14:44:15.172879+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
786	SAIDA	2	Importação automática - NF: 0000004573	2025-09-10 14:44:15.172879+00	934	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
787	SAIDA	2	4573	2025-09-10 14:44:33.419148+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
794	SAIDA	3	4574	2025-09-10 14:46:32.163244+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
795	SAIDA	20	\N	2025-09-10 14:47:04.193085+00	1041	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
797	SAIDA	4	4576	2025-09-10 14:48:04.457986+00	978	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
799	SAIDA	2	\N	2025-09-10 14:49:33.909063+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
800	SAIDA	3	Importação automática - NF: 0000001154	2025-09-10 14:50:13.538896+00	789	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
801	SAIDA	1	Importação automática - NF: 0000001154	2025-09-10 14:50:13.538896+00	911	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
802	SAIDA	1	Importação automática - NF: 0000004582	2025-09-10 14:50:45.356355+00	929	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
803	SAIDA	1	Importação automática - NF: 0000004582	2025-09-10 14:50:45.356355+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
804	SAIDA	3	Importação automática - NF: 0000001155	2025-09-10 14:51:57.50098+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
805	SAIDA	3	Importação automática - NF: 0000001155	2025-09-10 14:51:57.50098+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
806	SAIDA	2	Importação automática - NF: 0000001155	2025-09-10 14:51:57.50098+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
807	SAIDA	1	Importação automática - NF: 0000001155	2025-09-10 14:51:57.50098+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
808	SAIDA	1	Importação automática - NF: 0000001155	2025-09-10 14:51:57.50098+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
809	SAIDA	4	Importação automática - NF: 0000001155	2025-09-10 14:51:57.50098+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
810	SAIDA	1	\N	2025-09-10 14:52:10.232224+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
818	SAIDA	6	\N	2025-09-10 18:19:14.02654+00	793	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
819	SAIDA	1	\N	2025-09-10 18:19:24.213359+00	863	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
820	SAIDA	40	Importação automática - NF: 0000004595	2025-09-11 18:11:00.028014+00	897	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
821	SAIDA	40	Importação automática - NF: 0000004595	2025-09-11 18:11:00.028014+00	1040	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
822	SAIDA	2	Importação automática - NF: 0000004595	2025-09-11 18:11:00.028014+00	790	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
823	SAIDA	24	Importação automática - NF: 0000004595	2025-09-11 18:11:00.028014+00	787	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
824	SAIDA	5	Importação automática - NF: 0000004595	2025-09-11 18:11:00.028014+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
825	SAIDA	2	4595	2025-09-11 18:11:54.970982+00	856	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
826	SAIDA	2	\N	2025-09-11 18:12:09.977642+00	910	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
827	SAIDA	20	Importação automática - NF: 0000004584	2025-09-11 18:13:16.914097+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
828	SAIDA	20	Importação automática - NF: 0000004584	2025-09-11 18:13:16.914097+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
829	SAIDA	20	Importação automática - NF: 0000004584	2025-09-11 18:13:16.914097+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
830	SAIDA	1	1157	2025-09-11 18:14:38.050834+00	856	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
831	SAIDA	5	Importação automática - NF: 0000001158	2025-09-11 18:18:58.510914+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
832	SAIDA	2	Importação automática - NF: 0000001158	2025-09-11 18:18:58.510914+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
833	SAIDA	2	Importação automática - NF: 0000001158	2025-09-11 18:18:58.510914+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
834	SAIDA	2	Importação automática - NF: 0000001158	2025-09-11 18:18:58.510914+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
835	SAIDA	2	Importação automática - NF: 0000001158	2025-09-11 18:18:58.510914+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
836	SAIDA	2	Importação automática - NF: 0000001158	2025-09-11 18:18:58.510914+00	909	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
837	SAIDA	1	1158	2025-09-11 18:19:30.375647+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
838	SAIDA	8	4590	2025-09-11 18:19:46.042954+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
839	SAIDA	6	Importação automática - NF: 0000004588	2025-09-11 19:47:43.314854+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
840	SAIDA	6	Importação automática - NF: 0000004588	2025-09-11 19:47:43.314854+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
841	SAIDA	30	\N	2025-09-11 19:48:01.517101+00	844	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
842	SAIDA	2	Importação automática - NF: 0000004589	2025-09-11 19:49:27.162659+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
843	SAIDA	2	Importação automática - NF: 0000004589	2025-09-11 19:49:27.162659+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
844	SAIDA	1	Importação automática - NF: 0000004589	2025-09-11 19:49:27.162659+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
845	SAIDA	1	Importação automática - NF: 0000004589	2025-09-11 19:49:27.162659+00	1012	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
846	SAIDA	1	Importação automática - NF: 0000004589	2025-09-11 19:49:27.162659+00	931	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
847	SAIDA	10	Importação automática - NF: 0000004589	2025-09-11 19:49:27.162659+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
848	SAIDA	2	Importação automática - NF: 0000004594	2025-09-11 19:50:29.543675+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
849	SAIDA	1	Importação automática - NF: 0000004594	2025-09-11 19:50:29.543675+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
850	SAIDA	1	Importação automática - NF: 0000004594	2025-09-11 19:50:29.543675+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
851	SAIDA	2	Importação automática - NF: 0000004594	2025-09-11 19:50:29.543675+00	1013	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
852	SAIDA	5	Importação automática - NF: 0000004594	2025-09-11 19:50:29.543675+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
853	ENTRADA	8	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
854	ENTRADA	4	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
855	ENTRADA	4	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
856	ENTRADA	1	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
857	ENTRADA	4	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
858	ENTRADA	18	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
859	ENTRADA	16	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
860	ENTRADA	8	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
861	ENTRADA	4	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	863	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
862	ENTRADA	1	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
863	ENTRADA	7	Importação automática - NF: 0	2025-09-12 11:26:56.862279+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
864	ENTRADA	8	\N	2025-09-12 11:36:43.026976+00	1067	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
865	ENTRADA	4	\N	2025-09-12 12:27:32.556933+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
866	ENTRADA	4	\N	2025-09-12 12:27:45.797134+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
867	SAIDA	2	Importação automática - NF: 0000004592	2025-09-12 17:40:46.668922+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
868	SAIDA	2	Importação automática - NF: 0000004592	2025-09-12 17:40:46.668922+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
869	SAIDA	2	Importação automática - NF: 0000004592	2025-09-12 17:40:46.668922+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
870	SAIDA	2	Importação automática - NF: 0000004592	2025-09-12 17:40:46.668922+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
871	SAIDA	1	Importação automática - NF: 0000004592	2025-09-12 17:40:46.668922+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
872	ENTRADA	75	\N	2025-09-12 19:43:31.390874+00	818	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
873	ENTRADA	150	\N	2025-09-12 19:43:38.561042+00	817	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
874	SAIDA	2	Importação automática - NF: 0000004596	2025-09-12 19:44:05.901322+00	978	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
875	SAIDA	12	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
876	SAIDA	30	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	941	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
877	SAIDA	3	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
878	SAIDA	2	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	839	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
879	SAIDA	2	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	1046	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
880	SAIDA	1	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	976	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
881	SAIDA	1	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
882	SAIDA	2	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
883	SAIDA	3	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	802	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
884	SAIDA	3	Importação automática - NF: 0000004597	2025-09-12 19:45:59.182984+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
886	ENTRADA	200	\N	2025-09-16 17:49:16.503388+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
888	ENTRADA	10	\N	2025-09-16 17:49:40.550491+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
889	SAIDA	3	Importação automática - NF: 0000004599	2025-09-16 18:18:30.592076+00	796	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
890	SAIDA	3	Importação automática - NF: 0000004599	2025-09-16 18:18:30.592076+00	863	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
892	SAIDA	2	Importação automática - NF: 0000004604	2025-09-16 18:23:06.120746+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
893	SAIDA	2	Importação automática - NF: 0000004604	2025-09-16 18:23:06.120746+00	983	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
894	SAIDA	1	Importação automática - NF: 0000004604	2025-09-16 18:23:06.120746+00	988	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
895	SAIDA	1	Importação automática - NF: 0000004604	2025-09-16 18:23:06.120746+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
896	SAIDA	1	Importação automática - NF: 0000004604	2025-09-16 18:23:06.120746+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
897	SAIDA	1	Importação automática - NF: 0000004604	2025-09-16 18:23:06.120746+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
898	SAIDA	5	Importação automática - NF: 0000004604	2025-09-16 18:23:06.120746+00	880	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
899	SAIDA	50	Importação automática - NF: 0000004604	2025-09-16 18:23:06.120746+00	817	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
900	SAIDA	2	Importação automática - NF: 0000004604	2025-09-16 18:23:06.120746+00	819	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
902	SAIDA	15	\N	2025-09-16 18:23:56.864174+00	842	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
904	SAIDA	2	\N	2025-09-16 18:24:38.137877+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
908	SAIDA	3	Importação automática - NF: 0000004610	2025-09-17 18:05:10.754042+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
916	SAIDA	1	Importação automática - NF: 0000004606	2025-09-17 18:09:17.721776+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
917	SAIDA	5	Importação automática - NF: 0000004606	2025-09-17 18:09:17.721776+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
918	SAIDA	3	Importação automática - NF: 0000004606	2025-09-17 18:09:17.721776+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
919	SAIDA	1	Importação automática - NF: 0000004606	2025-09-17 18:09:17.721776+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2911	SAIDA	43	\N	2026-01-21 18:34:49.632552+00	941	3	\N	143	100	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
921	SAIDA	1	Importação automática - NF: 0000004606	2025-09-17 18:09:17.721776+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
922	SAIDA	1	Importação automática - NF: 0000004606	2025-09-17 18:09:17.721776+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
923	SAIDA	5	Importação automática - NF: 0000004606	2025-09-17 18:09:17.721776+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
924	SAIDA	1	Importação automática - NF: 0000004606	2025-09-17 18:09:17.721776+00	811	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
925	SAIDA	1	\N	2025-09-17 18:09:32.825449+00	1066	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
927	SAIDA	6	\N	2025-09-17 18:10:03.640399+00	840	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
931	SAIDA	2	Importação automática - NF: 0000004609	2025-09-17 18:11:40.805256+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
932	SAIDA	5	Importação automática - NF: 0000004609	2025-09-17 18:11:40.805256+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2761	SAIDA	6	Importação automática - NF: 0000004810 | Produto NF: S P A LA C S O T P IC / LIXO 55X55X0,25 - PRETO 40LT BETA	2026-01-09 14:13:24.884838+00	1001	3	VENDA	35	29	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
934	SAIDA	6	\N	2025-09-17 18:11:58.003952+00	1066	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
936	SAIDA	30	\N	2025-09-17 18:12:25.017403+00	889	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
938	SAIDA	1	\N	2025-09-17 18:43:20.513219+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
940	SAIDA	1	\N	2025-09-17 18:43:39.097294+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
943	ENTRADA	120	\N	2025-09-18 11:18:19.084268+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
944	SAIDA	2	Importação automática - NF: 0000001163	2025-09-18 11:19:48.783872+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
945	SAIDA	2	Importação automática - NF: 0000001163	2025-09-18 11:19:48.783872+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
946	SAIDA	2	Importação automática - NF: 0000001163	2025-09-18 11:19:48.783872+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
947	SAIDA	1	Importação automática - NF: 0000001163	2025-09-18 11:19:48.783872+00	859	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
948	SAIDA	1	Importação automática - NF: 0000001163	2025-09-18 11:19:48.783872+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
949	SAIDA	1	Importação automática - NF: 0000001163	2025-09-18 11:19:48.783872+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1351	ENTRADA	36	\N	2025-10-15 13:48:15.932141+00	895	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1353	SAIDA	35	\N	2025-10-15 13:48:49.071846+00	934	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1355	SAIDA	1	\N	2025-10-15 13:49:18.507966+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1357	SAIDA	2	\N	2025-10-15 13:49:56.8765+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1359	SAIDA	2	\N	2025-10-15 13:50:26.644522+00	988	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1361	SAIDA	1	\N	2025-10-15 13:50:52.673952+00	985	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1364	SAIDA	1	\N	2025-10-15 13:55:40.922776+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1366	SAIDA	1	\N	2025-10-15 13:56:08.679814+00	989	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1368	SAIDA	1	\N	2025-10-15 13:56:46.823754+00	928	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1370	SAIDA	1	\N	2025-10-15 13:58:30.429102+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1372	SAIDA	2	\N	2025-10-15 13:58:51.830096+00	988	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1373	SAIDA	3	\N	2025-10-15 14:00:51.70728+00	989	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1377	SAIDA	20	Importação automática - NF: 0000004657	2025-10-15 19:16:32.600513+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1378	SAIDA	20	Importação automática - NF: 0000004657	2025-10-15 19:16:32.600513+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1379	SAIDA	8	Importação automática - NF: 0000004657	2025-10-15 19:16:32.600513+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1380	SAIDA	4	Importação automática - NF: 0000004657	2025-10-15 19:16:32.600513+00	1010	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1381	SAIDA	4	Importação automática - NF: 0000004657	2025-10-15 19:16:32.600513+00	1011	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1382	SAIDA	4	Importação automática - NF: 0000004657	2025-10-15 19:16:32.600513+00	1013	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1383	SAIDA	12	\N	2025-10-15 19:16:48.236932+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1384	SAIDA	2	Importação automática - NF: 0000004655	2025-10-15 19:28:25.747141+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1385	SAIDA	4	Importação automática - NF: 0000004655	2025-10-15 19:28:25.747141+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1386	SAIDA	5	Importação automática - NF: 0000004655	2025-10-15 19:28:25.747141+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1387	SAIDA	3	Importação automática - NF: 0000004655	2025-10-15 19:28:25.747141+00	992	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1388	SAIDA	4	Importação automática - NF: 0000001197	2025-10-15 19:32:32.105059+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1389	SAIDA	2	Importação automática - NF: 0000001197	2025-10-15 19:32:32.105059+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1390	SAIDA	1	Importação automática - NF: 0000001197	2025-10-15 19:32:32.105059+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1391	SAIDA	1	Importação automática - NF: 0000001197	2025-10-15 19:32:32.105059+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1392	SAIDA	2	Importação automática - NF: 0000001197	2025-10-15 19:32:32.105059+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1393	SAIDA	1	Importação automática - NF: 0000001197	2025-10-15 19:32:32.105059+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1394	SAIDA	1	Importação automática - NF: 0000001197	2025-10-15 19:32:32.105059+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1395	SAIDA	1	Importação automática - NF: 0000001197	2025-10-15 19:32:32.105059+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1405	SAIDA	2	Importação automática - NF: 0000001195	2025-10-15 19:35:42.68398+00	917	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1406	SAIDA	3	Importação automática - NF: 0000001195	2025-10-15 19:35:42.68398+00	795	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1407	SAIDA	1	Importação automática - NF: 0000001195	2025-10-15 19:35:42.68398+00	866	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1409	ENTRADA	200	\N	2025-10-16 13:01:27.123375+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1411	SAIDA	3	\N	2025-10-16 13:14:22.787444+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1413	ENTRADA	20	\N	2025-10-16 13:15:00.638862+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1415	ENTRADA	70	\N	2025-10-16 13:15:23.895741+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1417	ENTRADA	30	\N	2025-10-16 13:15:55.87207+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1430	SAIDA	3	Importação automática - NF: 0000004658	2025-10-17 13:22:10.605378+00	796	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1431	SAIDA	2	Importação automática - NF: 0000004658	2025-10-17 13:22:10.605378+00	793	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1432	SAIDA	2	Importação automática - NF: 0000004658	2025-10-17 13:22:10.605378+00	863	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1444	SAIDA	2	\N	2025-10-17 13:28:19.989031+00	907	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1453	SAIDA	2	\N	2025-10-22 13:12:20.667751+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1458	SAIDA	2	\N	2025-10-22 13:13:54.99483+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1469	SAIDA	55	Importação automática - NF: 0000004664	2025-10-22 13:37:20.766392+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1470	SAIDA	2	Importação automática - NF: 0000004664	2025-10-22 13:37:20.766392+00	938	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1471	SAIDA	5	Importação automática - NF: 0000004664	2025-10-22 13:37:20.766392+00	996	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
891	SAIDA	2	\N	2025-09-16 18:18:47.924999+00	793	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
901	SAIDA	4	\N	2025-09-16 18:23:39.248432+00	939	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
903	SAIDA	48	\N	2025-09-16 18:24:11.150461+00	819	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
905	SAIDA	4	Importação automática - NF: 0000004611	2025-09-17 18:04:43.417546+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
906	SAIDA	3	Importação automática - NF: 0000004611	2025-09-17 18:04:43.417546+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
907	SAIDA	4	Importação automática - NF: 0000004611	2025-09-17 18:04:43.417546+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
909	SAIDA	12	Importação automática - NF: 0000001160	2025-09-17 18:07:42.915939+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
910	SAIDA	1	Importação automática - NF: 0000001160	2025-09-17 18:07:42.915939+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
911	SAIDA	16	Importação automática - NF: 0000001160	2025-09-17 18:07:42.915939+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
912	SAIDA	8	Importação automática - NF: 0000001160	2025-09-17 18:07:42.915939+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
913	SAIDA	3	Importação automática - NF: 0000001160	2025-09-17 18:07:42.915939+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
914	SAIDA	2	Importação automática - NF: 0000001160	2025-09-17 18:07:42.915939+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
915	SAIDA	5	Importação automática - NF: 0000001160	2025-09-17 18:07:42.915939+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
926	SAIDA	2	\N	2025-09-17 18:09:47.126203+00	861	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
928	SAIDA	3	Importação automática - NF: 0000004608	2025-09-17 18:10:50.160057+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
929	SAIDA	1	Importação automática - NF: 0000004608	2025-09-17 18:10:50.160057+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
930	SAIDA	1	Importação automática - NF: 0000004608	2025-09-17 18:10:50.160057+00	1021	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
935	SAIDA	80	\N	2025-09-17 18:12:17.206028+00	886	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
937	SAIDA	1	\N	2025-09-17 18:43:14.013164+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
939	SAIDA	1	\N	2025-09-17 18:43:30.583567+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
941	SAIDA	1	\N	2025-09-17 18:43:45.589722+00	796	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
942	ENTRADA	48	\N	2025-09-18 11:15:44.453849+00	787	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
950	SAIDA	4	Importação automática - NF: 0000001164	2025-09-19 12:12:51.626532+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
951	SAIDA	2	Importação automática - NF: 0000001164	2025-09-19 12:12:51.626532+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
952	SAIDA	2	Importação automática - NF: 0000001164	2025-09-19 12:12:51.626532+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
953	SAIDA	1	Importação automática - NF: 0000001164	2025-09-19 12:12:51.626532+00	1021	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
954	SAIDA	1	Importação automática - NF: 0000001164	2025-09-19 12:12:51.626532+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
955	SAIDA	7	Importação automática - NF: 0000001165	2025-09-19 12:13:14.880379+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
956	SAIDA	8	Importação automática - NF: 0000001165	2025-09-19 12:13:14.880379+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
957	SAIDA	8	Importação automática - NF: 0000001166	2025-09-19 12:18:00.653397+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
958	SAIDA	8	Importação automática - NF: 0000001166	2025-09-19 12:18:00.653397+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
959	SAIDA	1	\N	2025-09-19 12:59:19.710239+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
960	SAIDA	8	\N	2025-09-19 13:01:35.286945+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
961	ENTRADA	3	\N	2025-09-19 13:01:53.004943+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
962	SAIDA	13	\N	2025-09-19 13:02:09.06787+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
963	ENTRADA	57	\N	2025-09-19 13:02:40.541963+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
964	SAIDA	9	\N	2025-09-19 13:05:42.306742+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
965	ENTRADA	1	\N	2025-09-19 13:05:55.504186+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
966	SAIDA	4	\N	2025-09-19 13:08:10.934211+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
967	ENTRADA	8	\N	2025-09-19 13:08:25.359871+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
968	ENTRADA	3	\N	2025-09-19 13:08:53.370512+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
969	ENTRADA	7	\N	2025-09-19 13:09:13.094657+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
970	ENTRADA	1	\N	2025-09-19 13:09:31.868657+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
971	SAIDA	3	\N	2025-09-19 13:09:49.490579+00	1031	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
972	SAIDA	1	\N	2025-09-19 13:10:03.062865+00	1032	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
973	ENTRADA	3	\N	2025-09-19 13:10:23.25787+00	978	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
974	SAIDA	2	\N	2025-09-19 13:10:47.384423+00	815	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
975	ENTRADA	2	\N	2025-09-19 13:11:17.278293+00	813	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
976	SAIDA	4	\N	2025-09-19 13:11:39.94261+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
977	SAIDA	1	\N	2025-09-19 13:12:25.263872+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
978	SAIDA	2	\N	2025-09-19 13:12:36.498174+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
979	ENTRADA	4	\N	2025-09-19 13:14:53.735953+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
980	ENTRADA	2	\N	2025-09-19 13:15:11.324187+00	1017	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
981	ENTRADA	2	\N	2025-09-19 13:15:33.608824+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
982	ENTRADA	10	\N	2025-09-19 17:25:32.319859+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
983	ENTRADA	4	\N	2025-09-19 17:25:46.781852+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
984	ENTRADA	3	\N	2025-09-19 17:25:57.833065+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
985	ENTRADA	10	\N	2025-09-19 17:26:12.154346+00	989	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
986	SAIDA	1	Importação automática - NF: 0000004612	2025-09-19 19:37:14.987689+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
987	SAIDA	25	Importação automática - NF: 0000004612	2025-09-19 19:37:14.987689+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
988	SAIDA	1	Importação automática - NF: 0000004612	2025-09-19 19:37:14.987689+00	1010	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
989	SAIDA	10	Importação automática - NF: 0000004612	2025-09-19 19:37:14.987689+00	1003	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
990	SAIDA	1	Importação automática - NF: 0000004612	2025-09-19 19:37:14.987689+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
991	SAIDA	4	Importação automática - NF: 0000004612	2025-09-19 19:37:14.987689+00	934	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
992	ENTRADA	34	\N	2025-09-19 19:38:04.970327+00	934	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
993	ENTRADA	40	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
994	ENTRADA	32	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
995	ENTRADA	108	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
996	ENTRADA	12	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
997	ENTRADA	120	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
998	ENTRADA	5	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
999	ENTRADA	2	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1000	ENTRADA	1	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1001	ENTRADA	10	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1002	ENTRADA	10	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1003	ENTRADA	1	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1004	ENTRADA	3	Importação automática - NF: 0	2025-09-26 13:09:20.297458+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1005	ENTRADA	4	\N	2025-09-26 13:09:44.879754+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1006	ENTRADA	24	\N	2025-09-26 13:14:21.017744+00	1028	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1007	ENTRADA	12	\N	2025-09-26 13:14:37.303562+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1008	ENTRADA	4	\N	2025-09-26 13:15:11.534046+00	870	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1009	ENTRADA	75	\N	2025-09-26 13:16:22.509398+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1010	ENTRADA	16	\N	2025-09-26 13:16:43.838875+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1011	ENTRADA	16	\N	2025-09-26 13:16:49.149684+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1012	ENTRADA	4	\N	2025-09-26 13:17:07.670087+00	963	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1013	ENTRADA	5	\N	2025-09-26 13:17:28.466963+00	840	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1014	ENTRADA	4	\N	2025-09-26 13:17:41.11576+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1015	ENTRADA	6	\N	2025-09-26 13:18:04.313949+00	909	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1016	ENTRADA	4	\N	2025-09-26 13:18:19.293481+00	866	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1017	ENTRADA	7	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1018	ENTRADA	5	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1019	ENTRADA	1	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1020	ENTRADA	5	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1021	ENTRADA	16	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1022	ENTRADA	4	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1023	ENTRADA	4	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	1036	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1024	ENTRADA	4	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	1048	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1025	ENTRADA	19	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1026	ENTRADA	21	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1027	ENTRADA	32	Importação automática - NF: 6	2025-09-26 13:28:35.068221+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1028	ENTRADA	8	\N	2025-09-26 13:28:48.125887+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1029	ENTRADA	8	\N	2025-09-26 13:29:10.129375+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1030	ENTRADA	16	\N	2025-09-26 13:29:23.372877+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1031	ENTRADA	4	\N	2025-09-26 13:29:39.653504+00	903	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1032	ENTRADA	12	\N	2025-09-26 13:29:51.423474+00	904	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1033	ENTRADA	12	\N	2025-09-26 13:30:04.447881+00	978	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1035	ENTRADA	88	\N	2025-09-26 13:30:36.214838+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1037	ENTRADA	4	\N	2025-09-26 14:28:04.874149+00	1013	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1039	ENTRADA	7	\N	2025-09-26 14:31:34.657651+00	793	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1041	ENTRADA	12	\N	2025-09-26 14:36:14.917596+00	918	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1043	ENTRADA	80	\N	2025-09-29 12:13:02.634945+00	931	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1045	ENTRADA	20	\N	2025-09-29 12:13:38.85279+00	889	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1047	SAIDA	2	4620	2025-09-29 12:40:31.066873+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1049	SAIDA	8	\N	2025-09-29 18:37:36.245611+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1051	SAIDA	6	\N	2025-09-29 18:38:02.56626+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1052	SAIDA	16	\N	2025-09-29 18:39:08.423753+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1054	SAIDA	50	\N	2025-09-29 18:39:38.33955+00	1041	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1056	ENTRADA	7	\N	2025-09-29 18:55:25.068619+00	835	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1058	SAIDA	7	\N	2025-09-29 18:55:44.806737+00	834	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1060	SAIDA	8	\N	2025-09-29 19:10:24.475826+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1061	SAIDA	4	Importação automática - NF: 0000001172	2025-09-29 23:36:17.636885+00	820	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1062	SAIDA	4	Importação automática - NF: 0000001172	2025-09-29 23:36:17.636885+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1063	SAIDA	2	Importação automática - NF: 0000001172	2025-09-29 23:36:17.636885+00	862	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1064	SAIDA	15	Importação automática - NF: 0000001172	2025-09-29 23:36:17.636885+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1065	SAIDA	20	Importação automática - NF: 0000001172	2025-09-29 23:36:17.636885+00	919	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1066	SAIDA	10	Importação automática - NF: 0000001168	2025-09-29 23:42:45.207139+00	896	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1067	SAIDA	3	Importação automática - NF: 0000001168	2025-09-29 23:42:45.207139+00	891	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1068	SAIDA	2	Importação automática - NF: 0000001168	2025-09-29 23:42:45.207139+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1069	SAIDA	2	Importação automática - NF: 0000001168	2025-09-29 23:42:45.207139+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1070	SAIDA	1	Importação automática - NF: 0000001168	2025-09-29 23:42:45.207139+00	820	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1071	SAIDA	1	Importação automática - NF: 0000001168	2025-09-29 23:42:45.207139+00	995	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1072	SAIDA	1	Importação automática - NF: 0000001168	2025-09-29 23:42:45.207139+00	1006	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1076	SAIDA	5	Importação automática - NF: 0000004621	2025-09-29 23:46:07.336961+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1077	SAIDA	5	Importação automática - NF: 0000004621	2025-09-29 23:46:07.336961+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1078	SAIDA	4	Importação automática - NF: 0000004621	2025-09-29 23:46:07.336961+00	792	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1079	SAIDA	2	Importação automática - NF: 0000004619	2025-09-29 23:47:41.170906+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1080	SAIDA	1	Importação automática - NF: 0000004619	2025-09-29 23:47:41.170906+00	1006	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1081	SAIDA	20	Importação automática - NF: 0000004619	2025-09-29 23:47:41.170906+00	848	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1082	SAIDA	1	Importação automática - NF: 0000004619	2025-09-29 23:47:41.170906+00	822	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1084	SAIDA	2	Importação automática - NF: 0000001171	2025-09-29 23:50:35.893479+00	866	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1085	SAIDA	7	Importação automática - NF: 0000001165	2025-09-29 23:52:03.076964+00	918	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1089	SAIDA	1	Importação automática - NF: 0000004614	2025-09-29 23:55:15.718477+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1090	SAIDA	2	Importação automática - NF: 0000004614	2025-09-29 23:55:15.718477+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1091	SAIDA	1	Importação automática - NF: 0000004614	2025-09-29 23:55:15.718477+00	1035	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1092	SAIDA	5	Importação automática - NF: 0000004614	2025-09-29 23:55:15.718477+00	941	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1352	SAIDA	2	\N	2025-10-15 13:48:36.351118+00	928	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2912	ENTRADA	12	NF 6 - Processamento automático	2026-01-21 18:50:54.587922+00	1069	3	\N	0	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1356	SAIDA	3	\N	2025-10-15 13:49:34.256598+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1358	SAIDA	1	\N	2025-10-15 13:50:15.560929+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1360	SAIDA	4	\N	2025-10-15 13:50:39.362479+00	989	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1362	SAIDA	3	\N	2025-10-15 13:51:27.5167+00	1041	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1363	SAIDA	1	\N	2025-10-15 13:55:29.367527+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1365	SAIDA	1	\N	2025-10-15 13:55:55.519428+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1369	SAIDA	3	\N	2025-10-15 13:56:58.928671+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1371	SAIDA	1	\N	2025-10-15 13:58:39.84504+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1376	SAIDA	120	\N	2025-10-15 14:02:51.368381+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1396	SAIDA	2	Importação automática - NF: 0000004654	2025-10-15 19:34:09.409445+00	933	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1397	SAIDA	30	Importação automática - NF: 0000004654	2025-10-15 19:34:09.409445+00	1068	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1398	SAIDA	3	Importação automática - NF: 0000004654	2025-10-15 19:34:09.409445+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1399	SAIDA	3	Importação automática - NF: 0000004654	2025-10-15 19:34:09.409445+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1400	SAIDA	12	Importação automática - NF: 0000004654	2025-10-15 19:34:09.409445+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1401	SAIDA	3	Importação automática - NF: 0000004654	2025-10-15 19:34:09.409445+00	1046	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1402	SAIDA	2	Importação automática - NF: 0000004654	2025-10-15 19:34:09.409445+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1403	SAIDA	5	Importação automática - NF: 0000004653	2025-10-15 19:34:43.459042+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1404	SAIDA	3	Importação automática - NF: 0000004653	2025-10-15 19:34:43.459042+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1408	ENTRADA	12	\N	2025-10-16 12:58:37.36003+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1410	ENTRADA	3	\N	2025-10-16 13:14:12.649974+00	1007	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1412	ENTRADA	10	\N	2025-10-16 13:14:48.335066+00	997	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1414	ENTRADA	40	\N	2025-10-16 13:15:13.071449+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1416	ENTRADA	20	\N	2025-10-16 13:15:34.905325+00	1003	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1418	ENTRADA	10	\N	2025-10-16 13:16:10.285019+00	987	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1419	SAIDA	1	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1420	SAIDA	4	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1421	SAIDA	3	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1422	SAIDA	1	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1423	SAIDA	20	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	936	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1424	SAIDA	1	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	935	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1425	SAIDA	1	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1426	SAIDA	1	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	1033	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1427	SAIDA	3	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	1030	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1428	SAIDA	1	Importação automática - NF: 0000004656	2025-10-17 13:21:20.273828+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1429	SAIDA	4	\N	2025-10-17 13:21:32.616854+00	1025	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1433	SAIDA	2	Importação automática - NF: 0000004659	2025-10-17 13:22:36.954936+00	978	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1434	SAIDA	8	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1435	SAIDA	4	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1436	SAIDA	16	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1437	SAIDA	12	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1438	SAIDA	2	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1439	SAIDA	2	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1440	SAIDA	8	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1441	SAIDA	2	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	1015	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1442	SAIDA	2	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1443	SAIDA	4	Importação automática - NF: 0000001198	2025-10-17 13:26:09.574402+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1472	SAIDA	3	Importação automática - NF: 0000004664	2025-10-22 13:37:20.766392+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1486	ENTRADA	5	\N	2025-10-23 11:56:13.492027+00	932	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1489	SAIDA	2	Importação automática - NF: 0000001202	2025-10-23 12:01:53.238998+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1490	SAIDA	2	Importação automática - NF: 0000001202	2025-10-23 12:01:53.238998+00	820	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1491	SAIDA	2	Importação automática - NF: 0000001202	2025-10-23 12:01:53.238998+00	824	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1492	SAIDA	1	Importação automática - NF: 0000001202	2025-10-23 12:01:53.238998+00	859	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1034	ENTRADA	12	\N	2025-09-26 13:30:19.218903+00	853	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1036	ENTRADA	4	\N	2025-09-26 13:30:55.040566+00	946	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1038	ENTRADA	8	\N	2025-09-26 14:31:19.102302+00	1008	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1040	ENTRADA	12	\N	2025-09-26 14:32:29.850919+00	873	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1042	ENTRADA	24	\N	2025-09-26 14:36:29.632383+00	860	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1044	ENTRADA	216	\N	2025-09-29 12:13:23.174029+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1046	ENTRADA	12	\N	2025-09-29 12:13:54.955507+00	968	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1048	SAIDA	8	\N	2025-09-29 18:37:27.076985+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1050	SAIDA	4	\N	2025-09-29 18:37:49.915307+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1053	SAIDA	5	\N	2025-09-29 18:39:19.76957+00	964	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1055	SAIDA	7	\N	2025-09-29 18:55:14.969206+00	835	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1057	SAIDA	2	\N	2025-09-29 18:55:35.426619+00	835	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1059	SAIDA	8	\N	2025-09-29 19:10:10.362083+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2913	ENTRADA	8	NF 6 - Processamento automático	2026-01-21 18:50:54.59561+00	813	3	\N	4	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1074	SAIDA	5	Importação automática - NF: 0000004615	2025-09-29 23:43:40.740743+00	935	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1075	SAIDA	5	Importação automática - NF: 0000004615	2025-09-29 23:43:40.740743+00	996	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1083	SAIDA	2	Importação automática - NF: 0000001169	2025-09-29 23:49:50.769612+00	860	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1086	SAIDA	5	Importação automática - NF: 0000004617	2025-09-29 23:53:08.815221+00	820	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1087	SAIDA	10	Importação automática - NF: 0000004617	2025-09-29 23:53:08.815221+00	848	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1088	SAIDA	2	Importação automática - NF: 0000004617	2025-09-29 23:53:08.815221+00	1038	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1093	SAIDA	1	Importação automática - NF: 0000004614	2025-09-29 23:56:22.201767+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1095	SAIDA	70	\N	2025-10-06 13:57:20.3472+00	936	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1096	SAIDA	5	\N	2025-10-06 13:58:00.58025+00	935	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1097	SAIDA	2	\N	2025-10-06 13:58:20.905452+00	1062	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1098	SAIDA	2	\N	2025-10-06 13:58:41.154051+00	1038	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1099	SAIDA	4	\N	2025-10-06 13:59:44.103133+00	937	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1100	SAIDA	30	\N	2025-10-06 14:01:16.795024+00	931	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1101	SAIDA	10	\N	2025-10-06 14:01:28.445664+00	807	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1102	SAIDA	48	\N	2025-10-06 14:01:42.784814+00	788	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1103	SAIDA	6	\N	2025-10-06 14:02:49.985569+00	990	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1104	SAIDA	3	\N	2025-10-06 14:03:20.936631+00	999	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1105	SAIDA	12	\N	2025-10-06 14:04:24.443745+00	823	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1106	SAIDA	27	\N	2025-10-06 14:05:10.931675+00	977	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1107	SAIDA	3	\N	2025-10-06 14:07:02.245763+00	1002	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1108	ENTRADA	120	\N	2025-10-06 14:08:12.38624+00	1068	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1109	SAIDA	30	\N	2025-10-06 14:08:51.397477+00	1068	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1110	SAIDA	4	\N	2025-10-06 14:09:17.567236+00	1046	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1111	SAIDA	10	\N	2025-10-06 14:10:45.648017+00	926	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1112	SAIDA	1	\N	2025-10-06 14:12:24.372767+00	799	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1113	SAIDA	1	\N	2025-10-06 14:12:42.052739+00	809	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1114	SAIDA	10	\N	2025-10-06 14:13:02.541786+00	839	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1115	SAIDA	3	\N	2025-10-06 14:13:24.786926+00	996	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1116	SAIDA	2	\N	2025-10-06 14:13:54.486782+00	933	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1117	SAIDA	3	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	1033	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1118	SAIDA	1	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1119	SAIDA	36	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	788	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1120	SAIDA	4	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	990	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1121	SAIDA	3	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	999	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1122	SAIDA	12	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	823	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1123	SAIDA	4	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	1046	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1124	SAIDA	3	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	1016	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1125	SAIDA	1	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	799	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1126	SAIDA	1	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	808	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1127	SAIDA	10	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	839	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1128	SAIDA	3	Importação automática - NF: 0000004626	2025-10-06 14:33:58.379799+00	946	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1129	SAIDA	4	Importação automática - NF: 0000004625	2025-10-06 14:35:07.060347+00	937	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1130	SAIDA	30	Importação automática - NF: 0000004625	2025-10-06 14:35:07.060347+00	931	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1131	SAIDA	4	Importação automática - NF: 0000004637	2025-10-06 14:36:44.267189+00	823	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1132	SAIDA	1	Importação automática - NF: 0000004637	2025-10-06 14:36:44.267189+00	789	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1133	SAIDA	1	Importação automática - NF: 0000004637	2025-10-06 14:36:44.267189+00	951	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1134	SAIDA	1	Importação automática - NF: 0000004637	2025-10-06 14:36:44.267189+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1135	SAIDA	3	Importação automática - NF: 0000004637	2025-10-06 14:36:44.267189+00	977	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1136	SAIDA	2	Importação automática - NF: 0000004637	2025-10-06 14:36:44.267189+00	985	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1137	SAIDA	12	Importação automática - NF: 0000004623	2025-10-06 14:41:21.733138+00	788	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1138	SAIDA	2	Importação automática - NF: 0000004623	2025-10-06 14:41:21.733138+00	933	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1139	SAIDA	1	Importação automática - NF: 0000004623	2025-10-06 14:41:21.733138+00	1062	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1140	SAIDA	4	Importação automática - NF: 0000004623	2025-10-06 14:41:21.733138+00	977	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1141	SAIDA	4	Importação automática - NF: 0000004623	2025-10-06 14:41:21.733138+00	823	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1142	SAIDA	2	Importação automática - NF: 0000004623	2025-10-06 14:41:21.733138+00	990	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1143	SAIDA	3	Importação automática - NF: 0000004623	2025-10-06 14:41:21.733138+00	1002	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1144	SAIDA	3	Importação automática - NF: 0000004623	2025-10-06 14:41:21.733138+00	800	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1145	SAIDA	30	Importação automática - NF: 0000004623	2025-10-06 14:41:21.733138+00	1068	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1146	SAIDA	10	Importação automática - NF: 0000004636	2025-10-06 14:44:29.373129+00	940	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1147	SAIDA	1	Importação automática - NF: 0000004636	2025-10-06 14:44:29.373129+00	1062	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1148	SAIDA	6	Importação automática - NF: 0000004636	2025-10-06 14:44:29.373129+00	925	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1149	SAIDA	2	Importação automática - NF: 0000004636	2025-10-06 14:44:29.373129+00	1002	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1150	SAIDA	2	Importação automática - NF: 0000004636	2025-10-06 14:44:29.373129+00	951	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1151	SAIDA	6	Importação automática - NF: 0000004636	2025-10-06 14:44:29.373129+00	823	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1152	SAIDA	4	Importação automática - NF: 0000004636	2025-10-06 14:44:29.373129+00	802	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1153	SAIDA	2	Importação automática - NF: 0000004636	2025-10-06 14:44:29.373129+00	920	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1154	SAIDA	2	Importação automática - NF: 0000004636	2025-10-06 14:44:29.373129+00	983	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1155	SAIDA	1	Importação automática - NF: 0000004633	2025-10-06 14:48:14.143665+00	820	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1156	SAIDA	5	Importação automática - NF: 0000004633	2025-10-06 14:48:14.143665+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1157	SAIDA	3	Importação automática - NF: 0000004633	2025-10-06 14:48:14.143665+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1158	SAIDA	20	Importação automática - NF: 0000004633	2025-10-06 14:48:14.143665+00	936	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1159	SAIDA	1	Importação automática - NF: 0000004633	2025-10-06 14:48:14.143665+00	935	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1160	SAIDA	1	Importação automática - NF: 0000004633	2025-10-06 14:48:14.143665+00	1062	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1161	SAIDA	1	Importação automática - NF: 0000004633	2025-10-06 14:48:14.143665+00	1033	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1162	SAIDA	5	Importação automática - NF: 0000004633	2025-10-06 14:48:14.143665+00	1030	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1163	SAIDA	2	Importação automática - NF: 0000004633	2025-10-06 14:48:14.143665+00	1006	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1164	SAIDA	6	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	931	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1165	SAIDA	80	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	940	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1166	SAIDA	4	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	1062	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1167	SAIDA	2	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	984	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1168	SAIDA	2	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	991	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1169	SAIDA	1	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	951	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1170	SAIDA	1	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	789	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1171	SAIDA	1	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1172	SAIDA	14	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	839	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1173	SAIDA	100	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	817	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1174	SAIDA	6	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	925	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1175	SAIDA	1	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	1035	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1176	SAIDA	1	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	1045	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1177	SAIDA	1	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	922	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1178	SAIDA	1	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	837	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1179	SAIDA	2	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	892	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1180	SAIDA	2	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	891	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1181	SAIDA	2	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	804	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1182	SAIDA	4	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	853	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1183	SAIDA	1	Importação automática - NF: 0000004635	2025-10-06 14:56:16.081144+00	927	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1184	SAIDA	50	Importação automática - NF: 0000004624	2025-10-06 14:57:25.949886+00	936	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1185	SAIDA	4	Importação automática - NF: 0000004624	2025-10-06 14:57:25.949886+00	935	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1186	SAIDA	3	Importação automática - NF: 0000004624	2025-10-06 14:57:25.949886+00	996	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1188	ENTRADA	150	\N	2025-10-06 18:44:36.823365+00	817	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1190	ENTRADA	4	\N	2025-10-06 18:58:33.426551+00	937	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1192	ENTRADA	10	\N	2025-10-06 19:23:43.753831+00	807	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1194	ENTRADA	6	\N	2025-10-06 19:24:35.98725+00	990	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1196	ENTRADA	12	\N	2025-10-06 19:25:09.169752+00	823	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1204	ENTRADA	3	\N	2025-10-06 19:39:26.237157+00	996	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1205	ENTRADA	2	\N	2025-10-06 19:39:59.728894+00	933	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1209	ENTRADA	2	\N	2025-10-06 19:44:10.126032+00	1038	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1445	SAIDA	10	\N	2025-10-22 13:05:29.240907+00	956	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1493	SAIDA	2	Importação automática - NF: 0000001202	2025-10-23 12:01:53.238998+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1495	SAIDA	3	\N	2025-10-23 12:12:55.385155+00	1068	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1518	SAIDA	50	Importação automática - NF: 0000004672	2025-10-24 17:13:14.131556+00	817	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1519	SAIDA	2	Importação automática - NF: 0000004672	2025-10-24 17:13:14.131556+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1520	SAIDA	2	Importação automática - NF: 0000004672	2025-10-24 17:13:14.131556+00	983	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1521	SAIDA	2	Importação automática - NF: 0000004672	2025-10-24 17:13:14.131556+00	988	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1522	SAIDA	2	Importação automática - NF: 0000004672	2025-10-24 17:13:14.131556+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1523	SAIDA	4	Importação automática - NF: 0000004672	2025-10-24 17:13:14.131556+00	850	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1524	SAIDA	1	Importação automática - NF: 0000004672	2025-10-24 17:13:14.131556+00	902	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1525	SAIDA	20	\N	2025-10-24 17:14:26.787302+00	842	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1526	SAIDA	48	\N	2025-10-24 17:29:01.083396+00	895	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1527	SAIDA	7	Importação automática - NF: 0000004669	2025-10-27 18:04:24.325221+00	1024	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1528	SAIDA	8	Importação automática - NF: 0000004669	2025-10-27 18:04:24.325221+00	966	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1529	SAIDA	8	Importação automática - NF: 0000004669	2025-10-27 18:04:24.325221+00	1008	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1530	SAIDA	6	Importação automática - NF: 0000004669	2025-10-27 18:04:24.325221+00	876	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1532	SAIDA	3	Importação automática - NF: 0000001205	2025-10-27 18:07:33.678406+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1533	SAIDA	1	Importação automática - NF: 0000001205	2025-10-27 18:07:33.678406+00	1006	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1534	SAIDA	5	Importação automática - NF: 0000001205	2025-10-27 18:07:33.678406+00	874	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1544	SAIDA	10	\N	2025-10-27 19:05:44.808575+00	842	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1546	SAIDA	1	\N	2025-10-27 19:07:21.907949+00	985	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1548	SAIDA	2	\N	2025-10-27 19:07:48.53177+00	988	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1550	SAIDA	1	\N	2025-10-27 19:08:08.464259+00	1001	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1552	SAIDA	2	\N	2025-10-27 19:08:34.368506+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1187	ENTRADA	150	\N	2025-10-06 18:44:26.47837+00	819	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1189	ENTRADA	33	\N	2025-10-06 18:49:20.119308+00	931	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1191	ENTRADA	7	\N	2025-10-06 19:23:21.113022+00	895	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1193	ENTRADA	48	\N	2025-10-06 19:24:07.283836+00	788	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1195	ENTRADA	3	\N	2025-10-06 19:24:54.878105+00	999	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1197	ENTRADA	27	\N	2025-10-06 19:26:18.259529+00	977	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1198	ENTRADA	3	\N	2025-10-06 19:26:37.540367+00	1002	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1199	ENTRADA	30	\N	2025-10-06 19:34:04.116871+00	1068	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1200	ENTRADA	4	\N	2025-10-06 19:35:17.537856+00	1046	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1201	ENTRADA	10	\N	2025-10-06 19:36:24.57407+00	926	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1202	ENTRADA	1	\N	2025-10-06 19:37:21.587181+00	799	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1203	ENTRADA	10	\N	2025-10-06 19:38:48.213285+00	839	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1206	ENTRADA	70	\N	2025-10-06 19:41:01.248101+00	936	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1207	ENTRADA	5	\N	2025-10-06 19:43:09.70453+00	935	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1208	ENTRADA	2	\N	2025-10-06 19:43:31.218561+00	1062	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1210	SAIDA	15	Importação automática - NF: 0000004641	2025-10-07 14:00:15.545827+00	925	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1211	SAIDA	75	Importação automática - NF: 0000004641	2025-10-07 14:00:15.545827+00	940	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1212	SAIDA	1	Importação automática - NF: 0000004641	2025-10-07 14:00:15.545827+00	991	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1213	SAIDA	2	Importação automática - NF: 0000004641	2025-10-07 14:00:15.545827+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1214	SAIDA	2	Importação automática - NF: 0000004641	2025-10-07 14:00:15.545827+00	989	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1215	SAIDA	6	Importação automática - NF: 0000004641	2025-10-07 14:00:15.545827+00	802	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1216	SAIDA	1	Importação automática - NF: 0000004641	2025-10-07 14:00:15.545827+00	997	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1217	SAIDA	1	\N	2025-10-07 14:00:34.142722+00	985	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1218	SAIDA	3	Importação automática - NF: 0000004640	2025-10-07 14:02:19.696475+00	937	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1219	SAIDA	8	Importação automática - NF: 0000004640	2025-10-07 14:02:19.696475+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1220	SAIDA	6	Importação automática - NF: 0000004640	2025-10-07 14:02:19.696475+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1446	SAIDA	9	\N	2025-10-22 13:05:51.725392+00	809	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1497	SAIDA	2	\N	2025-10-24 12:26:21.392557+00	822	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1499	ENTRADA	3	\N	2025-10-24 12:32:26.687082+00	860	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1504	ENTRADA	16	\N	2025-10-24 12:36:39.485012+00	792	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1508	ENTRADA	6	\N	2025-10-24 12:37:35.892521+00	853	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1513	SAIDA	2	\N	2025-10-24 12:40:14.346568+00	920	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1531	SAIDA	2	1204	2025-10-27 18:06:24.261077+00	905	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1535	SAIDA	2	Importação automática - NF: 0000004674	2025-10-27 19:05:28.336963+00	933	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1536	SAIDA	6	Importação automática - NF: 0000004674	2025-10-27 19:05:28.336963+00	977	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1537	SAIDA	12	Importação automática - NF: 0000004674	2025-10-27 19:05:28.336963+00	788	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1538	SAIDA	1	Importação automática - NF: 0000004674	2025-10-27 19:05:28.336963+00	1062	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1539	SAIDA	2	Importação automática - NF: 0000004674	2025-10-27 19:05:28.336963+00	990	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1540	SAIDA	3	Importação automática - NF: 0000004674	2025-10-27 19:05:28.336963+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1541	SAIDA	1	Importação automática - NF: 0000004674	2025-10-27 19:05:28.336963+00	1016	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1542	SAIDA	1	Importação automática - NF: 0000004674	2025-10-27 19:05:28.336963+00	1035	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1543	SAIDA	30	\N	2025-10-27 19:05:38.92889+00	842	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1545	SAIDA	2	\N	2025-10-27 19:07:10.126327+00	987	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1547	SAIDA	2	\N	2025-10-27 19:07:34.698156+00	989	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1549	SAIDA	1	\N	2025-10-27 19:07:57.949575+00	993	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1551	SAIDA	2	\N	2025-10-27 19:08:19.422497+00	1002	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1553	SAIDA	1	\N	2025-10-27 19:08:44.684486+00	856	3	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2762	SAIDA	6	Importação automática - NF: 0000004810 | Produto NF: S B A E C TA O P P L / A L S I T X I O C 75X90X0,05 - PRETO 100LT	2026-01-09 14:13:24.884838+00	991	3	VENDA	30	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2763	SAIDA	6	Importação automática - NF: 0000004810 | Produto NF: SACO P/ LIXO INFECTANTE 75X105 100L LEVE	2026-01-09 14:13:24.884838+00	985	3	VENDA	21	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2764	SAIDA	12	Importação automática - NF: 0000004810 | Produto NF: DETERGENTE NEUTRO FC 500ML	2026-01-09 14:13:24.884838+00	823	3	VENDA	114	102	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2765	SAIDA	4	Importação automática - NF: 0000004810 | Produto NF: SABAO EM BARRA YPE 5x160G	2026-01-09 14:13:24.884838+00	976	3	VENDA	56	52	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2766	SAIDA	3	Importação automática - NF: 0000004810 | Produto NF: SABAO EM PO ALA FLOR DE LIS 400G	2026-01-09 14:13:24.884838+00	977	3	VENDA	108	105	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2767	SAIDA	4	Importação automática - NF: 0000004810 | Produto NF: VASSOURA LINDONA	2026-01-09 14:13:24.884838+00	1045	3	VENDA	46	42	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2768	SAIDA	2	Importação automática - NF: 0000004810 | Produto NF: ALCOOL SAFRA 5L	2026-01-09 14:13:24.884838+00	1062	3	VENDA	14	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2769	SAIDA	6	Importação automática - NF: 0000004810 | Produto NF: PANO DE CHAO ALVEJADO FLANELADO 48X68	2026-01-09 14:13:24.884838+00	925	3	VENDA	459	453	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2770	SAIDA	8	Importação automática - NF: 0000004810 | Código sincronizado (PROD017 -> 830) | Produto NF: AROMATIZADOR CHEIRO DE TALCO 360ML	2026-01-09 14:13:24.884838+00	803	3	VENDA	44	36	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD017\\"}"	"{\\"codigo\\": \\"830\\"}"	\N	f	\N	\N
2780	SAIDA	1	Importação automática - NF: 0000001280 | Produto NF: SEC MAQ PRO BB5L	2026-01-09 14:15:09.988397+00	1024	3	VENDA	5	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2781	SAIDA	12	Importação automática - NF: 0000001280 | Código sincronizado (1029355 -> 344) | Produto NF: SABONETE SUAVITEX BAC SP BOL 500ML	2026-01-09 14:15:09.988397+00	1030	3	VENDA	37	25	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1029355\\"}"	"{\\"codigo\\": \\"344\\"}"	\N	f	\N	\N
2794	SAIDA	3	Importação automática - NF: 0000004829 | Código sincronizado (1033005 -> 518) | Produto NF: LIMPAX DX BB5L	2026-01-09 14:16:58.990543+00	874	3	VENDA	165	162	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1033005\\"}"	"{\\"codigo\\": \\"518\\"}"	\N	f	\N	\N
2795	SAIDA	3	Importação automática - NF: 0000004829 | Código sincronizado (1023705 -> 215) | Produto NF: REMOX BB5L	2026-01-09 14:16:58.990543+00	966	3	VENDA	43	40	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1023705\\"}"	"{\\"codigo\\": \\"215\\"}"	\N	f	\N	\N
2914	ENTRADA	10	NF 129944 - Processamento automático	2026-01-22 09:23:27.720149+00	792	1	\N	0	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2918	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:23:28.019987+00	962	1	\N	0	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2922	ENTRADA	5	NF 129944 - Processamento automático	2026-01-22 09:23:28.092354+00	1007	1	\N	15	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2926	ENTRADA	29	NF 129944 - Processamento automático	2026-01-22 09:23:28.170103+00	1025	1	\N	21	50	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2930	ENTRADA	7	NF 129944 - Processamento automático	2026-01-22 09:23:28.196009+00	1036	1	\N	36	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2936	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:46:54.864086+00	903	1	\N	9	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2940	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:46:54.885426+00	1007	1	\N	24	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2944	ENTRADA	21	NF 129944 - Processamento automático	2026-01-22 09:46:54.907356+00	1025	1	\N	54	75	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2948	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:46:54.97789+00	1036	1	\N	43	44	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2953	ENTRADA	2	NF 129944 - Processamento automático	2026-01-22 09:56:22.725674+00	792	1	\N	34	36	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2957	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:56:22.748029+00	965	1	\N	8	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2961	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:56:22.770022+00	1024	1	\N	12	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2965	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:56:22.792623+00	1025	1	\N	158	162	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2969	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:56:22.864128+00	980	1	\N	15	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2971	ENTRADA	10	NF 129944 - Processamento automático	2026-01-22 09:59:53.432297+00	792	1	\N	36	46	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2975	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:59:53.456744+00	962	1	\N	12	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2979	ENTRADA	5	NF 129944 - Processamento automático	2026-01-22 09:59:53.48242+00	1007	1	\N	45	50	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2983	ENTRADA	29	NF 129944 - Processamento automático	2026-01-22 09:59:53.660373+00	1025	1	\N	183	212	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2987	ENTRADA	7	NF 129944 - Processamento automático	2026-01-22 09:59:53.870535+00	1036	1	\N	60	67	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3088	ENTRADA	12	NF None - Processamento automático	2026-01-29 18:42:00.673005+00	1030	3	\N	10	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3101	SAIDA	2	NF 0000004857 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:02:06.24829+00	931	3	\N	24	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3105	SAIDA	15	NF 0000004860 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:02:33.399356+00	1007	3	\N	76	61	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2771	SAIDA	6	Importação automática - NF: 0000004811 | Produto NF: PANO DE CHAO ALVEJADO FLANELADO 48X68	2026-01-09 14:14:20.236488+00	925	3	VENDA	453	447	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2772	SAIDA	2	Importação automática - NF: 0000004811 | Produto NF: ESPONJA DUPLA FACE	2026-01-09 14:14:20.236488+00	839	3	VENDA	201	199	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2773	SAIDA	3	Importação automática - NF: 0000004811 | Produto NF: FLANELA CRISTAL M 40X60	2026-01-09 14:14:20.236488+00	850	3	VENDA	126	123	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2774	SAIDA	1	Importação automática - NF: 0000004811 | Produto NF: AROMATIZADOR LAVANDA 360ML	2026-01-09 14:14:20.236488+00	802	3	VENDA	38	37	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2775	SAIDA	1	Importação automática - NF: 0000004811 | Produto NF: M 19 O 0 P G - R REFIL ZIGZAG MINI-MOP ALG. PAVIO MOPINHO	2026-01-09 14:14:20.236488+00	961	3	VENDA	11	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2776	SAIDA	6	Importação automática - NF: 0000004811 | Produto NF: DETERGENTE ECONOMICO NEUTRO 500ML	2026-01-09 14:14:20.236488+00	825	3	VENDA	65	59	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2777	SAIDA	1	Importação automática - NF: 0000004811 | Código sincronizado (PROD198 -> 568) | Produto NF: S P A LA C S O T P IC ARA LIXO AZUL 60 LITROS 60x70 BETA	2026-01-09 14:14:20.236488+00	984	3	VENDA	14	13	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD198\\"}"	"{\\"codigo\\": \\"568\\"}"	\N	f	\N	\N
2778	SAIDA	1	Importação automática - NF: 0000004811 | Código sincronizado (PROD050 -> 976) | Produto NF: ESCOVA SANITARIA C SUPORTE	2026-01-09 14:14:20.236488+00	836	3	VENDA	37	36	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD050\\"}"	"{\\"codigo\\": \\"976\\"}"	\N	f	\N	\N
2796	SAIDA	12	Importação automática - NF: 0000004831 | Código sincronizado (1027955 -> 222) | Produto NF: SPRAY SANITIZANTE BOLSA 500ML	2026-01-09 14:17:18.96003+00	1025	3	VENDA	54	42	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1027955\\"}"	"{\\"codigo\\": \\"222\\"}"	\N	f	\N	\N
2915	ENTRADA	2	NF 129944 - Processamento automático	2026-01-22 09:23:27.861198+00	792	1	\N	10	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2919	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:23:28.068244+00	965	1	\N	0	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2923	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:23:28.100356+00	1024	1	\N	4	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2927	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:23:28.177079+00	1025	1	\N	50	54	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2931	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:23:28.201958+00	980	1	\N	7	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2934	ENTRADA	2	NF 129944 - Processamento automático	2026-01-22 09:46:54.852699+00	792	1	\N	22	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2938	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:46:54.874852+00	965	1	\N	4	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2942	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:46:54.895977+00	1024	1	\N	8	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2946	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:46:54.966313+00	1025	1	\N	104	108	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2950	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:46:54.989001+00	980	1	\N	11	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2954	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:56:22.73124+00	870	1	\N	18	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2958	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:56:22.753394+00	1007	1	\N	30	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2962	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 09:56:22.775389+00	1024	1	\N	13	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2966	ENTRADA	12	NF 129944 - Processamento automático	2026-01-22 09:56:22.798788+00	1035	1	\N	42	54	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2970	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 09:56:22.870053+00	980	1	\N	16	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2973	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:59:53.44488+00	870	1	\N	22	26	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2977	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:59:53.469877+00	1007	1	\N	40	44	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2981	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 09:59:53.496168+00	1024	1	\N	17	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2985	ENTRADA	12	NF 129944 - Processamento automático	2026-01-22 09:59:53.767169+00	1035	1	\N	54	66	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2989	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 09:59:54.062183+00	980	1	\N	20	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3089	ENTRADA	8	NF None - Processamento automático	2026-01-29 18:42:00.681413+00	1048	3	\N	3	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3100	SAIDA	5	NF 0000004857 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:02:06.224258+00	940	3	\N	76	71	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2779	SAIDA	3	Importação automática - NF: 0000004832 | Código sincronizado (1021005 -> 8) | Produto NF: DESINCROST BB 5L	2026-01-09 14:14:47.307693+00	820	3	VENDA	64	61	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1021005\\"}"	"{\\"codigo\\": \\"8\\"}"	\N	f	\N	\N
2784	SAIDA	1	Importação automática - NF: 0000001279 | Produto NF: OXIPRO SOFT BB 5L REND 100L	2026-01-09 14:15:59.640605+00	920	3	VENDA	19	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2785	SAIDA	1	Importação automática - NF: 0000001279 | Produto NF: AGUASSANI BB 5L REND 20L	2026-01-09 14:15:59.640605+00	789	3	VENDA	20	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2786	SAIDA	1	Importação automática - NF: 0000001279 | Produto NF: PISOFLOR BB 5L REND 100L	2026-01-09 14:15:59.640605+00	952	3	VENDA	4	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2787	SAIDA	2	Importação automática - NF: 0000001279 | Produto NF: VIDROLUX BB 5L REND 25L	2026-01-09 14:15:59.640605+00	1048	3	VENDA	5	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2788	SAIDA	1	Importação automática - NF: 0000001279 | Código sincronizado (1018605 -> 27) | Produto NF: MULTILUX BAC BREEZE BB 5L REND 750	2026-01-09 14:15:59.640605+00	905	3	VENDA	4	3	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1018605\\"}"	"{\\"codigo\\": \\"27\\"}"	\N	f	\N	\N
2789	SAIDA	1	Importação automática - NF: 0000001278 | Produto NF: DESINCROST BB 5L	2026-01-09 14:16:34.203657+00	820	3	VENDA	61	60	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2790	SAIDA	1	Importação automática - NF: 0000001278 | Produto NF: VIDROLUX BB 5L REND 25L	2026-01-09 14:16:34.203657+00	1048	3	VENDA	3	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2791	SAIDA	1	Importação automática - NF: 0000001278 | Código sincronizado (1025805 -> 345) | Produto NF: SABONETE PRAXI ESPUMA ANDIROBA 5L	2026-01-09 14:16:34.203657+00	1033	3	VENDA	13	12	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1025805\\"}"	"{\\"codigo\\": \\"345\\"}"	\N	f	\N	\N
2792	SAIDA	1	Importação automática - NF: 0000001278 | Código sincronizado (1003305 -> 23) | Produto NF: SANILUX BB 5 L REND 50L	2026-01-09 14:16:34.203657+00	1021	3	VENDA	8	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1003305\\"}"	"{\\"codigo\\": \\"23\\"}"	\N	f	\N	\N
2793	SAIDA	4	Importação automática - NF: 0000001278 | Código sincronizado (1001405 -> 43) | Produto NF: DETERGENTE CLORADO BB 5L	2026-01-09 14:16:34.203657+00	824	3	VENDA	109	105	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1001405\\"}"	"{\\"codigo\\": \\"43\\"}"	\N	f	\N	\N
2916	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:23:27.963739+00	870	1	\N	10	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2920	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:23:28.078258+00	1007	1	\N	10	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2924	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 09:23:28.107426+00	1024	1	\N	5	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2928	ENTRADA	12	NF 129944 - Processamento automático	2026-01-22 09:23:28.183539+00	1035	1	\N	18	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2932	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 09:23:28.208371+00	980	1	\N	8	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2933	ENTRADA	10	NF 129944 - Processamento automático	2026-01-22 09:46:54.845655+00	792	1	\N	12	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2937	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:46:54.869446+00	962	1	\N	4	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2941	ENTRADA	5	NF 129944 - Processamento automático	2026-01-22 09:46:54.890853+00	1007	1	\N	25	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2945	ENTRADA	29	NF 129944 - Processamento automático	2026-01-22 09:46:54.959202+00	1025	1	\N	75	104	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2949	ENTRADA	7	NF 129944 - Processamento automático	2026-01-22 09:46:54.98343+00	1036	1	\N	44	51	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2955	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:56:22.737268+00	903	1	\N	13	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2959	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:56:22.758929+00	1007	1	\N	34	35	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2963	ENTRADA	21	NF 129944 - Processamento automático	2026-01-22 09:56:22.781329+00	1025	1	\N	108	129	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2967	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:56:22.804603+00	1036	1	\N	51	52	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2972	ENTRADA	2	NF 129944 - Processamento automático	2026-01-22 09:59:53.439326+00	792	1	\N	46	48	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2976	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:59:53.464203+00	965	1	\N	12	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2980	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:59:53.487857+00	1024	1	\N	16	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2984	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:59:53.667311+00	1025	1	\N	212	216	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2988	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:59:53.964843+00	980	1	\N	19	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2782	SAIDA	1	Importação automática - NF: 0000004830 | Produto NF: OXIPRO SOFT BB 5L	2026-01-09 14:15:30.540854+00	920	3	VENDA	20	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2783	SAIDA	1	Importação automática - NF: 0000004830 | Produto NF: DESINFETANTE SANIFLOR CAPIM LIMAO BB 5L	2026-01-09 14:15:30.540854+00	1012	3	VENDA	6	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2917	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:23:27.99403+00	903	1	\N	5	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2921	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:23:28.085428+00	1007	1	\N	14	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2925	ENTRADA	21	NF 129944 - Processamento automático	2026-01-22 09:23:28.163174+00	1025	1	\N	0	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2929	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:23:28.189877+00	1036	1	\N	35	36	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2935	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:46:54.858415+00	870	1	\N	14	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2939	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:46:54.880241+00	1007	1	\N	20	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2943	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 09:46:54.901582+00	1024	1	\N	9	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2947	ENTRADA	12	NF 129944 - Processamento automático	2026-01-22 09:46:54.972039+00	1035	1	\N	30	42	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2951	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 09:46:54.994359+00	980	1	\N	12	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2952	ENTRADA	10	NF 129944 - Processamento automático	2026-01-22 09:56:22.718558+00	792	1	\N	24	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2956	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:56:22.742685+00	962	1	\N	8	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2960	ENTRADA	5	NF 129944 - Processamento automático	2026-01-22 09:56:22.764252+00	1007	1	\N	35	40	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2964	ENTRADA	29	NF 129944 - Processamento automático	2026-01-22 09:56:22.786948+00	1025	1	\N	129	158	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2968	ENTRADA	7	NF 129944 - Processamento automático	2026-01-22 09:56:22.810263+00	1036	1	\N	52	59	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2974	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 09:59:53.450414+00	903	1	\N	17	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2978	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:59:53.476034+00	1007	1	\N	44	45	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2982	ENTRADA	21	NF 129944 - Processamento automático	2026-01-22 09:59:53.563602+00	1025	1	\N	162	183	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2986	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 09:59:53.863625+00	1036	1	\N	59	60	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2797	SAIDA	1	\N	2026-01-09 17:44:22.952634+00	993	3	\N	9	8	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2990	ENTRADA	10	NF 129944 - Processamento automático	2026-01-22 10:11:07.626173+00	792	1	\N	48	58	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2991	ENTRADA	2	NF 129944 - Processamento automático	2026-01-22 10:11:07.640629+00	792	1	\N	58	60	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2992	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:11:07.645748+00	870	1	\N	26	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2993	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:11:07.650935+00	903	1	\N	21	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2994	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:11:07.656206+00	962	1	\N	16	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2995	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:11:07.661361+00	965	1	\N	16	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2996	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:11:07.666575+00	1007	1	\N	50	54	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2997	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 10:11:07.671774+00	1007	1	\N	54	55	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2998	ENTRADA	5	NF 129944 - Processamento automático	2026-01-22 10:11:07.677114+00	1007	1	\N	55	60	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2999	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 10:11:07.682063+00	1024	1	\N	20	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3000	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 10:11:07.68734+00	1024	1	\N	21	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3001	ENTRADA	21	NF 129944 - Processamento automático	2026-01-22 10:11:07.692462+00	1025	1	\N	216	237	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3002	ENTRADA	29	NF 129944 - Processamento automático	2026-01-22 10:11:07.698139+00	1025	1	\N	237	266	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3003	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:11:07.702907+00	1025	1	\N	266	270	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3004	ENTRADA	12	NF 129944 - Processamento automático	2026-01-22 10:11:07.708309+00	1035	1	\N	66	78	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3005	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 10:11:07.762932+00	1036	1	\N	67	68	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3006	ENTRADA	7	NF 129944 - Processamento automático	2026-01-22 10:11:07.769027+00	1036	1	\N	68	75	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3007	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 10:11:07.862805+00	980	1	\N	23	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3008	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 10:11:07.961755+00	980	1	\N	24	27	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3010	ENTRADA	2	NF 129944 - Processamento automático	2026-01-22 10:13:36.633859+00	792	1	\N	70	72	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3013	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:13:36.649448+00	962	1	\N	20	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3016	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 10:13:36.664392+00	1007	1	\N	64	65	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3019	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 10:13:36.679274+00	1024	1	\N	25	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3022	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:13:36.694221+00	1025	1	\N	320	324	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3025	ENTRADA	7	NF 129944 - Processamento automático	2026-01-22 10:13:36.709093+00	1036	1	\N	76	83	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2798	SAIDA	2	Importação automática - NF: 0000001281 | Produto NF: LIMPAX DX BB5L	2026-01-12 13:59:52.831551+00	874	3	VENDA	162	160	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2799	SAIDA	2	Importação automática - NF: 0000001281 | Produto NF: DESINCROST BB 5L	2026-01-12 13:59:52.831551+00	820	3	VENDA	60	58	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2800	SAIDA	2	Importação automática - NF: 0000001281 | Produto NF: DETERGENTE CLORADO BB 5L	2026-01-12 13:59:52.831551+00	824	3	VENDA	105	103	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2801	SAIDA	1	Importação automática - NF: 0000001281 | Produto NF: OXIPRO SOFT BB 5L REND 100L	2026-01-12 13:59:52.831551+00	920	3	VENDA	18	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2804	SAIDA	3	\N	2026-01-12 14:04:27.525935+00	824	3	\N	103	100	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2811	ENTRADA	7	\N	2026-01-12 14:33:42.614419+00	1036	3	\N	28	35	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2813	ENTRADA	2	\N	2026-01-12 14:37:43.589279+00	1048	3	\N	2	4	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3009	ENTRADA	10	NF 129944 - Processamento automático	2026-01-22 10:13:36.62643+00	792	1	\N	60	70	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3012	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:13:36.644269+00	903	1	\N	25	29	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3015	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:13:36.659562+00	1007	1	\N	60	64	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3018	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 10:13:36.674157+00	1024	1	\N	24	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3021	ENTRADA	29	NF 129944 - Processamento automático	2026-01-22 10:13:36.689201+00	1025	1	\N	291	320	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3024	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 10:13:36.704163+00	1036	1	\N	75	76	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3027	ENTRADA	3	NF 129944 - Processamento automático	2026-01-22 10:13:36.765093+00	980	1	\N	28	31	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2802	ENTRADA	9	\N	2026-01-12 14:01:46.093353+00	789	3	\N	19	28	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2809	SAIDA	1	\N	2026-01-12 14:18:15.769663+00	1076	3	\N	6	5	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2812	SAIDA	1	\N	2026-01-12 14:35:42.686198+00	1025	3	\N	42	41	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3011	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:13:36.638941+00	870	1	\N	30	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3014	ENTRADA	4	NF 129944 - Processamento automático	2026-01-22 10:13:36.654435+00	965	1	\N	20	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3017	ENTRADA	5	NF 129944 - Processamento automático	2026-01-22 10:13:36.669345+00	1007	1	\N	65	70	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3020	ENTRADA	21	NF 129944 - Processamento automático	2026-01-22 10:13:36.684137+00	1025	1	\N	270	291	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3023	ENTRADA	12	NF 129944 - Processamento automático	2026-01-22 10:13:36.698992+00	1035	1	\N	78	90	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3026	ENTRADA	1	NF 129944 - Processamento automático	2026-01-22 10:13:36.714025+00	980	1	\N	27	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2803	ENTRADA	1	\N	2026-01-12 14:03:44.666613+00	822	3	\N	53	54	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2805	SAIDA	2	\N	2026-01-12 14:04:58.473136+00	874	3	\N	160	158	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2806	SAIDA	10	\N	2026-01-12 14:05:09.002926+00	874	3	\N	158	148	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2810	SAIDA	1	\N	2026-01-12 14:18:34.715897+00	910	3	\N	19	18	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3028	ENTRADA	1	\N	2026-01-23 13:32:43.988234+00	787	1	\N	10	11	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2807	SAIDA	4	\N	2026-01-12 14:05:54.708421+00	966	3	\N	40	36	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2808	ENTRADA	2	\N	2026-01-12 14:16:20.529627+00	903	3	\N	3	5	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3029	SAIDA	1	\N	2026-01-23 13:32:49.89489+00	787	1	\N	11	10	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2814	SAIDA	2	\N	2026-01-12 17:29:26.63309+00	807	3	\N	2	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3030	ENTRADA	12	\N	2026-01-26 13:18:38.060442+00	1112	3	\N	0	12	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3035	SAIDA	40	NF 0000004850 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:52:34.050019+00	936	3	\N	500	460	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3039	SAIDA	3	NF 0000004850 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:52:34.094264+00	1001	3	\N	37	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3042	SAIDA	1	NF 0000004849 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:22.570601+00	1021	3	\N	7	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3045	SAIDA	3	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.353346+00	977	3	\N	105	102	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3049	SAIDA	1	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.380955+00	929	3	\N	7	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3055	SAIDA	3	NF 0000004853 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:56:50.25484+00	874	3	\N	110	107	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3058	SAIDA	24	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:57:41.43954+00	788	3	\N	91	67	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3062	SAIDA	1	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:57:41.471435+00	1012	3	\N	4	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3072	SAIDA	3	NF 0000001289 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:58:42.85092+00	873	3	\N	39	36	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2815	SAIDA	3	thiago	2026-01-12 19:19:16.576344+00	941	3	\N	151	148	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3031	SAIDA	10	\N	2026-01-26 13:30:23.309489+00	843	3	\N	500	490	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
3032	SAIDA	4	\N	2026-01-26 13:30:30.6836+00	847	3	\N	168	164	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3038	SAIDA	5	NF 0000004850 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:52:34.087777+00	1002	3	\N	66	61	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3041	SAIDA	1	NF 0000004849 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:22.564089+00	991	3	\N	22	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3044	SAIDA	6	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.345764+00	823	3	\N	82	76	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3048	SAIDA	2	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.374454+00	991	3	\N	21	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3052	SAIDA	1	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.401557+00	1045	3	\N	41	40	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3061	SAIDA	10	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:57:41.464768+00	977	3	\N	102	92	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3067	SAIDA	2	NF 0000004854 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:58:04.316525+00	824	3	\N	59	57	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3071	SAIDA	1	NF 0000001289 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:58:42.83827+00	1048	3	\N	4	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2816	ENTRADA	46	\N	2026-01-13 14:35:14.895581+00	807	3	\N	0	46	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2819	SAIDA	1	Importação automática - NF: 0000001282 | Produto NF: DESINFETANTE SANIFLOR CAPIM LIMAO BB 5L	2026-01-13 14:40:27.154759+00	1012	3	VENDA	5	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2820	SAIDA	4	Importação automática - NF: 0000001282 | Produto NF: FLANELA CRISTAL M 40X60	2026-01-13 14:40:27.154759+00	850	3	VENDA	123	119	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2821	SAIDA	20	Importação automática - NF: 0000001282 | Produto NF: DETERGENTE NEUTRO FC 500ML	2026-01-13 14:40:27.154759+00	823	3	VENDA	102	82	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2822	SAIDA	10	Importação automática - NF: 0000001282 | Produto NF: PANO DE CHAO XADREZ 45X70	2026-01-13 14:40:27.154759+00	926	3	VENDA	329	319	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2823	SAIDA	15	Importação automática - NF: 0000001282 | Produto NF: ESPONJA DUPLA FACE	2026-01-13 14:40:27.154759+00	839	3	VENDA	199	184	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2824	SAIDA	5	Importação automática - NF: 0000001282 | Produto NF: AGUA SANITARIA CLORITO 1L	2026-01-13 14:40:27.154759+00	788	3	VENDA	120	115	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2825	SAIDA	1	Importação automática - NF: 0000001282 | Produto NF: VASSOURA PIACAVA RAINHA MAX	2026-01-13 14:40:27.154759+00	1046	3	VENDA	46	45	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2826	SAIDA	2	Importação automática - NF: 0000001282 | Produto NF: S P A LA C S O T P IC / LIXO 75X90X0,03 - PRETO 100LT BETA	2026-01-13 14:40:27.154759+00	990	3	VENDA	30	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2827	SAIDA	1	Importação automática - NF: 0000001282 | Produto NF: VASSOURA LINDONA	2026-01-13 14:40:27.154759+00	1045	3	VENDA	42	41	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2828	SAIDA	1	Importação automática - NF: 0000001282 | Código sincronizado (PROD233 -> 174) | Produto NF: DESINFETANTE SANIFLOR SOFT BB 5L	2026-01-13 14:40:27.154759+00	1019	3	VENDA	4	3	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD233\\"}"	"{\\"codigo\\": \\"174\\"}"	\N	f	\N	\N
2829	SAIDA	1	Importação automática - NF: 0000001282 | Código sincronizado (830 -> 362) | Produto NF: AROMATIZADOR CHEIRO DE TALCO 360ML	2026-01-13 14:40:27.154759+00	803	3	VENDA	36	35	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"830\\"}"	"{\\"codigo\\": \\"362\\"}"	\N	f	\N	\N
2830	SAIDA	5	Importação automática - NF: 0000001282 | Código sincronizado (PROD155 -> 389) | Produto NF: P P A R P E E M L IU T M OALHA INTERF.C/ 1000F 100% CELULOSE	2026-01-13 14:40:27.154759+00	941	3	VENDA	148	143	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD155\\"}"	"{\\"codigo\\": \\"389\\"}"	\N	f	\N	\N
2831	SAIDA	6	Importação automática - NF: 0000001282 | Código sincronizado (PROD099 -> 742) | Produto NF: LUVA MULTIUSO LATEX QUALITY P	2026-01-13 14:40:27.154759+00	885	3	VENDA	84	78	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD099\\"}"	"{\\"codigo\\": \\"742\\"}"	\N	f	\N	\N
2833	SAIDA	1	Importação automática - NF: 0000004833 | Produto NF: DESINCROST BB 5L	2026-01-13 14:44:01.123124+00	820	3	VENDA	58	57	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2834	SAIDA	4	Importação automática - NF: 0000004833 | Produto NF: LIMPAX DX BB5L	2026-01-13 14:44:01.123124+00	874	3	VENDA	144	140	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2835	SAIDA	3	Importação automática - NF: 0000004833 | Produto NF: DETERGENTE CLORADO BB 5L	2026-01-13 14:44:01.123124+00	824	3	VENDA	96	93	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2836	SAIDA	1	Importação automática - NF: 0000004833 | Produto NF: REMOX BB5L	2026-01-13 14:44:01.123124+00	966	3	VENDA	36	35	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2837	SAIDA	20	Importação automática - NF: 0000004833 | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2026-01-13 14:44:01.123124+00	936	3	VENDA	240	220	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2838	SAIDA	1	Importação automática - NF: 0000004833 | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2026-01-13 14:44:01.123124+00	935	3	VENDA	13	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2839	SAIDA	1	Importação automática - NF: 0000004833 | Produto NF: ALCOOL SAFRA 5L	2026-01-13 14:44:01.123124+00	1062	3	VENDA	12	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2840	SAIDA	3	Importação automática - NF: 0000004833 | Produto NF: SABONETE SUAVITEX BAC SP BOL 500ML	2026-01-13 14:44:01.123124+00	1030	3	VENDA	25	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2841	SAIDA	10	Importação automática - NF: 0000004833 | Produto NF: FIBRA P/ LIMPEZA 1X20X10 ULTRA PESADA	2026-01-13 14:44:01.123124+00	845	3	VENDA	10	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2842	SAIDA	1	Importação automática - NF: 0000004833 | Código sincronizado (345 -> 606) | Produto NF: PRAXI SABON ESPUMA ANDIROBA 5L	2026-01-13 14:44:01.123124+00	1033	3	VENDA	12	11	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"345\\"}"	"{\\"codigo\\": \\"606\\"}"	\N	f	\N	\N
2843	SAIDA	1	Importação automática - NF: 0000004833 | Código sincronizado (1027105 -> 191) | Produto NF: SANICLOR BB5L	2026-01-13 14:44:01.123124+00	1006	3	VENDA	33	32	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1027105\\"}"	"{\\"codigo\\": \\"191\\"}"	\N	f	\N	\N
3033	SAIDA	10	\N	2026-01-26 13:30:43.22036+00	848	3	\N	409	399	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
3037	SAIDA	2	NF 0000004850 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:52:34.079895+00	935	3	\N	10	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3040	SAIDA	3	NF 0000004849 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:22.55396+00	937	3	\N	4	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3043	SAIDA	1	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.334536+00	947	3	\N	8	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3047	SAIDA	2	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.367435+00	1001	3	\N	34	32	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3051	SAIDA	1	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.39489+00	1036	3	\N	83	82	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3053	SAIDA	5	NF 0000004842 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:56:29.679072+00	874	3	\N	115	110	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3056	SAIDA	2	NF 0000004853 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:56:50.266451+00	966	3	\N	30	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3059	SAIDA	5	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:57:41.450288+00	932	3	\N	5	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3063	SAIDA	1	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:57:41.47762+00	1013	3	\N	4	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3065	SAIDA	4	NF 0000004854 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:58:04.301589+00	966	3	\N	28	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3069	SAIDA	4	NF 0000001289 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:58:42.816521+00	824	3	\N	57	53	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2817	SAIDA	4	Importação automática - NF: 0000004834 | Produto NF: DETERGENTE CLORADO BB 5L	2026-01-13 14:38:05.832839+00	824	3	VENDA	100	96	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2818	SAIDA	4	Importação automática - NF: 0000004834 | Produto NF: LIMPAX DX BB5L	2026-01-13 14:38:05.832839+00	874	3	VENDA	148	144	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3034	SAIDA	1	\N	2026-01-26 13:30:56.627153+00	995	3	\N	6	5	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
3036	SAIDA	2	NF 0000004850 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:52:34.07175+00	938	3	\N	10	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3046	SAIDA	6	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.360361+00	839	3	\N	184	178	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3050	SAIDA	1	NF 0000004847 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:55:57.388071+00	789	3	\N	28	27	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3054	SAIDA	2	NF 0000004842 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:56:29.689612+00	966	3	\N	32	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3057	SAIDA	24	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:57:31.27009+00	788	3	\N	115	91	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3060	SAIDA	5	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:57:41.457557+00	935	3	\N	8	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3064	SAIDA	2	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:57:41.483561+00	974	3	\N	2	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3066	SAIDA	4	NF 0000004854 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:58:04.310473+00	874	3	\N	107	103	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3068	SAIDA	12	NF 0000001290 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:58:27.185834+00	1030	3	\N	22	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3070	SAIDA	1	NF 0000001289 - Processamento automático - Cliente: Frete por Conta C	2026-01-26 13:58:42.826269+00	820	3	\N	57	56	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2832	SAIDA	4	\N	2026-01-13 14:40:52.366471+00	807	3	\N	46	42	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2844	SAIDA	4	\N	2026-01-13 14:44:25.599472+00	1025	3	\N	41	37	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
3073	ENTRADA	20	\N	2026-01-27 18:07:27.492278+00	935	3	\N	3	23	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3076	SAIDA	4	NF 0000004856 - Processamento automático - Cliente: Frete por Conta C	2026-01-27 19:00:16.207085+00	796	3	\N	10	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1599	SAIDA	2	Importação automática - NF: 0000004684	2025-10-31 02:20:28.406053+00	874	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1600	SAIDA	2	Importação automática - NF: 0000004684	2025-10-31 02:20:28.406053+00	966	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1601	SAIDA	2	Importação automática - NF: 0000004684	2025-10-31 02:20:28.406053+00	824	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1602	SAIDA	1	Importação automática - NF: 0000004684	2025-10-31 02:20:28.406053+00	1012	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1603	SAIDA	5	Importação automática - NF: 0000004684	2025-10-31 02:20:28.406053+00	940	1	\N	\N	\N	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1604	SAIDA	6	Importação automática - NF: 0000004681	2025-10-31 02:48:29.771063+00	874	1	VENDA	164	158	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1605	SAIDA	3	Importação automática - NF: 0000004681	2025-10-31 02:48:29.771063+00	966	1	VENDA	62	59	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1606	SAIDA	12	Importação automática - NF: 0000001208	2025-10-31 02:49:37.574615+00	874	1	VENDA	158	146	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1607	SAIDA	6	Importação automática - NF: 0000001208	2025-10-31 02:49:37.574615+00	1030	1	VENDA	52	46	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1608	SAIDA	2	Importação automática - NF: 0000001208	2025-10-31 02:49:37.574615+00	822	1	VENDA	54	52	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1609	SAIDA	1	Importação automática - NF: 0000004683	2025-10-31 02:51:47.853466+00	978	1	VENDA	16	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1610	SAIDA	1	Importação automática - NF: 0000004683	2025-10-31 02:51:47.853466+00	1035	1	VENDA	27	26	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1611	SAIDA	2	Importação automática - NF: 0000004676	2025-10-31 02:53:55.743411+00	1001	1	VENDA	42	40	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1612	SAIDA	2	Importação automática - NF: 0000004676	2025-10-31 02:53:55.743411+00	991	1	VENDA	42	40	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1613	SAIDA	2	Importação automática - NF: 0000004676	2025-10-31 02:53:55.743411+00	1066	1	VENDA	2	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1614	SAIDA	1	Importação automática - NF: 0000004676	2025-10-31 02:53:55.743411+00	1012	1	VENDA	9	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1615	SAIDA	40	Importação automática - NF: 0000004679	2025-10-31 02:55:36.408783+00	936	1	VENDA	725	685	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1616	SAIDA	2	Importação automática - NF: 0000004679	2025-10-31 02:55:36.408783+00	938	1	VENDA	14	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1617	SAIDA	3	Importação automática - NF: 0000004679	2025-10-31 02:55:36.408783+00	935	1	VENDA	21	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1618	SAIDA	5	Importação automática - NF: 0000004679	2025-10-31 02:55:36.408783+00	996	1	VENDA	52	47	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1619	SAIDA	1	Importação automática - NF: 0000004679	2025-10-31 02:55:36.408783+00	1033	1	VENDA	10	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1620	SAIDA	6	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	1025	1	VENDA	112	106	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1621	SAIDA	1	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	1062	1	VENDA	14	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1622	SAIDA	2	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	984	1	VENDA	18	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1623	SAIDA	6	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	991	1	VENDA	40	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1624	SAIDA	2	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	951	1	VENDA	18	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1625	SAIDA	3	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	789	1	VENDA	40	37	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1626	SAIDA	3	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	824	1	VENDA	200	197	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1627	SAIDA	1	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	929	1	VENDA	6	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1628	SAIDA	12	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	839	1	VENDA	212	200	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1629	SAIDA	2	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	830	1	VENDA	5	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1630	SAIDA	12	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	925	1	VENDA	565	553	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1631	SAIDA	1	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	968	1	VENDA	25	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1632	SAIDA	1	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	808	1	VENDA	16	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1633	SAIDA	6	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	956	1	VENDA	93	87	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1634	SAIDA	2	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	976	1	VENDA	41	39	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1635	SAIDA	1	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	834	1	VENDA	11	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1636	SAIDA	60	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	940	1	VENDA	232	172	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1637	SAIDA	6	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	853	1	VENDA	14	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1638	SAIDA	12	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	802	1	VENDA	54	42	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1639	SAIDA	100	Importação automática - NF: 0000004680	2025-10-31 03:04:56.786359+00	817	1	VENDA	133	33	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1640	SAIDA	9	Importação automática - NF: 0000004678	2025-10-31 03:09:03.925775+00	925	1	VENDA	553	544	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1641	SAIDA	1	Importação automática - NF: 0000004678	2025-10-31 03:09:03.925775+00	929	1	VENDA	5	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1642	SAIDA	3	Importação automática - NF: 0000004678	2025-10-31 03:09:03.925775+00	789	1	VENDA	37	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1643	SAIDA	2	Importação automática - NF: 0000004678	2025-10-31 03:09:03.925775+00	951	1	VENDA	16	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1644	SAIDA	25	Importação automática - NF: 0000004678	2025-10-31 03:09:03.925775+00	817	1	VENDA	33	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1645	SAIDA	6	Importação automática - NF: 0000004678	2025-10-31 03:09:03.925775+00	850	1	VENDA	174	168	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1646	SAIDA	1	Importação automática - NF: 0000004678	2025-10-31 03:09:03.925775+00	1062	1	VENDA	13	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1647	SAIDA	2	Importação automática - NF: 0000004678	2025-10-31 03:09:03.925775+00	853	1	VENDA	8	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1648	SAIDA	4	ajuste	2025-10-31 11:31:12.84294+00	946	3	\N	4	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1649	SAIDA	6	ÓTICA	2025-10-31 12:04:37.44206+00	825	3	\N	226	220	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1650	SAIDA	5	HSO	2025-10-31 12:06:07.402115+00	931	3	\N	94	89	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1651	SAIDA	12	Importação automática - NF: 0000001212	2025-10-31 12:10:15.55582+00	824	3	VENDA	197	185	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1652	SAIDA	12	Importação automática - NF: 0000001212	2025-10-31 12:10:15.55582+00	874	3	VENDA	146	134	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1653	SAIDA	26	Importação automática - NF: 0000001212	2025-10-31 12:10:15.55582+00	919	3	VENDA	35	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1654	SAIDA	4	Importação automática - NF: 0000001212	2025-10-31 12:10:15.55582+00	966	3	VENDA	59	55	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1655	SAIDA	7	ALDENORA BELO	2025-10-31 12:11:35.72356+00	903	3	\N	8	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1656	ENTRADA	36	\N	2025-10-31 12:13:21.67618+00	934	3	\N	12	48	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1657	SAIDA	160	ajuste	2025-10-31 17:43:24.137642+00	941	3	\N	260	100	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1658	SAIDA	3	\N	2025-10-31 18:35:20.457792+00	937	3	\N	13	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1659	SAIDA	25	\N	2025-10-31 18:35:34.871241+00	931	3	\N	89	64	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1660	SAIDA	4	Importação automática - NF: 0000004685	2025-10-31 18:40:15.06267+00	966	3	VENDA	55	51	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1661	SAIDA	5	Importação automática - NF: 0000004685	2025-10-31 18:40:15.06267+00	874	3	VENDA	134	129	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1662	SAIDA	4	Importação automática - NF: 0000004685	2025-10-31 18:40:15.06267+00	824	3	VENDA	185	181	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1663	SAIDA	4	Importação automática - NF: 0000004685	2025-10-31 18:40:15.06267+00	792	3	VENDA	20	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1664	SAIDA	3	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	1033	3	VENDA	9	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1665	SAIDA	1	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	1015	3	VENDA	46	45	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1666	SAIDA	1	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	1016	3	VENDA	46	45	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1667	SAIDA	10	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	850	3	VENDA	168	158	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1668	SAIDA	5	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	925	3	VENDA	544	539	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1669	SAIDA	3	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	824	3	VENDA	181	178	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1670	SAIDA	2	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	950	3	VENDA	4	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1671	SAIDA	6	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	990	3	VENDA	50	44	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1672	SAIDA	3	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	999	3	VENDA	12	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1673	SAIDA	3	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	957	3	VENDA	12	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1674	SAIDA	1	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	797	3	VENDA	26	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1675	SAIDA	12	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	825	3	VENDA	220	208	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1676	SAIDA	2	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	951	3	VENDA	14	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1677	SAIDA	46	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	788	3	VENDA	82	36	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1678	SAIDA	2	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	902	3	VENDA	22	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1679	SAIDA	1	Importação automática - NF: 0000004686	2025-10-31 18:46:35.853841+00	868	3	VENDA	38	37	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1682	SAIDA	2	Importação automática - NF: 0000004688	2025-11-04 16:18:11.859949+00	978	1	VENDA	15	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1696	SAIDA	4	Importação automática - NF: 0000001218	2025-11-04 16:54:00.281715+00	874	1	VENDA	121	117	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1697	SAIDA	2	Importação automática - NF: 0000001218	2025-11-04 16:54:00.281715+00	920	1	VENDA	28	26	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1698	SAIDA	2	Importação automática - NF: 0000001218	2025-11-04 16:54:00.281715+00	966	1	VENDA	50	48	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1699	SAIDA	1	Importação automática - NF: 0000001218	2025-11-04 16:54:00.281715+00	868	1	VENDA	37	36	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1700	SAIDA	1	Importação automática - NF: 0000001218	2025-11-04 16:54:00.281715+00	1062	1	VENDA	12	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1701	SAIDA	12	Importação automática - NF: 0000001218	2025-11-04 16:54:00.281715+00	839	1	VENDA	200	188	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1702	SAIDA	24	Importação automática - NF: 0000001218	2025-11-04 16:54:00.281715+00	848	1	VENDA	570	546	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1703	SAIDA	1	Importação automática - NF: 0000004695	2025-11-04 16:54:59.436793+00	792	1	VENDA	16	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1704	SAIDA	2	Importação automática - NF: 0000004695	2025-11-04 16:54:59.436793+00	824	1	VENDA	175	173	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1705	SAIDA	4	Importação automática - NF: 0000004695	2025-11-04 16:54:59.436793+00	874	1	VENDA	117	113	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1706	SAIDA	4	Importação automática - NF: 0000004695	2025-11-04 16:54:59.436793+00	966	1	VENDA	48	44	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1714	SAIDA	12	Importação automática - NF: 0000001212	2025-11-04 16:58:24.454087+00	824	1	VENDA	171	159	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1715	SAIDA	12	Importação automática - NF: 0000001212	2025-11-04 16:58:24.454087+00	874	1	VENDA	111	99	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1716	SAIDA	4	Importação automática - NF: 0000001212	2025-11-04 16:58:24.454087+00	966	1	VENDA	44	40	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1727	SAIDA	10	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	956	1	VENDA	87	77	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1728	SAIDA	9	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	809	1	VENDA	52	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1729	SAIDA	5	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	968	1	VENDA	24	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1730	SAIDA	5	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	808	1	VENDA	15	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1731	SAIDA	10	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	846	1	VENDA	580	570	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1732	SAIDA	5	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	1038	1	VENDA	38	33	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1733	SAIDA	5	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	902	1	VENDA	20	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1734	SAIDA	1	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	1017	1	VENDA	2	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1735	SAIDA	2	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	1018	1	VENDA	2	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1736	SAIDA	5	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	881	1	VENDA	22	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1737	SAIDA	7	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	882	1	VENDA	44	37	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1738	SAIDA	2	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	918	1	VENDA	23	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1739	SAIDA	3	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	928	1	VENDA	13	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1740	SAIDA	15	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	926	1	VENDA	394	379	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1741	SAIDA	45	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	934	1	VENDA	48	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1742	SAIDA	450	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	936	1	VENDA	665	215	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1743	SAIDA	1	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	977	1	VENDA	159	158	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1744	SAIDA	3	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	1035	1	VENDA	26	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1745	SAIDA	30	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	1001	1	VENDA	40	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1746	SAIDA	4	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	1002	1	VENDA	71	67	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1747	SAIDA	2	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	993	1	VENDA	19	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1748	SAIDA	2	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	988	1	VENDA	5	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1749	SAIDA	2	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	985	1	VENDA	22	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1750	SAIDA	2	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	987	1	VENDA	8	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1751	SAIDA	2	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	1041	1	VENDA	124	122	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1752	SAIDA	7	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	880	1	VENDA	33	26	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1753	SAIDA	7	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	879	1	VENDA	54	47	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1754	SAIDA	5	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	902	1	VENDA	15	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1755	SAIDA	5	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	901	1	VENDA	25	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1756	SAIDA	5	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	901	1	VENDA	20	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1757	SAIDA	2	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	822	1	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1758	SAIDA	1	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	1048	1	VENDA	4	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1759	SAIDA	1	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	904	1	VENDA	12	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1760	SAIDA	2	Importação automática - NF: 0000004693	2025-11-04 18:13:43.421283+00	920	1	VENDA	26	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2845	SAIDA	6	\N	2026-01-13 18:26:04.247275+00	918	3	\N	19	13	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
3074	ENTRADA	5	\N	2026-01-27 18:10:00.638059+00	938	3	\N	8	13	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3075	ENTRADA	550	\N	2026-01-27 18:10:10.455523+00	936	3	\N	460	1010	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3078	SAIDA	4	NF 0000004856 - Processamento automático - Cliente: Frete por Conta C	2026-01-27 19:00:16.23197+00	863	3	\N	14	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1680	SAIDA	27	shopping	2025-10-31 18:47:02.529007+00	977	3	\N	186	159	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1681	SAIDA	1	shopping	2025-10-31 18:47:20.983849+00	1039	3	\N	18	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1683	SAIDA	3	Importação automática - NF: 0000004689	2025-11-04 16:19:32.003879+00	978	1	VENDA	13	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1684	SAIDA	2	Importação automática - NF: 0000004689	2025-11-04 16:19:32.003879+00	862	1	VENDA	28	26	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1685	SAIDA	4	Importação automática - NF: 0000004691	2025-11-04 16:20:12.743065+00	874	1	VENDA	129	125	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1686	SAIDA	1	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	820	1	VENDA	89	88	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1687	SAIDA	4	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	874	1	VENDA	125	121	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1688	SAIDA	3	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	824	1	VENDA	178	175	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1689	SAIDA	1	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	966	1	VENDA	51	50	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1690	SAIDA	20	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	936	1	VENDA	685	665	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1691	SAIDA	1	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	935	1	VENDA	18	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1692	SAIDA	1	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	1033	1	VENDA	6	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1693	SAIDA	3	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	1030	1	VENDA	46	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1694	SAIDA	1	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	1006	1	VENDA	26	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1695	SAIDA	4	Importação automática - NF: 0000004694	2025-11-04 16:23:11.121219+00	1025	1	VENDA	106	102	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1724	SAIDA	40	Importação automática - NF: 0000001214	2025-11-04 17:01:32.894642+00	874	1	VENDA	59	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1725	SAIDA	40	Importação automática - NF: 0000001214	2025-11-04 17:01:32.894642+00	820	1	VENDA	88	48	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1726	SAIDA	80	Importação automática - NF: 0000001214	2025-11-04 17:01:32.894642+00	824	1	VENDA	159	79	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1761	ENTRADA	1	\N	2025-11-04 19:14:10.1028+00	1008	3	\N	2	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2846	SAIDA	92	\N	2026-01-14 12:21:37.18115+00	848	3	\N	501	409	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3077	SAIDA	4	NF 0000004856 - Processamento automático - Cliente: Frete por Conta C	2026-01-27 19:00:16.221896+00	793	3	\N	11	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1707	SAIDA	2	Importação automática - NF: 0000001216	2025-11-04 16:56:25.079464+00	874	1	VENDA	113	111	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1708	SAIDA	2	Importação automática - NF: 0000001216	2025-11-04 16:56:25.079464+00	824	1	VENDA	173	171	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1709	SAIDA	1	Importação automática - NF: 0000001216	2025-11-04 16:56:25.079464+00	1006	1	VENDA	25	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1710	SAIDA	1	Importação automática - NF: 0000001216	2025-11-04 16:56:25.079464+00	995	1	VENDA	16	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1711	SAIDA	10	Importação automática - NF: 0000001216	2025-11-04 16:56:25.079464+00	847	1	VENDA	147	137	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1712	SAIDA	10	Importação automática - NF: 0000001216	2025-11-04 16:56:25.079464+00	848	1	VENDA	546	536	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1713	SAIDA	2	Importação automática - NF: 0000004682	2025-11-04 16:56:48.285639+00	978	1	VENDA	10	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1717	SAIDA	15	Importação automática - NF: 0000004690	2025-11-04 17:00:27.690577+00	889	1	VENDA	140	125	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1718	SAIDA	50	Importação automática - NF: 0000004690	2025-11-04 17:00:27.690577+00	886	1	VENDA	360	310	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1719	SAIDA	20	Importação automática - NF: 0000004690	2025-11-04 17:00:27.690577+00	1007	1	VENDA	50	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1720	SAIDA	1	Importação automática - NF: 0000001215	2025-11-04 17:01:03.015785+00	1022	1	VENDA	1	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1721	SAIDA	40	Importação automática - NF: 0000001215	2025-11-04 17:01:03.015785+00	822	1	VENDA	52	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1722	SAIDA	20	Importação automática - NF: 0000001215	2025-11-04 17:01:03.015785+00	1006	1	VENDA	24	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1723	SAIDA	40	Importação automática - NF: 0000001215	2025-11-04 17:01:03.015785+00	874	1	VENDA	99	59	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1762	SAIDA	3	HOSP. VETERINÁRIO - NF 4693	2025-11-05 12:16:06.110203+00	1028	1	\N	31	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1763	SAIDA	12	\N	2025-11-05 12:55:24.919012+00	789	1	\N	34	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1764	ENTRADA	12	\N	2025-11-05 12:55:42.369729+00	792	1	\N	15	27	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1765	SAIDA	9	ajuste manual estoque	2025-11-05 12:56:37.942715+00	820	1	\N	48	39	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1766	SAIDA	9	ajuste manual estoque	2025-11-05 12:57:23.493863+00	824	1	\N	79	70	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1767	SAIDA	1	ajuste manual estoque	2025-11-05 12:57:58.803342+00	873	1	\N	15	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1768	SAIDA	19	ajuste manual estoque	2025-11-05 12:59:40.728686+00	874	1	\N	19	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1769	ENTRADA	2	ajuste manual estoque	2025-11-05 13:01:43.037288+00	876	1	\N	3	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1770	SAIDA	2	ajuste manual estoque	2025-11-05 13:06:47.793309+00	964	1	\N	20	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1771	SAIDA	15	ajuste manual estoque	2025-11-05 13:10:37.309212+00	966	1	\N	40	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1772	SAIDA	1	ajuste manual estoque	2025-11-05 13:11:28.418553+00	1008	1	\N	3	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1773	SAIDA	2	ajuste manual estoque	2025-11-05 13:12:01.408229+00	1006	1	\N	4	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1774	ENTRADA	1	ajuste manual estoque	2025-11-05 13:16:40.786126+00	1008	1	\N	2	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1775	SAIDA	2	ajuste manual estoque	2025-11-05 13:17:09.242961+00	1007	1	\N	30	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1776	ENTRADA	1	ajuste manual estoque	2025-11-05 13:18:36.642777+00	904	1	\N	11	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1777	SAIDA	6	ajuste manual estoque	2025-11-05 13:19:06.990302+00	906	1	\N	9	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1778	SAIDA	91	ajuste	2025-11-05 13:19:22.240037+00	940	3	\N	172	81	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1779	SAIDA	15	ajuste manual estoque	2025-11-05 13:21:39.386817+00	901	1	\N	15	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1780	ENTRADA	7	\N	2025-11-05 13:22:49.006074+00	902	3	\N	10	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1781	SAIDA	1	ajuste manual estoque	2025-11-05 13:25:20.49669+00	1026	1	\N	12	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1782	SAIDA	6	ajuste manual estoque	2025-11-05 13:26:50.879967+00	1030	1	\N	43	37	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1783	ENTRADA	1	ajuste manual estoque	2025-11-05 13:27:08.687138+00	1031	1	\N	2	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1784	SAIDA	4	ajuste manual estoque	2025-11-05 13:29:57.20392+00	1036	1	\N	47	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1785	SAIDA	1	ajuste manual estoque	2025-11-05 13:32:28.729287+00	863	1	\N	12	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1786	SAIDA	4	ajuste manual estoque	2025-11-05 13:34:51.991111+00	870	1	\N	15	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1787	SAIDA	6	ajuste manual (conferência inventário)	2025-11-05 13:39:37.338121+00	856	1	\N	11	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1788	SAIDA	1	ajuste manual (conferência inventário)	2025-11-05 13:40:01.609321+00	1025	1	\N	102	101	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1789	SAIDA	3	ajuste manual (conferência inventário)	2025-11-05 13:40:31.360555+00	918	1	\N	21	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1790	ENTRADA	1	ajuste manual (conferência inventário)	2025-11-05 13:40:40.736101+00	918	1	\N	18	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1791	ENTRADA	4	ajuste manual (conferência inventário)	2025-11-05 13:40:57.676612+00	919	1	\N	9	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1792	ENTRADA	4	ajuste manual (conferência inventário)	2025-11-05 13:41:45.893572+00	946	1	\N	0	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1793	SAIDA	1	ajuste manual (conferência inventário)	2025-11-05 13:43:12.534191+00	1010	1	\N	9	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1794	SAIDA	1	ajuste manual (conferência inventário)	2025-11-05 13:43:50.194954+00	1012	1	\N	8	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1795	SAIDA	1	ajuste manual (conferência inventário)	2025-11-05 13:44:07.039509+00	1013	1	\N	8	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1796	SAIDA	3	\N	2025-11-05 13:44:35.783316+00	1014	1	\N	7	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1797	SAIDA	3	ajuste manual (conferência inventário)	2025-11-05 13:45:20.98632+00	1015	1	\N	45	42	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1798	SAIDA	3	ajuste manual (conferência inventário)	2025-11-05 13:45:48.757796+00	1016	1	\N	45	42	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1799	SAIDA	1	ajuste manual (conferência inventário)	2025-11-05 13:47:01.940593+00	1017	1	\N	1	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1800	ENTRADA	1	ajuste manual (conferência inventário)	2025-11-05 13:47:26.8539+00	1018	1	\N	0	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1801	SAIDA	1	ajuste manual (conferência inventário)	2025-11-05 13:47:43.300839+00	1021	1	\N	5	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1802	SAIDA	3	ajuste manual (conferência inventário)	2025-11-05 13:49:15.43564+00	1020	1	\N	3	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1803	ENTRADA	3	ajuste manual (conferência inventário)	2025-11-05 13:50:56.811197+00	963	1	\N	12	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1804	SAIDA	4	ajuste manual (conferência inventário)	2025-11-05 13:51:26.77928+00	860	1	\N	21	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1805	ENTRADA	1	ajuste manual (inventário)	2025-11-07 01:29:58.242986+00	997	1	\N	45	46	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1806	SAIDA	25	ajuste manual (inventário)	2025-11-07 01:35:55.400761+00	1002	1	\N	67	42	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1807	SAIDA	1	ajuste manual (inventário)	2025-11-07 01:38:22.971243+00	990	1	\N	44	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1808	ENTRADA	3	ajuste manual (inventário)	2025-11-07 01:38:52.27342+00	991	1	\N	34	37	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1809	ENTRADA	5	ajuste manual (inventário)	2025-11-07 01:39:23.418798+00	992	1	\N	19	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1810	SAIDA	9	ajuste manual (inventário)	2025-11-07 01:39:51.666323+00	993	1	\N	17	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1811	SAIDA	9	ajuste manual (inventário)	2025-11-07 01:40:32.71634+00	995	1	\N	15	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1812	SAIDA	19	ajuste manual (inventário)	2025-11-07 01:41:13.180465+00	996	1	\N	47	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1813	ENTRADA	7	ajuste manual (inventário)	2025-11-07 01:45:33.500899+00	998	1	\N	21	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1814	ENTRADA	9	ajuste manual (inventário)	2025-11-07 01:46:06.385513+00	999	1	\N	9	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1815	ENTRADA	5	ajuste manual (inventário)	2025-11-07 01:46:30.574797+00	1000	1	\N	20	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1816	ENTRADA	7	ajuste manual (inventário)	2025-11-07 01:48:05.114716+00	988	1	\N	3	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1817	ENTRADA	1	ajuste manual (inventário)	2025-11-07 01:48:54.875597+00	985	1	\N	20	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1818	ENTRADA	11	ajuste manual (inventário)	2025-11-07 01:49:16.023262+00	987	1	\N	6	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1819	SAIDA	4	ajuste manual (inventário)	2025-11-07 01:51:18.42845+00	982	1	\N	23	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1820	ENTRADA	5	ajuste manual (inventário)	2025-11-07 01:52:03.733841+00	981	1	\N	15	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1821	SAIDA	19	ajuste manual (inventário)	2025-11-07 01:52:59.831638+00	1003	1	\N	32	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1822	ENTRADA	4	ajuste manual (inventário)	2025-11-07 01:53:25.700178+00	986	1	\N	16	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1823	SAIDA	2	Importação automática - NF: 0000004703	2025-11-07 01:58:58.318629+00	978	1	VENDA	8	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1824	SAIDA	1	Importação automática - NF: 0000001226	2025-11-07 02:02:08.540721+00	793	1	VENDA	9	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1825	SAIDA	1	Importação automática - NF: 0000001226	2025-11-07 02:02:08.540721+00	863	1	VENDA	11	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1826	SAIDA	1	Importação automática - NF: 0000001226	2025-11-07 02:02:08.540721+00	863	1	VENDA	10	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1830	SAIDA	3	COLEGIO EDUCALLIS - NF 1219.PDF	2025-11-07 02:18:13.205508+00	856	7	\N	5	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1837	SAIDA	8	CIRCUS - NF 4704.PDF	2025-11-07 02:23:28.11241+00	833	7	\N	21	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2847	SAIDA	11	\N	2026-01-14 12:22:03.082264+00	846	3	\N	560	549	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2849	ENTRADA	31	\N	2026-01-14 12:22:29.236794+00	847	3	\N	137	168	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3079	ENTRADA	60	\N	2026-01-28 11:07:45.738252+00	934	3	\N	0	60	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
1827	SAIDA	2	Importação automática - NF: 0000001224	2025-11-07 02:10:02.523286+00	952	7	VENDA	10	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1828	SAIDA	1	Importação automática - NF: 0000001224	2025-11-07 02:10:02.523286+00	1015	7	VENDA	42	41	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1829	SAIDA	1	Importação automática - NF: 0000001224	2025-11-07 02:10:02.523286+00	911	7	VENDA	6	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1831	SAIDA	1	Importação automática - NF: 0000001219	2025-11-07 02:18:58.011548+00	918	7	VENDA	19	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1832	SAIDA	1	Importação automática - NF: 0000001219	2025-11-07 02:18:58.011548+00	1016	7	VENDA	42	41	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1833	SAIDA	1	Importação automática - NF: 0000001219	2025-11-07 02:18:58.011548+00	1015	7	VENDA	41	40	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1834	SAIDA	4	Importação automática - NF: 0000004704	2025-11-07 02:21:06.240514+00	834	7	VENDA	10	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1835	SAIDA	4	Importação automática - NF: 0000004704	2025-11-07 02:21:06.240514+00	835	7	VENDA	21	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1836	ENTRADA	4	CIRCUS - NF 4704.PDF	2025-11-07 02:22:04.165224+00	833	7	\N	17	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1838	SAIDA	2	Importação automática - NF: 0000004702	2025-11-07 02:24:29.556056+00	978	7	VENDA	6	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1839	SAIDA	22	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	1002	7	VENDA	42	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1840	SAIDA	2	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	918	7	VENDA	18	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1841	SAIDA	2	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	908	7	VENDA	5	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1842	SAIDA	5	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	976	7	VENDA	39	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1843	SAIDA	20	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	925	7	VENDA	539	519	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1844	SAIDA	3	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	920	7	VENDA	24	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1845	SAIDA	5	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	824	7	VENDA	70	65	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1846	SAIDA	6	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	957	7	VENDA	9	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1847	SAIDA	6	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	958	7	VENDA	19	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1848	SAIDA	4	Importação automática - NF: 0000001222	2025-11-07 02:28:21.196087+00	959	7	VENDA	26	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1849	SAIDA	1	1224	2025-11-07 11:57:01.763808+00	873	3	\N	14	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1850	SAIDA	22	Importação automática - NF: 0000001227	2025-11-07 13:20:20.761907+00	789	1	VENDA	22	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1851	ENTRADA	7	127.910	2025-11-10 13:45:02.287298+00	866	3	\N	0	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1852	SAIDA	2	\N	2025-11-10 14:00:45.851026+00	1062	3	\N	11	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1853	ENTRADA	72	MIX JESUS	2025-11-11 11:28:44.535454+00	788	3	\N	36	108	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1854	SAIDA	208	\N	2025-11-11 11:28:57.597556+00	825	3	\N	208	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1855	ENTRADA	48	MIX JESUS	2025-11-11 11:29:17.372061+00	825	3	\N	0	48	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1856	ENTRADA	144	MIX JESUS	2025-11-11 11:29:34.706556+00	823	3	\N	0	144	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1857	SAIDA	2	Importação automática - NF: 0000001229	2025-11-11 14:16:10.212182+00	866	3	VENDA	7	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1858	ENTRADA	8	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	789	1	COMPRA	0	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1859	ENTRADA	12	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	792	1	COMPRA	27	39	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1860	ENTRADA	12	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	820	1	COMPRA	39	51	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1861	ENTRADA	12	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	822	1	COMPRA	10	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1862	ENTRADA	24	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	824	1	COMPRA	65	89	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1863	ENTRADA	12	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	873	1	COMPRA	13	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1864	ENTRADA	64	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	874	1	COMPRA	0	64	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1865	ENTRADA	5	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	876	1	COMPRA	5	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1866	ENTRADA	16	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	966	1	COMPRA	25	41	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1867	ENTRADA	8	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	1033	1	COMPRA	5	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1868	ENTRADA	11	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	1006	1	COMPRA	2	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1869	ENTRADA	4	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	1048	1	COMPRA	3	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1870	ENTRADA	5	Importação automática - NF: 0	2025-11-11 14:32:54.829941+00	1024	1	COMPRA	2	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1871	SAIDA	30	Importação automática - NF: 0000004706	2025-11-11 14:33:53.744534+00	1025	3	VENDA	101	71	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1872	SAIDA	60	Importação automática - NF: 0000004706	2025-11-11 14:33:53.744534+00	1040	3	VENDA	126	66	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1873	SAIDA	20	Importação automática - NF: 0000004706	2025-11-11 14:33:53.744534+00	1036	3	VENDA	43	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1874	SAIDA	36	Importação automática - NF: 0000004706	2025-11-11 14:33:53.744534+00	787	3	VENDA	90	54	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1875	SAIDA	3	Importação automática - NF: 0000004706	2025-11-11 14:33:53.744534+00	858	3	VENDA	8	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1876	SAIDA	2	Importação automática - NF: 0000004707	2025-11-11 14:34:21.277512+00	813	3	VENDA	14	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1877	SAIDA	6	Importação automática - NF: 0000004709	2025-11-11 14:35:05.600929+00	796	3	VENDA	13	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1878	SAIDA	6	Importação automática - NF: 0000004709	2025-11-11 14:35:05.600929+00	793	3	VENDA	8	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1879	SAIDA	6	Importação automática - NF: 0000004709	2025-11-11 14:35:05.600929+00	863	3	VENDA	9	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1880	ENTRADA	42	NOVO PRODUTO	2025-11-11 14:36:19.590758+00	1070	1	\N	0	42	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1881	ENTRADA	30	\N	2025-11-11 14:37:43.962825+00	990	3	\N	43	73	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1882	ENTRADA	50	\N	2025-11-11 14:38:28.815858+00	1002	3	\N	20	70	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1883	ENTRADA	20	\N	2025-11-11 14:38:49.078126+00	1001	3	\N	10	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1884	ENTRADA	10	\N	2025-11-11 14:39:30.405713+00	996	3	\N	28	38	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1885	ENTRADA	7	ajuste manual entrada girassol	2025-11-11 14:41:39.412232+00	1024	1	\N	7	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1886	SAIDA	1	pendência - PJ	2025-11-11 14:42:10.556833+00	874	3	\N	64	63	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1887	ENTRADA	11	entrada girassol manual	2025-11-11 14:43:39.526591+00	876	1	\N	10	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1888	SAIDA	1	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	824	3	VENDA	89	88	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1889	SAIDA	1	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	951	3	VENDA	12	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1890	SAIDA	2	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	934	3	VENDA	3	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1891	SAIDA	1	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	993	3	VENDA	8	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1892	SAIDA	1	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	1002	3	VENDA	70	69	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1893	SAIDA	6	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	839	3	VENDA	188	182	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1894	SAIDA	4	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	925	3	VENDA	519	515	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1895	SAIDA	1	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	1015	3	VENDA	40	39	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1896	SAIDA	25	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	818	3	VENDA	111	86	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1897	SAIDA	5	Importação automática - NF: 0000004711	2025-11-11 14:44:46.822367+00	941	3	VENDA	100	95	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1898	ENTRADA	12	entada girassol	2025-11-11 14:44:51.862086+00	824	1	\N	88	100	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1899	SAIDA	5	Importação automática - NF: 0000004710	2025-11-11 14:45:18.219864+00	874	3	VENDA	63	58	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1900	SAIDA	2	Importação automática - NF: 0000004710	2025-11-11 14:45:18.219864+00	966	3	VENDA	41	39	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1901	SAIDA	24	Importação automática - NF: 0000001230	2025-11-11 14:48:37.147767+00	873	3	VENDA	25	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1902	SAIDA	12	Importação automática - NF: 0000001230	2025-11-11 14:48:37.147767+00	820	3	VENDA	51	39	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1903	SAIDA	8	Importação automática - NF: 0000001230	2025-11-11 14:48:37.147767+00	966	3	VENDA	39	31	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1913	ENTRADA	6	\N	2025-11-11 17:47:04.81276+00	1071	3	\N	0	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1904	SAIDA	4	Importação automática - NF: 0000001230	2025-11-11 14:48:37.147767+00	1006	3	VENDA	13	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1905	SAIDA	12	Importação automática - NF: 0000001228	2025-11-11 14:50:34.227002+00	874	3	VENDA	58	46	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1906	SAIDA	6	Importação automática - NF: 0000001228	2025-11-11 14:50:34.227002+00	1030	3	VENDA	37	31	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1907	SAIDA	2	Importação automática - NF: 0000001228	2025-11-11 14:50:34.227002+00	876	3	VENDA	21	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1908	SAIDA	3	Importação automática - NF: 0000001228	2025-11-11 14:50:34.227002+00	822	3	VENDA	22	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1909	SAIDA	1	Importação automática - NF: 0000004712	2025-11-11 14:55:52.094612+00	990	3	VENDA	73	72	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1910	SAIDA	1	Importação automática - NF: 0000004712	2025-11-11 14:55:52.094612+00	1035	3	VENDA	23	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1911	SAIDA	1	Importação automática - NF: 0000004712	2025-11-11 14:55:52.094612+00	1016	3	VENDA	41	40	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1912	SAIDA	15	Importação automática - NF: 0000004712	2025-11-11 14:55:52.094612+00	941	3	VENDA	95	80	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2848	SAIDA	10	\N	2026-01-14 12:22:14.000293+00	843	3	\N	510	500	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2850	SAIDA	170	\N	2026-01-14 12:22:51.660654+00	844	3	\N	170	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3080	ENTRADA	11	NF None - Processamento automático	2026-01-29 18:42:00.537752+00	792	3	\N	72	83	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3102	SAIDA	2	NF 0000004857 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:02:06.260985+00	1001	3	\N	32	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3106	SAIDA	10	NF 0000004860 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:02:33.409425+00	996	3	\N	24	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1914	SAIDA	1	\N	2025-11-11 18:23:16.167471+00	796	3	\N	7	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1915	SAIDA	12	Importação automática - NF: 0000004714	2025-11-12 17:35:11.395637+00	839	3	VENDA	182	170	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1916	SAIDA	10	Importação automática - NF: 0000004714	2025-11-12 17:35:11.395637+00	925	3	VENDA	515	505	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1917	SAIDA	6	Importação automática - NF: 0000004714	2025-11-12 17:35:11.395637+00	823	3	VENDA	144	138	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1918	SAIDA	2	Importação automática - NF: 0000004714	2025-11-12 17:35:11.395637+00	991	3	VENDA	37	35	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1919	SAIDA	1	Importação automática - NF: 0000004714	2025-11-12 17:35:11.395637+00	985	3	VENDA	21	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1920	SAIDA	3	Importação automática - NF: 0000004714	2025-11-12 17:35:11.395637+00	1002	3	VENDA	69	66	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1921	SAIDA	1	Importação automática - NF: 0000004714	2025-11-12 17:35:11.395637+00	989	3	VENDA	16	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1922	SAIDA	30	Importação automática - NF: 0000004714	2025-11-12 17:35:11.395637+00	940	3	VENDA	81	51	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1923	SAIDA	10	4714	2025-11-12 17:35:37.491823+00	846	3	\N	570	560	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1924	SAIDA	60	Importação automática - NF: 0000004715	2025-11-12 17:38:21.71422+00	936	3	VENDA	215	155	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1925	SAIDA	3	Importação automática - NF: 0000004715	2025-11-12 17:38:21.71422+00	938	3	VENDA	12	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1926	SAIDA	6	Importação automática - NF: 0000004715	2025-11-12 17:38:21.71422+00	935	3	VENDA	17	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1927	SAIDA	5	Importação automática - NF: 0000004715	2025-11-12 17:38:21.71422+00	1002	3	VENDA	66	61	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1928	SAIDA	2	Importação automática - NF: 0000004715	2025-11-12 17:38:21.71422+00	1033	3	VENDA	13	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1929	SAIDA	1	Orçamento #26 confirmado	2025-11-12 22:30:52.033122+00	789	8	VENDA	8	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1930	ENTRADA	1	\N	2025-11-12 22:31:39.41903+00	789	8	\N	7	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1931	SAIDA	7	ajuste	2025-11-14 17:48:23.794897+00	935	3	\N	11	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1932	SAIDA	105	ajuste	2025-11-14 17:48:36.268758+00	936	3	\N	155	50	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1933	SAIDA	7	ajuste	2025-11-14 17:48:50.011519+00	938	3	\N	9	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1934	SAIDA	2	Importação automática - NF: 0000004713	2025-11-14 18:49:32.889701+00	965	3	VENDA	2	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1935	SAIDA	2	4713	2025-11-14 18:49:48.936367+00	962	3	\N	2	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1936	SAIDA	1	Importação automática - NF: 0000004717	2025-11-14 18:51:23.494702+00	820	3	VENDA	39	38	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1937	SAIDA	5	Importação automática - NF: 0000004717	2025-11-14 18:51:23.494702+00	874	3	VENDA	46	41	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1938	SAIDA	3	Importação automática - NF: 0000004717	2025-11-14 18:51:23.494702+00	824	3	VENDA	100	97	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1939	SAIDA	1	Importação automática - NF: 0000004717	2025-11-14 18:51:23.494702+00	966	3	VENDA	31	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1940	SAIDA	1	Importação automática - NF: 0000004717	2025-11-14 18:51:23.494702+00	1062	3	VENDA	9	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1941	SAIDA	1	Importação automática - NF: 0000004717	2025-11-14 18:51:23.494702+00	1033	3	VENDA	11	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1942	SAIDA	5	Importação automática - NF: 0000004717	2025-11-14 18:51:23.494702+00	1030	3	VENDA	31	26	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1943	SAIDA	2	Importação automática - NF: 0000004717	2025-11-14 18:51:23.494702+00	1006	3	VENDA	9	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1944	SAIDA	2	Importação automática - NF: 0000001232	2025-11-14 18:52:05.372997+00	1024	3	VENDA	14	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1945	SAIDA	10	Importação automática - NF: 0000001232	2025-11-14 18:52:05.372997+00	874	3	VENDA	41	31	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1946	SAIDA	3	4718 - AINDA DEVENDO 2 UNID.	2025-11-14 18:52:35.878182+00	908	3	\N	3	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1947	SAIDA	2	Importação automática - NF: 0000004719	2025-11-14 18:53:08.258195+00	824	3	VENDA	97	95	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1948	SAIDA	2	Importação automática - NF: 0000004719	2025-11-14 18:53:08.258195+00	874	3	VENDA	31	29	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1949	ENTRADA	10	\N	2025-11-17 19:32:59.683588+00	935	3	\N	4	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1950	ENTRADA	10	\N	2025-11-17 19:33:03.726881+00	938	3	\N	2	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1951	ENTRADA	300	\N	2025-11-17 19:33:10.73171+00	936	3	\N	50	350	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1952	ENTRADA	4	compra	2025-11-18 12:07:06.865395+00	792	3	\N	39	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1953	ENTRADA	20	compra	2025-11-18 12:07:26.981743+00	820	3	\N	38	58	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1954	ENTRADA	32	compra	2025-11-18 12:07:46.225885+00	822	3	\N	19	51	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1955	ENTRADA	100	compra	2025-11-18 12:08:23.215617+00	824	3	\N	95	195	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1956	ENTRADA	6	\N	2025-11-18 12:09:55.513083+00	853	3	\N	6	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1957	ENTRADA	8	\N	2025-11-18 12:10:05.918134+00	856	3	\N	2	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1958	ENTRADA	8	\N	2025-11-18 12:10:20.402825+00	903	3	\N	1	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1959	ENTRADA	4	\N	2025-11-18 12:10:36.4879+00	920	3	\N	21	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1960	ENTRADA	8	\N	2025-11-18 12:11:49.406736+00	946	3	\N	4	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1961	ENTRADA	12	\N	2025-11-18 12:12:11.869796+00	966	3	\N	30	42	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1962	ENTRADA	8	\N	2025-11-18 12:12:29.164838+00	1006	3	\N	7	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1963	ENTRADA	4	\N	2025-11-18 12:15:40.991748+00	1018	3	\N	1	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1964	ENTRADA	4	\N	2025-11-18 12:15:58.582901+00	1022	3	\N	0	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1965	ENTRADA	8	\N	2025-11-18 12:16:57.963836+00	978	3	\N	4	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1966	ENTRADA	4	\N	2025-11-18 12:17:09.801501+00	1048	3	\N	7	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1967	ENTRADA	4	\N	2025-11-18 12:18:15.218711+00	1076	3	\N	0	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1968	SAIDA	2	\N	2025-11-18 12:18:21.769339+00	1076	3	\N	4	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1969	SAIDA	4	Importação automática - NF: 0000001234	2025-11-18 14:15:06.319029+00	870	3	VENDA	11	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1970	SAIDA	2	Importação automática - NF: 0000001234	2025-11-18 14:15:06.319029+00	1015	3	VENDA	39	37	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1971	SAIDA	2	Importação automática - NF: 0000001234	2025-11-18 14:15:06.319029+00	1016	3	VENDA	40	38	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1972	SAIDA	1	Importação automática - NF: 0000001234	2025-11-18 14:15:06.319029+00	820	3	VENDA	58	57	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1973	SAIDA	1	Importação automática - NF: 0000001234	2025-11-18 14:15:06.319029+00	873	3	VENDA	1	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1974	SAIDA	2	Importação automática - NF: 0000001234	2025-11-18 14:15:06.319029+00	1048	3	VENDA	11	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1975	SAIDA	1	Importação automática - NF: 0000001234	2025-11-18 14:15:06.319029+00	1021	3	VENDA	4	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1976	SAIDA	2	Importação automática - NF: 0000001233	2025-11-18 14:16:06.857253+00	874	3	VENDA	29	27	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1977	SAIDA	2	Importação automática - NF: 0000001233	2025-11-18 14:16:06.857253+00	824	3	VENDA	195	193	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1978	SAIDA	1	Importação automática - NF: 0000001233	2025-11-18 14:16:06.857253+00	820	3	VENDA	57	56	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1979	SAIDA	1	Importação automática - NF: 0000001233	2025-11-18 14:16:06.857253+00	1006	3	VENDA	15	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1980	SAIDA	3	Importação automática - NF: 0000004720	2025-11-18 14:18:17.861371+00	996	3	VENDA	38	35	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1981	SAIDA	4	Importação automática - NF: 0000001235	2025-11-18 14:24:49.222417+00	874	3	VENDA	27	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1982	SAIDA	1	Importação automática - NF: 0000001235	2025-11-18 14:24:49.222417+00	918	3	VENDA	16	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1983	SAIDA	1	Importação automática - NF: 0000001235	2025-11-18 14:24:49.222417+00	920	3	VENDA	25	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1984	SAIDA	1	Importação automática - NF: 0000001235	2025-11-18 14:24:49.222417+00	824	3	VENDA	193	192	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1985	SAIDA	20	Importação automática - NF: 0000004722	2025-11-18 14:26:51.71173+00	824	3	VENDA	192	172	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1986	SAIDA	20	Importação automática - NF: 0000004722	2025-11-18 14:26:51.71173+00	874	3	VENDA	23	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1987	SAIDA	4	Importação automática - NF: 0000004722	2025-11-18 14:26:51.71173+00	1010	3	VENDA	8	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1988	SAIDA	4	Importação automática - NF: 0000004722	2025-11-18 14:26:51.71173+00	1013	3	VENDA	7	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1989	SAIDA	4	Importação automática - NF: 0000004722	2025-11-18 14:26:51.71173+00	1012	3	VENDA	7	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1990	SAIDA	12	Importação automática - NF: 0000004722	2025-11-18 14:26:51.71173+00	792	3	VENDA	43	31	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1991	SAIDA	42	Importação automática - NF: 0000004722	2025-11-18 14:26:51.71173+00	1070	3	VENDA	42	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1992	SAIDA	75	Importação automática - NF: 0000004721	2025-11-18 14:29:31.535443+00	941	3	VENDA	80	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1993	SAIDA	10	Importação automática - NF: 0000004721	2025-11-18 14:29:31.535443+00	931	3	VENDA	64	54	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1994	SAIDA	8	Importação automática - NF: 0000001236	2025-11-18 18:28:57.779852+00	966	3	VENDA	42	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1995	SAIDA	8	Importação automática - NF: 0000001236	2025-11-18 18:28:57.779852+00	820	3	VENDA	56	48	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1996	SAIDA	12	Importação automática - NF: 0000004724	2025-11-18 18:29:47.357852+00	787	3	VENDA	54	42	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1997	SAIDA	2	Importação automática - NF: 0000004724	2025-11-18 18:29:47.357852+00	874	3	VENDA	3	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1998	SAIDA	2	Importação automática - NF: 0000004724	2025-11-18 18:29:47.357852+00	966	3	VENDA	34	32	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
1999	SAIDA	8	\N	2025-11-18 18:30:38.371601+00	789	3	\N	8	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2000	SAIDA	12	\N	2025-11-18 18:34:10.851095+00	792	3	\N	31	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2001	SAIDA	12	\N	2025-11-18 18:34:59.351734+00	792	3	\N	19	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2002	ENTRADA	12	\N	2025-11-18 18:35:08.474527+00	792	3	\N	7	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2003	SAIDA	4	\N	2025-11-18 18:35:22.892695+00	820	3	\N	48	44	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2004	SAIDA	4	\N	2025-11-18 18:37:03.591151+00	822	3	\N	51	47	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2005	ENTRADA	8	\N	2025-11-18 18:37:11.912358+00	822	3	\N	47	55	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2006	SAIDA	1	\N	2025-11-18 18:37:39.263958+00	824	3	\N	172	171	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2007	SAIDA	1	\N	2025-11-18 18:37:56.499162+00	874	3	\N	1	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2008	SAIDA	2	\N	2025-11-18 18:38:15.815601+00	876	3	\N	19	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2009	ENTRADA	2	\N	2025-11-18 18:40:32.729702+00	964	3	\N	18	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2010	ENTRADA	1	\N	2025-11-18 18:41:45.193409+00	1006	3	\N	14	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2011	ENTRADA	2	\N	2025-11-18 18:42:07.768171+00	1007	3	\N	28	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2012	SAIDA	1	\N	2025-11-18 18:42:59.004348+00	904	3	\N	12	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2013	SAIDA	1	\N	2025-11-18 18:44:33.291696+00	1031	3	\N	3	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2014	SAIDA	7	\N	2025-11-18 18:45:00.2863+00	1036	3	\N	23	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2015	ENTRADA	14	\N	2025-11-18 18:45:16.147965+00	1035	3	\N	22	36	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2016	SAIDA	28	\N	2025-11-18 18:45:29.610345+00	1035	3	\N	36	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2017	ENTRADA	1	\N	2025-11-18 18:46:31.895709+00	863	3	\N	3	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2018	ENTRADA	2	\N	2025-11-18 18:47:06.682421+00	862	3	\N	26	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2019	SAIDA	1	\N	2025-11-18 18:47:41.516032+00	853	3	\N	12	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2020	SAIDA	3	\N	2025-11-18 18:48:01.890399+00	856	3	\N	10	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2021	SAIDA	57	\N	2025-11-18 18:50:30.591857+00	1025	3	\N	71	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2022	SAIDA	1	\N	2025-11-18 18:50:48.898453+00	919	3	\N	13	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2023	SAIDA	4	\N	2025-11-18 18:50:56.11498+00	920	3	\N	24	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2024	ENTRADA	4	\N	2025-11-18 18:51:48.28939+00	1013	3	\N	3	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2025	SAIDA	4	\N	2025-11-18 18:52:00.367089+00	1014	3	\N	4	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2026	SAIDA	2	\N	2025-11-18 18:52:23.116+00	1015	3	\N	37	35	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2027	SAIDA	2	\N	2025-11-18 18:52:37.202273+00	1016	3	\N	38	36	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2028	SAIDA	3	\N	2025-11-18 18:53:02.297211+00	963	3	\N	15	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2029	ENTRADA	2	\N	2025-11-18 18:53:15.299908+00	860	3	\N	17	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2030	SAIDA	3	Importação automática - NF: 0000001237	2025-11-19 13:55:53.775509+00	822	3	VENDA	55	52	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2031	SAIDA	4	Importação automática - NF: 0000001238	2025-11-19 13:56:49.490727+00	870	3	VENDA	7	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2032	SAIDA	2	Importação automática - NF: 0000001238	2025-11-19 13:56:49.490727+00	1015	3	VENDA	35	33	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2033	SAIDA	2	Importação automática - NF: 0000001238	2025-11-19 13:56:49.490727+00	1016	3	VENDA	36	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2034	SAIDA	12	Importação automática - NF: 0000004727	2025-11-19 18:39:38.50195+00	850	3	VENDA	158	146	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2035	SAIDA	10	Importação automática - NF: 0000004727	2025-11-19 18:39:38.50195+00	926	3	VENDA	379	369	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2036	SAIDA	10	Importação automática - NF: 0000004727	2025-11-19 18:39:38.50195+00	848	3	VENDA	536	526	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2037	SAIDA	15	Importação automática - NF: 0000004727	2025-11-19 18:39:38.50195+00	977	3	VENDA	158	143	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2038	SAIDA	8	Importação automática - NF: 0000004727	2025-11-19 18:39:38.50195+00	990	3	VENDA	72	64	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2039	SAIDA	1	Importação automática - NF: 0000004727	2025-11-19 18:39:38.50195+00	1046	3	VENDA	56	55	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2040	SAIDA	5	Importação automática - NF: 0000004727	2025-11-19 18:39:38.50195+00	976	3	VENDA	34	29	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2041	SAIDA	1	Importação automática - NF: 0000004727	2025-11-19 18:39:38.50195+00	921	3	VENDA	13	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2042	SAIDA	2	\N	2025-11-19 18:39:56.800017+00	827	3	\N	11	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2043	SAIDA	36	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	850	3	VENDA	146	110	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2044	SAIDA	15	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	926	3	VENDA	369	354	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2045	SAIDA	10	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	848	3	VENDA	526	516	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2046	SAIDA	5	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	868	3	VENDA	36	31	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2047	SAIDA	10	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	839	3	VENDA	170	160	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2048	SAIDA	30	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	977	3	VENDA	143	113	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2049	SAIDA	5	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	787	3	VENDA	42	37	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2050	SAIDA	8	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	1002	3	VENDA	61	53	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2051	SAIDA	12	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	990	3	VENDA	64	52	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2052	SAIDA	2	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	1046	3	VENDA	55	53	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2053	SAIDA	10	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	976	3	VENDA	29	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2054	SAIDA	2	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	827	3	VENDA	9	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2055	SAIDA	2	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	921	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2056	SAIDA	1	Importação automática - NF: 0000004726	2025-11-19 18:42:54.740947+00	902	3	VENDA	17	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2057	SAIDA	1	\N	2025-11-19 18:48:53.238787+00	1071	3	\N	6	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2058	SAIDA	8	1239	2025-11-19 18:49:11.948534+00	963	3	\N	12	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2059	ENTRADA	100	\N	2025-11-19 19:41:08.940857+00	941	3	\N	5	105	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2060	SAIDA	4		2025-11-21 01:34:27.621455+00	996	13	\N	35	31	CONFIRMADO	1	2025-11-21 02:04:42.707522+00	\N	CARREGAMENTO		{"produto_id": 996, "quantidade": 4.0, "tipo_movimentacao": "SAIDA", "motivo_movimentacao": "CARREGAMENTO", "observacao": null}	{"produto_id": 996, "quantidade": 4.0, "tipo_movimentacao": "SAIDA", "motivo_movimentacao": "CARREGAMENTO", "observacao": ""}	\N	f	\N	\N
2061	ENTRADA	4	teste de ajuste	2025-11-21 02:05:19.337487+00	996	1	\N	31	35	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2063	SAIDA	2	\N	2025-11-21 02:06:18.163896+00	789	13	\N	0	0	REJEITADO	1	2025-11-21 02:06:47.055159+00	teste\n	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2062	SAIDA	1	\N	2025-11-21 02:06:18.133067+00	861	13	\N	0	0	REJEITADO	1	2025-11-21 02:06:50.960851+00	teste	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2064	SAIDA	3	\N	2025-11-21 02:47:19.966705+00	797	13	\N	25	25	REJEITADO	1	2025-11-21 03:08:53.221452+00	teste	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2065	SAIDA	2		2025-11-21 02:47:19.972882+00	789	13	\N	0	0	REJEITADO	1	2025-11-21 03:08:46.690773+00	teste	CARREGAMENTO		{"produto_id": 789, "quantidade": 2.0, "tipo_movimentacao": "SAIDA", "motivo_movimentacao": "CARREGAMENTO", "observacao": null}	{"produto_id": 789, "quantidade": 2.0, "tipo_movimentacao": "SAIDA", "motivo_movimentacao": "CARREGAMENTO", "observacao": ""}	\N	f	\N	\N
2066	ENTRADA	197	Entrada de produtos GIRASSOL (total 220-16-7)	2025-11-21 13:32:48.103496+00	874	1	\N	0	197	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2067	ENTRADA	38	Entrada GIRASSOL	2025-11-21 13:34:04.915184+00	789	1	\N	0	38	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2068	ENTRADA	4	Entrada de produtos GIRASSOL NF 128321	2025-11-21 13:35:12.814173+00	918	1	\N	15	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2069	ENTRADA	150	\N	2025-11-21 18:47:30.750083+00	818	3	\N	86	236	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2070	ENTRADA	150	\N	2025-11-21 18:47:36.621812+00	817	3	\N	8	158	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2071	SAIDA	2	Importação automática - NF: 0000001244	2025-11-25 13:22:27.378274+00	866	3	VENDA	5	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2072	SAIDA	1	4732	2025-11-25 13:23:41.718559+00	824	3	\N	171	170	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2073	SAIDA	1	4732	2025-11-25 13:23:58.792808+00	1015	3	\N	33	32	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2074	SAIDA	2	4731	2025-11-25 13:24:21.177343+00	824	3	\N	170	168	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2075	SAIDA	2	4731	2025-11-25 13:24:35.42226+00	874	3	\N	197	195	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2076	SAIDA	4	8 pendentes - 4733	2025-11-25 13:24:58.796844+00	963	3	\N	4	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2077	SAIDA	10	4738	2025-11-25 13:26:31.215704+00	941	3	\N	105	95	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2078	SAIDA	15	4730	2025-11-25 13:30:52.838306+00	1007	3	\N	30	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2079	SAIDA	2	4730	2025-11-25 13:31:02.916813+00	964	3	\N	20	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2080	SAIDA	4	4728	2025-11-25 13:31:21.691311+00	966	3	\N	32	28	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2081	SAIDA	4	4728	2025-11-25 13:31:50.129037+00	874	3	\N	195	191	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2082	SAIDA	2	4728	2025-11-25 13:32:01.825597+00	824	3	\N	168	166	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2083	SAIDA	70	4737	2025-11-25 13:32:29.815933+00	886	3	\N	310	240	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2084	SAIDA	3	4736	2025-11-25 13:32:54.455868+00	941	3	\N	95	92	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2085	SAIDA	3	4736	2025-11-25 13:33:08.255752+00	931	3	\N	54	51	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2086	SAIDA	1	4736	2025-11-25 13:33:24.204916+00	1003	3	\N	13	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2087	SAIDA	1	4736	2025-11-25 13:33:37.240124+00	1033	3	\N	10	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2088	SAIDA	8	4735	2025-11-25 13:35:39.593154+00	941	3	\N	92	84	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2089	SAIDA	12	4735	2025-11-25 13:35:55.493748+00	788	3	\N	108	96	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2090	SAIDA	3	\N	2025-11-25 13:36:12.219082+00	977	3	\N	113	110	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2091	SAIDA	2	\N	2025-11-25 13:36:23.878913+00	839	3	\N	160	158	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2092	SAIDA	3	\N	2025-11-25 13:36:38.220199+00	825	3	\N	48	45	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2093	SAIDA	1	\N	2025-11-25 13:36:48.448464+00	1035	3	\N	8	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2094	SAIDA	2	\N	2025-11-25 13:37:02.994333+00	802	3	\N	42	40	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2095	SAIDA	5	\N	2025-11-25 13:37:18.915856+00	920	3	\N	20	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2096	SAIDA	26	\N	2025-11-25 13:37:31.796706+00	789	3	\N	38	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2097	SAIDA	12	\N	2025-11-25 13:37:52.31295+00	874	3	\N	191	179	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2098	SAIDA	4	Importação automática - NF: 0000004725	2025-11-25 13:48:01.154838+00	874	1	VENDA	179	175	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2099	SAIDA	4	Importação automática - NF: 0000004725	2025-11-25 13:48:01.154838+00	966	1	VENDA	28	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2100	SAIDA	2	Importação automática - NF: 0000004702 | Código sincronizado (PROD192 -> 52) | Produto NF: SABONETE DESENGRAXANTE MICRO ESFERA BB 5L	2025-11-25 14:36:39.662167+00	978	1	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD192\\"}"	"{\\"codigo\\": \\"52\\"}"	\N	f	\N	\N
2101	ENTRADA	2	\N	2025-11-25 14:37:30.170209+00	978	1	\N	10	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2102	SAIDA	1	RENATO	2025-11-26 14:17:00.64643+00	918	3	\N	19	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2103	SAIDA	1	RENATO	2025-11-26 14:17:17.162366+00	1038	3	\N	33	32	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2104	SAIDA	1	RENATO	2025-11-26 14:17:37.445842+00	808	3	\N	10	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2105	SAIDA	5	RENATO	2025-11-26 14:17:54.415424+00	848	3	\N	516	511	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2106	SAIDA	60	Importação automática - NF: 0000004741 | Código sincronizado (PROD150 -> 262) | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2025-11-26 14:21:34.22741+00	936	3	VENDA	350	290	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD150\\"}"	"{\\"codigo\\": \\"262\\"}"	\N	f	\N	\N
2107	SAIDA	2	Importação automática - NF: 0000004741 | Código sincronizado (PROD152 -> 710) | Produto NF: PAPEL TOALHA BOBINA MG BRANCO 150MTS	2025-11-26 14:21:34.22741+00	938	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD152\\"}"	"{\\"codigo\\": \\"710\\"}"	\N	f	\N	\N
2108	SAIDA	2	Importação automática - NF: 0000004741 | Código sincronizado (PROD149 -> 513) | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2025-11-26 14:21:34.22741+00	935	3	VENDA	14	12	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD149\\"}"	"{\\"codigo\\": \\"513\\"}"	\N	f	\N	\N
2109	SAIDA	3	Importação automática - NF: 0000004741 | Código sincronizado (PROD210 -> 394) | Produto NF: S B A E C TA O P P L / A L S I T X I O C 90X100X0,08 - PRETO 200LT	2025-11-26 14:21:34.22741+00	996	3	VENDA	35	32	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD210\\"}"	"{\\"codigo\\": \\"394\\"}"	\N	f	\N	\N
2110	SAIDA	3	Importação automática - NF: 0000004741 | Código sincronizado (PROD206 -> 726) | Produto NF: S P A LA C S O T P IC / LIXO 75X90X0,08 - PRETO 100LT BETA	2025-11-26 14:21:34.22741+00	992	3	VENDA	24	21	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD206\\"}"	"{\\"codigo\\": \\"726\\"}"	\N	f	\N	\N
2111	SAIDA	2	MIRIAN	2025-11-26 14:28:33.469966+00	943	3	\N	90	88	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2112	SAIDA	2	MIRIAN	2025-11-26 14:28:48.77652+00	839	3	\N	158	156	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2113	SAIDA	5	USO	2025-11-26 14:28:57.574851+00	839	3	\N	156	151	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2114	SAIDA	1	MIRIAN	2025-11-26 14:30:40.927128+00	976	3	\N	19	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2115	SAIDA	1	MIRIAN	2025-11-26 14:34:22.91415+00	804	3	\N	94	93	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2116	SAIDA	1	MIRIAN	2025-11-26 14:34:34.726528+00	803	3	\N	48	47	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2117	SAIDA	1	MIRIAN	2025-11-26 14:34:46.152333+00	788	3	\N	96	95	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2118	ENTRADA	8	Importação automática - NF: 0 | Código sincronizado (PROD007 -> 1031305) | Produto NF: ALVITEC PE BB 5KG	2025-11-26 19:11:03.264452+00	793	3	COMPRA	2	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD007\\"}"	"{\\"codigo\\": \\"1031305\\"}"	\N	f	\N	\N
2119	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD010 -> 1031605) | Produto NF: AMACITEC PRIMAVERA BB 5L	2025-11-26 19:11:03.264452+00	796	3	COMPRA	6	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD010\\"}"	"{\\"codigo\\": \\"1031605\\"}"	\N	f	\N	\N
2120	ENTRADA	24	Importação automática - NF: 0 | Código sincronizado (PROD034 -> 1021005) | Produto NF: DESINCROST BB5L	2025-11-26 19:11:03.264452+00	820	3	COMPRA	44	68	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD034\\"}"	"{\\"codigo\\": \\"1021005\\"}"	\N	f	\N	\N
2121	ENTRADA	16	Importação automática - NF: 0 | Código sincronizado (PROD036 -> 1034605) | Produto NF: DESINCROST GEL BB5L	2025-11-26 19:11:03.264452+00	822	3	COMPRA	52	68	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD036\\"}"	"{\\"codigo\\": \\"1034605\\"}"	\N	f	\N	\N
2122	ENTRADA	20	Importação automática - NF: 0 | Código sincronizado (PROD038 -> 1001405) | Produto NF: DETERGENTE CLORADO BB 5L	2025-11-26 19:11:03.264452+00	824	3	COMPRA	166	186	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD038\\"}"	"{\\"codigo\\": \\"1001405\\"}"	\N	f	\N	\N
2123	ENTRADA	6	Importação automática - NF: 0 | Código sincronizado (PROD067 -> 1018110) | Produto NF: GEL ANTISSEPTICO BB1L PET	2025-11-26 19:11:03.264452+00	853	3	COMPRA	11	17	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD067\\"}"	"{\\"codigo\\": \\"1018110\\"}"	\N	f	\N	\N
2124	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD070 -> 1018105) | Produto NF: GEL ANTISSEPTICO BB5L	2025-11-26 19:11:03.264452+00	856	3	COMPRA	7	11	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD070\\"}"	"{\\"codigo\\": \\"1018105\\"}"	\N	f	\N	\N
2125	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD077 -> 1031505) | Produto NF: LAVPRO BB 5L	2025-11-26 19:11:03.264452+00	863	3	COMPRA	4	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD077\\"}"	"{\\"codigo\\": \\"1031505\\"}"	\N	f	\N	\N
2126	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD084 -> 1030205) | Produto NF: LIMPA PORCELANATO BB5L	2025-11-26 19:11:03.264452+00	870	3	COMPRA	3	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD084\\"}"	"{\\"codigo\\": \\"1030205\\"}"	\N	f	\N	\N
2127	ENTRADA	28	Importação automática - NF: 0 | Código sincronizado (PROD087 -> 1003905) | Produto NF: LIMPAX BB 5L	2025-11-26 19:11:03.264452+00	873	3	COMPRA	0	28	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD087\\"}"	"{\\"codigo\\": \\"1003905\\"}"	\N	f	\N	\N
2220	SAIDA	20	Importação automática - NF: 0000001245 | Produto NF: LIMPAX DX BB5L	2025-12-01 17:57:01.79787+00	874	3	VENDA	176	156	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2128	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD088 -> 1033005) | Produto NF: LIMPAX DX BB5L	2025-11-26 19:11:03.264452+00	874	3	COMPRA	175	179	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD088\\"}"	"{\\"codigo\\": \\"1033005\\"}"	\N	f	\N	\N
2129	ENTRADA	16	Importação automática - NF: 0 | Código sincronizado (PROD133 -> 1027305) | Produto NF: OXIPRO NATURAL BB5L	2025-11-26 19:11:03.264452+00	919	3	COMPRA	12	28	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD133\\"}"	"{\\"codigo\\": \\"1027305\\"}"	\N	f	\N	\N
2130	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD247 -> 1025805) | Produto NF: PRAXI SABON ESPUMA ANDIROBA 5L	2025-11-26 19:11:03.264452+00	1033	3	COMPRA	9	13	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD247\\"}"	"{\\"codigo\\": \\"1025805\\"}"	\N	f	\N	\N
2131	ENTRADA	12	Importação automática - NF: 0 | Código sincronizado (PROD180 -> 1023705) | Produto NF: REMOX BB5L	2025-11-26 19:11:03.264452+00	966	3	COMPRA	24	36	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD180\\"}"	"{\\"codigo\\": \\"1023705\\"}"	\N	f	\N	\N
2132	ENTRADA	16	Importação automática - NF: 0 | Código sincronizado (PROD220 -> 1027105) | Produto NF: SANICLOR BB5L	2025-11-26 19:11:03.264452+00	1006	3	COMPRA	15	31	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD220\\"}"	"{\\"codigo\\": \\"1027105\\"}"	\N	f	\N	\N
2133	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD221 -> 1034322) | Produto NF: SANICLOR DT BB 20L	2025-11-26 19:11:03.264452+00	1007	3	COMPRA	15	19	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD221\\"}"	"{\\"codigo\\": \\"1034322\\"}"	\N	f	\N	\N
2134	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (52 -> 1005705) | Produto NF: SUAVITEX DX MICRO ESF BB 5L	2025-11-26 19:11:03.264452+00	978	3	COMPRA	12	16	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"52\\"}"	"{\\"codigo\\": \\"1005705\\"}"	\N	f	\N	\N
2135	ENTRADA	6	Importação automática - NF: 0 | Código sincronizado (PROD244 -> 1029355) | Produto NF: SUAVITEX BAC SP 500 BOL	2025-11-26 19:11:03.264452+00	1030	3	COMPRA	26	32	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD244\\"}"	"{\\"codigo\\": \\"1029355\\"}"	\N	f	\N	\N
2136	ENTRADA	6	Importação automática - NF: 0 | Código sincronizado (PROD245 -> 1004510) | Produto NF: SUAVITEX LEITE HIDRAT BB 1L	2025-11-26 19:11:03.264452+00	1031	3	COMPRA	2	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD245\\"}"	"{\\"codigo\\": \\"1004510\\"}"	\N	f	\N	\N
2137	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD249 -> 1028205) | Produto NF: SUAVITEX PRO MILK BB5L	2025-11-26 19:11:03.264452+00	1035	3	COMPRA	7	11	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD249\\"}"	"{\\"codigo\\": \\"1028205\\"}"	\N	f	\N	\N
2138	ENTRADA	12	Importação automática - NF: 0 | Código sincronizado (PROD250 -> 1023005) | Produto NF: SUAVITEX PRO PESSEGO BB5L	2025-11-26 19:11:03.264452+00	1036	3	COMPRA	16	28	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD250\\"}"	"{\\"codigo\\": \\"1023005\\"}"	\N	f	\N	\N
2139	ENTRADA	20	Importação automática - NF: 0 | Código sincronizado (PROD003 -> 1005805) | Produto NF: AGUASSANI BB 5L	2025-11-26 19:11:03.264452+00	789	3	COMPRA	12	32	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD003\\"}"	"{\\"codigo\\": \\"1005805\\"}"	\N	f	\N	\N
2140	SAIDA	4	HOSP. VET.	2025-11-28 13:48:39.978952+00	1018	3	\N	5	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2141	SAIDA	1	HOSP. VET.	2025-11-28 13:53:34.000902+00	856	3	\N	11	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2142	SAIDA	1	HOSP. VET.	2025-11-28 14:00:51.738227+00	860	3	\N	19	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2143	SAIDA	4	HOSP. VET.	2025-11-28 14:01:21.270679+00	880	3	\N	26	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2144	SAIDA	1	HOSP. VET.	2025-11-28 14:01:45.838403+00	904	3	\N	11	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2145	SAIDA	2	\N	2025-11-28 14:02:00.841284+00	918	3	\N	18	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2146	SAIDA	3	\N	2025-11-28 14:02:15.514777+00	928	3	\N	10	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2147	SAIDA	1	\N	2025-11-28 14:02:26.247747+00	934	3	\N	1	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2148	ENTRADA	600	\N	2025-11-28 14:02:53.650305+00	936	3	\N	290	890	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2149	SAIDA	500	\N	2025-11-28 14:03:06.457117+00	936	3	\N	890	390	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2150	SAIDA	2	\N	2025-11-28 14:09:47.114172+00	1028	3	\N	28	26	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2151	SAIDA	2	\N	2025-11-28 14:09:57.69291+00	1035	3	\N	11	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2152	SAIDA	30	\N	2025-11-28 14:10:15.658697+00	1001	3	\N	30	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2153	SAIDA	5	\N	2025-11-28 14:10:33.269557+00	1002	3	\N	53	48	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2154	SAIDA	4	\N	2025-11-28 14:10:47.23124+00	990	3	\N	52	48	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2155	SAIDA	3	\N	2025-11-28 14:11:03.593496+00	993	3	\N	7	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2156	SAIDA	3	\N	2025-11-28 14:11:16.315386+00	988	3	\N	10	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2157	SAIDA	3	\N	2025-11-28 14:11:31.552722+00	989	3	\N	15	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2158	SAIDA	3	\N	2025-11-28 14:11:42.914155+00	985	3	\N	20	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2159	SAIDA	3	\N	2025-11-28 14:12:01.401714+00	987	3	\N	17	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2160	SAIDA	3	\N	2025-11-28 14:12:17.415431+00	1041	3	\N	122	119	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2161	SAIDA	10	\N	2025-11-28 14:12:31.261185+00	956	3	\N	77	67	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2162	SAIDA	8	\N	2025-11-28 14:13:06.626366+00	958	3	\N	13	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2163	SAIDA	4	\N	2025-11-28 14:13:40.918476+00	808	3	\N	9	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2164	SAIDA	4	\N	2025-11-28 14:13:59.927852+00	798	3	\N	48	44	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2165	SAIDA	6	Importação automática - NF: 0000004748 | Código sincronizado (PROD139 -> 259) | Produto NF: PANO DE CHAO ALVEJADO FLANELADO 48X68	2025-11-28 16:28:58.717486+00	925	3	VENDA	505	499	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD139\\"}"	"{\\"codigo\\": \\"259\\"}"	\N	f	\N	\N
2166	SAIDA	2	Importação automática - NF: 0000004748 | Código sincronizado (AL0002 -> 660) | Produto NF: ALCOOL SAFRA 5L	2025-11-28 16:28:58.717486+00	1062	3	VENDA	8	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"AL0002\\"}"	"{\\"codigo\\": \\"660\\"}"	\N	f	\N	\N
2167	SAIDA	2	Importação automática - NF: 0000004748 | Código sincronizado (PROD016 -> 330) | Produto NF: AROMATIZADOR LAVANDA 360ML	2025-11-28 16:28:58.717486+00	802	3	VENDA	40	38	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD016\\"}"	"{\\"codigo\\": \\"330\\"}"	\N	f	\N	\N
2168	SAIDA	2	Importação automática - NF: 0000004748 | Código sincronizado (PROD134 -> 25) | Produto NF: OXIPRO SOFT BB 5L	2025-11-28 16:28:58.717486+00	920	3	VENDA	15	13	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD134\\"}"	"{\\"codigo\\": \\"25\\"}"	\N	f	\N	\N
2169	SAIDA	2	Importação automática - NF: 0000004748 | Código sincronizado (PROD165 -> 341) | Produto NF: PERFUMAR LAVANDA 5L	2025-11-28 16:28:58.717486+00	951	3	VENDA	11	9	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD165\\"}"	"{\\"codigo\\": \\"341\\"}"	\N	f	\N	\N
2170	SAIDA	1	Importação automática - NF: 0000004748 | Código sincronizado (PROD145 -> 280) | Produto NF: PAPEL HIGIENICO ROLAO 8X300M (NOBRE)	2025-11-28 16:28:58.717486+00	931	3	VENDA	51	50	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD145\\"}"	"{\\"codigo\\": \\"280\\"}"	\N	f	\N	\N
2171	SAIDA	6	Importação automática - NF: 0000004748 | Código sincronizado (PROD154 -> 301) | Produto NF: PAPEL TOALHA INTERF.C/ 1000FLS 20X20 (NOBRE)	2025-11-28 16:28:58.717486+00	940	3	VENDA	51	45	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD154\\"}"	"{\\"codigo\\": \\"301\\"}"	\N	f	\N	\N
2172	SAIDA	4	Importação automática - NF: 0000004748 | Código sincronizado (PROD064 -> 644) | Produto NF: FLANELA CRISTAL M 40X60	2025-11-28 16:28:58.717486+00	850	3	VENDA	110	106	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD064\\"}"	"{\\"codigo\\": \\"644\\"}"	\N	f	\N	\N
2173	SAIDA	4	Importação automática - NF: 0000004748 | Código sincronizado (PROD039 -> 587) | Produto NF: DETERGENTE ECONOMICO NEUTRO 500ML	2025-11-28 16:28:58.717486+00	825	3	VENDA	45	41	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD039\\"}"	"{\\"codigo\\": \\"587\\"}"	\N	f	\N	\N
2174	SAIDA	1	Importação automática - NF: 0000004748 | Código sincronizado (PROD175 -> 234) | Produto NF: M 19 O 0 P G - R REFIL ZIGZAG MINI-MOP ALG. PAVIO MOPINHO	2025-11-28 16:28:58.717486+00	961	3	VENDA	12	11	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD175\\"}"	"{\\"codigo\\": \\"234\\"}"	\N	f	\N	\N
2175	SAIDA	25	Importação automática - NF: 0000004745 | Produto NF: PAPEL HIGIENICO ROLAO 8X300M (NOBRE)	2025-11-28 16:30:49.314182+00	931	3	VENDA	50	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2300	ENTRADA	10	\N	2025-12-03 19:16:17.189737+00	988	3	\N	6	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2176	SAIDA	6	Importação automática - NF: 0000004745 | Código sincronizado (PROD151 -> 82) | Produto NF: PAPEL TOALHA BOBINA HR 200X6 100% CELULOSE	2025-11-28 16:30:49.314182+00	937	3	VENDA	10	4	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD151\\"}"	"{\\"codigo\\": \\"82\\"}"	\N	f	\N	\N
2177	SAIDA	10	Importação automática - NF: 0000004746 | Produto NF: PANO DE CHAO ALVEJADO FLANELADO 48X68	2025-11-28 16:32:24.050534+00	925	3	VENDA	499	489	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2178	SAIDA	4	Importação automática - NF: 0000004746 | Produto NF: PULVERIZADOR 500ML SPRAY PERFECT	2025-11-28 16:32:24.050534+00	956	3	VENDA	67	63	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2179	SAIDA	3	Importação automática - NF: 0000004746 | Código sincronizado (1025805 -> 606) | Produto NF: PRAXI SABON ESPUMA ANDIROBA 5L	2025-11-28 16:32:24.050534+00	1033	3	VENDA	13	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1025805\\"}"	"{\\"codigo\\": \\"606\\"}"	\N	f	\N	\N
2180	SAIDA	1	Importação automática - NF: 0000004746 | Código sincronizado (PROD229 -> 138) | Produto NF: DESINFETANTE SANIFLOR MAX FRESH LEMON BB5L	2025-11-28 16:32:24.050534+00	1015	3	VENDA	32	31	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD229\\"}"	"{\\"codigo\\": \\"138\\"}"	\N	f	\N	\N
2181	SAIDA	1	Importação automática - NF: 0000004746 | Código sincronizado (PROD230 -> 48) | Produto NF: DESINFETANTE SANIFLOR MAX SOFT BB 5L	2025-11-28 16:32:24.050534+00	1016	3	VENDA	34	33	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD230\\"}"	"{\\"codigo\\": \\"48\\"}"	\N	f	\N	\N
2182	SAIDA	3	Importação automática - NF: 0000004746 | Código sincronizado (1001405 -> 43) | Produto NF: DETERGENTE CLORADO BB 5L	2025-11-28 16:32:24.050534+00	824	3	VENDA	186	183	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1001405\\"}"	"{\\"codigo\\": \\"43\\"}"	\N	f	\N	\N
2183	SAIDA	4	Importação automática - NF: 0000004746 | Código sincronizado (PROD160 -> 36) | Produto NF: PERFUMAR BREEZE BB 5L RENDE 50L	2025-11-28 16:32:24.050534+00	946	3	VENDA	12	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD160\\"}"	"{\\"codigo\\": \\"36\\"}"	\N	f	\N	\N
2184	SAIDA	36	Importação automática - NF: 0000004746 | Código sincronizado (PROD002 -> 231) | Produto NF: AGUA SANITARIA CLORITO 1L	2025-11-28 16:32:24.050534+00	788	3	VENDA	95	59	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD002\\"}"	"{\\"codigo\\": \\"231\\"}"	\N	f	\N	\N
2185	SAIDA	6	Importação automática - NF: 0000004746 | Código sincronizado (PROD204 -> 236) | Produto NF: S P A LA C S O T P IC / LIXO 75X90X0,03 - PRETO 100LT BETA	2025-11-28 16:32:24.050534+00	990	3	VENDA	48	42	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD204\\"}"	"{\\"codigo\\": \\"236\\"}"	\N	f	\N	\N
2186	SAIDA	3	Importação automática - NF: 0000004746 | Código sincronizado (PROD213 -> 167) | Produto NF: S B A E C TA O P P L / A L S I T X I O C 115X125X0,05 - PRETO 300L	2025-11-28 16:32:24.050534+00	999	3	VENDA	18	15	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD213\\"}"	"{\\"codigo\\": \\"167\\"}"	\N	f	\N	\N
2187	SAIDA	10	Importação automática - NF: 0000004746 | Código sincronizado (PROD110 -> 978) | Produto NF: MASCARA DESCARTAVEL AZUL PFF1	2025-11-28 16:32:24.050534+00	896	3	VENDA	96	86	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD110\\"}"	"{\\"codigo\\": \\"978\\"}"	\N	f	\N	\N
2188	SAIDA	12	Importação automática - NF: 0000004746 | Código sincronizado (PROD021 -> 610) | Produto NF: BAYGON ACAO TOTAL C/ CHEIRO 12X395ML	2025-11-28 16:32:24.050534+00	807	3	VENDA	18	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD021\\"}"	"{\\"codigo\\": \\"610\\"}"	\N	f	\N	\N
2189	SAIDA	10	Importação automática - NF: 0000004746 | Código sincronizado (PROD095 -> 972) | Produto NF: LUVA LATEX AMARELA SILVER - TAM G	2025-11-28 16:32:24.050534+00	881	3	VENDA	17	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD095\\"}"	"{\\"codigo\\": \\"972\\"}"	\N	f	\N	\N
2190	SAIDA	12	Importação automática - NF: 0000004746 | Código sincronizado (PROD037 -> 249) | Produto NF: DETERGENTE NEUTRO FC 500ML	2025-11-28 16:32:24.050534+00	823	3	VENDA	138	126	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD037\\"}"	"{\\"codigo\\": \\"249\\"}"	\N	f	\N	\N
2191	SAIDA	3	Importação automática - NF: 0000004746 | Código sincronizado (PROD020 -> 868) | Produto NF: BALDE PLASTICO PRETO 12L LITROS	2025-11-28 16:32:24.050534+00	806	3	VENDA	4	1	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD020\\"}"	"{\\"codigo\\": \\"868\\"}"	\N	f	\N	\N
2192	SAIDA	4	Importação automática - NF: 0000004746 | Código sincronizado (PROD257 -> 445) | Produto NF: VASSOURA CERDA MACIA PLAST 60 CM	2025-11-28 16:32:24.050534+00	1043	3	VENDA	7	3	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD257\\"}"	"{\\"codigo\\": \\"445\\"}"	\N	f	\N	\N
2193	SAIDA	4	Importação automática - NF: 0000004746 | Código sincronizado (PROD023 -> 296) | Produto NF: CABO DE ALUMINIO 22X1,40M (NOBRE)	2025-11-28 16:32:24.050534+00	809	3	VENDA	43	39	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD023\\"}"	"{\\"codigo\\": \\"296\\"}"	\N	f	\N	\N
2194	SAIDA	5	Importação automática - NF: 0000004747 | Produto NF: PAPEL HIGIENICO ROLAO 8X300M (NOBRE)	2025-12-01 17:49:46.428717+00	931	3	VENDA	25	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2195	SAIDA	4	Importação automática - NF: 0000004747 | Produto NF: PAPEL TOALHA INTERF.C/ 1000FLS 20X20 (NOBRE)	2025-12-01 17:49:46.428717+00	940	3	VENDA	45	41	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2196	SAIDA	1	Importação automática - NF: 0000004747 | Produto NF: PERFUMAR LAVANDA 5L	2025-12-01 17:49:46.428717+00	951	3	VENDA	9	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2197	SAIDA	1	Importação automática - NF: 0000004747 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-01 17:49:46.428717+00	824	3	VENDA	183	182	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2198	SAIDA	10	Importação automática - NF: 0000004747 | Produto NF: DETERGENTE ECONOMICO NEUTRO 500ML	2025-12-01 17:49:46.428717+00	825	3	VENDA	41	31	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2199	SAIDA	1	Importação automática - NF: 0000004747 | Produto NF: ALCOOL SAFRA 5L	2025-12-01 17:49:46.428717+00	1062	3	VENDA	6	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2200	SAIDA	4	Importação automática - NF: 0000004747 | Produto NF: FLANELA CRISTAL M 40X60	2025-12-01 17:49:46.428717+00	850	3	VENDA	106	102	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2201	ENTRADA	204	\N	2025-12-01 17:50:16.701574+00	940	3	\N	41	245	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2202	ENTRADA	12	\N	2025-12-01 17:50:48.818744+00	808	3	\N	5	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2203	ENTRADA	48	\N	2025-12-01 17:51:09.328917+00	882	3	\N	37	85	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2204	ENTRADA	24	\N	2025-12-01 17:51:27.502197+00	901	3	\N	0	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2205	ENTRADA	24	\N	2025-12-01 17:51:46.225094+00	957	3	\N	3	27	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2206	ENTRADA	8	\N	2025-12-01 17:52:16.011933+00	929	3	\N	4	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2207	SAIDA	44	\N	2025-12-01 17:52:42.293443+00	940	3	\N	245	201	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2208	SAIDA	2	\N	2025-12-01 17:52:57.822896+00	984	3	\N	16	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2209	SAIDA	4	\N	2025-12-01 17:53:10.83996+00	983	3	\N	12	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2210	SAIDA	4	\N	2025-12-01 17:54:00.933849+00	991	3	\N	35	31	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2211	SAIDA	2	\N	2025-12-01 17:54:20.46687+00	789	3	\N	32	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2212	SAIDA	12	\N	2025-12-01 17:54:35.782132+00	839	3	\N	151	139	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2213	SAIDA	50	\N	2025-12-01 17:54:48.105616+00	819	3	\N	193	143	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2214	SAIDA	2	\N	2025-12-01 17:55:03.918378+00	853	3	\N	17	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2215	SAIDA	5	\N	2025-12-01 17:55:20.943267+00	976	3	\N	18	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2216	SAIDA	2	\N	2025-12-01 17:55:38.184556+00	890	3	\N	16	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2217	SAIDA	12	Importação automática - NF: 0000004743 | Código sincronizado (PROD001 -> 982) | Produto NF: ACIDO MURIATICO 1L	2025-12-01 17:56:17.561499+00	787	3	VENDA	37	25	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD001\\"}"	"{\\"codigo\\": \\"982\\"}"	\N	f	\N	\N
2218	SAIDA	3	Importação automática - NF: 0000004743 | Código sincronizado (1033005 -> 518) | Produto NF: LIMPAX DX BB5L	2025-12-01 17:56:17.561499+00	874	3	VENDA	179	176	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1033005\\"}"	"{\\"codigo\\": \\"518\\"}"	\N	f	\N	\N
2219	SAIDA	3	Importação automática - NF: 0000004743 | Código sincronizado (1023705 -> 215) | Produto NF: REMOX BB5L	2025-12-01 17:56:17.561499+00	966	3	VENDA	36	33	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1023705\\"}"	"{\\"codigo\\": \\"215\\"}"	\N	f	\N	\N
2301	ENTRADA	10	\N	2025-12-03 19:30:35.727158+00	1062	3	\N	3	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2221	SAIDA	6	Importação automática - NF: 0000001245 | Código sincronizado (1029355 -> 344) | Produto NF: SABONETE SUAVITEX BAC SP BOL 500ML	2025-12-01 17:57:01.79787+00	1030	3	VENDA	32	26	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1029355\\"}"	"{\\"codigo\\": \\"344\\"}"	\N	f	\N	\N
2246	SAIDA	4	Importação automática - NF: 0000001247 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-01 18:12:13.810112+00	824	3	VENDA	177	173	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2247	SAIDA	3	Importação automática - NF: 0000001247 | Produto NF: D 25 E 0 S L INFETANTE SANIFLOR MAX SOFT BB 5L REND	2025-12-01 18:12:13.810112+00	1016	3	VENDA	33	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2248	SAIDA	1	Importação automática - NF: 0000001247 | Produto NF: DESINCROST BB 5L	2025-12-01 18:12:13.810112+00	820	3	VENDA	67	66	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2249	SAIDA	4	Importação automática - NF: 0000001247 | Código sincronizado (1030205 -> 221) | Produto NF: LIMPA PORCELANATO BB5L	2025-12-01 18:12:13.810112+00	870	3	VENDA	7	3	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1030205\\"}"	"{\\"codigo\\": \\"221\\"}"	\N	f	\N	\N
2250	SAIDA	2	Importação automática - NF: 0000001247 | Código sincronizado (518 -> 17) | Produto NF: LIMPAX BB5L	2025-12-01 18:12:13.810112+00	874	3	VENDA	143	141	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"518\\"}"	"{\\"codigo\\": \\"17\\"}"	\N	f	\N	\N
2251	SAIDA	1	Importação automática - NF: 0000001247 | Código sincronizado (606 -> 345) | Produto NF: SABONETE PRAXI ESPUMA ANDIROBA 5L	2025-12-01 18:12:13.810112+00	1033	3	VENDA	9	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"606\\"}"	"{\\"codigo\\": \\"345\\"}"	\N	f	\N	\N
2851	SAIDA	70	Importação automática - NF: 0000004835 | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2026-01-15 18:48:38.4779+00	936	3	VENDA	220	150	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2852	SAIDA	2	Importação automática - NF: 0000004835 | Produto NF: PAPEL TOALHA BOBINA MG BRANCO 150MTS	2026-01-15 18:48:38.4779+00	938	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2853	SAIDA	2	Importação automática - NF: 0000004835 | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2026-01-15 18:48:38.4779+00	935	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2854	SAIDA	5	Importação automática - NF: 0000004835 | Produto NF: S B A E C TA O P P L / A L S I T X I O C 90X100X0,08 - PRETO 200LT	2026-01-15 18:48:38.4779+00	996	3	VENDA	16	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2855	SAIDA	3	Importação automática - NF: 0000004835 | Produto NF: S P A LA C S O T P IC / LIXO 75X90X0,08 - PRETO 100LT BETA	2026-01-15 18:48:38.4779+00	992	3	VENDA	18	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2856	SAIDA	4	Importação automática - NF: 0000004835 | Produto NF: CABO DE ALUMINIO 22X1,40M (NOBRE)	2026-01-15 18:48:38.4779+00	809	3	VENDA	39	35	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2857	SAIDA	4	Importação automática - NF: 0000004835 | Produto NF: RODO DUPLO ALUMINIO 55CM (NOBRE)	2026-01-15 18:48:38.4779+00	968	3	VENDA	19	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2863	SAIDA	37	Importação automática - NF: 0000004837 | Produto NF: SPRAY SANITIZANTE BOLSA 500ML	2026-01-15 18:51:27.725004+00	1025	3	VENDA	37	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2864	SAIDA	30	Importação automática - NF: 0000004837 | Código sincronizado (PROD254 -> 556) | Produto NF: TELA PERFUMADA PARA MICTORIO TUTTI - FRUTTI	2026-01-15 18:51:27.725004+00	1040	3	VENDA	138	108	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD254\\"}"	"{\\"codigo\\": \\"556\\"}"	\N	f	\N	\N
3081	ENTRADA	20	NF None - Processamento automático	2026-01-29 18:42:00.548429+00	824	3	\N	53	73	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3090	SAIDA	24	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:00:40.782782+00	788	3	\N	67	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3095	SAIDA	30	NF 0000004859 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:01:04.535094+00	936	3	\N	1010	980	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3099	SAIDA	2	NF 0000004861 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:01:27.432764+00	929	3	\N	6	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3103	SAIDA	1	NF 0000004857 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:02:06.273884+00	923	3	\N	2	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3107	SAIDA	50	NF 0000004860 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:02:33.416951+00	886	3	\N	50	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2222	SAIDA	2	Importação automática - NF: 0000004742 | Produto NF: LIMPAX DX BB5L	2025-12-01 17:59:42.388756+00	874	3	VENDA	156	154	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2223	SAIDA	2	Importação automática - NF: 0000004742 | Produto NF: REMOX BB5L	2025-12-01 17:59:42.388756+00	966	3	VENDA	33	31	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2224	SAIDA	2	Importação automática - NF: 0000004742 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-01 17:59:42.388756+00	824	3	VENDA	182	180	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2225	SAIDA	5	Importação automática - NF: 0000004742 | Produto NF: PAPEL TOALHA INTERF.C/ 1000FLS 20X20 (NOBRE)	2025-12-01 17:59:42.388756+00	940	3	VENDA	201	196	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2226	SAIDA	1	Importação automática - NF: 0000004742 | Código sincronizado (1028205 -> 54) | Produto NF: SABONETE SUAVITEX PRO MILK BB 5L	2025-12-01 17:59:42.388756+00	1035	3	VENDA	9	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1028205\\"}"	"{\\"codigo\\": \\"54\\"}"	\N	f	\N	\N
2227	SAIDA	1	Importação automática - NF: 0000004742 | Código sincronizado (PROD226 -> 47) | Produto NF: DESINFETANTE SANIFLOR CAPIM LIMAO BB 5L	2025-12-01 17:59:42.388756+00	1012	3	VENDA	3	2	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD226\\"}"	"{\\"codigo\\": \\"47\\"}"	\N	f	\N	\N
2228	SAIDA	1	Importação automática - NF: 0000004742 | Código sincronizado (1034605 -> 787) | Produto NF: DESINCROST GEL BB 5	2025-12-01 17:59:42.388756+00	822	3	VENDA	68	67	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1034605\\"}"	"{\\"codigo\\": \\"787\\"}"	\N	f	\N	\N
2858	SAIDA	5	Importação automática - NF: 0000004842 | Produto NF: LIMPAX DX BB5L	2026-01-15 18:49:03.353112+00	874	3	VENDA	140	135	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2859	SAIDA	2	Importação automática - NF: 0000004842 | Produto NF: REMOX BB5L	2026-01-15 18:49:03.353112+00	966	3	VENDA	35	33	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2869	SAIDA	2	Importação automática - NF: 0000004840 | Produto NF: S B A E C TA O P P L / A L S I T X I O C 75X90X0,05 - PRETO 100LT	2026-01-15 18:54:46.371687+00	991	3	VENDA	24	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2870	SAIDA	2	Importação automática - NF: 0000004840 | Produto NF: S P A LA C S O T P IC / LIXO 55X55X0,25 - PRETO 40LT BETA	2026-01-15 18:54:46.371687+00	1001	3	VENDA	29	27	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2871	SAIDA	2	Importação automática - NF: 0000004840 | Produto NF: S P A LA C S O T P IC ARA LIXO AZUL 40L 55X55X0,025 BETA	2026-01-15 18:54:46.371687+00	983	3	VENDA	17	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2872	SAIDA	1	Importação automática - NF: 0000004840 | Produto NF: DESINFETANTE SANIFLOR MAX FRESH LEMON BB5L	2026-01-15 18:54:46.371687+00	1015	3	VENDA	17	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2873	SAIDA	1	Importação automática - NF: 0000004840 | Produto NF: OXIPRO SOFT BB 5L	2026-01-15 18:54:46.371687+00	920	3	VENDA	17	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2874	SAIDA	50	Importação automática - NF: 0000004840 | Produto NF: COPO DESCATAVEL ULTRA 180ML	2026-01-15 18:54:46.371687+00	818	3	VENDA	150	100	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2875	SAIDA	6	Importação automática - NF: 0000004840 | Produto NF: LUVA BORRACHA LATEX AMARELA M (NOBRE)	2026-01-15 18:54:46.371687+00	882	3	VENDA	83	77	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2876	SAIDA	8	Importação automática - NF: 0000004840 | Produto NF: PANO DE CHAO ALVEJADO FLANELADO 48X68	2026-01-15 18:54:46.371687+00	925	3	VENDA	447	439	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2877	SAIDA	4	Importação automática - NF: 0000004840 | Produto NF: FLANELA CRISTAL M 40X60	2026-01-15 18:54:46.371687+00	850	3	VENDA	119	115	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2878	SAIDA	25	Importação automática - NF: 0000004840 | Produto NF: PAPEL TOALHA INTERF.C/ 1000FLS 20X20 (NOBRE)	2026-01-15 18:54:46.371687+00	940	3	VENDA	101	76	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3082	ENTRADA	4	NF None - Processamento automático	2026-01-29 18:42:00.557763+00	870	3	\N	34	38	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3091	SAIDA	5	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:00:40.800297+00	935	3	\N	23	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3096	SAIDA	2	NF 0000004859 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:01:04.544764+00	938	3	\N	13	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3104	SAIDA	1	NF 0000004857 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:02:06.282262+00	1012	3	\N	2	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2229	SAIDA	5	Importação automática - NF: 0000004749 | Produto NF: LIMPAX DX BB5L	2025-12-01 18:11:04.831971+00	874	3	VENDA	154	149	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2230	SAIDA	3	Importação automática - NF: 0000004749 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-01 18:11:04.831971+00	824	3	VENDA	180	177	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2231	SAIDA	1	Importação automática - NF: 0000004749 | Produto NF: REMOX BB5L	2025-12-01 18:11:04.831971+00	966	3	VENDA	31	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2232	SAIDA	20	Importação automática - NF: 0000004749 | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2025-12-01 18:11:04.831971+00	936	3	VENDA	390	370	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2233	SAIDA	1	Importação automática - NF: 0000004749 | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2025-12-01 18:11:04.831971+00	935	3	VENDA	12	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2234	SAIDA	1	Importação automática - NF: 0000004749 | Produto NF: ALCOOL SAFRA 5L	2025-12-01 18:11:04.831971+00	1062	3	VENDA	5	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2235	SAIDA	1	Importação automática - NF: 0000004749 | Produto NF: PRAXI SABON ESPUMA ANDIROBA 5L	2025-12-01 18:11:04.831971+00	1033	3	VENDA	10	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2236	SAIDA	5	Importação automática - NF: 0000004749 | Produto NF: SABONETE SUAVITEX BAC SP BOL 500ML	2025-12-01 18:11:04.831971+00	1030	3	VENDA	26	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2237	SAIDA	1	Importação automática - NF: 0000004749 | Código sincronizado (1021005 -> 8) | Produto NF: DESINCROST BB 5L	2025-12-01 18:11:04.831971+00	820	3	VENDA	68	67	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1021005\\"}"	"{\\"codigo\\": \\"8\\"}"	\N	f	\N	\N
2238	SAIDA	2	Importação automática - NF: 0000004749 | Código sincronizado (1027105 -> 191) | Produto NF: SANICLOR BB5L	2025-12-01 18:11:04.831971+00	1006	3	VENDA	31	29	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1027105\\"}"	"{\\"codigo\\": \\"191\\"}"	\N	f	\N	\N
2860	SAIDA	18	Importação automática - NF: 0000004841 | Produto NF: PAPEL TOALHA INTERF.C/ 1000FLS 20X20 (NOBRE)	2026-01-15 18:50:21.387423+00	940	3	VENDA	119	101	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2861	SAIDA	2	Importação automática - NF: 0000004841 | Produto NF: PAPEL HIG. CAI CAI C/9000FLS 20X10 CM F. DUPLA	2026-01-15 18:50:21.387423+00	929	3	VENDA	9	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2862	SAIDA	50	Importação automática - NF: 0000004841 | Código sincronizado (PROD031 -> 792) | Produto NF: COPO DESCATAVEL ULTRA 150ML	2026-01-15 18:50:21.387423+00	817	3	VENDA	150	100	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD031\\"}"	"{\\"codigo\\": \\"792\\"}"	\N	f	\N	\N
2865	SAIDA	6	\N	2026-01-15 18:51:57.504872+00	824	3	\N	93	87	CONFIRMADO	\N	\N	\N	CARREGAMENTO	6	\N	\N	\N	f	\N	\N
2866	SAIDA	1	Importação automática - NF: 0000004839 | Produto NF: REMOX BB5L	2026-01-15 18:53:04.810407+00	966	3	VENDA	33	32	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2867	SAIDA	1	Importação automática - NF: 0000004839 | Produto NF: ALUMI CROST BB 5L	2026-01-15 18:53:04.810407+00	792	3	VENDA	14	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2868	SAIDA	1	Importação automática - NF: 0000004839 | Produto NF: SANIMAX BB5L	2026-01-15 18:53:04.810407+00	1022	3	VENDA	2	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3083	ENTRADA	8	NF None - Processamento automático	2026-01-29 18:42:00.565083+00	873	3	\N	36	44	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3092	SAIDA	10	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:00:40.810428+00	977	3	\N	92	82	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3097	SAIDA	3	NF 0000004859 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:01:04.552584+00	935	3	\N	18	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2239	SAIDA	6	Importação automática - NF: 0000001246 | Produto NF: LIMPAX DX BB5L	2025-12-01 18:11:45.775609+00	874	3	VENDA	149	143	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2240	SAIDA	3	Importação automática - NF: 0000001246 | Produto NF: REMOX BB5L	2025-12-01 18:11:45.775609+00	966	3	VENDA	30	27	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2241	SAIDA	2	Importação automática - NF: 0000001246 | Produto NF: OXIPRO SOFT BB 5L REND 100L	2025-12-01 18:11:45.775609+00	920	3	VENDA	13	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2242	SAIDA	1	Importação automática - NF: 0000001246 | Produto NF: ALCOOL SAFRA 5L	2025-12-01 18:11:45.775609+00	1062	3	VENDA	4	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2243	SAIDA	1	Importação automática - NF: 0000001246 | Código sincronizado (PROD073 -> 796) | Produto NF: HIGISEC BB 5L	2025-12-01 18:11:45.775609+00	859	3	VENDA	10	9	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD073\\"}"	"{\\"codigo\\": \\"796\\"}"	\N	f	\N	\N
2244	SAIDA	1	Importação automática - NF: 0000001246 | Código sincronizado (PROD132 -> 124) | Produto NF: OXIPRO FRESH LEMON BB5L	2025-12-01 18:11:45.775609+00	918	3	VENDA	16	15	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD132\\"}"	"{\\"codigo\\": \\"124\\"}"	\N	f	\N	\N
2245	SAIDA	3	Importação automática - NF: 0000001246 | Código sincronizado (PROD006 -> 211) | Produto NF: ALUMICROST BB 5L	2025-12-01 18:11:45.775609+00	792	3	VENDA	19	16	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD006\\"}"	"{\\"codigo\\": \\"211\\"}"	\N	f	\N	\N
2255	SAIDA	3	Importação automática - NF: 0000001249 | Código sincronizado (787 -> 776) | Produto NF: DESINCROST GEL BB 5 L	2025-12-01 18:12:51.189367+00	822	3	VENDA	67	64	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"787\\"}"	"{\\"codigo\\": \\"776\\"}"	\N	f	\N	\N
2256	SAIDA	2	Importação automática - NF: 0000001249 | Código sincronizado (PROD090 -> 827) | Produto NF: LOUCA MAQ PRO BB5L	2025-12-01 18:12:51.189367+00	876	3	VENDA	17	15	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD090\\"}"	"{\\"codigo\\": \\"827\\"}"	\N	f	\N	\N
2879	ENTRADA	100	\N	2026-01-19 18:04:28.583178+00	886	3	\N	0	100	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2882	SAIDA	9	\N	2026-01-19 18:21:41.404357+00	987	3	\N	9	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2885	ENTRADA	20	\N	2026-01-19 18:28:39.769512+00	1002	3	\N	46	66	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2899	SAIDA	20	\N	2026-01-19 18:38:12.415737+00	824	3	\N	79	59	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2901	SAIDA	4	\N	2026-01-19 18:38:42.735499+00	1014	3	\N	4	0	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2904	SAIDA	13	\N	2026-01-19 18:39:14.70468+00	792	3	\N	13	0	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2905	SAIDA	20	\N	2026-01-19 18:39:29.42783+00	874	3	\N	135	115	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
3084	ENTRADA	32	NF None - Processamento automático	2026-01-29 18:42:00.571404+00	874	3	\N	103	135	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3093	SAIDA	1	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:00:40.818579+00	1012	3	\N	3	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3098	SAIDA	5	NF 0000004859 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:01:04.5602+00	996	3	\N	29	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2252	SAIDA	14	Importação automática - NF: 0000001248 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-01 18:12:31.38397+00	824	3	VENDA	173	159	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2253	SAIDA	6	Importação automática - NF: 0000001248 | Produto NF: REMOX BB5L	2025-12-01 18:12:31.38397+00	966	3	VENDA	27	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2254	SAIDA	16	Importação automática - NF: 0000001248 | Código sincronizado (17 -> 518) | Produto NF: LIMPAX DX BB5L	2025-12-01 18:12:31.38397+00	874	3	VENDA	141	125	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"17\\"}"	"{\\"codigo\\": \\"518\\"}"	\N	f	\N	\N
2257	SAIDA	7	\N	2025-12-01 18:45:24.591746+00	903	3	\N	9	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2258	SAIDA	28	\N	2025-12-01 18:51:29.286951+00	919	3	\N	28	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2259	ENTRADA	6	\N	2025-12-02 11:05:18.427952+00	935	3	\N	11	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2260	ENTRADA	4	\N	2025-12-02 11:05:48.234707+00	938	3	\N	10	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2261	SAIDA	4	Importação automática - NF: 0000001250 | Código sincronizado (1031605 -> 847) | Produto NF: AMACITEC PRIMAVERA BB 5L	2025-12-02 17:28:30.93572+00	796	3	VENDA	10	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1031605\\"}"	"{\\"codigo\\": \\"847\\"}"	\N	f	\N	\N
2262	SAIDA	4	Importação automática - NF: 0000001250 | Código sincronizado (1031505 -> 391) | Produto NF: LAVPRO BB 5L	2025-12-02 17:28:30.93572+00	863	3	VENDA	8	4	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1031505\\"}"	"{\\"codigo\\": \\"391\\"}"	\N	f	\N	\N
2263	SAIDA	1	Importação automática - NF: 0000004750 | Produto NF: DESINFETANTE SANIFLOR MAX FRESH LEMON BB5L	2025-12-03 17:33:25.914632+00	1015	3	VENDA	31	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2264	SAIDA	1	Importação automática - NF: 0000004750 | Produto NF: OXIPRO SOFT BB 5L	2025-12-03 17:33:25.914632+00	920	3	VENDA	11	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2265	SAIDA	50	Importação automática - NF: 0000004750 | Código sincronizado (PROD032 -> 586) | Produto NF: COPO DESCATAVEL UTRA 180ML	2025-12-03 17:33:25.914632+00	818	3	VENDA	236	186	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD032\\"}"	"{\\"codigo\\": \\"586\\"}"	\N	f	\N	\N
2266	SAIDA	1	Importação automática - NF: 0000004750 | Código sincronizado (1023005 -> 60) | Produto NF: SABONETE SUAVITEX PESSEGO BB 5 L	2025-12-03 17:33:25.914632+00	1036	3	VENDA	28	27	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1023005\\"}"	"{\\"codigo\\": \\"60\\"}"	\N	f	\N	\N
2267	SAIDA	1	Importação automática - NF: 0000004750 | Código sincronizado (PROD205 -> 136) | Produto NF: S B A E C TA O P P L / A L S I T X I O C 75X90X0,05 - PRETO 100LT	2025-12-03 17:33:25.914632+00	991	3	VENDA	31	30	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD205\\"}"	"{\\"codigo\\": \\"136\\"}"	\N	f	\N	\N
2268	SAIDA	1	Importação automática - NF: 0000004750 | Código sincronizado (PROD197 -> 397) | Produto NF: S P A LA C S O T P IC ARA LIXO AZUL 40L 55X55X0,025 BETA	2025-12-03 17:33:25.914632+00	983	3	VENDA	8	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD197\\"}"	"{\\"codigo\\": \\"397\\"}"	\N	f	\N	\N
2269	SAIDA	1	Importação automática - NF: 0000004750 | Código sincronizado (PROD202 -> 617) | Produto NF: SACO P/ LIXO INFECTANTE 59X62X 30L LEVE	2025-12-03 17:33:25.914632+00	988	3	VENDA	7	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD202\\"}"	"{\\"codigo\\": \\"617\\"}"	\N	f	\N	\N
2270	SAIDA	1	Importação automática - NF: 0000004750 | Código sincronizado (PROD199 -> 619) | Produto NF: SACO P/ LIXO INFECTANTE 75X105 100L LEVE	2025-12-03 17:33:25.914632+00	985	3	VENDA	17	16	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD199\\"}"	"{\\"codigo\\": \\"619\\"}"	\N	f	\N	\N
2271	SAIDA	5	Importação automática - NF: 0000004750 | Código sincronizado (PROD153 -> 915) | Produto NF: P D A U P P E L L A TOALHA INTERF C/2.400FLS.20X21,5 CM FLS	2025-12-03 17:33:25.914632+00	939	3	VENDA	7	2	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD153\\"}"	"{\\"codigo\\": \\"915\\"}"	\N	f	\N	\N
2272	SAIDA	6	Importação automática - NF: 0000004750 | Código sincronizado (PROD239 -> 222) | Produto NF: SPRAY SANITIZANTE BOLSA 500ML	2025-12-03 17:33:25.914632+00	1025	3	VENDA	14	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD239\\"}"	"{\\"codigo\\": \\"222\\"}"	\N	f	\N	\N
2273	SAIDA	3	\N	2025-12-03 17:33:45.250075+00	880	3	\N	22	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2274	SAIDA	2	Importação automática - NF: 0000004751 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-03 17:34:44.181721+00	824	3	VENDA	159	157	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2275	SAIDA	1	Importação automática - NF: 0000004751 | Código sincronizado (PROD166 -> 41) | Produto NF: PISOFLOR SOFT BB 5L REND 100L	2025-12-03 17:34:44.181721+00	952	3	VENDA	8	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD166\\"}"	"{\\"codigo\\": \\"41\\"}"	\N	f	\N	\N
2276	SAIDA	60	Importação automática - NF: 0000004752 | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2025-12-03 17:36:22.940871+00	936	3	VENDA	370	310	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2277	SAIDA	2	Importação automática - NF: 0000004752 | Produto NF: PAPEL TOALHA BOBINA MG BRANCO 150MTS	2025-12-03 17:36:22.940871+00	938	3	VENDA	14	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2278	SAIDA	4	Importação automática - NF: 0000004752 | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2025-12-03 17:36:22.940871+00	935	3	VENDA	17	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2279	SAIDA	3	Importação automática - NF: 0000004752 | Produto NF: S B A E C TA O P P L / A L S I T X I O C 90X100X0,08 - PRETO 200LT	2025-12-03 17:36:22.940871+00	996	3	VENDA	32	29	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2280	SAIDA	3	Importação automática - NF: 0000001249 | Produto NF: DESINCROST GEL BB 5 L	2025-12-03 17:37:00.522785+00	822	3	VENDA	64	61	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2281	SAIDA	2	Importação automática - NF: 0000001249 | Produto NF: LOUCA MAQ PRO BB5L	2025-12-03 17:37:00.522785+00	876	3	VENDA	15	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2282	SAIDA	1	thiago	2025-12-03 17:42:15.554411+00	866	3	\N	3	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2283	SAIDA	2	Importação automática - NF: 0000001253 | Produto NF: LIMPAX DX BB5L	2025-12-03 17:58:57.90835+00	874	3	VENDA	125	123	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2284	SAIDA	1	Importação automática - NF: 0000001253 | Produto NF: DESINCROST BB 5L	2025-12-03 17:58:57.90835+00	820	3	VENDA	66	65	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2285	SAIDA	1	Importação automática - NF: 0000001253 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-03 17:58:57.90835+00	824	3	VENDA	157	156	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2286	SAIDA	1	Importação automática - NF: 0000001253 | Produto NF: HIGISEC BB 5L	2025-12-03 17:58:57.90835+00	859	3	VENDA	9	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2287	SAIDA	80	Importação automática - NF: 0000001251 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-03 17:59:18.240945+00	824	3	VENDA	156	76	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2288	SAIDA	40	Importação automática - NF: 0000001251 | Produto NF: DESINCROST GEL BB 5 L	2025-12-03 17:59:18.240945+00	822	3	VENDA	61	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2289	SAIDA	40	Importação automática - NF: 0000001251 | Produto NF: DESINCROST BB 5L	2025-12-03 17:59:18.240945+00	820	3	VENDA	65	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2290	SAIDA	80	Importação automática - NF: 0000001252 | Produto NF: LIMPAX DX BB5L	2025-12-03 17:59:50.09548+00	874	3	VENDA	123	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2291	SAIDA	20	Importação automática - NF: 0000001252 | Produto NF: SANICLOR BB5L	2025-12-03 17:59:50.09548+00	1006	3	VENDA	29	9	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2292	SAIDA	20	Importação automática - NF: 0000001252 | Código sincronizado (PROD242 -> 51) | Produto NF: SABONETE ANTISSEPTICO BB 5L	2025-12-03 17:59:50.09548+00	1028	3	VENDA	26	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD242\\"}"	"{\\"codigo\\": \\"51\\"}"	\N	f	\N	\N
2293	SAIDA	1	Importação automática - NF: 0000001252 | Código sincronizado (PROD236 -> 474) | Produto NF: SANIMAX BB5L	2025-12-03 17:59:50.09548+00	1022	3	VENDA	4	3	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD236\\"}"	"{\\"codigo\\": \\"474\\"}"	\N	f	\N	\N
2294	ENTRADA	20	\N	2025-12-03 19:14:51.596511+00	990	3	\N	42	62	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2295	ENTRADA	20	\N	2025-12-03 19:15:04.67072+00	1002	3	\N	48	68	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2296	ENTRADA	44	\N	2025-12-03 19:15:25.061621+00	1001	3	\N	0	44	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2297	ENTRADA	10	\N	2025-12-03 19:15:43.791242+00	1003	3	\N	12	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2298	ENTRADA	10	\N	2025-12-03 19:15:55.160512+00	983	3	\N	7	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2299	ENTRADA	10	\N	2025-12-03 19:16:07.465716+00	989	3	\N	12	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2302	SAIDA	10	\N	2025-12-03 19:31:54.407711+00	1062	3	\N	13	3	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2880	ENTRADA	100	\N	2026-01-19 18:04:39.860494+00	1041	3	\N	36	136	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2884	ENTRADA	50	\N	2026-01-19 18:27:45.817954+00	990	3	\N	28	78	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2891	SAIDA	2	NF 0000004845 - Processamento automático - Cliente: Frete por Conta C	2026-01-19 18:36:22.603745+00	824	3	\N	85	83	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2893	SAIDA	2	NF 0000004845 - Processamento automático - Cliente: Frete por Conta C	2026-01-19 18:36:51.498575+00	824	3	\N	83	81	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2896	SAIDA	1	\N	2026-01-19 18:37:24.079663+00	822	3	\N	51	50	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2900	SAIDA	4	\N	2026-01-19 18:38:30.246364+00	1010	3	\N	4	0	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2906	SAIDA	50	\N	2026-01-19 18:39:46.012204+00	895	3	\N	200	150	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2909	SAIDA	5	\N	2026-01-19 18:40:21.16113+00	964	3	\N	21	16	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
3085	ENTRADA	6	NF None - Processamento automático	2026-01-29 18:42:00.582266+00	1007	3	\N	70	76	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
3094	SAIDA	1	NF 0000004851 - Processamento automático - Cliente: Frete por Conta C	2026-01-29 19:00:40.826377+00	1013	3	\N	3	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2303	ENTRADA	4	\N	2025-12-03 19:32:02.656542+00	1062	3	\N	3	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2304	SAIDA	1	bonificação	2025-12-05 12:53:50.344038+00	1031	3	\N	8	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2305	SAIDA	1	bonificação	2025-12-05 12:56:20.9669+00	910	3	\N	20	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2306	SAIDA	1	\N	2025-12-05 12:57:26.017089+00	866	3	\N	2	1	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2307	SAIDA	14	\N	2025-12-05 16:10:38.866622+00	792	1	\N	16	2	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2308	SAIDA	25	\N	2025-12-05 16:11:27.393738+00	820	1	\N	25	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2309	SAIDA	4	\N	2025-12-05 16:12:17.12871+00	822	1	\N	21	17	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2310	SAIDA	38	\N	2025-12-05 16:12:39.710605+00	824	1	\N	76	38	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2311	SAIDA	26	\N	2025-12-05 16:13:18.231407+00	873	1	\N	28	2	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2312	SAIDA	43	\N	2025-12-05 16:13:55.830064+00	874	1	\N	43	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2313	ENTRADA	2	\N	2025-12-05 16:14:12.371271+00	876	1	\N	13	15	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2314	SAIDA	1	\N	2025-12-05 16:14:32.81573+00	1024	1	\N	12	11	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2315	ENTRADA	3	\N	2025-12-05 16:16:40.115538+00	964	1	\N	18	21	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2316	SAIDA	21	\N	2025-12-05 16:17:16.789341+00	966	1	\N	21	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2317	SAIDA	2	\N	2025-12-05 16:17:38.984243+00	1006	1	\N	9	7	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2318	SAIDA	18	\N	2025-12-05 16:18:08.100595+00	1007	1	\N	19	1	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2319	SAIDA	8	\N	2025-12-05 16:24:44.350565+00	1030	1	\N	21	13	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2320	SAIDA	8	\N	2025-12-05 16:26:00.529752+00	1035	1	\N	8	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2321	SAIDA	27	\N	2025-12-05 16:27:07.287334+00	1036	1	\N	27	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2322	SAIDA	12	\N	2025-12-05 16:27:34.797458+00	978	1	\N	16	4	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2323	SAIDA	8	\N	2025-12-05 16:31:15.770716+00	1025	1	\N	8	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2324	SAIDA	4	\N	2025-12-05 16:32:49.594102+00	918	1	\N	15	11	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2325	SAIDA	1	\N	2025-12-05 16:33:19.980654+00	920	1	\N	10	9	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2326	SAIDA	4	\N	2025-12-05 16:34:49.374832+00	1010	1	\N	4	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2327	SAIDA	1	\N	2025-12-05 16:35:11.283124+00	1011	1	\N	3	2	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2328	SAIDA	6	\N	2025-12-05 16:37:05.234624+00	1013	1	\N	7	1	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2329	SAIDA	1	\N	2025-12-05 16:37:14.501521+00	1013	1	\N	1	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2330	SAIDA	2	\N	2025-12-05 16:38:19.987041+00	1015	1	\N	30	28	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2331	SAIDA	3	\N	2025-12-05 16:38:43.943815+00	1016	1	\N	30	27	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2332	ENTRADA	1	\N	2025-12-05 16:39:35.538386+00	1017	1	\N	0	1	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2333	SAIDA	1	\N	2025-12-05 16:39:57.147262+00	1018	1	\N	1	0	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2334	SAIDA	1	\N	2025-12-05 16:41:30.876744+00	1048	1	\N	9	8	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2335	SAIDA	2	\N	2025-12-09 14:26:40.341917+00	873	3	\N	2	0	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2336	SAIDA	30	\N	2025-12-09 14:27:19.450359+00	1041	3	\N	119	89	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2337	SAIDA	8	\N	2025-12-09 14:27:53.135833+00	941	3	\N	84	76	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2338	SAIDA	15	\N	2025-12-09 14:28:13.390507+00	933	3	\N	16	1	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2339	SAIDA	4	\N	2025-12-09 14:28:26.212464+00	818	3	\N	186	182	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2340	SAIDA	40	\N	2025-12-09 14:28:51.945478+00	940	3	\N	196	156	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2341	SAIDA	10	\N	2025-12-09 14:29:09.04999+00	1003	3	\N	22	12	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2342	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (847 -> 1031605) | Produto NF: AMACITEC PRIMAVERA BB 5L	2025-12-09 19:43:53.380072+00	796	3	COMPRA	6	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"847\\"}"	"{\\"codigo\\": \\"1031605\\"}"	\N	f	\N	\N
2343	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (391 -> 1031505) | Produto NF: LAVPRO BB 5L	2025-12-09 19:43:53.380072+00	863	3	COMPRA	4	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"391\\"}"	"{\\"codigo\\": \\"1031505\\"}"	\N	f	\N	\N
2344	SAIDA	18	Importação automática - NF: 0000004765 | Produto NF: PAPEL TOALHA INTERF.C/ 1000FLS 20X20 (NOBRE)	2025-12-10 18:18:34.641088+00	940	3	VENDA	156	138	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2345	SAIDA	50	Importação automática - NF: 0000004765 | Produto NF: COPO DESCATAVEL UTRA 180ML	2025-12-10 18:18:34.641088+00	818	3	VENDA	182	132	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2346	SAIDA	1	Importação automática - NF: 0000004765 | Produto NF: ALCOOL SAFRA 5L	2025-12-10 18:18:34.641088+00	1062	3	VENDA	7	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2347	SAIDA	10	Importação automática - NF: 0000004765 | Produto NF: DETERGENTE ECONOMICO NEUTRO 500ML	2025-12-10 18:18:34.641088+00	825	3	VENDA	31	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2348	SAIDA	2	Importação automática - NF: 0000004765 | Código sincronizado (PROD143 -> 903) | Produto NF: PAPEL HIG. CAI CAI C/9000FLS 20X10 CM F. DUPLA	2025-12-10 18:18:34.641088+00	929	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD143\\"}"	"{\\"codigo\\": \\"903\\"}"	\N	f	\N	\N
2349	SAIDA	3	Importação automática - NF: 0000004765 | Código sincronizado (PROD053 -> 102) | Produto NF: ESPONJA DUPLA FACE	2025-12-10 18:18:34.641088+00	839	3	VENDA	139	136	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD053\\"}"	"{\\"codigo\\": \\"102\\"}"	\N	f	\N	\N
2350	SAIDA	1	\N	2025-12-10 18:18:52.334786+00	856	3	\N	10	9	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2351	SAIDA	2	Importação automática - NF: 0000001260 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-10 18:19:25.893145+00	824	3	VENDA	38	36	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2352	SAIDA	1	Importação automática - NF: 0000001260 | Produto NF: PISOFLOR BB 5L REND 100L	2025-12-10 18:19:25.893145+00	952	3	VENDA	7	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2353	SAIDA	4	Importação automática - NF: 0000001260 | Código sincronizado (1005805 -> 3) | Produto NF: AGUASSANI BB 5L REND 20L	2025-12-10 18:19:25.893145+00	789	3	VENDA	30	26	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1005805\\"}"	"{\\"codigo\\": \\"3\\"}"	\N	f	\N	\N
2354	SAIDA	3	Importação automática - NF: 0000001259 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-10 18:19:54.336818+00	824	3	VENDA	36	33	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2355	SAIDA	3	Importação automática - NF: 0000001259 | Produto NF: LIMPA PORCELANATO BB5L	2025-12-10 18:19:54.336818+00	870	3	VENDA	3	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2356	SAIDA	2	Importação automática - NF: 0000001259 | Produto NF: LOUCA MAQ PRO BB5L	2025-12-10 18:19:54.336818+00	876	3	VENDA	15	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2357	SAIDA	2	Importação automática - NF: 0000001259 | Código sincronizado (PROD238 -> 334) | Produto NF: SEC MAQ PRO BB5L	2025-12-10 18:19:54.336818+00	1024	3	VENDA	11	9	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD238\\"}"	"{\\"codigo\\": \\"334\\"}"	\N	f	\N	\N
2358	SAIDA	8	Importação automática - NF: 0000001257 | Código sincronizado (PROD079 -> 818) | Produto NF: LAVPRO BB 50L	2025-12-10 18:20:26.879199+00	865	3	VENDA	11	3	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD079\\"}"	"{\\"codigo\\": \\"818\\"}"	\N	f	\N	\N
2359	SAIDA	6	Importação automática - NF: 0000001257 | Código sincronizado (PROD008 -> 820) | Produto NF: ALVITEC PE BB 50KG	2025-12-10 18:20:26.879199+00	794	3	VENDA	8	2	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD008\\"}"	"{\\"codigo\\": \\"820\\"}"	\N	f	\N	\N
2360	SAIDA	3	Importação automática - NF: 0000001257 | Código sincronizado (PROD131 -> 821) | Produto NF: NEUTRAL BB 50L	2025-12-10 18:20:26.879199+00	917	3	VENDA	3	0	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD131\\"}"	"{\\"codigo\\": \\"821\\"}"	\N	f	\N	\N
2361	SAIDA	5	Importação automática - NF: 0000001257 | Código sincronizado (1031605 -> 822) | Produto NF: AMACITEC PRIMAVERA BB 50L	2025-12-10 18:20:26.879199+00	796	3	VENDA	10	5	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1031605\\"}"	"{\\"codigo\\": \\"822\\"}"	\N	f	\N	\N
2362	ENTRADA	8	\N	2025-12-11 14:06:05.115358+00	1094	3	\N	0	8	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2363	ENTRADA	4	Importação automática - NF: 0 | Produto NF: GEL ANTISSEPTICO BB5L	2025-12-11 14:42:07.602628+00	856	3	COMPRA	9	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2364	ENTRADA	12	Importação automática - NF: 0 | Produto NF: LIMPAX BB 5L	2025-12-11 14:42:07.602628+00	873	3	COMPRA	0	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2365	ENTRADA	4	Importação automática - NF: 0 | Produto NF: SUAVITEX DX MICRO ESF BB 5L	2025-12-11 14:42:07.602628+00	978	3	COMPRA	4	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2366	ENTRADA	15	Importação automática - NF: 0 | Produto NF: SANICLOR DT BB 20L	2025-12-11 14:42:07.602628+00	1007	3	COMPRA	1	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2367	ENTRADA	20	Importação automática - NF: 0 | Código sincronizado (3 -> 1005805) | Produto NF: AGUASSANI BB 5L	2025-12-11 14:42:07.602628+00	789	3	COMPRA	26	46	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"3\\"}"	"{\\"codigo\\": \\"1005805\\"}"	\N	f	\N	\N
2368	ENTRADA	20	Importação automática - NF: 0 | Código sincronizado (211 -> 1028105) | Produto NF: ALUMI CROST BB5L	2025-12-11 14:42:07.602628+00	792	3	COMPRA	2	22	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"211\\"}"	"{\\"codigo\\": \\"1028105\\"}"	\N	f	\N	\N
2369	ENTRADA	40	Importação automática - NF: 0 | Código sincronizado (8 -> 1021005) | Produto NF: DESINCROST BB5L	2025-12-11 14:42:07.602628+00	820	3	COMPRA	0	40	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"8\\"}"	"{\\"codigo\\": \\"1021005\\"}"	\N	f	\N	\N
2370	ENTRADA	20	Importação automática - NF: 0 | Código sincronizado (776 -> 1034605) | Produto NF: DESINCROST GEL BB5L	2025-12-11 14:42:07.602628+00	822	3	COMPRA	17	37	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"776\\"}"	"{\\"codigo\\": \\"1034605\\"}"	\N	f	\N	\N
2371	ENTRADA	100	Importação automática - NF: 0 | Código sincronizado (43 -> 1001405) | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-11 14:42:07.602628+00	824	3	COMPRA	33	133	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"43\\"}"	"{\\"codigo\\": \\"1001405\\"}"	\N	f	\N	\N
2372	ENTRADA	8	Importação automática - NF: 0 | Código sincronizado (221 -> 1030205) | Produto NF: LIMPA PORCELANATO BB5L	2025-12-11 14:42:07.602628+00	870	3	COMPRA	0	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"221\\"}"	"{\\"codigo\\": \\"1030205\\"}"	\N	f	\N	\N
2373	ENTRADA	100	Importação automática - NF: 0 | Código sincronizado (518 -> 1033005) | Produto NF: LIMPAX DX BB5L	2025-12-11 14:42:07.602628+00	874	3	COMPRA	0	100	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"518\\"}"	"{\\"codigo\\": \\"1033005\\"}"	\N	f	\N	\N
2374	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (827 -> 1034705) | Produto NF: A MAQ	2025-12-11 14:42:07.602628+00	876	3	COMPRA	13	17	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"827\\"}"	"{\\"codigo\\": \\"1034705\\"}"	\N	f	\N	\N
2375	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD117 -> 1020705) | Produto NF: MULTIBAC BP BB5L	2025-12-11 14:42:07.602628+00	903	3	COMPRA	2	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD117\\"}"	"{\\"codigo\\": \\"1020705\\"}"	\N	f	\N	\N
2376	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD119 -> 1018605) | Produto NF: MULTILUX BAC BREEZE BB5L	2025-12-11 14:42:07.602628+00	905	3	COMPRA	0	4	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD119\\"}"	"{\\"codigo\\": \\"1018605\\"}"	\N	f	\N	\N
2377	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD122 -> 1009305) | Produto NF: MULTILUX BAC SOFT BB 5L	2025-12-11 14:42:07.602628+00	908	3	COMPRA	0	4	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD122\\"}"	"{\\"codigo\\": \\"1009305\\"}"	\N	f	\N	\N
2378	ENTRADA	2	Importação automática - NF: 0 | Código sincronizado (124 -> 1028405) | Produto NF: OXIPRO FRESH LEMON BB5L	2025-12-11 14:42:07.602628+00	918	3	COMPRA	11	13	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"124\\"}"	"{\\"codigo\\": \\"1028405\\"}"	\N	f	\N	\N
2379	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (25 -> 1027405) | Produto NF: OXIPRO SOFT BB5L	2025-12-11 14:42:07.602628+00	920	3	COMPRA	9	13	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"25\\"}"	"{\\"codigo\\": \\"1027405\\"}"	\N	f	\N	\N
2380	ENTRADA	2	Importação automática - NF: 0 | Código sincronizado (PROD176 -> 1024522) | Produto NF: REMOCALC BB 20L	2025-12-11 14:42:07.602628+00	962	3	COMPRA	0	2	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD176\\"}"	"{\\"codigo\\": \\"1024522\\"}"	\N	f	\N	\N
2381	ENTRADA	28	Importação automática - NF: 0 | Código sincronizado (PROD177 -> 1017305) | Produto NF: REMOCRIL POWER BB5L	2025-12-11 14:42:07.602628+00	963	3	COMPRA	0	28	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD177\\"}"	"{\\"codigo\\": \\"1017305\\"}"	\N	f	\N	\N
2382	ENTRADA	2	Importação automática - NF: 0 | Código sincronizado (PROD179 -> 1023722) | Produto NF: REMOX BB 20L	2025-12-11 14:42:07.602628+00	965	3	COMPRA	0	2	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD179\\"}"	"{\\"codigo\\": \\"1023722\\"}"	\N	f	\N	\N
2383	ENTRADA	40	Importação automática - NF: 0 | Código sincronizado (215 -> 1023705) | Produto NF: REMOX BB5L	2025-12-11 14:42:07.602628+00	966	3	COMPRA	0	40	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"215\\"}"	"{\\"codigo\\": \\"1023705\\"}"	\N	f	\N	\N
2384	ENTRADA	16	Importação automática - NF: 0 | Código sincronizado (191 -> 1027105) | Produto NF: SANICLOR BB5L	2025-12-11 14:42:07.602628+00	1006	3	COMPRA	7	23	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"191\\"}"	"{\\"codigo\\": \\"1027105\\"}"	\N	f	\N	\N
2385	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD225 -> 1004905) | Produto NF: SANIFLOR CAMPESTRE BB 5L	2025-12-11 14:42:07.602628+00	1011	3	COMPRA	2	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD225\\"}"	"{\\"codigo\\": \\"1004905\\"}"	\N	f	\N	\N
2386	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (47 -> 1022605) | Produto NF: SANIFLOR CAPIM LIMAO BB5L	2025-12-11 14:42:07.602628+00	1012	3	COMPRA	2	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"47\\"}"	"{\\"codigo\\": \\"1022605\\"}"	\N	f	\N	\N
2387	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (214 -> 1022705) | Produto NF: SANIFLOR PLUS CAPIM LIMAO BB5L	2025-12-11 14:42:07.602628+00	1017	3	COMPRA	1	5	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"214\\"}"	"{\\"codigo\\": \\"1022705\\"}"	\N	f	\N	\N
2388	ENTRADA	80	Importação automática - NF: 0 | Código sincronizado (222 -> 1027955) | Produto NF: SPRAY SANITIZANTE BOLSA 500ML	2025-12-11 14:42:07.602628+00	1025	3	COMPRA	0	80	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"222\\"}"	"{\\"codigo\\": \\"1027955\\"}"	\N	f	\N	\N
2389	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (51 -> 1013805) | Produto NF: SUAVITEX BAC BB 5L	2025-12-11 14:42:07.602628+00	1028	3	COMPRA	6	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"51\\"}"	"{\\"codigo\\": \\"1013805\\"}"	\N	f	\N	\N
2390	ENTRADA	18	Importação automática - NF: 0 | Código sincronizado (344 -> 1029355) | Produto NF: SUAVITEX BAC SP 500 BOL	2025-12-11 14:42:07.602628+00	1030	3	COMPRA	13	31	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"344\\"}"	"{\\"codigo\\": \\"1029355\\"}"	\N	f	\N	\N
2391	ENTRADA	16	Importação automática - NF: 0 | Código sincronizado (54 -> 1028205) | Produto NF: SUAVITEX PRO MILK BB5L	2025-12-11 14:42:07.602628+00	1035	3	COMPRA	0	16	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"54\\"}"	"{\\"codigo\\": \\"1028205\\"}"	\N	f	\N	\N
2392	ENTRADA	12	Importação automática - NF: 0 | Código sincronizado (60 -> 1023005) | Produto NF: SUAVITEX PRO PESSEGO BB5L	2025-12-11 14:42:07.602628+00	1036	3	COMPRA	0	12	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"60\\"}"	"{\\"codigo\\": \\"1023005\\"}"	\N	f	\N	\N
2393	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD262 -> 1003505) | Produto NF: VIDROLUX BB 5L	2025-12-11 14:42:07.602628+00	1048	3	COMPRA	8	12	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD262\\"}"	"{\\"codigo\\": \\"1003505\\"}"	\N	f	\N	\N
2394	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (sss66 -> 1022505) | Produto NF: MULTILUX BAC CAPIM LIMAO BB5L	2025-12-11 14:42:07.602628+00	1076	3	COMPRA	2	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"sss66\\"}"	"{\\"codigo\\": \\"1022505\\"}"	\N	f	\N	\N
2395	SAIDA	13	\N	2025-12-11 17:29:22.743944+00	874	3	\N	100	87	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	pendência - mega	\N	\N	\N	f	\N	\N
2396	SAIDA	10	\N	2025-12-11 17:29:36.126998+00	966	3	\N	40	30	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	pendência - mega	\N	\N	\N	f	\N	\N
2397	SAIDA	4	\N	2025-12-11 17:30:01.496114+00	963	3	\N	28	24	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	pendência - linhares	\N	\N	\N	f	\N	\N
2398	SAIDA	2	\N	2025-12-11 17:31:12.643632+00	1036	3	\N	12	10	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	pendência - eqt ma	\N	\N	\N	f	\N	\N
2399	SAIDA	12	\N	2025-12-11 17:31:29.386442+00	1035	3	\N	16	4	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	pendência - eqt ma	\N	\N	\N	f	\N	\N
2400	SAIDA	1	\N	2025-12-11 17:32:35.223206+00	1036	3	\N	10	9	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	pendência - eqt ma	\N	\N	\N	f	\N	\N
2401	SAIDA	3	Importação automática - NF: 0000004766 | Código sincronizado (1023705 -> 215) | Produto NF: REMOX BB5L	2025-12-11 17:35:02.458338+00	966	3	VENDA	30	27	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1023705\\"}"	"{\\"codigo\\": \\"215\\"}"	\N	f	\N	\N
2402	SAIDA	6	Importação automática - NF: 0000004766 | Código sincronizado (1033005 -> 518) | Produto NF: LIMPAX DX BB5L	2025-12-11 17:35:02.458338+00	874	3	VENDA	87	81	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1033005\\"}"	"{\\"codigo\\": \\"518\\"}"	\N	f	\N	\N
2403	SAIDA	50	Importação automática - NF: 0000004770 | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2025-12-11 17:35:29.143902+00	936	3	VENDA	310	260	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2404	SAIDA	6	Importação automática - NF: 0000004770 | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2025-12-11 17:35:29.143902+00	935	3	VENDA	13	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2405	SAIDA	5	Importação automática - NF: 0000004770 | Produto NF: S B A E C TA O P P L / A L S I T X I O C 90X100X0,08 - PRETO 200LT	2025-12-11 17:35:29.143902+00	996	3	VENDA	29	24	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2406	SAIDA	10	Importação automática - NF: 0000004771 | Produto NF: PAPEL TOALHA INTERF.C/ 1000FLS 20X20 (NOBRE)	2025-12-11 17:36:03.305112+00	940	3	VENDA	138	128	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2407	SAIDA	2	Importação automática - NF: 0000004771 | Produto NF: PAPEL HIGIENICO ROLAO 8X300M (NOBRE)	2025-12-11 17:36:03.305112+00	931	3	VENDA	20	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2408	SAIDA	1	Importação automática - NF: 0000004771 | Código sincronizado (1018105 -> 10) | Produto NF: GEL SANITIZANTE BB 5L	2025-12-11 17:36:03.305112+00	856	3	VENDA	13	12	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1018105\\"}"	"{\\"codigo\\": \\"10\\"}"	\N	f	\N	\N
2409	SAIDA	2	Importação automática - NF: 0000004771 | Código sincronizado (PROD260 -> 460) | Produto NF: VASSOURA PIACAVA RAINHA MAX	2025-12-11 17:36:03.305112+00	1046	3	VENDA	53	51	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD260\\"}"	"{\\"codigo\\": \\"460\\"}"	\N	f	\N	\N
2410	SAIDA	1	Importação automática - NF: 0000004768 | Código sincronizado (1005705 -> 52) | Produto NF: SABONETE DESENGRAXANTE MICRO ESFERA BB 5L	2025-12-11 17:36:28.100798+00	978	3	VENDA	8	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1005705\\"}"	"{\\"codigo\\": \\"52\\"}"	\N	f	\N	\N
2411	SAIDA	50	Importação automática - NF: 0000004773 | Código sincronizado (PROD100 -> 1010) | Produto NF: LUVA NITRILICA AZUL SEM PO CX C/ 100UN. G	2025-12-11 17:36:52.829705+00	886	3	VENDA	240	190	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD100\\"}"	"{\\"codigo\\": \\"1010\\"}"	\N	f	\N	\N
2412	SAIDA	12	Importação automática - NF: 0000004773 | Código sincronizado (PROD103 -> 1009) | Produto NF: LUVA NITRILICA AZUL SEM PO CX C/ 100UN. M	2025-12-11 17:36:52.829705+00	889	3	VENDA	125	113	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD103\\"}"	"{\\"codigo\\": \\"1009\\"}"	\N	f	\N	\N
2413	SAIDA	8	Importação automática - NF: 0000001262 | Código sincronizado (1017305 -> 224) | Produto NF: REMOCRIL POWER BB 5L	2025-12-11 17:37:16.129269+00	963	3	VENDA	24	16	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1017305\\"}"	"{\\"codigo\\": \\"224\\"}"	\N	f	\N	\N
2414	SAIDA	2	Importação automática - NF: 0000004767 | Código sincronizado (1003505 -> 40) | Produto NF: VIDROLUX BB 5L REND 25L	2025-12-11 18:17:23.550258+00	1048	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1003505\\"}"	"{\\"codigo\\": \\"40\\"}"	\N	f	\N	\N
2415	ENTRADA	75	devolução	2025-12-12 13:55:11.083311+00	941	3	\N	76	151	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2416	SAIDA	4	\N	2025-12-12 14:01:43.114337+00	963	3	\N	16	12	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2417	SAIDA	42	\N	2025-12-12 14:02:16.474588+00	1025	3	\N	80	38	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2418	SAIDA	8	Importação automática - NF: 0000004772 | Produto NF: PULVERIZADOR 500ML SPRAY PERFECT	2025-12-12 14:03:00.963619+00	956	3	VENDA	63	55	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2419	SAIDA	4	Importação automática - NF: 0000004772 | Produto NF: REMOCRIL POWER BB 5L	2025-12-12 14:03:00.963619+00	963	3	VENDA	12	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2420	SAIDA	1	Importação automática - NF: 0000004772 | Código sincronizado (1027405 -> 25) | Produto NF: OXIPRO SOFT BB 5L	2025-12-12 14:03:00.963619+00	920	3	VENDA	13	12	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1027405\\"}"	"{\\"codigo\\": \\"25\\"}"	\N	f	\N	\N
2421	SAIDA	1	Importação automática - NF: 0000004772 | Código sincronizado (1001405 -> 43) | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-12 14:03:00.963619+00	824	3	VENDA	133	132	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1001405\\"}"	"{\\"codigo\\": \\"43\\"}"	\N	f	\N	\N
2422	SAIDA	3	Importação automática - NF: 0000004775 | Código sincronizado (PRATIK5 -> 641) | Produto NF: MULTIBAC PRATIK FR 500ML GATIL	2025-12-12 14:04:47.710354+00	1071	3	VENDA	5	2	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PRATIK5\\"}"	"{\\"codigo\\": \\"641\\"}"	\N	f	\N	\N
2423	SAIDA	2	Importação automática - NF: 0000004775 | Código sincronizado (PROD118 -> 62) | Produto NF: MULTIBAC BP DOS 1L	2025-12-12 14:04:47.710354+00	904	3	VENDA	10	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD118\\"}"	"{\\"codigo\\": \\"62\\"}"	\N	f	\N	\N
2424	SAIDA	5	Importação automática - NF: 0000004774 | Produto NF: SABONETE DESENGRAXANTE MICRO ESFERA BB 5L	2025-12-12 14:13:02.332114+00	978	3	VENDA	7	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2425	SAIDA	2	Importação automática - NF: 0000004769 | Produto NF: SABONETE DESENGRAXANTE MICRO ESFERA BB 5L	2025-12-12 14:13:27.761806+00	978	3	VENDA	2	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2426	SAIDA	20	Importação automática - NF: 0000004778 | Produto NF: PANO DE CHAO ALVEJADO FLANELADO 48X68	2025-12-12 14:14:53.410691+00	925	3	VENDA	489	469	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2427	SAIDA	60	Importação automática - NF: 0000004778 | Produto NF: PAPEL TOALHA INTERF.C/ 1000FLS 20X20 (NOBRE)	2025-12-12 14:14:53.410691+00	940	3	VENDA	128	68	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2428	SAIDA	12	Importação automática - NF: 0000004778 | Produto NF: DETERGENTE NEUTRO FC 500ML	2025-12-12 14:14:53.410691+00	823	3	VENDA	126	114	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2429	SAIDA	12	Importação automática - NF: 0000004778 | Produto NF: ESPONJA DUPLA FACE	2025-12-12 14:14:53.410691+00	839	3	VENDA	136	124	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2430	SAIDA	2	Importação automática - NF: 0000004778 | Código sincronizado (PROD211 -> 189) | Produto NF: S P A LA C S O T P IC / LIXO 40X50X0,025 - PRETO 20LT BETA	2025-12-12 14:14:53.410691+00	997	3	VENDA	46	44	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD211\\"}"	"{\\"codigo\\": \\"189\\"}"	\N	f	\N	\N
2431	SAIDA	1	Importação automática - NF: 0000004778 | Código sincronizado (PROD207 -> 399) | Produto NF: S B A E C TA O P P L / A L S I T X I O C 90X100X0,03 - PRETO 200LT	2025-12-12 14:14:53.410691+00	993	3	VENDA	4	3	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD207\\"}"	"{\\"codigo\\": \\"399\\"}"	\N	f	\N	\N
2432	SAIDA	2	Importação automática - NF: 0000004778 | Código sincronizado (PROD216 -> 134) | Produto NF: S P A LA C S O T P IC / LIXO 60X70X0,025 - PRETO 60LT BETA	2025-12-12 14:14:53.410691+00	1002	3	VENDA	68	66	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD216\\"}"	"{\\"codigo\\": \\"134\\"}"	\N	f	\N	\N
2433	SAIDA	1	Importação automática - NF: 0000004778 | Código sincronizado (PROD203 -> 618) | Produto NF: SACO P/ LIXO INFECTANTE 63X80 50L LEVE	2025-12-12 14:14:53.410691+00	989	3	VENDA	22	21	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD203\\"}"	"{\\"codigo\\": \\"618\\"}"	\N	f	\N	\N
2434	SAIDA	2	Importação automática - NF: 0000004778 | Código sincronizado (PROD096 -> 291) | Produto NF: LUVA BORRACHA LATEX AMARELA M (NOBRE)	2025-12-12 14:14:53.410691+00	882	3	VENDA	85	83	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD096\\"}"	"{\\"codigo\\": \\"291\\"}"	\N	f	\N	\N
2435	ENTRADA	48	\N	2025-12-15 14:47:45.705346+00	1096	3	\N	0	48	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2436	ENTRADA	48	\N	2025-12-15 14:48:31.968112+00	1097	3	\N	0	48	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2437	ENTRADA	20	\N	2025-12-15 17:25:29.934699+00	811	3	\N	0	20	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2438	ENTRADA	3	\N	2025-12-15 17:26:57.704635+00	1089	3	\N	0	3	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2439	ENTRADA	4	\N	2025-12-15 17:27:54.952616+00	1091	3	\N	0	4	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2440	ENTRADA	5	\N	2025-12-15 17:29:02.714594+00	1092	3	\N	0	5	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2441	ENTRADA	7	\N	2025-12-15 17:29:51.596342+00	1090	3	\N	0	7	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2442	ENTRADA	6	\N	2025-12-15 17:30:15.98494+00	969	3	\N	4	10	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2443	ENTRADA	12	\N	2025-12-15 17:33:01.115408+00	1077	3	\N	0	12	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2444	ENTRADA	10	\N	2025-12-15 17:34:43.629757+00	1098	3	\N	0	10	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2445	ENTRADA	3	\N	2025-12-15 17:35:55.391808+00	1099	3	\N	0	3	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2446	ENTRADA	150	\N	2025-12-15 17:36:07.523223+00	940	3	\N	68	218	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2447	SAIDA	4	Importação automática - NF: 0000004779 | Produto NF: REMOX BB5L	2025-12-16 13:15:46.138809+00	966	3	VENDA	27	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2448	SAIDA	4	Importação automática - NF: 0000004779 | Produto NF: LIMPAX DX BB5L	2025-12-16 13:15:46.138809+00	874	3	VENDA	81	77	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2449	SAIDA	2	Importação automática - NF: 0000004779 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-16 13:15:46.138809+00	824	3	VENDA	132	130	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2450	SAIDA	2	Importação automática - NF: 0000001264 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-16 13:16:15.38885+00	824	3	VENDA	130	128	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2451	SAIDA	1	Importação automática - NF: 0000001264 | Código sincronizado (1021005 -> 8) | Produto NF: DESINCROST BB 5L	2025-12-16 13:16:15.38885+00	820	3	VENDA	40	39	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1021005\\"}"	"{\\"codigo\\": \\"8\\"}"	\N	f	\N	\N
2452	SAIDA	1	Importação automática - NF: 0000004783 | Produto NF: DESINCROST BB 5L	2025-12-16 13:18:55.069805+00	820	3	VENDA	39	38	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2453	SAIDA	5	Importação automática - NF: 0000004783 | Produto NF: LIMPAX DX BB5L	2025-12-16 13:18:55.069805+00	874	3	VENDA	77	72	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2454	SAIDA	3	Importação automática - NF: 0000004783 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-16 13:18:55.069805+00	824	3	VENDA	128	125	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2455	SAIDA	1	Importação automática - NF: 0000004783 | Produto NF: REMOX BB5L	2025-12-16 13:18:55.069805+00	966	3	VENDA	23	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2456	SAIDA	20	Importação automática - NF: 0000004783 | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2025-12-16 13:18:55.069805+00	936	3	VENDA	260	240	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2457	SAIDA	1	Importação automática - NF: 0000004783 | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2025-12-16 13:18:55.069805+00	935	3	VENDA	7	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2458	SAIDA	1	Importação automática - NF: 0000004783 | Produto NF: ALCOOL SAFRA 5L	2025-12-16 13:18:55.069805+00	1062	3	VENDA	6	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2459	SAIDA	1	Importação automática - NF: 0000004783 | Código sincronizado (345 -> 606) | Produto NF: PRAXI SABON ESPUMA ANDIROBA 5L	2025-12-16 13:18:55.069805+00	1033	3	VENDA	8	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"345\\"}"	"{\\"codigo\\": \\"606\\"}"	\N	f	\N	\N
2460	SAIDA	2	Importação automática - NF: 0000004783 | Código sincronizado (1027105 -> 191) | Produto NF: SANICLOR BB5L	2025-12-16 13:18:55.069805+00	1006	3	VENDA	23	21	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1027105\\"}"	"{\\"codigo\\": \\"191\\"}"	\N	f	\N	\N
2461	SAIDA	5	Importação automática - NF: 0000004783 | Código sincronizado (1029355 -> 344) | Produto NF: SABONETE SUAVITEX BAC SP BOL 500ML	2025-12-16 13:18:55.069805+00	1030	3	VENDA	31	26	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1029355\\"}"	"{\\"codigo\\": \\"344\\"}"	\N	f	\N	\N
2462	SAIDA	1	Importação automática - NF: 0000004764 | Produto NF: REMOX BB5L	2025-12-16 13:19:34.816609+00	966	3	VENDA	22	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2463	SAIDA	2	Importação automática - NF: 0000004764 | Código sincronizado (1003905 -> 17) | Produto NF: LIMPAX BB5L	2025-12-16 13:19:34.816609+00	873	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1003905\\"}"	"{\\"codigo\\": \\"17\\"}"	\N	f	\N	\N
2464	SAIDA	2	Importação automática - NF: 0000004782 | Código sincronizado (PROD235 -> 23) | Produto NF: SANILUX BB 5 L REND 50L	2025-12-16 13:19:55.372353+00	1021	3	VENDA	3	1	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD235\\"}"	"{\\"codigo\\": \\"23\\"}"	\N	f	\N	\N
2465	SAIDA	2	Importação automática - NF: 0000001265 | Produto NF: OXIPRO SOFT BB 5L REND 100L	2025-12-16 13:54:24.587256+00	920	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2466	SAIDA	2	Importação automática - NF: 0000001265 | Produto NF: DESINFETANTE SANIFLOR MAX FRESH LEMON BB5L	2025-12-16 13:54:24.587256+00	1015	3	VENDA	28	26	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2467	SAIDA	2	Importação automática - NF: 0000001265 | Produto NF: PISOFLOR BB 5L REND 100L	2025-12-16 13:54:24.587256+00	952	3	VENDA	6	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2468	SAIDA	2	Importação automática - NF: 0000001265 | Produto NF: GEL SANITIZANTE BB 5L	2025-12-16 13:54:24.587256+00	856	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2469	SAIDA	3	Importação automática - NF: 0000001265 | Código sincronizado (1005805 -> 3) | Produto NF: AGUASSANI BB 5L REND 20L	2025-12-16 13:54:24.587256+00	789	3	VENDA	46	43	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1005805\\"}"	"{\\"codigo\\": \\"3\\"}"	\N	f	\N	\N
2470	SAIDA	2	Importação automática - NF: 0000001265 | Código sincronizado (1009305 -> 28) | Produto NF: MULTILUX BAC SOFT BB 5L REND 750	2025-12-16 13:54:24.587256+00	908	3	VENDA	4	2	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1009305\\"}"	"{\\"codigo\\": \\"28\\"}"	\N	f	\N	\N
2471	SAIDA	4	\N	2025-12-16 14:22:08.639793+00	789	3	\N	43	39	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2472	SAIDA	2	\N	2025-12-16 14:22:32.116195+00	820	3	\N	38	36	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2473	SAIDA	3	\N	2025-12-16 14:22:45.981762+00	824	3	\N	125	122	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2474	ENTRADA	2	\N	2025-12-16 14:22:58.126039+00	873	3	\N	10	12	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2475	SAIDA	2	\N	2025-12-16 14:23:37.570697+00	862	3	\N	28	26	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2476	SAIDA	1	\N	2025-12-16 14:24:36.93955+00	1022	3	\N	3	2	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2477	SAIDA	3	\N	2025-12-16 14:25:27.613238+00	904	3	\N	8	5	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2478	ENTRADA	6	\N	2025-12-16 14:25:57.059148+00	909	3	\N	0	6	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2479	ENTRADA	6	\N	2025-12-16 14:27:13.841322+00	1100	3	\N	0	6	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2480	SAIDA	1	\N	2025-12-16 14:27:22.814169+00	1100	3	\N	6	5	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2481	SAIDA	2	\N	2025-12-16 14:30:16.719601+00	1031	3	\N	7	5	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2482	ENTRADA	8	\N	2025-12-16 14:30:49.029419+00	978	3	\N	0	8	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2483	ENTRADA	10	\N	2025-12-16 14:31:08.455717+00	796	3	\N	5	15	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2484	SAIDA	2	\N	2025-12-16 14:31:21.394456+00	859	3	\N	8	6	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2485	ENTRADA	1	\N	2025-12-16 14:31:34.937768+00	866	3	\N	1	2	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2486	ENTRADA	2	\N	2025-12-16 14:32:01.290262+00	952	3	\N	4	6	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2487	ENTRADA	2	\N	2025-12-16 14:35:04.749053+00	853	3	\N	15	17	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2488	SAIDA	1	\N	2025-12-16 14:35:13.93946+00	856	3	\N	10	9	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2489	SAIDA	3	\N	2025-12-16 14:35:34.049292+00	918	3	\N	13	10	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2490	SAIDA	2	\N	2025-12-16 14:38:37.023018+00	860	3	\N	18	16	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2491	SAIDA	1	\N	2025-12-16 14:38:55.191612+00	1048	3	\N	10	9	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2492	ENTRADA	7	\N	2025-12-16 18:19:27.91504+00	935	3	\N	6	13	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2493	ENTRADA	20	\N	2025-12-16 18:35:05.117811+00	935	3	\N	13	33	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2494	ENTRADA	8	\N	2025-12-16 18:35:15.311075+00	938	3	\N	12	20	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2495	ENTRADA	700	\N	2025-12-16 18:35:21.757368+00	936	3	\N	240	940	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2496	SAIDA	70	Importação automática - NF: 0000004785 | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2025-12-17 13:12:36.735307+00	936	3	VENDA	940	870	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2497	SAIDA	2	Importação automática - NF: 0000004785 | Produto NF: PAPEL TOALHA BOBINA MG BRANCO 150MTS	2025-12-17 13:12:36.735307+00	938	3	VENDA	20	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2498	SAIDA	10	Importação automática - NF: 0000004785 | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2025-12-17 13:12:36.735307+00	935	3	VENDA	33	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2499	SAIDA	5	Importação automática - NF: 0000004785 | Produto NF: S B A E C TA O P P L / A L S I T X I O C 90X100X0,08 - PRETO 200LT	2025-12-17 13:12:36.735307+00	996	3	VENDA	24	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2500	SAIDA	2	Importação automática - NF: 0000004785 | Produto NF: PRAXI SABON ESPUMA ANDIROBA 5L	2025-12-17 13:12:36.735307+00	1033	3	VENDA	7	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2501	SAIDA	50	Importação automática - NF: 0000004784 | Produto NF: LUVA NITRILICA AZUL SEM PO CX C/ 100UN. G	2025-12-17 13:13:01.648436+00	886	3	VENDA	190	140	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2502	SAIDA	50	Importação automática - NF: 0000004784 | Código sincronizado (PROD255 -> 288) | Produto NF: TOUCA DESC. SANFONADA PCT C/ 100UND (NOBRE)	2025-12-17 13:13:01.648436+00	1041	3	VENDA	89	39	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD255\\"}"	"{\\"codigo\\": \\"288\\"}"	\N	f	\N	\N
2503	SAIDA	1	Importação automática - NF: 0000004787 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-17 14:09:25.154355+00	824	3	VENDA	122	121	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2504	SAIDA	1	Importação automática - NF: 0000004787 | Produto NF: PERFUMAR LAVANDA 5L	2025-12-17 14:09:25.154355+00	951	3	VENDA	8	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2505	SAIDA	1	Importação automática - NF: 0000004787 | Produto NF: S B A E C TA O P P L / A L S I T X I O C 90X100X0,03 - PRETO 200LT	2025-12-17 14:09:25.154355+00	993	3	VENDA	3	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2506	SAIDA	4	Importação automática - NF: 0000004787 | Produto NF: DETERGENTE ECONOMICO NEUTRO 500ML	2025-12-17 14:09:25.154355+00	825	3	VENDA	21	17	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2507	SAIDA	4	Importação automática - NF: 0000004787 | Produto NF: ESPONJA DUPLA FACE	2025-12-17 14:09:25.154355+00	839	3	VENDA	124	120	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2508	SAIDA	3	Importação automática - NF: 0000004788 | Produto NF: LIMPAX DX BB5L	2025-12-17 19:00:33.98815+00	874	3	VENDA	72	69	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2509	SAIDA	2	Importação automática - NF: 0000004788 | Produto NF: REMOX BB5L	2025-12-17 19:00:33.98815+00	966	3	VENDA	21	19	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2510	SAIDA	3	Importação automática - NF: 0000004786 | Código sincronizado (822 -> 823) | Produto NF: AMACITEC PRIMAVERA BB5L	2025-12-17 19:01:15.745846+00	796	3	VENDA	15	12	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"822\\"}"	"{\\"codigo\\": \\"823\\"}"	\N	f	\N	\N
2511	SAIDA	3	Importação automática - NF: 0000004786 | Código sincronizado (1031305 -> 572) | Produto NF: ALVITEC PE BB 5KG	2025-12-17 19:01:15.745846+00	793	3	VENDA	10	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1031305\\"}"	"{\\"codigo\\": \\"572\\"}"	\N	f	\N	\N
2512	SAIDA	3	Importação automática - NF: 0000004786 | Código sincronizado (1031505 -> 391) | Produto NF: LAVPRO BB 5L	2025-12-17 19:01:15.745846+00	863	3	VENDA	8	5	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1031505\\"}"	"{\\"codigo\\": \\"391\\"}"	\N	f	\N	\N
2513	ENTRADA	24	\N	2025-12-18 13:01:43.011904+00	1102	3	\N	0	24	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2514	SAIDA	40	\N	2025-12-18 13:16:50.015124+00	886	3	\N	140	100	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2515	ENTRADA	1	\N	2025-12-18 13:16:56.186724+00	889	3	\N	113	114	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2516	SAIDA	2	Importação automática - NF: 0000001266 | Produto NF: SEC MAQ PRO BB5L	2025-12-18 13:34:42.644491+00	1024	3	VENDA	9	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2517	SAIDA	12	Importação automática - NF: 0000001266 | Produto NF: SABONETE SUAVITEX BAC SP BOL 500ML	2025-12-18 13:34:42.644491+00	1030	3	VENDA	26	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2518	SAIDA	3	Importação automática - NF: 0000001263 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-18 13:35:01.049471+00	824	3	VENDA	121	118	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2519	SAIDA	1	Importação automática - NF: 0000001263 | Produto NF: REMOX BB5L	2025-12-18 13:35:01.049471+00	966	3	VENDA	19	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2520	SAIDA	2	Importação automática - NF: 0000001263 | Produto NF: DESINCROST BB 5L	2025-12-18 13:35:01.049471+00	820	3	VENDA	36	34	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2521	SAIDA	3	\N	2025-12-19 13:12:33.089131+00	1002	3	\N	66	63	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2522	SAIDA	2	\N	2025-12-19 13:12:51.967572+00	990	3	\N	62	60	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2523	SAIDA	1	\N	2025-12-19 13:13:18.801601+00	993	3	\N	2	1	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2524	SAIDA	5	\N	2025-12-19 13:13:34.302152+00	988	3	\N	16	11	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2525	SAIDA	5	\N	2025-12-19 13:13:50.747197+00	989	3	\N	21	16	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2526	SAIDA	3	\N	2025-12-19 13:14:11.072972+00	985	3	\N	16	13	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2527	SAIDA	3	\N	2025-12-19 13:14:24.767462+00	987	3	\N	14	11	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2528	SAIDA	6	\N	2025-12-19 13:14:42.931755+00	1096	3	\N	48	42	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2529	SAIDA	3	\N	2025-12-19 13:18:13.849124+00	928	3	\N	7	4	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2530	SAIDA	500	\N	2025-12-19 13:18:37.034496+00	936	3	\N	870	370	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2531	SAIDA	30	\N	2025-12-19 13:18:51.635138+00	1001	3	\N	44	14	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2532	SAIDA	5	\N	2025-12-19 13:19:06.846022+00	1002	3	\N	63	58	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2533	SAIDA	4	\N	2025-12-19 13:19:24.096218+00	990	3	\N	60	56	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2534	SAIDA	1	\N	2025-12-19 13:19:38.683183+00	993	3	\N	1	0	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2535	SAIDA	2	\N	2025-12-19 13:19:59.958635+00	988	3	\N	11	9	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2536	SAIDA	2	\N	2025-12-19 13:20:15.263305+00	989	3	\N	16	14	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2537	SAIDA	2	\N	2025-12-19 13:20:35.808135+00	985	3	\N	13	11	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2538	SAIDA	2	\N	2025-12-19 13:20:50.090395+00	987	3	\N	11	9	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2539	SAIDA	3	\N	2025-12-19 13:21:01.953126+00	1041	3	\N	39	36	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2540	ENTRADA	20	Importação automática - NF: 0 | Produto NF: OXIPRO NATURAL BB5L	2025-12-22 14:42:28.415735+00	919	3	COMPRA	0	20	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2541	ENTRADA	4	\N	2025-12-22 17:19:44.641622+00	1105	3	\N	0	4	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2542	SAIDA	1	\N	2025-12-23 11:34:31.128374+00	903	3	\N	6	5	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2543	SAIDA	10	Importação automática - NF: 0000001268 | Código sincronizado (1027305 -> 523) | Produto NF: OXIPRO NATURAL BB5L	2025-12-23 11:34:58.507293+00	919	3	VENDA	20	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1027305\\"}"	"{\\"codigo\\": \\"523\\"}"	\N	f	\N	\N
2544	SAIDA	5	Importação automática - NF: 0000004791 | Produto NF: LIMPAX DX BB5L	2025-12-23 11:35:29.010892+00	874	3	VENDA	69	64	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2545	SAIDA	3	Importação automática - NF: 0000004791 | Produto NF: REMOX BB5L	2025-12-23 11:35:29.010892+00	966	3	VENDA	18	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2546	SAIDA	30	Importação automática - NF: 0000004791 | Código sincronizado (PROD058 -> 63) | Produto NF: FIBRA DE LIMPEZA LEVE BETTANIN	2025-12-23 11:35:29.010892+00	844	3	VENDA	200	170	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD058\\"}"	"{\\"codigo\\": \\"63\\"}"	\N	f	\N	\N
2547	SAIDA	1	Importação automática - NF: 0000004790 | Produto NF: DESINFETANTE SANIFLOR MAX FRESH LEMON BB5L	2025-12-23 11:35:50.4215+00	1015	3	VENDA	26	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2548	SAIDA	2	Importação automática - NF: 0000001267 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-23 11:38:28.461472+00	824	3	VENDA	118	116	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2549	SAIDA	2	Importação automática - NF: 0000001267 | Produto NF: D 25 E 0 S L INFETANTE SANIFLOR MAX SOFT BB 5L REND	2025-12-23 11:38:28.461472+00	1016	3	VENDA	27	25	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2550	SAIDA	1	Importação automática - NF: 0000001267 | Produto NF: SANILUX BB 5 L REND 50L	2025-12-23 11:38:28.461472+00	1021	3	VENDA	1	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2551	SAIDA	2	Importação automática - NF: 0000001267 | Código sincronizado (1030205 -> 221) | Produto NF: LIMPA PORCELANATO BB5L	2025-12-23 11:38:28.461472+00	870	3	VENDA	8	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1030205\\"}"	"{\\"codigo\\": \\"221\\"}"	\N	f	\N	\N
2552	SAIDA	20	Importação automática - NF: 0000004795 | Produto NF: LUVA NITRILICA AZUL SEM PO CX C/ 100UN. G	2025-12-29 14:21:25.146802+00	886	3	VENDA	100	80	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2553	SAIDA	10	Importação automática - NF: 0000004795 | Produto NF: LUVA NITRILICA AZUL SEM PO CX C/ 100UN. M	2025-12-29 14:21:25.146802+00	889	3	VENDA	114	104	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2554	SAIDA	15	Importação automática - NF: 0000004795 | Código sincronizado (1034322 -> 910) | Produto NF: SANICLOR DT BB 20L	2025-12-29 14:21:25.146802+00	1007	3	VENDA	16	1	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1034322\\"}"	"{\\"codigo\\": \\"910\\"}"	\N	f	\N	\N
2555	SAIDA	30	Importação automática - NF: 0000004795 | Código sincronizado (1010 -> 835) | Produto NF: LUVA NITRILICA PRETA SEM PO CX C/ 100UN. G	2025-12-29 14:21:25.146802+00	886	3	VENDA	80	50	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1010\\"}"	"{\\"codigo\\": \\"835\\"}"	\N	f	\N	\N
2556	SAIDA	2	Importação automática - NF: 0000004795 | Código sincronizado (1023722 -> 901) | Produto NF: REMOX BB 20L	2025-12-29 14:21:25.146802+00	965	3	VENDA	2	0	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1023722\\"}"	"{\\"codigo\\": \\"901\\"}"	\N	f	\N	\N
2557	SAIDA	2	\N	2025-12-29 14:21:44.453839+00	962	3	\N	2	0	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2558	SAIDA	3	Importação automática - NF: 0000001269 | Código sincronizado (1034605 -> 776) | Produto NF: DESINCROST GEL BB 5 L	2025-12-29 14:24:30.766233+00	822	3	VENDA	37	34	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1034605\\"}"	"{\\"codigo\\": \\"776\\"}"	\N	f	\N	\N
2559	SAIDA	75	Importação automática - NF: 0000004794 | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2025-12-29 14:25:06.00572+00	936	3	VENDA	370	295	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2560	SAIDA	2	Importação automática - NF: 0000004794 | Produto NF: PAPEL TOALHA BOBINA MG BRANCO 150MTS	2025-12-29 14:25:06.00572+00	938	3	VENDA	18	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2561	SAIDA	8	Importação automática - NF: 0000004794 | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2025-12-29 14:25:06.00572+00	935	3	VENDA	23	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2562	SAIDA	5	Importação automática - NF: 0000004794 | Produto NF: S B A E C TA O P P L / A L S I T X I O C 90X100X0,08 - PRETO 200LT	2025-12-29 14:25:06.00572+00	996	3	VENDA	19	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2563	SAIDA	3	Importação automática - NF: 0000004794 | Produto NF: S P A LA C S O T P IC / LIXO 75X90X0,08 - PRETO 100LT BETA	2025-12-29 14:25:06.00572+00	992	3	VENDA	21	18	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2881	ENTRADA	15	\N	2026-01-19 18:04:53.67466+00	931	3	\N	9	24	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2889	SAIDA	2	NF 0000004845 - Processamento automático - Cliente: Frete por Conta C	2026-01-19 18:36:07.962202+00	824	3	\N	87	85	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2892	SAIDA	1	NF 0000004845 - Processamento automático - Cliente: Frete por Conta C	2026-01-19 18:36:22.611798+00	822	3	\N	53	52	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2894	SAIDA	1	NF 0000004845 - Processamento automático - Cliente: Frete por Conta C	2026-01-19 18:36:51.506292+00	822	3	\N	52	51	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2895	SAIDA	2	\N	2026-01-19 18:37:12.39444+00	824	3	\N	81	79	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2898	SAIDA	2	\N	2026-01-19 18:37:54.148769+00	996	3	\N	31	29	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2903	SAIDA	4	\N	2026-01-19 18:39:02.964743+00	1013	3	\N	8	4	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2907	SAIDA	40	\N	2026-01-19 18:39:57.421129+00	1041	3	\N	136	96	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2908	SAIDA	50	\N	2026-01-19 18:40:09.693735+00	886	3	\N	100	50	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
3086	ENTRADA	4	NF None - Processamento automático	2026-01-29 18:42:00.589772+00	1022	3	\N	1	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2564	SAIDA	2	Importação automática - NF: 0000004793 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-29 14:25:31.39615+00	824	3	VENDA	116	114	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2565	SAIDA	2	Importação automática - NF: 0000004793 | Produto NF: LIMPAX DX BB5L	2025-12-29 14:25:31.39615+00	874	3	VENDA	64	62	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2566	SAIDA	2	Importação automática - NF: 0000004793 | Produto NF: REMOX BB5L	2025-12-29 14:25:31.39615+00	966	3	VENDA	15	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2567	ENTRADA	4	Importação automática - NF: 0 | Produto NF: OXIPRO FRESH LEMON BB5L	2025-12-29 14:33:29.703413+00	918	3	COMPRA	10	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2568	ENTRADA	4	Importação automática - NF: 0 | Produto NF: SANIFLOR CAPIM LIMAO BB5L	2025-12-29 14:33:29.703413+00	1012	3	COMPRA	6	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2569	ENTRADA	30	Importação automática - NF: 0 | Produto NF: SPRAY SANITIZANTE BOLSA 500ML	2025-12-29 14:33:29.703413+00	1025	3	COMPRA	38	68	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2570	ENTRADA	8	Importação automática - NF: 0 | Produto NF: SUAVITEX PRO MILK BB5L	2025-12-29 14:33:29.703413+00	1035	3	COMPRA	4	12	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2571	ENTRADA	4	Importação automática - NF: 0 | Produto NF: SUAVITEX PRO PESSEGO BB5L	2025-12-29 14:33:29.703413+00	1036	3	COMPRA	9	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2572	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (823 -> 1031605) | Produto NF: AMACITEC PRIMAVERA BB 5L	2025-12-29 14:33:29.703413+00	796	3	COMPRA	12	16	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"823\\"}"	"{\\"codigo\\": \\"1031605\\"}"	\N	f	\N	\N
2573	ENTRADA	8	Importação automática - NF: 0 | Código sincronizado (776 -> 1034605) | Produto NF: DESINCROST GEL BB5L	2025-12-29 14:33:29.703413+00	822	3	COMPRA	34	42	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"776\\"}"	"{\\"codigo\\": \\"1034605\\"}"	\N	f	\N	\N
2574	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (391 -> 1031505) | Produto NF: LAVPRO BB 5L	2025-12-29 14:33:29.703413+00	863	3	COMPRA	5	9	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"391\\"}"	"{\\"codigo\\": \\"1031505\\"}"	\N	f	\N	\N
2575	ENTRADA	2	Importação automática - NF: 0 | Código sincronizado (PROD080 -> 1032222) | Produto NF: LAVPRO DX BB 20L	2025-12-29 14:33:29.703413+00	866	3	COMPRA	2	4	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD080\\"}"	"{\\"codigo\\": \\"1032222\\"}"	\N	f	\N	\N
2576	ENTRADA	8	Importação automática - NF: 0 | Código sincronizado (221 -> 1030205) | Produto NF: LIMPA PORCELANATO BB5L	2025-12-29 14:33:29.703413+00	870	3	COMPRA	6	14	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"221\\"}"	"{\\"codigo\\": \\"1030205\\"}"	\N	f	\N	\N
2577	ENTRADA	100	Importação automática - NF: 0 | Código sincronizado (518 -> 1033005) | Produto NF: LIMPAX DX BB5L	2025-12-29 14:33:29.703413+00	874	3	COMPRA	62	162	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"518\\"}"	"{\\"codigo\\": \\"1033005\\"}"	\N	f	\N	\N
2578	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (523 -> 1027305) | Produto NF: OXIPRO NATURAL BB5L	2025-12-29 14:33:29.703413+00	919	3	COMPRA	10	14	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"523\\"}"	"{\\"codigo\\": \\"1027305\\"}"	\N	f	\N	\N
2579	ENTRADA	20	Importação automática - NF: 0 | Código sincronizado (224 -> 1017305) | Produto NF: REMOCRIL POWER BB5L	2025-12-29 14:33:29.703413+00	963	3	COMPRA	8	28	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"224\\"}"	"{\\"codigo\\": \\"1017305\\"}"	\N	f	\N	\N
2580	ENTRADA	20	Importação automática - NF: 0 | Código sincronizado (215 -> 1023705) | Produto NF: REMOX BB5L	2025-12-29 14:33:29.703413+00	966	3	COMPRA	13	33	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"215\\"}"	"{\\"codigo\\": \\"1023705\\"}"	\N	f	\N	\N
2581	ENTRADA	8	Importação automática - NF: 0 | Código sincronizado (606 -> 1025805) | Produto NF: PRAXI SABON ESPUMA ANDIROBA 5L	2025-12-29 14:33:29.703413+00	1033	3	COMPRA	5	13	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"606\\"}"	"{\\"codigo\\": \\"1025805\\"}"	\N	f	\N	\N
2582	ENTRADA	6	Importação automática - NF: 0 | Código sincronizado (910 -> 1034322) | Produto NF: SANICLOR DT BB 20L	2025-12-29 14:33:29.703413+00	1007	3	COMPRA	1	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"910\\"}"	"{\\"codigo\\": \\"1034322\\"}"	\N	f	\N	\N
2583	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD228 -> 1023305) | Produto NF: SANIFLOR LIRIOS DO CAMPO BB5L	2025-12-29 14:33:29.703413+00	1014	3	COMPRA	0	4	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD228\\"}"	"{\\"codigo\\": \\"1023305\\"}"	\N	f	\N	\N
2584	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD232 -> 1007505) | Produto NF: SANIFLOR PLUS SOFT BB 5L	2025-12-29 14:33:29.703413+00	1018	3	COMPRA	0	4	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD232\\"}"	"{\\"codigo\\": \\"1007505\\"}"	\N	f	\N	\N
2585	ENTRADA	6	Importação automática - NF: 0 | Código sincronizado (344 -> 1029355) | Produto NF: SUAVITEX BAC SP 500 BOL	2025-12-29 14:33:29.703413+00	1030	3	COMPRA	14	20	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"344\\"}"	"{\\"codigo\\": \\"1029355\\"}"	\N	f	\N	\N
2586	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (572 -> 1031305) | Produto NF: ALVITEC PE BB 5KG	2025-12-29 14:34:36.758741+00	793	3	COMPRA	7	11	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"572\\"}"	"{\\"codigo\\": \\"1031305\\"}"	\N	f	\N	\N
2587	ENTRADA	12	Importação automática - NF: 0 | Código sincronizado (8 -> 1021005) | Produto NF: DESINCROST BB5L	2025-12-29 14:34:36.758741+00	820	3	COMPRA	34	46	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"8\\"}"	"{\\"codigo\\": \\"1021005\\"}"	\N	f	\N	\N
2588	SAIDA	2	Importação automática - NF: 0000001270 | Produto NF: SEC MAQ PRO BB5L	2025-12-30 18:06:21.646519+00	1024	3	VENDA	7	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2589	SAIDA	4	Importação automática - NF: 0000001270 | Código sincronizado (1034605 -> 776) | Produto NF: DESINCROST GEL BB 5 L	2025-12-30 18:06:21.646519+00	822	3	VENDA	42	38	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1034605\\"}"	"{\\"codigo\\": \\"776\\"}"	\N	f	\N	\N
2590	SAIDA	18	Importação automática - NF: 0000004802 | Produto NF: PAPEL HIGIENICO ROLAO 8X300M (NOBRE)	2025-12-30 18:09:51.425096+00	931	3	VENDA	18	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2591	SAIDA	4	Importação automática - NF: 0000004802 | Produto NF: BAYGON ACAO TOTAL C/ CHEIRO 12X395ML	2025-12-30 18:09:51.425096+00	807	3	VENDA	6	2	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2592	SAIDA	8	Importação automática - NF: 0000004802 | Código sincronizado (BOBBEM -> 1025) | Produto NF: P C A E P LU EL L O T S O E ALHA BOBINA BEMEL 200M 100%	2025-12-30 18:09:51.425096+00	1094	3	VENDA	8	0	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"BOBBEM\\"}"	"{\\"codigo\\": \\"1025\\"}"	\N	f	\N	\N
2593	SAIDA	2	Importação automática - NF: 0000004803 | Produto NF: DESINFETANTE SANIFLOR MAX FRESH LEMON BB5L	2025-12-30 18:11:01.305869+00	1015	3	VENDA	25	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2594	SAIDA	36	Importação automática - NF: 0000004803 | Produto NF: AGUA SANITARIA CLORITO 1L	2025-12-30 18:11:01.305869+00	788	3	VENDA	59	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2595	SAIDA	19	Importação automática - NF: 0000004803 | Produto NF: ESPONJA DUPLA FACE	2025-12-30 18:11:01.305869+00	839	3	VENDA	120	101	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2596	SAIDA	5	Importação automática - NF: 0000004803 | Produto NF: S P A LA C S O T P IC / LIXO 75X90X0,03 - PRETO 100LT BETA	2025-12-30 18:11:01.305869+00	990	3	VENDA	56	51	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2597	SAIDA	2	Importação automática - NF: 0000004803 | Produto NF: PERFUMAR BREEZE BB 5L RENDE 50L	2025-12-30 18:11:01.305869+00	946	3	VENDA	8	6	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2598	SAIDA	10	Importação automática - NF: 0000004803 | Produto NF: PANO DE CHAO ALVEJADO FLANELADO 48X68	2025-12-30 18:11:01.305869+00	925	3	VENDA	469	459	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2599	SAIDA	2	Importação automática - NF: 0000004803 | Produto NF: VIDROLUX BB 5L REND 25L	2025-12-30 18:11:01.305869+00	1048	3	VENDA	9	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2600	SAIDA	2	Importação automática - NF: 0000004803 | Produto NF: DESINFETANTE SANIFLOR MAX SOFT BB 5L	2025-12-30 18:11:01.305869+00	1016	3	VENDA	25	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2601	SAIDA	10	Importação automática - NF: 0000004803 | Código sincronizado (PROD059 -> 677) | Produto NF: FIBRA P/ LIMPEZA 1X20X10 ULTRA PESADA	2025-12-30 18:11:01.305869+00	845	3	VENDA	20	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD059\\"}"	"{\\"codigo\\": \\"677\\"}"	\N	f	\N	\N
2641	SAIDA	5	Importação automática - NF: 0000004806 | Produto NF: S P A LA C S O T P IC / LIXO 55X55X0,25 - PRETO 40LT BETA	2026-01-06 14:25:00.047575+00	1001	3	VENDA	10	5	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2602	SAIDA	3	Importação automática - NF: 0000004803 | Código sincronizado (PROD135 -> 197) | Produto NF: PA COLETORA DE LIXO	2025-12-30 18:11:01.305869+00	921	3	VENDA	10	7	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD135\\"}"	"{\\"codigo\\": \\"197\\"}"	\N	f	\N	\N
2603	SAIDA	4	Importação automática - NF: 0000004803 | Código sincronizado (PROD215 -> 135) | Produto NF: S P A LA C S O T P IC / LIXO 55X55X0,25 - PRETO 40LT BETA	2025-12-30 18:11:01.305869+00	1001	3	VENDA	14	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD215\\"}"	"{\\"codigo\\": \\"135\\"}"	\N	f	\N	\N
2604	SAIDA	8	Importação automática - NF: 0000004801 | Produto NF: DETERGENTE CLORADO BB 5L	2025-12-30 18:11:37.01503+00	824	3	VENDA	114	106	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2605	SAIDA	4	Importação automática - NF: 0000004801 | Código sincronizado (1022605 -> 47) | Produto NF: DESINFETANTE SANIFLOR CAPIM LIMAO BB 5L	2025-12-30 18:11:37.01503+00	1012	3	VENDA	10	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1022605\\"}"	"{\\"codigo\\": \\"47\\"}"	\N	f	\N	\N
2606	SAIDA	16	Importação automática - NF: 0000004801 | Código sincronizado (1028105 -> 211) | Produto NF: ALUMI CROST BB 5L	2025-12-30 18:11:37.01503+00	792	3	VENDA	22	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1028105\\"}"	"{\\"codigo\\": \\"211\\"}"	\N	f	\N	\N
2607	SAIDA	4	Importação automática - NF: 0000004801 | Código sincronizado (776 -> 787) | Produto NF: DESINCROST GEL BB 5	2025-12-30 18:11:37.01503+00	822	3	VENDA	38	34	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"776\\"}"	"{\\"codigo\\": \\"787\\"}"	\N	f	\N	\N
2608	SAIDA	12	Importação automática - NF: 0000004814 | Produto NF: FLANELA CRISTAL M 40X60	2026-01-06 14:22:45.360546+00	850	3	VENDA	102	90	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2609	SAIDA	10	Importação automática - NF: 0000004814 | Produto NF: ESPONJA DUPLA FACE	2026-01-06 14:22:45.360546+00	839	3	VENDA	101	91	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2610	SAIDA	2	Importação automática - NF: 0000004814 | Produto NF: DESINFETANTE SANIFLOR MAX FRESH LEMON BB5L	2026-01-06 14:22:45.360546+00	1015	3	VENDA	23	21	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2611	SAIDA	2	Importação automática - NF: 0000004814 | Produto NF: VASSOURA PIACAVA RAINHA MAX	2026-01-06 14:22:45.360546+00	1046	3	VENDA	51	49	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2612	SAIDA	4	Importação automática - NF: 0000004814 | Produto NF: AGUASSANI BB 5L	2026-01-06 14:22:45.360546+00	789	3	VENDA	39	35	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2613	SAIDA	10	Importação automática - NF: 0000004814 | Produto NF: ACIDO MURIATICO 1L	2026-01-06 14:22:45.360546+00	787	3	VENDA	25	15	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2614	SAIDA	6	Importação automática - NF: 0000004814 | Produto NF: S P A LA C S O T P IC / LIXO 75X90X0,03 - PRETO 100LT BETA	2026-01-06 14:22:45.360546+00	990	3	VENDA	51	45	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2615	SAIDA	5	Importação automática - NF: 0000004814 | Código sincronizado (PROD140 -> 457) | Produto NF: PANO DE CHAO XADREZ 50X75	2026-01-06 14:22:45.360546+00	926	3	VENDA	354	349	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD140\\"}"	"{\\"codigo\\": \\"457\\"}"	\N	f	\N	\N
2616	SAIDA	4	Importação automática - NF: 0000004814 | Código sincronizado (PROD082 -> 250) | Produto NF: LIMPA ALUMINIO ECONOMICO 500ML	2026-01-06 14:22:45.360546+00	868	3	VENDA	31	27	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD082\\"}"	"{\\"codigo\\": \\"250\\"}"	\N	f	\N	\N
2617	SAIDA	15	Importação automática - NF: 0000004814 | Código sincronizado (PROD191 -> 942) | Produto NF: SABAO EM PO ALA FLOR DE LIS 400G	2026-01-06 14:22:45.360546+00	977	3	VENDA	110	95	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD191\\"}"	"{\\"codigo\\": \\"942\\"}"	\N	f	\N	\N
2618	SAIDA	2	Importação automática - NF: 0000004814 | Código sincronizado (1028405 -> 124) | Produto NF: OXIPRO FRESH LEMON BB5L	2026-01-06 14:22:45.360546+00	918	3	VENDA	14	12	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1028405\\"}"	"{\\"codigo\\": \\"124\\"}"	\N	f	\N	\N
2619	SAIDA	2	Importação automática - NF: 0000004814 | Código sincronizado (PROD041 -> 316) | Produto NF: DISCO LIMPADOR 410MM VERDE (NOBRE)	2026-01-06 14:22:45.360546+00	827	3	VENDA	7	5	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD041\\"}"	"{\\"codigo\\": \\"316\\"}"	\N	f	\N	\N
2620	SAIDA	2	Importação automática - NF: 0000004814 | Código sincronizado (PROD259 -> 198) | Produto NF: VASSOURA LINDONA	2026-01-06 14:22:45.360546+00	1045	3	VENDA	12	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD259\\"}"	"{\\"codigo\\": \\"198\\"}"	\N	f	\N	\N
2621	SAIDA	8	Importação automática - NF: 0000004814 | Código sincronizado (1028205 -> 54) | Produto NF: SABONETE SUAVITEX PRO MILK BB 5L	2026-01-06 14:22:45.360546+00	1035	3	VENDA	12	4	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1028205\\"}"	"{\\"codigo\\": \\"54\\"}"	\N	f	\N	\N
2622	SAIDA	4	Importação automática - NF: 0000004814 | Código sincronizado (PROD190 -> 636) | Produto NF: SABAO EM BARRA YPE 5x160G	2026-01-06 14:22:45.360546+00	976	3	VENDA	13	9	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD190\\"}"	"{\\"codigo\\": \\"636\\"}"	\N	f	\N	\N
2623	SAIDA	12	Importação automática - NF: 0000004813 | Produto NF: AGUASSANI BB 5L	2026-01-06 14:24:31.28195+00	789	3	VENDA	35	23	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2624	SAIDA	36	Importação automática - NF: 0000004813 | Produto NF: FLANELA CRISTAL M 40X60	2026-01-06 14:24:31.28195+00	850	3	VENDA	90	54	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2625	SAIDA	20	Importação automática - NF: 0000004813 | Produto NF: PANO DE CHAO XADREZ 50X75	2026-01-06 14:24:31.28195+00	926	3	VENDA	349	329	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2626	SAIDA	5	Importação automática - NF: 0000004813 | Produto NF: LIMPA ALUMINIO ECONOMICO 500ML	2026-01-06 14:24:31.28195+00	868	3	VENDA	27	22	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2627	SAIDA	10	Importação automática - NF: 0000004813 | Produto NF: ESPONJA DUPLA FACE	2026-01-06 14:24:31.28195+00	839	3	VENDA	91	81	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2628	SAIDA	35	Importação automática - NF: 0000004813 | Produto NF: SABAO EM PO ALA FLOR DE LIS 400G	2026-01-06 14:24:31.28195+00	977	3	VENDA	95	60	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2629	SAIDA	5	Importação automática - NF: 0000004813 | Produto NF: ACIDO MURIATICO 1L	2026-01-06 14:24:31.28195+00	787	3	VENDA	15	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2630	SAIDA	10	Importação automática - NF: 0000004813 | Produto NF: S P A LA C S O T P IC / LIXO 60X70X0,025 - PRETO 60LT BETA	2026-01-06 14:24:31.28195+00	1002	3	VENDA	58	48	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2631	SAIDA	15	Importação automática - NF: 0000004813 | Produto NF: S P A LA C S O T P IC / LIXO 75X90X0,03 - PRETO 100LT BETA	2026-01-06 14:24:31.28195+00	990	3	VENDA	45	30	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2632	SAIDA	2	Importação automática - NF: 0000004813 | Produto NF: OXIPRO SOFT BB 5L	2026-01-06 14:24:31.28195+00	920	3	VENDA	10	8	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2633	SAIDA	1	Importação automática - NF: 0000004813 | Produto NF: DISCO LIMPADOR 410MM VERDE (NOBRE)	2026-01-06 14:24:31.28195+00	827	3	VENDA	5	4	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2634	SAIDA	2	Importação automática - NF: 0000004813 | Produto NF: SACO P/ LIXO INFECTANTE 59X62X 30L LEVE	2026-01-06 14:24:31.28195+00	988	3	VENDA	9	7	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2635	SAIDA	10	Importação automática - NF: 0000004813 | Código sincronizado (PROD062 -> 103) | Produto NF: FIBRA DE LIMPEZA PESADA BETTANIN	2026-01-06 14:24:31.28195+00	848	3	VENDA	511	501	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD062\\"}"	"{\\"codigo\\": \\"103\\"}"	\N	f	\N	\N
2636	SAIDA	7	Importação automática - NF: 0000004813 | Código sincronizado (1023005 -> 60) | Produto NF: SABONETE SUAVITEX PESSEGO BB 5 L	2026-01-06 14:24:31.28195+00	1036	3	VENDA	13	6	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"1023005\\"}"	"{\\"codigo\\": \\"60\\"}"	\N	f	\N	\N
2637	SAIDA	90	Importação automática - NF: 0000004806 | Produto NF: PAPEL TOALHA MG KING SOFT 640 FOLHAS	2026-01-06 14:25:00.047575+00	936	3	VENDA	295	205	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2638	SAIDA	3	Importação automática - NF: 0000004806 | Produto NF: PAPEL TOALHA BOBINA MG BRANCO 150MTS	2026-01-06 14:25:00.047575+00	938	3	VENDA	16	13	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2639	SAIDA	4	Importação automática - NF: 0000004806 | Produto NF: PAPEL HIGIENICO MG BRANCO 300MTS	2026-01-06 14:25:00.047575+00	935	3	VENDA	15	11	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2640	SAIDA	5	Importação automática - NF: 0000004806 | Produto NF: S P A LA C S O T P IC / LIXO 60X70X0,025 - PRETO 60LT BETA	2026-01-06 14:25:00.047575+00	1002	3	VENDA	48	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2642	ENTRADA	200	entrada	2026-01-07 14:04:49.10423+00	895	3	\N	0	200	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2643	ENTRADA	72	entrada	2026-01-07 14:05:06.365291+00	1040	3	\N	66	138	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2644	ENTRADA	6	entrada	2026-01-07 14:05:32.459435+00	834	3	\N	6	12	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2645	SAIDA	2	\N	2026-01-07 14:13:30.697599+00	835	3	\N	17	15	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2646	ENTRADA	9	\N	2026-01-07 14:14:24.60857+00	931	3	\N	0	9	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2647	ENTRADA	1	\N	2026-01-08 12:29:18.355429+00	935	3	\N	11	12	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2648	ENTRADA	1	\N	2026-01-08 12:29:21.982116+00	935	3	\N	12	13	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2649	SAIDA	1	\N	2026-01-08 12:29:30.781264+00	938	3	\N	13	12	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2650	ENTRADA	25	\N	2026-01-08 12:29:40.458538+00	936	3	\N	205	230	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2651	ENTRADA	10	\N	2026-01-08 12:29:46.878914+00	936	3	\N	230	240	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2652	ENTRADA	4	\N	2026-01-08 12:37:28.619773+00	939	3	\N	2	6	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2653	SAIDA	99	\N	2026-01-08 17:49:47.760851+00	940	3	\N	218	119	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2654	ENTRADA	10	\N	2026-01-08 17:50:30.616742+00	1062	3	\N	5	15	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2655	ENTRADA	10	\N	2026-01-08 17:57:46.302267+00	993	3	\N	0	10	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2656	ENTRADA	10	\N	2026-01-08 17:58:01.048289+00	1002	3	\N	43	53	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2657	ENTRADA	30	\N	2026-01-08 17:58:14.029191+00	1001	3	\N	5	35	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2658	ENTRADA	10	\N	2026-01-08 17:58:28.049131+00	996	3	\N	14	24	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2659	ENTRADA	10	\N	2026-01-08 17:58:45.896491+00	985	3	\N	11	21	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2660	ENTRADA	10	\N	2026-01-08 17:59:04.160119+00	989	3	\N	14	24	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2661	ENTRADA	10	\N	2026-01-08 17:59:12.723365+00	988	3	\N	7	17	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2662	SAIDA	3	\N	2026-01-08 18:27:58.942748+00	789	3	\N	23	20	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2663	ENTRADA	8	\N	2026-01-08 18:28:17.315969+00	792	3	\N	6	14	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2664	SAIDA	2	\N	2026-01-08 18:28:35.358523+00	820	3	\N	46	44	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2665	ENTRADA	19	\N	2026-01-08 18:28:51.731996+00	822	3	\N	34	53	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2666	SAIDA	18	\N	2026-01-08 18:29:10.456858+00	824	3	\N	106	88	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2667	ENTRADA	19	\N	2026-01-08 18:29:26.980721+00	873	3	\N	12	31	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2668	ENTRADA	2	\N	2026-01-08 18:29:34.870499+00	874	3	\N	162	164	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2669	SAIDA	4	\N	2026-01-08 18:31:03.088425+00	1067	3	\N	9	5	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2670	SAIDA	1	\N	2026-01-08 18:31:19.755926+00	862	3	\N	26	25	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2671	SAIDA	4	\N	2026-01-08 18:31:53.607399+00	963	3	\N	28	24	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2672	SAIDA	10	\N	2026-01-08 18:32:18.033876+00	966	3	\N	33	23	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2673	ENTRADA	42	\N	2026-01-08 18:32:33.259491+00	1070	3	\N	0	42	CONFIRMADO	\N	\N	\N	TRANSFERENCIA_INTERNA	\N	\N	\N	\N	f	\N	\N
2674	SAIDA	4	\N	2026-01-08 18:32:49.883262+00	1007	3	\N	7	3	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2675	SAIDA	2	\N	2026-01-08 18:33:00.481978+00	1007	3	\N	3	1	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2676	ENTRADA	4	\N	2026-01-08 18:33:59.760184+00	1007	3	\N	1	5	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2677	ENTRADA	2	\N	2026-01-08 18:34:27.954761+00	903	3	\N	5	7	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2678	SAIDA	2	\N	2026-01-08 18:34:42.549237+00	903	3	\N	7	5	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2679	SAIDA	2	\N	2026-01-08 18:34:52.585335+00	903	3	\N	5	3	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2680	SAIDA	1	\N	2026-01-08 18:35:48.459432+00	908	3	\N	2	1	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2681	SAIDA	2	\N	2026-01-08 18:36:04.804868+00	1100	3	\N	5	3	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2682	SAIDA	2	\N	2026-01-08 18:36:27.913829+00	1026	3	\N	11	9	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2683	ENTRADA	1	\N	2026-01-08 18:37:15.374387+00	824	3	\N	88	89	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2684	ENTRADA	1	\N	2026-01-08 18:37:23.888365+00	874	3	\N	164	165	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2685	SAIDA	3	\N	2026-01-08 18:37:55.162739+00	1028	3	\N	10	7	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2686	ENTRADA	37	\N	2026-01-08 18:38:05.006111+00	1030	3	\N	20	57	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2687	SAIDA	20	\N	2026-01-08 18:38:11.55442+00	1030	3	\N	57	37	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2688	ENTRADA	13	\N	2026-01-08 18:38:57.532076+00	1036	3	\N	6	19	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2689	ENTRADA	5	\N	2026-01-08 18:41:39.231767+00	1035	3	\N	4	9	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2690	ENTRADA	5	\N	2026-01-08 18:41:57.460062+00	1035	3	\N	9	14	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2691	ENTRADA	5	\N	2026-01-08 18:42:50.483214+00	1036	3	\N	19	24	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2692	SAIDA	3	\N	2026-01-08 18:43:08.953631+00	978	3	\N	8	5	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2693	SAIDA	6	\N	2026-01-08 18:44:27.240974+00	796	3	\N	16	10	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2694	ENTRADA	1	\N	2026-01-08 18:44:37.781888+00	859	3	\N	6	7	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2695	ENTRADA	2	\N	2026-01-08 18:45:07.30439+00	866	3	\N	4	6	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2696	ENTRADA	5	\N	2026-01-08 18:45:26.091183+00	863	3	\N	9	14	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2697	SAIDA	8	\N	2026-01-08 18:45:47.342676+00	813	3	\N	12	4	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2698	SAIDA	4	\N	2026-01-08 18:46:03.10193+00	870	3	\N	14	10	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2699	SAIDA	2	\N	2026-01-08 18:46:15.437122+00	952	3	\N	6	4	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2700	SAIDA	2	\N	2026-01-08 18:46:48.765198+00	853	3	\N	17	15	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2701	SAIDA	3	\N	2026-01-08 18:47:02.974686+00	856	3	\N	9	6	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2702	SAIDA	14	\N	2026-01-08 18:47:24.185765+00	1025	3	\N	68	54	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2703	ENTRADA	7	\N	2026-01-08 18:48:21.005127+00	918	3	\N	12	19	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2704	ENTRADA	7	\N	2026-01-08 18:48:36.277917+00	919	3	\N	14	21	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2705	ENTRADA	12	\N	2026-01-08 18:48:48.880024+00	920	3	\N	8	20	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2706	SAIDA	1	\N	2026-01-08 18:49:46.657748+00	946	3	\N	6	5	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2707	SAIDA	3	\N	2026-01-08 18:50:28.632044+00	951	3	\N	7	4	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2708	ENTRADA	4	\N	2026-01-08 18:50:53.338915+00	1010	3	\N	0	4	CONFIRMADO	\N	\N	\N	TRANSFERENCIA_INTERNA	\N	\N	\N	\N	f	\N	\N
2709	ENTRADA	4	\N	2026-01-08 18:51:01.690303+00	1011	3	\N	6	10	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2710	ENTRADA	8	\N	2026-01-08 18:51:11.571495+00	1013	3	\N	0	8	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2711	SAIDA	5	\N	2026-01-08 18:51:35.127283+00	1015	3	\N	21	16	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2712	ENTRADA	1	\N	2026-01-08 18:51:42.960318+00	1015	3	\N	16	17	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2713	SAIDA	3	\N	2026-01-08 18:51:54.126642+00	1016	3	\N	23	20	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2714	SAIDA	5	\N	2026-01-08 18:52:08.627863+00	1017	3	\N	5	0	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2715	SAIDA	4	\N	2026-01-08 18:52:43.152547+00	860	3	\N	16	12	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2716	SAIDA	2	\N	2026-01-08 18:53:03.136835+00	1048	3	\N	7	5	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2717	SAIDA	8	\N	2026-01-08 18:58:47.660848+00	817	3	\N	158	150	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2718	ENTRADA	18	\N	2026-01-08 18:58:56.543335+00	818	3	\N	132	150	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2719	ENTRADA	125	\N	2026-01-08 18:59:05.614505+00	819	3	\N	143	268	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2720	SAIDA	125	\N	2026-01-08 18:59:12.015893+00	819	3	\N	268	143	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2721	SAIDA	25	\N	2026-01-08 18:59:19.42105+00	819	3	\N	143	118	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2722	SAIDA	11	\N	2026-01-08 18:59:55.189089+00	788	3	\N	23	12	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2723	ENTRADA	120	\N	2026-01-08 19:00:02.497813+00	788	3	\N	12	132	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2724	ENTRADA	60	\N	2026-01-08 19:00:41.988109+00	791	3	\N	24	84	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2725	ENTRADA	48	\N	2026-01-08 19:01:57.376184+00	825	3	\N	17	65	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2726	ENTRADA	48	\N	2026-01-08 19:04:41.332767+00	976	3	\N	9	57	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2727	ENTRADA	54	\N	2026-01-08 19:05:06.360367+00	977	3	\N	60	114	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2728	ENTRADA	36	\N	2026-01-08 19:05:16.53846+00	1045	3	\N	10	46	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2729	ENTRADA	72	\N	2026-01-08 19:05:47.517778+00	850	3	\N	54	126	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2730	ENTRADA	120	\N	2026-01-08 19:05:58.193781+00	839	3	\N	81	201	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2731	ENTRADA	4	\N	2026-01-08 19:06:42.864966+00	806	3	\N	1	5	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2732	ENTRADA	36	\N	2026-01-08 19:07:21.32199+00	836	3	\N	1	37	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2733	ENTRADA	20	Importação automática - NF: 0 | Produto NF: DESINCROST BB5L	2026-01-09 12:19:31.442124+00	820	3	COMPRA	44	64	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2734	ENTRADA	20	Importação automática - NF: 0 | Produto NF: REMOX BB5L	2026-01-09 12:19:31.442124+00	966	3	COMPRA	23	43	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2735	ENTRADA	5	Importação automática - NF: 0 | Produto NF: SANICLOR DT BB 20L	2026-01-09 12:19:31.442124+00	1007	3	COMPRA	5	10	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2883	ENTRADA	10	\N	2026-01-19 18:25:38.496106+00	993	3	\N	8	18	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2736	ENTRADA	20	Importação automática - NF: 0 | Código sincronizado (43 -> 1001405) | Produto NF: DETERGENTE CLORADO BB 5L	2026-01-09 12:19:31.442124+00	824	3	COMPRA	89	109	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"43\\"}"	"{\\"codigo\\": \\"1001405\\"}"	\N	f	\N	\N
2737	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (10 -> 1018105) | Produto NF: GEL ANTISSEPTICO BB5L	2026-01-09 12:19:31.442124+00	856	3	COMPRA	6	10	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"10\\"}"	"{\\"codigo\\": \\"1018105\\"}"	\N	f	\N	\N
2738	ENTRADA	8	Importação automática - NF: 0 | Código sincronizado (17 -> 1003905) | Produto NF: LIMPAX BB 5L	2026-01-09 12:19:31.442124+00	873	3	COMPRA	31	39	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"17\\"}"	"{\\"codigo\\": \\"1003905\\"}"	\N	f	\N	\N
2739	ENTRADA	6	Importação automática - NF: 0 | Código sincronizado (641 -> 1033541) | Produto NF: MULTIBAC PRATIK FR 500ML GATIL	2026-01-09 12:19:31.442124+00	1071	3	COMPRA	2	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"641\\"}"	"{\\"codigo\\": \\"1033541\\"}"	\N	f	\N	\N
2740	ENTRADA	12	Importação automática - NF: 0 | Código sincronizado (191 -> 1027105) | Produto NF: SANICLOR BB5L	2026-01-09 12:19:31.442124+00	1006	3	COMPRA	21	33	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"191\\"}"	"{\\"codigo\\": \\"1027105\\"}"	\N	f	\N	\N
2741	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (PROD194 -> 1005705) | Produto NF: SUAVITEX DX MICRO ESF BB 5L	2026-01-09 12:19:31.442124+00	980	3	COMPRA	7	11	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD194\\"}"	"{\\"codigo\\": \\"1005705\\"}"	\N	f	\N	\N
2742	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (54 -> 1028205) | Produto NF: SUAVITEX PRO MILK BB5L	2026-01-09 12:19:31.442124+00	1035	3	COMPRA	14	18	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"54\\"}"	"{\\"codigo\\": \\"1028205\\"}"	\N	f	\N	\N
2743	ENTRADA	4	Importação automática - NF: 0 | Código sincronizado (60 -> 1023005) | Produto NF: SUAVITEX PRO PESSEGO BB5L	2026-01-09 12:19:31.442124+00	1036	3	COMPRA	24	28	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"60\\"}"	"{\\"codigo\\": \\"1023005\\"}"	\N	f	\N	\N
2744	ENTRADA	8	Importação automática - NF: 0 | Código sincronizado (23 -> 1003305) | Produto NF: SANILUX BB 5L	2026-01-09 12:19:31.442124+00	1021	3	COMPRA	0	8	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"23\\"}"	"{\\"codigo\\": \\"1003305\\"}"	\N	f	\N	\N
2745	SAIDA	4	\N	2026-01-09 12:19:59.843539+00	980	3	\N	11	7	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2746	ENTRADA	4	\N	2026-01-09 12:20:14.90224+00	978	3	\N	5	9	CONFIRMADO	\N	\N	\N	TRANSFERENCIA_INTERNA	\N	\N	\N	\N	f	\N	\N
2747	SAIDA	3	Importação automática - NF: 0000004816 | Produto NF: VASSOURA PIACAVA RAINHA MAX	2026-01-09 13:21:09.661437+00	1046	3	VENDA	49	46	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2748	SAIDA	6	Importação automática - NF: 0000004816 | Produto NF: SABAO EM PO ALA FLOR DE LIS 400G	2026-01-09 13:21:09.661437+00	977	3	VENDA	114	108	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2749	SAIDA	1	Importação automática - NF: 0000004816 | Produto NF: ALCOOL SAFRA 5L	2026-01-09 13:21:09.661437+00	1062	3	VENDA	15	14	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2750	SAIDA	1	Importação automática - NF: 0000004816 | Produto NF: SABAO EM BARRA YPE 5x160G	2026-01-09 13:21:09.661437+00	976	3	VENDA	57	56	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2751	SAIDA	12	Importação automática - NF: 0000004816 | Produto NF: AGUA SANITARIA CLORITO 1L	2026-01-09 13:21:09.661437+00	788	3	VENDA	132	120	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2752	SAIDA	4	Importação automática - NF: 0000004816 | Código sincronizado (PERS-1764877856255-e1c4760c -> 1028) | Produto NF: L N I O X B E R IR E A PLASTICA COM PEDAL 30L BRANCA -	2026-01-09 13:21:09.661437+00	1091	3	VENDA	4	0	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PERS-1764877856255-e1c4760c\\"}"	"{\\"codigo\\": \\"1028\\"}"	\N	f	\N	\N
2753	SAIDA	3	\N	2026-01-09 13:21:29.1766+00	803	3	\N	47	44	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2754	SAIDA	1	\N	2026-01-09 13:22:20.65922+00	993	3	\N	10	9	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2755	SAIDA	15	Importação automática - NF: 0000004815 | Produto NF: LUVA NITRILICA AZUL SEM PO CX C/ 100UN. M	2026-01-09 13:23:34.177546+00	889	3	VENDA	104	89	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2756	SAIDA	50	Importação automática - NF: 0000004815 | Produto NF: LUVA NITRILICA PRETA SEM PO CX C/ 100UN. G	2026-01-09 13:23:34.177546+00	886	3	VENDA	50	0	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2757	SAIDA	8	Importação automática - NF: 0000004815 | Produto NF: S B A E C TA O P P L / A L S I T X I O C 90X100X0,08 - PRETO 200LT	2026-01-09 13:23:34.177546+00	996	3	VENDA	24	16	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2758	SAIDA	5	Importação automática - NF: 0000004815 | Código sincronizado (PROD005 -> 491) | Produto NF: ALCOOL LIQ. 70% 1L	2026-01-09 13:23:34.177546+00	791	3	VENDA	84	79	CONFIRMADO	\N	\N	\N	\N	\N	"{\\"codigo\\": \\"PROD005\\"}"	"{\\"codigo\\": \\"491\\"}"	\N	f	\N	\N
2886	ENTRADA	10	\N	2026-01-19 18:28:50.083593+00	1001	3	\N	27	37	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2887	ENTRADA	20	\N	2026-01-19 18:29:01.295814+00	996	3	\N	11	31	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2888	ENTRADA	350	\N	2026-01-19 18:29:15.350028+00	936	3	\N	150	500	CONFIRMADO	\N	\N	\N	AJUSTE_FISICO	\N	\N	\N	\N	f	\N	\N
2890	SAIDA	1	NF 0000004845 - Processamento automático - Cliente: Frete por Conta C	2026-01-19 18:36:07.971168+00	822	3	\N	54	53	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
2897	SAIDA	2	\N	2026-01-19 18:37:38.370571+00	859	3	\N	7	5	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
2902	ENTRADA	4	\N	2026-01-19 18:38:52.972326+00	1011	3	\N	10	14	CONFIRMADO	\N	\N	\N	CARREGAMENTO	\N	\N	\N	\N	f	\N	\N
3087	ENTRADA	8	NF None - Processamento automático	2026-01-29 18:42:00.664988+00	1024	3	\N	28	36	CONFIRMADO	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N
\.


--
-- Data for Name: orcamento_itens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orcamento_itens (id, quantidade, preco_unitario_congelado, orcamento_id, produto_id) FROM stdin;
1	1	0	1	815
2	1	0	1	789
3	1	0	1	934
4	1	118.88	2	822
5	1	0	2	873
6	1	135	2	824
419	3	4.34	41	926
420	3	4.5	41	977
421	4	38.7	41	990
422	5	17.92	41	983
423	8	0.97	41	839
424	3	89.6	41	1035
431	6	3.29	42	788
432	6	143.87	42	792
433	3	9.99	42	1086
434	3	5.32	47	1079
435	10	5.33	47	1087
436	50	6.32	47	817
437	15	77.3	48	931
438	15	103.21	48	937
439	5	51.9	49	993
440	4	20.25	49	1002
441	6	38.7	49	990
442	8	14.55	49	1001
443	4	89.6	49	1036
257	2	57.68	25	935
258	16	11.09	25	936
259	6	126	25	824
260	4	180	25	862
261	4	132	25	1016
262	5	11.66	25	1046
263	2	93.85	25	995
264	3	20.25	25	1002
265	1	149.85	25	999
266	12	2.92	25	943
267	10	15.4	25	1072
268	2	20	25	1074
269	2	37.8	25	1073
270	6	20	25	1075
444	2	2.93	49	804
445	5	4.5	49	977
446	10	11.7	49	791
447	20	3.12	49	943
448	30	0.97	49	839
449	3	11.05	49	890
450	4	5.87	49	884
451	5	4.5	49	1088
452	8	5.32	50	1079
453	30	5.33	50	1087
456	24	68.91	52	873
274	5	3.29	29	788
275	2	47.09	29	789
276	2	11.7	29	791
277	2	148.53	29	792
278	2	101.4	30	980
279	3	213.53	30	862
719	12	29.36	77	1025
735	4	132	31	1016
736	2	20	31	1074
737	6	126	31	824
738	15	11.09	31	936
739	2	57.6	31	1066
740	3	20.25	31	1002
741	2	93.83	31	995
742	36	3.12	31	943
743	5	11.66	31	1046
744	10	18.9	31	1072
745	30	3.36	31	845
746	6	3.5	31	916
762	1	14.55	78	1001
763	7	51.9	78	993
764	6	27	78	894
765	18	24.4	78	893
766	2	15.34	78	1041
767	50	3.29	78	788
768	24	12.89	78	791
769	2	95.05	78	1011
770	5	90.31	78	874
771	8	120.81	78	876
772	2	156.07	78	966
773	3	112.69	78	822
774	1	143.87	78	792
317	5	77.3	34	931
318	48	19.3	34	940
319	2	24.92	34	984
320	4	17.92	34	983
321	4	70.5	34	991
322	1	139.04	34	951
323	2	47.09	34	789
324	1	121.9	34	824
325	10	2.91	34	825
326	12	0.97	34	839
327	75	6.32	34	817
328	50	3.99	34	819
329	1	58.8	34	1062
330	2	34.59	34	853
331	5	16.8	34	976
332	4	2.91	34	850
333	1	11.05	34	890
334	4	24.33	34	881
335	6	7.69	35	925
336	2	58.8	35	1062
337	2	14.92	35	802
338	2	165.94	35	920
339	2	139.04	35	951
340	1	77.3	35	931
341	6	18.13	35	940
342	4	2.91	35	850
343	4	2.7	35	823
344	1	20.3	35	960
345	6	7.69	36	925
346	2	58.8	36	1062
347	2	14.92	36	802
348	2	165.94	36	920
349	2	139.4	36	951
350	1	77.3	36	931
351	6	19.3	36	940
352	4	2.91	36	850
353	4	2.91	36	825
354	1	20.3	36	960
355	1	226.8	37	812
356	5	38.2	37	827
357	5	36.12	37	828
358	10	3.12	37	848
359	1	27.93	37	1038
360	1	24.38	37	809
361	1	4	38	1078
775	3	89.6	78	1035
776	10	7.76	78	1097
777	24	6.36	78	882
778	12	6.36	78	881
779	80	3.36	78	845
780	2	111.51	78	928
781	80	2.93	78	804
387	1	165.94	39	918
388	10	14.55	39	1001
389	40	18.78	39	940
390	10	98.55	39	1003
391	9	95.42	39	1035
392	1	95.79	39	1019
393	1	84.35	39	1048
406	60	3.29	40	788
407	60	11.7	40	791
408	10	90.31	40	873
409	5	156.07	40	966
410	10	112.69	40	822
411	10	89.7	40	1032
412	12	6.13	40	882
413	12	6.13	40	881
414	60	3.12	40	848
415	2	111.51	40	928
416	8	59.7	40	933
457	12	181.81	52	820
458	8	149.31	52	966
459	1	189.42	52	1024
460	25	110.5	53	874
461	3	101.17	53	822
462	6	31.22	53	1030
463	1	559.17	54	1089
464	1	559.17	54	1090
465	1	559.17	54	1091
466	1	559.17	54	1092
467	10	103.21	51	937
468	8	77.3	51	931
469	72	3.29	55	788
470	12	5.37	55	787
471	20	58.8	55	1062
472	1	123.15	55	1015
473	6	100.79	55	874
474	2	131.29	55	824
475	12	370.18	55	876
476	3	162.22	55	966
477	3	1	55	821
478	2	89.6	55	1035
479	2	89.6	55	1028
480	2	111.51	55	928
487	3	46.67	56	1071
488	2	293.63	56	904
489	2	43.5	57	1095
490	1	72.65	58	1048
491	2	138.5	59	1021
492	60	3.29	60	788
493	12	5.37	60	787
494	24	11.7	60	791
495	3	90.31	60	874
496	2	156.07	60	966
497	2	89.6	60	1036
498	1	176.82	60	1024
499	12	3.43	60	879
500	2	111.51	60	928
501	30	2.93	60	804
502	8	57.68	60	935
511	88	3.29	61	788
512	12	5.37	61	787
513	80	11.7	61	791
514	1	95.05	61	1010
515	5	90.31	61	874
516	3	131.29	61	824
517	4	120.81	61	876
518	3	156.07	61	966
519	3	112.79	61	822
520	2	89.6	61	1035
521	4	176.82	61	1024
522	12	5.87	61	884
523	30	1.5	61	847
524	80	3.12	61	848
525	12	5.87	61	883
526	2	111.51	61	928
527	30	2.93	61	804
528	8	57.68	61	935
529	1	14.55	62	1001
530	7	51.9	62	993
531	1	27	62	894
532	12	24.4	62	893
533	2	15.34	62	1041
539	4	24.56	32	809
540	4	36.48	32	968
545	12	41.58	66	789
546	36	2.91	66	850
547	20	4.34	66	926
548	10	3.12	66	848
549	5	3.15	66	868
550	10	0.97	66	839
551	35	4.5	66	977
552	5	5.37	66	787
553	10	20.25	66	1002
554	15	38.7	66	990
555	3	125.48	66	1016
556	2	136.39	66	920
557	7	73.66	66	1035
558	7	73.66	66	1036
559	1	35	66	827
560	10	16.8	66	976
561	42	27.1	67	1025
562	1	128.11	67	856
563	30	5.33	68	1087
564	40	22.39	68	1104
565	120	5.33	69	1087
566	280	22.39	69	1104
567	1	46.26	65	853
568	1	27.39	65	855
569	1	158.13	65	856
570	5	263.2	64	1103
571	2	136.22	70	824
572	2	100.79	70	874
573	2	154.8	70	966
574	1	332.9	71	1022
587	20	52.95	63	985
588	10	4.5	63	977
589	10	0.97	63	839
590	2	154.8	63	966
591	10	2.91	63	825
608	2	132.5	33	1015
609	10	3.36	33	845
610	36	3.29	33	788
611	3	45.77	33	921
612	19	0.97	33	839
613	30	77.3	33	931
614	5	38.7	33	990
615	2	132.54	33	946
616	10	7.69	33	925
617	2	83.84	33	1048
618	5	20.25	33	1002
619	2	132.5	33	1016
620	6	38.2	33	827
621	8	102.9	33	937
622	1	523.5	72	1106
623	1	523.5	72	1107
624	25	6.32	73	817
625	2	165.94	73	920
626	1	77.3	73	931
627	6	7.69	73	925
628	3	139.4	73	951
629	2	0.97	73	839
630	3	2.91	73	850
631	1	14.92	73	802
632	1	24.92	73	984
633	1	20	73	960
634	1	15.51	73	1045
635	1	10.5	73	836
636	6	2.91	73	825
654	5	51.9	75	993
655	80	3.29	75	788
656	12	5.37	75	787
657	80	11.7	75	791
658	3	106.73	75	874
659	3	136.22	75	824
660	3	154.8	75	966
661	3	112.69	75	822
662	2	89.6	75	1036
663	1	79.18	75	1006
664	12	6.36	75	882
665	60	3.12	75	848
666	12	6.36	75	881
667	2	111.51	75	928
668	40	2.93	75	804
669	8	57.68	75	935
718	7	294.43	76	813
747	2	95.05	74	1010
748	4	5.91	74	850
749	6	23.52	74	934
750	1	16.69	74	803
751	5	28.38	74	941
752	20	5.38	74	823
753	10	4.34	74	926
754	15	1.35	74	839
755	5	7.29	74	788
756	4	17.27	74	807
757	8	4.7	74	944
758	6	7.87	74	885
759	1	19.86	74	1046
760	2	37.69	74	990
761	1	19.87	74	1045
782	10	11.66	78	1046
783	36	3.29	79	788
784	4	158.13	79	856
785	84	12.89	79	791
786	6	34.5	79	797
787	20	2.93	79	804
788	6	12.2	79	1096
789	6	7.76	79	1097
790	8	24.38	79	809
791	48	10.5	79	816
792	72	2.91	79	825
793	8	10.5	79	836
794	8	3.5	79	837
795	100	0.97	79	839
796	10	3.12	79	848
797	10	15.27	79	807
798	1	83.84	79	1048
799	8	8.39	79	877
800	12	6.36	79	881
801	12	6.36	79	882
802	20	4.5	79	1088
803	15	17.1	79	902
804	15	20	79	960
805	8	39.36	79	957
806	30	4.06	79	914
807	6	45.77	79	921
808	60	7.69	79	925
809	80	3.12	79	943
810	180	17.44	79	852
811	20	13.02	79	973
812	50	4.5	79	977
813	8	89.6	79	1036
814	8	88.99	79	1033
815	12	38.7	79	990
816	12	51.9	79	993
817	10	14.55	79	1001
818	10	20.25	79	1002
819	60	4.6	79	1040
820	8	33.46	79	1043
821	8	11.66	79	1046
822	12	11.05	79	890
823	12	11.05	79	891
838	60	5.33	81	1087
839	12	6.89	81	1079
840	40	22.39	81	1104
841	275	7.01	81	818
842	20	5.22	81	897
843	3	60	82	857
844	3	33.75	82	1108
845	1	150.14	82	918
846	1	165.94	82	920
847	1	95.05	82	1010
848	1	97.77	82	1013
849	1125	7.01	80	818
850	560	22.39	80	1104
851	360	5.33	80	1087
852	16	6.89	80	1079
853	4	165.94	80	920
854	18	111.51	80	928
855	4	95.05	80	1010
856	4	97.77	80	1013
857	17	77.3	80	931
858	23	99.75	80	1094
859	4	150.14	80	918
860	6	33.75	80	1108
861	6	60	80	857
862	20	5.22	80	897
863	30	77.3	83	931
864	45	99.75	83	1094
865	12	3.29	84	788
866	4	158.13	84	856
867	24	12.89	84	791
868	24	2.91	84	825
869	6	10.5	84	836
870	6	3.5	84	837
871	60	0.97	84	839
872	1	83.84	84	1048
873	10	4.5	84	1088
874	8	6.36	84	881
875	8	6.36	84	882
876	8	11.05	84	890
877	8	11.05	84	891
878	8	34.5	84	797
879	10	20	84	960
880	10	4.06	84	914
881	15	7.69	84	925
882	6	111.51	84	928
883	50	3.12	84	943
884	6	26.35	84	970
885	10	13.02	84	973
886	10	4.5	84	977
887	8	89.6	84	1036
888	8	38.7	84	990
889	10	14.55	84	1001
890	8	20.25	84	1002
891	60	4.6	84	1040
892	6	33.46	84	1043
893	1	198.1	85	966
894	1	145.87	85	792
895	1	332.9	85	1022
896	5	88.2	86	830
897	18	19.13	87	940
898	2	175	87	930
899	50	7.01	87	818
900	4	13.75	87	1109
901	2	60	87	857
902	2	30.75	87	858
903	6	57.3	87	1110
904	20	22.39	87	1104
905	10	5.33	87	1087
925	1	136.22	88	824
926	1	154.8	88	966
927	1	24.19	88	1070
928	1	106.73	88	874
937	10	99.75	89	1094
938	24	3.29	89	788
939	5	4.06	89	1065
940	2	62.23	89	1111
941	10	59.98	89	932
942	10	4.5	89	977
943	2	96.12	89	1019
944	2	11.22	89	974
945	5	16.55	89	1001
946	2	37.8	89	1073
947	2	20.25	90	1002
948	2	70.5	90	991
949	10	17.5	90	941
950	9	4.34	90	926
951	1	61.25	90	932
952	6	7.76	90	1097
953	10	0.97	90	839
954	2	150.14	90	918
955	2	165.94	90	920
956	1	95.05	90	946
957	1	95.05	90	949
958	1	25.5	90	1074
959	2	11.66	90	1046
960	3	15.86	90	1045
961	10	3.36	90	845
962	8	3.12	90	943
963	10	5.87	90	883
964	5	1.75	90	896
965	1	6.32	90	817
966	2	12.77	90	1113
967	1	22.25	90	1114
\.


--
-- Data for Name: orcamentos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orcamentos (id, status, data_criacao, data_validade, usuario_id, condicao_pagamento, preco_minimo, preco_maximo, numero_nf, cliente_id, token_compartilhamento) FROM stdin;
1	RASCUNHO	2025-08-04 03:06:19.769558+00	\N	1	\N	\N	\N	\N	\N	\N
2	RASCUNHO	2025-08-08 12:20:25.70777+00	\N	3	\N	\N	\N	\N	\N	\N
29	FINALIZADO	2025-11-25 12:14:35.002568+00	\N	11	À vista	\N	\N	\N	23	\N
30	FINALIZADO	2025-11-25 12:40:58.790031+00	\N	11	30 dias	\N	\N	\N	27	\N
31	FINALIZADO	2025-11-25 12:41:18.352639+00	\N	9	30 dias	\N	\N	\N	30	\N
73	FINALIZADO	2025-12-29 18:04:57.805874+00	\N	9	30 dias	\N	\N	\N	40	893z16w1wmfzlzchezHDoOICyngjTzbGq-gsGfIfrX4
25	ENVIADO	2025-11-12 13:08:41.765083+00	\N	7	À vista	\N	\N	\N	30	\N
72	FINALIZADO	2025-12-29 14:59:22.336292+00	\N	11	30 dias	\N	\N	\N	53	ibkfx4Qjrgg5aOShSGZy8bi7ARG8x_dDEwc_pp3ID8E
71	FINALIZADO	2025-12-23 19:24:56.586494+00	\N	9	30 dias	\N	\N	\N	44	DwZLRaE1zdRtRXdHrba_9DV-o4UJ46CLWTuWvLyV58Q
70	FINALIZADO	2025-12-23 11:36:32.814172+00	\N	9	30 dias	\N	\N	\N	44	M_RnrUDobVFXfIlSqDZkPjXqqxew04PTxLLQ7a1A00Q
69	FINALIZADO	2025-12-22 12:12:23.476346+00	\N	11	30 dias	\N	\N	\N	50	iaqG-_OkmABDR0hZ6BTPcHmaqCfg8dvvf5CpRkancSU
68	FINALIZADO	2025-12-22 12:08:21.573751+00	\N	11	30 dias	\N	\N	\N	49	8uciwqb-OJ91WJ-evZgEedU7HmAlGEQj1HYzPD9TZDo
67	FINALIZADO	2025-12-19 12:44:37.529456+00	\N	11	30 dias	\N	\N	\N	57	llZaTiaDGg-Kyxy3PzUD2jxZBPi1ofhyGCRmZs8NTfw
66	FINALIZADO	2025-12-19 11:49:30.532089+00	\N	11	30 dias	\N	\N	\N	57	1Yn54QyzpXS2vtt5eR8gITzP85ZSmU4Y4JcaC35lHxA
65	FINALIZADO	2025-12-18 20:37:15.108323+00	\N	11	30 dias	\N	\N	\N	21	qTjpcZbS2WoCWjLix1zoWVaS-c8UZYCwEFIsUZYgz7M
64	FINALIZADO	2025-12-18 17:41:26.341998+00	\N	9	30 dias	\N	\N	\N	56	pUu_5U17gdBl4TqT6hMSKJiYDOA0jgQP4uJfr8F9XQs
63	FINALIZADO	2025-12-18 13:04:01.258981+00	\N	11	30 dias	\N	\N	\N	55	-O_tOLxQaDFaoCeFYp0gvR3gSWPcJ0ZSowG71op2zCQ
62	FINALIZADO	2025-12-18 12:40:37.61167+00	\N	11	30 dias	\N	\N	\N	21	3zVW7nXAjXrR5OOeqS9gq6QSVTRSq_CCM10ZKEhagTM
61	FINALIZADO	2025-12-18 12:22:20.656331+00	\N	11	30 dias	\N	\N	\N	21	AA_Hww__eAWZmohW9JiwVj7Ca-HWmZykdpEs9FWlTIM
60	FINALIZADO	2025-12-16 17:55:43.101635+00	\N	11	30 dias	\N	\N	\N	21	gKUpLQgapqeZQ-d2JyDID4yu8I3x-nHFmrUmClzDcU4
59	FINALIZADO	2025-12-15 11:44:13.958357+00	\N	9	À vista	\N	\N	\N	43	ONbZ1IYc-dghxJJ5JTZBHQo_wALbBM57ZLBa4MHus58
58	FINALIZADO	2025-12-15 11:42:07.060514+00	\N	11	30 dias	\N	\N	\N	42	VtUUXwDWdf_ylvtCwwZlHX0P9IYClUWkeFcL056vrz0
32	FINALIZADO	2025-11-26 00:18:46.660313+00	\N	9	30 dias	\N	\N	\N	23	\N
33	FINALIZADO	2025-11-27 13:53:00.559344+00	\N	9	30	\N	\N	\N	38	\N
34	FINALIZADO	2025-11-27 17:54:01.612785+00	\N	9	5 dias	\N	\N	\N	39	\N
35	FINALIZADO	2025-11-27 18:33:43.407972+00	\N	9	30	\N	\N	\N	40	\N
36	FINALIZADO	2025-11-27 18:55:53.665175+00	\N	9	5 dias	\N	\N	\N	40	\N
37	FINALIZADO	2025-12-01 19:19:31.312539+00	\N	11	5 dias	\N	\N	\N	42	GnSQs8RGe5mQqrAmWbQ-tT5HufJQa3NFdv7ukeOmdCM
38	FINALIZADO	2025-12-02 02:54:04.748134+00	\N	11	5 dias	\N	\N	\N	40	3v0UAr3CSpzZFfS31S2DY_ulv9D7Kq7ztcpztaOHNw8
39	FINALIZADO	2025-12-02 17:43:48.487632+00	\N	11	5 dias	\N	\N	\N	47	xuyFeE4XY7AyN2GqgGXD9qmmfTgw6EvGlE1a04FeK7g
40	FINALIZADO	2025-12-02 18:20:13.840669+00	\N	11	5 dias	\N	\N	\N	21	kzFGqSAf4WLo5EMHEN_R3hKK1Y23CAVaf9exIXMByM0
41	FINALIZADO	2025-12-03 13:26:46.935498+00	\N	11	30 dias	\N	\N	\N	49	3dvliCgXoLuOtDE2txnDRHia_PAq8yIaAqYwIiItiIk
42	FINALIZADO	2025-12-03 13:36:18.342198+00	\N	11	30 dias	\N	\N	\N	49	Uak7vYavTkL4SY4tpA80PoQcvEMPzS2SCegpNGgribI
47	FINALIZADO	2025-12-03 17:33:05.076741+00	\N	11	30 dias	\N	\N	\N	49	Bl_KOPTrH6zNZdZK-gGh2sBO1qUlElAF7fm3-4k469A
48	FINALIZADO	2025-12-03 17:41:43.928426+00	\N	11	30 dias	\N	\N	\N	49	W1Err_YhYyBBJd6sSr6eHpD56OUt0GZPNU4kUJbT5-g
49	FINALIZADO	2025-12-03 18:15:26.702056+00	\N	11	30 dias	\N	\N	\N	50	t3IBUjlcHylcHhzYuwVMrxCsEJ7_2IPgoKrH02fdqFc
50	FINALIZADO	2025-12-03 18:20:58.652012+00	\N	11	30 dias	\N	\N	\N	50	v8YVhCIzm0ok2efxzIT8EfPxigeG_yz_lxDDT7ur_5M
51	FINALIZADO	2025-12-03 18:24:36.954897+00	\N	11	30 dias	\N	\N	\N	50	cpJ2csU1UEk339LQcPgUCNIYbfezHvhIivHrBydgXLE
52	FINALIZADO	2025-12-03 19:13:13.32693+00	\N	11	30 dias	\N	\N	\N	51	uH7Ew-gkiBOn7AZE0Z7yTiUd4EjCR-wcU9I4b39vS8g
53	FINALIZADO	2025-12-03 19:22:58.797409+00	\N	11	30 dias	\N	\N	\N	52	q49G9ejfrMmwM0rXYw2n4JuSNLvMxzcag3danWK-_6s
54	FINALIZADO	2025-12-04 19:50:56.242986+00	\N	11	30 dias	\N	\N	\N	53	mfjye9YKAPUmaLILiYstnH3VTp8_dFGZVgt0SuhJnDo
55	FINALIZADO	2025-12-09 13:48:13.200968+00	\N	11	30 dias	\N	\N	\N	21	48NBj_A05bcIY0TdkqKxpE-nI0lMQ1KdM_7yTupOl7U
57	FINALIZADO	2025-12-12 14:11:17.569806+00	\N	11	À vista	\N	\N	\N	49	YegkQ8yfyS_U3v0-ZtCwnkTreZq7Ckn0Zapd8E14lbc
56	FINALIZADO	2025-12-10 12:15:19.558744+00	\N	9	30 dias	\N	\N	\N	54	phZL1Ua7w6rKxtM7CfpLbldDwELeYd7YRBaQUqAckDc
74	ENVIADO	2026-01-06 13:52:17.590798+00	\N	9	30 dias	\N	\N	\N	58	qGPv1t9-geFjO0AitwWZkeG5nXqxYKMdhT7QhAsZwFs
75	ENVIADO	2026-01-06 13:55:34.991083+00	\N	11	30 dias	\N	\N	\N	21	3qiq7Qj5_X8NF_BxR72TN8_fM1PXw4F3_gss0HM5_EI
76	ENVIADO	2026-01-07 14:36:25.286537+00	\N	11	30 dias	\N	\N	\N	59	FWKnWB5LOQqYVIV7UH-LJRv4VRkzi6g_hJ81qQcnmb0
77	ENVIADO	2026-01-07 20:40:24.338756+00	\N	9	30 dias	\N	\N	\N	54	PkdRUlkPuqhrD0qbkK9sAh3Mgfck19n-Fa6EWAx2WwE
78	ENVIADO	2026-01-12 19:22:48.58811+00	\N	11	30 dias	\N	\N	\N	21	bS1XkmFriA4YnBVNDTVDHglrs67HamjTKWNJ5WAdTG0
79	ENVIADO	2026-01-12 22:06:45.155241+00	\N	11	30 dias	\N	\N	\N	50	R-z077GS0NNCrpfV1OEZdJ2YAw_OsAFrgKG4P0zJwHY
80	ENVIADO	2026-01-12 22:22:18.125622+00	\N	11	30 dias	\N	\N	\N	50	IIPrZLSp7ggixEqn4nTjDAW7wa0ll5dgeHCOpWU7teo
81	ENVIADO	2026-01-12 23:53:15.93255+00	\N	11	30 dias	\N	\N	\N	49	bWEFwHha4Zn30S_yWDUbAXfrbYqGQIjkqIW1qJtO1CM
82	ENVIADO	2026-01-13 00:04:16.123579+00	\N	11	30 dias	\N	\N	\N	49	H9GFdF8p9iwVEbEWOATGDQKP-CCs5ImSIt6CiCPuRZY
83	ENVIADO	2026-01-13 00:15:01.334769+00	\N	11	30 dias	\N	\N	\N	49	dGlUA6GCkBt1oILGezNK6ZumYMPfIW-dq8wxfAk0VGE
84	ENVIADO	2026-01-13 00:31:31.743675+00	\N	11	30 dias	\N	\N	\N	49	XFWAbM1EZ400ndDANIQj7FJcLU-04-d8q7cD6F0_crU
85	ENVIADO	2026-01-13 14:51:06.36046+00	\N	9	30 dias	\N	\N	\N	45	wcHfVswK7yLMkY7wq5qkdEEZokuz4eK5BMvvHaomCEE
86	ENVIADO	2026-01-13 17:36:30.103851+00	\N	11	30 dias	\N	\N	\N	50	RaL08gzOrFxWdhc0RZ4rLQmm9MjVfw5J1DS7oko9a8Y
87	APROVADO	2026-01-13 19:30:11.211633+00	\N	11	30 dias	\N	\N	\N	42	lFrvV4CMPlF-a6jRNxmNEF9hhN7LwHBSYMbfAQba1VM
88	ENVIADO	2026-01-16 16:36:44.325337+00	\N	9	30 dias	\N	\N	\N	63	em7RJuPnUv5dgMbWNM-jdc6VZe9xjpNvppE1CjOKNKg
89	ENVIADO	2026-01-17 13:02:49.164002+00	\N	9	30 dias	\N	\N	\N	64	YUTzpqw5SUcjI-UBixbEGdbkOU9YqgNDOSBgskD2kes
90	ENVIADO	2026-01-29 19:07:34.067685+00	\N	9	30 dias	\N	\N	\N	71	W_3ZuBZrc1z5rEXg0zUr-dlCxEwdAtLeuBV1Iz6aMZ8
\.


--
-- Data for Name: ordens_compra; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ordens_compra (id, fornecedor_id, usuario_id, status, data_criacao, data_recebimento) FROM stdin;
2	\N	1	RASCUNHO	2025-11-14 12:31:22.500997+00	\N
3	\N	1	RASCUNHO	2025-11-14 13:39:20.254977+00	\N
\.


--
-- Data for Name: ordens_compra_itens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ordens_compra_itens (id, ordem_id, produto_id, quantidade_solicitada, custo_unitario_registrado) FROM stdin;
2	2	1065	5	2.43
3	2	1017	10	5.4
4	2	801	10	4
5	3	1065	5	2.43
6	3	1017	10	0
7	3	801	10	0
8	3	901	10	0
9	3	1066	5	34.56
10	3	909	10	0
11	3	905	10	162.67
12	3	1068	15	0.01
13	3	895	10	0
14	3	790	10	0
\.


--
-- Data for Name: precos_cliente_produto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.precos_cliente_produto (id, cliente_id, produto_id, preco_padrao, preco_minimo, preco_maximo, preco_medio, total_vendas, data_ultima_venda, data_criacao, data_atualizacao) FROM stdin;
1	40	817	6.32	6.32	6.32	6.32	3	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
2	40	920	165.94	165.94	165.94	165.94000000000003	9	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
3	40	931	77.3	77.3	77.3	77.29999999999998	9	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
4	40	925	7.69	7.69	7.69	7.6899999999999995	9	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
5	40	951	139.4	139.04	139.4	139.29000000000002	9	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
6	40	839	0.97	0.97	0.97	0.9700000000000001	3	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
7	40	850	2.91	2.91	2.91	2.91	9	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
8	40	802	14.92	14.92	14.92	14.92	9	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
25	57	856	128.11	128.11	128.11	128.11	3	2025-12-19 12:44:37.529456+00	2026-01-06 13:44:47.056029+00	2026-01-07 04:45:38.709735+00
26	57	789	41.58	41.58	41.58	41.58	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
27	57	850	2.91	2.91	2.91	2.91	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
28	57	926	4.34	4.34	4.34	4.34	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
29	57	848	3.12	3.12	3.12	3.1199999999999997	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
30	57	868	3.15	3.15	3.15	3.15	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
31	57	839	0.97	0.97	0.97	0.9700000000000001	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
32	57	977	4.5	4.5	4.5	4.5	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
33	57	787	5.37	5.37	5.37	5.37	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
34	57	1002	20.25	20.25	20.25	20.25	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
35	57	990	38.7	38.7	38.7	38.7	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
36	57	1016	125.48	125.48	125.48	125.48	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
37	57	920	136.39	136.39	136.39	136.39	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
38	57	1035	73.66	73.66	73.66	73.66	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
39	57	1036	73.66	73.66	73.66	73.66	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
40	57	827	35	35	35	35	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
41	57	976	16.8	16.8	16.8	16.8	3	2025-12-19 11:49:30.532089+00	2026-01-06 13:44:50.925678+00	2026-01-07 04:45:38.709735+00
42	21	853	46.26	46.26	46.26	46.26	3	2025-12-18 20:37:15.108323+00	2026-01-06 13:45:04.000767+00	2026-01-07 04:45:38.709735+00
43	21	855	27.39	27.39	27.39	27.39	3	2025-12-18 20:37:15.108323+00	2026-01-06 13:45:04.000767+00	2026-01-07 04:45:38.709735+00
44	21	856	158.13	158.13	158.13	158.13	3	2025-12-18 20:37:15.108323+00	2026-01-06 13:45:04.000767+00	2026-01-07 04:45:38.709735+00
45	56	1103	263.2	263.2	263.2	263.2	3	2025-12-18 17:41:26.341998+00	2026-01-06 13:45:06.652411+00	2026-01-07 04:45:38.709735+00
46	55	985	52.95	52.95	52.95	52.95000000000001	3	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00	2026-01-07 04:45:38.709735+00
47	55	977	4.5	4.5	4.5	4.5	3	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00	2026-01-07 04:45:38.709735+00
48	55	839	0.97	0.97	0.97	0.9700000000000001	3	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00	2026-01-07 04:45:38.709735+00
49	55	966	154.8	154.8	154.8	154.8	3	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00	2026-01-07 04:45:38.709735+00
50	55	825	2.91	2.91	2.91	2.91	3	2025-12-18 13:04:01.258981+00	2026-01-06 13:45:10.337213+00	2026-01-07 04:45:38.709735+00
51	21	1001	14.55	14.55	14.55	14.550000000000002	3	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00	2026-01-07 04:45:38.709735+00
52	21	993	51.9	51.9	51.9	51.9	3	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00	2026-01-07 04:45:38.709735+00
53	21	894	27	27	27	27	3	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00	2026-01-07 04:45:38.709735+00
54	21	893	24.4	24.4	24.4	24.399999999999995	3	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00	2026-01-07 04:45:38.709735+00
55	21	1041	15.34	15.34	15.34	15.339999999999998	3	2025-12-18 12:40:37.61167+00	2026-01-06 13:45:13.335973+00	2026-01-07 04:45:38.709735+00
56	21	788	3.29	3.29	3.29	3.2899999999999996	12	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
57	21	787	5.37	5.37	5.37	5.369999999999999	9	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
59	21	1010	95.05	95.05	95.05	95.05	3	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
61	21	824	131.29	131.29	131.29	131.29	6	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
62	21	876	370.18	120.81	370.18	245.495	6	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
64	21	822	112.69	112.69	112.79	112.74000000000001	6	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
65	21	1035	89.6	89.6	89.6	89.60000000000001	6	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
67	21	884	5.87	5.87	5.87	5.87	3	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
68	21	847	1.5	1.5	1.5	1.5	3	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
69	21	848	3.12	3.12	3.12	3.1200000000000006	6	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
70	21	883	5.87	5.87	5.87	5.87	3	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
71	21	928	111.51	111.51	111.51	111.51	12	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
73	21	935	57.68	57.68	57.68	57.68	6	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
74	21	1036	89.6	89.6	89.6	89.59999999999998	3	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00	2026-01-07 04:45:38.709735+00
75	21	879	3.43	3.43	3.43	3.43	3	2025-12-16 17:55:43.101635+00	2026-01-06 13:45:23.449117+00	2026-01-07 04:45:38.709735+00
76	43	1021	138.5	138.5	138.5	138.5	3	2025-12-15 11:44:13.958357+00	2026-01-06 13:45:30.500276+00	2026-01-07 04:45:38.709735+00
77	42	1048	72.65	72.65	72.65	72.65	3	2025-12-15 11:42:07.060514+00	2026-01-06 13:45:33.586767+00	2026-01-07 04:45:38.709735+00
78	23	788	3.29	3.29	3.29	3.2900000000000005	3	2025-11-25 12:14:35.002568+00	2026-01-06 13:45:40.57561+00	2026-01-07 04:45:38.709735+00
79	23	789	47.09	47.09	47.09	47.09	3	2025-11-25 12:14:35.002568+00	2026-01-06 13:45:40.57561+00	2026-01-07 04:45:38.709735+00
80	23	791	11.7	11.7	11.7	11.699999999999998	3	2025-11-25 12:14:35.002568+00	2026-01-06 13:45:40.57561+00	2026-01-07 04:45:38.709735+00
81	23	792	148.53	148.53	148.53	148.53	3	2025-11-25 12:14:35.002568+00	2026-01-06 13:45:40.57561+00	2026-01-07 04:45:38.709735+00
82	27	980	101.4	101.4	101.4	101.40000000000002	3	2025-11-25 12:40:58.790031+00	2026-01-06 13:45:44.960422+00	2026-01-07 04:45:38.709735+00
83	27	862	213.53	213.53	213.53	213.53	3	2025-11-25 12:40:58.790031+00	2026-01-06 13:45:44.960422+00	2026-01-07 04:45:38.709735+00
84	30	861	0	0	0	0	3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00	2026-01-07 04:45:38.709735+00
85	30	792	148.53	148.53	148.53	148.53	3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00	2026-01-07 04:45:38.709735+00
86	30	1074	20	20	20	20	3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00	2026-01-07 04:45:38.709735+00
87	30	829	32.2	32.2	32.2	32.2	3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00	2026-01-07 04:45:38.709735+00
60	21	874	100.79	90.31	100.79	94.38555555555556	9	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
66	21	1024	176.82	176.82	176.82	176.81999999999996	6	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
72	21	804	2.93	2.93	2.93	2.93	6	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
88	30	835	41.3	41.3	41.3	41.3	3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00	2026-01-07 04:45:38.709735+00
89	30	889	30	30	30	30	3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00	2026-01-07 04:45:38.709735+00
90	30	875	0	0	0	0	3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00	2026-01-07 04:45:38.709735+00
91	30	952	385.5	385.5	385.5	385.5	3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00	2026-01-07 04:45:38.709735+00
92	30	1016	123.45	123.45	123.45	123.45	3	2025-11-25 12:41:18.352639+00	2026-01-06 13:45:58.076874+00	2026-01-07 04:45:38.709735+00
93	23	809	24.56	24.56	24.56	24.56	3	2025-11-26 00:18:46.660313+00	2026-01-06 13:46:03.044612+00	2026-01-07 04:45:38.709735+00
94	23	968	36.48	36.48	36.48	36.48	3	2025-11-26 00:18:46.660313+00	2026-01-06 13:46:03.044612+00	2026-01-07 04:45:38.709735+00
95	38	1015	132.5	132.5	132.5	132.5	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
96	38	845	3.36	3.36	3.36	3.36	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
97	38	788	3.29	3.29	3.29	3.2900000000000005	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
98	38	921	45.77	45.77	45.77	45.77	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
99	38	839	0.97	0.97	0.97	0.9700000000000001	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
100	38	931	77.3	77.3	77.3	77.3	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
101	38	990	38.7	38.7	38.7	38.7	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
102	38	946	132.54	132.54	132.54	132.54	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
103	38	925	7.69	7.69	7.69	7.69	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
104	38	1048	83.84	83.84	83.84	83.84	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
105	38	1002	20.25	20.25	20.25	20.25	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
106	38	1016	132.5	132.5	132.5	132.5	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
107	38	827	38.2	38.2	38.2	38.2	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
108	38	937	102.9	102.9	102.9	102.90000000000002	3	2025-11-27 13:53:00.559344+00	2026-01-06 13:46:08.708271+00	2026-01-07 04:45:38.709735+00
109	39	931	77.3	77.3	77.3	77.3	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
110	39	940	19.3	19.3	19.3	19.3	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
111	39	984	24.92	24.92	24.92	24.92	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
112	39	983	17.92	17.92	17.92	17.92	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
113	39	991	70.5	70.5	70.5	70.5	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
114	39	951	139.04	139.04	139.04	139.04	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
115	39	789	47.09	47.09	47.09	47.09	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
116	39	824	121.9	121.9	121.9	121.90000000000002	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
117	39	825	2.91	2.91	2.91	2.91	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
118	39	839	0.97	0.97	0.97	0.9700000000000001	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
119	39	817	6.32	6.32	6.32	6.32	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
120	39	819	3.99	3.99	3.99	3.99	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
121	39	1062	58.8	58.8	58.8	58.79999999999999	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
122	39	853	34.59	34.59	34.59	34.59	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
123	39	976	16.8	16.8	16.8	16.8	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
124	39	850	2.91	2.91	2.91	2.91	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
125	39	890	11.05	11.05	11.05	11.050000000000002	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
126	39	881	24.33	24.33	24.33	24.33	3	2025-11-27 17:54:01.612785+00	2026-01-06 13:46:13.576757+00	2026-01-07 04:45:38.709735+00
127	40	1062	58.8	58.8	58.8	58.800000000000004	6	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:19.049495+00	2026-01-07 04:45:38.709735+00
128	40	940	19.3	18.13	19.3	18.715	6	2025-11-27 18:55:53.665175+00	2026-01-06 13:46:19.049495+00	2026-01-07 04:45:38.709735+00
129	40	823	2.7	2.7	2.7	2.7000000000000006	3	2025-11-27 18:33:43.407972+00	2026-01-06 13:46:19.049495+00	2026-01-07 04:45:38.709735+00
130	42	812	226.8	226.8	226.8	226.80000000000004	3	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00	2026-01-07 04:45:38.709735+00
131	42	827	38.2	38.2	38.2	38.2	3	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00	2026-01-07 04:45:38.709735+00
132	42	828	36.12	36.12	36.12	36.12	3	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00	2026-01-07 04:45:38.709735+00
133	42	848	3.12	3.12	3.12	3.1199999999999997	3	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00	2026-01-07 04:45:38.709735+00
134	42	1038	27.93	27.93	27.93	27.929999999999996	3	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00	2026-01-07 04:45:38.709735+00
135	42	809	24.38	24.38	24.38	24.38	3	2025-12-01 19:19:31.312539+00	2026-01-06 13:46:28.738531+00	2026-01-07 04:45:38.709735+00
136	40	1078	4	4	4	4	3	2025-12-02 02:54:04.748134+00	2026-01-06 13:46:35.145866+00	2026-01-07 04:45:38.709735+00
137	47	918	165.94	165.94	165.94	165.94	3	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00	2026-01-07 04:45:38.709735+00
138	47	1001	14.55	14.55	14.55	14.550000000000002	3	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00	2026-01-07 04:45:38.709735+00
139	47	940	18.78	18.78	18.78	18.78	3	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00	2026-01-07 04:45:38.709735+00
140	47	1003	98.55	98.55	98.55	98.55	3	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00	2026-01-07 04:45:38.709735+00
141	47	1035	95.42	95.42	95.42	95.42	3	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00	2026-01-07 04:45:38.709735+00
142	47	1019	95.79	95.79	95.79	95.79	3	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00	2026-01-07 04:45:38.709735+00
143	47	1048	84.35	84.35	84.35	84.35	3	2025-12-02 17:43:48.487632+00	2026-01-06 13:46:39.06856+00	2026-01-07 04:45:38.709735+00
144	21	873	90.31	90.31	90.31	90.31	3	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00	2026-01-07 04:45:38.709735+00
145	21	1032	89.7	89.7	89.7	89.7	3	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00	2026-01-07 04:45:38.709735+00
146	21	882	6.13	6.13	6.13	6.13	3	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00	2026-01-07 04:45:38.709735+00
147	21	881	6.13	6.13	6.13	6.13	3	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00	2026-01-07 04:45:38.709735+00
148	21	933	59.7	59.7	59.7	59.70000000000001	3	2025-12-02 18:20:13.840669+00	2026-01-06 13:46:43.137207+00	2026-01-07 04:45:38.709735+00
149	49	926	4.34	4.34	4.34	4.34	3	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00	2026-01-07 04:45:38.709735+00
150	49	977	4.5	4.5	4.5	4.5	3	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00	2026-01-07 04:45:38.709735+00
151	49	990	38.7	38.7	38.7	38.7	3	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00	2026-01-07 04:45:38.709735+00
152	49	983	17.92	17.92	17.92	17.92	3	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00	2026-01-07 04:45:38.709735+00
153	49	839	0.97	0.97	0.97	0.9700000000000001	3	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00	2026-01-07 04:45:38.709735+00
154	49	1035	89.6	89.6	89.6	89.59999999999998	3	2025-12-03 13:26:46.935498+00	2026-01-06 13:46:47.420345+00	2026-01-07 04:45:38.709735+00
155	49	788	3.29	3.29	3.29	3.2900000000000005	3	2025-12-03 13:36:18.342198+00	2026-01-06 13:46:51.703577+00	2026-01-07 04:45:38.709735+00
156	49	792	143.87	143.87	143.87	143.87	3	2025-12-03 13:36:18.342198+00	2026-01-06 13:46:51.703577+00	2026-01-07 04:45:38.709735+00
9	40	984	24.92	24.92	24.92	24.92	3	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
10	40	960	20.3	20	20.3	20.208333333333332	9	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
11	40	1045	15.51	15.51	15.51	15.51	3	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
12	40	836	10.5	10.5	10.5	10.5	3	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
13	40	825	2.91	2.91	2.91	2.91	6	2025-12-29 18:04:57.805874+00	2026-01-06 13:44:17.975899+00	2026-01-07 04:45:38.709735+00
14	53	1106	523.5	523.5	523.5	523.5	3	2025-12-29 14:59:22.336292+00	2026-01-06 13:44:30.682181+00	2026-01-07 04:45:38.709735+00
15	53	1107	523.5	523.5	523.5	523.5	3	2025-12-29 14:59:22.336292+00	2026-01-06 13:44:30.682181+00	2026-01-07 04:45:38.709735+00
16	44	1022	332.9	332.9	332.9	332.9	3	2025-12-23 19:24:56.586494+00	2026-01-06 13:44:36.224049+00	2026-01-07 04:45:38.709735+00
17	44	824	136.22	136.22	136.22	136.22	3	2025-12-23 11:36:32.814172+00	2026-01-06 13:44:39.303214+00	2026-01-07 04:45:38.709735+00
18	44	874	100.79	100.79	100.79	100.79	3	2025-12-23 11:36:32.814172+00	2026-01-06 13:44:39.303214+00	2026-01-07 04:45:38.709735+00
19	44	966	154.8	154.8	154.8	154.8	3	2025-12-23 11:36:32.814172+00	2026-01-06 13:44:39.303214+00	2026-01-07 04:45:38.709735+00
20	50	1087	5.33	5.33	5.33	5.329999999999999	6	2025-12-22 12:12:23.476346+00	2026-01-06 13:44:42.166297+00	2026-01-07 04:45:38.709735+00
21	50	1104	22.39	22.39	22.39	22.39	3	2025-12-22 12:12:23.476346+00	2026-01-06 13:44:42.166297+00	2026-01-07 04:45:38.709735+00
22	49	1087	5.33	5.33	5.33	5.329999999999999	6	2025-12-22 12:08:21.573751+00	2026-01-06 13:44:44.581962+00	2026-01-07 04:45:38.709735+00
23	49	1104	22.39	22.39	22.39	22.39	3	2025-12-22 12:08:21.573751+00	2026-01-06 13:44:44.581962+00	2026-01-07 04:45:38.709735+00
24	57	1025	27.1	27.1	27.1	27.100000000000005	3	2025-12-19 12:44:37.529456+00	2026-01-06 13:44:47.056029+00	2026-01-07 04:45:38.709735+00
58	21	791	11.7	11.7	11.7	11.700000000000001	9	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
63	21	966	162.22	156.07	162.22	158.11999999999998	12	2025-12-18 12:22:20.656331+00	2026-01-06 13:45:17.594791+00	2026-01-07 04:45:38.709735+00
157	49	1086	9.99	9.99	9.99	9.99	3	2025-12-03 13:36:18.342198+00	2026-01-06 13:46:51.703577+00	2026-01-07 04:45:38.709735+00
158	49	1079	5.32	5.32	5.32	5.32	3	2025-12-03 17:33:05.076741+00	2026-01-06 13:47:00.095094+00	2026-01-07 04:45:38.709735+00
159	49	817	6.32	6.32	6.32	6.32	3	2025-12-03 17:33:05.076741+00	2026-01-06 13:47:00.095094+00	2026-01-07 04:45:38.709735+00
160	49	931	77.3	77.3	77.3	77.3	3	2025-12-03 17:41:43.928426+00	2026-01-06 13:47:03.951757+00	2026-01-07 04:45:38.709735+00
161	49	937	103.21	103.21	103.21	103.21	3	2025-12-03 17:41:43.928426+00	2026-01-06 13:47:03.951757+00	2026-01-07 04:45:38.709735+00
162	50	993	51.9	51.9	51.9	51.9	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
163	50	1002	20.25	20.25	20.25	20.25	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
164	50	990	38.7	38.7	38.7	38.7	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
165	50	1001	14.55	14.55	14.55	14.550000000000002	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
166	50	1036	89.6	89.6	89.6	89.59999999999998	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
167	50	804	2.93	2.93	2.93	2.93	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
168	50	977	4.5	4.5	4.5	4.5	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
169	50	791	11.7	11.7	11.7	11.699999999999998	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
170	50	943	3.12	3.12	3.12	3.1199999999999997	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
171	50	839	0.97	0.97	0.97	0.9700000000000001	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
172	50	890	11.05	11.05	11.05	11.050000000000002	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
173	50	884	5.87	5.87	5.87	5.87	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
174	50	1088	4.5	4.5	4.5	4.5	3	2025-12-03 18:15:26.702056+00	2026-01-06 13:47:08.779602+00	2026-01-07 04:45:38.709735+00
175	50	1079	5.32	5.32	5.32	5.32	3	2025-12-03 18:20:58.652012+00	2026-01-06 13:47:13.510449+00	2026-01-07 04:45:38.709735+00
176	50	937	103.21	103.21	103.21	103.21	3	2025-12-03 18:24:36.954897+00	2026-01-06 13:47:16.9651+00	2026-01-07 04:45:38.709735+00
177	50	931	77.3	77.3	77.3	77.3	3	2025-12-03 18:24:36.954897+00	2026-01-06 13:47:16.9651+00	2026-01-07 04:45:38.709735+00
178	51	873	68.91	68.91	68.91	68.91	3	2025-12-03 19:13:13.32693+00	2026-01-06 13:47:22.224555+00	2026-01-07 04:45:38.709735+00
179	51	820	181.81	181.81	181.81	181.81000000000003	3	2025-12-03 19:13:13.32693+00	2026-01-06 13:47:22.224555+00	2026-01-07 04:45:38.709735+00
180	51	966	149.31	149.31	149.31	149.31	3	2025-12-03 19:13:13.32693+00	2026-01-06 13:47:22.224555+00	2026-01-07 04:45:38.709735+00
181	51	1024	189.42	189.42	189.42	189.42	3	2025-12-03 19:13:13.32693+00	2026-01-06 13:47:22.224555+00	2026-01-07 04:45:38.709735+00
182	52	874	110.5	110.5	110.5	110.5	3	2025-12-03 19:22:58.797409+00	2026-01-06 13:47:26.741379+00	2026-01-07 04:45:38.709735+00
183	52	822	101.17	101.17	101.17	101.17	3	2025-12-03 19:22:58.797409+00	2026-01-06 13:47:26.741379+00	2026-01-07 04:45:38.709735+00
184	52	1030	31.22	31.22	31.22	31.22	3	2025-12-03 19:22:58.797409+00	2026-01-06 13:47:26.741379+00	2026-01-07 04:45:38.709735+00
185	53	1089	559.17	559.17	559.17	559.17	3	2025-12-04 19:50:56.242986+00	2026-01-06 13:47:31.401399+00	2026-01-07 04:45:38.709735+00
186	53	1090	559.17	559.17	559.17	559.17	3	2025-12-04 19:50:56.242986+00	2026-01-06 13:47:31.401399+00	2026-01-07 04:45:38.709735+00
187	53	1091	559.17	559.17	559.17	559.17	3	2025-12-04 19:50:56.242986+00	2026-01-06 13:47:31.401399+00	2026-01-07 04:45:38.709735+00
188	53	1092	559.17	559.17	559.17	559.17	3	2025-12-04 19:50:56.242986+00	2026-01-06 13:47:31.401399+00	2026-01-07 04:45:38.709735+00
189	21	1062	58.8	58.8	58.8	58.79999999999999	3	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00	2026-01-07 04:45:38.709735+00
190	21	1015	123.15	123.15	123.15	123.15000000000002	3	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00	2026-01-07 04:45:38.709735+00
191	21	821	1	1	1	1	3	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00	2026-01-07 04:45:38.709735+00
192	21	1028	89.6	89.6	89.6	89.59999999999998	3	2025-12-09 13:48:13.200968+00	2026-01-06 13:47:36.227664+00	2026-01-07 04:45:38.709735+00
193	49	1095	43.5	43.5	43.5	43.5	3	2025-12-12 14:11:17.569806+00	2026-01-06 13:47:40.59687+00	2026-01-07 04:45:38.709735+00
194	54	1071	46.67	46.67	46.67	46.669999999999995	3	2025-12-10 12:15:19.558744+00	2026-01-06 13:47:43.381975+00	2026-01-07 04:45:38.709735+00
195	54	904	293.63	293.63	293.63	293.63	3	2025-12-10 12:15:19.558744+00	2026-01-06 13:47:43.381975+00	2026-01-07 04:45:38.709735+00
\.


--
-- Data for Name: produtos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.produtos (id, nome, codigo, categoria, descricao, preco_custo, preco_venda, unidade_medida, estoque_minimo, data_validade, quantidade_em_estoque, empresa_id, fornecedor_id, data_criacao) FROM stdin;
837	ESCOVÃO DE MADEIRA	975	UTENSÍLIOS	\N	2.5	3.5	UN	10	\N	19	1	\N	2025-12-05 14:44:35.094272+00
1103	LIXEIRA BASCULANTE 100L VERDE	411255	LIXEIRA		188	263.2	UN	0	\N	0	1	\N	2025-12-18 17:38:15.853565+00
1096	PULVERIZADOR 1L NOBRE	PUL1LN	DISPENSER	\N	3.59	12.2	UN	0	\N	42	1	\N	2025-12-15 14:47:21.780831+00
859	HIGISEC	796	QUIMICO	\N	46.96	120.22	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
846	FIBRA GERAL	PROD060	FIBRAS	\N	1.28	2.56	PCT	10	\N	549	1	\N	2025-12-05 14:44:35.094272+00
791	ÁLCOOL LIQUIDO 1L 70 SAFRA	491	QUIMICO	\N	7.8	12.89	UN	10	\N	79	1	\N	2025-12-05 14:44:35.094272+00
858	HC LAVANDA AZUL	PROD072	QUIMICO	\N	20.5	30.75	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
834	DISPENSER PAPEL HIGIENICO BOBINA	PROD048	DISPENSERS	\N	216.9	347.04	UN	10	\N	12	1	\N	2025-12-05 14:44:35.094272+00
802	AROMATIZANTE LAVANDA	330	QUIMICO	\N	10.66	14.92	UN	10	\N	37	1	\N	2025-12-05 14:44:35.094272+00
818	COPO DESCARTAVEL 180ML - ULTRA	586	DESCARTÁVEIS	\N	5.01	7.01	PCT	100	\N	100	1	\N	2025-12-05 14:44:35.094272+00
796	AMACITEC PRIMAVERA 5L	1031605	QUIMICO	\N	30.78	78.8	UN	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
1100	MULTILUX BAC CAPIM LIMÃO DOS 1L	4AS4AS	QUIMICO	\N	37.26	95.39	UN	0	\N	3	1	\N	2025-12-16 14:27:06.621552+00
815	CLORO ATIVO BB 20L	PROD029	QUIMICO	\N	106.2	271.87	UN	10	\N	10	1	\N	2025-12-05 14:44:35.094272+00
793	ALVITEC PE 5KG	1031305	QUIMICO	\N	109.3	279.81	UN	10	\N	7	1	\N	2025-12-05 14:44:35.094272+00
788	ÁGUA SANITÁRIA CLORITO 1L	231	QUIMICO	\N	2.35	3.29	UN	10	\N	43	1	\N	2025-12-05 14:44:35.094272+00
807	BAYGON 12X360ML	610	QUIMICO	\N	10.91	15.27	UN	10	\N	42	1	\N	2025-12-05 14:44:35.094272+00
860	HOSP NEUTRO PLUS BB 5L	PROD074	QUIMICO	\N	54.84	140.39	UN	10	\N	12	1	\N	2025-12-05 14:44:35.094272+00
812	CABO EXTENSÃO TELESCÓPIA 6M	PROD026	ACESSÓRIOS	\N	189	226.8	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
1069	HIGH CRIL BB 5L	HIGHC	QUIMICO	\N	156.82	156.82	UN	5	2026-10-27	12	1	\N	2025-12-05 14:44:35.094272+00
819	COPO DESCARTAVEL 50ML - ULTRA	PROD033	DESCARTÁVEIS	\N	2.6	3.64	UN	10	\N	118	1	\N	2025-12-05 14:44:35.094272+00
856	GEL ANTISSEPTICO BB5L	1018105	QUIMICO	\N	61.77	158.13	UN	10	\N	10	1	\N	2025-12-05 14:44:35.094272+00
806	BALDE COMUM	868	ACESSÓRIOS	\N	10.01	19.6	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
840	EXSSOL 500 BB 20L	PROD054	QUIMICO	\N	57.62	144.05	PCT	10	\N	18	1	\N	2025-12-05 14:44:35.094272+00
836	ESCOVA SANITÁRIA COM SUPORTE	976	UTENSÍLIOS	\N	7.5	10.5	UN	10	\N	36	1	\N	2025-12-05 14:44:35.094272+00
844	FIBRA DE LIMPEZA SLIM BRANCA	63	FIBRAS	\N	1.7	2.38	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
789	AGUASSANI BB 5L	3	QUIMICO	\N	18.3	46.85	UN	10	\N	27	1	\N	2025-12-05 14:44:35.094272+00
1112	DESENTUPIDOR DE VASO 	111	ARTIGOS		\N	16.5	UN	0	\N	12	1	\N	2026-01-26 13:18:18.605084+00
804	ASSOLAN PALHA DE AÇO	PROD018	UTENSÍLIOS	\N	2.09	2.93	PCT	10	\N	93	1	\N	2025-12-05 14:44:35.094272+00
792	ALUMICROST	211	QUIMICO	\N	56.2	143.87	UN	10	\N	83	1	\N	2025-12-05 14:44:35.094272+00
1041	TOUCA DESCARTÁVEL Cód. 34794	288	UTENSÍLIOS	\N	7.67	15.34	UN	10	\N	96	1	\N	2025-12-05 14:44:35.094272+00
843	FIBRA BETAÇO	PROD057	FIBRAS	\N	1.43	2.86	UN	10	\N	490	1	\N	2025-12-05 14:44:35.094272+00
821	DESINCROST GEL 1L	PROD035	QUIMICO	\N	11	28.31	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
813	CERACRIL 5L	PROD027	QUIMICO	\N	115.01	294.43	UN	10	\N	12	1	\N	2025-12-05 14:44:35.094272+00
797	SUPORTE MOP PÓ 40 CM	PROD011	ACESSÓRIOS	\N	17.25	34.5	UN	10	\N	25	1	\N	2025-12-05 14:44:35.094272+00
798	SUPORTE MOP PÓ 60 CM	PROD012	ACESSÓRIOS	\N	19.9	39.8	UN	10	\N	44	1	\N	2025-12-05 14:44:35.094272+00
857	HC CANOA	PROD071	QUIMICO	\N	40	60	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
814	CLOR MAQ BB5L	PROD028	QUIMICO	\N	62.12	159.03	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
828	DISCO PRETO 410	PROD042	ACESSÓRIOS	\N	18.06	36.12	UN	10	\N	27	1	\N	2025-12-05 14:44:35.094272+00
799	SUPORTE MOP PÓ 80 CM	PROD013	ACESSÓRIOS	\N	40.18	56.25	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
831	DISPENSER P/ ABSORVENTE	PROD045	DISPENSERS	\N	0	11.01	UN	10	\N	13	1	\N	2025-12-05 14:44:35.094272+00
855	GEL ANTISSEPTICO 500ML FRASCO	PROD069	QUIMICO	\N	10.7	27.39	UN	10	\N	11	1	\N	2025-12-05 14:44:35.094272+00
1063	REMOCALC BB 5L	AAAAAAAAA	QUIMICO	\N	114.09	292.07	UN	2	2026-08-26	3	1	\N	2025-12-05 14:44:35.094272+00
842	FD TOALHA INTERFOLHADO MILI	PROD056	PAPÉIS	\N	13.37	18.78	UN	10	\N	20	1	\N	2025-12-05 14:44:35.094272+00
811	CABO EXTENSÃO TELESCÓPIA 3M	PROD025	ACESSÓRIOS	\N	39.6	79.2	UN	10	\N	20	1	\N	2025-12-05 14:44:35.094272+00
830	DISPENSER COPO DESC.	PROD044	DISPENSERS	\N	0	88.2	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
1072	LUVA LATEX RANHURADA TAM. M	711	EPIS	\N	13.5	18.9	UN	15	\N	0	1	\N	2025-12-05 14:44:35.094272+00
849	FITA ZEBRADA	PROD063	ACESSÓRIOS	\N	10.5	15.75	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
833	DISPENSER P/ SABONETE SABONETEIRA	PROD047	DISPENSERS	\N	0	52.58	UN	10	\N	13	1	\N	2025-12-05 14:44:35.094272+00
826	DISCO BRANCO 410	PROD040	ACESSÓRIOS	\N	15.35	30.7	UN	10	\N	4	1	\N	2025-12-05 14:44:35.094272+00
816	COLETOR P/ ABSORVENTE	PROD030	DESCARTÁVEIS	\N	7.5	10.5	PCT	10	\N	96	1	\N	2025-12-05 14:44:35.094272+00
852	FORRO P/ ASSENTO DESC.	PROD066	HIGIENE	\N	8.72	17.44	UN	10	\N	157	1	\N	2025-12-05 14:44:35.094272+00
829	DISCO VERMELHO	PROD043	ACESSÓRIOS	\N	17.89	35.78	UN	10	\N	17	1	\N	2025-12-05 14:44:35.094272+00
790	ALCOOL BIOELITICO 96% 1L	PROD004	QUIMICO	\N	15.2	22.8	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
841	FD PAPEL HIGIÊNICO MILI	PROD055	PAPÉIS	\N	57.78	80.89	PCT	10	\N	11	1	\N	2025-12-05 14:44:35.094272+00
838	ESPANADOR ELETROESTÁTICO	PROD052	UTENSÍLIOS	\N	22.33	31.26	UN	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
832	DISPENSER P/ ASSENTO SANITÁRIO	PROD046	DISPENSERS	\N	24.5	34.3	UN	10	\N	17	1	\N	2025-12-05 14:44:35.094272+00
794	ALVITEC PE BB 50L	820	QUIMICO	\N	0	2253.98	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
795	AMACITEC BB 50L	PROD009	QUIMICO	\N	0	718.3	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
1077	APLICADOR DE CERA SEM CABO	APLIC35	ACESSORIO	\N	9.19	18.38	UN	0	\N	12	1	\N	2025-12-05 14:44:35.094272+00
800	AROMATIZANTE FLOR DE ALGODÃO	PROD014	QUIMICO	\N	10.66	14.92	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
805	BALDE COM SECADOR BETANNIN	PROD019	ACESSÓRIOS	\N	24.43	41.53	UN	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
810	CABO EM CHAPA DE AÇO 1,5 CM	PROD024	ACESSÓRIOS	\N	16.06	22.48	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
851	FLANELA LARANJA	PROD065	PANOS	\N	1.75	2.45	PCT	10	\N	-6	1	\N	2025-12-05 14:44:35.094272+00
1104	CAFE MELITA EXTRA FORTE 250G	PERS-1766405301583-89dcc2b2	Personalizado	Produto personalizado criado automaticamente	\N	22.39	UN	0	\N	0	1	\N	2025-12-22 12:08:21.573751+00
823	DETERGENTE NEUTRO FC 12X500ML	249	QUIMICO	\N	1.7	2.38	UN	10	\N	76	1	\N	2025-12-05 14:44:35.094272+00
839	ESPONJA DUPLA FACE	102	UTENSÍLIOS	\N	0.69	0.97	UN	10	\N	178	1	\N	2025-12-05 14:44:35.094272+00
923	PA COLETORA C/CABO CONDOR	PROD137	ACESSÓRIOS	\N	33.9	47.46	UN	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
866	LAVPRO DX BB 20L	1032222	QUIMICO	\N	230.82	590.9	ROLO	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
1101	interfolhas	PERS-1765909474173-45df7857	Personalizado	Produto personalizado criado automaticamente	0	11	UN	0	\N	0	1	\N	2025-12-16 18:24:34.167988+00
932	PAPEL HIGIENICO ECONIMICO BIG ROLL	PROD146	PAPÉIS	\N	40	56	ROLO	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
921	PÁ COLETORA C/ CABO BETANNIN	197	ACESSÓRIOS	\N	0	45.77	UN	10	\N	7	1	\N	2025-12-05 14:44:35.094272+00
1074	DETERGENTE OI 5L	DETG5	QUIMICO	\N	17	25.5	UN	0	\N	0	1	\N	2025-12-05 14:44:35.094272+00
873	LIMPAX BB 5L	1003905	QUIMICO	\N	31.46	80.54	UN	10	\N	44	1	\N	2025-12-05 14:44:35.094272+00
911	MULTILUX POWER BB5L	PROD125	QUIMICO	\N	134.64	344.68	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
868	LIMPA ALUMINIO ECONOMICO 12X500ML	250	QUIMICO	\N	2.25	3.15	UN	10	\N	22	1	\N	2025-12-05 14:44:35.094272+00
1067	LAVESSOL MAQ  BB 5L	115500	QUIMICO	\N	59.6	152.58	UN	2	2026-09-02	5	1	\N	2025-12-05 14:44:35.094272+00
907	MULTILUX BAC S/ FRAG BB5L	PROD121	QUIMICO	\N	125.18	330.15	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
862	LAVESSOL ORANGE BB 5L	PROD076	QUIMICO	\N	83.41	213.53	UN	10	\N	25	1	\N	2025-12-05 14:44:35.094272+00
882	LUVA LATEX AMARELA SILVER M	291	EPIS	\N	3.18	6.36	PCT	10	\N	77	1	\N	2025-12-05 14:44:35.094272+00
906	MULTILUX BAC BREEZE DOS1L	PROD120	QUIMICO	\N	40.91	104.73	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
929	PAPEL HIG. CAI CAI C/9.000 FLS	903	PAPÉIS	\N	96.31	192.62	ROLO	10	\N	4	1	\N	2025-12-05 14:44:35.094272+00
824	DETERGENTE CLORADO BB 5L	43	QUIMICO	\N	53.21	136.22	CX	10	\N	73	1	\N	2025-12-05 14:44:35.094272+00
853	GEL ANTISSEPTICO 1L PET	1018110	QUIMICO	\N	18.07	46.26	UN	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
910	MULTILUX ECO FRESH 1L	PROD124	QUIMICO	\N	20.07	51.38	UN	10	\N	18	1	\N	2025-12-05 14:44:35.094272+00
878	LUVA LATEX (P) (COD: 32429)	PROD092	EPIS	\N	3.45	7.9	PCT	10	\N	92	1	\N	2025-12-05 14:44:35.094272+00
825	DETERGENTE ECONOMICO NEUTRO 12X500ML	587	QUIMICO	\N	2.08	2.91	UN	10	\N	59	1	\N	2025-12-05 14:44:35.094272+00
845	FIBRA DE LIMPEZA ULTRA PESADA	677	FIBRAS	\N	1.68	3.36	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
863	LAVPRO BB 5L	1031505	QUIMICO	\N	71.99	184.29	UN	10	\N	10	1	\N	2025-12-05 14:44:35.094272+00
1109	Evita mofo	PERS-1768332611214-4db4eb8d	Personalizado	Produto personalizado criado automaticamente	\N	13.75	UN	0	\N	0	1	\N	2026-01-13 19:30:11.211633+00
886	LUVA NITRILICA SEM PÓ G: PRETA	835	EPIS	\N	19.6	33.32	PCT	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
1110	Aromatizante automático 	PERS-1768332611264-000cbd83	Personalizado	Produto personalizado criado automaticamente	\N	57.3	UN	0	\N	0	1	\N	2026-01-13 19:30:11.211633+00
880	LUVA LATEX (M) (COD:32430)	PROD094	EPIS	\N	3.95	7.9	PCT	10	\N	19	1	\N	2025-12-05 14:44:35.094272+00
896	MASCARA PFF1	978	ACESSÓRIOS	\N	1.25	1.75	UN	10	\N	86	1	\N	2025-12-05 14:44:35.094272+00
1073	SABONETE PREMISSE 5L	PREMIS	QUIMICO	\N	24	37.8	UN	1	2026-11-13	0	1	\N	2025-12-05 14:44:35.094272+00
875	LIXEIRA INOX 5L BRINOX	PROD089	LIXEIRAS	\N	128.4	179.76	UN	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
890	LUVA NITRILICA VERDE G	PROD104	EPIS	\N	7.89	11.05	PCT	10	\N	14	1	\N	2025-12-05 14:44:35.094272+00
879	LUVA LATEX (G) (COD: 32431)	PROD093	EPIS	\N	2.45	3.43	PCT	10	\N	47	1	\N	2025-12-05 14:44:35.094272+00
912	MULTILUX POWER DOS 1L	PROD126	QUIMICO	\N	34.09	87.27	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
861	LAVESSOL ORANGE BB 20L	PROD075	QUIMICO	\N	0	0	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
901	MOP ÚMIDO 340G - VERMELHO	PROD115	LIMPEZA GERAL	\N	14.36	28.72	UN	10	\N	24	1	\N	2025-12-05 14:44:35.094272+00
897	MEXEDOR P/ CAFÉ	PROD111	ACESSÓRIOS	\N	3.73	5.22	UN	10	\N	40	1	\N	2025-12-05 14:44:35.094272+00
872	LIMPAX 1L	PROD086	QUIMICO	\N	7.22	18.48	UN	10	\N	8	1	\N	2025-12-05 14:44:35.094272+00
869	LIMPA ALUMINIO NUTRILAR	PROD083	QUIMICO	\N	2.25	3.15	UN	10	\N	35	1	\N	2025-12-05 14:44:35.094272+00
1097	PULVERIZADOR 500ML NOBRE	PULV500	DISPENSER	\N	2.49	7.76	UN	0	\N	48	1	\N	2025-12-15 14:48:24.120148+00
864	LAVPRO AD 50L	PROD078	QUIMICO	\N	552.88	1415.37	UN	10	\N	10	1	\N	2025-12-05 14:44:35.094272+00
904	MULTIBAC BP DOS1L	62	QUIMICO	\N	114.7	293.63	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
893	LUVA VINIL S/ PÓ G	PROD107	EPIS	\N	12.2	24.4	PCT	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
924	PÁ PLÁSTICA ATIS	PROD138	ACESSÓRIOS	\N	5.9	8.26	UN	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
899	MOP ACRÍLICO 80CM	PROD113	ACESSÓRIOS	\N	15.25	28.21	UN	10	\N	7	1	\N	2025-12-05 14:44:35.094272+00
913	MULTIUSO AZULIM ROSA	PROD127	QUIMICO	\N	2.9	4.06	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
930	PAPEL HIG. CAI CAI C/6.000 FLS	PROD144	PAPÉIS	\N	84	175	ROLO	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
867	LENÇOL HOSPITALAR NOBRE	PROD081	PAPÉIS	\N	14.8	20.72	CX	10	\N	8	1	\N	2025-12-05 14:44:35.094272+00
865	LAVPRO BB 50L	818	QUIMICO	\N	143.98	353	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
877	LUSTRA MOVEIS PEROBBA	PROD091	QUIMICO	\N	5.99	8.39	PCT	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
900	MOP PÓ 80CM MAXI TEX	PROD114	ACESSÓRIOS	\N	41.98	58.77	UN	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
916	NAFTALINA	PROD130	QUIMICO	\N	2.5	3.5	UN	10	\N	52	1	\N	2025-12-05 14:44:35.094272+00
894	LUVA VINIL S/ PÓ M	PROD108	EPIS	\N	18	27	PCT	10	\N	30	1	\N	2025-12-05 14:44:35.094272+00
881	LUVA LATEX AMARELA SILVER G	972	EPIS	\N	3.18	6.36	PCT	10	\N	7	1	\N	2025-12-05 14:44:35.094272+00
1087	Açúcar cristal	PERS-1764783185116-4a2cb9d2	Personalizado	Produto personalizado criado automaticamente	3.55	5.33	UN	0	\N	0	1	\N	2025-12-05 14:44:35.094272+00
1093	ALVITEC OXI BB 5L	ALVIOXI	QUIMICO	\N	44.56	114.07	UN	0	\N	0	1	\N	2025-12-09 19:44:41.426451+00
888	LUVA NITRILICA MULTIUSO VERDE CANO LONGO M	PROD102	EPIS	\N	0	256.62	PCT	10	\N	14	1	\N	2025-12-05 14:44:35.094272+00
871	LIMPADOR C/ BRILHO 5L	PROD085	QUIMICO	\N	0	133	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
902	MOP ÚMIDO 340G - BEGE	PROD116	LIMPEZA GERAL	\N	8.55	17.1	UN	10	\N	16	1	\N	2025-12-05 14:44:35.094272+00
917	NEUTRAL BB 50L	821	QUIMICO	\N	174.61	447	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
945	PERFUMAR BREEZE 1L	PROD159	QUIMICO	\N	10.4	26.62	UN	10	\N	8	1	\N	2025-12-05 14:44:35.094272+00
847	FIBRA LIMPEZA USO LEVE (AZUL) PCT C/ 3	PROD061	FIBRAS	\N	3.07	4.3	UN	10	\N	164	1	\N	2025-12-05 14:44:35.094272+00
809	CABO ALUMÍNIO S/ PONTEIRA	296	ACESSÓRIOS	\N	0	24.38	UN	10	\N	35	1	\N	2025-12-05 14:44:35.094272+00
988	SACO PARA LIXO HOSPITALAR 30L	617	SACOS DE LIXO	\N	16.5	24.75	PCT	10	\N	17	1	\N	2025-12-05 14:44:35.094272+00
954	PLASTILUX BB 5L	PROD168	QUIMICO	\N	75.79	194.02	UN	10	\N	13	1	\N	2025-12-05 14:44:35.094272+00
927	PANO MULTIUSO SLIM 60 PANOS	PROD141	PANOS	\N	16.9	33.8	CX	10	\N	21	1	\N	2025-12-05 14:44:35.094272+00
944	PEDRA SANITARIA SANI	PROD158	QUIMICO	\N	1.85	3.7	UN	10	\N	60	1	\N	2025-12-05 14:44:35.094272+00
990	SACO PARA LIXO PRETO 100L MICRA 0,3	236	SACOS DE LIXO	\N	25.8	38.7	PCT	10	\N	78	1	\N	2025-12-05 14:44:35.094272+00
1105	DOSADOR EASY FOAMER 1,3L	1035	DILUIDOR		289.9	579.8	UN	0	\N	4	1	\N	2025-12-22 17:19:27.062194+00
938	PAPEL TOALHA BOBINA BRANCO 150MTS MG	710	PAPÉIS	\N	48	67.2	PCT	10	\N	11	1	\N	2025-12-05 14:44:35.094272+00
903	MULTIBAC BP BB5L	1020705	QUIMICO	\N	334.55	856.45	UN	10	\N	29	1	\N	2025-12-05 14:44:35.094272+00
995	SACO PARA LIXO PRETO 200L MICRA 0,5	PROD209	SACOS DE LIXO	\N	62.55	93.83	PCT	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
987	SACO PARA LIXO HOSPITALAR 200L LEVE	PROD201	SACOS DE LIXO	\N	58	81.2	PCT	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
964	REMOQUAT BB 20L	PROD178	QUIMICO	\N	205.63	526.41	UN	10	\N	16	1	\N	2025-12-05 14:44:35.094272+00
934	PAPEL HIGIENICO MAX PURE	PROD148	PAPÉIS	\N	16.09	22.53	PCT	10	\N	60	1	\N	2025-12-05 14:44:35.094272+00
940	PAPEL TOALHA INTERF. C1000 20X20 (CÓD.39500) NOBRE	301	PAPÉIS	\N	12.75	19.13	PCT	10	\N	71	1	\N	2025-12-05 14:44:35.094272+00
939	PAPEL TOALHA INTERF. 2.400 FLS	915	PAPÉIS	\N	70.96	141.92	PCT	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
822	DESINCROST GEL BB 5L	787	QUIMICO	\N	44.02	112.69	CX	10	\N	50	1	\N	2025-12-05 14:44:35.094272+00
947	PERFUMAR CAPIM LIMÃO BB 5L	PROD161	QUIMICO	\N	37.13	95.05	UN	10	\N	7	1	\N	2025-12-05 14:44:35.094272+00
925	PANO DE CHAO FLANELADO 'M' TAM: 48X68	259	PANOS	\N	5.49	7.69	PCT	10	\N	439	1	\N	2025-12-05 14:44:35.094272+00
935	PAPEL HIGIENICO MG BRANCO 300MTS	513	PAPÉIS	\N	41.2	57.68	CX	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
876	LOUÇA MAQ PRO BB5L	1034705	QUIMICO	\N	47.19	120.81	UN	10	\N	17	1	\N	2025-12-05 14:44:35.094272+00
931	PAPEL HIGIENICO ROLAO 8X300M (NOBRE)	280	PAPÉIS	\N	51.53	77.3	CX	10	\N	22	1	\N	2025-12-05 14:44:35.094272+00
961	REFIL MOPINHO BRALIMPIA	234	LIMPEZA PESADA	\N	30.76	46.14	UN	10	\N	10	1	\N	2025-12-05 14:44:35.094272+00
874	LIMPAX DX BB5L	518	QUIMICO	\N	41.69	106.73	UN	10	\N	135	1	\N	2025-12-05 14:44:35.094272+00
946	PERFUMAR BREEZE BB5L	36	QUIMICO	\N	37.13	95.05	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
952	PISOFLOR BB 5L	41	QUIMICO	\N	35.08	89.8	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
1094	PAPEL TOALHA BOBINA BEMEL 200M 100% CELULOSE	1025	PAPÉIS	\N	66.5	99.75	UNID	0	\N	20	1	\N	2025-12-11 14:05:39.049722+00
1088	Luva malha com pigmento	PERS-1764785726704-6fa56a45	Personalizado	Produto personalizado criado automaticamente	0	4.5	UN	0	\N	0	1	\N	2025-12-05 14:44:35.094272+00
985	SACO PARA LIXO HOSPITALAR 100L	619	SACOS DE LIXO	\N	35.3	52.95	PCT	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
942	PAPEL TOALHA SCALA	PROD156	PAPÉIS	\N	5.19	7.79	UN	10	\N	11	1	\N	2025-12-05 14:44:35.094272+00
970	RODO DUPLO 35CM NOBRE	PROD184	ACESSÓRIOS	\N	15.5	26.35	UN	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
1046	VASSOURA PIAÇAVA	460	UTENSÍLIOS	\N	8.33	11.66	UN	10	\N	45	1	\N	2025-12-05 14:44:35.094272+00
1000	SACO PARA LIXO PRETO 300L MICRA 0,8	PROD214	SACOS DE LIXO	\N	156	218.4	PCT	10	\N	25	1	\N	2025-12-05 14:44:35.094272+00
1078	teste	PERS-1764644044	Personalizado	Produto personalizado criado automaticamente	0	4	UN	0	\N	0	1	\N	2025-12-05 14:44:35.094272+00
891	LUVA NITRILICA VERDE M	PROD105	EPIS	\N	7.89	11.05	PCT	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
892	LUVA NITRILICA VERDE P	PROD106	EPIS	\N	78.9	11.05	PCT	10	\N	28	1	\N	2025-12-05 14:44:35.094272+00
950	PERFUMAR SOFT BB 5L	PROD164	QUIMICO	\N	57.68	147.66	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
960	REFIL MOPINHO BETANIN	PROD174	LIMPEZA PESADA	\N	28	20	UN	10	\N	12	1	\N	2025-12-05 14:44:35.094272+00
982	SACO PARA LIXO AZUL 30L MICRA 0,25	PROD196	SACOS DE LIXO	\N	12.1	16.94	PCT	10	\N	19	1	\N	2025-12-05 14:44:35.094272+00
958	REFIL MOP PÓ ALGODÃO 60CM	PROD172	ACESSÓRIOS	\N	16.05	32.1	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
998	SACO PARA LIXO PRETO 300L MICRA 0,4	PROD212	SACOS DE LIXO	\N	85	119	PCT	10	\N	28	1	\N	2025-12-05 14:44:35.094272+00
981	SACO PARA LIXO AZUL 100L MICRA 0,4	PROD195	SACOS DE LIXO	\N	43.2	60.48	PCT	10	\N	20	1	\N	2025-12-05 14:44:35.094272+00
973	SABÃO EM BARRA GAROTO	PROD187	QUIMICO	\N	9.3	13.02	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
986	SACO PARA LIXO HOSPITALAR 15L	PROD200	SACOS DE LIXO	\N	12	18	PCT	10	\N	20	1	\N	2025-12-05 14:44:35.094272+00
959	REFIL MOP PÓ ALGODÃO 80CM	PROD173	ACESSÓRIOS	\N	41.98	58.77	UN	10	\N	22	1	\N	2025-12-05 14:44:35.094272+00
948	PERFUMAR FRESH LEMON BB5L	PROD162	QUIMICO	\N	57.68	147.66	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
994	SACO PARA LIXO PRETO 200L MICRA 0,4	PROD208	SACOS DE LIXO	\N	49	68.6	PCT	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
975	SABÃO EM BARRA NUTRILAR	PROD189	QUIMICO	\N	0	2.75	UN	1	\N	10	1	\N	2025-12-05 14:44:35.094272+00
971	RODO SAFE PRO 50CM PERFECT	PROD185	ACESSÓRIOS	\N	30.51	51.87	UN	10	\N	12	1	\N	2025-12-05 14:44:35.094272+00
953	PLACA SINALIZAÇÃO PISO MOLHADO	PROD167	ACESSÓRIOS	\N	32.6	65.2	UN	10	\N	9	1	\N	2025-12-05 14:44:35.094272+00
922	PÁ COLETORA C/ CABO JEITOSA	PROD136	ACESSÓRIOS	\N	11.93	17.9	UN	10	\N	16	1	\N	2025-12-05 14:44:35.094272+00
949	PERFUMAR LIRIOS DO CAMPO BB5L	PROD163	QUIMICO	\N	37.13	95.05	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
943	PEDRA SANITARIA AZULIM 25G	PROD157	QUIMICO	\N	2.08	3.12	UN	10	\N	88	1	\N	2025-12-05 14:44:35.094272+00
969	RODO COMBINADO 40CM S/ CABO	PROD183	ACESSÓRIOS	\N	28.4	45.44	UN	10	\N	10	1	\N	2025-12-05 14:44:35.094272+00
972	RODO TWISTER	PROD186	ACESSÓRIOS	\N	63.11	88.35	CX	10	\N	4	1	\N	2025-12-05 14:44:35.094272+00
957	REFIL MOP PÓ ALGODÃO 40CM	PROD171	ACESSÓRIOS	\N	19.68	39.36	UN	10	\N	27	1	\N	2025-12-05 14:44:35.094272+00
967	RENOVADOR DE PNEUS	PROD181	QUIMICO	\N	24.92	65.49	UN	10	\N	4	1	\N	2025-12-05 14:44:35.094272+00
979	SABONETE SUAVITEX DX CITRUS 1L	PROD193	QUIMICO	\N	10.21	26.14	PCT	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
955	PULVERIZADOR 1L	PROD169	ACESSÓRIOS	\N	104.04	176.88	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
928	PANO MULTIUSO SLIM 600 PANOS	PROD142	PANOS	\N	79.65	111.51	CX	10	\N	4	1	\N	2025-12-05 14:44:35.094272+00
1021	SANILUX BB 5L	23	QUIMICO	\N	56.58	144.84	UN	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
883	LUVA MULTIUSO LATEX QUALITY BETANIN G	PROD097	EPIS	\N	3.45	5.87	PCT	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
1022	SANIMAX BB 5L	474	QUIMICO	\N	130.04	332.9	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
1013	SANIFLOR EUCALIPTO BB 5L	PROD227	QUIMICO	\N	38.19	97.77	UN	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
803	AROMATIZANTE TALCO	362	QUIMICO	\N	0	14.69	UN	10	\N	35	1	\N	2025-12-05 14:44:35.094272+00
787	ACIDO MURIATICO RETIRO 1L CX C/12	982	QUIMICO	\N	3.58	5.37	UN	10	\N	10	1	\N	2025-12-05 14:44:35.094272+00
1113	PANO MICROFIBRA 45X65CM	PERS-1769713654162-3c090c65	Personalizado	Produto personalizado criado automaticamente	\N	12.77	UN	0	\N	0	1	\N	2026-01-29 19:07:34.067685+00
1024	SEC MAQ PRO BB5L	334	QUIMICO	\N	69.07	176.82	UN	10	\N	36	1	\N	2025-12-05 14:44:35.094272+00
1010	SANIFLOR BREEZE BB5L	PROD224	QUIMICO	\N	37.13	95.05	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
933	PAPEL HIGIÊNICO HR PAPEIS 100% CELULOSE 8X300	PROD147	PAPÉIS	\N	55	7.7	ROLO	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
974	SABÃO EM BARRA GUARANI LIMÃO 10X5	PROD188	QUIMICO	\N	0	11.22	CX	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
835	DISPENSER PAPEL TOALHA INTERF.	PROD049	UTENSÍLIOS	\N	0	41.3	UN	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
1065	MULTIUSO AZULIM ORIGINAL	AZULIM	QUIMICO	\N	2.9	4.06	UN	5	2026-09-02	0	1	\N	2025-12-05 14:44:35.094272+00
820	DESINCROST BB5L	8	QUIMICO	\N	81.67	209.08	UN	10	\N	56	1	\N	2025-12-05 14:44:35.094272+00
817	COPO DESCARTAVEL 150ML - ULTRA	792	DESCARTÁVEIS	\N	3.95	6.32	PCT	150	\N	100	1	\N	2025-12-05 14:44:35.094272+00
1026	SUAVITEX ANDIROBA 1L	PROD240	QUIMICO	\N	8.45	21.63	UN	10	\N	9	1	\N	2025-12-05 14:44:35.094272+00
1027	SUAVITEX BAC BB 1L	PROD241	QUIMICO	\N	9.99	25.57	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
999	SACO PARA LIXO PRETO 300L MICRA 0,5	167	SACOS DE LIXO	\N	99.9	149.85	PCT	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
951	PERFUMAR LAVANDA BB 5L	341	QUIMICO	\N	57.68	147.66	UN	10	\N	4	1	\N	2025-12-05 14:44:35.094272+00
1014	SANIFLOR LIRIOS DO CAMPO BB5L	1023305	QUIMICO	\N	37.13	95.05	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
895	MASCARA CIRÚRGICA TRIPLA	PROD109	DESCARTÁVEIS	\N	9.9	12.14	PCT	10	\N	150	1	\N	2025-12-05 14:44:35.094272+00
1043	VASSOURA 60CM BETANNIN	445	UTENSÍLIOS	\N	23.9	33.46	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
1005	SACO PRETO 250L MICRA 05	PROD219	SACOS DE LIXO	\N	100	140	UN	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
1040	TELA P/MICTORIO	556	UTENSÍLIOS	\N	2.3	4.6	UN	10	\N	108	1	\N	2025-12-05 14:44:35.094272+00
1042	VASCULHADOR NYLON	PROD256	UTENSÍLIOS	\N	24.5	34.3	UN	10	\N	4	1	\N	2025-12-05 14:44:35.094272+00
996	SACO PARA LIXO PRETO 200L MICRA 0,8	394	SACOS DE LIXO	\N	0	51.38	PCT	10	\N	14	1	\N	2025-12-05 14:44:35.094272+00
1079	Adoçante liq 100ml	PERS-1764768978	Personalizado	Produto personalizado criado automaticamente	4.19	6.89	UN	0	\N	0	1	\N	2025-12-05 14:44:35.094272+00
1114	BOBIMA 3KG GENÉRICA 	PERS-1769713654362-aceee0b7	Personalizado	Produto personalizado criado automaticamente	\N	22.25	UN	0	\N	0	1	\N	2026-01-29 19:07:34.067685+00
808	CABO ALUMÍNIO C/ PONTEIRA	PROD022	ACESSÓRIOS	\N	13.76	27.52	UN	10	\N	17	1	\N	2025-12-05 14:44:35.094272+00
968	RODO 55 CM	295	ACESSÓRIOS	\N	23.65	35.48	UN	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
801	AROMATIZANTE JARDIM DE PEÔNIA	PROD015	QUIMICO	\N	0	14.92	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
885	LUVA MULTIUSO LATEX QUALITY BETANIN P	742	EPIS	\N	3.45	5.87	PCT	10	\N	78	1	\N	2025-12-05 14:44:35.094272+00
1019	SANIFLOR SOFT BB 5L	174	QUIMICO	\N	37.13	95.05	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
992	SACO PARA LIXO PRETO 100L MICRA 0,8	726	SACOS DE LIXO	\N	68.5	102.75	PCT	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
1009	SANIFLOR BREEZE 1L	PROD223	QUIMICO	\N	8.7	22.27	UN	10	\N	8	1	\N	2025-12-05 14:44:35.094272+00
887	LUVA NITRILICA MULTIUSO VERDE CANO LONGO G	PROD101	EPIS	\N	0	18.33	PCT	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
850	FLANELA BRANCA CRISTAL 40X60	644	PANOS	\N	2.08	2.91	UN	10	\N	115	1	\N	2025-12-05 14:44:35.094272+00
983	SACO PARA LIXO AZUL 40L MICRA 0,25	397	SACOS DE LIXO	\N	12.8	17.92	PCT	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
1089	LIXEIRA PLÁSTICA C PEDAL 15L NOBRE	PERS-1764877856247-94d0040f	LIXEIRAS	Produto personalizado criado automaticamente	29.83	59.66	UN	0	\N	3	1	\N	2025-12-05 14:44:35.094272+00
914	MULTIUSO AZULIM VERDE	PROD128	QUIMICO	\N	2.9	4.06	PCT	10	\N	2	1	\N	2025-12-05 14:44:35.094272+00
1015	SANIFLOR MAX FRESH LEMON BB 5L	138	QUIMICO	\N	55.17	141.24	UN	10	\N	16	1	\N	2025-12-05 14:44:35.094272+00
1039	SUPORTE MOP ÚMIDO	PROD253	ACESSÓRIOS	\N	8.89	12.45	PCT	10	\N	17	1	\N	2025-12-05 14:44:35.094272+00
1023	SANIMAX BB1L	PROD237	QUIMICO	\N	35.57	91.06	UN	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
1032	SUAVITEX PESSEGO 1L	PROD246	QUIMICO	\N	9.99	25.57	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
1086	produto de teste	PERS-1764772035	Personalizado	Produto personalizado criado automaticamente	0	9.99	UN	0	\N	0	1	\N	2025-12-05 14:44:35.094272+00
884	LUVA MULTIUSO LATEX QUALITY BETANIN M	PROD098	EPIS	\N	3.45	5.87	PCT	10	\N	56	1	\N	2025-12-05 14:44:35.094272+00
854	GEL ANTISSEPTICO 500ML BOLSA	PROD068	QUIMICO	\N	13.41	34.33	UN	10	\N	24	1	\N	2025-12-05 14:44:35.094272+00
1090	LIXEIRA PLÁSTICA C PEDAL 100L NOBRE	PERS-1764877856251-9ffa9c96	LIXEIRAS	Produto personalizado criado automaticamente	75.65	258.46	UN	0	\N	7	1	\N	2025-12-05 14:44:35.094272+00
1004	SACO PARA LIXO TRANSPARENTE 60L	PROD218	SACOS DE LIXO	\N	0	26.25	UN	10	\N	8	1	\N	2025-12-05 14:44:35.094272+00
1003	SACO PARA LIXO TRANSPARENTES 100L MICRA 0,5	PROD217	SACOS DE LIXO	\N	65.7	98.55	PCT	10	\N	12	1	\N	2025-12-05 14:44:35.094272+00
1008	SANICLOR DT BB 5L	PROD222	QUIMICO	\N	53.21	136.22	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
1034	SUAVITEX PRO ERVA DOCE BB5L	PROD248	QUIMICO	\N	20.73	53.07	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
1020	SANILUX 1L	PROD234	QUIMICO	\N	12.48	31.95	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
1037	SUAVITEX PRO SP ERVA DOCE 500ML	PROD251	QUIMICO	\N	7.4	18.94	UN	10	\N	69	1	\N	2025-12-05 14:44:35.094272+00
1038	SUPORTE LT	PROD252	ACESSÓRIOS	\N	9.57	19.14	UN	10	\N	32	1	\N	2025-12-05 14:44:35.094272+00
898	MOP ACRÍLICO 60CM	PROD112	ACESSÓRIOS	\N	15.25	28.21	UN	10	\N	25	1	\N	2025-12-05 14:44:35.094272+00
1044	VASSOURA CASA E RUA BETANIN	PROD258	UTENSÍLIOS	\N	14.9	29.8	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
1047	VASSOURÃO GARI	PROD261	UTENSÍLIOS	\N	24	33.6	UN	10	\N	15	1	\N	2025-12-05 14:44:35.094272+00
1025	SPRAY SANITIZANTE BOLSA 500ML	222	QUIMICO	\N	11.47	29.36	UN	10	\N	324	1	\N	2025-12-05 14:44:35.094272+00
1001	SACO PARA LIXO PRETO 40L - 0,25	135	SACOS DE LIXO	\N	9.7	14.55	PCT	10	\N	30	1	\N	2025-12-05 14:44:35.094272+00
1092	LIXEIRA PLÁSTICA C PEDAL 50L NOBRE	PERS-1764877856258-9c1c369b	Personalizado	Produto personalizado criado automaticamente	75.65	151.3	UN	0	\N	5	1	\N	2025-12-05 14:44:35.094272+00
980	SABONETE SUAVITEX DX CITRUS BB 5L	1005705	QUIMICO	\N	39.61	101.4	PCT	10	\N	31	1	\N	2025-12-05 14:44:35.094272+00
1012	SANIFLOR CAPIM LIMÃO BB 5L	47	QUIMICO	\N	37.05	95.05	UN	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
1108	HC Pindorama	PERS-1768262656127-5a55fffa	Personalizado	Produto personalizado criado automaticamente	\N	33.75	UN	0	\N	0	1	\N	2026-01-13 00:04:16.123579+00
1007	SANICLOR DT BB 20L	1034322	QUIMICO	\N	172.39	441.32	UN	10	\N	61	1	\N	2025-12-05 14:44:35.094272+00
978	SABONETE DX MICRO ESFERA	52	QUIMICO	\N	60.38	154.57	UN	10	\N	9	1	\N	2025-12-05 14:44:35.094272+00
991	SACO PARA LIXO PRETO 100L MICRA 0,5	136	SACOS DE LIXO	\N	47	70.5	PCT	10	\N	19	1	\N	2025-12-05 14:44:35.094272+00
989	SACO PARA LIXO HOSPITALAR 50L	618	SACOS DE LIXO	\N	22.5	33.75	PCT	10	\N	24	1	\N	2025-12-05 14:44:35.094272+00
966	REMOX BB5L	215	QUIMICO	\N	60.47	154.8	UN	16	\N	24	1	\N	2025-12-05 14:44:35.094272+00
963	REMOCRIL POWER 5L	1017305	QUIMICO	\N	119.55	306.05	UN	2	\N	24	1	\N	2025-12-05 14:44:35.094272+00
1018	SANIFLOR PLUS SOFT	1007505	QUIMICO	\N	170.73	437.07	UN	10	\N	4	1	\N	2025-12-05 14:44:35.094272+00
1091	LIXEIRA PLÁSTICA C PEDAL 30L NOBRE	1028	Personalizado	Produto personalizado criado automaticamente	58.69	117.38	UN	0	\N	0	1	\N	2025-12-05 14:44:35.094272+00
1006	SANICLOR BB5L	191	QUIMICO	\N	30.93	79.18	UN	10	\N	32	1	\N	2025-12-05 14:44:35.094272+00
1085	novo produto de teste	PERS-1764770879	Personalizado	Produto personalizado criado automaticamente	\N	5	UN	0	\N	0	1	\N	2025-12-05 14:44:35.094272+00
976	SABÃO EM BARRA YPE ALOE E VERA 10X5	636	QUIMICO	\N	12	16.8	UN	10	\N	52	1	\N	2025-12-05 14:44:35.094272+00
870	LIMPA PORCELANATO BB5L	1030205	QUIMICO	\N	62.29	159.46	UN	10	\N	38	1	\N	2025-12-05 14:44:35.094272+00
962	REMOCALC BB 20L	1024522	QUIMICO	\N	468.32	1198.9	UN	1	\N	24	1	\N	2025-12-05 14:44:35.094272+00
965	REMOX BB 20L	901	QUIMICO	\N	277.53	710.48	UN	10	\N	24	1	\N	2025-12-05 14:44:35.094272+00
908	MULTILUX BAC SOFT BB 5L	28	QUIMICO	\N	154.93	396.62	UN	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
1028	SUAVITEX BAC BB 5L	1013805	QUIMICO	\N	35	89.6	UN	10	\N	7	1	\N	2025-12-05 14:44:35.094272+00
1048	VIDROLUX BB 5L	40	QUIMICO	\N	32.75	83.84	L	10	\N	11	1	\N	2025-12-05 14:44:35.094272+00
919	OXIPRO NATURAL BB5L	1027305	QUIMICO	\N	51.43	131.66	UN	10	\N	21	1	\N	2025-12-05 14:44:35.094272+00
1017	SANIFLOR PLUS CAPIM LIMÃO BB5L	1022705	QUIMICO	\N	\N	389	UN	10	\N	0	1	\N	2025-12-05 14:44:35.094272+00
997	SACO PARA LIXO PRETO 20L - 0,25	189	SACOS DE LIXO	\N	7.8	11.7	PCT	10	\N	44	1	\N	2025-12-05 14:44:35.094272+00
936	PAPEL TOALHA MG KING SOFT 640 FOLHAS	262	PAPÉIS	\N	7.92	11.09	ROLO	10	\N	980	1	\N	2025-12-05 14:44:35.094272+00
1111	ÁLCOOL GEL SAFRA 5L	PERS-1768654969167-7325f511	Personalizado	Produto personalizado criado automaticamente	\N	62.23	UN	0	\N	0	1	\N	2026-01-17 13:02:49.164002+00
993	SACO PARA LIXO PRETO 200L MICRA 0,3	399	SACOS DE LIXO	\N	34.6	51.9	PCT	10	\N	18	1	\N	2025-12-05 14:44:35.094272+00
984	SACO PARA LIXO AZUL 60L MICRA 0,3	568	SACOS DE LIXO	\N	17.8	24.92	PCT	10	\N	13	1	\N	2025-12-05 14:44:35.094272+00
1098	DISCO PARA ENCERADEIRA VERDE 410MM	VER41	FIBRA	\N	19.1	38.2	UN	0	\N	10	1	\N	2025-12-15 17:34:30.60125+00
1102	MOP ÚMIDO 340G - AZUL	SAS	MOP	\N	\N	34.27	UN	0	\N	24	1	\N	2025-12-18 12:17:44.664559+00
905	MULTILUX BAC BREEZE BB5L	27	QUIMICO	\N	154.93	396.62	UN	10	\N	3	1	\N	2025-12-05 14:44:35.094272+00
956	PULVERIZADOR 500ML	508	ACESSÓRIOS	\N	7.52	12.78	UN	10	\N	55	1	\N	2025-12-05 14:44:35.094272+00
1075	REFIL MOPINHO ENCAIXE HEXAG	MOPHE	MOP	\N	20	28	UN	0	2026-11-17	0	1	\N	2025-12-05 14:44:35.094272+00
1011	SANIFLOR CAMPESTRE BB 5L	1004905	QUIMICO	\N	37.13	95.05	UN	10	\N	14	1	\N	2025-12-05 14:44:35.094272+00
1033	SUAVITEX PRAXI ANDIROBA BB 5L	606	QUIMICO	\N	34.76	88.99	UN	10	\N	11	1	\N	2025-12-05 14:44:35.094272+00
909	MULTILUX BAC SOFT DOS1L	PROD123	QUIMICO	\N	40.91	104.73	UN	10	\N	6	1	\N	2025-12-05 14:44:35.094272+00
1062	ÁLCOOL SAFRA 5L	660	QUIMICO	\N	42	58.8	UN	4	2028-08-22	11	1	\N	2025-12-05 14:44:35.094272+00
918	OXIPRO FRESH LEMON BB5L	124	QUIMICO	\N	58.65	150.14	UN	10	\N	13	1	\N	2025-12-05 14:44:35.094272+00
920	OXIPRO SOFT BB5L	25	ACESSÓRIOS	\N	58.65	165.94	UN	10	\N	16	1	\N	2025-12-05 14:44:35.094272+00
1106	LIXEIRA PLÁSTICA C PEDAL 120L LARANJA TONK	PERS-1767020362340-c906800b	Personalizado	Produto personalizado criado automaticamente	\N	523.5	UN	0	\N	0	1	\N	2025-12-29 14:59:22.336292+00
1107	LIXEIRA PLÁSTICA C PEDAL 120L AZUL TONK	PERS-1767020362347-8d4278ba	Personalizado	Produto personalizado criado automaticamente	\N	523.5	UN	0	\N	0	1	\N	2025-12-29 14:59:22.336292+00
827	DISCO LIMPADOR VERDE ABRASIVO 410	316	ACESSÓRIOS	\N	19.1	38.2	UN	10	\N	4	1	\N	2025-12-05 14:44:35.094272+00
1035	SUAVITEX PRO MILK BB5L	1028205	QUIMICO	\N	35	89.6	UN	10	\N	90	1	\N	2025-12-05 14:44:35.094272+00
1016	SANIFLOR MAX SOFT BB 5L	48	QUIMICO	\N	55.17	141.24	UN	10	\N	20	1	\N	2025-12-05 14:44:35.094272+00
1066	PAPEL HIGIENICO 8X300M BRANCO	BEME300	PAPÉIS	\N	34.56	57.6	UN	5	2026-09-02	0	1	\N	2025-12-05 14:44:35.094272+00
1071	MULTIBAC PRATIK 500ML	1033541	QUIMICO	\N	18.23	46.66	UN	2	2026-11-11	8	1	\N	2025-12-05 14:44:35.094272+00
1068	PAPEL TOALHA INTERF. MG 100% CELULOSE 1000 FLS	PAPINT2	PAPÉIS	PAPEL TOALHA INTERF. 100% CELULOSE 1000 FLS - 120 unid	12.5	17.5	UN	15	\N	0	1	\N	2025-12-05 14:44:35.094272+00
848	FIBRA PESADA	103	ACESSÓRIOS	\N	1.56	3.12	ROLO	10	\N	399	1	\N	2025-12-05 14:44:35.094272+00
1070	SANICLOR BB1L	SCLORBB1L	QUIMICO	SANICLOR BB1L	9.45	24.19	L	15	\N	42	1	\N	2025-12-05 14:44:35.094272+00
1002	SACO PARA LIXO PRETO 60L - 0,25	134	SACOS DE LIXO	\N	13.5	20.25	PCT	10	\N	61	1	\N	2025-12-05 14:44:35.094272+00
937	PAPEL TOALHA BOBINA HR 200X6 100% CELULOSE	82	PAPÉIS	\N	73.5	102.9	PCT	10	\N	1	1	\N	2025-12-05 14:44:35.094272+00
1036	SUAVITEX PRO PESSEGO BB5L	60	QUIMICO	\N	35	89.6	UN	10	\N	82	1	\N	2025-12-05 14:44:35.094272+00
1045	VASSOURA LINDONA	198	UTENSÍLIOS	\N	11.08	15.86	UN	10	\N	40	1	\N	2025-12-05 14:44:35.094272+00
1031	SUAVITEX LEITE HIDRATE 1L	1004510	QUIMICO	\N	14.7	37.63	UN	10	\N	5	1	\N	2025-12-05 14:44:35.094272+00
889	LUVA NITRILICA SEM PÓ M PRETA	1009	EPIS	\N	19.5	33.15	PCT	10	\N	89	1	\N	2025-12-05 14:44:35.094272+00
1030	SUAVITEX BAC SP 500ML BOL	344	QUIMICO	\N	10.71	27.42	UN	10	\N	22	1	\N	2025-12-05 14:44:35.094272+00
941	PAPEL TOALHA INTERF.C/ 1000F 100% CELULOSE PREMIUM BEMEL	389	PAPÉIS	\N	11	17.5	UN	10	\N	100	1	\N	2025-12-05 14:44:35.094272+00
977	SABÃO EM PO ALA FLOR DE LIS 400G	942	QUIMICO	\N	2.97	4.5	UN	10	\N	82	1	\N	2025-12-05 14:44:35.094272+00
1076	MULTILUX BAC CAPIM LIMÃO BB 5L	1022505	QUIMICO	\N	154.93	396.62	UN	2	2027-07-15	5	1	\N	2025-12-05 14:44:35.094272+00
1099	CARRO BALDE 35L (C/ DIVISOR DE AGUA ESPREMEDOR)	35LAS	DISPENSER	\N	348.99	558.38	UNID	0	\N	3	1	\N	2025-12-15 17:35:49.249673+00
1095	Dispenser p/ sabonete líquido Velox	PERS-1765548677571-b90e1bea	Personalizado	Produto personalizado criado automaticamente	\N	43.5	UN	0	\N	0	1	\N	2025-12-12 14:11:17.569806+00
926	PANO DE CHAO XADREZ TAM: 50X75 CM - COD 14	457	PANOS	\N	3.1	4.34	ROLO	10	\N	319	1	\N	2025-12-05 14:44:35.094272+00
\.


--
-- Data for Name: produtos_concorrentes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.produtos_concorrentes (id, nome, marca, preco_medio, rendimento_litro, dilucao, dilucao_numerador, dilucao_denominador, categoria, observacoes, ativo, data_criacao, data_atualizacao) FROM stdin;
\.


--
-- Data for Name: propostas_detalhadas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.propostas_detalhadas (id, orcamento_id, cliente_id, vendedor_id, produto_id, ficha_tecnica_id, quantidade_produto, dilucao_aplicada, dilucao_numerador, dilucao_denominador, rendimento_total_litros, preco_produto, custo_por_litro_final, concorrente_id, economia_vs_concorrente, economia_percentual, economia_valor, observacoes, compartilhavel, token_compartilhamento, data_criacao, data_atualizacao) FROM stdin;
3	\N	27	11	789	\N	1	1:4	1	4	4	47.09	11.7725	\N	\N	\N	\N	\N	f	\N	2025-11-21 13:15:45.075922+00	2025-11-21 13:15:45.075922+00
4	\N	23	11	789	\N	5	1:5	1	5	25	47.09	9.418000000000001	\N	\N	\N	\N	\N	f	\N	2025-11-25 12:22:36.530013+00	2025-11-25 12:22:36.530013+00
5	\N	40	11	789	\N	5	1:10	1	10	50	47.09	4.7090000000000005	\N	\N	\N	\N	teste	f	\N	2025-12-03 00:00:53.836217+00	2025-12-03 00:00:53.836217+00
6	\N	40	11	789	\N	5	1:10	1	10	50	47.09	4.7090000000000005	\N	\N	\N	\N	novo teste 	f	\N	2025-12-03 00:07:55.296115+00	2025-12-03 00:07:55.296115+00
7	\N	30	9	1016	\N	1	1:250	1	250	250	141.24	0.56496	\N	\N	\N	\N	\N	f	\N	2026-01-09 17:40:04.524871+00	2026-01-09 17:40:04.524871+00
8	\N	30	9	1016	\N	1	1:250	1	250	250	141.24	0.56496	\N	\N	\N	\N	\N	f	\N	2026-01-09 18:10:27.21887+00	2026-01-09 18:10:27.21887+00
9	\N	30	9	1016	\N	1	1:250	1	250	250	141.24	0.56496	\N	\N	\N	\N	\N	f	\N	2026-01-09 18:53:07.762948+00	2026-01-09 18:53:07.762948+00
10	\N	30	9	1016	\N	1	1:250	1	250	250	141.24	0.56496	\N	\N	\N	\N	\N	f	\N	2026-01-12 14:03:23.084487+00	2026-01-12 14:03:23.084487+00
11	\N	30	9	1016	\N	1	1:250	1	250	250	141.24	0.56496	\N	\N	\N	\N	\N	f	\N	2026-01-12 14:18:34.653298+00	2026-01-12 14:18:34.653298+00
12	\N	30	9	1016	\N	1	1:250	1	250	250	141.24	0.56496	\N	\N	\N	\N	\N	f	\N	2026-01-12 14:28:58.349131+00	2026-01-12 14:28:58.349131+00
13	\N	31	9	1016	\N	1	1:250	1	250	250	141.24	0.56496	\N	\N	\N	\N	\N	f	\N	2026-01-12 14:34:46.250124+00	2026-01-12 14:34:46.250124+00
14	\N	30	9	1016	\N	1	1:250	1	250	250	141.24	0.56496	\N	\N	\N	\N	\N	f	\N	2026-01-12 14:44:12.18581+00	2026-01-12 14:44:12.18581+00
15	\N	64	9	1019	\N	1	1:20	1	20	20	95.05	4.7524999999999995	\N	\N	\N	\N	\N	f	\N	2026-01-17 13:17:34.63274+00	2026-01-17 13:17:34.63274+00
16	\N	64	9	1016	\N	1	1:200	1	200	200	141.24	0.7062	\N	\N	\N	\N	\N	f	\N	2026-01-19 17:07:05.431309+00	2026-01-19 17:07:05.431309+00
17	\N	64	9	1019	\N	1	1:100	1	100	100	95.05	0.9505	\N	\N	\N	\N	\N	f	\N	2026-01-19 17:11:32.449989+00	2026-01-19 17:11:32.449989+00
18	\N	48	9	1012	\N	1	1:50	1	50	50	95.05	1.901	\N	\N	\N	\N	\N	f	\N	2026-01-24 00:29:23.012316+00	2026-01-24 00:29:23.012316+00
19	\N	30	9	789	\N	1	1:20	1	20	20	46.85	2.3425000000000002	\N	\N	\N	\N	\N	f	\N	2026-01-28 14:48:19.981474+00	2026-01-28 14:48:19.981474+00
\.


--
-- Data for Name: propostas_detalhadas_concorrentes; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.propostas_detalhadas_concorrentes (id, proposta_id, nome, rendimento_litro, custo_por_litro, observacoes, ordem, data_criacao, data_atualizacao) FROM stdin;
1	5	agua sanitária jesus	1	2.59		1	2025-12-03 00:00:53.836217+00	2025-12-03 00:00:53.836217+00
\.


--
-- Data for Name: propostas_detalhadas_itens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.propostas_detalhadas_itens (id, proposta_id, produto_id, quantidade_produto, dilucao_aplicada, dilucao_numerador, dilucao_denominador, rendimento_total_litros, preco_produto, custo_por_litro_final, observacoes, ordem, concorrente_nome_manual, concorrente_rendimento_manual, concorrente_custo_por_litro_manual, data_criacao, data_atualizacao, concorrente_quantidade, concorrente_dilucao_numerador, concorrente_dilucao_denominador) FROM stdin;
1	3	789	1	1:4	1	4	4	47.09	11.7725	\N	1	\N	\N	\N	2025-11-27 02:24:37.725784+00	2025-11-27 02:24:37.725784+00	\N	\N	\N
2	4	789	5	1:5	1	5	25	47.09	9.418000000000001	\N	1	\N	\N	\N	2025-11-27 02:24:37.725784+00	2025-11-27 02:24:37.725784+00	\N	\N	\N
3	5	789	5	1:10	1	10	50	47.09	4.7090000000000005	limpeza pesada	1	\N	\N	\N	2025-12-03 00:00:53.836217+00	2025-12-03 00:00:53.836217+00	\N	\N	\N
4	6	789	5	1:10	1	10	50	47.09	4.7090000000000005	Limpeza pesada	1	agua sanitária	125	29.99	2025-12-03 00:07:55.296115+00	2025-12-03 00:07:55.296115+00	\N	\N	\N
5	7	1016	1	1:250	1	250	250	141.24	0.56496	\N	1	castelo clean	10	50	2026-01-09 17:40:04.524871+00	2026-01-09 17:40:04.524871+00	1	1	10
6	8	1016	1	1:250	1	250	250	141.24	0.56496	20	1	Castelo clean 	10	\N	2026-01-09 18:10:27.21887+00	2026-01-09 18:10:27.21887+00	1	1	10
7	9	1016	1	1:250	1	250	250	141.24	0.56496	\N	1	Castelo clean	10	3.5	2026-01-09 18:53:07.762948+00	2026-01-09 18:53:07.762948+00	1	1	10
8	10	1016	1	1:250	1	250	250	141.24	0.56496	\N	1	palmolive	5	29	2026-01-12 14:03:23.084487+00	2026-01-12 14:03:23.084487+00	1	1	5
9	11	1016	1	1:250	1	250	250	141.24	0.56496	\N	1	Palmolive 	5	5.98	2026-01-12 14:18:34.653298+00	2026-01-12 14:18:34.653298+00	1	1	5
10	12	1016	1	1:250	1	250	250	141.24	0.56496	\N	1	PALMOLIVE	5	5.98	2026-01-12 14:28:58.349131+00	2026-01-12 14:28:58.349131+00	1	1	5
11	13	1016	1	1:250	1	250	250	141.24	0.56496	\N	1	palmolive	\N	5.98	2026-01-12 14:34:46.250124+00	2026-01-12 14:34:46.250124+00	1	\N	5
12	13	1016	1	1:250	1	250	250	141.24	0.56496	\N	2	palmolive	5	5.98	2026-01-12 14:34:46.250124+00	2026-01-12 14:34:46.250124+00	1	1	5
13	14	1016	1	1:250	1	250	250	141.24	0.56496	\N	1	castelo	5	5.97	2026-01-12 14:44:12.18581+00	2026-01-12 14:44:12.18581+00	1	1	5
14	15	1019	1	1:20	1	20	20	95.05	4.7524999999999995	\N	1	CASTELO	10	14.5	2026-01-17 13:17:34.63274+00	2026-01-17 13:17:34.63274+00	1	1	10
15	15	1016	1	1:40	1	40	40	141.24	3.531	\N	2	CENTER CLEAN	10	14.5	2026-01-17 13:17:34.63274+00	2026-01-17 13:17:34.63274+00	1	1	10
16	15	920	1	1:40	1	40	40	165.94	4.1485	\N	3	CASTELO	10	14.5	2026-01-17 13:17:34.63274+00	2026-01-17 13:17:34.63274+00	1	1	10
17	16	1016	1	1:200	1	200	200	141.24	0.7062	\N	1	CASTELO	10	14.45	2026-01-19 17:07:05.431309+00	2026-01-19 17:07:05.431309+00	1	1	10
18	17	1019	1	1:100	1	100	100	95.05	0.9505	\N	1	CENTER CLEAN	10	14.45	2026-01-19 17:11:32.449989+00	2026-01-19 17:11:32.449989+00	1	1	10
19	18	1012	1	1:50	1	50	50	95.05	1.901	\N	1	castelo	10	14.5	2026-01-24 00:29:23.012316+00	2026-01-24 00:29:23.012316+00	1	1	10
20	19	789	1	1:20	1	20	20	46.85	2.3425000000000002	\N	1	clean	10	7.55	2026-01-28 14:48:19.981474+00	2026-01-28 14:48:19.981474+00	1	1	10
\.


--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.refresh_tokens (id, token, usuario_id, expires_at, created_at, revoked) FROM stdin;
1	r4DPSZuhZJSMdujJigHwXr6ON7Gt2jyRrsDPiCfqKpE	1	2025-10-31 13:16:37.415904+00	2025-10-24 13:16:36.987071+00	f
2	vdzUCcSGs8jv30DMr4LSeExYRipdjHYGn9oUh5A_PUM	3	2025-10-31 17:11:17.353782+00	2025-10-24 17:11:16.962705+00	f
3	1UeVXILcn3swYpavMHfsaEm5cDH3bTJKVtsSVjSeUvA	3	2025-11-03 13:27:00.102868+00	2025-10-27 13:26:59.683457+00	f
4	qhc-GPS3_3cZKvEddOiAkk6GnGYTrTY2la_1JfTlraE	3	2025-11-03 18:03:25.700397+00	2025-10-27 18:03:25.300976+00	f
5	HUpt9IB0gWLyooysCPn2gScg0jULBVWIk4htXczlNgI	3	2025-11-03 19:03:48.601417+00	2025-10-27 19:03:48.18822+00	f
6	1yG22uQo_fE3WiyDXMa4GBvr9v0q62ZXfhQotmHlrZY	3	2025-11-04 12:57:39.558537+00	2025-10-28 12:57:39.114737+00	f
7	fFoJ4EsbOPzNMRfrvXWkRhb6yrZd0hPYiS0GQTlGmsA	3	2025-11-04 14:48:24.679116+00	2025-10-28 14:48:24.306625+00	f
8	PubBGwyjHXeePvEHZqmQyu24zRKIfWDS2q-K1jaY--E	3	2025-11-04 19:21:39.677318+00	2025-10-28 19:21:39.282501+00	f
9	P1DnsROfj0eqlQKXviW0qlDEu4s3FAuefBOoLy5xBSY	3	2025-11-05 14:23:14.981687+00	2025-10-29 14:23:14.572545+00	f
10	RXu88KHMeS0mALG75-B-RFMAN4WMmqAxE38tWRyID5k	3	2025-11-05 17:14:42.380451+00	2025-10-29 17:14:41.992059+00	f
11	0LjzJmjHaOqJNzQ0PBbnJxLonrsLWMUenTET6cDh9tI	1	2025-11-05 19:26:01.293383+00	2025-10-29 19:26:00.92403+00	f
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id, nome, email, hashed_password, empresa_id, perfil, is_active, data_criacao, xp, level, foto_perfil) FROM stdin;
2	Thiago	thiago@higiplas.com	$2b$12$9u35K1.UxpZ0YW590g/8UOJiWP0CID9udKruu0rY9oejSpepj7TTy	1	GESTOR	t	2025-07-07 05:38:13.211668+00	0	1	\N
3	Mirian	mirian@higiplas.com	$2b$12$xMtpfIvSX8qOBUwQbt/LB.HBCmtviiOl1dRCDHl8IrmyhT0aVVKNK	1	GESTOR	t	2025-07-07 05:39:26.204964+00	10	1	\N
4	Admin Higiplas	admin@gmail.com	$2b$12$OhTH2JzU6Nx39bCNE4w/O.nEFiMpz8.pP4IxJfDGCzeX.4CAShh9u	2	ADMIN	t	2025-08-13 01:07:27.705878+00	0	1	\N
5	Test User	test@example.com	$2b$12$61XWpWRfe/oydrSwh.xW8./UvskGLRU4crr9LYVbGUwNRGPGehB0G	1	OPERADOR	t	2025-08-13 01:11:40.017541+00	0	1	\N
6	Admin Higiplas	admin@higiplas.com	$2b$12$MUEtw/PzEdxcV4JuDInKWOAPfteb5p7hmNrmhnsFvapZySWSfws2K	1	ADMIN	t	2025-08-28 20:41:22.97537+00	0	1	\N
7	vendedor teste	vendedorteste@gmail.com	$2b$12$KZi7KJQwnLd9d3JyqjAIN..vPt2g14JLjOw1HGVkqgCxKv0sRta9W	1	vendedor	t	2025-11-07 00:10:52.915587+00	0	1	\N
8	Mirian	mirian.adm@higiplas.com	$2b$12$iDjKmiAwrD.eK70/Z.5Rx.ci1fmm5mlTCKpbt.UiNfHzoDBvPwj3e	1	ADMIN	t	2025-11-12 12:08:46.29419+00	0	1	\N
9	Eliomar Santos	eliomar@higiplas.com	$2b$12$8HKI/kwWeJucNroROz5hKexVQVybJS1soLgogkA6LfxqvIQ3jDMey	1	vendedor	t	2025-11-12 13:23:16.850713+00	0	1	\N
10	teste gestor	testegestor@gmail.com	$2b$12$pvSBRcTs3sD/1M4mP/s6ZONRJiUJIDltt5JuNPQ1hyfPR.YHzfGlq	1	GESTOR	t	2025-11-12 13:31:26.80804+00	0	1	\N
11	Renato 	renato@higiplas.com	$2b$12$CBSY9ZBlR9z0dAzGX4Tw1.1QDr7.a72PUTTRZps.xctigqMo41Vna	1	vendedor	t	2025-11-12 18:45:13.832303+00	0	1	\N
12	Thiago Marinho	adm@higiplas.com.br	$2b$12$NdJUFHIBmJ2zBtqu8DLsluFD3iAHqNPbRi67Ko.uBza7Cvh0YBB1q	1	ADMIN	t	2025-11-18 18:39:28.995333+00	0	1	\N
13	entregador	entregador@teste.com	$2b$12$KdiAk2M1/rogyGhwptbxbu1qHKQKdMDH0Gm32xwnWEGI.Apzz.yea	1	OPERADOR	t	2025-11-21 00:58:32.872998+00	0	1	\N
1	enzo almeida	enzo.alverde@gmail.com	$2b$12$0aC.2gYp64e6JzPb4w0DwugExRC6H3XoIwg78FG0HkaC6LyOdzsSi	1	ADMIN	t	2025-07-07 04:14:36.864182+00	10	1	\N
\.


--
-- Data for Name: vendas_historicas; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.vendas_historicas (id, ident_antigo, descricao, quantidade_vendida_total, custo_compra_total, valor_vendido_total, lucro_bruto_total, margem_lucro_percentual, produto_atual_id) FROM stdin;
7753	659	ACIDO MURIÁTICO BRASIL 1L	117	533.62	879.52	345.9	64.82	\N
7754	458	ÁCIDO MURIÁTICO COMBATE 1L	124	607.18	833.1	225.92	37.21	\N
7755	415	ACIDO MURIATICO LIMPA FACIL 1L	80	406.04	562.17	156.13	38.45	\N
7756	715	ACIDO MURIATICO NUTRILAR 1000ML	223	1162.1	1667.29	505.19	43.47	\N
7757	745	ACIDO MURIATICO RETIRO 1L	774	2770.92	6048.34	3277.42	118.28	\N
7758	414	ACIDO MURIATICO START 4X5L	6	135	189	54	40	\N
7759	920	AÇUCAR CRISTAL BLANCO 1KG	278	986.9	1779.94	793.04	80.36	\N
7760	230	AÇUCAR CRISTAL ITAJÁ 1KG	112	347.4	627	279.6	80.48	\N
7761	919	ADOÇANTE LIQ 100ML	66	245.34	436.14	190.8	77.77	\N
7762	231	ÁGUA SANITÁRIA  CLORITO 1L	2126	3319.11	5352.97	2033.86	61.28	\N
7763	248	ÁGUA SANITARIA CLORADA FC 1L	490	794.95	1123.88	328.93	41.38	\N
7764	666	ÁGUA SANITÁRIA DULAGO 1L	48	91.2	127.68	36.48	40	\N
7765	725	AGUA SANITARIA NAZARE 1L	12	21.6	30.24	8.64	40	\N
7766	3	AGUASSANI BB 5L	2909	40042.2	78490.11	38447.91	96.02	\N
7767	853	ALÇA DE FIXAÇÃO DO CHICOTE	1	0	50	50	0	\N
7768	251	ALCOOL GEL 65 ECON. TRAD.500ML	66	303.34	429.61	126.27	41.63	\N
7769	509	ALCOOL GEL CLEAN 70 500ML	20	180	252	72	40	\N
7770	419	ALCOOL GEL MEGA 70 INPM NEUTRO 5L	10	93.18	120.09	26.91	28.88	\N
7771	252	ALCOOL HIDRATADO ECONOMICO 70 INPM	12	72.48	101.52	29.04	40.07	\N
7772	491	ALCOOL LIQ. 70% 1L	341	2601.4	3706.69	1105.29	42.49	\N
7773	210	ALCOOL LIQ. START 70  1L	247	1821.8	2572.7	750.9	41.22	\N
7774	165	ALCOOL LIQUIDO 70% SAFRA 1L	163	1103.86	1615.22	511.36	46.32	\N
7775	420	ALCOOL LIQUIDO MEGA  1L	104	903.6	1060.24	156.64	17.34	\N
7776	499	ALCOOL LIQUIDO MEGA 70 INPM 5L	225	8696.87	13911.92	5215.05	59.96	\N
7777	660	ÁLCOOL SAFRA 5L	152	6329.8	8988.2	2658.4	42	\N
7778	5	ALTGEL BB 1 L	37	426.99	1006.45	579.46	135.71	\N
7779	211	ALUMI CROST BB 5L	131	7301.16	18111.07	10809.91	148.06	\N
7780	572	ALVITEC PE BB 5KG	15	1420.9	3934.8	2513.9	176.92	\N
7781	392	AMACITEC PREMIUM PRIMAV BB5L	13	619.45	1361.88	742.43	119.85	\N
7782	823	AMACITEC PRIMAVERA  BB5L	13	400.14	1199.64	799.5	199.81	\N
7783	237	AMONIX BB 1L	2	11.78	0.02	-11.76	-99.83	\N
7784	480	APLICADOR DE CERA 35CM SEM CABO	3	153.48	214.88	61.4	40.01	\N
7785	857	AR. BLACK  AIR FR100G	2	64.6	96.9	32.3	50	\N
7786	856	ARES BAC 315 CEREJA E AVELÃ 5L	3	105	178.56	73.56	70.06	\N
7787	529	ARMAÇAO PARA MOP PO 40 CM	11	404.25	565.25	161	39.83	\N
7788	530	ARMAÇAO PARA MOP PO 60 CM	2	77	107.8	30.8	40	\N
7789	531	ARMAÇAO PARA MOP PO 80 CM	3	120.54	176.29	55.75	46.25	\N
7790	925	AROM GLADE AER REF ENERG FLORAL 269ML	2	78.98	110.58	31.6	40.01	\N
7791	926	AROM GLADE AER REF FLORAIS 269ML	4	157.96	221.16	63.2	40.01	\N
7792	924	AROM GLADE AER REF LAVANDA 269ML	3	118.47	165.87	47.4	40.01	\N
7793	642	AROM GLEDE ARE LEM. INFANC 269ML	23	677.35	866.3	188.95	27.9	\N
7794	815	AROMATIZADOR AUTOMATICO GLADE LAVANDA	2	0	159.56	159.56	0	\N
7795	830	AROMATIZADOR CHEIRO DE TALCO  360ML	238	2100.02	3496.02	1396	66.48	\N
7796	929	AROMATIZADOR GLADE AUTOM LEMBR INFANCIA	1	60.29	84.41	24.12	40.01	\N
7797	930	AROMATIZADOR GLADE AUTOM TOQUE MACIEZ	1	60.29	84.41	24.12	40.01	\N
7798	330	AROMATIZADOR LAVANDA  360ML	247	2403.43	3361.21	957.78	39.85	\N
7799	866	AROMATIZANTE AIR CLEAN PREMISSE 500ML	2	34	47.6	13.6	40	\N
7800	816	AROMATIZANTE BOM AR FRESHMATIC CAMP LAV	11	0	550.95	550.95	0	\N
7801	843	AROMATIZANTE DOCE CARINHO PREMISSE 500ML	4	10.66	156.8	146.14	1370.92	\N
7802	436	AROMATIZANTE FLOR DE ALGODÃO 360ML	79	752.36	1056.77	304.41	40.46	\N
7803	270	AROMATIZANTE GLADE LAVANDA VANILLA	45	401.25	694.57	293.32	73.1	\N
7804	608	AROMATIZANTE JD PEONIA 360ML	104	1062.88	1462.36	399.48	37.58	\N
7805	810	AROMATIZANTE PETALAS DE ROSAS 360 ML	20	0	271.6	271.6	0	\N
7806	938	AROMATIZANTE REFIL GLADE LEMBRANÇA INF . 269ML	2	0	82.46	82.46	0	\N
7807	432	AROMATIZANTE SENSE ALEGRIA 360 ML	21	203.7	285.18	81.48	40	\N
7808	437	AROMATIZANTE ULTRA FRESH ERVA DOCE 400ML	25	217.8	288.67	70.87	32.54	\N
7809	609	AROMATIZANTE ULTRA FRESH VINÓLIA 360ML	5	43.75	62.5	18.75	42.86	\N
7810	688	AVENTAL DE NAPA 1,20X70CM	17	314.5	469.9	155.4	49.41	\N
7811	679	AVENTAL DE PVC FORRADO 1,20 x 70cm	52	717	1010.8	293.8	40.98	\N
7812	166	BALDE ESPREMEDOR 20L C/ DIVIDSOR	3	767.55	1075.79	308.24	40.16	\N
7813	583	BALDE PLASTICO 15L LITROS	36	350.28	483.84	133.56	38.13	\N
7814	868	BALDE PLASTICO PRETO 12L LITROS	3	30.03	42.03	12	39.96	\N
7815	707	BALDE PLASTICO SUPERPRO 14L C/ ESPREMEDOR	7	171.01	290.71	119.7	70	\N
7816	554	BALDE RETRATIL 10L BRANCO C/ AZUL NOBRE	5	110.25	203.3	93.05	84.4	\N
7817	199	BALDE ZIG ZAG C/ ESPREMEDOR	10	349.45	482.44	132.99	38.06	\N
7818	610	BAYGON AÇÃO TOTAL C/ CHEIRO 12X395ML	42	439.02	615.22	176.2	40.13	\N
7819	858	BIOELITICO 96% - 1L FR1KG	35	532	798	266	50	\N
7820	139	BOMBONA 1L TRANSLUCIDA	456	853.48	2124.57	1271.09	148.93	\N
7821	168	BOMBONA PLASTICA 5 L	79	245.15	478.3	233.15	95.11	\N
7822	428	BOTA BORRACHA CANO CURTO BRANCA	2	66.95	107.17	40.22	60.07	\N
7823	668	BOTA DE PVC CANO MÉDIO	1	35	49	14	40	\N
7824	674	BOTA DE SEGURAÇA EM PVC AQUAFLEX CANO CURTO	1	38	53.2	15.2	40	\N
7825	540	BOTA VULCAFLEX 10VB48A C/ ELAS C/B 35	3	168	256	88	52.38	\N
7826	541	BOTA VULCAFLEX 10VB48A C/ ELAS C/B 36	1	56	60	4	7.14	\N
7827	145	CABO CHAPA DE AÇO 150CM ROSCA BETANIN	18	265.5	403.1	137.6	51.83	\N
7828	296	CABO DE ALUMINIO 22X1,40M (NOBRE)	410	4304.15	8210.69	3906.54	90.76	\N
7829	235	CABO DE ALUMINIO 22X1,40M C/ PONTEIRA (NOBRE)	36	489.14	941.72	452.58	92.53	\N
7830	446	CABO EM ACO 150CM C/ROSCA DIAM 2,5CM 1X12	3	37.41	52.38	14.97	40.02	\N
7831	218	CABO EM ALUMINIO 1,50 C/ ROSCA BETTANIN	17	359.74	506.48	146.74	40.79	\N
7832	582	CABO EXTENSÃO TELESCOPICA DE ALUMINIO 3M	2	79.2	158.4	79.2	100	\N
7833	776	CABO EXTENSÃO TELESCOPICA DE ALUMINIO 6M C/ PONTEI	5	945	1323	378	40	\N
7834	543	CABO EXTENSOR CHAPA  AÇO 3 M BETANNI	5	142.86	206.42	63.56	44.49	\N
7835	497	CABO EXTENSOR DE ALUMINIO 4,5MT C/ PONTEIRA PERFEC	1	101.95	152.6	50.65	49.68	\N
7836	232	CAFÉ BOM DIA  AVACO PCT 250G	170	747.5	1164.5	417	55.79	\N
7837	348	CAFÉ MARATA  250G	120	477.6	668.4	190.8	39.95	\N
7838	918	CAFÉ MELITTA EXTRA FORTE  250G	1026	14353.74	20093.74	5740	39.99	\N
7839	842	CAFÉ SANTA CLARA CLASSICO  250G	280	3295	4731	1436	43.58	\N
7840	67	CANECA DOSADORA 140 ML	16	57.23	191.76	134.53	235.07	\N
7841	192	CARPETEX BB 1L	3	31.37	70.48	39.11	124.65	\N
7842	239	CARPETEX TIRA MANCHAS BB 1L	1	13.58	35.68	22.1	162.8	\N
7843	577	CARRO BALDE 30L (C/ DIVISOR DE AGUA ESPREMEDOR)	2	362	845.8	483.8	133.65	\N
7844	500	CARRO FUNCIONAL PARA LIMPEZA PERFECT	3	1606.14	2297.01	690.87	43.01	\N
7845	895	CARTUCHO RC 203 VAP. ORG. GASES ACIDOS	4	55.6	83.4	27.8	50	\N
7846	2	CERA DE ALTO BRILHO / SUBLIME BB 5L	36	6147.19	14833.57	8686.38	141.31	\N
7847	6	CERACRIL BB 5 L	106	9889.92	24783.77	14893.85	150.6	\N
7848	538	CERACRIL PRETA BB5L	17	1613.53	4336.8	2723.27	168.78	\N
7849	790	CESTO 51X24 23L BRANCO TAMPA BASC BRALIMPIA	2	136.88	191.64	54.76	40.01	\N
7850	380	CESTO TELADO 10L	5	24.95	309.11	284.16	1138.92	\N
7851	812	CHOCOLATE CAIXA CUBO 145G CACAU SHOW	10	259.9	363.9	104	40.02	\N
7852	712	CJ ARMACAO ALUMINIO E MOP 40CM 1X6 BETTANIN	1	45.3	63.42	18.12	40	\N
7853	722	CLOR IN 10000 ACUAPURA	8	527.2	1230.88	703.68	133.47	\N
7854	455	CLORO ATIVO BB 20L	72	6551.04	17447.48	10896.44	166.33	\N
7855	871	COADOR DE CAFÉ DU BOM GRAN N3	4	31.56	63.12	31.56	100	\N
7856	152	COLETORA PLASTICA VERD 660L S/PEDAL C/ RODAS E ENG	1	1107	1550	443	40.02	\N
7857	112	CONJUNTO ESPREMEDOR MOPINHO	2	10.5	14.7	4.2	40	\N
7858	563	COPO DESC. COPOBRAS BRANCO 100X150ML	200	808	1103.5	295.5	36.57	\N
7859	750	COPO DESC. MARATA BRANCO 100X180ML	285	1470.6	2057.7	587.1	39.92	\N
7860	687	COPO DESC. MARATA TRANSP 150ML	1164	5466.39	7885.87	2419.48	44.26	\N
7861	367	COPO DESCARTAVEL COPOBRAS TRANSP 180ML	291	1651.39	1551.76	-99.63	-6.03	\N
7862	363	COPO DESCARTAVEL FC 150ML	350	1542.25	2037.25	495	32.1	\N
7863	233	COPO DESCARTÁVEL FC 180ML	1481	3968.97	6092.63	2123.66	53.51	\N
7864	253	COPO DESCARTAVEL FC 50ML	533	1181.55	1603.16	421.61	35.68	\N
7865	188	COPO DESCARTÁVEL MARATA BRANCO 100X50 ML	775	2493	3118.5	625.5	25.09	\N
7866	423	COPO DESCARTAVEL MARATA TRANS. 180ML	935	4385.3	5934.8	1549.5	35.33	\N
7867	661	COPO DESCARTÁVEL TRANSP. KEROCOPO 180ML	55	304.3	352.7	48.4	15.91	\N
7868	880	COPO DESCATAVEL TOTALPLAST  50ML	188	374.12	524.52	150.4	40.2	\N
7869	422	COPO DESCATAVEL UTRA  50ML	211	443.3	627.46	184.16	41.54	\N
7870	792	COPO DESCATAVEL UTRA 150ML	1675	6616.25	10594.5	3978.25	60.13	\N
7871	586	COPO DESCATAVEL UTRA 180ML	1034	5341.83	7420.73	2078.9	38.92	\N
7872	699	COPO KEROCOPO 100X180	30	107.7	177.65	69.95	64.95	\N
7873	195	CREMOLINE BB 5L	4	80.14	203.87	123.73	154.41	\N
7874	175	CREOLINA 1L	1	13.75	17.88	4.13	30.04	\N
7875	7	DESINCROST BB 1 L	10	106.2	901.24	795.04	748.63	\N
7876	8	DESINCROST BB 5	6472	384194.66	903184.47	518989.82	135.09	\N
7877	788	DESINCROST GEL  BB 1L	10	110	216	106	96.36	\N
7878	787	DESINCROST GEL  BB 5	125	5405.35	11492.33	6086.98	112.61	\N
7879	729	DESINF. AZULIM MARINER 1L	20	91.6	177	85.4	93.23	\N
7880	730	DESINF. AZULIM WAVE 1L	15	68.7	132.75	64.05	93.23	\N
7881	44	DESINFETANTE SANIFLOR BREEZE BB 5L	192	5138.23	12008.65	6870.43	133.71	\N
7882	46	DESINFETANTE SANIFLOR CAMPESTRE BB 5L	216	5681.35	12787.72	7106.38	125.08	\N
7883	47	DESINFETANTE SANIFLOR CAPIM LIMÃO BB 5L	84	2294.13	5267.85	2973.72	129.62	\N
7884	900	DESINFETANTE SANIFLOR EUCALIPTO BB 5L	15	572.85	1363.39	790.54	138	\N
7885	718	DESINFETANTE SANIFLOR FRUCTYS BB 5L	27	901.8	2218.26	1316.46	145.98	\N
7886	219	DESINFETANTE SANIFLOR LAVANDA  BB 5L	80	1874.85	4099.35	2224.5	118.65	\N
7887	45	DESINFETANTE SANIFLOR LIRIOS DO CAMPO BB 5L	206	5316.61	12323.97	7007.35	131.8	\N
7888	138	DESINFETANTE SANIFLOR MAX FRESH LEMON BB5L	1663	63766.66	130870.37	67103.71	105.23	\N
7889	48	DESINFETANTE SANIFLOR MAX SOFT BB 5L	1554	58750.44	138204.4	79453.96	135.24	\N
7890	214	DESINFETANTE SANIFLOR PLUS CAPIM LIMAO BB5L	5	705.93	1753.18	1047.25	148.35	\N
7891	340	DESINFETANTE SANIFLOR PLUS SOFT 1L	4	107.32	269.72	162.4	151.32	\N
7892	50	DESINFETANTE SANIFLOR PLUS SOFT BB 5L	181	27980.01	65625.48	37645.47	134.54	\N
7893	174	DESINFETANTE SANIFLOR SOFT BB 5L	108	2732.07	6595.96	3863.89	141.43	\N
7894	43	DETERGENTE CLORADO BB 5L	11251	430295.32	1104738.09	674442.77	156.74	\N
7895	411	DETERGENTE CLORADO FR 1L	1	8.63	22.68	14.05	162.8	\N
7896	801	DETERGENTE CLORADO FR 2L TD	5	94	240.65	146.65	156.01	\N
7897	229	DETERGENTE DE USO GERAL NEUTRO GAROTO 24X500ML	253	301.76	458.26	156.5	51.86	\N
7898	854	DETERGENTE ECONOMICO COCO 12X500ML	2	0	5.12	5.12	0	\N
7899	587	DETERGENTE ECONOMICO NEUTRO 500ML	890	1606.18	2237.76	631.58	39.32	\N
7900	669	DETERGENTE LIMPOL LIMAO 24X500ML	46	84.18	117.76	33.58	39.89	\N
7901	671	DETERGENTE LIMPOL NEUTRO 24X500ML	65	118.95	166.4	47.45	39.89	\N
7902	249	DETERGENTE NEUTRO FC 500ML	735	1259.66	1776.51	516.85	41.03	\N
7903	115	DETERGENTE NUTRILAR LIMÃO 500ML	346	410.88	597.56	186.68	45.43	\N
7904	657	DETERGENTE OI 500ML	252	361.11	535.51	174.4	48.3	\N
7905	844	DETERGENTE OI 5L	9	153	229.5	76.5	50	\N
7906	670	DETERGENTE YPE MAÇA 24X500ML	20	36.6	51.2	14.6	39.89	\N
7907	767	DIABO VERDE 1L	6	240.3	371.7	131.4	54.68	\N
7908	769	DIFUSOR DE AROMAS ONLY 12X25ML DUBAI	2	0	117.6	117.6	0	\N
7909	748	DIFUSOR DE AROMAS ONLY 12X25ML MALDIVAS	11	462	646.8	184.8	40	\N
7910	770	DIFUSOR DE AROMAS PREMISSE LAVANDA 350ML	4	72	108	36	50	\N
7911	337	DIL PROMAX BUT 4P 16L PXB4N16S PROMX BUTTON 4 PR	2	994	1988	994	100	\N
7912	76	DILUIDOR ACCUDOSE	2	900	1621	721	80.11	\N
7913	365	DILUIDOR DOSADOR TOTALMIX  TRON	38	6406.35	13829.5	7423.15	115.87	\N
7914	316	DISCO LIMPADOR 410MM VERDE (NOBRE)	92	1610.65	3271.7	1661.05	103.13	\N
7915	645	DISCO LIMPADOR VERDE ABRASIVO 410MM	76	1390.92	2819.28	1428.36	102.69	\N
7916	575	DISCO LUSTRADOR BRANCO 410MM	2	30.7	61.4	30.7	100	\N
7917	312	DISCO REMOVEDOR 410MM PRETO ABRASIVO	17	312.82	562.94	250.12	79.96	\N
7918	140	DISCO RESTAURADOR VERMELHO ABRASIVO 410	7	119	224.2	105.2	88.4	\N
7919	193	DISP. SABONETEIRA PLESTIN 600ML	45	1196.2	2365.92	1169.72	97.79	\N
7920	553	DISPENSER AUTOCORTANTE P/ TOALHA BOBINA BRANCO	7	1518.3	2429.28	910.98	60	\N
7921	306	DISPENSER COPO AGUA  BRANCO	7	351.31	502.84	151.53	43.13	\N
7922	338	DISPENSER COPO DE CAFÉ 50ML	3	103.9	145.26	41.36	39.81	\N
7923	515	DISPENSER DE PAPEL HIGIÊNICO 300MTS PREMISSE	10	314	460.53	146.53	46.67	\N
7924	514	DISPENSER DE PAPEL TOALHA PREMISSE	3	90	126	36	40	\N
7925	285	DISPENSER P/ HIG.ROLÃO 300/500M (NOBRE)	94	1745.48	3631.36	1885.88	108.04	\N
7926	88	DISPENSER P/ SABONETE LIQUIDO PARA REFIL	30	457.2	1140.65	683.45	149.49	\N
7927	552	DISPENSER P/ SACO PLAS. ABSORV. FEMININO	21	222.6	231.2	8.6	3.86	\N
7928	286	DISPENSER P/ TOALHA  (NOBRE)	98	1818.72	3726.48	1907.76	104.9	\N
7929	146	DISPENSER P/PAPEL HIGIENICO ROLAO 300/500M - BRANC	2	51	90.9	39.9	78.24	\N
7930	320	DISPENSER PAPEL HIGIENICO 300/500 BETTANIN	5	139.5	195.3	55.8	40	\N
7931	875	DISPENSER PAPEL HIGIENICO INTERF.	2	66	92.4	26.4	40	\N
7932	321	DISPENSER PAPEL TOALHA INTERFOLHADO BETTANIN	8	223.2	330.4	107.2	48.03	\N
7933	558	DISPENSER PARA PROTETOR DE ASSENTO	1	24.5	34.3	9.8	40	\N
7934	93	DISPENSER TOALHEIRO	2	36.36	80	43.64	120.02	\N
7935	664	DOSADOR PROMIX ML 08424	1	2200	2200	0	0	\N
7936	336	DOSADOR UNIKIT DETERGENTE	2	994.94	1989.88	994.94	100	\N
7937	335	DOSADOR UNIKIT SECANTE	2	994.94	1989.88	994.94	100	\N
7938	74	DURACRIL BB 5L	1	91.75	230	138.25	150.68	\N
7939	863	ESCADA MOR ALUMINIO 5D RESID 5103	1	149.9	224.85	74.95	50	\N
7940	732	ESCOVA PLAST MULTIUSO OVAL 1X36	23	97.06	186.41	89.35	92.06	\N
7941	733	ESCOVA PLAST MULTIUSO PRO 1X12	5	24.4	41.5	17.1	70.08	\N
7942	976	ESCOVA SANITARIA C SUPORTE	8	60	84	24	40	\N
7943	585	ESCOVA SANITARIA C SUPORTE  BETTANIN	38	488.86	715.9	227.04	46.44	\N
7944	169	ESCOVÃO MULTIUSO BRILHUS	33	90.9	166.58	75.68	83.26	\N
7945	975	ESCOVÃO MULTIUSO DE MADEIRA	1	2.5	3.5	1	40	\N
7946	921	ESCOVÃO MULTIUSO PERFECT	12	23.88	47.76	23.88	100	\N
7947	814	ESPANADOR	2	0	53.96	53.96	0	\N
7948	839	ESPANADOR ELESTROSTATICO AZUL BRALIMPIA	1	22.33	31.26	8.93	39.99	\N
7949	66	ESPONJA AZUL NÃO RISCA 3M	17	63.58	56.2	-7.38	-11.61	\N
7950	102	ESPONJA DUPLA FACE	2908	1380.36	2006.62	626.26	45.37	\N
7951	591	ESPONJA DUPLA FACE LIMPONA	1219	650.18	909.25	259.07	39.85	\N
7952	791	ESPONJA MULTIUSO ECONOMICA	188	112.8	150.4	37.6	33.33	\N
7953	65	ESPONJA SANITARIA ROSA 3M	14	15.12	30.24	15.12	100	\N
7954	73	ESPONJA SCOTH BRITE ULTRA	6	23.94	34.5	10.56	44.11	\N
7955	663	ETIQUETAS PARA FRASCO	50	47.5	62.5	15	31.58	\N
7956	817	EVITA MOFO INSPIRA 180G LAVANDA	18	112.9	248.46	135.56	120.07	\N
7957	927	EVITA MOFO SECAR 180G BABY	2	11.98	19.58	7.6	63.44	\N
7958	928	EVITA MOFO SECAR 80G ORIGINAL	9	53.91	89.23	35.32	65.52	\N
7959	883	FERVEDOR PANELUX ANT N 14	1	41.35	57.89	16.54	40	\N
7960	303	FIBRA  P/ LIMPEZA GERAL (NOBRE)	410	436.8	914.41	477.61	109.34	\N
7961	704	FIBRA DE LIMPEZA GERAL BETTANIN	314	426.95	730.47	303.52	71.09	\N
7962	63	FIBRA DE LIMPEZA LEVE BETTANIN	320	331.8	599.3	267.5	80.62	\N
7963	103	FIBRA DE LIMPEZA PESADA BETTANIN	2853.79	4959.93	8224.58	3264.65	65.82	\N
7964	298	FIBRA LIMPEZA LEVE (NOBRE)	253	264.35	368.31	103.96	39.33	\N
7965	299	FIBRA LIMPEZA PESADA (NOBRE)	263	332.77	585.57	252.8	75.97	\N
7966	590	FIBRA LIMPEZA PESADA SLIM 101X225MM C/10	20	34	55.8	21.8	64.12	\N
7967	576	FIBRA NOBRAÇO	135	275	392.8	117.8	42.84	\N
7968	677	FIBRA P/ LIMPEZA 1X20X10 ULTRA PESADA	316	591.8	1153.6	561.8	94.93	\N
7969	885	FIBRA P/ LIMPEZA BETTAÇO 1X20X10	20	28.6	59.8	31.2	109.09	\N
7970	369	FIBRA PARA LIMPEZA LEVE AZUL EMB C/3	21	48.89	56.58	7.69	15.73	\N
7971	890	FITA ZEBRADA 0,70X200M	1	10.5	15.75	5.25	50	\N
7972	206	FLANELA  LARANJA 28X48	408	663.2	990.89	327.69	49.41	\N
7973	451	FLANELA 100% ALGODÃO 40X60 BRANCA	711	931.68	2073.02	1141.34	122.5	\N
7974	261	FLANELA CRISTAL M 38X58	900	1451.23	2050.26	599.03	41.28	\N
7975	644	FLANELA CRISTAL M 40X60	386	753.74	1043.46	289.72	38.44	\N
7976	104	FLANELA LARANJA 40X60CM	546	759.81	1148	388.19	51.09	\N
7977	354	FLANELA VERMELHA 38X58	103	107.45	163.39	55.94	52.06	\N
7978	69	FRASCO 500 ML CRISTAL	151	304.2	685.25	381.05	125.26	\N
7979	68	GATILHO PULVERIZADOR	436	982.8	2259.5	1276.7	129.91	\N
7980	503	GATILHO PULVERIZADOR AMARELO TRIGGER 28/410	20	50	131.4	81.4	162.8	\N
7981	504	GATILHO PULVERIZADOR AZUL TRIGGER 28/410	20	50	131.4	81.4	162.8	\N
7982	278	GEL ANTISSEPTICO BOLSA 500ML	311	3055.54	6738.25	3682.71	120.53	\N
7983	512	GEL ANTISSEPTICO FR 500ML	126	1047.52	2414.28	1366.76	130.48	\N
7984	11	GEL SANITIZANTE 800 ML	292	3355.92	8076.19	4720.27	140.66	\N
7985	9	GEL SANITIZANTE BB 1L PET	711	9611.63	18555.28	8943.65	93.05	\N
7986	10	GEL SANITIZANTE BB 5L	2055	91780.36	211660.86	119880.5	130.62	\N
7987	789	GUARDA SOL FASHION MOR	2	99.8	139.72	39.92	40	\N
7988	807	GUARDANAPEIRA BRANCA PREMISSE	2	34.94	48.92	13.98	40.01	\N
7989	370	GUARDANAPO DE PAPEL 22X20CM SCALA	48	40.56	107.26	66.7	164.45	\N
7990	366	GUARDANAPO KITCHEN 22X24	36	59.4	70.2	10.8	18.18	\N
7991	245	GUARDANAPO NAPS 22X23 EMB.COM 72 UN	298	376.86	531.42	154.56	41.01	\N
7992	339	GUARDANAPO SANTEPEL 22X24	79	95.59	138.55	42.96	44.94	\N
7993	201	GUARDANAPOS ESPECIAL 20X18 48X50 VIP	126	98.22	146.38	48.16	49.03	\N
7994	859	HC CANOA  FR 250G	212	8150	12180	4030	49.45	\N
7995	820	HC LAVANDA AZUL  FR 250G	206.25	4869.44	7380	2510.56	51.56	\N
7996	362	HC LUXURIA  250G	347.5	3620.61	5198.85	1578.24	43.59	\N
7997	819	HC PINDORAMA   250G	21.75	1957.5	1751.25	-206.25	-10.54	\N
7998	923	HIGISEC BB 5L	1	46.96	120	73.04	155.54	\N
7999	522	HOPT. NEUTRO PLUS BB5L	2	109.68	280.78	171.1	156	\N
8000	848	HOSP NEUTRO PLUS BB 5L	18	1080	2070	990	91.67	\N
8001	204	INSET. SBP MULT REGULAR 273ML	12	89.88	37.8	-52.08	-57.94	\N
8002	519	INSETICIDA 380ML AEROSOL	92	860.2	1204.01	343.81	39.97	\N
8003	164	LÃ DE AÇO	6	4.64	11.8	7.16	154.31	\N
8004	313	LÃ DE AÇO ASSOLAN	396.8	508.65	801.5	292.85	57.57	\N
8005	408	LAPZYME BB1L	1	56.59	144.87	88.28	156	\N
8006	13	LAVESSOL ORANGE BB 1L REND 300	2	21.3	80	58.7	275.59	\N
8007	12	LAVESSOL ORANGE BB 5L	326	20128.55	53560.78	33432.23	166.09	\N
8008	634	LAVESSOL ORANGE INCOLOR BB5L	24	2018.88	4877.52	2858.64	141.6	\N
8009	391	LAVPRO BB 5L	46	3072.1	7201.48	4129.38	134.42	\N
8010	781	LAVPRO DX BB20L	1	230.82	603.01	372.19	161.25	\N
8011	349	LEITE NINHO 400 G	3	37.17	52.05	14.88	40.03	\N
8012	83	LENCOL HOSPITALAR 0,70X50m	54	613.35	934.15	320.8	52.3	\N
8013	667	LIMPA ALUMINIO DO LAGO 500ML	58	96.86	135.72	38.86	40.12	\N
8014	250	LIMPA ALUMINIO ECONÔMICO 500ML	471	812.6	1135.73	323.13	39.76	\N
8015	933	LIMPA ESTOFAMENTOS 500ML	2	52.5	73.5	21	40	\N
8016	220	LIMPA PORCELANATO  BB 1L	1	8.85	22.09	13.24	149.6	\N
8017	221	LIMPA PORCELANATO BB5L	225	10041.43	24744.85	14703.42	146.43	\N
8018	143	LIMPA TUDO COM CABO	1	0	39	39	0	\N
8019	332	LIMPADOR COM BRILHO BB 1L	12	114.88	300.41	185.53	161.5	\N
8020	841	LIMPADOR COM BRILHO BB 5L	1	0	133	133	0	\N
8021	17	LIMPAX  BB5L DETERGENTE DE LOUÇA UTRA CONCENTRADO	5162	106290.33	343270.81	236980.48	222.96	\N
8022	518	LIMPAX DX BB5L	5346	192022.71	417236.35	225213.64	117.28	\N
8023	743	LIXEIRA 100L  BRANCA C/ PEDAL PERFECT	4	1097.8	1450.2	352.4	32.1	\N
8024	805	LIXEIRA C/ PEDAL 12L BRANCA	4	180	252	72	40	\N
8025	650	LIXEIRA C/ PEDAL 50L BRANCA	8	1170.4	1576.24	405.84	34.68	\N
8026	782	LIXEIRA C/ PEDAL 50L MARROM PERFECT	1	0	212.5	212.5	0	\N
8027	861	LIXEIRA INOX C/ PEDAL E BALDE 5L BRINOX	4	513.6	719.04	205.44	40	\N
8028	860	LIXEIRA PLASTICA 50L BASCULANTE	1	0	178.5	178.5	0	\N
8029	779	LIXEIRA PLASTICA C PEDAL 120L AMARELA NOBRE	1	310	434	124	40	\N
8030	777	LIXEIRA PLASTICA C PEDAL 120L AZUL NOBRE	1	310	434	124	40	\N
8031	778	LIXEIRA PLASTICA C PEDAL 120L VERDE NOBRE	1	310	434	124	40	\N
8032	780	LIXEIRA PLASTICA C PEDAL 120L VERMELHA NOBRE	1	310	434	124	40	\N
8033	738	LIXEIRA PLASTICA C/ PEDAL 13,5L	5	170.54	238.85	68.31	40.06	\N
8034	322	LIXEIRA PLASTICA COM PEDAL 30L BRANCA	5	613.18	818.16	204.98	33.43	\N
8035	640	LIXEIRA SELETIVA 50L MARROM	1	90.16	212.5	122.34	135.69	\N
8036	639	LIXEIRA SELETIVA 50L VERMELHA	1	133	212.5	79.5	59.77	\N
8037	333	LOUÇA MAQ BB5L	69	3901.29	9189.81	5288.52	135.56	\N
8038	318	LUMINA BB 5L	4	312.8	790.75	477.95	152.8	\N
8039	723	LUSTAR MOVEIS PEROBA 200ML	4	23.96	33.6	9.64	40.23	\N
8040	864	LUSTRA MOVEIS  200ML	15	98.85	138.19	39.34	39.8	\N
8041	209	LUSTRA MOVEIS NOBRE 200ML	44	225.77	314.24	88.47	39.19	\N
8042	865	LUVA BICOLOR NEOLATEX SLIM G	7	52.5	73.5	21	40	\N
8043	292	LUVA BORRACHA LATEX AMARELA G (NOBRE)	441	1250.55	2448.98	1198.43	95.83	\N
8044	291	LUVA BORRACHA LATEX AMARELA M (NOBRE)	477	1445.33	2842.79	1397.46	96.69	\N
8045	290	LUVA BORRACHA LATEX AMARELA P (NOBRE)	90	246.38	427.71	181.33	73.6	\N
8046	440	LUVA DE PROCEDIMENTO LATEX TAM G	1	19	26.6	7.6	40	\N
8047	246	LUVA DE PROCEDIMENTO LATEX TAM M	201	36.18	76.6	40.42	111.72	\N
8048	724	LUVA DE RASPA CANO 7CM CURTO	1	18.87	26.42	7.55	40.01	\N
8049	293	LUVA LATEX COM PÓ C/100UN. (NOBRE)	10	145.6	216.24	70.64	48.52	\N
8050	105	LUVA LATEX MULTIUSO G LAGROTTA	172	473.01	673.02	200.01	42.28	\N
8051	694	LUVA LATEX PROCEDIMENTO N/ CIRURGICA C/PÓ M	1	31.12	40.46	9.34	30.01	\N
8052	711	LUVA LATEX RANHURADA TAM. M	14	189	264.6	75.6	40	\N
8053	483	LUVA MALHA C/PIGMENTOS 4 FIO TSUZUKI G	15	30	45	15	50	\N
8054	734	LUVA MULTIUSO LATEX QUALITY G	171	534.83	579.42	44.59	8.34	\N
8055	735	LUVA MULTIUSO LATEX QUALITY M	147	456.27	458.64	2.37	0.52	\N
8056	147	LUVA MULTIUSO LATEX QUALITY P	86	317.7	457.21	139.51	43.91	\N
8057	798	LUVA NITRILICA  CANO LONGO SLIM G	28	366.52	507.78	141.26	38.54	\N
8058	799	LUVA NITRILICA  CANO LONGO SLIM M	29	0	540.87	540.87	0	\N
8059	835	LUVA NITRILICA PRETA  SEM PÓ CX 10X/100UN.G	340	5440.4	11873.4	6433	118.24	\N
8060	832	LUVA NITRILICA PRETA  SEM PÓ CX 10X/100UN.M	80	1590.05	2456.8	866.75	54.51	\N
8061	892	LUVA NITRILICA PRETA  SEM PÓ TALGE  CX 10X/100UN.G	20	560	630	70	12.5	\N
8062	495	LUVA NITRILICA VERDE G	116	822.44	1187.04	364.6	44.33	\N
8063	496	LUVA NITRILICA VERDE M	197	1460.37	2054.31	593.94	40.67	\N
8064	627	LUVA NITRILICA VERDE P	159	1208.49	1716.53	508.04	42.04	\N
8065	100	LUVA PLASTICA PACOTE COM 100	283	243.1	501.1	258	106.13	\N
8066	800	LUVA PVC 70cm P/ ESGOTO	3	148.5	222.75	74.25	50	\N
8067	247	LUVA TALGE DE PROCEDIMENTO VINIL COM TALCO TAM P	202	59	89.8	30.8	52.2	\N
8068	737	LUVA TPE DESCARTAVEL CLEAR 1X100X6 M	7	57.68	98.07	40.39	70.02	\N
8069	163	LUVA TRICOTADA PIGMENTADA PRETA	80	340.6	479.84	139.24	40.88	\N
8070	485	LUVA VAQUETA DORSO RASPA MISTA GB/ VALCAN G	15	120	191.25	71.25	59.38	\N
8071	477	LUVA VINIL C/PÓ PROTEÇÃO AGENTES C/100UN.G	50	900	1260	360	40	\N
8072	478	LUVA VINIL C/PÓ PROTEÇÃO AGENTES C/100UN.M	50	900	1260	360	40	\N
8073	472	LUVA VINIL S/PÓ PROTEÇÃO AGENTES C/100UN.G (NOBRE)	65	919.3	1794.52	875.22	95.21	\N
8074	489	LUVA VINIL S/PÓ PROTEÇÃO AGENTES C/100UN.M	10	180	270	90	50	\N
8075	490	LUVA VINIL S/PÓ PROTEÇÃO AGENTES C/100UN.M	26	471.5	771.5	300	63.63	\N
8076	302	LUVA VINIL S/PÓ PROTEÇÃO AGENTES C/100UN.M (NOBRE)	80	921.08	1782.2	861.12	93.49	\N
8077	488	LUVA VINIL S/PÓ PROTEÇÃO AGENTES C/100UN.P	20	360	540	180	50	\N
8078	862	MANGUEIRA JARDIM FLEX 20M TRAM	1	99.9	149.85	49.95	50	\N
8079	912	MANUTENÇÃO ENCERADEIRA CLEANER 410	1	380	494	114	30	\N
8080	911	MANUTENÇÃO ENCERADEIRA CLEANER 500	1	260	338	78	30	\N
8081	766	MASCARA DE PROTEÇÃO S/ VALVULA PFF2 CA	200	786	605	-181	-23.03	\N
8082	289	MASCARA DESC. COM ELASTICO PCT C/50UND (NOBRE)	166	1410.6	1975.16	564.56	40.02	\N
8083	203	MASCARA DESCARTÁVEIS TNT COM 100UND	2	15.3	29.64	14.34	93.73	\N
8084	106	MASCARA DESCARTAVEL  AZUL	187	284.9	452.22	167.32	58.73	\N
8085	894	MASCARA RESPIRADOR CARBOGRAF CG 306	2	69.8	104.7	34.9	50	\N
8086	695	MASCARA TNT PRIPLA BRANCA CX C/ 50 UND	22	416.8	318.85	-97.95	-23.5	\N
8087	896	METABISSULFITO DE SÓDIO  - BB 20L	5	650	975	325	50	\N
8088	456	MEXEDOR DE CAFE PACOTE COM 500UND	1113	6712.24	9856.76	3144.52	46.85	\N
8089	774	MEXEDOR P CAFÉ CX C/ 20X500 ULTRA	640	4235.06	5926.4	1691.34	39.94	\N
8090	227	MEXEDOR PLAST P/ CAFÉ CRISTAL PC/100 UND	298	1041.86	1433.84	391.98	37.62	\N
8091	234	MOP-REFIL ZIGZAG MINI-MOP ALG. PAVIO MOPINHO 190GR	89	1043.68	1603.19	559.51	53.61	\N
8092	465	MOP ESFREGÃO GIRATORIO C/ BALDE ESPREMEDOR	17	328.95	731.82	402.87	122.47	\N
8093	464	MOP PÓ ACRILICO 40CMX15CM NOBRE	15	228.75	479.43	250.68	109.59	\N
8094	185	MOP PO SINTETICO 40 CM 9205 BETANIN - 1X12	2	73.92	102.8	28.88	39.07	\N
8095	852	MOP SPRAY INOX C/ RESERV. PERFECT	1	69.5	97.3	27.8	40	\N
8096	304	MOP UMIDO PONTA DOBRADA  340G (NOBRE) AZUL	124	1202.96	2267.14	1064.18	88.46	\N
8097	427	MOP UMIDO PONTA DOBRADA 390GR PONTA DOBRADA	1	18	25.2	7.2	40	\N
8098	450	MOP UMIDO REF 340G PONTA DOBRADA (NOBRE) BEGE	43	367.65	1009.42	641.77	174.56	\N
8099	449	MOP UMIDO VERMELHO REF 340G PONTA DOBRADA (NOBRE)	24	205.2	507.7	302.5	147.42	\N
8100	760	MOTOBOMBA PERIFERICA BP500 1/2CV INTECH	1	189.9	290.55	100.65	53	\N
8101	273	MULTI-USO ECON LARANJA 500ML	34	63.24	94.86	31.62	50	\N
8102	272	MULTI-USO ECON LIMÃO 500ML	34	63.24	94.86	31.62	50	\N
8103	271	MULTI-USO ECON TRADICIONAL 500ML	60	130.5	183.24	52.74	40.41	\N
8104	114	MULTIBAC BP 5L RENDE 1.000L	42	18829.75	42853.01	24023.26	127.58	\N
8105	62	MULTIBAC BP DOS 1L	215	19821.55	53505.62	33684.07	169.94	\N
8106	641	MULTIBAC PRATIK FR 500ML GATIL	5	84.1	214.29	130.19	154.8	\N
8107	27	MULTILUX BAC BREEZE BB 5L REND 750	132	18609.81	43796.22	25186.41	135.34	\N
8108	26	MULTILUX BAC BREEZE DOS 1L  REND  150L	134	3948.42	9764.72	5816.3	147.31	\N
8109	29	MULTILUX BAC SOFT BB 1L	29	855.42	2102.71	1247.29	145.81	\N
8110	28	MULTILUX BAC SOFT BB 5L REND 750	80	11777.06	26616.82	14839.76	126.01	\N
8111	307	MULTILUX ECO FRESH BB1L	6	116.6	385.8	269.2	230.87	\N
8112	425	MULTILUX POWER BB5L	45	4117.61	9250.2	5132.59	124.65	\N
8113	31	MULTILUX POWER DOS 1L REND 50 L	231	5365.27	12602.16	7236.89	134.88	\N
8114	703	MULTINOX FR 500ML GATILHO	6	135.54	349.87	214.33	158.13	\N
8115	612	MULTIUSO AZULIM FLORATA 12X500ML	17	44.4	62.12	17.72	39.91	\N
8116	613	MULTIUSO AZULIM LIMAO 12X500ML	13	36.23	55.75	19.52	53.88	\N
8117	611	MULTIUSO AZULIM ORIGINAL 12X500ML	18	46.81	66.73	19.92	42.56	\N
8118	381	MULTIUSO VEJA TRADICIONAL AZUL 500ML	59	233.11	369.49	136.38	58.5	\N
8119	527	NAFTALINA	155	253.25	337.37	84.12	33.22	\N
8120	651	NT 100 BB 20L	17	2847.25	6934.72	4087.47	143.56	\N
8121	481	NT 100 BB 5L	11	561.24	1126.23	564.99	100.67	\N
8122	846	OCULOS FENIX FUME DANNY	4	28	42	14	50	\N
8123	673	OCULOS PROTEÇÃO INCOLOR	15	84.75	129.23	44.48	52.48	\N
8124	510	ORGANIZADOR PARA 3 ACESSORIOS BRALIMPIA	5	259.44	294.6	35.16	13.55	\N
8125	274	OXIPRO FRESH LEMON BB1L	8	94.5	257.26	162.76	172.23	\N
8126	124	OXIPRO FRESH LEMON BB5L	2161	100118.7	229351.17	129232.47	129.08	\N
8127	802	OXIPRO FRESH LEMON FR 2L TD	2	45.34	116.08	70.74	156.02	\N
8128	523	OXIPRO NATURAL BB5L	239	11158.87	21473.95	10315.08	92.44	\N
8129	25	OXIPRO SOFT BB 5L	1802	83041.59	190853.88	107812.29	129.83	\N
8130	24	OXIPRO SOFT BB1L	9	89.73	194.27	104.54	116.51	\N
8131	197	PÁ COLETORA DE LIXO	32	955.25	1324.45	369.2	38.65	\N
8132	678	PA COLETORA PLASTICA ARTICULADA C/CABO 1.10M	5	165.5	250.6	85.1	51.42	\N
8133	142	PA COLETORA SUPERPRO BETTANIN C/ CABO	72	2054.85	3295.69	1240.84	60.39	\N
8134	148	PA COMUM COM CABO	10	129.8	181.72	51.92	40	\N
8135	785	PA COMUM S/ CABO	2	21	27.76	6.76	32.19	\N
8136	836	PÁ JEITOSA PLASTICO C/ CABO BETTANIN	5	59.65	89.5	29.85	50.04	\N
8137	615	PÁ PARA LIXO ATIS C/CABO LONGO	15	81.54	136.02	54.48	66.81	\N
8138	260	PANO ALVEJADO VILA DO RIO FLANELADO 45X65	125	362.5	509.44	146.94	40.54	\N
8139	107	PANO DE CHÃO  40X80 SANTA MARG.	518	1574.65	2226.82	652.17	41.42	\N
8140	259	PANO DE CHÃO ALVEJA DO FLANELADO 45X68 ESP. SANTO	1499	6405.49	9035.72	2630.23	41.06	\N
8141	424	PANO DE CHÃO BARCA 50X67	513	2323.1	3209.75	886.65	38.17	\N
8142	431	PANO DE CHÃO MICROFIBRA  50X60 PERFECT	164	552.41	774.79	222.38	40.26	\N
8143	850	PANO DE CHÃO MICROFIBRA 45X65 PANEW	4	31.92	51.08	19.16	60.03	\N
8144	457	PANO DE CHAO XADREZ 50X75	1747	4799.57	7366.7	2567.13	53.49	\N
8145	448	PANO DE MICROFIBRA 40X40 VERMELHO (NOBRE)	48	633.54	692.25	58.71	9.27	\N
8146	696	PANO DE PRATO	61	164.33	232.65	68.32	41.57	\N
8147	95	PANO MULTIUSO 27x240m C/ 600 PANOS BETTANIN	32	1181.39	1883.02	701.63	59.39	\N
8148	99	PANO MULTIUSO 28X300 C 600 PANOS AZUL	4	240	418.78	178.78	74.49	\N
8149	97	PANO MULTIUSO 28X300 C 600 PANOS LARANJA	2	120	200	80	66.67	\N
8150	98	PANO MULTIUSO 28X300 C 600 PANOS VERDE	23	2368	4117	1749	73.86	\N
8151	94	PANO MULTIUSO 30X50 C  5 PANOS	244	379.08	637.32	258.24	68.12	\N
8152	855	PANO MULTIUSO C/ 600 PANOS 40cm x240mt PERFECT	5	274.85	465.01	190.16	69.19	\N
8153	96	PANO MULTIUSO SLIM( C/60 PANOS 30cm x 30m x50cm)	52	757.02	1566.94	809.92	106.99	\N
8154	763	PANO MULTIUSO SLIM(C/ 500 PANOS 28cm x 200m verde)	16	701.4	981.96	280.56	40	\N
8155	325	PANO MULTIUSO SLIM(C/ 600 PANOS 28cm x 300m verde)	89	6497.88	9013.41	2515.53	38.71	\N
8156	771	PANO MULTIUSO SLIM(rolo c/ 28cm x 30m aprox 50cm)	3	32.28	64.56	32.28	100	\N
8157	550	PAPEL HIG. CAI CAI C/6000FLS 9,6X20,5 CM F. DUPLA	206	16165.2	32625.13	16459.93	101.82	\N
8158	903	PAPEL HIG. CAI CAI C/9000FLS 20X10 CM F. DUPLA	29	3017.74	5909.91	2892.17	95.84	\N
8159	77	PAPEL HIGIÊNICO ECONOMICO 8X300 EXTRA LUXO	45	1680	2486.14	806.14	47.98	\N
8160	324	PAPEL HIGIÊNICO HR PAPEIS 100% CELULOSE 8X300	611	26589.14	36907.68	10318.54	38.81	\N
8161	676	PAPEL HIGIENICO MAX PURE FD C/12 30MT	262	4186.81	5786.44	1599.63	38.21	\N
8162	513	PAPEL HIGIENICO MG BRANCO 300MTS	1952	78032.3	102766.49	24734.19	31.7	\N
8163	906	PAPEL HIGIENICO ROLÃO 8X300M (BEMEL)	30	1380	2070	690	50	\N
8164	280	PAPEL HIGIENICO ROLÃO 8X300M (NOBRE)	821	35730.99	53551.84	17820.85	49.88	\N
8165	281	PAPEL HIGIENICO ROLÃO 8X500M (NOBRE)	30	1610.1	2220.79	610.69	37.93	\N
8166	939	PAPEL HIGIENICO UNIQUE SOFT  ELEGANS 8X300 - MILI	60	3466.8	4716.6	1249.8	36.05	\N
8167	262	PAPEL TOALHA  MG KING SOFT 640 FOLHAS	17094	132280.84	184780.04	52499.2	39.69	\N
8168	907	PAPEL TOALHA BOBINA  6X200 100% CELULOSE BEMEL	5	332.5	498.75	166.25	50	\N
8169	82	PAPEL TOALHA BOBINA  HR  200X6 100% CELULOSE	419	27574	38403.3	10829.3	39.27	\N
8170	379	PAPEL TOALHA BOBINA ESSENCIAL EXTRA LUXO 200M C/6	2	116	162.4	46.4	40	\N
8171	378	PAPEL TOALHA BOBINA FIBRA MAXI MAIS 30G FDO C/6RLS	81	5636.4	7674.75	2038.35	36.16	\N
8172	710	PAPEL TOALHA BOBINA MG BRACO 150MTS	277	13221	18550.07	5329.07	40.31	\N
8173	915	PAPEL TOALHA INTERF C/2.400FLS.20X21,5 CM FLS DUPLA	8	560.96	1112.16	551.2	98.26	\N
8174	549	PAPEL TOALHA INTERF C/2000FLS.22,5X20,5CMFLS DUPLA	162	9366.35	18418	9051.65	96.64	\N
8175	954	PAPEL TOALHA INTERF UNIQUE BASIC SLIM 1000FLS MILI	100	1337	1878	541	40.46	\N
8176	796	PAPEL TOALHA INTERF.C/ 1000F 100% CELULOSE PREMIUM	1890	20656.8	28821.32	8164.52	39.52	\N
8177	301	PAPEL TOALHA INTERF.C/ 1000FLS 20X20 (NOBRE)	5761	67698.55	104611.29	36912.74	54.53	\N
8178	207	PAPEL TOALHA INTERFOLHADO HR 100%CEL 20X21	2957	33038.3	46296.77	13258.47	40.13	\N
8179	952	PAPEL TOALHA INTERFOLHADO MG 1.000FLS BRANCO	450	4050	5670	1620	40	\N
8180	559	PAPEL TOALHA MECHA BOBINA C/10X100MT 100% CELULOSE	8	438.4	492.26	53.86	12.29	\N
8181	560	PAPEL TOALHA MECHA BOBINA C/4X300MT 100% CELULOSE	29	1894.5	2652.3	757.8	40	\N
8182	872	PASTILHA  DE CLORO AQUAPOOL TABLETE 200G	20	279	300	21	7.53	\N
8183	635	PASTILHA ADESIVA PATO	90	288.6	504	215.4	74.64	\N
8184	831	PEDRA SANITÁRIA  AZULIM	200	226.72	681.98	455.26	200.8	\N
8185	520	PEDRA SANITÁRIA  NUTRILAR LIMÃO	46	78.2	170.2	92	117.65	\N
8186	150	PEDRA SANITARIA 25G BLOCO (SUPORTE E REFIL) MISTA	569	934.1	1514.22	580.12	62.1	\N
8187	435	PEDRA SANITÁRIA FLORAL	493	582.55	1109.12	526.57	90.39	\N
8188	434	PEDRA SANITÁRIA LAVANDA	434	582.54	1158.16	575.62	98.81	\N
8189	33	PERFUMAR BREEZE BB 1 L RENDE 10L	18	114.82	295.3	180.48	157.19	\N
8190	36	PERFUMAR BREEZE BB 5L RENDE 50L	268	9990.36	24601.33	14610.97	146.25	\N
8191	326	PERFUMAR CAPIM LIMAO BB1L	7	54.36	136.44	82.08	150.99	\N
8192	244	PERFUMAR CAPIM LIMAO BB5L	86	3117.04	7675.5	4558.46	146.24	\N
8193	144	PERFUMAR FRESH LEMON BB5L	182	6047.49	15457.18	9409.69	155.6	\N
8194	327	PERFUMAR FRESH LIMON BB1L	5	47.39	102.18	54.79	115.62	\N
8195	721	PERFUMAR FRUCTYS BB5L	30	1594.8	3203.5	1608.7	100.87	\N
8196	341	PERFUMAR LAVANDA 5L	83	3096.36	7754	4657.64	150.42	\N
8197	34	PERFUMAR LAVANDA BB 1 L RENDE 10L	1	6.19	15.85	9.66	156.06	\N
8198	37	PERFUMAR LIRIOS DO CAMPO BB 5 L REND 50  L	204	8091.33	19427.54	11336.21	140.1	\N
8199	328	PERFUMAR LIRIOS DO CAMPO BB1L	8	56.55	147.69	91.14	161.17	\N
8200	329	PERFUMAR SOFT BB 1L	7	42.55	116.69	74.14	174.24	\N
8201	35	PERFUMAR SOFT BB 5 L RENDE 50 L	205	6714.42	16916.2	10201.78	151.94	\N
8202	705	PISO PASTINHADO	5	76.1	106.55	30.45	40.01	\N
8203	706	PISO VINILICO MOEDA PRETO	6	756	1058.4	302.4	40	\N
8204	41	PISOFLOR SOFT BB 5L REND 100L	579	12086.17	25994.8	13908.63	115.08	\N
8205	42	PISONEUTRO PLUS SOFT DOS 1L REND 150L	8	109.86	242.64	132.78	120.86	\N
8206	409	PLACA SINALIZADORA PISO MOLHADO	3	101.7	180.47	78.77	77.45	\N
8207	38	PLASTILUX BB 1L REND 10L	17	160.85	450.88	290.03	180.31	\N
8208	154	PLASTILUX BB 5L	155	7206.19	17274.01	10067.82	139.71	\N
8209	85	PORTA PAPEL HIGIENICO EM ROLO BRANCO	1	18.18	47.9	29.72	163.48	\N
8210	413	PRAXI LIMPADOR CLORADO BB5L	3	62.22	258.27	196.05	315.09	\N
8211	300	PROTETOR DE PAPEL DESC. P/ ASSENTO C/40UN. GOEDERT	1399	11130.16	22203.76	11073.6	99.49	\N
8212	702	PROTETOR PROAUTO 200ML	10	137.9	213.5	75.6	54.82	\N
8213	845	PROTETOR SOLAR  NUTRIEX UV FPS 60 120ML	6	144	216	72	50	\N
8214	507	PULVERIZADOR 1LT SPRAY PERFECT	196	1382.36	2719.51	1337.15	96.73	\N
8215	849	PULVERIZADOR 500ML SPRAY GIRASSOL	8	53.44	90.88	37.44	70.06	\N
8216	508	PULVERIZADOR 500ML SPRAY PERFECT	890	4791.13	7553.48	2762.35	57.66	\N
8217	454	PULVERIZADOR DE PRESSAO 2 LITRO (BETANIN)	3	97.47	154.98	57.51	59	\N
8218	283	PULVERIZADOR PET TRANSPARENTE 500ML (NOBRE)	319	1018.59	1699.4	680.81	66.84	\N
8219	194	PUMP ESPUMA VA6001ES GIRASSOL	39	202.8	429	226.2	111.54	\N
8220	487	PUMP SPRAY VA 6003SP GIRASSOL	5	24.45	64.25	39.8	162.78	\N
8221	75	RACK ARAMADO 1 GARRAFA COM TRAVA	43	2513	5853.22	3340.22	132.92	\N
8222	532	REFIL 40 CM MOP PÓ ALGODÃO NATURAL	28	737.24	1072.65	335.41	45.5	\N
8223	535	REFIL 40 CM MOP PÓ SINTÉTICO	9	422.55	595.7	173.15	40.98	\N
8224	533	REFIL 60 CM MOP PÓ ALGODÃO NATURAL	15	504	718.9	214.9	42.64	\N
8225	536	REFIL 60 CM MOP PÓ SINTÉTICO	1	43.59	65.1	21.51	49.35	\N
8226	534	REFIL 80 CM MOP PÓ ALGODÃO NATURAL	15	621.3	887.9	266.6	42.91	\N
8227	537	REFIL 80 CM MOP PÓ SINTÉTICO	1	57.95	86.8	28.85	49.78	\N
8228	358	REFIL MOP PÓ  ALGODAO 40CMX15CM. BRANCO	4	65.7	119.92	54.22	82.53	\N
8229	359	REFIL MOP PÓ ALGODAO 60CMX15CM. BRACO	1	16.05	32.1	16.05	100	\N
8230	838	REFIL MOPINHO AZUL PONTA CORTADA BRALIMPIA	2	30.76	46.14	15.38	50	\N
8231	433	REFIL MOPINHO LOOP S/ CINTA ALG -HEXA	7	130	215.6	85.6	65.85	\N
8232	557	REFIL SAQUINHO PLAST. P/ ABSORVENTE CX C/24 UND	520	4411.7	8812.04	4400.34	99.74	\N
8233	902	REMOCALC BB 20L	4	1404.96	5003.38	3598.42	256.12	\N
8234	21	REMOCRIL BB 1L REND 10L	1	12.38	35	22.62	182.71	\N
8235	351	REMOCRIL INCOLOR BB 5L	15	963.94	2941.45	1977.51	205.15	\N
8236	1	REMOCRIL POWER BB 1L	14	450.95	1135.98	685.03	151.91	\N
8237	224	REMOCRIL POWER BB 5L	57	6273.93	14189.97	7916.04	126.17	\N
8238	18	REMOLUX BB 5 L REND  250L	12	489.76	1264.2	774.44	158.13	\N
8239	899	REMOQUAT BB 20L	34	6991.42	17476.68	10485.26	149.97	\N
8240	177	REMOVEDOR SEM CHEIRO / REMOCRIL POWER BB5L	10	411.39	1071.96	660.57	160.57	\N
8241	901	REMOX  BB 20L	4	832.59	2957.15	2124.56	255.17	\N
8242	215	REMOX  BB5L	2124	133748.42	279348.83	145600.41	108.86	\N
8243	20	REMOX BB 1L	2	25.78	70.72	44.94	174.32	\N
8244	122	RENOVADOR DE PNEUS FR 01 LITRO	9	135.55	355.31	219.76	162.13	\N
8245	874	REPELENTE ELÉTRICO LIQ. SBP	10	199	298.5	99.5	50	\N
8246	184	RESERVATÓRIO PARA SABONETE	8	55.2	64	8.8	15.94	\N
8247	516	RESERVATÓRIO PREMISSA 800ML	7	61.6	87.5	25.9	42.05	\N
8248	494	RODO COMBINADO 40CM S/ CABO P/ VIDRO NOBRE	8	222.32	346.78	124.46	55.98	\N
8249	479	RODO DE PLÁSTICO 40 CM	55	268.56	475.44	206.88	77.03	\N
8250	182	RODO DE PLÁSTICO 60 CM	60	605.5	967.75	362.25	59.83	\N
8251	294	RODO DUPLO ALUMINIO 35CM (NOBRE)	24	333.94	509.41	175.47	52.55	\N
8252	295	RODO DUPLO ALUMINIO 55CM (NOBRE)	87	1720.86	2758.32	1037.46	60.29	\N
8253	438	RODO DUPLO ALUMINIO 65CM (NOBRE)	3	108	134.4	26.4	24.44	\N
8254	141	RODO TWISTER SEM CABO BRALIMPIA	123	4810.62	6764.45	1953.83	40.61	\N
8255	108	SABÃO EM BARRA FC NEUTRO 10X5200G	35	184.8	262.81	78.01	42.21	\N
8256	442	SABÃO EM BARRA GAROTO LIMAO 200G	162	995.8	1547.6	551.8	55.41	\N
8257	441	SABÃO EM BARRA GUARANI 200G	5	10.47	47.58	37.11	354.44	\N
8258	453	SABAO EM BARRA NUTRILAR 200G	48	265.84	377.94	112.1	42.17	\N
8259	636	SABÃO EM BARRA YPÊ 10x5x180G	415	4895.95	6864.24	1968.29	40.2	\N
8260	443	SABAO EM PO ALA COCO 500G	151	399.46	540.02	140.56	35.19	\N
8261	942	SABAO EM PO ALA FLOR DE LIS 400G	115	340.4	517.5	177.1	52.03	\N
8262	429	SABAO EM PO ALA FLOR DE LIS SH 500G	2110	6997.4	9921.59	2924.19	41.79	\N
8263	383	SABAO EM PO ALA LAVANDA SH 500G	28	99.82	148.28	48.46	48.55	\N
8264	614	SABÃO EM PÓ ALA VERDE ERVA DOCE 500G	58	148.86	215.23	66.37	44.59	\N
8265	256	SABAO PO OMO MULTIAÇÃO SH 500G	57	255.18	298.8	43.62	17.09	\N
8266	51	SABONETE ANTISSEPTICO BB 5L	1094	35020.39	102773.37	67752.98	193.47	\N
8267	52	SABONETE DESENGRAXANTE MICRO ESFERA BB 5L	116	7966.82	16551.38	8584.56	107.75	\N
8268	183	SABONETE HIDR.  ANDIROBA BB 1L	17	142.12	388.99	246.87	173.71	\N
8269	475	SABONETE LIQUIDO DEOLINE ERVA DOCE 5L	69	1587	3348.81	1761.81	111.02	\N
8270	345	SABONETE PRAXI ESPUMA  ANDIROBA 5L	1315	38416.43	91611.46	53195.03	138.47	\N
8271	208	SABONETE SUAVITEX BAC LIQ. BOL 500ML	25	121.51	563.65	442.14	363.86	\N
8272	344	SABONETE SUAVITEX BAC SP BOL 500ML	412	4122.6	9843.74	5721.14	138.78	\N
8273	279	SABONETE SUAVITEX ESPUMA ANDIROBA BB 5L	18	609.15	1357.95	748.8	122.93	\N
8274	59	SABONETE SUAVITEX ESPUMA ANDIROBA REFIL 800ML	23	211.38	493.83	282.45	133.62	\N
8275	57	SABONETE SUAVITEX PEROLA ERVA DOCE BB 5L	11	206.68	499.31	292.63	141.59	\N
8276	60	SABONETE SUAVITEX PESSEGO BB 5 L	1281	35211.59	78047.58	42835.99	121.65	\N
8277	55	SABONETE SUAVITEX PRO ERVA DOCE BB 5 L	345	7764.88	18440.1	10675.22	137.48	\N
8278	56	SABONETE SUAVITEX PRO ERVA DOCE REF 800ML	18	113.22	102.78	-10.44	-9.22	\N
8279	54	SABONETE SUAVITEX PRO MILK BB 5L	632	19542.1	43549.24	24007.14	122.85	\N
8280	58	SABONETE SUAVITEX PRO PESSEGO REF 800 ML	13	76.92	171.9	94.98	123.48	\N
8281	749	SABONETE SUAVITEX PRO SP ANDIROBA BOL500	10	100.1	232.3	132.2	132.07	\N
8282	439	SABONETE SUAVITEX PRO SP E DOCE BB5L	17	352.41	1113.24	760.83	215.89	\N
8283	196	SABONETE SUAVITEX PRO SP ERVA DOCE 500ML	723	3486.06	15820.36	12334.3	353.82	\N
8284	739	SABONETE SUAVITEX PRO SP REF 500 C/ VALVULA	254	2903.22	7429.5	4526.28	155.91	\N
8285	505	SABONETE SUAVITEX PRO SP VIOLETA BB 5L	60	1583.8	4005.12	2421.32	152.88	\N
8286	467	SABONETEIRA 600ML BRANCA C/ RESERVATORIO ESPUMA	678	17313.02	34152.24	16839.22	97.26	\N
8287	466	SABONETEIRA 600ML REFIL/ BRANCA C/ VALVU. SPRAY	67	1449.61	2911.96	1462.35	100.88	\N
8288	86	SABONETEIRA BOX CRISTAL  1000 ML	12	280.92	670.61	389.69	138.72	\N
8289	87	SABONETEIRA BOX CRISTAL 400 ML	25	448.75	1069.6	620.85	138.35	\N
8290	120	SABONETEIRA BRANCA PARA ESPUMA	1	18	48	30	166.67	\N
8291	89	SABONETEIRA COM RESERVATORIO BRANCA INFINITY	3	55.95	165	109.05	194.91	\N
8292	153	SABONETEIRA DOSADORA ESPUMA 800ML	7	241.57	252	10.43	4.32	\N
8293	287	SABONETEIRA DOSADORA ESPUMA 800ML (NOBRE)	23	566	842.53	276.53	48.86	\N
8294	284	SABONETEIRA DOSADORA LIQ. 800ML (NOBRE)	75	1484.55	2902.11	1417.56	95.49	\N
8295	876	SABONETEIRA LIQ 800ML C/RES. FRENT INOX PRETA	17	1581	2344.04	763.04	48.26	\N
8296	870	SABONETEIRA VISIUM INOX POLIDO 500ML S/VISOR BIOVI	20	3201	4481.4	1280.4	40	\N
8297	806	SACO P/ LIXO 115X125X0,04 - PRETO 300L BETAPLASTIC	2	170	238	68	40	\N
8298	167	SACO P/ LIXO 115X125X0,05 - PRETO 300L BETAPLASTIC	70	6557.86	10242.2	3684.34	56.18	\N
8299	713	SACO P/ LIXO 115X125X0,08 - PRETO 300L BETAPLASTIC	4	624	873.6	249.6	40	\N
8300	189	SACO P/ LIXO 40X50X0,025 - PRETO 20LT BETA PLASTIC	320	2242.21	3352.36	1110.15	49.51	\N
8301	135	SACO P/ LIXO 55X55X0,25 - PRETO 40LT BETA PLASTIC	835	7785.95	11805.77	4019.82	51.63	\N
8302	134	SACO P/ LIXO 60X70X0,025 - PRETO 60LT BETA PLASTIC	1540	20532.9	31278.71	10745.81	52.33	\N
8303	953	SACO P/ LIXO 60X70X0,025 - TRANSP 60LT BETA PLASTIC	5	0	131.25	131.25	0	\N
8304	765	SACO P/ LIXO 75X100X05 - TRANSP 100LT BETA PLASTIC	87	5715.9	8573.85	2857.95	50	\N
8305	879	SACO P/ LIXO 75X100X05 - TRANSP 50LT BETA PLASTIC	10	175	285	110	62.86	\N
8306	236	SACO P/ LIXO 75X90X0,03 - PRETO 100LT BETA PLASTIC	1577	39961.4	59145.92	19184.52	48.01	\N
8307	136	SACO P/ LIXO 75X90X0,05 - PRETO 100LT BETAPLASTIC	262	11970.51	17941.33	5970.82	49.88	\N
8308	726	SACO P/ LIXO 75X90X0,08 - PRETO 100LT BETA PLASTIC	119	8151.5	12227.25	4075.75	50	\N
8309	399	SACO P/ LIXO 90X100X0,03 - PRETO 200LT BETAPLASTIC	338	11461	17257.25	5796.25	50.57	\N
8310	775	SACO P/ LIXO 90X100X0,04 - PRETO 200LT BETAPLASTIC	37	1813	2340.6	527.6	29.1	\N
8311	654	SACO P/ LIXO 90X100X0,05 - PRETO 200LT BETAPLASTIC	42	2561.6	3828.53	1266.93	49.46	\N
8312	394	SACO P/ LIXO 90X100X0,08 - PRETO 200LT BETAPLASTIC	687	61829.28	86556.78	24727.5	39.99	\N
8313	617	SACO P/ LIXO INFECTANTE 59X62X 30L LEVE	100	1586.8	2368.03	781.23	49.23	\N
8314	618	SACO P/ LIXO INFECTANTE 63X80 50L LEVE	108	2379	4004.75	1625.75	68.34	\N
8315	619	SACO P/ LIXO INFECTANTE 75X105 100L LEVE	138	4731.3	7286.44	2555.14	54.01	\N
8316	648	SACO P/ LIXO INFECTANTE 90X105 200L LEVE	10	580	858.8	278.8	48.07	\N
8317	662	SACO PARA LIXO 250L PRETO 110X120X6	2	178	249.2	71.2	40	\N
8318	638	SACO PARA LIXO AZUL 100L 75X90X0,04 BETA PLASTIC	59	1722	2260.2	538.2	31.25	\N
8319	869	SACO PARA LIXO AZUL 30L 55X55X0,025 BETA PLASTIC	11	133.1	186.34	53.24	40	\N
8320	397	SACO PARA LIXO AZUL 40L 55X55X0,025 BETA PLASTIC	191	2574.8	3547.4	972.6	37.77	\N
8321	548	SACO PARA LIXO AZUL 50LITROS 63X80 BETA PLASTIC	10	170	238	68	40	\N
8322	568	SACO PARA LIXO AZUL 60 LITROS 60x70 BETA PLASTIC	80	1477.64	2118.68	641.04	43.38	\N
8323	728	SACO PLASTICO AMOSTRA 16X25PCT C/500UND	4	542.72	814.4	271.68	50.06	\N
8324	764	SALVA PISO 1,00X25M SALVABRAS	4	910	1365	455	50	\N
8325	191	SANICLOR BB5L	1800	40170.24	99122.24	58952	146.76	\N
8326	910	SANICLOR DT BB 20L	107	18442.09	58850	40407.91	219.11	\N
8327	916	SANICLOR DT BB 5L	19	1010.99	2598.42	1587.43	157.02	\N
8328	22	SANILUX BB 1L REND 10L	15	135.32	289.66	154.34	114.06	\N
8329	23	SANILUX BB 5 L REND 50L	255	10251.55	24894.23	14642.68	142.83	\N
8330	317	SANIMAX BB1L	22	450.78	1136.78	686	152.18	\N
8331	680	SAPATO DE EVA MARLUVA	2	148	190	42	28.38	\N
8332	334	SEC MAQ PRO BB5L	65	3901.94	8911.01	5009.07	128.37	\N
8333	137	SELACRIL BB 5L	1	0	180	180	0	\N
8334	630	SELACRIL EX 1L	1	35.26	62.98	27.72	78.62	\N
8335	190	SELACRIL EX BB 5L	25	3108.58	6883.35	3774.77	121.43	\N
8336	123	SHAMPOO AUTO .CREMOLINE BALDE 20 L	1	80.14	210.59	130.46	162.79	\N
8337	834	SODA CÁUSTICA  24x450G NUTRILAR	1	13	18.2	5.2	40	\N
8338	629	SOVENTE  THINNER LATA 450 ML	2	17.8	53.9	36.1	202.81	\N
8339	222	SPRAY SANITIZANTE BOLSA 500ML	2764	24967.01	64070.5	39103.49	156.62	\N
8340	768	SUAVIT PRO SP ANDIROBA BOL500	136	979.12	919.36	-59.76	-6.1	\N
8341	170	SUBLIME BB 1L	16	505.88	1316.08	810.2	160.16	\N
8342	840	SUBLIME BB 5L	11	0	4168.74	4168.74	0	\N
8343	762	SUPORT P/ GARRAFÃO DE 5L	6	378	1022.58	644.58	170.52	\N
8344	818	SUPORT P/ SABÃO LIQUIDO E ESPONJA	1	0	27	27	0	\N
8345	297	SUPORTE LT S/CABO C/ PINÇA P/ FIBRA (NOBRE)	229	2205.01	4287.52	2082.51	94.44	\N
8346	355	SUPORTE P/ MOP PÓ 40CM	21	385.75	736.7	350.95	90.98	\N
8347	356	SUPORTE P/ MOP PÓ 60CM	19	378.1	756.2	378.1	100	\N
8348	357	SUPORTE P/ MOP PÓ 80CM	9	202.5	420	217.5	107.41	\N
8349	151	SUPORTE P/FIBRA ABRASIVA BT/LT REF:9516	28	501	704.15	203.15	40.55	\N
8350	217	SUPORTE PARA FIBRA  ABRASIVA/ LT	14	249.85	356.13	106.28	42.54	\N
8351	708	SUPORTE PLAST MANUAL P/BETTAÇO 1X10	3	19.35	32.91	13.56	70.08	\N
8352	305	SUPORTE PLAST.S/ CABO C/ PINÇA P/MOP UMIDO (NOBRE)	87	665.02	931.45	266.43	40.06	\N
8353	155	TAMPA  42 MM	75	37.5	112.5	75	200	\N
8354	157	TAMPA 28 MM PP LARANJA	25	12.5	31.25	18.75	150	\N
8355	156	TAMPA 28 MM PP VERDE	25	12.5	31.25	18.75	150	\N
8356	319	TAMPA PUMP PULL 28/410	14	10.64	27.3	16.66	156.58	\N
8357	390	TAMPA PUSH PULL 28/410	10	9.5	24.9	15.4	162.11	\N
8358	931	TAPETE N YORK 45X75 GRAFIITE	2	99.98	139.98	40	40.01	\N
8359	90	TELA ODORIZADORA PARA MICITORIO CITRICA	71	151.23	403.6	252.37	166.88	\N
8360	91	TELA ODORIZANTE COM PEDRA PARA MICTORIO	6	36.72	91.8	55.08	150	\N
8361	932	TELA P/ PIA 56X34	2	31.98	47.98	16	50.03	\N
8362	555	TELA PERFUMADA PARA MICTORIO MARINE AZUL	160	351.6	730.4	378.8	107.74	\N
8363	556	TELA PERFUMADA PARA MICTORIO TUTTI - FRUTTI	1140	2841.4	5668.4	2827	99.49	\N
8364	92	TOALHEIRO ALAVANCA	7	641.69	1508.21	866.52	135.04	\N
8365	847	TOUCA CAPUZ DE MALHA TIPO NINJA	3	22.5	33.75	11.25	50	\N
8366	893	TOUCA DESC. SANFONADA PCT C/ 100UND	40	0	613.6	613.6	0	\N
8367	288	TOUCA DESC. SANFONADA PCT C/ 100UND (NOBRE)	109	812.64	1564.73	752.09	92.55	\N
8368	959	TOUCA DESC. SANFONADA PCT C/ 100UND (VABENE)	200	1600	2800	1200	75	\N
8369	101	TOUCA TNT PCT COM 100 UNIDADES	54	236.7	306.3	69.6	29.4	\N
8370	752	TROCA DA CAIXA DE LIÇÃO COMPLETA	1	39.52	350	310.48	785.63	\N
8371	492	VALVULA PUMP A VZ 3ML/BB1LNAC 28/410	1	5.04	12.58	7.54	149.6	\N
8372	70	VALVULA PUMP A VZ 3ML/BB5L NAC	7	53.9	112.68	58.78	109.05	\N
8373	71	VALVULA PUMP ALTA VASÃO 1L	12	44.32	112.09	67.77	152.91	\N
8374	470	VALVULA PUMP SABONETE 28/410 T FRASCO 1L	26	43.06	112.89	69.83	162.17	\N
8375	746	VALVULA SABONETEIRA 0,8 SPRAY	3	19.17	38.34	19.17	100	\N
8376	546	VALVULA SABONETEIRA 600ML ESPUMA	87	276.66	553.32	276.66	100	\N
8377	205	VASCULHADOR FIBRAS DE NYLON	6	147	187.2	40.2	27.35	\N
8378	833	VASELINA SPRAY 300ML/160G ORBI	15	315	478.2	163.2	51.81	\N
8379	808	VASELINA TEKSPRAY	4	112.4	157.36	44.96	40	\N
8380	198	VASSOURA  LINDONA	255	2451.54	3569.18	1117.64	45.59	\N
8381	720	VASSOURA CASA E RUA PRO C/CABO 1X15	13	193.7	342.52	148.82	76.83	\N
8382	445	VASSOURA CERDA MACIA PLAST 60 CM	15	340	539.9	199.9	58.79	\N
8383	877	VASSOURA CERDA RIGIDA PLAST 60 CM	1	0	47.6	47.6	0	\N
8384	628	VASSOURA CERDAS MACIA SEM CABO	2	52.8	73.92	21.12	40	\N
8385	412	VASSOURA CONDOR V-35	42	419.58	587.58	168	40.04	\N
8386	111	VASSOURA DE PIAÇAVA N 5 IMPERIAL	191	1016.41	1646.86	630.45	62.03	\N
8387	459	VASSOURA ENCANTADA NYLON	195	1185.92	2255.41	1069.49	90.18	\N
8388	643	VASSOURA LIMPAMANIA  DONNA	14	84	150.61	66.61	79.3	\N
8389	258	VASSOURA LINDISSIMA  ATIS	23	184.27	261.34	77.07	41.82	\N
8390	731	VASSOURA MULTIUSO PLAST C/CABO	94	1100.5	1746.52	646.02	58.7	\N
8391	460	VASSOURA PIAÇAVA RAINHA MAX	261	1737.39	2433.48	696.09	40.07	\N
8392	159	VASSOURA SANITARIA NYLON C/SUPORTE	28	170.7	432.74	262.04	153.51	\N
8393	162	VASSOURÃO 60CM	15	322.2	441.21	119.01	36.94	\N
8394	761	VASSOURAS CERDAS MACIAS 60CM S/ CABO	7	167.3	253.67	86.37	51.63	\N
8395	685	VASSOURINHA PARA VASO SEM SUPORTE SANILUX	1	9.5	9.5	0	0	\N
8396	39	VIDROLUX BB 1L REND 5L	29	150.87	359.4	208.53	138.22	\N
8397	40	VIDROLUX BB 5L REND 25L	292	6330.55	15607.46	9276.91	146.54	\N
8398	822	AMACITEC PRIMAVERA BB 50L	8	2320	5746.37	3426.37	147.6884	\N
8399	797	AROMATIZANTE SECAR  ALGODÃO DO NILO 360ML	36	428.4	599.76	171.36	40	\N
8400	794	CABO EXTENSÃO TELESCOPICA DE AÇO 3M	2	0	158.4	158.4	0	\N
8401	851	CLOR MAQ BB5L	1	0	136	136	0	\N
8402	727	COLHER REFEIÇAO BRANCA 50 UND PARA FESTA	20	69	96.6	27.6	40	\N
8403	784	COPO DESCATAVEL UTRA 150ML	100	395	598	203	51.3924	\N
8404	714	DESINFETANTE SANIFLOR FRUCTYS BB 5L	19	638.78	1183	544.22	85.1968	\N
8405	716	DISCO REMOVEDOR 410MM VERDE ABRASIVO	1	18.06	36.12	18.06	100	\N
8406	793	ESCOVA LAVA CAR BOLA	2	81.14	196.5	115.36	142.174	\N
8407	825	FIBRA LIMPEZA  LEVE (NOBRE)	10	0	20.5	20.5	0	\N
8408	623	LAVPRO BB 20L	10	2374.7	5707.4	3332.7	140.3419	\N
8409	837	LAVPRO SOLV BB 5L	1	0	1	1	0	\N
8410	804	LIXEIRA 100L BRANCA C/ PEDAL PERFECT	5	1304.88	1826.83	521.95	39.9998	\N
8411	827	LOUÇA MAQ PRO BB5L	5	0	909.43	909.43	0	\N
8412	809	LUSTRA MOVEIS UAU 200ML	15	89.85	121.2	31.35	34.8915	\N
8413	741	LUVA MULTIUSO LATEX QUALITY G	12	41.4	55.8	14.4	34.7826	\N
8414	742	LUVA MULTIUSO LATEX QUALITY P	12	41.4	55.08	13.68	33.0435	\N
8415	740	MASCARA DE PROTEÇÃO S/ VALVULA PFF2 CA	40	157.2	220	62.8	39.9491	\N
8416	821	NEUTRAL BB 50L	3	1161.57	2787.75	1626.18	139.9985	\N
8417	418	PAPEL HIGIENICO BRANCO EXTRA LUXO 300M	30	1350	2058	708	52.4444	\N
8418	795	PAPEL HIGIÊNICO ECONOMICO 8X300 EXTRA LUXO	37	1480	2120.72	640.72	43.2919	\N
8419	566	PAPEL HIGIENICO MAX PURE FD C/12 30MT	110	1405.76	1934.16	528.4	37.5882	\N
8420	502	PAPEL HIGIENICO MG 100% CELULOSE 300MT	44	2112	3028.8	916.8	43.4091	\N
8421	410	PAPEL TOALHA 6X200 MTS CELULOSE LUXO	1	68	95.2	27.2	40	\N
8422	829	PAPEL TOALHA BOBINA  6X200 100% CELULOSE BEMEL	4	266	399	133	50	\N
8423	376	PAPEL TOALHA BOBINA MG 6X200 100% CELULOSE	39	2535	3811.5	1276.5	50.355	\N
8424	377	PAPEL TOALHA ELEGANCY 100% INTERFOLHADO 20X20	20	218	338	120	55.0459	\N
8425	389	PAPEL TOALHA INTERF.C/ 1000F 100% CELULOSE PREMIUM	1035	11355	15897	4542	40	\N
8426	709	PERFUMAR FRUCTYS BB 5L	37	1960.57	3735.67	1775.1	90.54	\N
8427	452	PULVERIZADOR DE COMPRESSÃO 1,250ML GUARANY	1	93.55	135.65	42.1	45.0027	\N
8428	681	REMOCALC BB5L	3	342.27	890.52	548.25	160.1806	\N
8429	826	SABAO EM BARRA NUTRILAR 200G	20	29.6	207.84	178.24	602.1622	\N
8430	506	SABONETE SUAVITEX LEITE HIDRAT BB 1L	1	14.08	37.84	23.76	168.75	\N
8431	772	SABONETEIRA 600ML BRANCA C/ RESERVATORIO LIQ	21	0	1137.78	1137.78	0	\N
8432	474	SANIMAX BB5L	3	452.59	772.49	319.9	70.6821	\N
8433	632	TELA PERFUMADA PARA MICTORIO MENTA	30	69	150	81	117.3913	\N
8434	773	VASSOURA LINDISSIMA  ATIS	4	35	49	14	40	\N
\.


--
-- Data for Name: visitas_vendedor; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.visitas_vendedor (id, vendedor_id, cliente_id, data_visita, latitude, longitude, endereco_completo, motivo_visita, observacoes, foto_comprovante, confirmada, empresa_id, criado_em, atualizado_em) FROM stdin;
1	11	49	2026-01-16 01:00:09.39297+00	-2.6491	-44.3047	\N	Diluição	teste	\N	t	1	2026-01-16 01:00:09.387802+00	2026-01-16 01:00:09.983826+00
2	11	21	2026-01-16 01:00:57.358563+00	-2.6491	-44.3047	\N	Diluição	123	\N	t	1	2026-01-16 01:00:57.35889+00	2026-01-16 01:00:57.932648+00
3	11	57	2026-01-16 01:01:58.791114+00	-2.6491	-44.3047	\N	Atendimento	123	\N	t	1	2026-01-16 01:01:58.791532+00	2026-01-16 01:01:59.391465+00
\.


--
-- Name: arquivos_processados_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.arquivos_processados_id_seq', 1, false);


--
-- Name: clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.clientes_id_seq', 74, true);


--
-- Name: empresas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresas_id_seq', 2, true);


--
-- Name: fichas_tecnicas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fichas_tecnicas_id_seq', 1, false);


--
-- Name: fornecedores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.fornecedores_id_seq', 1, false);


--
-- Name: historico_pagamentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.historico_pagamentos_id_seq', 1, false);


--
-- Name: historico_preco_produto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.historico_preco_produto_id_seq', 1, false);


--
-- Name: historico_vendas_cliente_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.historico_vendas_cliente_id_seq', 257, true);


--
-- Name: movimentacoes_estoque_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.movimentacoes_estoque_id_seq', 3107, true);


--
-- Name: orcamento_itens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orcamento_itens_id_seq', 967, true);


--
-- Name: orcamentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orcamentos_id_seq', 90, true);


--
-- Name: ordens_compra_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ordens_compra_id_seq', 3, true);


--
-- Name: ordens_compra_itens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ordens_compra_itens_id_seq', 14, true);


--
-- Name: precos_cliente_produto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.precos_cliente_produto_id_seq', 195, true);


--
-- Name: produtos_concorrentes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.produtos_concorrentes_id_seq', 1, false);


--
-- Name: produtos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.produtos_id_seq', 1114, true);


--
-- Name: propostas_detalhadas_concorrentes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.propostas_detalhadas_concorrentes_id_seq', 1, true);


--
-- Name: propostas_detalhadas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.propostas_detalhadas_id_seq', 19, true);


--
-- Name: propostas_detalhadas_itens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.propostas_detalhadas_itens_id_seq', 20, true);


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.refresh_tokens_id_seq', 11, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 13, true);


--
-- Name: vendas_historicas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.vendas_historicas_id_seq', 8434, true);


--
-- Name: visitas_vendedor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.visitas_vendedor_id_seq', 3, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: arquivos_processados arquivos_processados_hash_arquivo_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.arquivos_processados
    ADD CONSTRAINT arquivos_processados_hash_arquivo_key UNIQUE (hash_arquivo);


--
-- Name: arquivos_processados arquivos_processados_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.arquivos_processados
    ADD CONSTRAINT arquivos_processados_pkey PRIMARY KEY (id);


--
-- Name: clientes clientes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_pkey PRIMARY KEY (id);


--
-- Name: empresas empresas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresas
    ADD CONSTRAINT empresas_pkey PRIMARY KEY (id);


--
-- Name: fichas_tecnicas fichas_tecnicas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fichas_tecnicas
    ADD CONSTRAINT fichas_tecnicas_pkey PRIMARY KEY (id);


--
-- Name: fornecedores fornecedores_cnpj_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fornecedores
    ADD CONSTRAINT fornecedores_cnpj_key UNIQUE (cnpj);


--
-- Name: fornecedores fornecedores_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fornecedores
    ADD CONSTRAINT fornecedores_pkey PRIMARY KEY (id);


--
-- Name: historico_pagamentos historico_pagamentos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_pagamentos
    ADD CONSTRAINT historico_pagamentos_pkey PRIMARY KEY (id);


--
-- Name: historico_preco_produto historico_preco_produto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_preco_produto
    ADD CONSTRAINT historico_preco_produto_pkey PRIMARY KEY (id);


--
-- Name: historico_vendas_cliente historico_vendas_cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_vendas_cliente
    ADD CONSTRAINT historico_vendas_cliente_pkey PRIMARY KEY (id);


--
-- Name: movimentacoes_estoque movimentacoes_estoque_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimentacoes_estoque
    ADD CONSTRAINT movimentacoes_estoque_pkey PRIMARY KEY (id);


--
-- Name: orcamento_itens orcamento_itens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orcamento_itens
    ADD CONSTRAINT orcamento_itens_pkey PRIMARY KEY (id);


--
-- Name: orcamentos orcamentos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orcamentos
    ADD CONSTRAINT orcamentos_pkey PRIMARY KEY (id);


--
-- Name: ordens_compra_itens ordens_compra_itens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordens_compra_itens
    ADD CONSTRAINT ordens_compra_itens_pkey PRIMARY KEY (id);


--
-- Name: ordens_compra ordens_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordens_compra
    ADD CONSTRAINT ordens_compra_pkey PRIMARY KEY (id);


--
-- Name: precos_cliente_produto precos_cliente_produto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.precos_cliente_produto
    ADD CONSTRAINT precos_cliente_produto_pkey PRIMARY KEY (id);


--
-- Name: produtos_concorrentes produtos_concorrentes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.produtos_concorrentes
    ADD CONSTRAINT produtos_concorrentes_pkey PRIMARY KEY (id);


--
-- Name: produtos produtos_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.produtos
    ADD CONSTRAINT produtos_pkey PRIMARY KEY (id);


--
-- Name: propostas_detalhadas_concorrentes propostas_detalhadas_concorrentes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas_concorrentes
    ADD CONSTRAINT propostas_detalhadas_concorrentes_pkey PRIMARY KEY (id);


--
-- Name: propostas_detalhadas_itens propostas_detalhadas_itens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas_itens
    ADD CONSTRAINT propostas_detalhadas_itens_pkey PRIMARY KEY (id);


--
-- Name: propostas_detalhadas propostas_detalhadas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas
    ADD CONSTRAINT propostas_detalhadas_pkey PRIMARY KEY (id);


--
-- Name: propostas_detalhadas propostas_detalhadas_token_compartilhamento_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas
    ADD CONSTRAINT propostas_detalhadas_token_compartilhamento_key UNIQUE (token_compartilhamento);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: precos_cliente_produto uq_cliente_produto; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.precos_cliente_produto
    ADD CONSTRAINT uq_cliente_produto UNIQUE (cliente_id, produto_id);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: vendas_historicas vendas_historicas_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendas_historicas
    ADD CONSTRAINT vendas_historicas_pkey PRIMARY KEY (id);


--
-- Name: visitas_vendedor visitas_vendedor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visitas_vendedor
    ADD CONSTRAINT visitas_vendedor_pkey PRIMARY KEY (id);


--
-- Name: idx_arquivo_empresa_data; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_arquivo_empresa_data ON public.arquivos_processados USING btree (empresa_id, data_processamento);


--
-- Name: idx_arquivo_nf; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_arquivo_nf ON public.arquivos_processados USING btree (nota_fiscal, empresa_id);


--
-- Name: idx_cliente_data; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cliente_data ON public.historico_vendas_cliente USING btree (cliente_id, data_venda);


--
-- Name: idx_cliente_produto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cliente_produto ON public.historico_vendas_cliente USING btree (cliente_id, produto_id);


--
-- Name: idx_concorrente_ativo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_concorrente_ativo ON public.produtos_concorrentes USING btree (ativo);


--
-- Name: idx_concorrente_categoria; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_concorrente_categoria ON public.produtos_concorrentes USING btree (categoria);


--
-- Name: idx_ficha_nome; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ficha_nome ON public.fichas_tecnicas USING btree (nome_produto);


--
-- Name: idx_ficha_produto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ficha_produto ON public.fichas_tecnicas USING btree (produto_id);


--
-- Name: idx_preco_cliente_produto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_preco_cliente_produto ON public.precos_cliente_produto USING btree (cliente_id, produto_id);


--
-- Name: idx_preco_produto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_preco_produto ON public.precos_cliente_produto USING btree (produto_id);


--
-- Name: idx_produto_data; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_produto_data ON public.historico_vendas_cliente USING btree (produto_id, data_venda);


--
-- Name: idx_proposta_concorrente_manual; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_proposta_concorrente_manual ON public.propostas_detalhadas_concorrentes USING btree (proposta_id, nome);


--
-- Name: idx_proposta_data; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_proposta_data ON public.propostas_detalhadas USING btree (data_criacao);


--
-- Name: idx_proposta_item_produto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_proposta_item_produto ON public.propostas_detalhadas_itens USING btree (proposta_id, produto_id);


--
-- Name: idx_proposta_produto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_proposta_produto ON public.propostas_detalhadas USING btree (produto_id);


--
-- Name: idx_proposta_vendedor_cliente; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_proposta_vendedor_cliente ON public.propostas_detalhadas USING btree (vendedor_id, cliente_id);


--
-- Name: idx_vendedor_cliente_produto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vendedor_cliente_produto ON public.historico_vendas_cliente USING btree (vendedor_id, cliente_id, produto_id);


--
-- Name: idx_visita_cliente; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_visita_cliente ON public.visitas_vendedor USING btree (cliente_id, data_visita);


--
-- Name: idx_visita_empresa_confirmada; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_visita_empresa_confirmada ON public.visitas_vendedor USING btree (empresa_id, confirmada, data_visita);


--
-- Name: idx_visita_vendedor_data; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_visita_vendedor_data ON public.visitas_vendedor USING btree (vendedor_id, data_visita);


--
-- Name: ix_arquivos_processados_data_processamento; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_arquivos_processados_data_processamento ON public.arquivos_processados USING btree (data_processamento);


--
-- Name: ix_arquivos_processados_empresa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_arquivos_processados_empresa_id ON public.arquivos_processados USING btree (empresa_id);


--
-- Name: ix_arquivos_processados_hash_arquivo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_arquivos_processados_hash_arquivo ON public.arquivos_processados USING btree (hash_arquivo);


--
-- Name: ix_arquivos_processados_nome_arquivo; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_arquivos_processados_nome_arquivo ON public.arquivos_processados USING btree (nome_arquivo);


--
-- Name: ix_arquivos_processados_nota_fiscal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_arquivos_processados_nota_fiscal ON public.arquivos_processados USING btree (nota_fiscal);


--
-- Name: ix_clientes_cnpj; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_clientes_cnpj ON public.clientes USING btree (cnpj);


--
-- Name: ix_clientes_criado_em; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clientes_criado_em ON public.clientes USING btree (criado_em);


--
-- Name: ix_clientes_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clientes_id ON public.clientes USING btree (id);


--
-- Name: ix_clientes_razao_social; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clientes_razao_social ON public.clientes USING btree (razao_social);


--
-- Name: ix_clientes_telefone; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clientes_telefone ON public.clientes USING btree (telefone);


--
-- Name: ix_clientes_vendedor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clientes_vendedor_id ON public.clientes USING btree (vendedor_id);


--
-- Name: ix_empresas_cnpj; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_empresas_cnpj ON public.empresas USING btree (cnpj);


--
-- Name: ix_empresas_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_empresas_id ON public.empresas USING btree (id);


--
-- Name: ix_empresas_nome; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_empresas_nome ON public.empresas USING btree (nome);


--
-- Name: ix_fichas_tecnicas_nome_produto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_fichas_tecnicas_nome_produto ON public.fichas_tecnicas USING btree (nome_produto);


--
-- Name: ix_fichas_tecnicas_produto_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_fichas_tecnicas_produto_id ON public.fichas_tecnicas USING btree (produto_id);


--
-- Name: ix_fornecedores_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_fornecedores_id ON public.fornecedores USING btree (id);


--
-- Name: ix_fornecedores_nome; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_fornecedores_nome ON public.fornecedores USING btree (nome);


--
-- Name: ix_historico_preco_produto_cliente_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_preco_produto_cliente_id ON public.historico_preco_produto USING btree (cliente_id);


--
-- Name: ix_historico_preco_produto_data_venda; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_preco_produto_data_venda ON public.historico_preco_produto USING btree (data_venda);


--
-- Name: ix_historico_preco_produto_empresa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_preco_produto_empresa_id ON public.historico_preco_produto USING btree (empresa_id);


--
-- Name: ix_historico_preco_produto_nota_fiscal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_preco_produto_nota_fiscal ON public.historico_preco_produto USING btree (nota_fiscal);


--
-- Name: ix_historico_preco_produto_produto_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_preco_produto_produto_id ON public.historico_preco_produto USING btree (produto_id);


--
-- Name: ix_historico_vendas_cliente_cliente_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_vendas_cliente_cliente_id ON public.historico_vendas_cliente USING btree (cliente_id);


--
-- Name: ix_historico_vendas_cliente_data_venda; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_vendas_cliente_data_venda ON public.historico_vendas_cliente USING btree (data_venda);


--
-- Name: ix_historico_vendas_cliente_empresa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_vendas_cliente_empresa_id ON public.historico_vendas_cliente USING btree (empresa_id);


--
-- Name: ix_historico_vendas_cliente_orcamento_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_vendas_cliente_orcamento_id ON public.historico_vendas_cliente USING btree (orcamento_id);


--
-- Name: ix_historico_vendas_cliente_produto_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_vendas_cliente_produto_id ON public.historico_vendas_cliente USING btree (produto_id);


--
-- Name: ix_historico_vendas_cliente_vendedor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_historico_vendas_cliente_vendedor_id ON public.historico_vendas_cliente USING btree (vendedor_id);


--
-- Name: ix_movimentacoes_estoque_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_movimentacoes_estoque_id ON public.movimentacoes_estoque USING btree (id);


--
-- Name: ix_movimentacoes_estoque_reversao_de_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_movimentacoes_estoque_reversao_de_id ON public.movimentacoes_estoque USING btree (reversao_de_id);


--
-- Name: ix_movimentacoes_estoque_revertida; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_movimentacoes_estoque_revertida ON public.movimentacoes_estoque USING btree (revertida);


--
-- Name: ix_movimentacoes_estoque_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_movimentacoes_estoque_status ON public.movimentacoes_estoque USING btree (status);


--
-- Name: ix_orcamento_itens_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_orcamento_itens_id ON public.orcamento_itens USING btree (id);


--
-- Name: ix_orcamentos_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_orcamentos_id ON public.orcamentos USING btree (id);


--
-- Name: ix_orcamentos_token_compartilhamento; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_orcamentos_token_compartilhamento ON public.orcamentos USING btree (token_compartilhamento);


--
-- Name: ix_ordens_compra_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ordens_compra_id ON public.ordens_compra USING btree (id);


--
-- Name: ix_ordens_compra_itens_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ordens_compra_itens_id ON public.ordens_compra_itens USING btree (id);


--
-- Name: ix_produtos_categoria; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_produtos_categoria ON public.produtos USING btree (categoria);


--
-- Name: ix_produtos_codigo; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_produtos_codigo ON public.produtos USING btree (codigo);


--
-- Name: ix_produtos_concorrentes_categoria; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_produtos_concorrentes_categoria ON public.produtos_concorrentes USING btree (categoria);


--
-- Name: ix_produtos_concorrentes_nome; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_produtos_concorrentes_nome ON public.produtos_concorrentes USING btree (nome);


--
-- Name: ix_produtos_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_produtos_id ON public.produtos USING btree (id);


--
-- Name: ix_produtos_nome; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_produtos_nome ON public.produtos USING btree (nome);


--
-- Name: ix_propostas_concorrentes_proposta; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_propostas_concorrentes_proposta ON public.propostas_detalhadas_concorrentes USING btree (proposta_id);


--
-- Name: ix_propostas_detalhadas_cliente_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_propostas_detalhadas_cliente_id ON public.propostas_detalhadas USING btree (cliente_id);


--
-- Name: ix_propostas_detalhadas_data_criacao; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_propostas_detalhadas_data_criacao ON public.propostas_detalhadas USING btree (data_criacao);


--
-- Name: ix_propostas_detalhadas_orcamento_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_propostas_detalhadas_orcamento_id ON public.propostas_detalhadas USING btree (orcamento_id);


--
-- Name: ix_propostas_detalhadas_produto_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_propostas_detalhadas_produto_id ON public.propostas_detalhadas USING btree (produto_id);


--
-- Name: ix_propostas_detalhadas_token_compartilhamento; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_propostas_detalhadas_token_compartilhamento ON public.propostas_detalhadas USING btree (token_compartilhamento);


--
-- Name: ix_propostas_detalhadas_vendedor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_propostas_detalhadas_vendedor_id ON public.propostas_detalhadas USING btree (vendedor_id);


--
-- Name: ix_propostas_itens_produto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_propostas_itens_produto ON public.propostas_detalhadas_itens USING btree (produto_id);


--
-- Name: ix_propostas_itens_proposta; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_propostas_itens_proposta ON public.propostas_detalhadas_itens USING btree (proposta_id);


--
-- Name: ix_refresh_tokens_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_refresh_tokens_id ON public.refresh_tokens USING btree (id);


--
-- Name: ix_refresh_tokens_token; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_refresh_tokens_token ON public.refresh_tokens USING btree (token);


--
-- Name: ix_refresh_tokens_usuario_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_refresh_tokens_usuario_id ON public.refresh_tokens USING btree (usuario_id);


--
-- Name: ix_usuarios_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_usuarios_email ON public.usuarios USING btree (email);


--
-- Name: ix_usuarios_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usuarios_id ON public.usuarios USING btree (id);


--
-- Name: ix_usuarios_nome; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usuarios_nome ON public.usuarios USING btree (nome);


--
-- Name: ix_vendas_historicas_descricao; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_vendas_historicas_descricao ON public.vendas_historicas USING btree (descricao);


--
-- Name: ix_vendas_historicas_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_vendas_historicas_id ON public.vendas_historicas USING btree (id);


--
-- Name: ix_vendas_historicas_ident_antigo; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_vendas_historicas_ident_antigo ON public.vendas_historicas USING btree (ident_antigo);


--
-- Name: ix_visitas_vendedor_cliente_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_visitas_vendedor_cliente_id ON public.visitas_vendedor USING btree (cliente_id);


--
-- Name: ix_visitas_vendedor_confirmada; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_visitas_vendedor_confirmada ON public.visitas_vendedor USING btree (confirmada);


--
-- Name: ix_visitas_vendedor_data_visita; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_visitas_vendedor_data_visita ON public.visitas_vendedor USING btree (data_visita);


--
-- Name: ix_visitas_vendedor_empresa_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_visitas_vendedor_empresa_id ON public.visitas_vendedor USING btree (empresa_id);


--
-- Name: ix_visitas_vendedor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_visitas_vendedor_id ON public.visitas_vendedor USING btree (id);


--
-- Name: ix_visitas_vendedor_vendedor_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_visitas_vendedor_vendedor_id ON public.visitas_vendedor USING btree (vendedor_id);


--
-- Name: arquivos_processados arquivos_processados_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.arquivos_processados
    ADD CONSTRAINT arquivos_processados_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: arquivos_processados arquivos_processados_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.arquivos_processados
    ADD CONSTRAINT arquivos_processados_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- Name: clientes clientes_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT clientes_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: fichas_tecnicas fichas_tecnicas_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fichas_tecnicas
    ADD CONSTRAINT fichas_tecnicas_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: clientes fk_cliente_vendedor; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clientes
    ADD CONSTRAINT fk_cliente_vendedor FOREIGN KEY (vendedor_id) REFERENCES public.usuarios(id);


--
-- Name: movimentacoes_estoque fk_movimentacao_reversao_de; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimentacoes_estoque
    ADD CONSTRAINT fk_movimentacao_reversao_de FOREIGN KEY (reversao_de_id) REFERENCES public.movimentacoes_estoque(id);


--
-- Name: movimentacoes_estoque fk_movimentacao_revertida_por; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimentacoes_estoque
    ADD CONSTRAINT fk_movimentacao_revertida_por FOREIGN KEY (revertida_por_id) REFERENCES public.usuarios(id);


--
-- Name: movimentacoes_estoque fk_movimentacoes_estoque_aprovado_por; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimentacoes_estoque
    ADD CONSTRAINT fk_movimentacoes_estoque_aprovado_por FOREIGN KEY (aprovado_por_id) REFERENCES public.usuarios(id) ON DELETE SET NULL;


--
-- Name: produtos fk_produtos_fornecedores_on_fornecedor_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.produtos
    ADD CONSTRAINT fk_produtos_fornecedores_on_fornecedor_id FOREIGN KEY (fornecedor_id) REFERENCES public.fornecedores(id);


--
-- Name: visitas_vendedor fk_visitas_cliente; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visitas_vendedor
    ADD CONSTRAINT fk_visitas_cliente FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: visitas_vendedor fk_visitas_empresa; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visitas_vendedor
    ADD CONSTRAINT fk_visitas_empresa FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: visitas_vendedor fk_visitas_vendedor; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.visitas_vendedor
    ADD CONSTRAINT fk_visitas_vendedor FOREIGN KEY (vendedor_id) REFERENCES public.usuarios(id);


--
-- Name: fornecedores fornecedores_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.fornecedores
    ADD CONSTRAINT fornecedores_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: historico_pagamentos historico_pagamentos_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_pagamentos
    ADD CONSTRAINT historico_pagamentos_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: historico_preco_produto historico_preco_produto_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_preco_produto
    ADD CONSTRAINT historico_preco_produto_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: historico_preco_produto historico_preco_produto_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_preco_produto
    ADD CONSTRAINT historico_preco_produto_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: historico_preco_produto historico_preco_produto_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_preco_produto
    ADD CONSTRAINT historico_preco_produto_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: historico_vendas_cliente historico_vendas_cliente_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_vendas_cliente
    ADD CONSTRAINT historico_vendas_cliente_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: historico_vendas_cliente historico_vendas_cliente_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_vendas_cliente
    ADD CONSTRAINT historico_vendas_cliente_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: historico_vendas_cliente historico_vendas_cliente_orcamento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_vendas_cliente
    ADD CONSTRAINT historico_vendas_cliente_orcamento_id_fkey FOREIGN KEY (orcamento_id) REFERENCES public.orcamentos(id);


--
-- Name: historico_vendas_cliente historico_vendas_cliente_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_vendas_cliente
    ADD CONSTRAINT historico_vendas_cliente_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: historico_vendas_cliente historico_vendas_cliente_vendedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.historico_vendas_cliente
    ADD CONSTRAINT historico_vendas_cliente_vendedor_id_fkey FOREIGN KEY (vendedor_id) REFERENCES public.usuarios(id);


--
-- Name: movimentacoes_estoque movimentacoes_estoque_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimentacoes_estoque
    ADD CONSTRAINT movimentacoes_estoque_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: movimentacoes_estoque movimentacoes_estoque_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.movimentacoes_estoque
    ADD CONSTRAINT movimentacoes_estoque_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- Name: orcamento_itens orcamento_itens_orcamento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orcamento_itens
    ADD CONSTRAINT orcamento_itens_orcamento_id_fkey FOREIGN KEY (orcamento_id) REFERENCES public.orcamentos(id);


--
-- Name: orcamento_itens orcamento_itens_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orcamento_itens
    ADD CONSTRAINT orcamento_itens_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: orcamentos orcamentos_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orcamentos
    ADD CONSTRAINT orcamentos_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: orcamentos orcamentos_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orcamentos
    ADD CONSTRAINT orcamentos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- Name: ordens_compra ordens_compra_fornecedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordens_compra
    ADD CONSTRAINT ordens_compra_fornecedor_id_fkey FOREIGN KEY (fornecedor_id) REFERENCES public.fornecedores(id);


--
-- Name: ordens_compra_itens ordens_compra_itens_ordem_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordens_compra_itens
    ADD CONSTRAINT ordens_compra_itens_ordem_id_fkey FOREIGN KEY (ordem_id) REFERENCES public.ordens_compra(id);


--
-- Name: ordens_compra_itens ordens_compra_itens_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordens_compra_itens
    ADD CONSTRAINT ordens_compra_itens_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: ordens_compra ordens_compra_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ordens_compra
    ADD CONSTRAINT ordens_compra_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);


--
-- Name: precos_cliente_produto precos_cliente_produto_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.precos_cliente_produto
    ADD CONSTRAINT precos_cliente_produto_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id) ON DELETE CASCADE;


--
-- Name: precos_cliente_produto precos_cliente_produto_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.precos_cliente_produto
    ADD CONSTRAINT precos_cliente_produto_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id) ON DELETE CASCADE;


--
-- Name: produtos produtos_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.produtos
    ADD CONSTRAINT produtos_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: propostas_detalhadas propostas_detalhadas_cliente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas
    ADD CONSTRAINT propostas_detalhadas_cliente_id_fkey FOREIGN KEY (cliente_id) REFERENCES public.clientes(id);


--
-- Name: propostas_detalhadas propostas_detalhadas_concorrente_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas
    ADD CONSTRAINT propostas_detalhadas_concorrente_id_fkey FOREIGN KEY (concorrente_id) REFERENCES public.produtos_concorrentes(id);


--
-- Name: propostas_detalhadas_concorrentes propostas_detalhadas_concorrentes_proposta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas_concorrentes
    ADD CONSTRAINT propostas_detalhadas_concorrentes_proposta_id_fkey FOREIGN KEY (proposta_id) REFERENCES public.propostas_detalhadas(id) ON DELETE CASCADE;


--
-- Name: propostas_detalhadas propostas_detalhadas_ficha_tecnica_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas
    ADD CONSTRAINT propostas_detalhadas_ficha_tecnica_id_fkey FOREIGN KEY (ficha_tecnica_id) REFERENCES public.fichas_tecnicas(id);


--
-- Name: propostas_detalhadas_itens propostas_detalhadas_itens_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas_itens
    ADD CONSTRAINT propostas_detalhadas_itens_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: propostas_detalhadas_itens propostas_detalhadas_itens_proposta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas_itens
    ADD CONSTRAINT propostas_detalhadas_itens_proposta_id_fkey FOREIGN KEY (proposta_id) REFERENCES public.propostas_detalhadas(id) ON DELETE CASCADE;


--
-- Name: propostas_detalhadas propostas_detalhadas_orcamento_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas
    ADD CONSTRAINT propostas_detalhadas_orcamento_id_fkey FOREIGN KEY (orcamento_id) REFERENCES public.orcamentos(id);


--
-- Name: propostas_detalhadas propostas_detalhadas_produto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas
    ADD CONSTRAINT propostas_detalhadas_produto_id_fkey FOREIGN KEY (produto_id) REFERENCES public.produtos(id);


--
-- Name: propostas_detalhadas propostas_detalhadas_vendedor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.propostas_detalhadas
    ADD CONSTRAINT propostas_detalhadas_vendedor_id_fkey FOREIGN KEY (vendedor_id) REFERENCES public.usuarios(id);


--
-- Name: refresh_tokens refresh_tokens_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;


--
-- Name: usuarios usuarios_empresa_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_empresa_id_fkey FOREIGN KEY (empresa_id) REFERENCES public.empresas(id);


--
-- Name: vendas_historicas vendas_historicas_produto_atual_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vendas_historicas
    ADD CONSTRAINT vendas_historicas_produto_atual_id_fkey FOREIGN KEY (produto_atual_id) REFERENCES public.produtos(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 8IPyZOu44PUqGborIehZ8EGWhmHt7GZGOjuslWmk34QyjFzHOI3cgPMdTjQ7ub3

