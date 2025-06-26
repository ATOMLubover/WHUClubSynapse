# 后端架构建议

## 服务层设计

### ClubService.js

```javascript
class ClubService {
  /**
   * 获取社团列表
   * @param {Object} params 查询参数
   * @param {string} userId 用户ID（可选）
   * @returns {Object} 社团列表数据
   */
  async getClubList(params, userId = null) {
    const { page = 1, pageSize = 10, category, sortBy = 'hot', includeUserData = false } = params;
    
    // 基础查询 - 获取社团基本信息
    let query = `
      SELECT c.id, c.name, c.description, c.cover_image, c.category,
             c.current_members, c.max_members, c.tags, c.is_hot,
             c.created_at, u.username as admin_name
      FROM clubs c
      LEFT JOIN users u ON c.admin_id = u.id
      WHERE 1=1
    `;
    
    const queryParams = [];
    
    // 添加分类筛选
    if (category) {
      query += ` AND c.category = ?`;
      queryParams.push(category);
    }
    
    // 添加排序
    switch (sortBy) {
      case 'time':
        query += ` ORDER BY c.created_at DESC`;
        break;
      case 'members':
        query += ` ORDER BY c.current_members DESC`;
        break;
      default: // 'hot'
        query += ` ORDER BY c.is_hot DESC, c.current_members DESC`;
    }
    
    // 分页
    query += ` LIMIT ? OFFSET ?`;
    queryParams.push(pageSize, (page - 1) * pageSize);
    
    const clubs = await db.query(query, queryParams);
    
    // 如果用户已登录且需要用户数据，则补充用户相关信息
    if (userId && includeUserData) {
      await this.enrichClubsWithUserData(clubs, userId);
    }
    
    // 获取总数
    const countQuery = `SELECT COUNT(*) as total FROM clubs c WHERE 1=1 ${category ? 'AND c.category = ?' : ''}`;
    const countParams = category ? [category] : [];
    const [{ total }] = await db.query(countQuery, countParams);
    
    return {
      list: clubs,
      total,
      page: parseInt(page),
      pageSize: parseInt(pageSize)
    };
  }
  
  /**
   * 为社团列表补充用户相关数据（收藏状态、申请状态等）
   * @param {Array} clubs 社团列表
   * @param {string} userId 用户ID
   */
  async enrichClubsWithUserData(clubs, userId) {
    if (!clubs.length) return;
    
    const clubIds = clubs.map(club => club.id);
    
    // 批量查询收藏状态
    const favoriteQuery = `
      SELECT club_id FROM favorites 
      WHERE user_id = ? AND club_id IN (${clubIds.map(() => '?').join(',')})
    `;
    const favorites = await db.query(favoriteQuery, [userId, ...clubIds]);
    const favoriteSet = new Set(favorites.map(f => f.club_id));
    
    // 批量查询申请状态
    const applicationQuery = `
      SELECT club_id, status FROM user_clubs 
      WHERE user_id = ? AND club_id IN (${clubIds.map(() => '?').join(',')})
    `;
    const applications = await db.query(applicationQuery, [userId, ...clubIds]);
    const applicationMap = new Map(applications.map(a => [a.club_id, a.status]));
    
    // 为每个社团补充用户数据
    clubs.forEach(club => {
      club.isFavorite = favoriteSet.has(club.id);
      club.status = applicationMap.get(club.id) || 'not_applied';
    });
  }
}
```

### 控制器层设计

```javascript
class ClubController {
  /**
   * 获取社团列表
   */
  async getClubList(req, res) {
    try {
      const { includeUserData } = req.query;
      const userId = req.user?.id; // 从JWT中获取用户ID
      
      // 如果需要用户数据但用户未登录，返回错误
      if (includeUserData === 'true' && !userId) {
        return res.status(401).json({
          code: 401,
          message: '需要登录才能获取个人相关数据'
        });
      }
      
      const result = await clubService.getClubList(req.query, userId);
      
      res.json({
        code: 200,
        message: '获取成功',
        data: result
      });
    } catch (error) {
      console.error('获取社团列表失败:', error);
      res.status(500).json({
        code: 500,
        message: '服务器内部错误'
      });
    }
  }
}
```

## 中间件设计

### 认证中间件

```javascript
const authMiddleware = (required = false) => {
  return (req, res, next) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (token) {
      try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded;
      } catch (error) {
        if (required) {
          return res.status(401).json({
            code: 401,
            message: '无效的认证token'
          });
        }
      }
    } else if (required) {
      return res.status(401).json({
        code: 401,
        message: '缺少认证token'
      });
    }
    
    next();
  };
};
```

