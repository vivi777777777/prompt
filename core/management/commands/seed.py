"""填充示例数据：python manage.py seed"""

from django.core.management.base import BaseCommand

from core.models import Server, Model


SERVERS = [
    ("OpenAI", "https://api.openai.com/v1", "OpenAI", "https://openai.com"),
    ("阿里云百炼(通义)", "https://dashscope.aliyuncs.com/compatible-mode/v1", "阿里巴巴", "https://www.aliyun.com"),
    ("硅基流动", "https://api.siliconflow.cn/v1", "硅基流动", "https://siliconflow.cn"),
    ("智谱AI", "https://open.bigmodel.cn/api/paas/v4", "智谱华章", "https://www.zhipuai.cn"),
    ("月之暗面", "https://api.moonshot.cn/v1", "月之暗面", "https://www.moonshot.cn"),
    ("百度文心", "https://qianfan.baidubce.com/v2", "百度", "https://cloud.baidu.com"),
    ("深度求索", "https://api.deepseek.com/v1", "深度求索", "https://www.deepseek.com"),
    ("火山方舟", "https://ark.cn-beijing.volces.com/api/v3", "火山引擎", "https://www.volcengine.com"),
]

MODELS = [
    # svc_idx(1-based), model_name, in, out, unit, type, url
    (1, "GPT-4o", 2.5, 10.0, "百万", "对话", ""),
    (1, "GPT-4o-mini", 0.15, 0.6, "百万", "对话", ""),
    (2, "通义千问-Max", 2.4, 9.6, "百万", "对话", ""),
    (2, "通义千问-VL", 4.0, 12.0, "百万", "生图,对话", ""),
    (3, "DeepSeek-V3", 1.0, 2.0, "百万", "对话", ""),
    (3, "Qwen2.5-72B", 4.0, 4.0, "百万", "对话,嵌入", ""),
    (4, "GLM-4-Plus", 3.0, 10.0, "百万", "对话", ""),
    (7, "DeepSeek-R1", 4.0, 16.0, "百万", "对话,推理", ""),
]


class Command(BaseCommand):
    help = "填充 server / model 示例数据（幂等）"

    def handle(self, *args, **options):
        if Server.objects.exists():
            self.stdout.write(self.style.WARNING("server 已有数据，跳过填充。"))
            return

        servers = []
        for plat_name, base_url, company, homepage in SERVERS:
            servers.append(Server.objects.create(
                plat_name=plat_name, base_url=base_url, company=company, homepage=homepage
            ))
        self.stdout.write(self.style.SUCCESS(f"已创建 {len(servers)} 个服务"))

        count = 0
        for svc_idx, name, i_fee, o_fee, unit, mtype, url in MODELS:
            Model.objects.create(
                svc=servers[svc_idx - 1],
                model_name=name,
                in_token_fee=i_fee,
                out_token_fee=o_fee,
                unit=unit,
                type=mtype,
                url=url,
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"已创建 {count} 个模型"))
