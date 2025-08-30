# Dockerfile
# 多阶段构建：构建阶段编译 Next，运行阶段仅安装生产依赖并启动 next start

# ---------- Build Stage ----------
FROM node:20-alpine AS builder
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

# 仅拷贝依赖声明，利用缓存
COPY package.json package-lock.json* ./
RUN --mount=type=cache,target=/root/.npm npm ci

# 拷贝源代码并构建
COPY . .
RUN npm run build

# ---------- Runtime Stage ----------
FROM node:20-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000

# 安装生产依赖（不需要 dev 依赖）
COPY package.json package-lock.json* ./
RUN --mount=type=cache,target=/root/.npm npm ci --omit=dev

# 拷贝构建产物与静态资源
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000
# 依赖 package.json 中的 "start": "next start"
CMD ["npm", "run", "start"]