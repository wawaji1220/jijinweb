"""
图表生成器
使用Plotly生成交互式基金净值走势图
"""
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json


class ChartGenerator:
    """基金净值图表生成器"""

    @staticmethod
    def generate_nav_chart(history_data):
        """
        生成基金净值走势图

        Args:
            history_data: 历史净值数据列表

        Returns:
            str: Plotly图表JSON
        """
        if not history_data:
            return None

        # 准备数据
        dates = []
        unit_navs = []
        accumulated_navs = []

        for item in history_data:
            dates.append(item.get('nav_date', ''))
            unit_navs.append(float(item.get('unit_nav', 0)))
            accumulated_navs.append(float(item.get('accumulated_nav', 0)))

        # 创建图表
        fig = go.Figure()

        # 添加单位净值曲线
        fig.add_trace(go.Scatter(
            x=dates,
            y=unit_navs,
            mode='lines+markers',
            name='单位净值',
            line=dict(color='#1890ff', width=2),
            marker=dict(size=4),
        ))

        # 添加累计净值曲线
        fig.add_trace(go.Scatter(
            x=dates,
            y=accumulated_navs,
            mode='lines+markers',
            name='累计净值',
            line=dict(color='#52c41a', width=2),
            marker=dict(size=4),
        ))

        # 设置布局
        fig.update_layout(
            title='基金净值走势',
            xaxis_title='日期',
            yaxis_title='净值',
            hovermode='x unified',
            template='plotly_white',
            height=400,
            margin=dict(l=50, r=30, t=50, b=50),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                tickangle=-45,
            )
        )

        # 转换为JSON
        chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)

        return chart_json

    @staticmethod
    def generate_growth_chart(history_data):
        """
        生成基金增长率走势图

        Args:
            history_data: 历史净值数据列表

        Returns:
            str: Plotly图表JSON
        """
        if not history_data:
            return None

        # 准备数据
        dates = []
        growths = []

        for item in history_data:
            dates.append(item.get('nav_date', ''))
            growth = item.get('daily_growth', '0')
            try:
                growths.append(float(growth))
            except:
                growths.append(0.0)

        # 创建图表
        fig = go.Figure()

        # 添加增长率曲线
        colors = ['#52c41a' if g >= 0 else '#f5222d' for g in growths]

        fig.add_trace(go.Bar(
            x=dates,
            y=growths,
            name='日增长率(%)',
            marker_color=colors,
        ))

        # 设置布局
        fig.update_layout(
            title='基金日增长率',
            xaxis_title='日期',
            yaxis_title='增长率(%)',
            template='plotly_white',
            height=400,
            margin=dict(l=50, r=30, t=50, b=50),
            xaxis=dict(
                tickangle=-45,
            )
        )

        # 转换为JSON
        chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)

        return chart_json
