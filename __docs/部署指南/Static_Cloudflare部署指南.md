# Static 静态资源 Cloudflare 部署指南

> 10 分钟完成静态资源 CDN 部署

## 🎯 部署目标

将 `static/` 目录下的静态资源部署到 Cloudflare Pages，实现：

- 全球 CDN 加速访问
- 无限带宽，零成本
- 自动 HTTPS
- 多产品支持（headshot-ai, group-photo-ai 等）

## 📋 为什么选择 Cloudflare Pages？

| 特性 | Cloudflare Pages | AWS S3 + CloudFront | 其他 CDN |
|------|-----------------|---------------------|----------|
| **带宽费用** | 免费无限 | 按量付费 | 按量付费 |
| **CDN 节点** | 300+ 全球节点 | 需额外配置 | 有限节点 |
| **部署方式** | Git 自动部署 | 手动上传 | 手动上传 |
| **SSL 证书** | 自动免费 | 需配置 | 需配置 |
| **适用场景** | ✅ 完美适配 | 大型企业 | 中小项目 |

## 🚀 部署步骤（10 分钟）

### ⚠️ 遇到部署错误？

如果看到 `Missing entry-point to Worker script` 错误，请查看：
👉 [Cloudflare 快速修复指南](./Cloudflare_快速修复.md)

### 前置准备

