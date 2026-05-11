from django.db import models
from django.core.cache import cache


class Fund(models.Model):
    """基金基本信息模型"""
    fund_code = models.CharField('基金代码', max_length=10, unique=True, db_index=True)
    fund_name = models.CharField('基金名称', max_length=200)
    fund_type = models.CharField('基金类型', max_length=50, blank=True)
    fund_company = models.CharField('基金公司', max_length=100, blank=True)
    established_date = models.DateField('成立日期', null=True, blank=True)
    display_order = models.IntegerField('显示排序', default=0, db_index=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '基金信息'
        verbose_name_plural = '基金信息'
        ordering = ['display_order', '-updated_at']

    def __str__(self):
        return f"{self.fund_code} - {self.fund_name}"

    @property
    def latest_nav(self):
        """获取最新净值"""
        cache_key = f'fund_nav_{self.fund_code}'
        nav_data = cache.get(cache_key)
        if nav_data:
            return nav_data
        # 如果缓存没有，从数据库获取最新记录
        latest = self.nav_records.first()
        if latest:
            return {
                'unit_nav': latest.unit_nav,
                'accumulated_nav': latest.accumulated_nav,
                'daily_growth': latest.daily_growth,
                'nav_date': latest.nav_date,
                'estimated_nav': latest.estimated_nav,
                'estimated_growth': latest.estimated_growth,
            }
        return None


class FundNav(models.Model):
    """基金净值历史记录模型"""
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='nav_records', verbose_name='基金')
    nav_date = models.DateField('净值日期', db_index=True)
    unit_nav = models.DecimalField('单位净值', max_digits=10, decimal_places=4)
    accumulated_nav = models.DecimalField('累计净值', max_digits=10, decimal_places=4)
    daily_growth = models.DecimalField('日增长率', max_digits=8, decimal_places=4, null=True, blank=True)
    estimated_nav = models.DecimalField('估算净值', max_digits=10, decimal_places=4, null=True, blank=True)
    estimated_growth = models.DecimalField('估算增长率', max_digits=8, decimal_places=4, null=True, blank=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '基金净值记录'
        verbose_name_plural = '基金净值记录'
        ordering = ['-nav_date', '-updated_at']
        unique_together = ['fund', 'nav_date']

    def __str__(self):
        return f"{self.fund.fund_code} - {self.nav_date} - {self.unit_nav}"
