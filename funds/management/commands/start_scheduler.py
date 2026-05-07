"""
Django 管理命令 - 启动基金数据定时更新调度器
"""
from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '启动基金数据定时更新调度器'

    def handle(self, *args, **options):
        _ = args, options  # 暂时忽略参数
        self.stdout.write(self.style.SUCCESS('启动调度器...'))

        # 创建调度器
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)

        # 添加定时任务 - 从 settings 读取间隔（默认 30 分钟）
        interval_minutes = getattr(settings, 'FUND_UPDATE_INTERVAL', 30)

        scheduler.add_job(
            self.update_fund_data,
            trigger=IntervalTrigger(minutes=interval_minutes),
            id='update_fund_realtime',
            name='更新基金实时数据',
            replace_existing=True
        )

        # 启动调度器
        scheduler.start()
        self.stdout.write(self.style.SUCCESS(f'调度器已启动，每 {interval_minutes} 分钟更新一次基金数据'))

        try:
            # 保持调度器运行
            import time
            while True:
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            self.stdout.write(self.style.WARNING('调度器已停止'))

    def update_fund_data(self):
        """更新基金数据"""
        from funds.tasks import update_all_popular_funds

        try:
            update_all_popular_funds()
            logger.info('基金数据更新任务执行完成')
        except Exception as e:
            logger.error(f'基金数据更新任务执行失败: {e}')
