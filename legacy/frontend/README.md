# AI English Lab - 英语学习网站 App

基于 uni-app 框架开发的英语学习应用，支持公立学校模式和国际学校模式两种学习路径。

## 项目结构

```
pages/
├── home/
│   └── index.vue          # 第1页：首页-模式选择
├── public/
│   ├── grade-select.vue    # 第2页：公立模式-年级与教材选择
│   └── practice.vue        # 第3页：公立模式-基础练习做题
├── international/
│   ├── test.vue           # 第4页：国际模式-分级测试
│   └── path.vue           # 第5页：国际模式-AI学习路径与教练
└── mylearning/
    └── index.vue          # 第6页：我的学习总览
```

## 功能特性

### 1. 全局底部导航栏（TabBar）
- Home：首页模式选择
- Public：公立学校模式
- International：国际学校模式
- My Learning：我的学习总览

### 2. 公立学校模式
- 年级与教材选择
- 按单元出题练习
- 错题本功能
- 基础词汇与语法训练

### 3. 国际学校模式
- 分级测试（A1-C1）
- AI 推荐学习路径
- 学习模块管理
- AI 学习教练对话

### 4. 我的学习
- 学习进度总览
- 本周练习打卡
- 错题本与生词本入口

## 开始使用

### 前置要求
- 已安装 HBuilderX 或配置好 uni-app 开发环境
- Node.js 环境

### 安装步骤

1. **添加 TabBar 图标**
   
   在 `static/tabbar/` 目录下添加以下图标文件：
   - `home.png` / `home-active.png`
   - `public.png` / `public-active.png`
   - `international.png` / `international-active.png`
   - `learning.png` / `learning-active.png`
   
   详细说明请查看 `static/tabbar/README.md`

2. **运行项目**
   
   ```bash
   # 使用 HBuilderX 打开项目，选择运行到浏览器/小程序/App
   # 或使用命令行（如果已配置）
   npm run dev:h5
   ```

## 设计风格

- **主题**：极简文艺风
- **主色调**：墨绿色 (#2F5D62)
- **背景色**：浅暖色 (#F8F6F2)
- **字体**：无衬线字体，细线条风格

## 数据存储

应用使用 `uni.setStorageSync` 和 `uni.getStorageSync` 进行本地数据存储：

- `practiceInfo`: 公立模式练习信息（年级、教材、单元）
- `testResult`: 国际模式分级测试结果
- `testCompleted`: 测试完成状态
- `wrongBook`: 错题本数据

## 页面路由

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | `/pages/home/index` | 模式选择页 |
| 公立-选择 | `/pages/public/grade-select` | 年级与教材选择 |
| 公立-练习 | `/pages/public/practice` | 基础练习做题 |
| 国际-测试 | `/pages/international/test` | 分级测试 |
| 国际-路径 | `/pages/international/path` | AI学习路径与教练 |
| 我的学习 | `/pages/mylearning/index` | 学习总览 |

## 开发说明

### Mock 数据
当前使用前端假数据模拟：
- 练习题目（`pages/public/practice.vue`）
- 测试题目（`pages/international/test.vue`）
- 学习模块（`pages/international/path.vue`）

后续需要接入真实的后端 API 和 AI 服务。

### 待完善功能
- [ ] 错题本详细页面
- [ ] 生词本功能
- [ ] AI 对话真实接口对接
- [ ] 学习进度统计
- [ ] 用户登录与数据同步

## 技术栈

- **框架**：uni-app
- **语言**：Vue 2
- **样式**：CSS / rpx 响应式单位
- **存储**：uni.storage（本地存储）

## 注意事项

1. TabBar 图标必须添加，否则应用无法正常运行
2. 所有页面数据目前使用本地存储，刷新会丢失
3. 部分功能（如错题本、生词本）目前仅显示占位，待后续开发

## 许可证

MIT


