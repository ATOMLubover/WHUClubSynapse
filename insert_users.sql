-- 插入用户数据（适配public.users 表结构）
INSERT INTO "public"."users" (
  "username", 
  "password_hash", 
  "email", 
  "avatar_url", 
  "role", 
  "created_at", 
  "updated_at", 
  "last_active", 
  "extension"
) VALUES 
-- 用户1
(
  'user_0001', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0001@example.com',  
  NULL, 
  'admin', 
  '2025-01-25 11:02:36', 
  '2025-01-26 11:02:36', 
  '2025-01-26 23:34:36', 
  '{"realName":"周涛","studentId":"20236170","major":"软件工程","bio":"专注于数据分析","preferences":{"interestedCategories":["阅读","运动","音乐"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":true},"tags":["开朗外向","独立思考"],"phone":"13057013952"}'
),
-- 用户2
(
  'user_0002', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0002@example.com',  
  NULL, 
  'admin', 
  '2025-01-01 11:02:36', 
  '2025-01-04 11:02:36', 
  '2025-01-04 17:58:36', 
  '{"realName":"李娜","studentId":"20236268","major":"人工智能","bio":"热衷于技术创新","preferences":{"interestedCategories":["游戏","旅行"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":true},"tags":["独立思考"],"phone":"13198126929"}'
),
-- 用户3
(
  'user_0003', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0003@example.com',  
  NULL, 
  'user', 
  '2025-04-17 11:02:36', 
  '2025-04-22 11:02:36', 
  '2025-04-22 23:28:36', 
  '{"realName":"赵磊","studentId":"20231391","major":"通信工程","bio":"积极向上，乐于学习","preferences":{"interestedCategories":["旅行","游戏"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":false},"tags":["逻辑清晰","学习能力强"],"phone":"13476426347"}'
),
-- 用户4
(
  'user_0004', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0004@example.com',  
  NULL, 
  'user', 
  '2025-03-19 11:03:47', 
  '2025-03-24 11:03:47', 
  '2025-03-25 08:27:47', 
  '{"realName":"何丹","studentId":"20234083","major":"自动化","bio":"积极向上，乐于学习","preferences":{"interestedCategories":["阅读","金融"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":true},"tags":["耐心细致","责任心强","沉着冷静"],"phone":"13645875997"}'
),
-- 用户5
(
  'user_0005', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0005@example.com',  
  NULL, 
  'admin', 
  '2025-03-22 11:03:47', 
  '2025-03-27 11:03:47', 
  '2025-03-27 15:43:47', 
  '{"realName":"陈洁","studentId":"20233239","major":"传播学","bio":"热爱编程和篮球","preferences":{"interestedCategories":["教育","科技","健康","电影"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":false},"tags":["独立思考","逻辑清晰","勇于担当"],"phone":"13682439169"}'
),
-- 用户6
(
  'user_0006', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0006@example.com',  
  NULL, 
  'admin', 
  '2025-03-03 11:03:47', 
  '2025-03-10 11:03:47', 
  '2025-03-10 14:09:47', 
  '{"realName":"高飞","studentId":"20232544","major":"机械工程","bio":"擅长团队协作","preferences":{"interestedCategories":["摄影","美食"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":true},"tags":["责任心强","幽默风趣"],"phone":"13988746261"}'
),
-- 用户7
(
  'user_0007', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0007@example.com',  
  NULL, 
  'admin', 
  '2024-11-13 11:23:34', 
  '2025-05-30 11:23:34', 
  '2025-07-07 08:54:34', 
  '{"realName":"李娜","studentId":"20235687","major":"生物医学工程","bio":"喜欢探索未知领域","preferences":{"interestedCategories":["文化","自然","时尚","历史","美食"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":false},"tags":["沉着冷静","善于沟通","学习能力强","幽默风趣"],"phone":"13757024443"}'
),
-- 用户8
(
  'user_0008', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0008@example.com',  
  NULL, 
  'admin', 
  '2025-04-20 11:23:34', 
  '2025-05-31 11:23:34', 
  '2025-07-07 08:22:34', 
  '{"realName":"王伟","studentId":"20231815","major":"教育学","bio":"独立思考，勇于创新","preferences":{"interestedCategories":["新闻","金融","摄影","阅读"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":true},"tags":["独立思考"],"phone":"13671798942"}'
),
-- 用户9
(
  'user_0009', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0009@example.com',  
  NULL, 
  'admin', 
  '2025-03-02 11:23:34', 
  '2025-05-12 11:23:34', 
  '2025-07-06 16:58:34', 
  '{"realName":"王伟","studentId":"20232516","major":"人工智能","bio":"喜欢探索未知领域","preferences":{"interestedCategories":["游戏","艺术","生活","金融","运动"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":true},"tags":["组织能力强","富有创造力"],"phone":"13319503286"}'
),
-- 用户10
(
  'user_0010', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0010@example.com',  
  NULL, 
  'admin', 
  '2024-09-07 11:24:03', 
  '2024-10-01 11:24:03', 
  '2024-10-14 10:21:03', 
  '{"realName":"姜文","studentId":"20235259","major":"机械工程","bio":"热爱编程和篮球","preferences":{"interestedCategories":["文化","商业","电影","旅行","历史"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":false},"tags":["学习能力强"],"phone":"13472419978"}'
),
-- 用户11
(
  'user_0011', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0011@example.com',  
  NULL, 
  'admin', 
  '2025-01-20 11:24:03', 
  '2025-02-06 11:24:03', 
  '2025-03-03 11:30:03', 
  '{"realName":"吴迪","studentId":"20231378","major":"传播学","bio":"享受生活，乐于分享","preferences":{"interestedCategories":["金融"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":true},"tags":["开朗外向"],"phone":"13329633879"}'
),
-- 用户12
(
  'user_0012', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0012@example.com',  
  NULL, 
  'user', 
  '2025-04-30 11:24:03', 
  '2025-05-10 11:24:03', 
  '2025-05-13 02:09:03', 
  '{"realName":"高飞","studentId":"20236750","major":"统计学","bio":"热衷于公益事业","preferences":{"interestedCategories":["旅游","公益","金融","美食"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":true},"tags":["自我驱动","沉着冷静","善解人意"],"phone":"13765107269"}'
),
-- 用户13
(
  'user_0013', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0013@example.com',  
  NULL, 
  'admin', 
  '2024-09-08 11:24:41', 
  '2024-09-17 11:24:41', 
  '2024-09-17 11:27:41', 
  '{"realName":"吴丽","studentId":"20235940","major":"汉语言文学","bio":"追求卓越，不断进步","preferences":{"interestedCategories":["育儿","旅游","金融","历史"]},"tags":["抗压能力强","适应力强","自我驱动"],"phone":"13426219488"}'
),
-- 用户14
(
  'user_0014', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0014@example.com',  
  NULL, 
  'user', 
  '2024-08-01 11:24:41', 
  '2024-08-16 11:24:41', 
  '2024-08-16 11:32:41', 
  '{"realName":"林志玲","studentId":"20239062","major":"市场营销","bio":"喜欢探索未知领域","preferences":{"interestedCategories":["阅读","时尚","文化","游戏","体育"]},"tags":["创新思维","耐心细致","善于沟通"],"phone":"13693409160"}'
),
-- 用户15
(
  'user_0015', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0015@example.com',  
  NULL, 
  'user', 
  '2025-04-22 11:24:41', 
  '2025-05-18 11:24:41', 
  '2025-05-18 11:59:41', 
  '{"realName":"赵薇","studentId":"20235338","major":"哲学","bio":"热爱大自然","preferences":{"interestedCategories":["教育","艺术","音乐"]},"tags":["幽默风趣","自我驱动","积极乐观"],"phone":"13428801931"}'
),
-- 用户16
(
  'user_0016', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0016@example.com',  
  NULL, 
  'user', 
  '2024-08-01 11:56:21', 
  '2024-09-09 11:56:21', 
  '2025-02-20 13:43:21', 
  '{"realName":"黄磊","studentId":"20236191","major":"心理学","bio":"享受瑜伽和冥想的平静","preferences":{"interestedCategories":["美食烹饪","游戏","科学","自然"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":true},"tags":["责任心强","适应力强"],"phone":"13573173824"}'
),
-- 用户17
(
  'user_0017', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0017@example.com',  
  NULL, 
  'user', 
  '2024-08-17 11:56:21', 
  '2025-06-03 11:56:21', 
  '2025-06-27 21:20:21', 
  '{"realName":"彭于晏","studentId":"20238197","major":"护理学","bio":"积极向上，乐于学习","preferences":{"interestedCategories":["历史","游戏","运动","时尚","公益"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":false},"tags":["有条不紊","决策果断"],"phone":"13932997341"}'
),
-- 用户18
(
  'user_0018', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0018@example.com',  
  NULL, 
  'user', 
  '2024-08-23 11:56:21', 
  '2025-05-10 11:56:21', 
  '2025-06-29 16:12:21', 
  '{"realName":"彭于晏","studentId":"20239253","major":"药学","bio":"热衷于公益事业","preferences":{"interestedCategories":["音乐","育儿","阅读"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":false},"tags":["富有同情心","幽默风趣","独立思考","细心周到"],"phone":"13475135538"}'
),
-- 用户19
(
  'user_0019', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0019@example.com',  
  NULL, 
  'user', 
  '2025-06-11 11:57:44', 
  '2025-06-24 11:57:44', 
  '2025-06-25 18:43:44', 
  '{"realName":"迪丽热巴","studentId":"20232100","major":"自动化","bio":"热衷于技术创新","preferences":{"interestedCategories":["游戏","宠物","娱乐"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":true},"tags":["独立思考","富有同情心"],"phone":"13148712448"}'
),
-- 用户20
(
  'user_0020', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0020@example.com',  
  NULL, 
  'admin', 
  '2024-07-15 11:57:44', 
  '2025-06-23 11:57:44', 
  '2025-07-02 23:06:44', 
  '{"realName":"刘德华","studentId":"20237404","major":"数学","bio":"对新能源充满兴趣","preferences":{"interestedCategories":["心理健康","投资理财","职场"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":true},"tags":["抗压能力强","富有同情心","开朗外向","积极乐观"],"phone":"13642552693"}'
),
-- 用户21
(
  'user_0021', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0021@example.com',  
  NULL, 
  'admin', 
  '2024-12-28 11:57:44', 
  '2025-06-24 11:57:44', 
  '2025-06-24 16:47:44', 
  '{"realName":"王俊凯","studentId":"20238541","major":"建筑学","bio":"擅长团队协作","preferences":{"interestedCategories":["科学","历史","电影","阅读","手工艺"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":false},"tags":["决策果断"],"phone":"13088509562"}'
),
-- 用户22
(
  'user_0022', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0022@example.com',  
  NULL, 
  'user', 
  '2025-05-11 11:58:06', 
  '2025-05-26 11:58:06', 
  '2025-06-01 19:14:06', 
  '{"realName":"谢霆锋","studentId":"20235848","major":"医学影像学","bio":"善于跨文化交流","preferences":{"interestedCategories":["生活","健康","阅读","投资理财","历史"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":false},"tags":["团队合作","耐心细致","积极乐观"],"phone":"13786425884"}'
),
-- 用户23
(
  'user_0023', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0023@example.com',  
  NULL, 
  'admin', 
  '2024-10-13 11:58:06', 
  '2025-04-16 11:58:06', 
  '2025-06-07 17:19:06', 
  '{"realName":"方圆","studentId":"20231550","major":"社会工作","bio":"擅长解决复杂问题","preferences":{"interestedCategories":["新闻","美食烹饪","动物保护","健康"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":true},"tags":["条理清晰","勇于担当","创新思维","决策果断"],"phone":"13393237011"}'
),
-- 用户24
(
  'user_0024', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0024@example.com',  
  NULL, 
  'admin', 
  '2025-03-06 11:58:06', 
  '2025-04-05 11:58:06', 
  '2025-05-14 12:53:06', 
  '{"realName":"吴丽","studentId":"20235231","major":"体育学","bio":"享受解决复杂问题的过程","preferences":{"interestedCategories":["音乐","育儿"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":true},"tags":["责任心强"],"phone":"13069391672"}'
),
-- 用户25
(
  'user_0025', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0025@example.com',  
  NULL, 
  'admin', 
  '2025-06-15 11:58:28', 
  '2025-06-27 11:58:28', 
  '2025-07-06 00:22:28', 
  '{"realName":"成龙","studentId":"20232088","major":"数据科学与大数据技术","bio":"享受生活，乐于分享","preferences":{"interestedCategories":["美食","职场"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":false},"tags":["自我驱动","积极主动","富有创造力"],"phone":"13014065179"}'
),
-- 用户26
(
  'user_0026', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0026@example.com',  
  NULL, 
  'user', 
  '2024-10-24 11:58:28', 
  '2025-06-06 11:58:28', 
  '2025-06-23 01:35:28', 
  '{"realName":"杨洋","studentId":"20237854","major":"计算机科学","bio":"擅长解决复杂问题","preferences":{"interestedCategories":["美食烹饪"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":false},"tags":["追求完美","富有激情"],"phone":"13235122180"}'
),
-- 用户27
(
  'user_0027', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0027@example.com',  
  NULL, 
  'user', 
  '2024-08-24 11:58:28', 
  '2024-11-04 11:58:28', 
  '2025-01-27 00:14:28', 
  '{"realName":"章子怡","studentId":"20231240","major":"材料科学与工程","bio":"热衷于公益事业","preferences":{"interestedCategories":["哲学","运动","历史","职业发展","户外探险"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":true},"tags":["抗压能力强","团队合作","富有激情","批判性思维"],"phone":"13547384316"}'
),
-- 用户28
(
  'user_0028', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0028@example.com',  
  NULL, 
  'user', 
  '2024-07-10 11:58:58', 
  '2025-02-05 11:58:58', 
  '2025-06-19 14:10:58', 
  '{"realName":"梁朝伟","studentId":"20239765","major":"工商管理","bio":"沉迷于科幻小说","preferences":{"interestedCategories":["科技"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":true},"tags":["高效执行"],"phone":"13635757613"}'
),
-- 用户29
(
  'user_0029', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0029@example.com',  
  NULL, 
  'admin', 
  '2025-02-01 11:58:58', 
  '2025-05-15 11:58:58', 
  '2025-05-28 05:43:58', 
  '{"realName":"蔡华","studentId":"20237462","major":"物理学","bio":"乐于助人，富有同情心","preferences":{"interestedCategories":["历史","数字艺术","游戏","机器人"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":false,"profilePublic":false,"showJoinedClubs":true},"tags":["细心周到","正直诚信"],"phone":"13189869251"}'
),
-- 用户30
(
  'user_0030', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0030@example.com',  
  NULL, 
  'admin', 
  '2025-01-04 11:58:58', 
  '2025-01-27 11:58:58', 
  '2025-02-18 05:04:58', 
  '{"realName":"朱莉","studentId":"20232555","major":"经济学","bio":"喜欢阅读和写作","preferences":{"interestedCategories":["社会"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":false,"profilePublic":false,"showJoinedClubs":true},"tags":["追求完美","自我驱动","创新思维","条理清晰"],"phone":"13738291331"}'
),
-- 用户31
(
  'user_0031', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0031@example.com',  
  NULL, 
  'user', 
  '2024-10-18 11:59:16', 
  '2025-05-23 11:59:16', 
  '2025-06-29 08:15:16', 
  '{"realName":"梁家辉","studentId":"20234123","major":"环境工程","bio":"热衷于学习新技能","preferences":{"interestedCategories":["职场","宠物","金融","历史"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":false},"tags":["灵活应变","高效率","自律"],"phone":"13912345678"}'
),
-- 用户32
(
  'user_0032', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0032@example.com',  
  NULL, 
  'admin', 
  '2025-01-05 11:59:16', 
  '2025-06-01 11:59:16', 
  '2025-07-06 03:40:16', 
  '{"realName":"张家辉","studentId":"20238765","major":"人工智能","bio":"对人工智能充满热情","preferences":{"interestedCategories":["科技","数字艺术","游戏"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":false,"profilePublic":false,"showJoinedClubs":true},"tags":["逻辑清晰","创新思维","批判性思维"],"phone":"13887654321"}'
),
-- 用户33
(
  'user_0033', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0033@example.com',  
  NULL, 
  'user', 
  '2024-09-22 11:59:16', 
  '2025-04-10 11:59:16', 
  '2025-06-15 22:05:16', 
  '{"realName":"古丽娜扎","studentId":"20235678","major":"金融学","bio":"注重个人成长","preferences":{"interestedCategories":["投资理财","健康","教育"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":false},"tags":["责任心强","严谨细致","富有远见"],"phone":"13765432109"}'
),
-- 用户34
(
  'user_0034', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0034@example.com',  
  NULL, 
  'user', 
  '2024-09-07 11:59:36', 
  '2025-03-20 11:59:36', 
  '2025-05-18 19:30:36', 
  '{"realName":"唐嫣","studentId":"20231029","major":"国际经济与贸易","bio":"热衷于极限运动","preferences":{"interestedCategories":["旅行","户外探险","运动","健康"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":false},"tags":["富有冒险精神","乐观向上","积极主动"],"phone":"13698765432"}'
),
-- 用户35
(
  'user_0035', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0035@example.com',  
  NULL, 
  'admin', 
  '2024-11-25 11:59:36', 
  '2025-06-05 11:59:36', 
  '2025-07-07 08:10:36', 
  '{"realName":"杨幂","studentId":"20235567","major":"计算机科学","bio":"热爱编程和篮球","preferences":{"interestedCategories":["科技","游戏","数字艺术"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":true},"tags":["逻辑清晰","学习能力强","高效率","批判性思维"],"phone":"13876543210"}'
),
-- 用户36
(
  'user_0036', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0036@example.com',  
  NULL, 
  'user', 
  '2025-03-01 11:59:36', 
  '2025-06-20 11:59:36', 
  '2025-07-06 15:25:36', 
  '{"realName":"刘德华","studentId":"20239012","major":"音乐学","bio":"享受生活，乐于分享","preferences":{"interestedCategories":["音乐","艺术","电影","娱乐"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":false},"tags":["幽默风趣","善于沟通","开朗外向"],"phone":"13567890123"}'
),
-- 用户37
(
  'user_0037', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0037@example.com',  
  NULL, 
  'user', 
  '2024-07-20 11:59:36', 
  '2025-01-15 11:59:36', 
  '2025-06-01 10:45:36', 
  '{"realName":"周杰伦","studentId":"20234567","major":"美术学","bio":"热衷于艺术创作","preferences":{"interestedCategories":["艺术","摄影","文化","历史"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":true},"tags":["富有创造力","独立思考","追求完美"],"phone":"13789012345"}'
),
-- 用户38
(
  'user_0038', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0038@example.com',  
  NULL, 
  'admin', 
  '2025-04-01 11:59:36', 
  '2025-06-10 11:59:36', 
  '2025-07-05 09:00:36', 
  '{"realName":"林志玲","studentId":"20237890","major":"行政管理","bio":"擅长团队协作","preferences":{"interestedCategories":["职场","教育","社会"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":false},"tags":["组织能力强","善于沟通","执行力强"],"phone":"13901234567"}'
),
-- 用户39
(
  'user_0039', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0039@example.com',  
  NULL, 
  'user', 
  '2024-12-12 11:59:36', 
  '2025-05-01 11:59:36', 
  '2025-06-20 17:50:36', 
  '{"realName":"彭于晏","studentId":"20232345","major":"体育学","bio":"喜欢挑战自我","preferences":{"interestedCategories":["运动","户外探险","健康"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":true},"tags":["自我驱动","积极乐观","适应力强"],"phone":"13023456789"}'
),
-- 用户40
(
  'user_0040', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0040@example.com',  
  NULL, 
  'admin', 
  '2025-02-18 11:59:36', 
  '2025-06-25 11:59:36', 
  '2025-07-07 05:30:36', 
  '{"realName":"迪丽热巴","studentId":"20236789","major":"设计学","bio":"热衷于艺术创作","preferences":{"interestedCategories":["艺术","时尚","摄影","数字艺术"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":false,"profilePublic":false,"showJoinedClubs":false},"tags":["富有创造力","注重细节","追求完美"],"phone":"13198765432"}'
),
-- 用户41
(
  'user_0041', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0041@example.com',  
  NULL, 
  'user', 
  '2024-08-05 11:59:36', 
  '2025-03-01 11:59:36', 
  '2025-06-11 12:15:36', 
  '{"realName":"易烊千玺","studentId":"20233456","major":"新闻学","bio":"喜欢阅读和写作","preferences":{"interestedCategories":["新闻","阅读","历史","文化"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":true},"tags":["逻辑清晰","表达清晰","批判性思维"],"phone":"13210987654"}'
),
-- 用户42
(
  'user_0042', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0042@example.com',  
  NULL, 
  'user', 
  '2025-05-10 11:59:36', 
  '2025-06-20 11:59:36', 
  '2025-07-06 23:40:36', 
  '{"realName":"王俊凯","studentId":"20237654","major":"药学","bio":"热衷于公益事业","preferences":{"interestedCategories":["公益","健康","社会","环保"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":false},"tags":["乐于助人","富有同情心","正直诚信"],"phone":"13345678901"}'
),
-- 用户43
(
  'user_0043', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0043@example.com',  
  NULL, 
  'admin', 
  '2024-10-01 11:59:36', 
  '2025-04-15 11:59:36', 
  '2025-06-28 16:00:36', 
  '{"realName":"古天乐","studentId":"20239988","major":"临床医学","bio":"擅长解决复杂问题","preferences":{"interestedCategories":["科学","健康","医学"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":true},"tags":["沉着冷静","决策果断","抗压能力强","严谨细致"],"phone":"13490123456"}'
),
-- 用户44
(
  'user_0044', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0044@example.com',  
  NULL, 
  'user', 
  '2024-11-08 12:00:01', 
  '2025-05-19 12:00:01', 
  '2025-06-25 07:30:01', 
  '{"realName":"郑秀文","studentId":"20231122","major":"工商管理","bio":"热衷于技术创新","preferences":{"interestedCategories":["商业","金融","职场"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":false},"tags":["创新思维","高效率","决策果断"],"phone":"13911223344"}'
),
-- 用户45
(
  'user_0045', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0045@example.com',  
  NULL, 
  'admin', 
  '2024-07-25 12:00:01', 
  '2025-01-01 12:00:01', 
  '2025-05-10 18:45:01', 
  '{"realName":"梁朝伟","studentId":"20234455","major":"电影","bio":"喜欢阅读和写作","preferences":{"interestedCategories":["电影","艺术","阅读","历史"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":false,"profilePublic":false,"showJoinedClubs":true},"tags":["细心周到","富有创造力","追求完美"],"phone":"13876543210"}'
),
-- 用户46
(
  'user_0046', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0046@example.com',  
  NULL, 
  'user', 
  '2025-03-15 12:00:01', 
  '2025-06-28 12:00:01', 
  '2025-07-06 09:10:01', 
  '{"realName":"章子怡","studentId":"20237788","major":"国际关系","bio":"善于跨文化交流","preferences":{"interestedCategories":["文化","社会","新闻","公益"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":false},"tags":["善于沟通","灵活应变","富有同情心"],"phone":"13700112233"}'
),
-- 用户47
(
  'user_0047', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0047@example.com',  
  NULL, 
  'user', 
  '2024-08-01 12:00:01', 
  '2025-02-10 12:00:01', 
  '2025-06-15 21:20:01', 
  '{"realName":"金城武","studentId":"20239900","major":"哲学","bio":"独立思考，勇于创新","preferences":{"interestedCategories":["哲学","科学","历史","阅读"],"emailNotifications":false,"applicationNotifications":false,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":true},"tags":["独立思考","批判性思维","好奇心强"],"phone":"13622334455"}'
),
-- 用户48
(
  'user_0048', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0048@example.com',  
  NULL, 
  'admin', 
  '2025-04-20 12:00:01', 
  '2025-06-05 12:00:01', 
  '2025-07-07 02:05:01', 
  '{"realName":"舒淇","studentId":"20235678","major":"表演艺术","bio":"享受生活，乐于分享","preferences":{"interestedCategories":["艺术","时尚","美食","旅行"],"emailNotifications":true,"applicationNotifications":true,"activityNotifications":true,"profilePublic":true,"showJoinedClubs":false},"tags":["开朗外向","幽默风趣","善于倾听"],"phone":"13588776655"}'
),
-- 用户49
(
  'user_0049', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0049@example.com',  
  NULL, 
  'user', 
  '2024-10-10 12:00:01', 
  '2025-03-01 12:00:01', 
  '2025-06-20 10:00:01', 
  '{"realName":"周润发","studentId":"20231234","major":"会计学","bio":"擅长解决复杂问题","preferences":{"interestedCategories":["金融","商业","职场","投资理财"],"emailNotifications":true,"applicationNotifications":false,"activityNotifications":false,"profilePublic":true,"showJoinedClubs":true},"tags":["严谨细致","条理清晰","逻辑清晰"],"phone":"13399887766"}'
),
-- 用户50
(
  'user_0050', 
  '$2a$10$GBq4EkE71/./1enmPH5u1e9PsgdhzBuZQ20HcgDhk7r3quWJjq/yK', 
  'user0050@example.com',  
  NULL, 
  'admin', 
  '2025-01-01 12:00:01', 
  '2025-06-15 12:00:01', 
  '2025-07-07 00:15:01', 
  '{"realName":"张曼玉","studentId":"20238877","major":"汉语言文学","bio":"热衷于艺术创作","preferences":{"interestedCategories":["文学","艺术","历史","文化"],"emailNotifications":false,"applicationNotifications":true,"activityNotifications":true,"profilePublic":false,"showJoinedClubs":false},"tags":["富有创造力","追求完美","细心周到"],"phone":"13455667788"}'
); 