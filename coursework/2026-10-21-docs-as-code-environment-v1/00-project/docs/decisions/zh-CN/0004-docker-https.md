# ADR-0004：Docker与HTTPS部署候选

| Metadata | Value |
| --- | --- |
| Doc-ID | ADR-0004 |
| Version | 0.3.0 |
| Status | DRAFT |
| Updated | 2026-10-12 |
| Language | zh-CN |
| Decision-Status | ACCEPTED |
| Deployment-Status | NOT_EXECUTED |

## 1 上下文

用户偏好Docker和HTTPS，实际部署位置未知。DEC-010、DEC-015明确技术方向，OPEN-010仍PARTIAL；选择架构不等于部署已完成。

## 2 决定

部署候选采用Docker Compose，Caddy为公开HTTPS入口，前端静态资源仍由Nginx服务，/api转发FastAPI，PostgreSQL位于内部网络；数据库、应用业务数据和证书各自持久存储。开发继续SQLite。部署域名、机位、密码和公开端口未配置；不设置真实或默认生产凭据。

当前compose.yaml仍是本地HTTP骨架候选，不能称生产HTTPS配置已就绪；实际容器构建/启动未验证。正式部署前需要单独准备生产配置、迁移、备份恢复和HTTPS检查。

## 3 前提及验证

公开域名需指向服务器，80/443可访问，Caddy证书存储可写且持久；本地私有证书需要客户端信任，不代表公开可信证书。实际证书申请、DNS和安全配置只在部署授权后执行。[Caddy官方说明](https://caddyserver.com/docs/automatic-https)。

上线门包括实际镜像构建、容器健康、PostgreSQL迁移/回滚、真实HTTPS、三语流程和业务测试证据。本次均未声称完成。

## 4 后果

吕嘉伟作为项目经理协调部署期限与风险，曹浩然作为测试员设计迁移和并发验证，开发/部署由全员协作；减少手动环境差异，增加证书及数据卷维护责任。域名/服务器未定时继续本地开发，不能以配置文件替代真实发布验收。
