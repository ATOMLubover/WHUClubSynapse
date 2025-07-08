-- 为社团leader插入club_members记录
-- 根据temp.sql文件中的社团数据生成

INSERT INTO public.club_members
(member_id, user_id, club_id, role_in_club, joined_at, last_active)
VALUES
-- 社团1：英语口语社团 (club_id: 6, leader_id: 8)
(nextval('club_members_member_id_seq'::regclass), 8, 6, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团2：青年志愿者协会 (club_id: 7, leader_id: 8)
(nextval('club_members_member_id_seq'::regclass), 8, 7, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团3：摄影社 (club_id: 8, leader_id: 8)
(nextval('club_members_member_id_seq'::regclass), 8, 8, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团4：机器人社团 (club_id: 9, leader_id: 8)
(nextval('club_members_member_id_seq'::regclass), 8, 9, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团5：茶艺社 (club_id: 10, leader_id: 8)
(nextval('club_members_member_id_seq'::regclass), 8, 10, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团6：街舞社 (club_id: 11, leader_id: 9)
(nextval('club_members_member_id_seq'::regclass), 8, 11, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团7：动漫社 (club_id: 12, leader_id: 10)
(nextval('club_members_member_id_seq'::regclass), 8, 12, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团8：心理健康协会 (club_id: 13, leader_id: 11)
(nextval('club_members_member_id_seq'::regclass), 8, 13, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团9：编程俱乐部 (club_id: 14, leader_id: 12)
(nextval('club_members_member_id_seq'::regclass), 8, 14, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团10：文学社 (club_id: 15, leader_id: 13)
(nextval('club_members_member_id_seq'::regclass), 8, 15, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团11：足球爱好者协会 (club_id: 16, leader_id: 14)
(nextval('club_members_member_id_seq'::regclass), 8, 16, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团12：棋艺社 (club_id: 17, leader_id: 15)
(nextval('club_members_member_id_seq'::regclass), 8, 17, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团13：吉他社 (club_id: 18, leader_id: 16)
(nextval('club_members_member_id_seq'::regclass), 8, 18, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团14：辩论社 (club_id: 19, leader_id: 17)
(nextval('club_members_member_id_seq'::regclass), 8, 19, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团15：天文爱好者协会 (club_id: 20, leader_id: 18)
(nextval('club_members_member_id_seq'::regclass), 8, 20, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团16：烹饪社 (club_id: 21, leader_id: 19)
(nextval('club_members_member_id_seq'::regclass), 8, 21, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团17：创业俱乐部 (club_id: 22, leader_id: 20)
(nextval('club_members_member_id_seq'::regclass), 8, 22, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团18：篮球社 (club_id: 23, leader_id: 21)
(nextval('club_members_member_id_seq'::regclass), 8, 23, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团19：手工艺社 (club_id: 24, leader_id: 22)
(nextval('club_members_member_id_seq'::regclass), 8, 24, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团20：电影鉴赏社 (club_id: 25, leader_id: 23)
(nextval('club_members_member_id_seq'::regclass), 8, 25, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团21：环保协会 (club_id: 26, leader_id: 24)
(nextval('club_members_member_id_seq'::regclass), 8, 26, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团22：乐高俱乐部 (club_id: 27, leader_id: 25)
(nextval('club_members_member_id_seq'::regclass), 8, 27, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团23：模拟联合国社团 (club_id: 28, leader_id: 26)
(nextval('club_members_member_id_seq'::regclass), 8, 28, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团24：瑜伽社 (club_id: 29, leader_id: 27)
(nextval('club_members_member_id_seq'::regclass), 8, 29, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),

-- 社团25：心理咨询互助社 (club_id: 30, leader_id: 8)
(nextval('club_members_member_id_seq'::regclass), 8, 30, 'leader'::character varying, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP); 
