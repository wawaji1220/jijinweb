"""
基金应用管理后台配置
"""
from django.contrib import admin
from .models import Fund, FundNav


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    """基金信息管理"""
    list_display = ['fund_code', 'fund_name', 'fund_type', 'fund_company', 'established_date', 'updated_at']
    list_filter = ['fund_type', 'established_date', 'updated_at']
    search_fields = ['fund_code', 'fund_name', 'fund_company']
    list_per_page = 50
    ordering = ['-updated_at']

    fieldsets = (
        ('基本信息', {
            'fields': ('fund_code', 'fund_name', 'fund_type', 'fund_company')
        }),
        ('日期信息', {
            'fields': ('established_date',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(FundNav)
class FundNavAdmin(admin.ModelAdmin):
    """基金净值记录管理"""
    list_display = ['fund', 'nav_date', 'unit_nav', 'accumulated_nav', 'daily_growth', 'estimated_nav', 'updated_at']
    list_filter = ['nav_date', 'updated_at']
    search_fields = ['fund__fund_code', 'fund__fund_name']
    list_per_page = 50
    ordering = ['-nav_date', '-updated_at']

    fieldsets = (
        ('基金信息', {
            'fields': ('fund',)
        }),
        ('净值数据', {
            'fields': ('nav_date', 'unit_nav', 'accumulated_nav', 'daily_growth')
        }),
        ('估算数据', {
            'fields': ('estimated_nav', 'estimated_growth')
        }),
    )

    readonly_fields = ['updated_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('fund')
