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

--
-- Data for Name: admin; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

INSERT INTO public.admin (id, username, password_hash, email) VALUES (1, 'Nanou', 'scrypt:32768:8:1$2oUrJ8YVY49mF5hs$591524aadac00c7de82a39db970a896b67c315feebc6270cbefab3eb7191dac658a153e5a5860f548e034e134e825241805bbeb198f8565fbafc7c9bf7bc1ff6', 'nanou_fabie@icloud.com');


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

INSERT INTO public.alembic_version (version_num) VALUES ('885cc882c393');


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

INSERT INTO public."user" (id, username, firstname, lastname, fidelity_level, password_hash, email, fidelity_cycle, admin_id, consent_privacy, consent_date, is_approved, deleted_at, is_anonymized) VALUES (20, 'deleted_user_20_41e2b5', 'Cyril', 'Gharbi', 0, 'scrypt:32768:8:1$pfrvcvkxsbrRTKhS$2489898e96eb9ecc9c9e30862cd74fde5e7adddf1ac6269eac235241dc10161f1c2f07075b679dcdec65935ecfee60bf70729b89ddb9fd9178f18a33a49a606f', 'deleted_user_20_556e3a45@example.com', 0, NULL, true, '2025-06-18 13:49:13.441362+02', true, '2025-06-18 08:17:42.342352', true);
INSERT INTO public."user" (id, username, firstname, lastname, fidelity_level, password_hash, email, fidelity_cycle, admin_id, consent_privacy, consent_date, is_approved, deleted_at, is_anonymized) VALUES (29, 'Fabie', 'Fabienne', 'André', 0, 'scrypt:32768:8:1$YdSUkH1DWDIf08if$1f981b4b0a1069d9e03e1d0e4ecd142583f834787b143e24af6c42d46be61440db1c78919c4a1a697b155ee6ad942a6e40f16f891f1e35d0d2d9a6d9136d1086', 'assia_fabie@hotmail.com', 0, NULL, true, '2025-06-18 14:43:26.69122+02', true, NULL, false);
INSERT INTO public."user" (id, username, firstname, lastname, fidelity_level, password_hash, email, fidelity_cycle, admin_id, consent_privacy, consent_date, is_approved, deleted_at, is_anonymized) VALUES (30, 'deleted_user_30_4f2fbf', 'Cyril', 'Gharbi', 3, 'scrypt:32768:8:1$nTH5HX9WniTk9pJt$6ff2d4a0b03f7bfe628579edfe4eecdf4af775786cd47aa94c9dda1070eca370f656a3b5375e591e4cedb57884afc2830bfc98a2b1bb94d4e4604c877ef160aa', 'deleted_user_30_17a36754@example.com', 0, NULL, true, '2025-06-18 14:46:56.099682+02', true, '2025-06-18 12:48:56.539444', true);
INSERT INTO public."user" (id, username, firstname, lastname, fidelity_level, password_hash, email, fidelity_cycle, admin_id, consent_privacy, consent_date, is_approved, deleted_at, is_anonymized) VALUES (31, 'deleted_user_31_5b90a0', 'Cyril', 'Gharbi', 0, 'scrypt:32768:8:1$zvAqBMTxS5dpPqjx$34dc95841710ed40e3d731cd18e753e90eb97b93e25b778a34cfd7eb2ee6c2eae012882e754abdd7a85fbdf01ab27f8f2f70eaf68600e5f3be50147bda410a11', 'deleted_user_31_2b6cbc2d@example.com', 0, NULL, true, '2025-06-18 14:49:23.666733+02', true, '2025-09-01 10:33:37.360686', true);
INSERT INTO public."user" (id, username, firstname, lastname, fidelity_level, password_hash, email, fidelity_cycle, admin_id, consent_privacy, consent_date, is_approved, deleted_at, is_anonymized) VALUES (35, 'CyG_GH', 'Cyril', 'Gharbi', 0, 'scrypt:32768:8:1$RI38YwtUUBk0qyVc$92471ba92e1abcdb601c561792115e59c4f7f73c315574e31ad753b19e09f1472f10de54a2e1a2cabd065c09f31b933fbd692b97b0e346fdb4e3427137add7db', 'cyril.gharbi@gmail.com', 0, NULL, true, '2025-09-01 11:03:43.949236+02', true, NULL, false);


--
-- Data for Name: comment; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

INSERT INTO public.comment (id, content, date, user_id, username_at_time, is_visible) VALUES (14, 'super efficace !!!', '2025-06-18 07:32:34.243433+02', NULL, 'Cyril_GH', true);


--
-- Data for Name: fidelity_reward_log; Type: TABLE DATA; Schema: public; Owner: cyg_gh
--

INSERT INTO public.fidelity_reward_log (id, user_id, level_reached, date, cycle_number) VALUES (1, NULL, 4, '2025-05-16 08:09:30.187574+02', 0);
INSERT INTO public.fidelity_reward_log (id, user_id, level_reached, date, cycle_number) VALUES (2, NULL, 9, '2025-05-16 08:20:25.588911+02', 0);
INSERT INTO public.fidelity_reward_log (id, user_id, level_reached, date, cycle_number) VALUES (3, NULL, 9, '2025-05-16 14:26:01.347032+02', 1);
INSERT INTO public.fidelity_reward_log (id, user_id, level_reached, date, cycle_number) VALUES (4, NULL, 4, '2025-05-16 14:27:06.774358+02', 2);
INSERT INTO public.fidelity_reward_log (id, user_id, level_reached, date, cycle_number) VALUES (5, NULL, 9, '2025-05-16 14:45:01.584615+02', 2);
INSERT INTO public.fidelity_reward_log (id, user_id, level_reached, date, cycle_number) VALUES (6, NULL, 4, '2025-05-21 10:11:32.222382+02', 3);


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
-- PostgreSQL database dump complete
--

