"""
基金数据获取服务 - 使用真实API
基于东方财富网的真实数据
"""
import requests
import re
import logging

logger = logging.getLogger(__name__)


class FundDataFetcherReal:
    """基金数据获取器 - 使用真实API"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'UTF-8',
        }

    def fetch_fund_realtime_data(self, fund_code):
        """
        获取基金实时数据
        优先从东方财富获取准确的净值数据，从新浪获取实时估值

        Args:
            fund_code: 基金代码

        Returns:
            dict: 包含实时数据的字典,失败返回None
            字段说明:
            - fund_code: 基金代码
            - name: 基金名称
            - unit_nav: 今日单位净值(来自东方财富,准确)
            - accumulated_nav: 今日累计净值(来自东方财富,准确)
            - nav_date: 数据日期(来自东方财富)
            - estimated_nav: 最新估值(来自新浪API,实时估算)
            - estimated_growth: 估值涨跌%(来自新浪API)
            - prev_nav: 前一日净值(来自东方财富历史数据)
            - prev_nav_date: 前一日净值日期
        """
        try:
            # 从HTML页面获取基金名称
            fund_name = self._get_fund_name_from_html(fund_code)

            # 获取历史数据以获取准确的今日和前一日净值
            history_data = self.fetch_fund_history_nav(fund_code, page=1, per_page=2)

            # 从新浪基金获取最新估值和涨跌
            sina_data = self._fetch_sina_realtime(fund_code)

            # 构建返回数据
            data = {
                'fund_code': fund_code,
                'name': fund_name or sina_data.get('name', f'基金{fund_code}'),
            }

            # 从历史数据中获取今日和前一日净值（这些是官方公布的准确数据）
            if history_data and len(history_data) > 0:
                latest = history_data[0]
                data['unit_nav'] = latest['unit_nav']  # 今日单位净值（准确）
                data['accumulated_nav'] = latest['accumulated_nav']  # 今日累计净值（准确）
                data['nav_date'] = latest['nav_date']
                data['daily_growth'] = latest['daily_growth']  # 今日实际涨跌幅（准确）

                # 从历史数据中获取前一日净值
                if len(history_data) > 1:
                    data['prev_nav'] = history_data[1]['unit_nav']
                    data['prev_nav_date'] = history_data[1]['nav_date']
                else:
                    # 如果只有一天的数据，计算前一日日期
                    try:
                        from datetime import datetime, timedelta
                        nav_date = datetime.strptime(data['nav_date'], '%Y-%m-%d')
                        prev_date = nav_date - timedelta(days=1)
                        data['prev_nav_date'] = prev_date.strftime('%Y-%m-%d')
                    except:
                        data['prev_nav_date'] = None
            else:
                # 如果历史数据获取失败，尝试用新浪数据
                logger.warning(f"基金 {fund_code} 历史数据获取失败，尝试使用新浪数据")
                if sina_data:
                    data['unit_nav'] = sina_data.get('unit_nav')
                    data['accumulated_nav'] = sina_data.get('accumulated_nav')
                    data['nav_date'] = sina_data.get('nav_date')
                    data['prev_nav'] = sina_data.get('prev_nav')

            # 处理新浪数据（用于获取实时估值和涨跌）
            if sina_data:
                data['estimated_nav'] = sina_data.get('estimated_nav')
                data['estimated_growth'] = sina_data.get('estimated_growth')
            else:
                # 没有实时估值数据
                data['estimated_nav'] = None
                data['estimated_growth'] = None

            # 检查是否有有效数据
            if data.get('unit_nav'):
                logger.info(f"成功获取基金 {fund_code} 数据: 估值={data.get('estimated_nav')}, 估值涨跌={data.get('estimated_growth')}%, 净值={data['unit_nav']}, 前一日={data.get('prev_nav')}")
                return data
            else:
                logger.warning(f"基金 {fund_code} 未找到有效数据")
                return None

        except Exception as e:
            logger.error(f"获取基金 {fund_code} 实时数据异常: {str(e)}")
            return None

    def fetch_fund_history_nav(self, fund_code, page=1, per_page=50):
        """
        获取基金历史净值数据

        Args:
            fund_code: 基金代码
            page: 页码
            per_page: 每页数量

        Returns:
            list: 历史净值数据列表
        """
        try:
            url = "http://fundf10.eastmoney.com/F10DataApi.aspx"
            params = {
                'type': 'lsjz',
                'code': fund_code,
                'page': page,
                'per': per_page,
            }

            headers = self.headers.copy()
            headers['Referer'] = 'http://fundf10.eastmoney.com/'

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code != 200:
                logger.error(f"获取基金 {fund_code} 历史数据失败: HTTP {response.status_code}")
                return []

            content = response.text

            # 检查是否有数据
            if '暂无数据' in content:
                logger.info(f"基金 {fund_code} 暂无历史数据")
                return []

            # 解析HTML表格
            pattern = r'<tr><td>(\d{4}-\d{2}-\d{2})</td><td[^>]*>([\d.]+)</td><td[^>]*>([\d.]+)</td><td[^>]*>\s*([+-]?\d+\.\d+)%</td>'
            matches = re.findall(pattern, content)

            if not matches:
                logger.warning(f"基金 {fund_code} 历史数据解析失败")
                return []

            nav_list = []
            for match in matches:
                nav_info = {
                    'nav_date': match[0],
                    'unit_nav': match[1],
                    'accumulated_nav': match[2],
                    'daily_growth': match[3],
                }
                nav_list.append(nav_info)

            logger.info(f"获取基金 {fund_code} 历史数据成功: {len(nav_list)} 条")
            return nav_list

        except Exception as e:
            logger.error(f"获取基金 {fund_code} 历史数据异常: {str(e)}")
            return []

    def _fetch_sina_realtime(self, fund_code):
        """
        从新浪基金获取实时估值和净值数据
        使用新浪的hq接口获取实时数据

        Returns:
            dict: 包含估值和净值数据的字典,失败返回None
        """
        try:
            # 使用新浪的hq接口获取实时数据
            url = f'https://hq.sinajs.cn/list=fu_{fund_code}'
            headers = self.headers.copy()
            headers['Referer'] = 'https://finance.sina.com.cn/'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                logger.error(f"新浪基金 {fund_code} 请求失败: HTTP {response.status_code}")
                return None

            # 新浪API返回GBK编码
            response.encoding = 'gbk'
            content = response.text

            # 解析格式: var hq_str_fu_110022="易方达消费行业股票,16:04:00,3.3587,3.3720,3.3720,0,-0.3944,2026-02-13,3.3600,-0.3559";
            # 字段含义:
            # 0: 基金名称
            # 1: 时间
            # 2: 最新估值 (实时估值)
            # 3: 前一日净值
            # 4: 累计净值
            # 5: 成交量
            # 6: 估值涨跌%
            # 7: 日期
            # 8: 今日开盘净值
            # 9: 开盘涨跌%

            pattern = rf'var hq_str_fu_{fund_code}="([^"]+)"'
            match = re.search(pattern, content)

            if not match:
                logger.warning(f"新浪基金 {fund_code} 数据格式解析失败")
                return None

            data_str = match.group(1)
            fields = data_str.split(',')

            if len(fields) < 8:
                logger.warning(f"新浪基金 {fund_code} 数据字段不足: {len(fields)}")
                return None

            # 构建返回数据
            data = {
                'name': fields[0],  # 基金名称
                'time': fields[1],  # 时间
            }

            # 最新估值 (字段2)
            try:
                estimated_nav = float(fields[2])
                data['estimated_nav'] = estimated_nav
            except (ValueError, IndexError):
                data['estimated_nav'] = None

            # 前一日净值 (字段3)
            try:
                prev_nav = float(fields[3])
                data['prev_nav'] = prev_nav
            except (ValueError, IndexError):
                data['prev_nav'] = None

            # 累计净值 (字段4)
            try:
                accumulated_nav = float(fields[4])
                data['accumulated_nav'] = accumulated_nav
            except (ValueError, IndexError):
                data['accumulated_nav'] = None

            # 估值涨跌% (字段6)
            try:
                estimated_growth = float(fields[6])
                data['estimated_growth'] = estimated_growth
            except (ValueError, IndexError):
                data['estimated_growth'] = None

            # 数据日期 (字段7)
            if len(fields) > 7:
                data['nav_date'] = fields[7]
                # 标准化日期格式
                nav_date = fields[7]
                nav_date = nav_date.replace('/', '-')
                parts = nav_date.split('-')
                if len(parts) == 3:
                    if len(parts[1]) == 1:
                        parts[1] = '0' + parts[1]
                    if len(parts[2]) == 1:
                        parts[2] = '0' + parts[2]
                    data['nav_date'] = '-'.join(parts)

            # 今日开盘净值 (字段8)
            try:
                unit_nav = float(fields[8])
                data['unit_nav'] = unit_nav
            except (ValueError, IndexError):
                data['unit_nav'] = None

            # 至少要有估值数据
            if data['estimated_nav'] is None and data['unit_nav'] is None:
                logger.warning(f"新浪基金 {fund_code} 未找到有效数据")
                return None

            logger.info(f"新浪基金 {fund_code} 数据获取成功: 估值={data.get('estimated_nav', 'N/A')}, 估值涨跌={data.get('estimated_growth', 'N/A')}%, 净值={data.get('unit_nav', 'N/A')}, 前一日={data.get('prev_nav', 'N/A')}")
            return data

        except Exception as e:
            logger.error(f"获取新浪基金 {fund_code} 数据异常: {str(e)}")
            return None

    def _get_fund_name_from_html(self, fund_code):
        """从HTML页面获取基金名称"""
        result = self._get_fund_info_from_html(fund_code)
        return result.get('fund_name') if result else None

    def _get_fund_info_from_html(self, fund_code):
        """从HTML页面获取基金名称和类型"""
        try:
            url = f'https://fund.eastmoney.com/{fund_code}.html'
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                # 确保使用UTF-8编码
                response.encoding = 'utf-8'
                content = response.text

                # 检查是否是错误页面
                if '页面未找到' in content or '您访问的页面不存在' in content:
                    return None

                fund_name = None
                fund_type = None

                # 从title提取基金名称
                title_match = re.search(r'<title>([^()]+)\(' + re.escape(fund_code) + r'\)', content)
                if title_match:
                    fund_name = title_match.group(1).strip()
                    if isinstance(fund_name, bytes):
                        fund_name = fund_name.decode('utf-8', errors='ignore')

                # 从页面内容提取基金类型
                # 东方财富页面中基金类型通常在 class="theme-nav" 或 data 属性中
                # 常见格式: "股票型", "混合型", "债券型", "指数型", "QDII", "货币型"
                type_patterns = [
                    r'class="fundType"\s*>([^<]+)<',
                    r'"fundType"\s*:\s*"([^"]+)"',
                    r'基金类型：</span>\s*<[^>]+>([^<]+)<',
                    r'<dd[^>]*>\s*基金类型\s*</dt>\s*<dd[^>]*>([^<]+)<',
                ]
                for pattern in type_patterns:
                    type_match = re.search(pattern, content)
                    if type_match:
                        fund_type = type_match.group(1).strip()
                        # 清理HTML标签
                        fund_type = re.sub(r'<[^>]+>', '', fund_type).strip()
                        break

                # 如果上面没找到，尝试从基金名称推断类型
                if not fund_type and fund_name:
                    type_indicators = {
                        '指数': '指数型',
                        'ETF': '指数型',
                        'QDII': 'QDII',
                        '货币': '货币型',
                        '债券': '债券型',
                        '混合': '混合型',
                    }
                    for indicator, ftype in type_indicators.items():
                        if indicator in fund_name:
                            fund_type = ftype
                            break

                return {
                    'fund_name': fund_name,
                    'fund_type': fund_type
                }

            return None

        except Exception as e:
            logger.error(f"获取基金 {fund_code} 信息异常: {str(e)}")
            return None

    def search_funds(self, keyword):
        """搜索基金 - 基于数据库搜索"""
        try:
            from funds.models import Fund

            # 从数据库搜索
            db_results = list(Fund.objects.filter(
                fund_code__icontains=keyword
            ).values('fund_code', 'fund_name', 'fund_type')[:20])

            if db_results:
                logger.info(f"从数据库找到 {len(db_results)} 个基金")
                return db_results

            return []

        except Exception as e:
            logger.error(f"搜索基金异常: {str(e)}")
            return []

    def validate_fund_code(self, fund_code):
        """验证基金代码是否有效"""
        try:
            # 尝试获取历史数据
            history = self.fetch_fund_history_nav(fund_code, page=1, per_page=1)
            return history is not None and len(history) > 0

        except Exception as e:
            logger.error(f"验证基金代码 {fund_code} 异常: {str(e)}")
            return False


# 创建全局实例
fund_fetcher_real = FundDataFetcherReal()
