import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import random

from core.generate.generate import TestCaseAutomaticGeneration
from core.generate.reader import ReaderCase
from core.utils.path import data_path


class HtmlGraph:
    app = dash.Dash(__name__, external_stylesheets=[
        "https://unpkg.com/element-ui/lib/theme-chalk/index.css"
    ])

    # 随机生成节点的坐标
    @staticmethod
    def generate_random_coordinates(nodes, x_range=(0.15, 3.85), y_range=(0.15, 3.85)):
        return {node: (random.uniform(*x_range), random.uniform(*y_range)) for node in nodes}

    def __init__(self, nodes, edges, cases):
        self.nodes = nodes
        self.edges = edges
        self.cases = cases
        self.node_positions = self.generate_random_coordinates(self.nodes)

    # 找到以 start_node 为终点的所有父节点和祖先节点
    def __find_ancestors(self, node):
        ancestors = set()
        to_explore = [node]  # 使用栈来遍历节点
        while to_explore:
            current_node = to_explore.pop()
            for start, end in self.edges:
                if end == current_node and start not in ancestors:
                    ancestors.add(start)
                    to_explore.append(start)
        return ancestors

    # 创建有向图的初始图形
    def __create_figure(self, show_nodes=None, highlight_nodes=None):
        # 如果节点的坐标尚未生成，则随机生成
        fig = go.Figure()
        # 添加节点到图中，默认所有节点颜色为 lightblue
        for node, (x, y) in self.node_positions.items():
            if show_nodes and node not in show_nodes:
                continue  # 不展示无关节点

            color = 'lightblue'
            if highlight_nodes and node in highlight_nodes:
                color = 'orange'  # 高亮颜色
            elif highlight_nodes and node not in highlight_nodes:
                color = 'lightgray'  # 变暗的颜色

            fig.add_trace(go.Scatter(
                x=[x], y=[y], text=[node], mode='markers+text',
                textposition='top center', marker=dict(size=20, color=color),
                name=node
            ))

        # 添加有向边 (使用 annotations 创建箭头)
        for start_node, end_node in self.edges:
            if show_nodes and (start_node not in show_nodes or end_node not in show_nodes):
                continue  # 不展示无关边

            x0, y0 = self.node_positions[start_node]
            x1, y1 = self.node_positions[end_node]

            # 添加边
            fig.add_shape(
                type="line",
                x0=x0, y0=y0, x1=x1, y1=y1,
                line=dict(color="black", width=1)
            )

            # 添加箭头
            fig.add_annotation(
                ax=x0, ay=y0, x=x1, y=y1,
                xref="x", yref="y", axref="x", ayref="y",
                showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=2
            )

        fig.update_layout(
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, visible=False),  # 隐藏X轴
            yaxis=dict(showgrid=False, zeroline=False, visible=False),  # 隐藏Y轴
            plot_bgcolor='white',
            xaxis_range=[0, 4],
            yaxis_range=[0, 4],
            # title="有向图"
        )

        return fig

    def __html_layout(self):
        self.app.layout = html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='graph',
                        figure=self.__create_figure(),
                        style={'width': '100%', 'height': '100%'}
                    )
                ], className="el-card", style={'width': '67%', 'height': '100%', 'padding': '20px'}),  # 右侧区域，占 67% 宽度
                html.Div([
                    # 下拉框部分
                    html.Div(
                        dcc.Dropdown(
                            id='node-dropdown',
                            options=[{'label': node, 'value': node} for node in self.nodes],
                            placeholder="选择一个节点",
                            style={'width': '90%', 'margin': 'auto'}
                        ),
                        className="el-form-item",  # 使用 ElementUI 表单样式
                        style={'margin-bottom': '20px'}
                    ),

                    # 节点信息展示部分
                    html.Div([
                        html.H3("节点信息：", className="el-card__header", style={'text-align': 'center'}),
                        html.Pre(id='node-info', className="el-card__body",
                                 style={'padding': '20px', 'font-size': '16px'})
                    ], className="el-card",
                        style={'width': '90%', 'height': '400px', 'overflowY': 'auto', 'border-top': '1px solid black',
                               'margin': 'auto'})

                ], style={'width': '33%', 'padding': '20px', 'border-right': '1px solid #ccc'}),  # 左侧区域，占 33% 宽度
            ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%', 'height': '100vh'})
            # 使用 Flexbox 实现左右结构
        ])

    def __update_figure(self):
        # 回调函数：监听点击事件和下拉框选择并更新图形和节点信息
        @self.app.callback(
            [Output('graph', 'figure'),
             Output('node-info', 'children')],
            [Input('graph', 'clickData'),
             Input('node-dropdown', 'value')]
        )
        def __update_figure(click_data, dropdown_value):
            if dropdown_value:  # 如果下拉框选择了节点
                clicked_node = dropdown_value
                # 找到所有能到达被点击节点的父节点和祖先节点
                ancestors = self.__find_ancestors(clicked_node)
                ancestors.add(clicked_node)  # 包括被点击的节点

                # 生成节点的详细信息
                node_info = f"节点名称: {clicked_node}\n" \
                            f"坐标: {self.node_positions[clicked_node]}\n" \
                            f"祖先节点: {', '.join(ancestors - {clicked_node})}\n" \
                            f"{str(self.cases.get(clicked_node))}"

                # 重新绘制图形并仅显示祖先节点和被点击节点
                return self.__create_figure(show_nodes=ancestors, highlight_nodes=ancestors), node_info

            elif click_data:  # 如果图表中的节点被点击
                clicked_node = click_data['points'][0]['text']
                # 找到所有与点击节点相关的节点
                ancestors = self.__find_ancestors(clicked_node)
                ancestors.add(clicked_node)  # 包括被点击的节点

                # 生成节点的详细信息
                node_info = f"节点名称: {clicked_node}\n" \
                            f"坐标: {self.node_positions[clicked_node]}\n" \
                            f"相关节点: {', '.join(ancestors)}\n" \
                            f"{str(self.cases.get(clicked_node))}"

                # 高亮显示相关节点，但不隐藏其他节点
                return self.__create_figure(highlight_nodes=ancestors), node_info

            # 默认返回初始图
            return self.__create_figure(), "点击图中的节点或从下拉框中选择节点以显示详细信息"

    def run_server(self, debug=True):
        self.__html_layout()
        self.__update_figure()
        return self.app.run_server(debug=debug)


if __name__ == '__main__':
    raw_data = ReaderCase(data_path()).get_all_cases()
    t = TestCaseAutomaticGeneration(raw_data)
    nodes = t.get_all_case_name()
    edges = t.get_all_edges()
    all_cases = t.get_all_cases()
    HtmlGraph(nodes, edges, all_cases).run_server()
