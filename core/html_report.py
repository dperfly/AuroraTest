import json
from datetime import datetime
from collections import defaultdict


class CompactHTMLTestReportGenerator:
    def __init__(self, report_data):
        self.report_data = report_data
        self.html = ""
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_report(self):
        self._generate_html_header()
        self._generate_summary_section()
        self._generate_charts_section()
        self._generate_test_cases_by_group()
        self._generate_footer()
        return self.html

    def save_report(self, file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_report())

    def _generate_html_header(self):
        self.html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>接口自动化测试报告</title>
    <!-- 引入 Element UI 样式 -->
    <link rel="stylesheet" href="https://unpkg.com/element-ui/lib/theme-chalk/index.css">
    <!-- 引入 Vue 和 Element UI JS -->
    <script src="https://cdn.jsdelivr.net/npm/vue@2.6.14/dist/vue.js"></script>
    <script src="https://unpkg.com/element-ui/lib/index.js"></script>
    <!-- 引入 Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- 引入 Chart.js datalabels 插件 -->
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
    <style>
        body {{
            font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB", Arial, sans-serif;
            line-height: 1.5;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f7fa;
            font-size: 14px;
        }}

        #app {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 15px;
        }}

        .report-header {{
            text-align: center;
            margin-bottom: 15px;
            padding: 15px;
            background: linear-gradient(135deg, #409EFF, #67C23A);
            color: white;
            border-radius: 4px;
            box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
        }}

        .report-header h1 {{
            margin: 0;
            font-size: 22px;
            font-weight: 500;
        }}

        .report-header p {{
            margin: 8px 0 0;
            opacity: 0.9;
            font-size: 13px;
        }}

        .summary-cards {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 15px;
        }}

        .summary-card {{
            flex: 1;
            min-width: 120px;
            background: white;
            border-radius: 4px;
            padding: 12px;
            box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
            text-align: center;
        }}

        .summary-card .value {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 3px;
        }}

        .summary-card .label {{
            color: #909399;
            font-size: 12px;
        }}

        .success {{
            color: #67C23A;
        }}

        .failure {{
            color: #F56C6C;
        }}

        .skipped {{
            color: #E6A23C;
        }}

        .charts-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
        }}

        .chart-container {{
            flex: 1;
            min-width: 350px;
            background: white;
            border-radius: 4px;
            padding: 15px;
            box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
        }}

        .chart-title {{
            text-align: center;
            font-weight: 500;
            margin-bottom: 15px;
            color: #303133;
            font-size: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #EBEEF5;
        }}

        .chart-wrapper {{
            position: relative;
            height: 280px;
            width: 100%;
        }}

        .test-groups {{
            margin-bottom: 15px;
        }}

        .test-group {{
            margin-bottom: 12px;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
        }}

        .test-group-header {{
            padding: 10px 15px;
            background: #f0f7ff;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 14px;
        }}

        .test-group-header:hover {{
            background: #e0f0ff;
        }}

        .test-group-title {{
            font-weight: 500;
            color: #303133;
        }}

        .test-group-summary {{
            font-size: 12px;
        }}

        .group-status-passed {{
            color: #67C23A;
        }}

        .group-status-failed {{
            color: #F56C6C;
        }}

        .group-status-mixed {{
            color: #E6A23C;
        }}

        .test-group-content {{
            display: none;
            background: white;
            padding: 8px 0;
        }}

        .test-group-content.active {{
            display: block;
        }}

        .test-case {{
            margin: 8px;
            border: 1px solid #EBEEF5;
            border-radius: 4px;
            overflow: hidden;
            transition: all 0.3s;
            font-size: 13px;
        }}

        .test-case:hover {{
            box-shadow: 0 2px 8px 0 rgba(0, 0, 0, 0.1);
        }}

        .test-case-header {{
            padding: 10px 12px;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }}

        .test-case-title {{
            font-weight: 500;
        }}

        .test-case-status {{
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: bold;
        }}

        .status-passed {{
            background-color: #f0f9eb;
            color: #67C23A;
        }}

        .status-failed {{
            background-color: #fef0f0;
            color: #F56C6C;
        }}

        .status-skipped {{
            background-color: #fdf6ec;
            color: #E6A23C;
        }}

        .test-case-content {{
            display: none;
            background: white;
        }}

        .test-case-content.active {{
            display: block;
        }}

        .section {{
            padding: 12px;
            border-bottom: 1px solid #EBEEF5;
        }}

        .section:last-child {{
            border-bottom: none;
        }}

        .section-title {{
            font-weight: 500;
            margin-bottom: 8px;
            color: #303133;
            font-size: 13px;
        }}

        .param-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }}

        .param-table th, .param-table td {{
            padding: 6px 8px;
            text-align: left;
            border: 1px solid #EBEEF5;
        }}

        .param-table th {{
            background-color: #f5f7fa;
            font-weight: 500;
            color: #909399;
        }}

        .log-entry {{
            margin-bottom: 5px;
            padding: 5px 8px;
            border-left: 3px solid #409EFF;
            background-color: #f5f7fa;
            font-size: 12px;
            border-radius: 2px;
        }}

        .log-time {{
            color: #909399;
            font-size: 11px;
            margin-right: 8px;
        }}

        .log-level-info {{
            border-left-color: #409EFF;
        }}

        .log-level-error {{
            border-left-color: #F56C6C;
            background-color: #fef0f0;
        }}

        .log-level-warning {{
            border-left-color: #E6A23C;
            background-color: #fdf6ec;
        }}

        .response-section {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 8px;
        }}

        .response-block {{
            flex: 1;
            min-width: 280px;
        }}

        pre {{
            background: #f5f7fa;
            padding: 8px;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 12px;
            margin: 0;
            line-height: 1.4;
            font-family: Consolas, Monaco, 'Andale Mono', monospace;
        }}

        .timestamp {{
            text-align: right;
            color: #909399;
            font-size: 12px;
            margin-top: 15px;
        }}

        .collapse-all {{
            text-align: right;
            margin-bottom: 12px;
        }}

        @media (max-width: 768px) {{
            .summary-cards {{
                flex-direction: column;
            }}

            .charts-container {{
                flex-direction: column;
            }}

            .response-section {{
                flex-direction: column;
            }}

            .chart-container {{
                min-width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div id="app">
        <div class="report-header">
            <h1>接口自动化测试报告</h1>
            <p>测试执行时间: {self.report_data.get('start_time', self.timestamp)}</p>
        </div>"""

    def _generate_summary_section(self):
        summary = self.report_data.get('summary', {})
        total = summary.get('total', 0)
        passed = summary.get('passed', 0)
        failed = summary.get('failed', 0)
        skipped = summary.get('skipped', 0)
        pass_rate = (passed / total * 100) if total > 0 else 0

        self.html += f"""
        <div class="summary-cards">
            <el-card class="summary-card">
                <div class="value">{total}</div>
                <div class="label">总用例数</div>
            </el-card>
            <el-card class="summary-card">
                <div class="value success">{passed}</div>
                <div class="label">通过</div>
            </el-card>
            <el-card class="summary-card">
                <div class="value failure">{failed}</div>
                <div class="label">失败</div>
            </el-card>
            <el-card class="summary-card">
                <div class="value skipped">{skipped}</div>
                <div class="label">跳过</div>
            </el-card>
            <el-card class="summary-card">
                <div class="value">{pass_rate:.1f}%</div>
                <div class="label">通过率</div>
            </el-card>
        </div>
        """

    def _generate_charts_section(self):
        summary = self.report_data.get('summary', {})
        passed = summary.get('passed', 0)
        failed = summary.get('failed', 0)
        skipped = summary.get('skipped', 0)

        # 准备分组数据
        test_cases = self.report_data.get('test_cases', [])
        groups = defaultdict(lambda: {'passed': 0, 'failed': 0, 'skipped': 0, 'total': 0})

        for case in test_cases:
            group_name = case.get('group', '未分组')
            groups[group_name]['total'] += 1
            status = case.get('status', 'passed')
            groups[group_name][status] += 1

        group_names = sorted(groups.keys())
        group_passed = [groups[name]['passed'] for name in group_names]
        group_failed = [groups[name]['failed'] for name in group_names]
        group_skipped = [groups[name]['skipped'] for name in group_names]

        self.html += f"""
        <div class="charts-container">
            <el-card class="chart-container">
                <div class="chart-title">测试结果分布</div>
                <div class="chart-wrapper">
                    <canvas id="pieChart"></canvas>
                </div>
            </el-card>
            <el-card class="chart-container">
                <div class="chart-title">各模块测试结果</div>
                <div class="chart-wrapper">
                    <canvas id="barChart"></canvas>
                </div>
            </el-card>
        </div>"""

    def _generate_test_cases_by_group(self):
        test_cases = self.report_data.get('test_cases', [])
        groups = defaultdict(list)

        for case in test_cases:
            group_name = case.get('group', '未分组')
            groups[group_name].append(case)

        sorted_groups = sorted(groups.items(), key=lambda x: x[0])

        self.html += """
        <div class="collapse-all">
            <el-button size="small" @click="toggleAllGroups">展开/收起所有分组</el-button>
        </div>
        <div class="test-groups">"""

        for group_name, cases in sorted_groups:
            group_total = len(cases)
            group_passed = sum(1 for case in cases if case.get('status') == 'passed')
            group_failed = sum(1 for case in cases if case.get('status') == 'failed')
            group_skipped = sum(1 for case in cases if case.get('status') == 'skipped')

            if group_failed > 0:
                group_status_class = "group-status-failed"
                group_status_text = f"失败 {group_failed}个"
            elif group_skipped > 0:
                group_status_class = "group-status-mixed"
                group_status_text = f"通过 {group_passed}个, 跳过 {group_skipped}个"
            else:
                group_status_class = "group-status-passed"
                group_status_text = f"全部通过 ({group_passed}个)"

            self.html += f"""
            <div class="test-group">
                <div class="test-group-header" @click="toggleGroupContent($event)">
                    <div class="test-group-title">
                        <i class="el-icon-folder-opened"></i> {group_name}
                    </div>
                    <div class="test-group-summary {group_status_class}">
                        共 {group_total} 个用例 - {group_status_text}
                    </div>
                </div>
                <div class="test-group-content{' active' if group_failed > 0 else ''}">"""

            for case in cases:
                self._generate_test_case(case)

            self.html += """
                </div>
            </div>"""

        self.html += """
        </div>"""

    def _generate_test_case(self, case):
        status_class = {
            'passed': 'status-passed',
            'failed': 'status-failed',
            'skipped': 'status-skipped'
        }.get(case.get('status', 'passed'), 'status-passed')

        status_text = {
            'passed': '通过',
            'failed': '失败',
            'skipped': '跳过'
        }.get(case.get('status', 'passed'), '通过')

        self.html += f"""
            <el-card class="test-case">
                <div class="test-case-header" @click="toggleContent($event)">
                    <div class="test-case-title">
                        <i class="el-icon-document"></i> {case.get('case_id', '')} - {case.get('name', '未命名测试用例')}
                    </div>
                    <div class="test-case-status {status_class}">{status_text}</div>
                </div>
                <div class="test-case-content{' active' if case.get('status') == 'failed' else ''}">"""

        self._generate_test_case_basic_info(case)
        self._generate_request_params(case)
        self._generate_request_headers(case)
        self._generate_test_logs(case)
        self._generate_test_results(case)

        self.html += """
                </div>
            </el-card>"""

    def _generate_test_case_basic_info(self, case):
        self.html += f"""
                    <div class="section">
                        <div class="section-title"><i class="el-icon-info"></i> 基本信息</div>
                        <table class="param-table">
                            <tr>
                                <th width="15%">接口名称</th>
                                <td>{case.get('api_name', '')}</td>
                            </tr>
                            <tr>
                                <th>接口地址</th>
                                <td>{case.get('url', '')}</td>
                            </tr>
                            <tr>
                                <th>请求方法</th>
                                <td>{case.get('method', '').upper()}</td>
                            </tr>
                        </table>
                    </div>"""

    def _generate_request_params(self, case):
        params = case.get('params', [])
        if not params:
            return

        self.html += """
                    <div class="section">
                        <div class="section-title"><i class="el-icon-document-copy"></i> 请求参数</div>
                        <table class="param-table">
                            <thead>
                                <tr>
                                    <th>参数名</th>
                                    <th>参数值</th>
                                    <th>类型</th>
                                    <th>必填</th>
                                </tr>
                            </thead>
                            <tbody>"""

        for param in params:
            self.html += f"""
                                <tr>
                                    <td>{param.get('name', '')}</td>
                                    <td>{self._format_value(param.get('value', ''))}</td>
                                    <td>{param.get('type', '')}</td>
                                    <td>{'是' if param.get('required', False) else '否'}</td>
                                </tr>"""

        self.html += """
                            </tbody>
                        </table>
                    </div>"""

    def _format_value(self, value):
        """格式化显示值，处理长字符串"""
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, str) and len(value) > 50:
            return value[:50] + "..."
        return str(value)

    def _generate_request_headers(self, case):
        headers = case.get('headers', [])
        if not headers:
            return

        self.html += """
                    <div class="section">
                        <div class="section-title"><i class="el-icon-tickets"></i> 请求头</div>
                        <table class="param-table">
                            <thead>
                                <tr>
                                    <th>Header名</th>
                                    <th>Header值</th>
                                </tr>
                            </thead>
                            <tbody>"""

        for header in headers:
            self.html += f"""
                                <tr>
                                    <td>{header.get('name', '')}</td>
                                    <td>{header.get('value', '')}</td>
                                </tr>"""

        self.html += """
                            </tbody>
                        </table>
                    </div>"""

    def _generate_test_logs(self, case):
        logs = case.get('logs', [])
        if not logs:
            return

        self.html += """
                    <div class="section">
                        <div class="section-title"><i class="el-icon-notebook-2"></i> 测试日志</div>"""

        for log in logs:
            level_class = {
                'info': 'log-level-info',
                'error': 'log-level-error',
                'warning': 'log-level-warning'
            }.get(log.get('level', 'info'), 'log-level-info')

            self.html += f"""
                        <div class="log-entry {level_class}">
                            <span class="log-time">{log.get('time', '')}</span>
                            [{log.get('level', '').upper()}] {log.get('message', '')}
                        </div>"""

        self.html += """
                    </div>"""

    def _generate_test_results(self, case):
        self.html += """
                    <div class="section">
                        <div class="section-title"><i class="el-icon-finished"></i> 测试结果</div>
                        <div class="response-section">
                            <div class="response-block">
                                <div class="section-title">请求内容</div>
                                <pre>{request_content}</pre>
                            </div>
                            <div class="response-block">
                                <div class="section-title">响应内容</div>
                                <pre>{response_content}</pre>
                            </div>
                        </div>""".format(
            request_content=json.dumps(case.get('request', {}), indent=2, ensure_ascii=False),
            response_content=json.dumps(case.get('response', {}), indent=2, ensure_ascii=False)
        )

        assertions = case.get('assertions', [])
        if assertions:
            self.html += """
                        <div style="margin-top: 12px;">
                            <div class="section-title"><i class="el-icon-check"></i> 断言结果</div>
                            <table class="param-table">
                                <thead>
                                    <tr>
                                        <th width="30%">断言项</th>
                                        <th width="10%">结果</th>
                                        <th>详细信息</th>
                                    </tr>
                                </thead>
                                <tbody>"""

            for assertion in assertions:
                status_class = 'success' if assertion.get('passed', False) else 'failure'
                status_text = '通过' if assertion.get('passed', False) else '失败'

                self.html += f"""
                                    <tr>
                                        <td>{assertion.get('name', '')}</td>
                                        <td class="{status_class}">{status_text}</td>
                                        <td>{assertion.get('message', '')}</td>
                                    </tr>"""

            self.html += """
                                </tbody>
                            </table>
                        </div>"""

        self.html += """
                    </div>"""

    def _generate_footer(self):
        # 准备分组数据用于图表
        test_cases = self.report_data.get('test_cases', [])
        groups = defaultdict(lambda: {'passed': 0, 'failed': 0, 'skipped': 0, 'total': 0})

        for case in test_cases:
            group_name = case.get('group', '未分组')
            groups[group_name]['total'] += 1
            status = case.get('status', 'passed')
            groups[group_name][status] += 1

        group_names = sorted(groups.keys())
        group_passed = [groups[name]['passed'] for name in group_names]
        group_failed = [groups[name]['failed'] for name in group_names]
        group_skipped = [groups[name]['skipped'] for name in group_names]

        self.html += f"""
        <div class="timestamp">
            报告生成时间: {self.timestamp}
        </div>
    </div>

    <script>
        new Vue({{
            el: '#app',
            methods: {{
                toggleContent(event) {{
                    const content = event.currentTarget.nextElementSibling;
                    content.classList.toggle('active');
                }},
                toggleGroupContent(event) {{
                    const content = event.currentTarget.nextElementSibling;
                    content.classList.toggle('active');
                }},
                toggleAllGroups() {{
                    const groups = document.querySelectorAll('.test-group-content');
                    const allCollapsed = Array.from(groups).every(g => g.classList.contains('active'));

                    groups.forEach(group => {{
                        if (allCollapsed) {{
                            group.classList.remove('active');
                        }} else {{
                            group.classList.add('active');
                        }}
                    }});
                }}
            }},
            mounted() {{
                // 默认展开有失败的测试组和失败的测试用例
                const failedGroups = document.querySelectorAll('.group-status-failed');
                failedGroups.forEach(el => {{
                    el.closest('.test-group-header').nextElementSibling.classList.add('active');
                }});

                // 展开所有失败的测试用例
                const failedCases = document.querySelectorAll('.status-failed');
                failedCases.forEach(el => {{
                    el.closest('.test-case-header').nextElementSibling.classList.add('active');
                }});

                // 图表数据
                const pieData = {{
                    labels: ['通过', '失败', '跳过'],
                    datasets: [{{
                        data: [{self.report_data.get('summary', {}).get('passed', 0)}, 
                               {self.report_data.get('summary', {}).get('failed', 0)}, 
                               {self.report_data.get('summary', {}).get('skipped', 0)}],
                        backgroundColor: [
                            '#67C23A',
                            '#F56C6C',
                            '#E6A23C'
                        ],
                        borderWidth: 1
                    }}]
                }};

                // 饼图配置
                const pieConfig = {{
                    type: 'pie',
                    data: pieData,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{
                                position: 'right',
                                labels: {{
                                    padding: 15,
                                    usePointStyle: true,
                                    pointStyle: 'circle',
                                    font: {{
                                        size: 12
                                    }}
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(context) {{
                                        const label = context.label || '';
                                        const value = context.raw || 0;
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = Math.round((value / total) * 100);
                                        return `${{label}}: ${{value}} (${{percentage}}%)`;
                                    }}
                                }},
                                bodyFont: {{
                                    size: 12
                                }}
                            }},
                            datalabels: {{
                                display: false
                            }}
                        }},
                        cutout: '60%',
                        borderRadius: 5,
                        spacing: 5
                    }}
                }};

                // 创建饼图
                new Chart(
                    document.getElementById('pieChart'),
                    pieConfig
                );

                // 柱状图数据
                const barData = {{
                    labels: {json.dumps(group_names, ensure_ascii=False)},
                    datasets: [
                        {{
                            label: '通过',
                            data: {json.dumps(group_passed)},
                            backgroundColor: '#67C23A',
                        }},
                        {{
                            label: '失败',
                            data: {json.dumps(group_failed)},
                            backgroundColor: '#F56C6C',
                        }},
                        {{
                            label: '跳过',
                            data: {json.dumps(group_skipped)},
                            backgroundColor: '#E6A23C',
                        }}
                    ]
                }};

                // 柱状图配置
                const barConfig = {{
                    type: 'bar',
                    data: barData,
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {{
                            x: {{
                                stacked: true,
                                grid: {{
                                    display: false
                                }},
                                ticks: {{
                                    font: {{
                                        size: 11
                                    }}
                                }}
                            }},
                            y: {{
                                stacked: true,
                                beginAtZero: true,
                                ticks: {{
                                    precision: 0,
                                    font: {{
                                        size: 11
                                    }}
                                }},
                                grid: {{
                                    color: '#EBEEF5'
                                }}
                            }}
                        }},
                        plugins: {{
                            legend: {{
                                position: 'right',
                                labels: {{
                                    padding: 15,
                                    usePointStyle: true,
                                    pointStyle: 'circle',
                                    font: {{
                                        size: 12
                                    }}
                                }}
                            }},
                            tooltip: {{
                                callbacks: {{
                                    afterBody: function(context) {{
                                        const dataset = context[0].dataset;
                                        const total = dataset.data.reduce((a, b) => a + b, 0);
                                        return `总计: ${{total}}`;
                                    }}
                                }},
                                bodyFont: {{
                                    size: 12
                                }}
                            }}
                        }},
                        barThickness: 30,
                        borderRadius: 3
                    }}
                }};

                // 创建柱状图
                new Chart(
                    document.getElementById('barChart'),
                    barConfig
                );
            }}
        }});
    </script>
</body>
</html>"""