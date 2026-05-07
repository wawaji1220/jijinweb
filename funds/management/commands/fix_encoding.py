"""
Django管理命令: 修复数据库中的乱码
使用方法: python manage.py fix_encoding
"""
from django.core.management.base import BaseCommand
from funds.models import Fund
from funds.services.fund_fetcher_real import fund_fetcher_real
from funds.services.cache_manager import cache_manager
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '修复数据库中的乱码数据'

    def handle(self, *args, **options):
        funds = Fund.objects.all()
        total = funds.count()

        self.stdout.write(f'开始修复数据库乱码, 共 {total} 只基金...')

        fixed_count = 0
        failed_count = 0

        for fund in funds:
            try:
                # 从真实API获取数据
                realtime_data = fund_fetcher_real.fetch_fund_realtime_data(fund.fund_code)

                if realtime_data and realtime_data.get('name'):
                    # 更新基金名称
                    old_name = fund.fund_name
                    fund.fund_name = realtime_data['name']
                    fund.save()

                    # 更新缓存
                    cache_manager.set_fund_realtime(fund.fund_code, realtime_data)

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'修复成功: {fund.fund_code} | {realtime_data["name"]}'
                        )
                    )
                    fixed_count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f'获取失败: {fund.fund_code}')
                    )
                    failed_count += 1

            except Exception as e:
                logger.error(f'修复基金 {fund.fund_code} 失败: {str(e)}')
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'修复完成: 成功 {fixed_count} 只, 失败 {failed_count} 只'
            )
        )
