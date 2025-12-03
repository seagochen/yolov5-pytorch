# 周易占卜前端

基于 React + TypeScript + Vite 构建的现代化周易占卜界面。

## 技术栈

- **React 18** - 现代化的UI框架
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速的构建工具
- **Axios** - HTTP客户端
- **CSS3** - 优雅的中国传统风格设计

## 功能特性

1. **随机占卜** - 用户输入问题后，系统随机生成6位数字进行占卜
2. **卦象展示** - 显示本卦、变卦及其详细信息（卦名、卦辞、爻辞等）
3. **AI解卦** - 集成AI分析，提供专业的卦象解读
4. **响应式设计** - 支持桌面和移动设备

## 界面设计

采用典雅的中国传统配色方案：
- 主色调：#CCD5AE（艾绿）
- 次色调：#E9EDC9（月白）
- 浅色：#FEFAE0（象牙白）
- 强调色：#FAEDCD（杏黄）
- 深色：#D4A373（驼色）

界面布局采用居中设计，左右留白，营造专注的占卜氛围。

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## 项目结构

```
src/
├── api/          # API客户端
├── types/        # TypeScript类型定义
├── App.tsx       # 主应用组件
├── App.css       # 样式文件
├── index.css     # 全局样式
└── main.tsx      # 应用入口
```

## API集成

前端通过以下API与后端通信：

- `POST /api/divination/random` - 随机占卜
- `POST /api/interpretation/analyze` - AI解卦

开发环境配置了代理，自动转发API请求到 `http://localhost:8000`。

## 环境变量

创建 `.env` 文件配置API地址：

```
VITE_API_URL=http://localhost:8000
```

## 浏览器支持

支持所有现代浏览器：
- Chrome / Edge (最新版本)
- Firefox (最新版本)
- Safari (最新版本)

## License

MIT
