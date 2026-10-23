# StudySpace 测试用例草稿

> 历史草案范围提示：2026-10-23 的 DEC-018 与 [本地版本说明](18_Local_Version.md) 已覆盖本文件涉及真实学校核验、远程域名/HTTPS和初始化未实现状态的旧约束；其余稳定规则保留。


| Metadata | Value |
| --- | --- |
| Doc-ID | DOC-06 |
| Version | 0.4.0 |
| Status | DRAFT |
| Updated | 2026-10-23 |
| Language | zh-CN |

> 初始化草稿：业务需求尚未经过正式评审与批准。标为“项目假设”或“待确认”的内容不得视为已确认需求；本文件不声明已完成用户调研、业务测试或验收。

## 1 状态与使用说明

全部业务用例为NOT_RUN，来自../data/test-cases.json。对应功能尚未实现；此处为计划骨架。需要规则确认的预期不得假装确定，基础检查另记。

## 2 计划用例索引

<!-- GENERATED:BEGIN -->
| TC | 需求ID | 范围 | 状态 | 标题 |
| --- | --- | --- | --- | --- |
| TC-001 | FR-001 | MVP | NOT_RUN | 学生注册与核验状态验证 |
| TC-002 | FR-002 | MVP | NOT_RUN | 登录与退出验证 |
| TC-003 | FR-003 | MVP | NOT_RUN | 角色访问控制验证 |
| TC-004 | FR-004 | MVP | NOT_RUN | 教室与自习室查询验证 |
| TC-005 | FR-005 | MVP | NOT_RUN | 可预约时间查询验证 |
| TC-006 | FR-006 | MVP | NOT_RUN | 空闲座位查询验证 |
| TC-007 | FR-007 | MVP | NOT_RUN | 提交预约验证 |
| TC-008 | FR-008 | MVP | NOT_RUN | 预约冲突检测验证 |
| TC-009 | FR-009 | MVP | NOT_RUN | 取消预约验证 |
| TC-010 | FR-010 | MVP | NOT_RUN | 个人预约记录验证 |
| TC-011 | FR-011 | MVP | NOT_RUN | 房间与座位信息管理验证 |
| TC-012 | FR-012 | MVP | NOT_RUN | 开放时间设置验证 |
| TC-013 | FR-013 | MVP | NOT_RUN | 预约规则管理验证 |
| TC-014 | FR-014 | MVP | NOT_RUN | 管理员预约查询验证 |
| TC-015 | FR-015 | MVP | NOT_RUN | 用户信息维护验证 |
| TC-016 | FR-016 | MVP | NOT_RUN | 基础统计验证 |
| TC-017 | FR-017 | MVP | NOT_RUN | 座位级预约验证 |
| TC-018 | FR-018 | FUTURE | NOT_RUN | 预约提醒验证 |
| TC-019 | FR-019 | FUTURE | NOT_RUN | 二维码签到验证 |
| TC-020 | FR-020 | FUTURE | NOT_RUN | 违约记录验证 |
| TC-021 | FR-021 | FUTURE | NOT_RUN | 资源使用率统计验证 |
| TC-022 | NFR-001 | MVP | NOT_RUN | 可维护性验证 |
| TC-023 | NFR-002 | MVP | NOT_RUN | 性能与容量验证 |
| TC-024 | NFR-003 | MVP | NOT_RUN | 安全性验证 |
| TC-025 | NFR-004 | MVP | NOT_RUN | 事务一致性验证 |
| TC-026 | NFR-005 | MVP | NOT_RUN | 数据库可迁移性验证 |
| TC-027 | NFR-006 | MVP | NOT_RUN | 三语界面与可用性验证 |
| TC-028 | NFR-007 | MVP | NOT_RUN | 运行诊断与隐私验证 |
| TC-029 | NFR-008 | MVP | NOT_RUN | 双语文档及追溯性验证 |
| TC-030 | BR-001 | MVP | NOT_RUN | 时间区间有效性验证 |
| TC-031 | BR-002 | MVP | NOT_RUN | 座位占用互斥验证 |
| TC-032 | BR-003 | MVP | NOT_RUN | 开放时间限制验证 |
| TC-033 | BR-004 | MVP | NOT_RUN | 预约配额及提前量验证 |
| TC-034 | BR-005 | MVP | NOT_RUN | 取消时限及后果验证 |
| TC-035 | BR-006 | MVP | NOT_RUN | 账号资格及角色授予验证 |
| TC-036 | BR-007 | MVP | NOT_RUN | 资源停用与历史记录验证 |
| TC-037 | BR-008 | MVP | NOT_RUN | 时区与日期解释验证 |
| TC-038 | FR-022 | MVP | RETIRED | 校内身份审核验证 |
<!-- GENERATED:END -->

## 3 单个用例模板

每个用例包含：ID、需求ID、标题、前置条件、步骤、预期、实际结果、状态、环境、执行人、日期和证据。JSON中已保存双语标题、前置条件、步骤和初步预期。实际结果、执行人、执行日期及证据尚无记录；实施后补充。

## 4 维护规则

修改同一用例须同步两语，不重新分配旧ID。范围变更后保留撤销记录；批准测试前核对需求状态与可验证的预期。自动登记检查只能检查结构与引用，不能判断实际业务通过。
