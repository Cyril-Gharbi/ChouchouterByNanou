--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4
-- Dumped by pg_dump version 17.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin; Type: TABLE; Schema: public; Owner: cyg_gh
--

CREATE TABLE public.admin (
    id integer NOT NULL,
    username character varying(150) NOT NULL,
    password_hash character varying(512),
    email character varying(150) DEFAULT 'default@example.com'::character varying NOT NULL
);


ALTER TABLE public.admin OWNER TO cyg_gh;

--
-- Name: admin_id_seq; Type: SEQUENCE; Schema: public; Owner: cyg_gh
--

CREATE SEQUENCE public.admin_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.admin_id_seq OWNER TO cyg_gh;

--
-- Name: admin_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cyg_gh
--

ALTER SEQUENCE public.admin_id_seq OWNED BY public.admin.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: cyg_gh
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO cyg_gh;

--
-- Name: comment; Type: TABLE; Schema: public; Owner: cyg_gh
--

CREATE TABLE public.comment (
    id integer NOT NULL,
    content text NOT NULL,
    date timestamp with time zone NOT NULL,
    user_id integer,
    username_at_time character varying(250) NOT NULL,
    is_visible boolean
);


ALTER TABLE public.comment OWNER TO cyg_gh;

--
-- Name: comment_id_seq; Type: SEQUENCE; Schema: public; Owner: cyg_gh
--

CREATE SEQUENCE public.comment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.comment_id_seq OWNER TO cyg_gh;

--
-- Name: comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cyg_gh
--

ALTER SEQUENCE public.comment_id_seq OWNED BY public.comment.id;


--
-- Name: fidelity_reward_log; Type: TABLE; Schema: public; Owner: cyg_gh
--

CREATE TABLE public.fidelity_reward_log (
    id integer NOT NULL,
    user_id integer,
    level_reached integer NOT NULL,
    date timestamp with time zone,
    cycle_number integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.fidelity_reward_log OWNER TO cyg_gh;

--
-- Name: fidelity_reward_log_id_seq; Type: SEQUENCE; Schema: public; Owner: cyg_gh
--

CREATE SEQUENCE public.fidelity_reward_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fidelity_reward_log_id_seq OWNER TO cyg_gh;

--
-- Name: fidelity_reward_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cyg_gh
--

ALTER SEQUENCE public.fidelity_reward_log_id_seq OWNED BY public.fidelity_reward_log.id;


--
-- Name: user; Type: TABLE; Schema: public; Owner: cyg_gh
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    username character varying(150) NOT NULL,
    firstname character varying(150) NOT NULL,
    lastname character varying(150) NOT NULL,
    fidelity_level integer,
    password_hash character varying(512) NOT NULL,
    email character varying(150) NOT NULL,
    fidelity_cycle integer DEFAULT 0,
    admin_id integer,
    consent_privacy boolean NOT NULL,
    consent_date timestamp with time zone,
    is_approved boolean,
    deleted_at timestamp without time zone,
    is_anonymized boolean
);


ALTER TABLE public."user" OWNER TO cyg_gh;

--
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: cyg_gh
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO cyg_gh;

--
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cyg_gh
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- Name: admin id; Type: DEFAULT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.admin ALTER COLUMN id SET DEFAULT nextval('public.admin_id_seq'::regclass);


--
-- Name: comment id; Type: DEFAULT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.comment ALTER COLUMN id SET DEFAULT nextval('public.comment_id_seq'::regclass);


--
-- Name: fidelity_reward_log id; Type: DEFAULT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.fidelity_reward_log ALTER COLUMN id SET DEFAULT nextval('public.fidelity_reward_log_id_seq'::regclass);


--
-- Name: user id; Type: DEFAULT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- Data for Name: admin; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

COPY public.admin (id, username, password_hash, email) FROM stdin;
1	Nanou	scrypt:32768:8:1$2oUrJ8YVY49mF5hs$591524aadac00c7de82a39db970a896b67c315feebc6270cbefab3eb7191dac658a153e5a5860f548e034e134e825241805bbeb198f8565fbafc7c9bf7bc1ff6	nanou_fabie@icloud.com
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

COPY public.alembic_version (version_num) FROM stdin;
885cc882c393
\.


--
-- Data for Name: comment; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

COPY public.comment (id, content, date, user_id, username_at_time, is_visible) FROM stdin;
14	super efficace !!!	2025-06-18 07:32:34.243433+02	\N	Cyril_GH	t
\.


--
-- Data for Name: fidelity_reward_log; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

