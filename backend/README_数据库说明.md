# 数据库配置说明

## 多项目共存

本项目的数据库配置在 `app/config.py` 中，使用独立的数据库名，不会与其他项目冲突。

### 当前项目配置
- **数据库名**: `victor_english`
- **配置文件**: `backend/app/config.py`

### 如何切换不同项目

#### 方法1：修改配置文件（推荐用于开发）

直接修改 `app/config.py` 中的 `DB_NAME`：

```python
DB_NAME = os.getenv("DB_NAME", "victor_english")  # 改为你需要的数据库名
```

#### 方法2：使用环境变量（推荐用于生产环境）

在启动服务前设置环境变量：

```bash
# 使用 victor_english 数据库（当前项目）
export DB_NAME=victor_english
python3 main.py

# 或者使用其他数据库
export DB_NAME=my_app
python3 main.py
```

#### 方法3：创建不同的启动脚本

为不同项目创建不同的启动脚本：

**启动 victor-英语 项目：**
```bash
cd <project-directory>
export DB_NAME=victor_english
python3 main.py
```

**启动 10后创业星球 项目：**
```bash
cd <project-directory>
export DB_NAME=my_app
python3 main.py
```

## 数据库列表

你的MySQL服务器上可能有多个数据库：

1. **mysql** - MySQL系统数据库（不要删除）
2. **my_app** - 10后创业星球项目的数据库
3. **victor_english** - victor-英语项目的数据库

每个项目使用不同的数据库，完全独立，互不干扰。

## 注意事项

1. ✅ 两个项目可以同时存在，使用不同的数据库名
2. ✅ 启动时会自动创建数据库（如果不存在）
3. ✅ 每个项目的表结构独立，不会互相影响
4. ⚠️ 确保不同项目使用不同的数据库名
5. ⚠️ 不要删除 `mysql` 系统数据库

## 验证当前使用的数据库

运行以下命令查看当前配置：

```bash
cd backend
python3 check_db.py
```

或启动服务时查看日志输出。

