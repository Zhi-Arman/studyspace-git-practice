# StudySpace 业务API契约草稿

| Metadata | Value |
| --- | --- |
| Doc-ID | DOC-17 |
| Version | 0.1.0 |
| Status | DRAFT |
| Updated | 2026-10-16 |
| Language | zh-CN |

## 1 范围与来源

[OpenAPI 3.1.0 契约](../api/openapi.yaml)（SS-API-04 0.1.0）按课堂 RoomBook 风格示例补齐三个既定业务端点。中文与俄语说明共同保存在 YAML 中；本文件与俄语对应文档记录同一设计。范围来自 US-002、US-004 时序图及 SS-API-01/02/03 端点、操作、数据模式作业。完整MVP还需其他接口，本契约仅覆盖这两个课堂场景。

应用仍0.1.0基础骨架；业务接口尚未实现，业务测试NOT_RUN。运行中的 `/api/v1/openapi.json` 由FastAPI生成，只描述已有健康/就绪接口；静态业务契约独立存放，不能视为已运行接口。

## 2 操作与响应

| 操作 | 方法与路径 | operationId | 成功 | 4xx |
| --- | --- | --- | --- | --- |
| OP-01 | `POST /api/v1/bookings` | `createBooking` | 201 | 401、403、409、422 |
| OP-02 | `GET /api/v1/identity-reviews/pending` | `getPendingIdentityReview` | 200 | 401、403、404、422 |
| OP-03 | `POST /api/v1/identity-reviews` | `saveIdentityReviewDecision` | 200 | 401、403、409、422 |

两个POST均定义 `requestBody.required=true` 和 `application/json`；GET只用必填查询参数 `user_id`。请求与响应通过 `$ref` 复用数据模式。所有4xx使用 `Error{code,message}`，401还定义 `WWW-Authenticate: Bearer`。确认冲突才使用409；锁超时及其他数据库失败不能直接冒充业务冲突。

## 3 数据模式、必填与约束

| 作业编号 | 模式 | 用途 |
| --- | --- | --- |
| DS-01 | `BookingCreateRequest` | seat_id、D、start、end全部必填；不接受客户端user_id |
| DS-02 | `BookingCreatedResponse` | booking_id、seat_id、start、end全部必填 |
| DS-03 | `PendingReviewQuery` | user_id必填；对应GET查询参数集合，不是请求体 |
| DS-04 | `PendingReviewResponse` | user_id、student_no、full_name、status、revision全部必填 |
| DS-05 | `IdentityReviewDecisionRequest` | user_id、decision、source_type、source_ref、revision全部必填 |
| DS-06 | `IdentityReviewDecisionResponse` | user_id、status全部必填 |
| DS-07 | `Error` | code、message全部必填 |

所有对象设置 `additionalProperties=false`。ID和revision长1–128，student_no长1–64，full_name长1–200，source_type长1–64，source_ref长1–256，message长1–500。它们是本次拟定技术约束，尚未宣称符合学校实际编号格式。ID及revision为不透明字符串，不预设UUID、整数或JWT。D用date，起止用带时区date-time；revision按读取值原样回传。

待审status仅PENDING；决定与保存后status为VERIFIED或REJECTED。code取AUTH_REQUIRED、FORBIDDEN、REVIEW_NOT_FOUND、VALIDATION_ERROR、SOURCE_UNVERIFIABLE、STUDENT_OVERLAP、SEAT_OVERLAP、STALE_REVIEW。每个模式和错误响应有虚构结构示例，SOURCE_TYPE_TBD/REFERENCE_TBD不能通过真实来源校验。

## 4 安全、时间与事务

三项操作均声明 `security: [{bearerAuth: []}]`。Bearer是本次拟定的会话凭据传输方案；签发、撤销、存储、过期及密码策略需实现前技术评审，不预设JWT。服务端仍须逐次检查当前身份、启用状态及权限；创建预约仅允许启用且VERIFIED的学生，审核读写仅允许有审核权限的管理员。

沿用DEC-016和已授权时间规则：Asia/Shanghai，锁后实际今天至今天+6，30分钟边界/最短时长，最长24小时，默认08:00–22:00。start严格晚于锁后时刻且属于D；end允许恰为D+1 00:00。[start,end)允许相邻，同学生或同座位重叠拒绝，非重叠多条允许。资格、资源、时间、冲突、写入及最少审计必须在同一事务检查/提交；JSON Schema只能检查静态格式。

OPEN-003学校认可来源仍待确认。管理员人工核验可信相符才可VERIFIED、可信不符才可REJECTED；来源不可核实时422并保持PENDING，快照过期时409 STALE_REVIEW。审计不复制学号、姓名或证明影像。

## 5 追溯与同步

OP-01追溯US-002、SP-FR-007、SP-FR-008、SP-FR-009、SP-NFR-004及DEC-016。OP-02追溯US-004、SP-FR-004、SP-FR-022、SP-DR-001。OP-03另含SP-IF-002及OPEN-003。YAML的 `x-operation-id`、`x-coursework-id` 和 `x-traceability` 保留对应关系。

任务一列出端点；任务二列出操作、返回码与角色；任务三列出七个模式及示例。`scripts/check_api_contract.py` 检查三份作业与YAML的路径、状态码、模式名称、必填字段、示例和项目时间参数，避免资料彼此漂移。修改契约后同步两语说明及对应作业源数据，再重建受影响Word。正式需求状态和38个业务用例仍按原登记保持PROPOSED/NOT_RUN。

## 6 验证与证据

执行环境为本地macOS、项目 `backend/.venv` 和锁定的开发依赖；命令从项目根执行：

```bash
backend/.venv/bin/python scripts/check_api_contract.py --report artifacts/api-contract-validation.json
python3 scripts/check_docs.py
python3 scripts/generate_registers.py --check
```

契约检查包含OpenAPI规范验证、本地引用解析、全部Schema/媒体/参数示例、缺必填/多余user_id/无效时间/超长ID/非法决定等拒绝样例及作业一致性。它不启动业务服务，也不证明并发、权限、真实学校核验或业务验收。实际结果保存在上述报告；业务测试NOT_RUN。

2026-10-16实测：契约110项静态检查通过（17个示例、6个拒绝反例），后端20项及前端19项测试通过，前端lint/类型/构建通过，更新的两份Word均单页目视检查通过。项目总检查在9个历史课程脚本的719项Ruff问题处失败；新增检查脚本的lint/格式通过。完整本地记录：`artifacts/api-contract-completion.json`，历史问题清单：`artifacts/api-contract-existing-lint.json`。

## 7 文件与后续条件

交付路径：`docs/api/openapi.yaml`；说明为本文件及 `docs/ru-RU/17_API_Contract.md`；检查脚本为 `scripts/check_api_contract.py`。正式清单登记DOC-17，课程入口链接SS-API-01/02/03与契约。下一步实现前评审认证生命周期、ID编码及学校学号格式，落实OPEN-003，并以隔离数据验证服务端事务与真实业务流程。
