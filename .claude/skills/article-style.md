# /article-style - 公众号文章风格规范

适用于所有 daily_tech 公众号文章。写作、排版、配图前先对照此文档，保证每篇文章风格一致、质量稳定。

---

## 一、CSS 合规（微信限制）

微信公众号**禁用 `<style>` 块**，所有样式必须内联。

### 强制规则

| 规则 | 正确 | 错误 |
|------|------|------|
| 颜色格式 | `#ffffff` | `white`、`rgb(255,255,255)` |
| 样式位置 | `style="..."` 内联 | `<style>` 块 |
| 字体栈 | `-apple-system,'PingFang SC','Microsoft YaHei',sans-serif` | `system-ui`、`Inter` |
| 宽度上限 | `max-width:677px` | 超过 677px 会截断 |
| 外链资源 | 禁止引用外部 CSS/JS | `<link>`、`<script>` 均无效 |
| 图片路径 | 微信 CDN URL（发布时替换） | 本地路径 `/img/...` |

### 常用内联样式片段

```html
<!-- 正文容器 -->
<div style="max-width:677px;margin:0 auto;padding:24px 16px 60px;">

<!-- 正文段落 -->
<p style="margin:0 0 18px;font-size:15px;line-height:2.0;color:#333;">

<!-- 二级标题 -->
<h2 style="font-size:18px;font-weight:bold;color:#1a1a1a;margin:40px 0 16px;padding-left:14px;border-left:4px solid {主题色};">

<!-- 引言块 -->
<div style="font-size:15px;color:#4a4a4a;background:{主题色浅};border-left:4px solid {主题色};padding:16px 20px;margin:0 0 32px;line-height:1.9;border-radius:0 8px 8px 0;">

<!-- 代码块 -->
<div style="background:#1e1e2e;border-radius:8px;padding:16px 18px;margin:16px 0;font-family:'SF Mono','Fira Code',monospace;font-size:12px;line-height:1.9;overflow-x:auto;word-break:break-all;">

<!-- 标签胶囊 -->
<span style="display:inline-block;background:{主题色浅};border:1px solid {主题色边框};border-radius:20px;padding:4px 14px;font-size:12px;color:{主题色};font-weight:bold;letter-spacing:2px;">
```

---

## 二、整体风格

### 定位与语气

- **定位**：面向有一定技术背景的产品、运营、创业者，不是纯开发者
- **语气**：有立场、敢判断，但不煽情、不标题党
- **节奏**：开门见山 → 分层论证 → 给出行动建议 → 诚实说局限
- **字数**：深度分析文 2500~4000 字；资讯摘要类 800~1500 字

### 文章结构模板（深度分析文）

```
标签行（1~2 个主题标签）
标题
装饰分隔线
引言块（1 段，点明核心判断）

一、正在发生的事（事实层）
二、[品牌/开发者/行业] 面对的真实问题（分析层）
三、[方案/对比/路径]（方案层）
四、值得做的 N 件事（行动层）
五、[某个值得深入讨论的争议点]（批判层）

结语（· · · + 1~2 段）
结语深色块（核心观点凝练，1~2 句话）
标签行 + 参考来源
```

### 禁止出现的内容

- 文章内不出现写作过程方法（红队测试、prompt 技巧、审查流程等）
- 不引用自己的写作辅助工具或 AI 提示词
- 不使用「笔者认为」「本文将」等论文腔
- 不以「总结一下」「综上所述」结尾

---

## 三、配色方案

每篇文章选定一个主题色，全文统一使用。主题色决定：标题左边框、引言块、强调文字、标签、SVG 图表高亮色。

### 已用配色

| 文章类型 | 主题色 | 浅背景 | 边框色 | 使用场景 |
|---------|--------|--------|--------|---------|
| 茶饮/消费品牌 | `#C8965A` 暖棕金 | `#fdf6ed` | `#e8d5b0` | agent-distribution 文章 |
| 淘宝/电商技术 | `#6B4CA8` 紫色 | `#f3f0fa` | `#c9b8e8` | taobao-native 文章 |
| 工程/工具类 | `#2D7D46` 深绿 | `#f0f7f2` | `#b8ddc4` | 建议用于 Dev 工具类 |
| 模型/AI研究 | `#1A6FA8` 科技蓝 | `#f0f6fc` | `#b8d8f0` | 建议用于模型分析类 |

**选色原则：** 消费/品牌类用暖色，工程/工具类用冷色，同系列文章用同一套配色。

---

## 四、图表规范

### SVG 内联图（优先选择）

适用于：流程对比、分层架构、指标说明等结构化信息。
- 宽度：`width="100%" viewBox="0 0 640 N"`，高度按内容定
- 背景：`#fafafa` 或 `#f9f9f9`
- 字体：`font-family="'PingFang SC',sans-serif"`，正文 11~13px
- 标题：13px bold，居中，`fill="#1a1a1a"`
- 高亮色使用当前文章主题色

```html
<div style="margin:24px 0;">
  <svg width="100%" viewBox="0 0 640 200" xmlns="http://www.w3.org/2000/svg" style="display:block;border-radius:12px;overflow:hidden;">
    <!-- 内容 -->
  </svg>
  <p style="text-align:center;font-size:12px;color:#aaa;margin:8px 0 0;">图注文字</p>
</div>
```

### 封面图（cover）

- **尺寸**：900×500px（公众号封面裁剪为 900×383，但保留上下余量）
- **背景**：深色（`#1a1a1a`）或品牌色渐变
- **必须包含**：文章标题、副标题或关键词卡片、主题色点缀
- **制作方式**：HTML 模板 → Chrome headless 截图 → PNG
- **文件命名**：`img-01-cover.png`（约 50~100KB）

```bash
# 封面渲染命令
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --screenshot=img-01-cover.png \
  --window-size=900,500 --hide-scrollbars \
  "file:///path/to/img-01-cover.html"
```

### 正文配图（Napkin / 截图）

- 使用 Napkin.ai 生成可视化（详见 napkin-images.md）
- 导出 PNG，2x 分辨率
- 宽度 100%，`border-radius:8px`
- 图片下方加灰色图注：`font-size:12px;color:#aaa;text-align:center`

### 深色信息块（替代图表）

当信息不适合 SVG、但需要视觉区分时，使用深色块：

```html
<div style="background:#1a1a1a;color:#f5f0e8;border-radius:12px;padding:22px 26px;margin:16px 0;font-size:14px;line-height:2.0;">
  <div style="font-size:11px;color:#C8965A;font-weight:bold;letter-spacing:2px;margin-bottom:14px;">标签文字</div>
  内容...
</div>
```

---

## 五、发布前 CSS 自检

发布前快速扫描 HTML，确认以下项：

- [ ] 没有 `<style>` 标签
- [ ] 没有 `rgb()`、`rgba()`、颜色英文名（`white`、`black` 等）
- [ ] 没有 `<link>`、`<script>` 标签
- [ ] 图片 `src` 均为微信 CDN URL（发布脚本执行后自动替换）
- [ ] 字体栈包含 `PingFang SC`（中文渲染保障）
- [ ] 正文容器 `max-width` 不超过 677px
