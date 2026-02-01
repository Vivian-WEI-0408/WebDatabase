# sbol_graphics.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patches import FancyArrowPatch, Arc

class SBOLGraphics:
    """优化版SBOL图形符号绘制类，启动子为直角箭头"""
    
    @staticmethod
    def promoter(ax, center, size=0.05, color='lightgreen', orientation='right'):
        """绘制启动子图标 - 直角箭头：垂直短直线 + 水平直线 + 箭头"""
        x, y = center
        
        # 尺寸参数
        vertical_length = size * 0.8  # 垂直短线长度
        horizontal_length = size * 1.2  # 水平线长度
        arrow_size = size * 0.3  # 箭头大小
        line_width = size * 2  # 线宽
        
        if orientation == 'right':
            # 向右的启动子
            # 1. 垂直短直线（向上）
            ax.plot([x, x], 
                   [y, y + vertical_length], 
                   color='black', 
                   linewidth=line_width,
                   solid_capstyle='round')
            
            # 2. 水平直线（向右）
            ax.plot([x, x + horizontal_length], 
                   [y + vertical_length, y + vertical_length], 
                   color='black', 
                   linewidth=line_width,
                   solid_capstyle='round')
            
            # 3. 箭头（向右）
            arrow_points = np.array([
                [x + horizontal_length, y + vertical_length],  # 箭头尖端
                [x + horizontal_length - arrow_size, y + vertical_length - arrow_size/2],  # 左下
                [x + horizontal_length - arrow_size, y + vertical_length + arrow_size/2],  # 左上
                [x + horizontal_length, y + vertical_length]   # 回到尖端
            ])
            
            arrow = patches.Polygon(
                arrow_points,
                closed=True,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(arrow)
            
        elif orientation == 'left':
            # 向左的启动子
            # 1. 垂直短直线（向上）
            ax.plot([x, x], 
                   [y, y + vertical_length], 
                   color='black', 
                   linewidth=line_width,
                   solid_capstyle='round')
            
            # 2. 水平直线（向左）
            ax.plot([x, x - horizontal_length], 
                   [y + vertical_length, y + vertical_length], 
                   color='black', 
                   linewidth=line_width,
                   solid_capstyle='round')
            
            # 3. 箭头（向左）
            arrow_points = np.array([
                [x - horizontal_length, y + vertical_length],  # 箭头尖端
                [x - horizontal_length + arrow_size, y + vertical_length - arrow_size/2],  # 右下
                [x - horizontal_length + arrow_size, y + vertical_length + arrow_size/2],  # 右上
                [x - horizontal_length, y + vertical_length]   # 回到尖端
            ])
            
            arrow = patches.Polygon(
                arrow_points,
                closed=True,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(arrow)
            
        elif orientation == 'up':
            # 向上的启动子
            # 1. 水平短直线（向左）
            ax.plot([x, x - vertical_length], 
                   [y, y], 
                   color='black', 
                   linewidth=line_width,
                   solid_capstyle='round')
            
            # 2. 垂直直线（向上）
            ax.plot([x - vertical_length, x - vertical_length], 
                   [y, y + horizontal_length], 
                   color='black', 
                   linewidth=line_width,
                   solid_capstyle='round')
            
            # 3. 箭头（向上）
            arrow_points = np.array([
                [x - vertical_length, y + horizontal_length],  # 箭头尖端
                [x - vertical_length - arrow_size/2, y + horizontal_length - arrow_size],  # 左下
                [x - vertical_length + arrow_size/2, y + horizontal_length - arrow_size],  # 右下
                [x - vertical_length, y + horizontal_length]   # 回到尖端
            ])
            
            arrow = patches.Polygon(
                arrow_points,
                closed=True,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(arrow)
            
        else:  # orientation == 'down'
            # 向下的启动子
            # 1. 水平短直线（向左）
            ax.plot([x, x - vertical_length], 
                   [y, y], 
                   color='black', 
                   linewidth=line_width,
                   solid_capstyle='round')
            
            # 2. 垂直直线（向下）
            ax.plot([x - vertical_length, x - vertical_length], 
                   [y, y - horizontal_length], 
                   color='black', 
                   linewidth=line_width,
                   solid_capstyle='round')
            
            # 3. 箭头（向下）
            arrow_points = np.array([
                [x - vertical_length, y - horizontal_length],  # 箭头尖端
                [x - vertical_length - arrow_size/2, y - horizontal_length + arrow_size],  # 左上
                [x - vertical_length + arrow_size/2, y - horizontal_length + arrow_size],  # 右上
                [x - vertical_length, y - horizontal_length]   # 回到尖端
            ])
            
            arrow = patches.Polygon(
                arrow_points,
                closed=True,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(arrow)
        
        return arrow
    
    @staticmethod
    def rbs(ax, center, size=0.05, color='orange', orientation='right'):
        """绘制RBS图标 - 半圆形"""
        x, y = center
        
        # 半圆形参数
        width = size
        height = size / 1.5
        
        if orientation in ['right', 'left']:
            # 水平方向
            if orientation == 'right':
                theta1, theta2 = -90, 90  # 朝右的半圆
            else:
                theta1, theta2 = 90, 270  # 朝左的半圆
            
            wedge = patches.Wedge(
                (x, y),
                width/2,
                theta1,
                theta2,
                width=height/2,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
        else:
            # 垂直方向
            if orientation == 'up':
                theta1, theta2 = 0, 180  # 朝上的半圆
            else:
                theta1, theta2 = 180, 360  # 朝下的半圆
            
            wedge = patches.Wedge(
                (x, y),
                height/2,
                theta1,
                theta2,
                width=width/2,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
        
        ax.add_patch(wedge)
        return wedge
    
    @staticmethod
    def cds(ax, center, size=0.05, color='lightblue', orientation='right'):
        """绘制CDS图标 - 直线箭头"""
        x, y = center
        
        # 箭头参数
        arrow_length = size * 1.5
        arrow_width = size * 0.6
        head_length = size * 0.4
        
        if orientation == 'right':
            # 向右的CDS箭头
            # 绘制主体矩形
            body = patches.Rectangle(
                (x - arrow_length/2, y - arrow_width/2),
                arrow_length - head_length,
                arrow_width,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(body)
            
            # 绘制箭头头部
            head_points = [
                (x + arrow_length/2 - head_length, y - arrow_width/2),
                (x + arrow_length/2, y),
                (x + arrow_length/2 - head_length, y + arrow_width/2)
            ]
            head = patches.Polygon(
                head_points,
                closed=True,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(head)
            
        elif orientation == 'left':
            # 向左的CDS箭头
            body = patches.Rectangle(
                (x - arrow_length/2 + head_length, y - arrow_width/2),
                arrow_length - head_length,
                arrow_width,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(body)
            
            head_points = [
                (x - arrow_length/2 + head_length, y - arrow_width/2),
                (x - arrow_length/2, y),
                (x - arrow_length/2 + head_length, y + arrow_width/2)
            ]
            head = patches.Polygon(
                head_points,
                closed=True,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(head)
            
        elif orientation == 'up':
            # 向上的CDS箭头
            body = patches.Rectangle(
                (x - arrow_width/2, y - arrow_length/2 + head_length),
                arrow_width,
                arrow_length - head_length,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(body)
            
            head_points = [
                (x - arrow_width/2, y + arrow_length/2 - head_length),
                (x, y + arrow_length/2),
                (x + arrow_width/2, y + arrow_length/2 - head_length)
            ]
            head = patches.Polygon(
                head_points,
                closed=True,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(head)
            
        else:  # down
            # 向下的CDS箭头
            body = patches.Rectangle(
                (x - arrow_width/2, y - arrow_length/2),
                arrow_width,
                arrow_length - head_length,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(body)
            
            head_points = [
                (x - arrow_width/2, y - arrow_length/2 + head_length),
                (x, y - arrow_length/2),
                (x + arrow_width/2, y - arrow_length/2 + head_length)
            ]
            head = patches.Polygon(
                head_points,
                closed=True,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(head)
        
        return head
    
    @staticmethod
    def reporter(ax, center, size=0.05, color='red', orientation='horizontal'):
        """绘制CDS图标 - 直线箭头"""
        x, y = center
        
        # 箭头参数
        arrow_length = size * 1.5
        arrow_width = size * 0.6
        head_length = size * 0.4
        
        body = patches.Rectangle(
            (x - arrow_length/2, y - arrow_width/2),
            arrow_length - head_length,
            arrow_width,
            facecolor=color,
            edgecolor='black',
            linewidth=1,
            alpha=0.8
        )
        ax.add_patch(body)
            
        # 绘制箭头头部
        head_points = [
            (x + arrow_length/2 - head_length, y - arrow_width/2),
            (x + arrow_length/2, y),
            (x + arrow_length/2 - head_length, y + arrow_width/2)
        ]
        head = patches.Polygon(
            head_points,
            closed=True,
            facecolor=color,
            edgecolor='black',
            linewidth=1,
            alpha=0.8
        )
        ax.add_patch(head)
        return head
    
    @staticmethod
    def ori(ax, center, size=0.05, color='lightblue'):
        """绘制选择标记图标 - 圆角矩形（用于URA3）"""
        x, y = center
        width, height = size*1.2, size*0.8
        
        # 圆角矩形
        print(size)
        print(width)
        print(height)
        rect = patches.FancyBboxPatch(
            (x - width/2, y - height/2),
            width, height,
            boxstyle="round,pad=0.005, rounding_size=0.005",
            facecolor=color,
            edgecolor='black',
            linewidth=1.5,
            alpha=0.8
        )
        ax.add_patch(rect)
        return rect
    
    @staticmethod
    def terminator(ax, center, size=0.05, color='gray', orientation='horizontal'):
        """绘制终止子图标 - T形"""
        x, y = center
        
        # T形参数
        t_width = size
        t_height = size
        
        if orientation == 'horizontal':
            # 横线
            ax.plot([x - t_width/2, x + t_width/2], 
                   [y, y], 
                   color='black', 
                   linewidth=3,
                   solid_capstyle='butt')
            
            # 竖线
            ax.plot([x, x], 
                   [y - t_height/4, y + t_height/4], 
                   color='black', 
                   linewidth=3,
                   solid_capstyle='butt')
            
            # 填充竖线（加粗效果）
            line_fill = patches.Rectangle(
                (x - t_width/20, y - t_height/4),
                t_width/10,
                t_height/2,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(line_fill)
            
            # 填充横线
            line_fill_h = patches.Rectangle(
                (x - t_width/2, y - t_width/20),
                t_width,
                t_width/10,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(line_fill_h)
            
        else:  # vertical
            # 横线（垂直方向时为竖线）
            ax.plot([x, x], 
                   [y - t_height/2, y + t_height/2], 
                   color='black', 
                   linewidth=3,
                   solid_capstyle='butt')
            
            # 竖线（垂直方向时为横线）
            ax.plot([x - t_width/4, x + t_width/4], 
                   [y, y], 
                   color='black', 
                   linewidth=3,
                   solid_capstyle='butt')
            
            # 填充
            line_fill = patches.Rectangle(
                (x - t_width/20, y - t_height/2),
                t_width/10,
                t_height,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(line_fill)
            
            line_fill_h = patches.Rectangle(
                (x - t_width/4, y - t_width/20),
                t_width/2,
                t_width/10,
                facecolor=color,
                edgecolor='black',
                linewidth=1,
                alpha=0.8
            )
            ax.add_patch(line_fill_h)
        
        return None

# plasmid_generator.py
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from io import BytesIO
from django.http import HttpResponse

class PlasmidGenerator:
    """质粒图谱生成器"""
    
    def __init__(self, width=10, height=10, dpi=150):
        self.width = width
        self.height = height
        self.dpi = dpi
        self.fig = None
        self.ax = None
        self.sbol = SBOLGraphics()
        
    def create_figure(self):
        """创建图形"""
        self.fig, self.ax = plt.subplots(figsize=(self.width, self.height))
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
    def draw_rounded_rectangle(self, center=(0.5, 0.5), width=0.8, height=0.4, 
                                radius=0.5, color='lightblue', alpha=0.1):
        """绘制圆矩形质粒"""
        x, y = center
        box_x, box_y = x - width/2, y - height/2
        
        # 使用FancyBboxPatch绘制圆角矩形
        rounded_rect = FancyBboxPatch(
            (box_x, box_y),
            width, height,
            boxstyle="Round,pad=0.02,rounding_size=0.05",
            facecolor=color,
            edgecolor='blue',
            linewidth=3,
            alpha=alpha
        )
        self.ax.add_patch(rounded_rect)
        return rounded_rect
    
    def calculate_positions_on_plasmid(self, num_elements, plasmid_center=(0.5, 0.5), 
                                        plasmid_width=0.8, plasmid_height=0.4):
        """计算元件在圆矩形上的位置"""
        x_center, y_center = plasmid_center
        positions = []
        
        # 计算圆矩形周长
        perimeter = 2 * (plasmid_width + plasmid_height) - 8 * (0.1) + 2 * np.pi * 0.1
        
        # 等距分布元件
        for i in range(num_elements):
            # 计算沿周长的位置参数
            t = i / num_elements
            segment_length = perimeter / num_elements
            
            # 确定在哪条边上
            if t < plasmid_width / perimeter:  # 上边
                x = x_center - plasmid_width/2 + (t * perimeter)
                y = y_center + plasmid_height/2
                orientation = 'right'
            elif t < (plasmid_width + plasmid_height) / perimeter:  # 右边
                x = x_center + plasmid_width/2
                y = y_center + plasmid_height/2 - ((t - plasmid_width/perimeter) * perimeter)
                orientation = 'down'
            elif t < (2*plasmid_width + plasmid_height) / perimeter:  # 下边
                x = x_center + plasmid_width/2 - ((t - (plasmid_width+plasmid_height)/perimeter) * perimeter)
                y = y_center - plasmid_height/2
                orientation = 'left'
            else:  # 左边
                x = x_center - plasmid_width/2
                y = y_center - plasmid_height/2 + ((t - (2*plasmid_width+plasmid_height)/perimeter) * perimeter)
                orientation = 'up'
            
            positions.append({
                'center': (x, y),
                'orientation': orientation,
                'index': i
            })
        
        return positions
    
    def draw_plasmid_elements(self, elements):
        """绘制质粒元件"""
        positions = self.calculate_positions_on_plasmid(len(elements))
        
        for elem, pos in zip(elements, positions):
            elem_type = elem.get('type', 'cds')
            center = pos['center']
            orientation = pos['orientation']
            
            # 根据元件类型绘制对应的SBOL图标
            if elem_type == 'promoter':
                self.sbol.promoter(self.ax, center, 
                                  size=elem.get('size', 0.04),
                                  color=elem.get('color', 'lightgreen'),
                                  orientation=orientation)
            elif elem_type == 'reporter':
                self.sbol.reporter(self.ax, center,
                                  size=elem.get('size', 0.05),
                                  color=elem.get('color', 'red'))
            elif elem_type == 'selectable_marker':
                self.sbol.selectable_marker(self.ax, center,
                                           size=elem.get('size', 0.05),
                                           color=elem.get('color', 'orange'))
            elif elem_type == 'origin':
                self.sbol.origin(self.ax, center,
                                size=elem.get('size', 0.05),
                                color=elem.get('color', 'yellow'))
            elif elem_type == 'terminator':
                self.sbol.terminator(self.ax, center,
                                    size=elem.get('size', 0.04),
                                    color=elem.get('color', 'gray'))
            else:  # 默认CDS
                self.sbol.cds(self.ax, center,
                             size=elem.get('size', 0.04),
                             color=elem.get('color', 'lightblue'),
                             orientation='horizontal' if orientation in ['left', 'right'] else 'vertical')
            
            # 添加标签
            self.ax.text(center[0], center[1], 
                        elem.get('label', elem['name']),
                        fontsize=10, ha='center', va='center',
                        fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", 
                                 facecolor="white", 
                                 alpha=0.8,
                                 edgecolor='none'))
    
    def draw_connection_lines(self, elements):
        """绘制元件连接线"""
        positions = self.calculate_positions_on_plasmid(len(elements))
        
        for i in range(len(positions)):
            # 连接相邻元件
            current = positions[i]['center']
            next_idx = (i + 1) % len(positions)
            next_pos = positions[next_idx]['center']
            
            # 计算控制点（贝塞尔曲线）
            mid_x = (current[0] + next_pos[0]) / 2
            mid_y = (current[1] + next_pos[1]) / 2
            
            # 绘制曲线连接
            from matplotlib.patches import PathPatch
            import matplotlib.path as mpath
            
            # 创建贝塞尔曲线路径
            verts = [
                current,  # 起点
                (mid_x, mid_y),  # 控制点
                next_pos  # 终点
            ]
            
            codes = [mpath.Path.MOVETO, 
                    mpath.Path.CURVE3, 
                    mpath.Path.CURVE3]
            
            path = mpath.Path(verts, codes)
            patch = PathPatch(path, 
                             facecolor='none', 
                             edgecolor='gray', 
                             linewidth=1.5,
                             linestyle='--',
                             alpha=0.6)
            self.ax.add_patch(patch)
    
    def add_plasmid_info(self, plasmid_name="pExample", size="5000 bp"):
        """添加质粒信息"""
        info_text = f"{plasmid_name}\n{size}"
        self.ax.text(0.5, 0.5, info_text,
                    ha='center', va='center',
                    fontsize=12, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.3",
                             facecolor="white",
                             alpha=0.9))
    
    def generate_plasmid(self, elements, plasmid_info=None):
        """生成完整的质粒图"""
        self.create_figure()
        
        # 绘制质粒骨架
        self.draw_rounded_rectangle()
        
        # 绘制元件
        self.draw_plasmid_elements(elements)
        
        # 绘制连接线
        # self.draw_connection_lines(elements)
        
        # 添加质粒信息
        if plasmid_info:
            self.add_plasmid_info(plasmid_info.get('name', 'Plasmid'),
                                 plasmid_info.get('size', 'Unknown'))
        
        # 添加图例
        self.add_legend(elements)
        
        plt.tight_layout()
        return self.fig
    
    def add_legend(self, elements):
        """添加SBOL图例"""
        from matplotlib.patches import Patch
        
        legend_elements = []
        legend_labels = []
        
        for elem in elements:
            elem_type = elem.get('type', 'cds')
            color = elem.get('color', 'lightblue')
            name = elem.get('name', 'Unknown')
            
            if elem_type == 'promoter':
                patch = patches.Polygon([[0,0],[0,1],[1,1]], 
                                       facecolor=color, edgecolor='red')
            elif elem_type == 'reporter':
                patch = patches.Polygon([[0,0.5],[0.5,0],[1,0.5],[0.5,1]], 
                                       facecolor=color, edgecolor='black')
            elif elem_type == 'selectable_marker':
                patch = patches.RegularPolygon((0.5,0.5), 6, 
                                              facecolor=color, edgecolor='black')
            elif elem_type == 'origin':
                patch = patches.Circle((0.5,0.5), 0.3, 
                                      facecolor=color, edgecolor='black')
            else:
                patch = patches.Rectangle((0,0), 1, 1, 
                                         facecolor=color, edgecolor='black')
            
            legend_elements.append(patch)
            legend_labels.append(f"{name} ({elem_type})")
        
        self.ax.legend(legend_elements, legend_labels,
                      loc='upper left',
                      bbox_to_anchor=(1.02, 1),
                      borderaxespad=0.,
                      frameon=False,
                      fontsize=9)
    
    def save_to_bytes(self):
        """将图形保存为字节流"""
        buffer = BytesIO()
        self.fig.savefig(buffer, format='png', dpi=self.dpi, 
                        bbox_inches='tight', transparent=False)
        buffer.seek(0)
        plt.close(self.fig)
        return buffer

import json
def generate_plasmid_view(request, repositoryName):
    """生成质粒图谱的视图"""
    
    # 定义元件（示例数据）
    elements = [
        {
            'name': 'P_Van',
            'type': 'promoter',
            'label': 'P_{Van}',
            'color': '#90EE90',
            'size': 0.04
        },
        {
            'name': 'RFP',
            'type': 'reporter',
            'label': 'RFP',
            'color': '#FF6B6B',
            'size': 0.05
        },
        {
            'name': 'URA3',
            'type': 'selectable_marker',
            'label': 'URA3',
            'color': '#87CEEB',
            'size': 0.05
        },
        {
            'name': 'P_Tet',
            'type': 'promoter',
            'label': 'P_{Tet}',
            'color': '#FFD700',
            'size': 0.04
        },
        {
            'name': 'YFP',
            'type': 'reporter',
            'label': 'YFP',
            'color': '#FFFF00',
            'size': 0.05
        }
    ]
    
    plasmid_info = {
        'name': 'pExample_Vector',
        'size': '5321 bp'
    }
    
    # 生成质粒图
    generator = PlasmidGenerator(width=12, height=10, dpi=150)
    generator.generate_plasmid(elements, plasmid_info)
    
    # 获取图像字节流
    buffer = generator.save_to_bytes()
    
    # 返回HTTP响应
    return HttpResponse(buffer.getvalue(), content_type='image/png')

