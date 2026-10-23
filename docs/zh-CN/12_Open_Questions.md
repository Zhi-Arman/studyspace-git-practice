# StudySpace 澄清事项与决定状态

| Metadata | Value |
| --- | --- |
| Doc-ID | DOC-12 |
| Version | 0.3.0 |
| Status | DRAFT |
| Updated | 2026-10-12 |
| Language | zh-CN |

> 0.3.0需求整理草稿：CONFIRMED表示用户明确答复，DELEGATED表示依据用户授权作出的课程项目设计决定；两者均不代表整份SRS已审阅、学校现行政策、业务实现或验收。所有正式需求仍为PROPOSED。

## 1 来源、状态与边界

本版纳入用户对15项OPEN的答复及对自主设计的授权；DEC-016纠正学生时段规则，DEC-017附图确认四个课堂主角色。CONFIRMED为直接答复，DELEGATED为授权选择的课程策略，不声称学校政策。CLOSED表示该问题已有决定；PARTIAL表示明确列出的外部条件仍缺，不能把已定部分重新写成未知。正式需求仍PROPOSED，整份SRS及老师验收未执行。

## 2 澄清登记

| ID | 已定内容与来源 | 剩余条件 | 责任人 | Status |
| --- | --- | --- | --- | --- |
| OPEN-001 | CONFIRMED四人顺序不变；DEC-017：A支浩然分析员/ТЗ作者、B俞智文文档编辑、C曹浩然测试员、D吕嘉伟项目经理（期限/风险/паспорт）；全员开发由D组织，主题轮换须交接，三人兼任备注不减员 | 无规模未决；不代表工作已完成 | D吕嘉伟 | CLOSED |
| OPEN-002 | CONFIRMED单座位MVP，无整室预约；FR-017保留ID进入MVP | 无粒度未决 | A支浩然 / C曹浩然 | CLOSED |
| OPEN-003 | CONFIRMED校内身份必须验证；DELEGATED管理员人工核验，PENDING可登录但不可预约，只有VERIFIED可预约，拒绝可复核；无可信渠道fail closed | 学校实际可信证明/名单/平台来源渠道需学校确定，无虚构邮箱域或SSO | A支浩然 / C曹浩然 | PARTIAL |
| OPEN-004 | CONFIRMED每次一个seat、每个重叠时间段仅一预约；DEC-016纠正DEC-004旧全局配额解释：同user未取消[start,end)互斥，非重叠未来多条及相邻允许（同日/不同日），不设每日/未来总数配额；DELEGATED硬上限24h、最短/粒度30min、start严格>锁后now、7个业务自然日 | 无规则阈值未决；默认08–22使实际最长14h | A支浩然 / C曹浩然 | CLOSED |
| OPEN-005 | DELEGATED每日08–22，同一业务日；学生now<start可取消，开始后admin附原因；关闭/停用同事务取消受影响未结束预约并记原因；重复取消幂等，单条取消仅释放该时段、其他预约保持 | 无策略未决；实现与测试尚未完成 | C曹浩然 / D吕嘉伟 | CLOSED |
| OPEN-006 | DELEGATED Asia/Shanghai业务日期与显示、UTC存储；[start,end)，D的24:00结束可为次日00:00且不占次日 | 无时区未决 | A支浩然 / C曹浩然 | CLOSED |
| OPEN-007 | DELEGATED最少数据，User存必要学号姓名；日志无密码token影像/原始身份复制；预约终结起180天、事件event_at起180天；停用≥30天且无未结束后有资格、清除取停用+30与关联180到期最大；备份每日7份恢复前清理且不外发 | 课程策略已定，不声称法律合规；实际生命周期测试尚未完成 | A支浩然 / C曹浩然 | CLOSED |
| OPEN-008 | CONFIRMED由老师验收 | 老师姓名、实际期限、评分、提交格式未提供 | D吕嘉伟 | PARTIAL |
| OPEN-009 | CONFIRMED界面中俄英；正式文档中俄；列表/网格与三语同键维护纳入前端规划 | 不声明任何无障碍认证；实际设备/三语测试未执行 | B俞智文 / C曹浩然 | CLOSED |
| OPEN-010 | CONFIRMED部署地点未知且优先Docker+HTTPS；DELEGATED Docker Compose+Caddy HTTPS，PostgreSQL部署目标 | 位置、域名、证书/公网条件和实际部署未确定 | D吕嘉伟 / C曹浩然 | PARTIAL |
| OPEN-011 | DELEGATED校区/楼栋/楼层/房间名/CLASSROOM或STUDY_ROOM；Seat唯一(room_id,seat_code)、enabled，容量启用seat数，无整室预约；列表/网格无需图形图 | 规则字段已定；不编造真实学校资源数据 | B俞智文 / C曹浩然 | CLOSED |
| OPEN-012 | DELEGATED统一预约业务日期D+as_of：截至快照创建数/取消数/非取消且end>as_of数（含未来）；保留期外不可统计，不假0 | 不代表实际到场或使用率 | A支浩然 / C曹浩然 | CLOSED |
| OPEN-013 | DELEGATED首位admin显式命令、无默认密码/自助升权；停用用户立即事务取消其未结束预约；实际清除遵循30/180最大值 | 管理命令及功能未实现 | C曹浩然 / D吕嘉伟 | CLOSED |
| OPEN-014 | DELEGATED文档管理机制结合DEC-017：A目标/需求ТЗ，B术语/版本/格式/登记，C每条如何验证/TC/证据，D期限/风险/项目基本信息/老师协调；同伴审阅，主题轮换带交接，MAJOR.MINOR.PATCH和稳定ID | 整份SRS正式审阅仍未执行，不因此把问题重开 | A支浩然 / B俞智文 | CLOSED |
| OPEN-015 | DELEGATED SQLite开发/PostgreSQL部署；Alembic首个实体前引入，分别做迁移/回滚/并发验证 | 工具引入、领域模型和迁移验收尚未完成 | C曹浩然 / D吕嘉伟 | CLOSED |

## 3 下一次输入与状态维护

剩余外部输入聚焦OPEN-003真实校内证明来源、OPEN-008课程细节、OPEN-010位置域名。其余授权规则进入设计与计划测试，不再作为未知阻塞。来源、影响ID和细化策略详见需求登记与[本次决定记录](16_Requirements_Clarification.md)；双语、设计、测试、追溯和变更同时维护。性能量化与具体实现仍须后续设计，不伪造已调研或已通过。