## 路由设计

```javascript
// 社团相关路由
router.get('/clubs', authMiddleware(false), clubController.getClubList);
router.get('/clubs/:id', authMiddleware(false), clubController.getClubDetail);
router.post('/clubs/:id/favorite', authMiddleware(true), clubController.favoriteClub);
router.delete('/clubs/:id/favorite', authMiddleware(true), clubController.unfavoriteClub);
router.post('/clubs/apply', authMiddleware(true), clubController.applyToClub);
```

## 性能优化建议

### 1. 数据库索引优化

```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_clubs_category ON clubs(category);
CREATE INDEX idx_clubs_is_hot ON clubs(is_hot);
CREATE INDEX idx_clubs_created_at ON clubs(created_at);
CREATE INDEX idx_clubs_current_members ON clubs(current_members);

-- 复合索引
CREATE INDEX idx_clubs_category_hot ON clubs(category, is_hot);
```

### 2. 缓存策略

```javascript
// Redis缓存热门社团列表
const CACHE_KEYS = {
  HOT_CLUBS: 'hot_clubs',
  CLUB_CATEGORIES: 'club_categories',
  CLUB_LIST: (params) => `club_list:${JSON.stringify(params)}`
};

class ClubService {
  async getHotClubs(limit = 10) {
    // 先从缓存获取
    const cached = await redis.get(CACHE_KEYS.HOT_CLUBS);
    if (cached) {
      return JSON.parse(cached).slice(0, limit);
    }
    
    // 缓存未命中，从数据库获取
    const hotClubs = await this.fetchHotClubsFromDB(limit);
    
    // 缓存结果（30分钟过期）
    await redis.setex(CACHE_KEYS.HOT_CLUBS, 1800, JSON.stringify(hotClubs));
    
    return hotClubs;
  }
}
```

### 3. API响应优化

```javascript
// 数据传输优化 - 根据客户端需求返回不同字段
const getResponseFields = (includeUserData, isLoggedIn) => {
  const baseFields = [
    'id', 'name', 'description', 'coverImage', 'category',
    'adminName', 'currentMembers', 'maxMembers', 'tags',
    'isHot', 'createdAt'
  ];
  
  if (includeUserData && isLoggedIn) {
    return [...baseFields, 'isFavorite', 'status'];
  }
  
  return baseFields;
};
```

## 安全建议

### 1. 参数验证

```javascript
const validateClubListParams = (req, res, next) => {
  const { page, pageSize, category, sortBy } = req.query;
  
  // 验证分页参数
  if (page && (!Number.isInteger(+page) || +page < 1)) {
    return res.status(400).json({
      code: 400,
      message: '无效的页码参数'
    });
  }
  
  if (pageSize && (!Number.isInteger(+pageSize) || +pageSize < 1 || +pageSize > 100)) {
    return res.status(400).json({
      code: 400,
      message: '无效的页面大小参数'
    });
  }
  
  // 验证分类参数
  const validCategories = ['学术科技', '文艺体育', '志愿服务', '创新创业', '其他'];
  if (category && !validCategories.includes(category)) {
    return res.status(400).json({
      code: 400,
      message: '无效的分类参数'
    });
  }
  
  // 验证排序参数
  const validSortBy = ['hot', 'time', 'members'];
  if (sortBy && !validSortBy.includes(sortBy)) {
    return res.status(400).json({
      code: 400,
      message: '无效的排序参数'
    });
  }
  
  next();
};
```

### 2. 限流保护

```javascript
const rateLimit = require('express-rate-limit');

// 对获取社团列表接口进行限流
const clubListLimiter = rateLimit({
  windowMs: 1 * 60 * 1000, // 1分钟
  max: 100, // 每分钟最多100次请求
  message: {
    code: 429,
    message: '请求过于频繁，请稍后再试'
  }
});

router.get('/clubs', clubListLimiter, authMiddleware(false), validateClubListParams, clubController.getClubList);
```

这个架构设计的核心优势：

1. **灵活性**：根据用户登录状态返回不同数据，避免未登录用户获取到无意义的字段
2. **性能**：通过索引优化、缓存策略和按需加载提高响应速度
3. **安全性**：完善的参数验证、认证机制和限流保护
4. **扩展性**：模块化设计，便于后续功能扩展
5. **用户体验**：未登录用户仍能浏览基本信息，登录后获得完整功能 