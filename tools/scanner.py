import io
import json
from typing import Any, Generator, List
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

class ScatterPlotTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        # 获取输入数据
        x_data_str = tool_parameters.get("data", "")
        if not x_data_str:
            yield self.create_text_message("请输入 data（逗号或分号分隔的数字或 JSON 数组）。")
            return

        y_data_str = tool_parameters.get("x_axis", "")
        if not y_data_str:
            yield self.create_text_message("请输入 x_axis（逗号或分号分隔的数字或 JSON 数组）。")
            return

        # 解析数据的辅助函数
        def parse_data_string(data_string: str) -> List[float] | None:
            try:
                if data_string.startswith("[") and data_string.endswith("]"):
                    data_list = json.loads(data_string)
                    return [float(item) for item in data_list]
                if ';' in data_string:
                    items = data_string.split(";")
                elif ',' in data_string:
                    items = data_string.split(",")
                else:
                    items = [data_string]
                return [float(i.strip()) for i in items]
            except (ValueError, json.JSONDecodeError):
                return None

        # 解析 x 和 y 数据
        x_data_values = parse_data_string(x_data_str)
        if x_data_values is None:
            yield self.create_text_message("data 格式错误，数据应为逗号或分号分隔的数字或 JSON 数组。")
            return

        y_data_values = parse_data_string(y_data_str)
        if y_data_values is None:
            yield self.create_text_message("x_axis 格式错误，数据应为逗号或分号分隔的数字或 JSON 数组。")
            return

        # 检查数据点数量是否一致
        if len(x_data_values) != len(y_data_values):
            yield self.create_text_message("data 和 x_axis 的数据点数量必须一致。")
            return

        # 检查数据是否为空
        if not x_data_values:
            yield self.create_text_message("解析后 data 不能为空。")
            return

        # 获取标题和轴标签
        title = tool_parameters.get("title", "散点图")
        x_label = tool_parameters.get("x_label", "X轴")
        y_label = tool_parameters.get("y_label", "Y轴")

        # 生成 ECharts 配置
        scatter_data = [[x, y] for x, y in zip(x_data_values, y_data_values)]
        echarts_config = {
            "title": {
                "left": "center",
                "text": title
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {
                    "type": "cross"
                }
            },
            "xAxis": {
                "type": "value",
                "name": x_label
            },
            "yAxis": {
                "type": "value",
                "name": y_label
            },
            "series": [
                {
                    "type": "scatter",
                    "data": scatter_data
                }
            ]
        }

        # 格式化为带 ```echarts 代码块的字符串
        formatted_output = f"```echarts\n{json.dumps(echarts_config, indent=2, ensure_ascii=False)}\n```"
        yield self.create_text_message(formatted_output)