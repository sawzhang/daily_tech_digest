# /wechat-publish - 微信公众号图文发布

发布图文文章到微信公众号，支持正文图片上传。

## 触发方式

```
/wechat-publish <文章目录路径>
```

## 使用示例

```bash
/wechat-publish /Users/alexzhang/Downloads/my-article
/wechat-publish ~/Desktop/文章目录
```

## 文章目录结构

```
article-folder/
├── *.html           # 文章内容（必需）
├── cover.png/jpg    # 封面图片（必需）
└── *.png/jpg        # 正文图片（可选，自动上传替换路径）
```

## 文章制作完整流程

1. **撰写 HTML 文章**：按微信排版规范编写，图片用本地文件名引用（如 `img-arch.jpg`）
2. **对照风格规范**：参考 `article-style.md`，确认配色、CSS 合规、SVG 图表、封面尺寸符合规范
3. **准备封面图片**：HTML 模板 → Chrome headless 截图，900×500px，文件名 `img-01-cover.png`
4. **生成正文插图**：使用 `/napkin-images` 通过 Napkin.ai 生成专业可视化图表（详见 napkin-images.md）
5. **发布前质量审查**：执行 `/article-review`，四轮对抗测试找出逻辑漏洞，修订后再发布（详见 article-review.md）
6. **所有文件放入同一目录**
7. **执行 `/wechat-publish <目录路径>` 发布**

## 执行指令

```bash
source venv/bin/activate && python .claude/skills/wechat_publish.py "<文章目录路径>"
```

## 执行流程

1. 读取 HTML 文件，提取标题和 body 内容
2. 上传正文图片到微信素材库，获取 URL 替换本地路径
3. 上传封面图片，获取 media_id
4. 优化 HTML（颜色转十六进制、清理空白、图片样式）
5. 创建草稿
6. 尝试发布（无权限则提示手动发布）

## 环境要求

`.env` 配置：
```
WECHAT_APP_ID=wxxxxxxxxxxx
WECHAT_APP_SECRET=xxxxxxxxxx
```

## 微信 API

| API | 用途 | 返回 |
|-----|------|------|
| `media/uploadimg` | 上传正文图片 | URL |
| `material/add_material` | 上传封面 | media_id |
| `draft/add` | 创建草稿 | media_id |
| `freepublish/submit` | 发布文章 | publish_id |

## 排版规范

详见 `article-style.md`（CSS 合规、配色方案、SVG 规范、封面制作、图表规范）。

核心要点：
- 颜色：必须十六进制 `#ffffff`，禁用 `white`、`rgb()` 等
- 无 `<style>` 块，100% 内联 `style="..."`
- 字体：正文 15px，行高 2.0，字体栈含 `PingFang SC`
- 正文容器 `max-width:677px`

## 常见问题

**发布API未授权**: 公众号需微信认证，否则只能创建草稿手动发布

**图片上传失败**: 检查格式 PNG/JPG，大小限制 1MB（正文）/2MB（封面）