1. **Cloudflare 账号**
   - 访问 [Cloudflare](https://dash.cloudflare.com/sign-up)
   - 注册免费账号

2. **Git 仓库**
   - 确保 static 项目已推送到 GitHub/GitLab
   - 或准备好本地 static 目录

3. **重要提醒**
   - ✅ 使用 **Cloudflare Pages**（不是 Workers）
   - ✅ 不需要构建命令
   - ✅ 直接部署 static 目录

### 步骤 1: 创建 Cloudflare Pages 项目（3 分钟）

#### ⚠️ 重要：选择正确的部署方式

**必须使用 Cloudflare Pages，不是 Workers！**

#### 方式 1: 通过 Git 连接（推荐）

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 在左侧菜单选择 **"Workers & Pages"**
3. 点击 **"Create application"**
4. 选择 **"Pages"** 标签页（不是 Workers！）
5. 点击 **"Connect to Git"**
6. 授权 GitHub/GitLab
7. 选择 `aipso-static` 仓库
8. 点击 "Begin setup"

#### 方式 2: 直接上传

1. 登录 Cloudflare Dashboard
2. 选择 "Workers & Pages"
3. 点击 "Create application"
4. 选择 **"Pages"** 标签页
5. 点击 **"Upload assets"**
6. 上传 `static/` 目录

### 步骤 2: 配置构建设置（2 分钟）

在 Cloudflare Pages 配置页面：

```yaml
# 项目名称
Project name: aipso-static

# 生产分支
Production branch: main

# 构建设置
Framework preset: None (选择 "None" 或 "Static")
Build command: (留空，不需要构建)
Build output directory: static

# 根目录（如果有选项）
Root directory: (留空)

# 环境变量
(不需要)
```

**重要配置说明**：
- ✅ `Framework preset`: 选择 **"None"** 或 **"Static"**
- ✅ `Build command`: **留空**（我们不需要构建，直接部署静态文件）
- ✅ `Build output directory`: 设置为 **`static`**
- ✅ 这样 Cloudflare 会直接部署 static 目录下的内容

**常见错误**：
- ❌ 不要选择任何框架（React, Vue 等）
- ❌ 不要填写构建命令
- ❌ 不要使用 Workers 部署方式

### 步骤 3: 部署（1 分钟）

点击 "Save and Deploy"，Cloudflare 会自动：

1. 拉取代码
2. 部署 static 目录
3. 生成临时域名（如 `aipso-static.pages.dev`）

部署完成后，你会看到：
```
✅ Deployment successful
🌐 https://aipso-static.pages.dev
```

### 步骤 4: 配置自定义域名（4 分钟）

#### 4.1 添加域名

1. 在 Cloudflare Pages 项目页面
2. 点击 "Custom domains"
3. 点击 "Set up a custom domain"
4. 输入域名：`static.aip.so`
5. 点击 "Continue"

#### 4.2 配置 DNS

Cloudflare 会自动检测并提示配置 DNS：

**如果域名在 Cloudflare**：
- 自动配置，无需手动操作 ✅

**如果域名在其他服务商**：
```
类型: CNAME
名称: static
值: aipso-static.pages.dev
```

#### 4.3 等待生效

- DNS 生效时间：5-30 分钟
- SSL 证书自动配置：5-10 分钟

## 🌐 访问 URL 结构

部署完成后，访问结构如下：

```
# 主域名
https://static.aip.so/

# 产品资源
https://static.aip.so/headshot-ai/images/home/City/city-1.webp
https://static.aip.so/headshot-ai/images/options/backdrops/...

# 其他产品
https://static.aip.so/group-photo-ai/images/...
https://static.aip.so/fashion-shot-ai/images/...
```

## 🔧 目录结构要求

确保你的 static 目录结构正确：

```
static/
├── headshot-ai/
│   └── images/
│       ├── home/
│       ├── demo-faces/
│       └── options/
├── group-photo-ai/
│   └── images/
└── fashion-shot-ai/
    └── images/
```

**注意**：
- ❌ 不要包含 `files.txt`（已在 .gitignore 中）
- ❌ 不要包含隐藏文件（.DS_Store 等）
- ✅ 只包含图片文件

## 🧪 测试验证

### 1. 基础访问测试

```bash
# 测试主域名
curl -I https://static.aip.so

# 测试图片访问
curl -I https://static.aip.so/headshot-ai/images/home/City/city-1.webp

# 应该返回 200 OK
```

### 2. 浏览器测试

```
1. 访问 https://static.aip.so/headshot-ai/images/home/City/city-1.webp
2. 应该显示图片 ✅
3. 检查 HTTPS 证书（应该是绿色锁） ✅
```

### 3. 性能测试

```bash
# 测试响应时间
curl -w "@curl-format.txt" -o /dev/null -s https://static.aip.so/headshot-ai/images/home/City/city-1.webp

# 或使用在线工具
# https://tools.pingdom.com/
# https://www.webpagetest.org/
```

### 4. CDN 测试

```bash
# 检查 CDN 节点
curl -I https://static.aip.so/headshot-ai/images/home/City/city-1.webp | grep -i cf-ray

# 应该看到 CF-RAY 头，表示通过 Cloudflare CDN
```

## 🔄 自动部署配置

### Git 自动部署

如果使用 Git 连接方式，每次推送代码会自动部署：

```bash
# 1. 添加新图片
cp new-image.webp static/headshot-ai/images/home/City/

# 2. 提交到 Git
git add static/headshot-ai/images/
git commit -m "Add new images"
git push origin main

# 3. Cloudflare 自动部署（1-2 分钟）
# 4. 自动清除 CDN 缓存
```

### 手动部署

如果使用直接上传方式：

```bash
# 1. 在 Cloudflare Pages 项目页面
# 2. 点击 "Create deployment"
# 3. 上传更新后的 static 目录
```

## ⚙️ 高级配置

### 1. 缓存配置

创建 `_headers` 文件在 static 目录：

```
# static/_headers

# 图片文件 - 长期缓存
/*/images/*
  Cache-Control: public, max-age=31536000, immutable
  Access-Control-Allow-Origin: *

# 根目录 - 短期缓存
/*
  Cache-Control: public, max-age=3600
```

### 2. 重定向配置

创建 `_redirects` 文件在 static 目录：

```
# static/_redirects

# 重定向旧路径到新路径（如果需要）
/old-path/* /new-path/:splat 301

# 404 处理
/* /404.html 404
```

### 3. 自定义 404 页面

创建 `static/404.html`：

```html
<!DOCTYPE html>
<html>
<head>
    <title>404 - File Not Found</title>
</head>
<body>
    <h1>404 - File Not Found</h1>
    <p>The requested resource was not found.</p>
</body>
</html>
```

## 🔒 安全配置

### 1. 防盗链（可选）

在 Cloudflare Dashboard：

1. 进入 "Security" → "WAF"
2. 创建规则：
```
如果 Referer 不包含 aip.so
则 阻止请求
```

### 2. 访问限制（可选）

```
如果 请求速率 > 100/分钟
则 挑战（CAPTCHA）
```

### 3. 地域限制（可选）

```
如果 国家 不在 [允许列表]
则 阻止请求
```

## 📊 监控和分析

### 1. Cloudflare Analytics

在 Cloudflare Dashboard 查看：

- 请求数量
- 带宽使用
- 缓存命中率
- 访问地域分布
- 响应时间

### 2. 实时日志

```bash
# 使用 Cloudflare Logpush（需要付费计划）
# 或使用 Workers 记录访问日志
```

## 🔧 故障排查

### 问题 1: 错误使用了 Workers 而不是 Pages

**症状**: 构建日志显示 `Missing entry-point to Worker script`

```
✘ [ERROR] Missing entry-point to Worker script or to assets directory
```

**原因**: 选择了 Workers 部署方式，而不是 Pages

**解决方案**:
1. ❌ 删除当前的 Workers 项目
2. ✅ 重新创建，选择 **"Pages"** 标签页
3. ✅ 不要选择 "Workers"

**正确步骤**:
```
Cloudflare Dashboard
  → Workers & Pages
  → Create application
  → 选择 "Pages" 标签页 ← 重要！
  → Connect to Git
```

### 问题 2: 构建配置错误

**症状**: 部署失败，提示找不到文件

**解决方案**:
```yaml
# 正确配置
Framework preset: None
Build command: (留空)
Build output directory: static  ← 必须是 static

# 错误配置 ❌
Framework preset: React/Vue/Next.js
Build command: npm run build
Build output directory: dist
```

### 问题 3: 部署失败

**症状**: 部署过程中出错

**解决方案**:
1. 检查 static 目录结构
2. 确保没有超大文件（>25MB）
3. 检查 Git 仓库是否正常
4. 查看 Cloudflare 部署日志

### 问题 2: 图片无法访问

**症状**: 404 Not Found

**解决方案**:
```bash
# 1. 检查文件路径
ls -la static/headshot-ai/images/home/City/

# 2. 检查文件名大小写
# Cloudflare 区分大小写

# 3. 重新部署
git push origin main --force
```

### 问题 3: SSL 证书问题

**症状**: HTTPS 不安全警告

**解决方案**:
1. 等待 10-30 分钟（自动配置）
2. 在 Cloudflare Pages 检查域名状态
3. 删除域名重新添加

### 问题 4: 缓存问题

**症状**: 更新后仍显示旧图片

**解决方案**:
```bash
# 1. 清除 Cloudflare 缓存
# Dashboard → Caching → Purge Everything

# 2. 或使用 API
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'
```

### 问题 5: 访问速度慢

**症状**: 图片加载缓慢

**解决方案**:
1. 检查图片大小（建议 < 500KB）
2. 使用 WebP 格式
3. 启用 Cloudflare 图片优化（Polish）
4. 检查 CDN 缓存命中率

## 💰 成本分析

### Cloudflare Pages 免费计划

| 项目 | 限制 | 说明 |
|------|------|------|
| 带宽 | 无限 | ✅ 完全免费 |
| 请求数 | 无限 | ✅ 完全免费 |
| 构建次数 | 500/月 | 足够使用 |
| 并发构建 | 1 | 够用 |
| 自定义域名 | 100 | 足够 |

**结论**：对于 static 静态资源，免费计划完全够用！

### 与 AWS S3 对比

假设每月 1TB 流量：

| 服务 | 月费用 |
|------|--------|
| Cloudflare Pages | $0 |
| AWS S3 + CloudFront | ~$85 |
| 阿里云 OSS + CDN | ~¥500 |

**节省**：每月节省 $85+ 💰

## 🎯 最佳实践

### 1. 图片优化

```bash
# 使用 WebP 格式
cwebp -q 80 input.jpg -o output.webp

# 压缩图片
# 使用 tools/create-backdrops-blur-image/
```

### 2. 目录结构

```
static/
├── headshot-ai/
│   └── images/          # 只包含图片
│       ├── home/
│       ├── demo-faces/
│       └── options/
└── _headers             # 缓存配置
```

### 3. 版本管理

```bash
# 使用 Git 标签管理版本
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# Cloudflare 支持按标签部署
```

### 4. 多环境部署

```
# 生产环境
分支: main
域名: static.aip.so

# 测试环境
分支: develop
域名: static-dev.aip.so
```

## 🔄 更新流程

### 日常更新

```bash
# 1. 添加新图片
cp new-images/* static/headshot-ai/images/home/City/

# 2. 提交到 Git
git add static/
git commit -m "Add new images"
git push origin main

# 3. Cloudflare 自动部署（1-2 分钟）

# 4. 验证
curl -I https://static.aip.so/headshot-ai/images/home/City/new-image.webp
```

### 批量更新

```bash
# 1. 批量添加图片
cp -r batch-images/* static/headshot-ai/images/

# 2. 提交
git add static/
git commit -m "Batch import images"
git push origin main

# 3. 等待部署完成
```

## 📚 相关文档

- [Cloudflare Pages 官方文档](https://developers.cloudflare.com/pages/)
- [前端部署指南](./02.前端部署指南.md)
- [多产品架构](./多产品架构.md)

## 🎊 部署检查清单

### 部署前
- [ ] Cloudflare 账号已注册
- [ ] static 目录结构正确
- [ ] 已移除 files.txt 等内部文件
- [ ] 图片已优化（WebP 格式）
- [ ] Git 仓库已推送

### 部署后
- [ ] Cloudflare Pages 项目已创建
- [ ] 构建配置正确（output: store）
- [ ] 部署成功
- [ ] 临时域名可访问
- [ ] 自定义域名已添加
- [ ] DNS 已配置
- [ ] DNS 已生效
- [ ] HTTPS 证书正常
- [ ] 图片可正常访问
- [ ] CDN 缓存正常工作

## 🚀 快速部署命令

```bash
# 1. 确保 static 目录干净
git status

# 2. 推送到 Git
git add static/
git commit -m "Prepare for Cloudflare deployment"
git push origin main

# 3. 在 Cloudflare Dashboard 创建 Pages 项目
# - 连接 Git 仓库
# - 设置 output directory: static
# - 部署

# 4. 配置自定义域名
# - 添加 static.aip.so
# - 配置 DNS

# 5. 等待生效（5-30 分钟）

# 6. 测试
curl -I https://static.aip.so/headshot-ai/images/home/City/city-1.webp

# 完成！🎉
```

## 🎯 Server 端集成

部署完成后，更新 server 端配置：

```javascript
// config.js
const STATIC_CONFIG = {
  development: {
    domain: 'http://localhost:8080',
    product: 'headshot-ai'
  },
  production: {
    domain: 'https://static.aip.so',  // ← 更新为 Cloudflare 域名
    product: 'headshot-ai'
  }
};

export const getImageUrl = (relativePath) => {
  const { domain, product } = STATIC_CONFIG[process.env.NODE_ENV];
  return `${domain}/${product}${relativePath}`;
};
```

## 💡 总结

Cloudflare Pages 是部署 static 静态资源的最佳选择：

- ✅ **零成本**：无限带宽，完全免费
- ✅ **高性能**：全球 300+ CDN 节点
- ✅ **易部署**：Git 自动部署，一键更新
- ✅ **高可用**：99.99% SLA 保证
- ✅ **安全**：自动 HTTPS，DDoS 防护

**开始部署吧！** 🚀

---

**需要帮助？**
- 查看 [Cloudflare Pages 文档](https://developers.cloudflare.com/pages/)
- 查看本文档的故障排查部分
- 联系 Cloudflare 支持（免费计划也有支持）
