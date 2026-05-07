"""
Django管理命令: 获取基金数据
使用方法: python manage.py fetch_fund_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import logging

from funds.models import Fund
from funds.services.fund_fetcher_real import fund_fetcher_real
from funds.services.cache_manager import cache_manager

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '获取并更新基金数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--code',
            type=str,
            help='指定基金代码',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='更新所有基金',
        )
        parser.add_argument(
            '--history',
            action='store_true',
            help='同时更新历史数据',
        )

    def handle(self, *args, **options):
        fund_code = options.get('code')
        update_all = options.get('all')
        update_history = options.get('history')

        if fund_code:
            self.update_single_fund(fund_code, update_history)
        elif update_all:
            self.update_all_funds(update_history)
        else:
            self.stdout.write(
                self.style.WARNING('请指定 --code 或 --all 参数')
            )

    def update_single_fund(self, fund_code, update_history):
        """更新单个基金数据"""
        self.stdout.write(f'开始获取基金 {fund_code} 的数据...')

        # 获取或创建基金
        fund, created = Fund.objects.get_or_create(
            fund_code=fund_code,
            defaults={'fund_name': '未命名基金'}
        )

        # 获取实时数据
        realtime_data = fund_fetcher_real.fetch_fund_realtime_data(fund_code)
        if realtime_data:
            # 更新基金信息
            if realtime_data.get('name'):
                fund.fund_name = realtime_data['name']
            if realtime_data.get('estimated_nav'):
                fund.estimated_nav = realtime_data['estimated_nav']
            fund.save()

            # 更新缓存
            cache_manager.set_fund_realtime(fund_code, realtime_data)

            self.stdout.write(
                self.style.SUCCESS(f'基金 {fund_code} 实时数据更新成功')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'基金 {fund_code} 实时数据获取失败')
            )

        # 获取历史数据
        if update_history:
            history_data = fund_fetcher_real.fetch_fund_history_nav(fund_code, per_page=30)
            if history_data:
                cache_manager.set_fund_history(fund_code, history_data)
                self.stdout.write(
                    self.style.SUCCESS(f'基金 {fund_code} 历史数据更新成功, 共 {len(history_data)} 条记录')
                )

    def update_all_funds(self, update_history):
        """更新所有基金数据"""
        funds = Fund.objects.all()
        total = funds.count()

        self.stdout.write(f'开始更新所有基金数据, 共 {total} 只基金...')

        success_count = 0
        fail_count = 0

        for fund in funds:
            try:
                # 获取实时数据
                realtime_data = fund_fetcher_real.fetch_fund_realtime_data(fund.fund_code)
                if realtime_data:
                    # 更新基金信息
                    if realtime_data.get('name'):
                        fund.fund_name = realtime_data['name']
                    fund.save()

                    # 更新缓存
                    cache_manager.set_fund_realtime(fund.fund_code, realtime_data)
                    success_count += 1
                else:
                    fail_count += 1

                # 获取历史数据
                if update_history:
                    history_data = fund_fetcher_real.fetch_fund_history_nav(fund.fund_code, per_page=30)
                    if history_data:
                        cache_manager.set_fund_history(fund.fund_code, history_data)

            except Exception as e:
                logger.error(f'更新基金 {fund.fund_code} 失败: {str(e)}')
                fail_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'更新完成: 成功 {success_count} 只, 失败 {fail_count} 只'
            )
        )
