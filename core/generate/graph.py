import json

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import random

from core.model import VIRTUAL_NODE, Case


class HtmlGraph:
    app = dash.Dash(__name__, external_stylesheets=[
        "https://unpkg.com/element-ui/lib/theme-chalk/index.css"
    ])

    # 随机生成节点的坐标
    @staticmethod
    def generate_random_coordinates(nodes, x_range=(1.15, 2.85), y_range=(1.15, 2.85)):
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
            if (show_nodes and (start_node not in show_nodes or end_node not in show_nodes)
                    or start_node == VIRTUAL_NODE):
                continue  # 不展示无关边
            else:
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
                    # 下拉框部分
                    html.Div(
                        dcc.Dropdown(
                            id='node-dropdown',
                            options=[{'label': node, 'value': node} for node in self.nodes],
                            placeholder="筛选节点",
                            style={'width': '100%', 'margin': 'auto'}
                        ),
                        className="el-form-item",  # 使用 ElementUI 表单样式
                        style={'margin-bottom': '30px'}
                    ),
                    dcc.Graph(
                        id='graph',
                        figure=self.__create_figure(),
                        style={'width': '100%', 'height': '100%'}
                    )
                ], className="el-card",
                    style={'width': '50%', 'padding': '20px'}),
                html.Div([
                    # 节点信息展示部分
                    html.Div([
                        # html.H3("节点信息：", className="el-card__header", style={'text-align': 'center'}),
                        dcc.Markdown(id='node-info', className="el-card__body",
                                     style={'padding': '20px', 'font-size': '16px', 'white-space': 'pre-wrap',
                                            'word-wrap': 'break-word', 'overflow-wrap': 'break-word'})

                    ], className="el-card",
                        style={'width': '90%', 'height': '100%', 'overflowY': 'auto',
                               'margin': 'auto'})

                ], style={'width': '50%', 'padding': '20px', 'border-right': '1px solid #ccc'}),
            ], style={'display': 'flex', 'flex-direction': 'row', 'width': '100%', 'height': '90vh'})
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
                case: Case = self.cases.get(clicked_node)
                # 生成节点的详细信息
                node_info = f"#### 节点名称:{clicked_node}\n" \
                            f"#### 描述信息:{case.desc}\n" \
                            f"#### 祖先节点:{', '.join(ancestors - {clicked_node})}\n\n" \
                            f"#### 节点信息:\n" \
                            f"##### inter_type:{case.inter_type}\n" \
                            f"##### domain:     \t{case.domain}\n" \
                            f"##### url:        \t{case.url}\n" \
                            f"##### method:     \t{case.method}\n" \
                            f"##### headers:    \t{case.headers}\n" \
                            f"##### data:       \t{case.data.data_type}|{case.data.body}\n" \
                            f"##### plc:        \t{case.plc}\n" \
                            f"##### extracts:   \t{case.extracts}\n" \
                            f"##### asserts:    \t{case.asserts}\n"

                print(node_info)
                # 重新绘制图形并仅显示祖先节点和被点击节点
                return self.__create_figure(show_nodes=ancestors, highlight_nodes=ancestors), node_info

            elif click_data:  # 如果图表中的节点被点击
                clicked_node = click_data['points'][0]['text']
                # 找到所有与点击节点相关的节点
                ancestors = self.__find_ancestors(clicked_node)
                ancestors.add(clicked_node)  # 包括被点击的节点
                case: Case = self.cases.get(clicked_node)
                # 生成节点的详细信息
                node_info = f"#### 节点名称:{clicked_node}\n" \
                            f"#### 描述信息:{case.desc}\n" \
                            f"#### 祖先节点:{', '.join(ancestors - {clicked_node})}\n\n" \
                            f"#### 节点信息:\n" \
                            f"##### inter_type:{case.inter_type}\n" \
                            f"##### domain:     \t{case.domain}\n" \
                            f"##### url:        \t{case.url}\n" \
                            f"##### method:     \t{case.method}\n" \
                            f"##### headers:    \t{case.headers}\n" \
                            f"##### data:       \t{case.data.data_type}|{case.data.body}\n" \
                            f"##### plc:        \t{case.plc}\n" \
                            f"##### extracts:   \t{case.extracts}\n" \
                            f"##### asserts:    \t{case.asserts}\n"
                # 高亮显示相关节点，但不隐藏其他节点
                return self.__create_figure(highlight_nodes=ancestors), node_info

            # 默认返回初始图
            return self.__create_figure(), "点击图中的节点或从下拉框中选择节点以显示详细信息"

    def run_server(self, debug=True):
        self.__html_layout()
        self.__update_figure()
        return self.app.run(debug=debug)
