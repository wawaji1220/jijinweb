"""
基金应用视图
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
import logging

from .models import Fund, FundNav
from .services.fund_fetcher_real import fund_fetcher_real
from .services.cache_manager import cache_manager
from .utils.chart_generator import ChartGenerator

logger = logging.getLogger(__name__)


@require_GET
def index(request):
    """首页 - 显示热门基金列表"""
    # 获取热门基金(最近更新的)
    popular_funds = Fund.objects.all()[:50]

    context = {
        'popular_funds': popular_funds,
        'page_title': '基金净值实时估算',
    }
    return render(request, 'funds/index.html', context)


@require_GET
def fund_detail(request, fund_code):
    """基金详情页"""
    fund = get_object_or_404(Fund, fund_code=fund_code)

    # 尝试从缓存获取实时数据
    realtime_data = cache_manager.get_fund_realtime(fund_code)

    # 如果缓存没有,则获取实时数据
    if not realtime_data:
        realtime_data = fund_fetcher_real.fetch_fund_realtime_data(fund_code)
        if realtime_data:
            cache_manager.set_fund_realtime(fund_code, realtime_data)

    # 获取历史净值数据(最近30天)
    history_data = cache_manager.get_fund_history(fund_code)
    if not history_data:
        history_data = fund_fetcher_real.fetch_fund_history_nav(fund_code, per_page=30)
        if history_data:
            cache_manager.set_fund_history(fund_code, history_data)

    # 生成图表
    chart_generator = ChartGenerator()
    nav_chart = chart_generator.generate_nav_chart(history_data)

    context = {
        'fund': fund,
        'realtime_data': realtime_data,
        'history_data': history_data,
        'nav_chart': nav_chart,
        'page_title': f'{fund.fund_name} - 基金详情',
    }
    return render(request, 'funds/detail.html', context)


@require_GET
def search(request):
    """搜索基金"""
    keyword = request.GET.get('q', '').strip()

    if not keyword:
        return render(request, 'funds/search.html', {
            'page_title': '基金搜索',
            'keyword': keyword,
            'results': [],
        })

    # 先从缓存获取
    cached_results = cache_manager.get_search_result(keyword)
    if cached_results:
        results = cached_results
    else:
        # 从数据库搜索
        db_results = Fund.objects.filter(
            Q(fund_code__icontains=keyword) | Q(fund_name__icontains=keyword)
        )[:20]

        # 如果数据库结果不足,从网络搜索
        if len(db_results) < 20:
            web_results = fund_fetcher_real.search_funds(keyword)
            results = list(db_results) + web_results[:20-len(db_results)]
        else:
            results = list(db_results)

        # 缓存结果
        cache_manager.set_search_result(keyword, results)

    # 分页
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': f'基金搜索 - {keyword}',
        'keyword': keyword,
        'page_obj': page_obj,
        'results': page_obj,
    }
    return render(request, 'funds/search.html', context)


@csrf_exempt
def api_fund_realtime(request):
    """API: 获取基金实时数据"""
    fund_code = request.GET.get('code')
    force_refresh = request.GET.get('force', 'false').lower() == 'true'

    if not fund_code:
        return JsonResponse({'error': '请提供基金代码'}, status=400)

    # 强制刷新时清除缓存
    if force_refresh:
        cache_manager.clear_fund_cache(fund_code)

    # 尝试从缓存获取(非强制刷新时)
    data = cache_manager.get_fund_realtime(fund_code) if not force_refresh else None

    if not data:
        data = fund_fetcher_real.fetch_fund_realtime_data(fund_code)
        if data:
            cache_manager.set_fund_realtime(fund_code, data)

    if data:
        return JsonResponse({
            'success': True,
            'data': data,
            'cached': not force_refresh and bool(cache_manager.get_fund_realtime(fund_code))
        })
    else:
        return JsonResponse({
            'success': False,
            'error': '获取数据失败'
        }, status=500)


@csrf_exempt
def api_fund_history(request):
    """API: 获取基金历史净值数据"""
    fund_code = request.GET.get('code')
    days = int(request.GET.get('days', 30))

    if not fund_code:
        return JsonResponse({'error': '请提供基金代码'}, status=400)

    # 尝试从缓存获取
    data = cache_manager.get_fund_history(fund_code)

    if not data:
        data = fund_fetcher_real.fetch_fund_history_nav(fund_code, per_page=days)
        if data:
            cache_manager.set_fund_history(fund_code, data)

    if data:
        return JsonResponse({
            'success': True,
            'data': data[:days],
        })
    else:
        return JsonResponse({
            'success': False,
            'error': '获取数据失败'
        }, status=500)


@csrf_exempt
def api_fund_search(request):
    """API: 搜索基金"""
    keyword = request.GET.get('q', '').strip()

    if not keyword:
        return JsonResponse({'error': '请提供搜索关键词'}, status=400)

    # 从数据库搜索
    db_results = list(Fund.objects.filter(
        Q(fund_code__icontains=keyword) | Q(fund_name__icontains=keyword)
    ).values('fund_code', 'fund_name', 'fund_type')[:20])

    # 如果数据库结果不足,从网络搜索
    if len(db_results) < 20:
        web_results = fund_fetcher_real.search_funds(keyword)
        results = db_results + web_results[:20-len(db_results)]
    else:
        results = db_results

    return JsonResponse({
        'success': True,
        'data': results
    })


@csrf_exempt
def api_fund_info(request):
    """API: 获取基金基本信息（名称和类型）"""
    fund_code = request.GET.get('code', '').strip()

    if not fund_code:
        return JsonResponse({'error': '请提供基金代码'}, status=400)

    try:
        fund_name = None
        fund_type = None

        # 如果数据库中已有该基金，使用数据库中的信息
        db_fund = Fund.objects.filter(fund_code=fund_code).first()
        if db_fund:
            fund_name = db_fund.fund_name
            fund_type = db_fund.fund_type

        # 从东方财富获取基金名称和类型
        eastmoney_info = fund_fetcher_real._get_fund_info_from_html(fund_code)
        if eastmoney_info:
            if not fund_name:
                fund_name = eastmoney_info.get('fund_name')
            if not fund_type and eastmoney_info.get('fund_type'):
                fund_type = eastmoney_info.get('fund_type')

        # 如果东方财富获取失败，尝试从新浪获取
        if not fund_name:
            sina_data = fund_fetcher_real._fetch_sina_realtime(fund_code)
            if sina_data:
                fund_name = sina_data.get('name')

        if not fund_name:
            return JsonResponse({
                'success': False,
                'error': '无法获取基金信息，请检查基金代码是否正确'
            }, status=404)

        return JsonResponse({
            'success': True,
            'data': {
                'fund_code': fund_code,
                'fund_name': fund_name,
                'fund_type': fund_type
            }
        })
    except Exception as e:
        logger.error(f"获取基金 {fund_code} 信息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '获取基金信息失败'
        }, status=500)


@csrf_exempt
@require_POST
def api_add_fund(request):
    """API: 添加基金到首页"""
    try:
        fund_code = request.POST.get('code', '').strip()
        fund_name = request.POST.get('name', '').strip()
        fund_type = request.POST.get('type', '').strip()

        if not fund_code:
            return JsonResponse({
                'success': False,
                'error': '请提供基金代码'
            }, status=400)

        # 检查基金是否已存在
        if Fund.objects.filter(fund_code=fund_code).exists():
            return JsonResponse({
                'success': False,
                'error': '基金已存在'
            }, status=400)

        # 创建基金
        fund = Fund.objects.create(
            fund_code=fund_code,
            fund_name=fund_name or f'基金{fund_code}',
            fund_type=fund_type or '未知'
        )

        return JsonResponse({
            'success': True,
            'message': '基金添加成功',
            'data': {
                'fund_code': fund.fund_code,
                'fund_name': fund.fund_name,
                'fund_type': fund.fund_type
            }
        })
    except Exception as e:
        logger.error(f"添加基金失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '添加失败，请稍后重试'
        }, status=500)


@csrf_exempt
@require_POST
def api_delete_fund(request):
    """API: 从首页删除基金"""
    try:
        fund_code = request.POST.get('code', '').strip()

        if not fund_code:
            return JsonResponse({
                'success': False,
                'error': '请提供基金代码'
            }, status=400)

        # 查找并删除基金
        fund = Fund.objects.filter(fund_code=fund_code).first()
        if not fund:
            return JsonResponse({
                'success': False,
                'error': '基金不存在'
            }, status=404)

        fund.delete()

        # 清除缓存
        cache_manager.clear_fund_cache(fund_code)

        return JsonResponse({
            'success': True,
            'message': '基金删除成功'
        })
    except Exception as e:
        logger.error(f"删除基金失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '删除失败，请稍后重试'
        }, status=500)


@csrf_exempt
@require_GET
def api_settings_get(request):
    """API: 获取设置信息"""
    interval = getattr(settings, 'FUND_UPDATE_INTERVAL', 30)
    return JsonResponse({
        'success': True,
        'data': {
            'update_interval': interval
        }
    })


@csrf_exempt
@require_POST
def api_settings_update(request):
    """API: 更新设置"""
    try:
        import os
        from pathlib import Path

        interval = request.POST.get('update_interval', '').strip()

        if not interval:
            return JsonResponse({
                'success': False,
                'error': '请提供刷新间隔'
            }, status=400)

        try:
            interval = int(interval)
            if interval < 1:
                return JsonResponse({
                    'success': False,
                    'error': '刷新间隔不能小于1分钟'
                }, status=400)
            if interval > 1440:
                return JsonResponse({
                    'success': False,
                    'error': '刷新间隔不能超过1440分钟(24小时)'
                }, status=400)
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': '刷新间隔必须是数字'
            }, status=400)

        # 更新环境变量文件
        env_file = Path(settings.BASE_DIR) / '.env'
        if env_file.exists():
            content = env_file.read_text(encoding='utf-8')
            lines = []
            updated = False

            for line in content.splitlines():
                if line.startswith('FUND_UPDATE_INTERVAL='):
                    lines.append(f'FUND_UPDATE_INTERVAL={interval}')
                    updated = True
                else:
                    lines.append(line)

            if not updated:
                lines.append(f'FUND_UPDATE_INTERVAL={interval}')

            env_file.write_text('\n'.join(lines) + '\n', encoding='utf-8')

        # 更新运行时配置
        settings.FUND_UPDATE_INTERVAL = interval

        return JsonResponse({
            'success': True,
            'message': f'刷新间隔已设置为 {interval} 分钟',
            'data': {
                'update_interval': interval
            }
        })
    except Exception as e:
        logger.error(f"更新设置失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': '更新失败，请稍后重试'
        }, status=500)
