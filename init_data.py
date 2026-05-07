"""
初始化基金数据脚本
使用方法: python init_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jijinweb.settings')
django.setup()

from funds.models import Fund


def init_popular_funds():
    """初始化热门基金数据"""
    # 热门基金列表
    funds_data = [
        ('011370', '华商均衡成长混合C', '混合型', '华商基金'),
        ('025833', '天弘中证电网设备主题指数发起C', '指数型', '天弘基金'),
        ('012863', '汇添富中证电池主题ETF发起式联接C', '指数型', '汇添富基金'),
        ('000961', '天弘沪深300ETF联接A', '指数型', '天弘基金'),
        ('161725', '招商中证白酒指数', '指数型', '招商基金'),
        ('011103', '天弘中证光伏C', '指数型', '天弘基金'),
        ('001595', '天弘中证银行ETF联接C', '指数型', '天弘基金'),
        ('110020', '易方达沪深300ETF联接A', '指数型', '易方达基金'),
        ('161025', '富国中证智能汽车主题', '指数型', '富国基金'),
        ('005918', '天弘沪深300ETF联接C', '指数型', '天弘基金'),
        ('290008', '泰信发展主题混合', '混合型', '泰信基金'),
        ('022167', '富国资源精选混合发起式C', '混合型', '富国基金'),
        ('002891', '华夏移动互联混合(QDII)(人民币)', 'QDII-混合型', '中邮基金'),
        ('001938', '中融中证煤炭指数', '指数型', '中融基金'),
        ('013403', '华夏恒生科技ETF发起式联接(QDII)C', '指数型', '华夏基金'),
        ('019261', '富国恒生港股通高股息低波动ETF发起式联接C', '混合型', '富国基金'),  
    ]

    print('开始初始化基金数据...\n')

    created_count = 0
    updated_count = 0

    for code, name, ftype, company in funds_data:
        fund, created = Fund.objects.get_or_create(
            fund_code=code,
            defaults={
                'fund_name': name,
                'fund_type': ftype,
                'fund_company': company
            }
        )

        if created:
            print(f'[新增] {code} - {name}')
            created_count += 1
        else:
            # 更新基金信息
            if fund.fund_name != name or fund.fund_type != ftype:
                fund.fund_name = name
                fund.fund_type = ftype
                fund.fund_company = company
                fund.save()
                print(f'[更新] {code} - {name}')
                updated_count += 1

    print(f'\n初始化完成!')
    print(f'新增基金: {created_count} 只')
    print(f'更新基金: {updated_count} 只')
    print(f'总基金数: {Fund.objects.count()} 只\n')


def clear_all_funds():
    """清空所有基金数据"""
    import sys

    confirm = input('确认要删除所有基金数据吗? (yes/no): ')
    if confirm.lower() == 'yes':
        count = Fund.objects.count()
        Fund.objects.all().delete()
        print(f'已删除 {count} 只基金数据\n')
    else:
        print('取消操作\n')


def main():
    """主函数"""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'clear':
            clear_all_funds()
        elif command == 'init':
            init_popular_funds()
        else:
            print('未知命令')
            print('可用命令: init, clear')
    else:
        init_popular_funds()


if __name__ == '__main__':
    main()
