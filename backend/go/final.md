# Go 部分后端说明

## 负责模块

- 数据库表设计
- 系统基础功能服务器开发（管理系统逻辑，以及对 LLM、RAG 等微服务器反向代理）
- 邮箱验证码发送服务器开发
- 数据库及上述两种服务器上云、代理部署。

## 关键功能

### 数据库表设计

后端数据库基于 PostgreSQL 设计，针对需求优化字段

#### 实现

```sql
CREATE TABLE categories (
  category_id INT PRIMARY KEY DEFAULT nextval('categories_category_id_seq'),
  name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
  user_id INT PRIMARY KEY DEFAULT nextval('users_user_id_seq'),
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash CHAR(60) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  avatar_url VARCHAR(255),
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clubs (
  club_id INT PRIMARY KEY DEFAULT nextval('clubs_club_id_seq'),
  name VARCHAR(100) NOT NULL,
  leader_id INT NOT NULL REFERENCES users(user_id),
  category_id INT NOT NULL REFERENCES categories(category_id),
  description TEXT NOT NULL,
  logo_url VARCHAR(255),
  member_count INT NOT NULL DEFAULT 0,
  requirements TEXT,
  tags JSONB,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE club_members (
  member_id INT PRIMARY KEY DEFAULT nextval('club_members_member_id_seq'),
  user_id INT NOT NULL REFERENCES users(user_id),
  club_id INT NOT NULL REFERENCES clubs(club_id),
  role_in_club VARCHAR(20) NOT NULL DEFAULT 'member',
  joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE club_posts (
  post_id INT PRIMARY KEY DEFAULT nextval('club_posts_post_id_seq'),
  club_id INT NOT NULL REFERENCES clubs(club_id),
  user_id INT NOT NULL REFERENCES users(user_id),
  title VARCHAR(120) NOT NULL,
  content_url TEXT NOT NULL,
  comment_count INT NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE club_post_comments (
  comment_id INT PRIMARY KEY DEFAULT nextval('post_comments_comment_id_seq'),
  post_id INT NOT NULL REFERENCES club_posts(post_id),
  user_id INT NOT NULL REFERENCES users(user_id),
  content TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE join_club_applications (
  join_appli_id INT PRIMARY KEY DEFAULT nextval('club_applications_application_id_seq'),
  user_id INT NOT NULL REFERENCES users(user_id),
  club_id INT NOT NULL REFERENCES clubs(club_id),
  applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  status VARCHAR(20) NOT NULL DEFAULT 'pending'
);

CREATE TRIGGER trg_update_member_count
AFTER INSERT OR DELETE ON club_members
FOR EACH ROW EXECUTE PROCEDURE update_club_member_count();

CREATE TRIGGER trg_update_comment_count
AFTER INSERT OR DELETE ON club_post_comments
FOR EACH ROW EXECUTE PROCEDURE update_post_comment_count();

CREATE FUNCTION update_club_member_count() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE clubs SET member_count = member_count + 1 WHERE club_id = NEW.club_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE clubs SET member_count = member_count - 1 WHERE club_id = OLD.club_id;
  END IF;
  RETURN NULL;
END; 
$$ LANGUAGE plpgsql;

CREATE FUNCTION update_post_comment_count() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE club_posts SET comment_count = comment_count + 1 WHERE post_id = NEW.post_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE club_posts SET comment_count = comment_count - 1 WHERE post_id = OLD.post_id;
  END IF;
  RETURN NULL;
END; 
$$ LANGUAGE plpgsql;
```

#### 说明

##### 核心实体表

| 表名 | 说明 |
|------|------|
| `users` | 用户表（存储系统用户信息） |
| `categories` | 分类表（社团分类） |
| `clubs` | 社团主表（存储所有社团信息） |

##### 关系表

| 表名 | 说明 |
|------|------|
| `club_members` | 社团成员关系表（用户与社团的多对多关系） |
| `club_favorites` | 社团收藏表（用户收藏的社团） |

##### 内容表

| 表名 | 说明 |
|------|------|
| `club_posts` | 社团帖子表 |
| `club_post_comments` | 帖子评论表 |

##### 申请流程表

| 表名 | 说明 |
|------|------|
| `join_club_applications` | 加入社团申请表 |
| `create_club_applications` | 创建社团申请表 |
| `update_club_info_applications` | 社团信息修改申请表 |

#### 表关系示意图

```text
users
├─┬ club_members → clubs
│ ├─ club_favorites
│ └─┬ join_club_applications
│   └─ create_club_applications
│
clubs
├── club_posts → club_post_comments
│
categories → clubs
```

#### 补充

- `clubs.tags` 使用JSONB存储灵活标签
- 各类申请表的 `proposal` 字段使用JSONB存储结构化数据，提供扩展可能

### 前端文件代理

为简便起见，直接使用 Nginx 在网关层代理 Vue3 生成的静态文件

### Base Server 设计

包含所有系统非 LLM 和 RAG 部分的系统管理核心功能；同时提供鉴权、过滤等功能，作为网关反向代理 LLM 和 RAG 服务器；基于 Redis、gRPC 进行跨服务通信

