# 代码重构计划

## 问题分析

### 1. API 架构重复问题
- **现状**：存在两套 API 系统
  - `src/api/main.py` + `src/api/simple.py` - 简化版（无需认证）
  - `src/api/auth.py` - 完整认证 API（多用户）
- **问题**：架构混乱，维护困难
- **影响**：高优先级

### 2. 数据库模型分散
- **现状**：
  - `src/database/models.py` - 主数据模型（签到、抢券、积分）
  - `src/database/user_models.py` - 用户模型（用户、会话）
- **问题**：模型分散，关系不清晰
- **影响**：高优先级

### 3. CRUD 操作重复
- **现状**：
  - `src/database/crud.py` - 主要 CRUD 操作
  - `src/database/user_crud.py` - 用户相关 CRUD
- **问题**：代码重复，缺乏统一基类
- **影响**：高优先级

## 重构方案

### 阶段 1：统一数据库模型（不影响现有功能）

#### 1.1 创建新的模型文件结构
```
src/database/
├── __init__.py          # 统一导出
├── base.py              # Base、引擎、会话
├── models/
│   ├── __init__.py
│   ├── user.py          # User, UserSession
│   ├── business.py      # CheckinRecord, GrabRecord, PointsRecord
│   └── system.py        # SystemConfig, TaskSchedule
└── crud/
    ├── __init__.py
    ├── base.py          # CRUD 基类
    ├── user.py          # 用户 CRUD
    └── business.py      # 业务 CRUD
```

#### 1.2 迁移步骤
1. 创建新文件结构（保留旧文件）
2. 逐步迁移代码到新结构
3. 测试验证
4. 删除旧文件

### 阶段 2：统一 CRUD 操作

#### 2.1 创建 CRUD 基类
```python
class BaseCRUD(Generic[ModelType]):
    """CRUD 基类，提供通用操作"""
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, id: int) -> Optional[ModelType]:
        ...

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        ...

    def create(self, obj_in: dict) -> ModelType:
        ...

    def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        ...

    def delete(self, id: int) -> bool:
        ...
```

#### 2.2 实现
1. 创建 `src/database/crud/base.py`
2. 重构现有 CRUD 类继承基类
3. 移除重复代码

### 阶段 3：重构 API 系统

#### 3.1 统一 API 入口
```python
# src/api/main.py
app = FastAPI(title="整点抢券")

# 认证中间件（可选）
app.add_middleware(OptionalAuthMiddleware)

# 路由
app.include_router(auth_router, prefix="/api/auth")   # 认证相关
app.include_router(business_router, prefix="/api")    # 业务接口
app.include_router(admin_router, prefix="/api/admin") # 管理接口
```

#### 3.2 实现可选认证
```python
class OptionalAuthMiddleware:
    """可选认证中间件"""
    async def dispatch(self, request, call_next):
        # 尝试从请求头获取用户信息
        # 如果没有 token，使用默认用户或匿名
        ...
```

#### 3.3 业务接口支持两种模式
```python
@app.post("/api/checkin")
async def checkin(
    request: Request,
    data: CookieInput,
    current_user: Optional[User] = Depends(get_optional_user)
):
    # 如果有认证用户，使用用户 Cookie
    # 否则使用请求体中的 Cookie
    ...
```

### 阶段 4：测试验证

#### 4.1 功能测试
- [ ] 用户注册/登录
- [ ] 每日签到
- [ ] 积分查询
- [ ] 抢券功能
- [ ] 历史记录

#### 4.2 性能测试
- [ ] API 响应时间
- [ ] 数据库查询效率

## 执行计划

### 第 1 周：数据库模型统一
- Day 1-2: 创建新文件结构
- Day 3-4: 迁移模型代码
- Day 5: 测试验证

### 第 2 周：CRUD 统一
- Day 1-2: 创建 CRUD 基类
- Day 3-4: 重构现有 CRUD
- Day 5: 测试验证

### 第 3 周：API 重构
- Day 1-2: 实现可选认证中间件
- Day 3-4: 重构业务接口
- Day 5: 测试验证

### 第 4 周：收尾优化
- Day 1-2: 全面测试
- Day 3: 文档更新
- Day 4: 代码清理
- Day 5: 部署上线

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 数据库迁移失败 | 高 | 备份数据库，分步迁移 |
| API 兼容性破坏 | 高 | 保留旧接口，逐步废弃 |
| 功能回归 | 中 | 完善单元测试和集成测试 |
| 性能下降 | 低 | 性能基准测试 |

## 成功标准

- ✅ 单一的数据库模型文件结构
- ✅ 统一的 CRUD 基类
- ✅ 单一的 API 入口，认证可选
- ✅ 所有功能测试通过
- ✅ 代码行数减少 20% 以上
- ✅ 无性能下降

## 备注

- 重构过程中保持向后兼容
- 优先保证功能稳定性
- 代码审查是必需环节