COPY public.fidelity_reward_log (id, user_id, level_reached, date, cycle_number) FROM stdin;
1	\N	4	2025-05-16 08:09:30.187574+02	0
2	\N	9	2025-05-16 08:20:25.588911+02	0
3	\N	9	2025-05-16 14:26:01.347032+02	1
4	\N	4	2025-05-16 14:27:06.774358+02	2
5	\N	9	2025-05-16 14:45:01.584615+02	2
6	\N	4	2025-05-21 10:11:32.222382+02	3
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

COPY public."user" (id, username, firstname, lastname, fidelity_level, password_hash, email, fidelity_cycle, admin_id, consent_privacy, consent_date, is_approved, deleted_at, is_anonymized) FROM stdin;
20	deleted_user_20_41e2b5	Cyril	Gharbi	0	scrypt:32768:8:1$pfrvcvkxsbrRTKhS$2489898e96eb9ecc9c9e30862cd74fde5e7adddf1ac6269eac235241dc10161f1c2f07075b679dcdec65935ecfee60bf70729b89ddb9fd9178f18a33a49a606f	deleted_user_20_556e3a45@example.com	0	\N	t	2025-06-18 13:49:13.441362+02	t	2025-06-18 08:17:42.342352	t
29	Fabie	Fabienne	André	0	scrypt:32768:8:1$YdSUkH1DWDIf08if$1f981b4b0a1069d9e03e1d0e4ecd142583f834787b143e24af6c42d46be61440db1c78919c4a1a697b155ee6ad942a6e40f16f891f1e35d0d2d9a6d9136d1086	assia_fabie@hotmail.com	0	\N	t	2025-06-18 14:43:26.69122+02	t	\N	f
30	deleted_user_30_4f2fbf	Cyril	Gharbi	3	scrypt:32768:8:1$nTH5HX9WniTk9pJt$6ff2d4a0b03f7bfe628579edfe4eecdf4af775786cd47aa94c9dda1070eca370f656a3b5375e591e4cedb57884afc2830bfc98a2b1bb94d4e4604c877ef160aa	deleted_user_30_17a36754@example.com	0	\N	t	2025-06-18 14:46:56.099682+02	t	2025-06-18 12:48:56.539444	t
31	deleted_user_31_5b90a0	Cyril	Gharbi	0	scrypt:32768:8:1$zvAqBMTxS5dpPqjx$34dc95841710ed40e3d731cd18e753e90eb97b93e25b778a34cfd7eb2ee6c2eae012882e754abdd7a85fbdf01ab27f8f2f70eaf68600e5f3be50147bda410a11	deleted_user_31_2b6cbc2d@example.com	0	\N	t	2025-06-18 14:49:23.666733+02	t	2025-09-01 10:33:37.360686	t
35	CyG_GH	Cyril	Gharbi	0	scrypt:32768:8:1$RI38YwtUUBk0qyVc$92471ba92e1abcdb601c561792115e59c4f7f73c315574e31ad753b19e09f1472f10de54a2e1a2cabd065c09f31b933fbd692b97b0e346fdb4e3427137add7db	cyril.gharbi@gmail.com	0	\N	t	2025-09-01 11:03:43.949236+02	t	\N	f
\.


--
-- Name: admin_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cyg_gh
--

SELECT pg_catalog.setval('public.admin_id_seq', 1, true);


--
-- Name: comment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cyg_gh
--

SELECT pg_catalog.setval('public.comment_id_seq', 22, true);


--
-- Name: fidelity_reward_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cyg_gh
--

SELECT pg_catalog.setval('public.fidelity_reward_log_id_seq', 6, true);


--
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cyg_gh
--

SELECT pg_catalog.setval('public.user_id_seq', 41, true);


--
-- Name: admin admin_email_key; Type: CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_email_key UNIQUE (email);


--
-- Name: admin admin_pkey; Type: CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_pkey PRIMARY KEY (id);


--
-- Name: admin admin_username_key; Type: CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.admin
    ADD CONSTRAINT admin_username_key UNIQUE (username);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: comment comment_pkey; Type: CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.comment
    ADD CONSTRAINT comment_pkey PRIMARY KEY (id);


--
-- Name: fidelity_reward_log fidelity_reward_log_pkey; Type: CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.fidelity_reward_log
    ADD CONSTRAINT fidelity_reward_log_pkey PRIMARY KEY (id);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: comment comment_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.comment
    ADD CONSTRAINT comment_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: fidelity_reward_log fidelity_reward_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public.fidelity_reward_log
    ADD CONSTRAINT fidelity_reward_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: user user_admin_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cyg_gh
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_admin_id_fkey FOREIGN KEY (admin_id) REFERENCES public.admin(id);


--
-- PostgreSQL database dump complete
--