#### Base Server 配置项

提供了快捷修改核心配置的能力，且使用 Viper 保留了热更新配置的扩展空间

```json
{
  "env_level": "debug",
  "server_port": 8080,
  "database": {
    "dsn": "postgresql://server_user:xxxxxx@xxxxxxxxx:5432/whuclubsynapse?connect_timeout=10&sslmode=disable&application_name=auth_server&search_path=public&client_encoding=UTF8&timezone=UTC"
  },
  "redis": {
    "host": "8.141.92.242",
    "port": 6379,
    "password": "xxxxxxxxx",
    "db": 0,
    "max_conn": 10,
    "min_idle": 3,
    "max_retries": 3
  },
  "grpc": {
    "host": "localhost",
    "port": 50051,
    "max_conn": 5,
    "min_conn": 1,
    "idle_timeout": 60
  },
  "jwt": {
    "expiration_time": 24,
    "secret_key": "priestess"
  },
  "llm": {
    "addr": "https://6a52-125-220-159-5.ngrok-free.app"
  },
  "rag": {
    "addr": "http://7c3dc0cb.r36.cpolar.top"
  }
}
```

#### 设计思路

- 使用 Go 开发，确保不出现性能瓶颈
- 将核心逻辑封装在 repo 层，从数据库查询层面提升操作效率
- 处理申请等时的复杂跨表操作基于 gorm.DB 上下文封装事务
- 对上传文件等操作协调 OS 和数据库事务

#### 核心接口概览

```text
API 接口层次分类 (共58个路由)

================ 核心功能模块 ================
1. 用户系统
   POST   /auth/login               用户登录
   POST   /auth/register            用户注册
   POST   /auth/verify              邮箱验证
   GET    /auth/my_info             获取当前用户信息
   GET    /api/user/{id}            获取用户信息
   GET    /api/user/list            用户列表
   PUT    /api/user/update          更新用户信息
   POST   /api/user/upload_avatar   上传头像

2. 社团系统
   GET    /api/club/list             社团列表
   GET    /api/club/{id}/info        社团详情
   GET    /api/club/categories       分类列表
   GET    /api/club/category/{catId} 按分类查询
   GET    /api/club/my_clubs         我加入的社团
   GET    /api/club/my_favorites     我的收藏

3. 内容系统
   GET    /api/club/post/posts/{id}    社团帖子列表
   GET    /api/club/post/pinned/{id}   置顶帖子
   GET    /api/club/post/comments/{id} 帖子评论
   POST   /api/club/post/create        创建帖子
   POST   /api/club/post/comment       发表评论

================ 申请审批流程 ================
1. 加入/创建流程
   POST   /api/club/{id}/join       申请加入社团
   POST   /api/club/create          申请创建社团
   POST   /api/club/pub/update/{id} 申请修改社团信息

2. 审批处理
   PUT    /api/club/pub/proc_join     处理加入申请
   PUT    /api/club/admin/proc_create 处理创建申请
   PUT    /api/club/admin/proc_update 处理修改申请

================ 管理功能 ================
1. 内容管理
   PUT    /api/club/post/pub/pin/{id} 置顶帖子
   PUT    /api/club/post/pub/ban/{id} 禁用帖子

2. 申请管理
   GET    /api/club/admin/create_list 创建申请列表
   GET    /api/club/admin/update_list 修改申请列表

================ 辅助功能 ================
1. 文件服务
   GET    /pub/user_avatars/{file} 用户头像
   GET    /pub/club_logos/{file}   社团LOGO
   GET    /pub/post_files/{file}   帖子内容

2. AI服务
   GET/POST /api/trans/llm/{route} LLM交互
   GET/POST /api/trans/rag/{route} RAG检索

================ 个人中心 ================
   GET    /api/club/my_joinapplis    我的加入申请
   GET    /api/club/my_createapplis  我的创建申请
   GET    /api/club/my_update_applis 我的修改申请
   POST   /api/club/favorite         收藏社团
   POST   /api/club/unfavorite       取消收藏
```

#### 转发 LLM 和 RAG 部分实现

- 复用 Redis Streams，转发 Club 和 Post 的信息供两者向量化或缓存，做到异步解耦获取数据

```go
func (s *sRedisClientService) UploadClubInfo(clubInfo *dbstruct.Club) error {
  s.logger.Debug("上传社团信息", "club", clubInfo)

  // 防止超时
  ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
  defer cancel()

  strClubId := strconv.Itoa(int(clubInfo.ClubId))
  if strClubId == "" {
    return errors.New("无法转化club_id为字符串")
  }

  // 传输检索时的元数据
  metadataJson, err := json.Marshal(map[string]any{
    "name":         clubInfo.Name,
    "description":  clubInfo.Description,
    "requirements": clubInfo.Requirements,
    "tags":         clubInfo.Tags,
    "category":     clubInfo.CategoryId,
  })
  if err != nil {
    return err
  }

  // 向流中线程安全地推送
  cmd := s.client.Inst().XAdd(ctx, &redis.XAddArgs{
    Stream: "rag_sync_stream",
    Values: map[string]any{
      "source_id": "club_id::" + strClubId,
      "content":   clubInfo.Description,
      "metadata":  string(metadataJson),
    },
  })

  msgId, err := cmd.Result()
  if err != nil {
    s.logger.Error("Redis操作异常", "error", err)
    return err
  }

  s.logger.Info("上传社团信息成功", "msg_id", msgId)

  return nil
}
```

