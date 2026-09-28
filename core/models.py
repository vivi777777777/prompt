"""Test_Prompt 数据模型：服务表 server、模型表 model。"""

from django.db import models


class Server(models.Model):
    """服务表：一个模型服务平台 / 官方（如 OpenAI、硅基流动）。"""

    plat_name = models.CharField("平台/官方名", max_length=100, default="")
    base_url = models.CharField("API 网址 (base_url)", max_length=255, default="")
    company = models.CharField("公司名", max_length=100, default="")
    homepage = models.CharField("首页地址", max_length=255, default="")

    class Meta:
        db_table = "server"
        verbose_name = "服务"
        verbose_name_plural = "服务"
        indexes = [models.Index(fields=["plat_name"], name="idx_plat_name")]

    def __str__(self):
        return self.plat_name or f"server#{self.id}"


class Model(models.Model):
    """模型表：某服务下的具体模型，关联 server（外键级联删除）。"""

    svc = models.ForeignKey(
        Server,
        on_delete=models.CASCADE,
        db_column="svc_id",
        verbose_name="服务ID",
    )
    model_name = models.CharField("模型名", max_length=100, default="")
    in_token_fee = models.DecimalField("输入 token 计费", max_digits=12, decimal_places=6, default=0)
    out_token_fee = models.DecimalField("输出 token 计费", max_digits=12, decimal_places=6, default=0)
    unit = models.CharField("单位", max_length=20, default="")  # K / 万 / 十万 / 百万
    type = models.CharField("类型", max_length=50, default="")  # 对话/视频/嵌入/生图/语音/重排，逗号分隔
    url = models.CharField("网址", max_length=255, default="")

    class Meta:
        db_table = "model"
        verbose_name = "模型"
        verbose_name_plural = "模型"
        indexes = [models.Index(fields=["svc_id"], name="idx_svc_id")]

    def __str__(self):
        return self.model_name or f"model#{self.id}"
