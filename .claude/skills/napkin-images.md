# /napkin-images - 使用 Napkin.ai 生成文章插图

通过浏览器自动化操作 Napkin.ai，为公众号文章生成专业可视化插图。

## 触发方式

```
/napkin-images <图片描述内容>
```

## 使用示例

```bash
/napkin-images "Stage 1: Analysis - 2 min\nStage 2: Parallel Execution - 2 min\nStage 3: Verification - 2 min"
```

## 前置条件

- 已安装 Claude in Chrome 扩展（MCP 浏览器自动化）
- 已登录 Napkin.ai 账号（https://app.napkin.ai）

## 执行流程

1. 获取浏览器 Tab 上下文（`tabs_context_mcp`）
2. 打开 Napkin.ai，点击 `+ New Napkin`
3. 选择 `Blank Napkin`
4. 在标题区域输入图片标题
5. 按 Enter，在正文区域输入结构化内容
6. `Cmd+A` 全选文本，点击左侧 `Generate Visual` 按钮
7. 等待 5-6 秒，AI 生成可视化图表
8. 滚动到生成的 visual，点击选中
9. 点击右侧工具栏的下载图标（↓）
10. 在 Export Visual 对话框中：
    - 格式选择 `PNG`
    - Background: `On`
    - Resolution: `2x`（推荐，清晰度更好）
    - 点击 `Download`
11. 将下载的 PNG 复制到文章目录，重命名为对应的 img-*.jpg

## 内容编写技巧

Napkin.ai 根据文本结构自动生成不同类型的可视化：

### 流程/时间线
```
Stage 1: bdd-analyst (Analysis) - 2 min
Read 71 lines BDD scenarios and Skill definitions
Output: 12 business rules, 3 API endpoints

Stage 2: PARALLEL EXECUTION - 2 min
domain-coder: 5 files (Repository, Controller, EmailService)
test-coder: 2 files (Karate API tests, Cucumber Steps)

Stage 3: validator (Verification) - 2 min
File completeness: 8/8 PASS
BDD traceability: 100%
```

### 数据仪表盘
```
Input: 71 lines BDD scenarios (6 scenarios)
Output: 1294 lines of code (8 files)
Amplification: 18.2x code generation ratio
BDD Traceability: 100% coverage
Scenario Coverage: 6/6 all four layers
```

### 层次/架构图
```
Layer 1: BDD Scenarios (Business Requirements)
Layer 2: SDD Skills (Code Generation Rules)
Layer 3: AI Agent Team (Parallel Autonomous Agents)
Layer 4: Verified Output (Production-Ready Code)
```

## 注意事项

- **Napkin Logo 移除**是付费功能，免费版导出的图片会带 "Made with Napkin" 水印
- **剪贴板冲突**：下载 PNG 后剪贴板会包含图片数据，此时在 Napkin 中粘贴文本会报错 "Unable to paste"。解决方法：直接用 `type` 输入而非粘贴
- 每个 Napkin 页面建议只放一张图的内容，多张图创建多个 `+ New Napkin` 页面
- 建议导出分辨率选 `2x`，微信公众号显示效果更清晰
- 生成的 visual 可能出现在文本下方，需要向下滚动查找

## 批量生成工作流

为一篇文章生成多张插图的推荐流程：

```
1. 准备所有图片的文本内容（标题 + 结构化描述）
2. 逐个创建 New Napkin → 输入内容 → 生成 → 导出
3. 所有 PNG 下载到 ~/Downloads/
4. 批量复制到文章目录：
   cp ~/Downloads/图片名.png /path/to/article/img-xxx.jpg
5. 运行 /wechat-publish 发布
```