- 客户端即时请求时，响应采用 SSE 转发提升用户体验（针对 SSE event 的换行符特性，使用 Scanner优化无缓冲发送）

```go
// 尝试获取 Flusher 接口
flusher, ok := ctx.ResponseWriter().(http.Flusher)
if !ok {
  h.Logger.Error("ResponseWriter不支持Flush，无法进行SSE转发")
  http.Error(ctx.ResponseWriter(), "Streaming unsupported!", http.StatusInternalServerError)
  return
}

scanner := bufio.NewScanner(res.Body)
for scanner.Scan() {
  line := scanner.Bytes()
  // 将读取到的行直接写入到下游客户端，并添加换行符以保持SSE格式
  if _, writeErr := ctx.ResponseWriter().Write(append(line, '\n')); writeErr != nil {
    h.Logger.Error("SSE转发写入下游客户端错误", "error", writeErr)
    // 如果写入下游客户端失败，通常表示客户端断开，此时应退出循环
    break
  }
  // 每次写入一行后立即刷新，确保数据实时发送
  flusher.Flush()
}

// 检查Scanner是否在读取过程中遇到了错误（除了io.EOF）
if err := scanner.Err(); err != nil {
  h.Logger.Error("从上游SSE读取数据时发生错误", "error", err)
} else {
  // 如果没有错误，且循环结束，意味着上游SSE流已优雅关闭或数据已传输完毕
  h.Logger.Debug("上游SSE流已优雅结束或数据传输完毕")
}
```

### Email Verification Code Server 设计

微服务，专门提供本地的邮箱验证码发送功能

#### Email Verification Code Server 配置项

```json
{
    "email": {
        "user": "xxxxxxxxx@163.com",
        "password": "xxxxxxxx"
    },
    "redis": {
        "host": "127.0.0.1",
        "port": 6379,
        "password": "xxxxxxx"
    }
}
```

#### Email Verification Code Server 设计思路

- 使用 Node.js 开发，保证并发性能
- 使用 nodemail 实现核心的发送邮箱验证码功能
- 使用 gRPC 供 Base Server 调用
- 检验不存在重复发送后，将验证码结果异步存入 Redis，供跨服务器共享信息

#### 关键实现

```javascript
/**
 * @param req 等于GetVerifyRequest
 * @param rsp 等于GetVerifyResponse
 */
async function GetVerifyCode(req, rsp) {
    console.log("目标email为：", req.request.email);
    try {
        // 以 “vrfcode_{email}” 作为 key 值存在 redis，返回值是对应的验证码
        let get_result
            = await redis_module.GetRedis(
                CONST_MOD.CODE_PREFIX + req.request.email);
        console.log("查询该email的结果为: ", get_result);

        let uuid;
        // 如果 get_result 为空，则说明之前没有对该邮箱发送验证码
        // 补充一个 uuid 再进行下面的步骤
        if (get_result == null) {
            // 生成一个新 uuid 到 redis 中
            uuid = uuidv4();
            if (uuid.length > 4) {
                uuid = uuid.substring(0, 4);
            }
            let expire_result
                = await redis_module.SetRedisExpire(
                    CONST_MOD.CODE_PREFIX + req.request.email,
                    uuid,
                    180
                );
            // 当设置时限失败则直接返回
            if (!expire_result) {
                rsp(
                    null,
                    {
                        email: req.request.email,
                        error: CONST_MOD.EnumError.ErrorRedis
                    }
                );
                return;
            }

            console.log("uuid新建: ", uuid)
        }

        console.log("uuid为: ", uuid);
        let str_text
            = req.request.email + '的验证码为：' + uuid
            + ', 请在三分钟内完成验证';
        //发送邮件
        let mail_options = {
            from: CONFIG_MOD.EMAIL_USR,
            to: req.request.email,
            subject: 'Verification code',
            text: str_text
        };

        let send_result
            = await AsyncSendMail(mail_options);
        console.log("邮件发送结果为：", send_result);

        // 如果发送邮件失败，也直接返回
        if (!send_result) {
            rsp(
                null,
                {
                    email: req.request.email,
                    error: CONST_MOD.EnumError.ErrorSend
                }
            );
            return;
        }
        rsp(
            null,
            {
                email: req.request.email,
                error: CONST_MOD.EnumError.Success
            }
        );

    } catch (exp) {
        console.log("GetVerifyCode函数处异常：", exp);

        rsp(
            null,
            {
                email: req.request.email,
                error: CONST_MOD.EnumError.Exception
            }
        );
    }
}
```
