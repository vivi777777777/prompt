"""Test_Prompt 视图：登录/登出 + 服务器/模型/调试业务页面。"""

import json

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Model, Server


# ---------- 服务器 ----------
def server_list(request):
    if request.method == "POST":
        ids = request.POST.getlist("del_ids")
        if ids:
            Server.objects.filter(id__in=ids).delete()
        return redirect("server_list")

    plat = request.GET.get("plat", "").strip()
    company = request.GET.get("company", "").strip()
    qs = Server.objects.all().order_by("id")
    if plat:
        qs = qs.filter(plat_name__icontains=plat)
    if company:
        qs = qs.filter(company__icontains=company)
    return render(request, "server_list.html", {
        "servers": qs, "plat": plat, "company": company,
    })


def server_add(request):
    if request.method == "POST":
        plat_name = request.POST.get("plat_name", "").strip()
        base_url = request.POST.get("base_url", "").strip()
        company = request.POST.get("company", "").strip()
        homepage = request.POST.get("homepage", "").strip()
        if plat_name:  # 平台名为必填
            Server.objects.create(
                plat_name=plat_name, base_url=base_url, company=company, homepage=homepage
            )
            return redirect("server_list")
        return render(request, "server_add.html", {
            "err": "平台/官方名为必填",
            "plat_name": plat_name, "base_url": base_url, "company": company, "homepage": homepage,
        })
    return render(request, "server_add.html", {
        "plat_name": "", "base_url": "", "company": "", "homepage": "",
    })


def server_detail(request, pk):
    srv = get_object_or_404(Server, pk=pk)
    models = srv.model_set.all().order_by("id")
    return render(request, "server_detail.html", {"srv": srv, "models": models})


# ---------- 模型 ----------
def model_list(request):
    if request.method == "POST":
        ids = request.POST.getlist("del_ids")
        if ids:
            Model.objects.filter(id__in=ids).delete()
        return redirect("model_list")

    plat = request.GET.get("plat", "").strip()
    mtype = request.GET.get("mtype", "").strip()
    mname = request.GET.get("mname", "").strip()
    in_min = request.GET.get("in_min", "").strip()
    in_max = request.GET.get("in_max", "").strip()
    out_min = request.GET.get("out_min", "").strip()
    out_max = request.GET.get("out_max", "").strip()

    qs = Model.objects.select_related("svc").all().order_by("id")
    if plat:
        qs = qs.filter(svc__plat_name__icontains=plat)
    if mtype:
        qs = qs.filter(type__icontains=mtype)
    if mname:
        qs = qs.filter(model_name__icontains=mname)
    try:
        if in_min:
            qs = qs.filter(in_token_fee__gte=float(in_min))
        if in_max:
            qs = qs.filter(in_token_fee__lte=float(in_max))
        if out_min:
            qs = qs.filter(out_token_fee__gte=float(out_min))
        if out_max:
            qs = qs.filter(out_token_fee__lte=float(out_max))
    except ValueError:
        pass

    return render(request, "model_list.html", {
        "models": qs,
        "plat": plat, "mtype": mtype, "mname": mname,
        "in_min": in_min, "in_max": in_max, "out_min": out_min, "out_max": out_max,
        "servers": Server.objects.all().order_by("plat_name"),
    })


def model_add(request):
    servers = Server.objects.all().order_by("plat_name")
    if request.method == "POST":
        svc_id = request.POST.get("svc_id")
        model_name = request.POST.get("model_name", "").strip()
        in_fee = request.POST.get("in_token_fee", "").strip()
        out_fee = request.POST.get("out_token_fee", "").strip()
        unit = request.POST.get("unit", "").strip()
        mtype = ",".join(request.POST.getlist("type"))  # 多选
        url = request.POST.get("url", "").strip()

        errs = {}
        if not svc_id:
            errs["svc_id"] = "请选择服务器"
        if not model_name:
            errs["model_name"] = "模型名为必填"
        try:
            in_fee = float(in_fee) if in_fee else 0.0
            out_fee = float(out_fee) if out_fee else 0.0
        except ValueError:
            errs["fee"] = "计费只能为数字"

        if not errs:
            Model.objects.create(
                svc_id=svc_id, model_name=model_name,
                in_token_fee=in_fee, out_token_fee=out_fee,
                unit=unit, type=mtype, url=url,
            )
            return redirect("model_list")

        return render(request, "model_add.html", {
            "servers": servers, "errs": errs,
            "svc_id": svc_id, "model_name": model_name,
            "in_token_fee": in_fee, "out_token_fee": out_fee,
            "unit": unit, "type": request.POST.getlist("type"), "url": url,
        })
    return render(request, "model_add.html", {
        "servers": servers, "errs": {}, "svc_id": "", "model_name": "",
        "in_token_fee": "", "out_token_fee": "", "unit": "", "type": [], "url": "",
    })


# ---------- 提示词调试 ----------
def debug(request):
    servers = Server.objects.all().order_by("id")
    models = Model.objects.select_related("svc").all().order_by("id")
    # 传给前端的模型费率表：[{id, name, in_fee, out_fee, unit}]
    model_fees = [
        {"id": m.id, "name": m.model_name,
         "in_fee": float(m.in_token_fee), "out_fee": float(m.out_token_fee),
         "unit": m.unit}
        for m in models
    ]
    return render(request, "debug.html", {
        "servers": servers, "models": models,
        "model_fees_json": json.dumps(model_fees, ensure_ascii=False),
    })
