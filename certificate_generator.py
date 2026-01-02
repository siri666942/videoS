from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from pathlib import Path
from typing import Optional
import os


class CertificateGenerator:
    """
    毕业证生成模块，使用PIL生成具有仪式感的电子毕业证书图片
    """
    def __init__(self, output_dir: str = "certificates"):
        """
        初始化证书生成器
        
        Args:
            output_dir: 证书输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 证书尺寸（A4比例，300 DPI）
        self.width = 2480  # A4宽度 @ 300 DPI
        self.height = 3508  # A4高度 @ 300 DPI
        
        # 颜色定义
        self.colors = {
            'cream': (250, 245, 235),  # 米色背景
            'gold': (212, 175, 55),  # 金色
            'dark_gold': (184, 134, 11),  # 深金色
            'brown': (139, 69, 19),  # 棕色边框
            'dark_brown': (101, 67, 33),  # 深棕色
            'text_dark': (51, 51, 51),  # 深色文字
            'blue': (70, 130, 180),  # 蓝色（用于渐变球体）
            'purple': (138, 43, 226),  # 紫色（用于渐变球体）
            'orange': (255, 140, 0),  # 橙色（用于渐变球体）
        }
    
    def _draw_decorative_border(self, draw: ImageDraw.ImageDraw, width: int, height: int):
        """
        绘制装饰性边框
        
        Args:
            draw: PIL ImageDraw对象
            width: 图片宽度
            height: 图片高度
        """
        # 外层深色边框
        border_width = 20
        draw.rectangle(
            [(0, 0), (width, height)],
            fill=self.colors['dark_brown'],
            outline=None
        )
        
        # 内层金色边框
        inner_margin = 30
        draw.rectangle(
            [(inner_margin, inner_margin), (width - inner_margin, height - inner_margin)],
            fill=self.colors['cream'],
            outline=self.colors['gold'],
            width=8
        )
        
        # 装饰性角花（简化版）
        corner_size = 100
        for corner_x, corner_y in [(inner_margin, inner_margin),
                                   (width - inner_margin, inner_margin),
                                   (inner_margin, height - inner_margin),
                                   (width - inner_margin, height - inner_margin)]:
            # 绘制简单的装饰图案
            for i in range(3):
                size = corner_size - i * 20
                draw.ellipse(
                    [(corner_x - size//2, corner_y - size//2),
                     (corner_x + size//2, corner_y + size//2)],
                    outline=self.colors['gold'],
                    width=3
                )
    
    def _draw_heart_spheres(self, draw: ImageDraw.ImageDraw, center_x: int, center_y: int):
        """
        绘制由两个发光球体组成的爱心图案
        
        Args:
            draw: PIL ImageDraw对象
            center_x: 中心X坐标
            center_y: 中心Y坐标
        """
        # 球体半径
        radius = 120
        offset = 60  # 两个球体的偏移距离
        
        # 左球体（蓝色到紫色渐变）
        left_x = center_x - offset
        for i in range(radius, 0, -5):
            # 简化渐变效果 - 混合颜色
            if i > radius * 0.6:
                # 蓝色为主
                ratio = (i - radius * 0.6) / (radius * 0.4)
                r = int(self.colors['blue'][0] * ratio + self.colors['purple'][0] * (1 - ratio))
                g = int(self.colors['blue'][1] * ratio + self.colors['purple'][1] * (1 - ratio))
                b = int(self.colors['blue'][2] * ratio + self.colors['purple'][2] * (1 - ratio))
            else:
                # 紫色为主
                r, g, b = self.colors['purple'][:3]
            
            color = (r, g, b)
            
            # 使用椭圆模拟球体
            draw.ellipse(
                [(left_x - i, center_y - i), (left_x + i, center_y + i)],
                fill=color,
                outline=self.colors['blue'] if i == radius else None,
                width=2 if i == radius else 0
            )
        
        # 右球体（紫色到橙色渐变）
        right_x = center_x + offset
        for i in range(radius, 0, -5):
            # 简化渐变效果 - 混合颜色
            if i > radius * 0.6:
                # 紫色为主
                ratio = (i - radius * 0.6) / (radius * 0.4)
                r = int(self.colors['purple'][0] * ratio + self.colors['orange'][0] * (1 - ratio))
                g = int(self.colors['purple'][1] * ratio + self.colors['orange'][1] * (1 - ratio))
                b = int(self.colors['purple'][2] * ratio + self.colors['orange'][2] * (1 - ratio))
            else:
                # 橙色为主
                r, g, b = self.colors['orange'][:3]
            
            color = (r, g, b)
            
            # 使用椭圆模拟球体
            draw.ellipse(
                [(right_x - i, center_y - i), (right_x + i, center_y + i)],
                fill=color,
                outline=self.colors['purple'] if i == radius else None,
                width=2 if i == radius else 0
            )
    
    def _get_font(self, size: int, bold: bool = False) -> Optional[ImageFont.FreeTypeFont]:
        """
        获取字体（尝试使用系统字体，如果失败则使用默认字体）
        
        Args:
            size: 字体大小
            bold: 是否加粗
            
        Returns:
            PIL字体对象
        """
        try:
            # 尝试使用中文字体（Windows）
            if os.name == 'nt':
                font_path = "C:/Windows/Fonts/simhei.ttf"  # 黑体
                if not os.path.exists(font_path):
                    font_path = "C:/Windows/Fonts/msyh.ttc"  # 微软雅黑
            else:
                # Linux/Mac
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except:
            pass
        
        # 使用默认字体
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
    
    def generate_certificate(
        self,
        user_name: str,
        video_title: str,
        score: int,
        total: int,
        completion_date: Optional[str] = None,
        output_filename: Optional[str] = None
    ) -> str:
        """
        生成毕业证书
        
        Args:
            user_name: 用户姓名
            video_title: 视频标题
            score: 得分
            total: 总分
            completion_date: 完成日期（格式：YYYY.MM.DD），如果为None则使用当前日期
            output_filename: 输出文件名，如果为None则自动生成
            
        Returns:
            证书图片文件路径
        """
        # 创建图片
        img = Image.new('RGB', (self.width, self.height), color=self.colors['cream'])
        draw = ImageDraw.Draw(img)
        
        # 绘制边框
        self._draw_decorative_border(draw, self.width, self.height)
        
        # 内容区域边距
        margin = 150
        
        # 1. 绘制标题 "结业证书"
        title_font = self._get_font(120, bold=True)
        title_text = "结业证书"
        title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        title_y = margin + 100
        draw.text((title_x, title_y), title_text, fill=self.colors['text_dark'], font=title_font)
        
        # 2. 绘制英文标题 "CERTIFICATE"
        subtitle_font = self._get_font(40)
        subtitle_text = "CERTIFICATE"
        subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        subtitle_x = (self.width - subtitle_width) // 2
        subtitle_y = title_y + 150
        draw.text((subtitle_x, subtitle_y), subtitle_text, fill=self.colors['dark_gold'], font=subtitle_font)
        
        # 3. 绘制核心图形（爱心球体）
        graphic_y = subtitle_y + 200
        self._draw_heart_spheres(draw, self.width // 2, graphic_y)
        
        # 4. 绘制认证文本
        text_y = graphic_y + 250
        text_font = self._get_font(50)
        small_font = self._get_font(40)
        
        # 认证文本
        cert_text = f"兹证明 {user_name} 已顺利完成《{video_title}》课程的学习，"
        cert_text2 = f"在测试中获得 {score}/{total} 分，掌握了相关知识点，"
        cert_text3 = "具备独立理解和应用所学知识的能力。"
        
        # 计算文本位置（居中）
        for i, text in enumerate([cert_text, cert_text2, cert_text3]):
            bbox = draw.textbbox((0, 0), text, font=text_font)
            text_width = bbox[2] - bbox[0]
            text_x = (self.width - text_width) // 2
            draw.text((text_x, text_y + i * 80), text, fill=self.colors['text_dark'], font=text_font)
        
        # 5. 绘制日期和签名
        bottom_y = self.height - margin - 200
        
        # 日期
        if completion_date is None:
            completion_date = datetime.now().strftime("%Y.%m.%d")
        
        date_text = f"日期：{completion_date}"
        date_bbox = draw.textbbox((0, 0), date_text, font=small_font)
        date_x = margin + 100
        draw.text((date_x, bottom_y), date_text, fill=self.colors['text_dark'], font=small_font)
        draw.text((date_x, bottom_y + 50), "日期", fill=self.colors['dark_gold'], font=small_font)
        
        # 签名（右侧）
        signature_text = "VedioS学习平台"
        signature_bbox = draw.textbbox((0, 0), signature_text, font=small_font)
        signature_x = self.width - margin - 100 - (signature_bbox[2] - signature_bbox[0])
        draw.text((signature_x, bottom_y), signature_text, fill=self.colors['text_dark'], font=small_font)
        draw.text((signature_x, bottom_y + 50), "签名", fill=self.colors['dark_gold'], font=small_font)
        
        # 保存图片
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"certificate_{timestamp}.png"
        
        output_path = self.output_dir / output_filename
        img.save(output_path, 'PNG', quality=95)
        
        return str(output_path)

