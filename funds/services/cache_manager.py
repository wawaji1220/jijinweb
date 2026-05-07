"""
基金数据缓存管理器
使用Django缓存框架实现数据缓存
"""
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """缓存管理器"""

    # 缓存键前缀
    FUND_REALTIME_PREFIX = 'fund_realtime_'
    FUND_INFO_PREFIX = 'fund_info_'
    FUND_HISTORY_PREFIX = 'fund_history_'
    FUND_SEARCH_PREFIX = 'fund_search_'

    # 缓存时间(秒)
    REALTIME_CACHE_TIMEOUT = 1800  # 实时数据缓存30分钟
    INFO_CACHE_TIMEOUT = 3600  # 基金信息缓存1小时
    HISTORY_CACHE_TIMEOUT = 3600  # 历史数据缓存1小时
    SEARCH_CACHE_TIMEOUT = 300  # 搜索结果缓存5分钟

    @staticmethod
    def get_fund_realtime(fund_code):
        """获取基金实时数据缓存"""
        cache_key = f"{CacheManager.FUND_REALTIME_PREFIX}{fund_code}"
        return cache.get(cache_key)

    @staticmethod
    def set_fund_realtime(fund_code, data):
        """设置基金实时数据缓存"""
        cache_key = f"{CacheManager.FUND_REALTIME_PREFIX}{fund_code}"
        try:
            cache.set(cache_key, data, CacheManager.REALTIME_CACHE_TIMEOUT)
            return True
        except Exception as e:
            logger.error(f"设置实时数据缓存失败: {str(e)}")
            return False

    @staticmethod
    def get_fund_info(fund_code):
        """获取基金信息缓存"""
        cache_key = f"{CacheManager.FUND_INFO_PREFIX}{fund_code}"
        return cache.get(cache_key)

    @staticmethod
    def set_fund_info(fund_code, data):
        """设置基金信息缓存"""
        cache_key = f"{CacheManager.FUND_INFO_PREFIX}{fund_code}"
        try:
            cache.set(cache_key, data, CacheManager.INFO_CACHE_TIMEOUT)
            return True
        except Exception as e:
            logger.error(f"设置基金信息缓存失败: {str(e)}")
            return False

    @staticmethod
    def get_fund_history(fund_code):
        """获取基金历史数据缓存"""
        cache_key = f"{CacheManager.FUND_HISTORY_PREFIX}{fund_code}"
        return cache.get(cache_key)

    @staticmethod
    def set_fund_history(fund_code, data):
        """设置基金历史数据缓存"""
        cache_key = f"{CacheManager.FUND_HISTORY_PREFIX}{fund_code}"
        try:
            cache.set(cache_key, data, CacheManager.HISTORY_CACHE_TIMEOUT)
            return True
        except Exception as e:
            logger.error(f"设置历史数据缓存失败: {str(e)}")
            return False

    @staticmethod
    def get_search_result(keyword):
        """获取搜索结果缓存"""
        cache_key = f"{CacheManager.FUND_SEARCH_PREFIX}{keyword}"
        return cache.get(cache_key)

    @staticmethod
    def set_search_result(keyword, data):
        """设置搜索结果缓存"""
        cache_key = f"{CacheManager.FUND_SEARCH_PREFIX}{keyword}"
        try:
            cache.set(cache_key, data, CacheManager.SEARCH_CACHE_TIMEOUT)
            return True
        except Exception as e:
            logger.error(f"设置搜索结果缓存失败: {str(e)}")
            return False

    @staticmethod
    def clear_fund_cache(fund_code):
        """清除指定基金的所有缓存"""
        keys_to_clear = [
            f"{CacheManager.FUND_REALTIME_PREFIX}{fund_code}",
            f"{CacheManager.FUND_INFO_PREFIX}{fund_code}",
            f"{CacheManager.FUND_HISTORY_PREFIX}{fund_code}",
        ]

        for key in keys_to_clear:
            try:
                cache.delete(key)
            except Exception as e:
                logger.error(f"删除缓存失败 {key}: {str(e)}")

    @staticmethod
    def clear_all_fund_cache():
        """清除所有基金缓存(谨慎使用)"""
        try:
            cache.clear()
            return True
        except Exception as e:
            logger.error(f"清除所有缓存失败: {str(e)}")
            return False


# 创建全局实例
cache_manager = CacheManager()
