# StudySpace 需求登记表草稿

> 历史草案范围提示：2026-10-23 的 DEC-018 与 [本地版本说明](18_Local_Version.md) 已覆盖本文件涉及真实学校核验、远程域名/HTTPS和初始化未实现状态的旧约束；其余稳定规则保留。


| Metadata | Value |
| --- | --- |
| Doc-ID | DOC-14 |
| Version | 0.4.0 |
| Status | DRAFT |
| Updated | 2026-10-23 |
| Language | zh-CN |

> 初始化草稿：业务需求尚未经过正式评审与批准。标为“项目假设”或“待确认”的内容不得视为已确认需求；本文件不声明已完成用户调研、业务测试或验收。

## 1 登记来源与状态

本登记由../data/requirements.json双语源维护，源为课程任务说明，未进行正式需求评审。所有需求为PROPOSED，MVP和FUTURE是候选范围标签，不代表已批准或已实现。需求不得因章节调整改变ID；implementation当前为空。

## 2 候选需求登记

<!-- GENERATED:BEGIN -->
| ID | 类型 | 范围 | 状态 | 标题 | 描述 | 验证方法 | 设计草稿 | 计划测试用例 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-001 | FR | MVP | PROPOSED | 本地学生注册 | DEC-018：仅保存本地用户名、显示名和密码散列，不采集学号或学校证明。用户名3–32个ASCII字母/数字/下划线且不区分大小写，显示名1–60，密码10–128字符；身份模式LOCAL_ONLY，启用学生可预约。 | 注册规则确认后，覆盖有效、重复与不符合资格的注册。 | [04_System_Design.md](04_System_Design.md) §3.1; [18_Local_Version.md](18_Local_Version.md) §3 | TC-001 |
| FR-002 | FR | MVP | PROPOSED | 登录与退出 | scrypt保存密码；随机会话仅存SHA-256，HttpOnly/SameSite=Strict，12小时过期；退出、账号停用或角色变更撤销会话。5分钟内5次失败后限流，无邮件或密码找回服务。 | 使用有效及无效凭据验证登录，退出后验证会话行为。 | [04_System_Design.md](04_System_Design.md) §3.1; [18_Local_Version.md](18_Local_Version.md) §3 | TC-002 |
| FR-003 | FR | MVP | PROPOSED | 角色访问控制 | 匿名可查空间座位；启用STUDENT预约及管理本人记录；ADMIN维护资源、用户、预约和统计。公开注册不能自授管理员，无校内审核状态。 | 以匿名、学生、管理员身份访问受限操作并检查服务端判定。 | [04_System_Design.md](04_System_Design.md) §3.1; [18_Local_Version.md](18_Local_Version.md) §3 | TC-003 |
| FR-004 | FR | MVP | PROPOSED | 教室与自习室查询 | 按校区、楼栋、楼层和CLASSROOM/STUDY_ROOM类型查询房间及其座位；预约单位是单个Seat，房间不可整室预约。 | 对存在、不存在及边界筛选条件检查查询结果。 | [04_System_Design.md](04_System_Design.md) §3.2; [18_Local_Version.md](18_Local_Version.md) §3 | TC-004 |
| FR-005 | FR | MVP | PROPOSED | 可预约时间查询 | 按Asia/Shanghai业务日期查询座位开放及可预约时段；默认每日08:00–22:00、30分钟粒度，今天至今天+6。 | 根据配置的开放时间和预约记录核对可预约时间。 | [04_System_Design.md](04_System_Design.md) §3.2; [18_Local_Version.md](18_Local_Version.md) §3 | TC-005 |
| FR-006 | FR | MVP | PROPOSED | 空闲座位查询 | 给定业务日期与[start,end)区间查询启用房间内启用且无重叠有效预约的座位；查询不锁定结果，提交时服务端重新验证。 | 构造空闲、占用及关闭资源数据，核对查询结果。 | [04_System_Design.md](04_System_Design.md) §3.2; [18_Local_Version.md](18_Local_Version.md) §3 | TC-006 |
| FR-007 | FR | MVP | PROPOSED | 提交预约 | 启用的本地学生每次预约1座位；写锁后验证资格、开放、提前窗口、30分钟、最多24h及同学生/同seat区间冲突。允许多条不重叠预约，无全局未结束总数限制。 | 规则确认后提交有效与无效预约，验证持久化及错误反馈。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | TC-007 |
| FR-008 | FR | MVP | PROPOSED | 预约冲突检测 | 同seat或同user的未取消预约均用existing.start < new.end且new.start < existing.end判冲突；不同seat也不能使同学生时间重叠。相邻[start,end)允许，非重叠未来多条允许，检查与写入在同一事务。 | 计划：同学生同/不同seat重叠拒绝，包含与部分重叠拒绝，非重叠同日/不同日及相邻均允许；并发重叠仅1成功，非重叠均成功；取消仅影响其时段。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | TC-008 |
| FR-009 | FR | MVP | PROPOSED | 取消预约 | 学生锁后now<start可取消本人预约，开始后仅管理员带原因取消，重复幂等；取消仅释放该预约的seat和时段，其他非重叠预约不受影响。 | 验证本人、他人、已取消与超过截止时间的取消行为。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | TC-009 |
| FR-010 | FR | MVP | PROPOSED | 个人预约记录 | 学生仅查询本人预约；按起始时间倒序、状态与业务日期筛选，分页默认20且最多100。终结后保留180天，到期数据不伪造为空白历史。 | 检查自己的记录可见、他人记录不可见及空列表结果。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | TC-010 |
| FR-011 | FR | MVP | PROPOSED | 房间与座位信息管理 | 管理员维护房间位置、类型、名称与启停及Seat编码、启停；room_id+seat_code唯一，容量从启用座位派生；有历史的资源保留并软停用。 | 验证管理员增改停用资源及学生权限拒绝。 | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | TC-011 |
| FR-012 | FR | MVP | PROPOSED | 开放时间设置 | 默认每天08:00–22:00，支持管理员按房间配置常规和日期例外；缩减开放窗口时同事务取消不满足新窗口的未结束预约，记录原因。 | 修改开放时间，核对查询和新预约规则变化。 | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | TC-012 |
| FR-013 | FR | MVP | PROPOSED | 预约规则管理 | 管理员配置房间开放和1–7自然日提前窗口；24h硬上限、同用户时段互斥、每条1seat和权限不可放宽；不设置未结束总数限制；变更审计。缩短提前窗口只影响新提交。 | 配置经确认的规则，验证边界及权限；不使用未经批准阈值。 | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | TC-013 |
| FR-014 | FR | MVP | PROPOSED | 管理员预约查询 | 管理员按业务日期、房间、座位、状态和本地用户名分页查看保留期内预约，不批量导出；已匿名化记录不显示原用户名或显示名。 | 核对筛选结果及仅管理员可访问。 | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | TC-014 |
| FR-015 | FR | MVP | PROPOSED | 用户信息维护 | 管理员维护启停和角色；首位管理员通过显式CLI创建，无默认密码。停用或移出学生角色时原子取消未结束预约并撤销会话；禁止停用/降级最后一位启用管理员。 | 验证允许的状态维护与越权拒绝，检查个人数据最小化。 | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | TC-015 |
| FR-016 | FR | MVP | PROPOSED | 基础统计 | 按预约业务日期D与统一as_of提供累计创建数、累计取消数和未取消且未结束数（包含未来）；不推断到场、实际占用或使用率，清理过期数据返回不可统计。 | 指标确认后，用已知数据手工核对统计结果。 | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | TC-016 |
| FR-017 | FR | MVP | PROPOSED | 座位级预约 | 已确认MVP为单座位预约，沿用原ID并从FUTURE移至MVP；Seat隶属于Room且编码在房间内唯一，查询、冲突和管理围绕seat_id。不要求图形座位图。 | 验证同室不同座位、同学生时间互斥及非重叠多条，seat粒度与管理一致。 | [04_System_Design.md](04_System_Design.md) §3.2; [18_Local_Version.md](18_Local_Version.md) §3 | TC-017 |
| FR-018 | FR | FUTURE | PROPOSED | 预约提醒 | 扩展候选：提供预约提醒；渠道、同意、重试和发送时机待确认。 | 扩展获批后验证提醒时机、重复抑制及发送失败处理。 | [04_System_Design.md](04_System_Design.md) §3.5 | TC-018 |
| FR-019 | FR | FUTURE | PROPOSED | 二维码签到 | 扩展候选：二维码签到；令牌有效期、反重放及离线处理待确认。 | 扩展获批后验证有效、过期及重放二维码。 | [04_System_Design.md](04_System_Design.md) §3.5 | TC-019 |
| FR-020 | FR | FUTURE | PROPOSED | 违约记录 | 扩展候选：记录预约违约；认定依据、申诉及保留期待确认。 | 规则获批后验证认定、更正与授权访问。 | [04_System_Design.md](04_System_Design.md) §3.5 | TC-020 |
| FR-021 | FR | FUTURE | PROPOSED | 资源使用率统计 | 扩展候选：资源利用率统计；有效占用和分母定义待确认。 | 指标获批后用已知占用样本核对计算。 | [04_System_Design.md](04_System_Design.md) §3.5 | TC-021 |
| NFR-001 | NFR | MVP | PROPOSED | 可维护性 | 拟保持前后端分层、类型检查、锁文件和可重复运行说明；验收标准待确认。 | 评审目录依赖和文档并执行经批准的质量检查。 | [04_System_Design.md](04_System_Design.md) §7; [18_Local_Version.md](18_Local_Version.md) §5 | TC-022 |
| NFR-002 | NFR | MVP | PROPOSED | 性能与容量 | 响应时间、并发用户数、数据量及测量环境均待确认；不在初始化时承诺数值。 | 确认负载与阈值后执行可重复的性能测试。 | [04_System_Design.md](04_System_Design.md) §7; [18_Local_Version.md](18_Local_Version.md) §5 | TC-023 |
| NFR-003 | NFR | MVP | PROPOSED | 安全性 | 仅本地课程环境：scrypt密码散列、散列会话、服务端授权及输入校验、同源写入请求头和Origin检查。错误不回显密码等输入，日志和最小审计不保存秘密；不提供真实校内核验。 | 评审密码存储、配置及权限，并执行批准的安全测试。 | [04_System_Design.md](04_System_Design.md) §6; [18_Local_Version.md](18_Local_Version.md) §5 | TC-024 |
| NFR-004 | NFR | MVP | PROPOSED | 事务一致性 | SQLite BEGIN IMMEDIATE串行化业务写入，锁后取now，在同一事务完成同学生/同seat冲突检查和写入。停用资源或账号与取消原子完成；并发同座位或同学生重叠只允许1成功，相邻时段可都成功。 | 计划：同学生同/不同seat重叠拒绝，包含与部分重叠拒绝，非重叠同日/不同日及相邻均允许；并发重叠仅1成功，非重叠均成功；取消仅影响其时段。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §5 | TC-025 |
| NFR-005 | NFR | MVP | PROPOSED | SQLite模式迁移 | 本地原生与Docker统一使用SQLite/Alembic；启动自动迁移，验证upgrade/downgrade往返及新文件恢复。PostgreSQL适配和并发不属于当前交付。 | 在明确迁移计划后核对模式、数据、约束及回滚；连接能力不等同迁移验收。 | [04_System_Design.md](04_System_Design.md) §4; [18_Local_Version.md](18_Local_Version.md) §5 | TC-026 |
| NFR-006 | NFR | MVP | PROPOSED | 三语界面与可用性 | 界面中俄英即时切换，上海时区一致，375px/768px/1440px响应布局。当前仅实测Chromium；Firefox/Safari与人工无障碍验收尚未执行。 | 确认界面范围后验证语言切换、核心流程及无障碍要求。 | [04_System_Design.md](04_System_Design.md) §7; [18_Local_Version.md](18_Local_Version.md) §5 | TC-027 |
| NFR-007 | NFR | MVP | PROPOSED | 运行诊断与隐私 | 健康与就绪用于诊断，操作/审核日志保留180天且不复制秘密或身份字段；预约终结后180天、备份每日7份，恢复先运行到期清理。账号不可逆身份清除按停用30天和关联记录到期的较晚时点。 | 核对健康接口契约，并在日志策略获批后检查脱敏与保留。 | [04_System_Design.md](04_System_Design.md) §6; [18_Local_Version.md](18_Local_Version.md) §5 | TC-028 |
| NFR-008 | NFR | MVP | PROPOSED | 双语文档及追溯性 | 文档编号、版本、章节与需求编号须保持中俄一致；候选需求应记录设计及计划测试关系。 | 运行文档一致性检查并人工复核术语、需求语义及追溯状态。 | [04_System_Design.md](04_System_Design.md) §7; [18_Local_Version.md](18_Local_Version.md) §5 | TC-029 |
| BR-001 | BR | MVP | PROPOSED | 时间区间有效性 | 采用[start,end)，时刻带时区并UTC存储；上海业务起止必须整点/半点且秒微秒为0，时长至少30分钟、不超过24小时，起点严格晚于锁后now，结束可为该业务日次日00:00边界。 | 验证零长、反向及相邻区间，预期以批准规则为准。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | TC-030 |
| BR-002 | BR | MVP | PROPOSED | 座位占用互斥 | 同seat有效预约不得重叠；取消记录不占用，相邻[start,end)不冲突；房间容量不作为整室预约或共享同一seat的替代。 | 验证覆盖、包含、部分重叠及不同资源场景。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | TC-031 |
| BR-003 | BR | MVP | PROPOSED | 开放时间限制 | 默认所有星期与节假日按08:00–22:00开放，管理员明确例外优先；预约须在单个业务日允许窗口内，默认最多14小时。配置全天00:00–24:00时才有24h合法正例。 | 验证开放边界、关闭时段和经批准的例外。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | TC-032 |
| BR-004 | BR | MVP | PROPOSED | 预约配额及提前量 | 每学生的未取消预约时段不得重叠，但允许多条非重叠预约，包括同日及不同未来日；没有全局未结束总量限制。每条仅1seat且最多24h，仍符合开放时间、30分钟及今天至+6规则。相邻[start,end)允许。 | 计划：同学生同/不同seat重叠拒绝，包含与部分重叠拒绝，非重叠同日/不同日及相邻均允许；并发重叠仅1成功，非重叠均成功；取消仅影响其时段。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | TC-033 |
| BR-005 | BR | MVP | PROPOSED | 取消时限及后果 | 学生仅锁后now<start时取消本人预约；开始及之后仅ADMIN有原因取消。重复取消幂等不重复计数；停止资源/账号所致取消也有原因并原子释放座位与配额。 | 规则确认后测试截止前后及重复取消。 | [04_System_Design.md](04_System_Design.md) §3.3; [18_Local_Version.md](18_Local_Version.md) §3 | TC-034 |
| BR-006 | BR | MVP | PROPOSED | 账号资格及角色授予 | 只有启用STUDENT可预约，身份模式固定LOCAL_ONLY；注册不能指定ADMIN，管理员显式CLI创建且无默认密码。角色变更及停用撤销会话，离开学生资格取消未结束预约。 | 批准资格与权限策略后验证注册、角色变更和停用。 | [04_System_Design.md](04_System_Design.md) §3.1; [18_Local_Version.md](18_Local_Version.md) §3 | TC-035 |
| BR-007 | BR | MVP | PROPOSED | 资源停用与历史记录 | 房间/seat停用或开放缩减时，同事务取消受影响未结束预约并记录理由；启用不恢复旧预约。保存历史资源，以软停用代替物理删除；预约终结后保留180天。 | 验证停用后的新预约行为及批准的历史处理。 | [04_System_Design.md](04_System_Design.md) §3.4; [18_Local_Version.md](18_Local_Version.md) §3 | TC-036 |
| BR-008 | BR | MVP | PROPOSED | 时区与日期解释 | 学校业务默认Asia/Shanghai，UTC保存时刻并按该时区解释自然日；日区间[D00:00,(D+1)00:00)，次日00:00仅可为结束边界。设备时区无效；未来范围按锁后业务今天至+6计算。 | 时区获批后验证本地日期、跨日和转换边界。 | [04_System_Design.md](04_System_Design.md) §5; [18_Local_Version.md](18_Local_Version.md) §3 | TC-037 |
| FR-022 | FR | MVP | RETIRED | 校内身份人工审核 | DEC-018：用户明确取消真实学校身份验证，本地课程版本不实现该审核流程；保留编号，不伪造VERIFIED。 | 计划验证待审核、拒绝、重新申请、通过、重复学号及账号停用竞争；真实来源先与学校确认，所有用例NOT_RUN。 | [04_System_Design.md](04_System_Design.md) §3.1 | TC-038 |
<!-- GENERATED:END -->

## 3 评审与状态转换

评审后补充业务来源、负责人、批准日期、可测量验收条件及影响；只有有权审阅人批准后改为APPROVED。APPROVED、IMPLEMENTED或VERIFIED须记录approval（approved_by、approved_at、evidence）；IMPLEMENTED或VERIFIED另需真实且非空的implementation，VERIFIED须关联有证据的PASS用例。实现、验证和接受需独立证据，不由文档编写自动转换。撤销或否决使用RETIRED并保留ID与理由，严禁重用。双语更新后重生成登记和追溯，并检查TC双向引用。

## 4 未建立的基线

目前无批准需求基线、真实用户研究、业务实现映射或业务测试结果。用户已确认与授权制定的规则见16_Requirements_Clarification.md及project-decisions.json；仍未落实的是学校核验来源、课程具体条件与部署机位/域名。性能实测未执行，课程标准未确认。
