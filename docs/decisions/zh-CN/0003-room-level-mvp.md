# ADR-0003：单座位级MVP范围

> 历史草案范围提示：2026-10-23 的 DEC-018 与 [本地版本说明](../../zh-CN/18_Local_Version.md) 已覆盖本文件涉及真实学校核验、远程域名/HTTPS和初始化未实现状态的旧约束；其余稳定规则保留。


| Metadata | Value |
| --- | --- |
| Doc-ID | ADR-0003 |
| Version | 0.3.0 |
| Status | DRAFT |
| Updated | 2026-10-12 |
| Language | zh-CN |
| Decision-Status | ACCEPTED |

> 0.3.0需求整理草稿：CONFIRMED表示用户明确答复，DELEGATED表示依据用户授权作出的课程项目设计决定；两者均不代表整份SRS已审阅、学校现行政策、业务实现或验收。所有正式需求仍为PROPOSED。

## 1 上下文与历史

0.1.0曾按房间级MVP提出PROPOSED假设，未获批准；用户新答复明确要求单座位，旧假设被取代。为追溯保留ADR-0003及历史路径0003-room-level-mvp.md，文件名不表示现行预约粒度。

## 2 已接受决定

Decision-Status为ACCEPTED：MVP预约一个Seat，不提供整室预约。FR-017原编号保留并改为MVP，FR-022加入校内审核；FR-018至FR-021仍未来。Seat以(room_id,seat_code)唯一且有enabled，Room容量从启用Seat计数。列表/网格即可，无必须图形座位图；界面中俄英，正式文档中俄。

## 3 约束与后果

学生必须校内身份VERIFIED。一次一个seat；同学生非取消预约按existing.start < new.end AND new.start < existing.end判冲突，同/不同seat重叠均拒绝。非重叠未来多条及相邻允许（同日/不同日），不设每日/未来总数配额；取消只释放该时段，其他预约保持。DEC-016明确纠正并取代DEC-004旧全局解释，保留历史ID。最长24小时还受单一业务自然日和开放限制，默认08:00–22:00实际最多14小时。冲突键转为Seat；查询、管理、时间与关闭/停用事务需围绕座位设计和测试。

## 4 决定状态与未完成工作

用户范围CONFIRMED，具体时间/身份/隐私/资源策略按DELEGATED授权选定；此ADR技术/范围决定ACCEPTED不意味着整份SRS或需求APPROVED。正式文档DRAFT，所有需求PROPOSED，领域实体与预约尚未实现、测试TC未执行。OPEN-002已CLOSED；OPEN-003校内真实证据来源仍PARTIAL。
