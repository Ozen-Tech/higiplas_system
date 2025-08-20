GRANT USAGE ON SCHEMA public TO higiplas_user;
GRANT ALL PRIVILEGES ON TABLE public.produtos TO higiplas_user;
GRANT USAGE, SELECT ON SEQUENCE public.produtos_id_seq TO higiplas_user;
GRANT ALL PRIVILEGES ON TABLE public.clientes TO higiplas_user;
GRANT USAGE, SELECT ON SEQUENCE public.clientes_id_seq TO higiplas_user;