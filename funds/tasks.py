"""
异步任务 - 使用Celery或APScheduler定期更新基金数据
"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def update_fund_realtime_data(fund_codes):
    """
    更新基金实时数据

    Args:
        fund_codes: 基金代码列表
    """
    from .services.fund_fetcher_real import fund_fetcher_real
    from .services.cache_manager import cache_manager

    logger.info(f"开始更新基金实时数据, 共 {len(fund_codes)} 只基金")

    success_count = 0
    fail_count = 0

    for fund_code in fund_codes:
        try:
            data = fund_fetcher_real.fetch_fund_realtime_data(fund_code)
            if data:
                cache_manager.set_fund_realtime(fund_code, data)
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            logger.error(f"更新基金 {fund_code} 数据失败: {str(e)}")
            fail_count += 1

    logger.info(f"基金实时数据更新完成, 成功: {success_count}, 失败: {fail_count}")


def update_all_popular_funds():
    """更新所有热门基金的实时数据"""
    from .models import Fund

    fund_codes = list(Fund.objects.values_list('fund_code', flat=True))
    update_fund_realtime_data(fund_codes)


# 如果使用Celery,可以添加以下任务:
"""
from celery import shared_task
from django.conf import settings

@shared_task
def celery_update_fund_realtime():
    '''Celery定时任务 - 更新基金实时数据'''
    update_all_popular_funds()

@shared_task
def celery_update_fund_history():
    '''Celery定时任务 - 更新基金历史数据'''
    from .models import Fund
    from .services.fund_fetcher_real import fund_fetcher_real
    from .services.cache_manager import cache_manager

    funds = Fund.objects.all()[:50]  # 更新前50只基金

    for fund in funds:
        try:
            history_data = fund_fetcher_real.fetch_fund_history_nav(fund.fund_code, per_page=30)
            if history_data:
                cache_manager.set_fund_history(fund.fund_code, history_data)
        except Exception as e:
            logger.error(f"更新基金 {fund.fund_code} 历史数据失败: {str(e)}")
"""
