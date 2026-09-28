-- ============================================================
-- 数据库建表语句：服务表 & 模型表
-- 字符集：utf8mb4（支持中文与 emoji）  引擎：InnoDB
-- 命名约定：表名/字段名使用英文简写，注释用中文
-- ============================================================

-- ----------------------------
-- 服务表（对应原「服务表」）
-- ----------------------------
CREATE TABLE `server` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `plat_name`  VARCHAR(100)    NOT NULL DEFAULT '' COMMENT '平台/官方名',
  `base_url`   VARCHAR(255)    NOT NULL DEFAULT '' COMMENT 'API 网址 (base_url)',
  `company`    VARCHAR(100)    NOT NULL DEFAULT '' COMMENT '公司名',
  `homepage`   VARCHAR(255)    NOT NULL DEFAULT '' COMMENT '首页地址',
  PRIMARY KEY (`id`),
  KEY `idx_plat_name` (`plat_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='服务表';

-- ----------------------------
-- 模型表（对应原「模型表」）
-- 外键 svc_id 关联 服务表.id
-- ----------------------------
CREATE TABLE `model` (
  `id`           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `svc_id`       BIGINT UNSIGNED NOT NULL COMMENT '服务ID（关联 server.id）',
  `model_name`   VARCHAR(100)    NOT NULL DEFAULT '' COMMENT '模型名',
  `in_token_fee` DECIMAL(12,6)   NOT NULL DEFAULT 0.000000 COMMENT '输入 token 计费',
  `out_token_fee` DECIMAL(12,6)  NOT NULL DEFAULT 0.000000 COMMENT '输出 token 计费',
  `unit`         VARCHAR(20)     NOT NULL DEFAULT '' COMMENT '单位（K / 万 / 十万 / 百万）',
  `type`         VARCHAR(50)     NOT NULL DEFAULT '' COMMENT '类型（对话/视频/嵌入/生图/语音/重排，多值用逗号分隔）',
  `url`          VARCHAR(255)    NOT NULL DEFAULT '' COMMENT '网址',
  PRIMARY KEY (`id`),
  KEY `idx_svc_id` (`svc_id`),
  CONSTRAINT `fk_model_svc` FOREIGN KEY (`svc_id`)
    REFERENCES `server` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='模型表';
