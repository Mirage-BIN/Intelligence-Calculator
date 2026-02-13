import sys
import time
import json
import os
import webbrowser
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from win10toast import ToastNotifier


class ThemeManager:
    """主题管理器"""
    
    def __init__(self):
        self.current_theme = "light"
        self.themes = {
            "light": {
                "window_bg": "#F5F5F5",
                "card_bg": "#FFFFFF",
                "text_color": "#333333",
                "button_bg": "#0078D7",
                "button_hover": "#005A9E",
                "border_color": "#E0E0E0",
                "title_color": "#0078D7",  # 标题蓝色
                "icon_color": "#333333"  # 图标颜色
            },
            "dark": {
                "window_bg": "#1E1E1E",
                "card_bg": "#2D2D30",
                "text_color": "#FFFFFF",
                "button_bg": "#0E639C",
                "button_hover": "#1177BB",
                "border_color": "#3E3E42",
                "title_color": "#0E639C",  # 暗蓝色
                "icon_color": "#FFFFFF"  # 白色图标
            },
            "morandi": {
                "window_bg": "#F5F0EB",
                "card_bg": "#FFFFFF",
                "text_color": "#5C534E",
                "button_bg": "#D8C4B6",
                "button_hover": "#C9B2A3",
                "border_color": "#E5DCD5",
                "title_color": "#8B7D6B",  # 莫兰迪色系
                "icon_color": "#5C534E"  # 莫兰迪色
            },
            "golden": {
                "window_bg": "#0A0A0A",
                "card_bg": "#1A1A1A",
                "text_color": "#FFD700",
                "button_bg": "#D4AF37",
                "button_hover": "#C19C30",
                "border_color": "#333333",
                "title_color": "#FFD700",  # 金色
                "icon_color": "#FFD700",  # 金色图标
                "gold_light": "#FFE066",  # 金色亮色（修正无效颜色码）
                "gold_dark": "#CC9900"  # 金色暗色（修正无效颜色码）
            }
        }
    
    def set_theme(self, theme_name):
        """设置主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
    
    def get_current_theme(self):
        """获取当前主题"""
        return self.themes.get(self.current_theme, self.themes["light"])
    
    def get_theme_names(self):
        """获取所有主题名称"""
        return list(self.themes.keys())
    
    def get_title_color(self):
        """获取当前主题的标题颜色"""
        theme = self.get_current_theme()
        return theme.get("title_color", "#0078D7")


class FontManager:
    """字体管理器"""
    
    def __init__(self):
        self.fonts_loaded = False
        self.font_families = {}
        self.load_fonts()
    
    def load_fonts(self):
        """加载字体"""
        font_files = {
            "Black": "HarmonyOS_Sans_SC_Black.ttf",
            "Bold": "HarmonyOS_Sans_SC_Bold.ttf",
            "Thin": "HarmonyOS_Sans_SC_Thin.ttf",
            "Regular": "HarmonyOS_Sans_SC_Regular.ttf",
            "Medium": "HarmonyOS_Sans_SC_Medium.ttf",
            "Light": "HarmonyOS_Sans_SC_Light.ttf"
        }
        
        fonts_dir = "fonts"
        if os.path.exists(fonts_dir) and os.path.isdir(fonts_dir):
            try:
                for weight, filename in font_files.items():
                    font_path = os.path.join(fonts_dir, filename)
                    if os.path.exists(font_path):
                        font_id = QFontDatabase.addApplicationFont(font_path)
                        if font_id != -1:
                            font_families = QFontDatabase.applicationFontFamilies(font_id)
                            if font_families:
                                self.font_families[weight] = font_families[0]
                                self.fonts_loaded = True
                                print(f"加载字体成功: {weight}")
                if not self.fonts_loaded:
                    print("警告: 无法加载任何HarmonyOS字体，将使用系统默认字体")
            except Exception as e:
                print(f"加载字体时出错: {e}")
        else:
            print(f"警告: 字体文件夹'{fonts_dir}'不存在")
    
    def get_font(self, weight="Regular", size=10):
        """获取字体"""
        font = QFont()
        
        if self.fonts_loaded and weight in self.font_families:
            font.setFamily(self.font_families[weight])
        else:
            # 如果字体加载失败，使用系统默认字体
            if weight in ["Black", "Bold"]:
                font.setWeight(QFont.Bold)
            elif weight == "Medium":
                font.setWeight(QFont.Medium)
            elif weight in ["Light", "Thin"]:
                font.setWeight(QFont.Light)
            else:
                font.setWeight(QFont.Normal)
        
        font.setPointSize(size)
        return font


class UserManager:
    """用户管理类，处理用户级别和权限"""
    
    def __init__(self, theme_manager):
        self.user_file = "user_info.json"
        self.theme_manager = theme_manager
        self.on_level_changed = None  # 等级变更回调
        
        # 统一使用带空格的"So Big"作为键名
        self.levels = {
            "Plus": {"price": 0, "max_number": 10, "theme_access": ["light"], "description": "基础版"},
            "Pro": {"price": 24, "max_number": 100, "theme_access": ["light"], "description": "专业版"},
            "Max": {"price": 50, "max_number": 1000, "theme_access": ["light"], "description": "增强版"},
            "Ultra": {"price": 100, "max_number": 1000, "theme_access": ["light", "dark", "morandi"], "description": "高级版"},
            "So Big": {"price": 200, "max_number": float('inf'), "theme_access": ["light", "dark", "morandi", "golden"], "description": "至尊版"}
        }
        self.current_user = self.load_user_info()
    
    def load_user_info(self):
        """从JSON文件加载用户信息"""
        default_info = {
            "level": "Plus",
            "expire_date": None,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "theme": "light"
        }
        
        try:
            if os.path.exists(self.user_file):
                with open(self.user_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 检查是否过期
                    if data.get("expire_date"):
                        expire_date = datetime.strptime(data["expire_date"], "%Y-%m-%d %H:%M:%S")
                        if datetime.now() > expire_date:
                            data["level"] = "Plus"
                            data["expire_date"] = None
                            self.save_user_info(data)
                    
                    # 设置主题
                    if "theme" in data:
                        self.theme_manager.set_theme(data["theme"])
                    
                    return data
            else:
                # 创建默认文件
                self.save_user_info(default_info)
                return default_info
        except Exception as e:
            print(f"加载用户信息失败: {e}")
            return default_info
    
    def save_user_info(self, user_info=None):
        """保存用户信息到JSON文件"""
        if user_info is None:
            user_info = self.current_user
        
        try:
            with open(self.user_file, 'w', encoding='utf-8') as f:
                json.dump(user_info, f, ensure_ascii=False, indent=4)
            
            # 触发等级变更回调
            if self.on_level_changed:
                self.on_level_changed(user_info.get("level", "Plus"))
            
            return True
        except Exception as e:
            print(f"保存用户信息失败: {e}")
            return False
    
    def get_current_level(self):
        """获取当前用户级别"""
        level = self.current_user.get("level", "Plus")
        return level
    
    def upgrade_user(self, level, months=1):
        """升级用户级别"""
        if level not in self.levels:
            return False
        
        # 更新用户信息
        self.current_user["level"] = level
        if level == "Plus":
            self.current_user["expire_date"] = None
        else:
            expire_date = datetime.now() + timedelta(days=30*months)
            self.current_user["expire_date"] = expire_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存用户信息
        if self.save_user_info():
            return True
        return False
    
    def can_calculate(self, a, b, operator):
        """检查用户是否有权限进行计算"""
        level = self.get_current_level()
        max_num = self.levels[level]["max_number"]
        
        # 检查数字大小
        if max_num != float('inf') and (abs(a) > max_num or abs(b) > max_num):
            return False, f"当前版本仅支持{max_num}以内的计算，请升级到更高级别！"
        
        return True, ""
    
    def get_level_info(self, level):
        """获取级别信息"""
        if level in self.levels:
            info = self.levels[level].copy()
            info["name"] = level
            return info
        return None
    
    def get_all_levels(self):
        """获取所有级别信息"""
        return self.levels
    
    def get_expire_days(self):
        """获取剩余天数"""
        if "expire_date" not in self.current_user or not self.current_user["expire_date"]:
            return None
        
        try:
            expire_date = datetime.strptime(self.current_user["expire_date"], "%Y-%m-%d %H:%M:%S")
            days_left = (expire_date - datetime.now()).days
            return max(0, days_left)
        except:
            return None
    
    def check_expire_soon(self):
        """检查是否即将过期（7天内）"""
        days_left = self.get_expire_days()
        if days_left is not None and days_left <= 7:
            return True
        return False
    
    def set_theme(self, theme_name):
        """设置主题"""
        level = self.get_current_level()
        if theme_name in self.levels[level]["theme_access"]:
            self.current_user["theme"] = theme_name
            self.theme_manager.set_theme(theme_name)
            self.save_user_info()
            return True
        else:
            return False
    
    def can_use_theme(self, theme_name):
        """检查用户是否有权限使用该主题"""
        level = self.get_current_level()
        return theme_name in self.levels[level]["theme_access"]


class CalculationThread(QThread):
    """计算线程，用于执行复杂计算过程"""
    
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str, str, str)  # 参数：操作符, 操作数1, 操作数2
    error_signal = pyqtSignal(str)  # 错误信号
    
    def __init__(self, expression, user_manager):
        super().__init__()
        self.expression = expression
        self.user_manager = user_manager
    
    def run(self):
        """解析表达式并执行计算"""
        try:
            # 检查输入是否为空
            if not self.expression.strip():
                self.error_signal.emit("错误：请输入算式")
                return
            
            # 解析表达式
            if '+' in self.expression:
                parts = self.expression.split('+')
                if len(parts) == 2:
                    try:
                        a, b = float(parts[0].strip()), float(parts[1].strip())
                    except ValueError:
                        self.error_signal.emit("错误：请输入有效的数字")
                        return
                    
                    # 检查用户权限
                    can_calc, msg = self.user_manager.can_calculate(a, b, '+')
                    if not can_calc:
                        self.error_signal.emit(f"权限错误: {msg}")
                        return
                    
                    result = self.compute_addition(a, b)
                    self.finished_signal.emit('+', str(a), str(b))
                else:
                    self.error_signal.emit("错误：表达式格式不正确（只能有两个操作数）")
            elif '-' in self.expression:
                parts = self.expression.split('-')
                if len(parts) == 2:
                    try:
                        a, b = float(parts[0].strip()), float(parts[1].strip())
                    except ValueError:
                        self.error_signal.emit("错误：请输入有效的数字")
                        return
                    
                    # 检查用户权限
                    can_calc, msg = self.user_manager.can_calculate(a, b, '-')
                    if not can_calc:
                        self.error_signal.emit(f"权限错误: {msg}")
                        return
                    
                    result = self.compute_subtraction(a, b)
                    self.finished_signal.emit('-', str(a), str(b))
                else:
                    self.error_signal.emit("错误：表达式格式不正确（只能有两个操作数）")
            else:
                self.error_signal.emit("错误：只支持加法和减法，请使用 + 或 -")
        
        except Exception as e:
            self.error_signal.emit(f"发生错误: {str(e)}")
    
    def slow_output(self, text):
        """模拟缓慢输出"""
        for char in text:
            self.output_signal.emit(char)
            time.sleep(0.03)
        self.output_signal.emit('\n')
    
    def compute_addition(self, a, b):
        """加法计算"""
        self.slow_output(f"开始计算 {a} + {b} ...")
        time.sleep(1)
        
        self.slow_output("\n=== 阶段1: 欧拉公式推导 ===")
        time.sleep(0.5)
        
        self.slow_output("exp(z) = Σ[n=0→∞] z^n/n!")
        time.sleep(0.5)
        
        self.slow_output("令 z = iπ，得到 exp(iπ) = Σ[n=0→∞] (iπ)^n/n!")
        time.sleep(0.5)
        
        self.slow_output("i^0 = 1, i^1 = i, i^2 = -1, i^3 = -i, i^4 = 1, ...")
        time.sleep(0.5)
        
        self.slow_output("分离实部和虚部：")
        self.slow_output("exp(iπ) = Σ[k=0→∞] (-1)^k π^{2k}/(2k)! + iΣ[k=0→∞] (-1)^k π^{2k+1}/(2k+1)!")
        time.sleep(0.5)
        
        self.slow_output("这对应余弦和正弦的泰勒级数：")
        self.slow_output("cos(π) = Σ[k=0→∞] (-1)^k π^{2k}/(2k)! = -1")
        self.slow_output("sin(π) = Σ[k=0→∞] (-1)^k π^{2k+1}/(2k+1)! = 0")
        time.sleep(0.5)
        
        self.slow_output("因此：exp(iπ) = cos(π) + i sin(π) = -1 + 0i = -1")
        time.sleep(0.5)
        
        self.slow_output("欧拉恒等式：exp(iπ) + 1 = 0")
        time.sleep(0.5)
        
        self.slow_output("\n=== 阶段2: 定义辅助函数 ===")
        time.sleep(0.5)
        
        self.slow_output("定义 f(θ) = exp(iθ) + exp(-iθ)")
        time.sleep(0.5)
        
        self.slow_output("使用欧拉公式：")
        self.slow_output("f(θ) = (cosθ + i sinθ) + (cosθ - i sinθ)")
        self.slow_output("f(θ) = 2cosθ")
        time.sleep(0.5)
        
        self.slow_output("\n=== 阶段3: 计算f(0) ===")
        time.sleep(0.5)
        
        self.slow_output("方法1: 直接计算")
        self.slow_output(f"f(0) = exp(i·0) + exp(-i·0)")
        self.slow_output(f"exp(0) = Σ[n=0→∞] 0^n/n! = 1")
        self.slow_output(f"因此 f(0) = 1 + 1")
        time.sleep(0.5)
        
        self.slow_output("\n方法2: 通过f(θ) = 2cosθ计算")
        self.slow_output(f"f(0) = 2cos(0)")
        self.slow_output(f"cos(0) = Σ[k=0→∞] (-1)^k·0^(2k)/(2k)! = 1")
        self.slow_output(f"因此 f(0) = 2·1 = 2")
        time.sleep(0.5)
        
        self.slow_output("\n=== 阶段4: 积分验证 ===")
        time.sleep(0.5)
        
        self.slow_output("计算积分 I = ∫[0,π/2] sin²φ dφ = π/4")
        self.slow_output("计算积分 J = ∫[0,π/2] cos²φ dφ = π/4")
        time.sleep(0.5)
        
        self.slow_output("定义 A = (2/π)I = 1/2, B = (2/π)J = 1/2")
        self.slow_output("则 2A = 1, 2B = 1")
        self.slow_output("2A + 2B = 1 + 1")
        time.sleep(0.5)
        
        self.slow_output("但 2A + 2B = 2(A+B) = 2(2/π I + 2/π J)")
        self.slow_output(f"= (4/π)(I+J) = (4/π)(π/2) = 2")
        time.sleep(0.5)
        
        self.slow_output("\n=== 阶段5: 微分方程验证 ===")
        time.sleep(0.5)
        
        self.slow_output("解微分方程 dy/dx = y, y(0) = 1")
        self.slow_output("解为 y(x) = exp(x)")
        self.slow_output("计算 y(ln2) = exp(ln2) = 2")
        time.sleep(0.5)
        
        self.slow_output("注意到 y(0) = 1")
        self.slow_output("y(ln2) = 2y(0) = 2·1 = 2")
        time.sleep(0.5)
        
        self.slow_output("\n=== 阶段6: 代数验证 ===")
        time.sleep(0.5)
        
        self.slow_output("考虑恒等式 (1+1)² = 1² + 2·1·1 + 1² = 1 + 2 + 1 = 4")
        self.slow_output("因此 1 + 1 = √4 = 2 (取正根)")
        time.sleep(0.5)
        
        self.slow_output("\n=== 阶段7: 推广到一般情况 ===")
        time.sleep(0.5)
        
        self.slow_output(f"将上述推导中的'1'替换为具体的数值:")
        self.slow_output(f"设 x = {a}, y = {b}")
        
        self.slow_output(f"\n根据加法交换律和结合律:")
        self.slow_output(f"x + y = {a} + {b}")
        
        self.slow_output(f"\n根据实数域的完备性:")
        self.slow_output(f"存在唯一实数 r 使得 r = {a} + {b}")
        time.sleep(0.5)
        
        result = a + b
        
        self.slow_output("\n" + "="*50)
        self.slow_output(f"最终结论：{a} + {b} = {result}")
        self.slow_output("="*50)
        
        return result
    
    def compute_subtraction(self, a, b):
        """减法计算"""
        self.slow_output(f"开始计算 {a} - {b} ...")
        time.sleep(1)
        
        self.slow_output("\n=== 阶段1: 转换为加法 ===")
        time.sleep(0.5)
        
        self.slow_output(f"减法 {a} - {b} 可以转化为加法:")
        self.slow_output(f"{a} - {b} = {a} + (-{b})")
        time.sleep(0.5)
        
        self.slow_output("\n=== 阶段2: 使用加法推导 ===")
        time.sleep(0.5)
        
        # 调用加法计算
        result = a + (-b)
        self.slow_output(f"根据加法推导:")
        self.slow_output(f"{a} + (-{b}) = {result}")
        time.sleep(0.5)
        
        self.slow_output("\n" + "="*50)
        self.slow_output(f"最终结论：{a} - {b} = {result}")
        self.slow_output("="*50)
        
        return result


class CalculationDialog(QDialog):
    """计算过程显示对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("计算过程")
        self.setMinimumSize(700, 500)
        
        # 设置窗口属性
        self.setModal(True)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 创建文本框
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Consolas", 10))
        layout.addWidget(self.text_edit)
        
        # 创建按钮
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("关闭")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # 设置窗口标志
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
    
    def append_text(self, text):
        """向文本框添加文本"""
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        if text == '\n':
            cursor.insertText(text)
        else:
            cursor.insertText(text)
            
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()
        QApplication.processEvents()  # 更新UI
    
    def show_error(self, error_message):
        """显示错误信息"""
        self.append_text(f"\n⚠️ {error_message}")


class PaymentDialog(QDialog):
    """支付页面"""
    
    def __init__(self, level_name, price, font_manager, parent=None):
        super().__init__(parent)
        self.font_manager = font_manager
        self.setWindowTitle(f"支付 - {level_name}")
        self.setMinimumSize(800, 650)
        
        # 设置窗口属性
        self.setModal(True)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 添加标题
        title_label = QLabel(f"升级到 {level_name} 版本")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(self.font_manager.get_font("Bold", 20))
        title_label.setObjectName("payment_title")
        main_layout.addWidget(title_label)
        
        # 添加价格
        price_label = QLabel(f"价格: ¥{price}/月")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setFont(self.font_manager.get_font("Bold", 18))
        price_label.setObjectName("payment_price")
        main_layout.addWidget(price_label)
        
        # 添加描述
        desc_label = QLabel("请选择支付方式并扫描二维码完成支付")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(self.font_manager.get_font("Regular", 14))
        desc_label.setObjectName("payment_desc")
        main_layout.addWidget(desc_label)
        
        # 创建图片容器
        images_layout = QHBoxLayout()
        images_layout.setSpacing(30)
        
        # 微信支付图片
        wechat_layout = QVBoxLayout()
        wechat_title = QLabel("微信支付")
        wechat_title.setAlignment(Qt.AlignCenter)
        wechat_title.setFont(self.font_manager.get_font("Bold", 16))
        wechat_layout.addWidget(wechat_title)
        
        self.wechat_image = QLabel()
        self.wechat_image.setAlignment(Qt.AlignCenter)
        self.wechat_image.setMinimumSize(300, 300)
        self.wechat_image.setMaximumSize(300, 300)
        self.wechat_image.setObjectName("payment_image")
        wechat_layout.addWidget(self.wechat_image)
        wechat_layout.addStretch()
        
        # 支付宝图片
        alipay_layout = QVBoxLayout()
        alipay_title = QLabel("支付宝")
        alipay_title.setAlignment(Qt.AlignCenter)
        alipay_title.setFont(self.font_manager.get_font("Bold", 16))
        alipay_layout.addWidget(alipay_title)
        
        self.alipay_image = QLabel()
        self.alipay_image.setAlignment(Qt.AlignCenter)
        self.alipay_image.setMinimumSize(300, 300)
        self.alipay_image.setMaximumSize(300, 300)
        self.alipay_image.setObjectName("payment_image")
        alipay_layout.addWidget(self.alipay_image)
        alipay_layout.addStretch()
        
        # 加载图片
        self.load_images()
        
        # 将两个图片布局添加到主布局
        images_layout.addLayout(wechat_layout)
        images_layout.addLayout(alipay_layout)
        main_layout.addLayout(images_layout)
        
        # 添加提示文字
        hint_label = QLabel("你不用真的支付，仅供娱乐，当然也可以赞助我这个高一牲一杯瑞幸的茉莉花香拿铁哦~")
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setFont(self.font_manager.get_font("Light", 12))
        hint_label.setObjectName("payment_hint")
        hint_label.setWordWrap(True)
        main_layout.addWidget(hint_label)
        
        # 添加倒计时按钮
        self.payment_button = QPushButton("我已支付 (3)")
        self.payment_button.clicked.connect(self.on_payment_clicked)
        self.payment_button.setEnabled(False)
        self.payment_button.setMinimumHeight(50)
        self.payment_button.setFont(self.font_manager.get_font("Medium", 16))
        self.payment_button.setObjectName("payment_button")
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.payment_button, 0, Qt.AlignCenter)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 设置窗口标志
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 启动倒计时
        self.countdown_time = 3
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_button_text)
        self.timer.start(1000)  # 每秒触发一次
        
        # 保存等级信息
        self.level_name = level_name
        self.price = price
    
    def load_images(self):
        """加载支付二维码图片"""
        try:
            # 检查picture文件夹是否存在
            if not os.path.exists("picture"):
                os.makedirs("picture")
                print("创建了picture文件夹")
            
            # 加载微信支付图片
            wechat_path = "picture/wechatpay.png"
            if os.path.exists(wechat_path):
                wechat_pixmap = QPixmap(wechat_path)
                if not wechat_pixmap.isNull():
                    # 缩放图片到合适大小
                    wechat_pixmap = wechat_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.wechat_image.setPixmap(wechat_pixmap)
                else:
                    self.show_default_image(self.wechat_image, "微信支付")
            else:
                self.show_default_image(self.wechat_image, "微信支付")
        except Exception as e:
            print(f"加载微信支付图片失败: {e}")
            self.show_default_image(self.wechat_image, "微信支付")
        
        try:
            # 加载支付宝图片
            alipay_path = "picture/alipay.png"
            if os.path.exists(alipay_path):
                alipay_pixmap = QPixmap(alipay_path)
                if not alipay_pixmap.isNull():
                    # 缩放图片到合适大小
                    alipay_pixmap = alipay_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.alipay_image.setPixmap(alipay_pixmap)
                else:
                    self.show_default_image(self.alipay_image, "支付宝")
            else:
                self.show_default_image(self.alipay_image, "支付宝")
        except Exception as e:
            print(f"加载支付宝图片失败: {e}")
            self.show_default_image(self.alipay_image, "支付宝")
    
    def show_default_image(self, label, platform):
        """显示默认图片"""
        label.setText(f"{platform}\n(图片加载失败)\n\n请将图片放入\npicture文件夹")
        label.setFont(self.font_manager.get_font("Regular", 14))
        label.setStyleSheet("""
            QLabel {
                border: 2px dashed #999;
                padding: 10px;
                color: #666;
                background-color: #f9f9f9;
            }
        """)
    
    def update_button_text(self):
        """更新按钮倒计时文本"""
        self.countdown_time -= 1
        if self.countdown_time > 0:
            self.payment_button.setText(f"我已支付 ({self.countdown_time})")
        else:
            self.payment_button.setText("我已支付")
            self.payment_button.setEnabled(True)
            self.timer.stop()
    
    def on_payment_clicked(self):
        """支付按钮点击事件"""
        QMessageBox.information(self, "支付成功", f"恭喜您成功升级到 {self.level_name} 版本！")
        self.accept()


class SponsorDialog(QDialog):
    """赞助页面对话框"""
    
    def __init__(self, font_manager, parent=None):
        super().__init__(parent)
        self.font_manager = font_manager
        self.setWindowTitle("支持我们")
        self.setMinimumSize(800, 750)
        
        # 设置窗口属性
        self.setModal(True)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 添加标题
        title_label = QLabel("感谢您的支持！")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(self.font_manager.get_font("Bold", 20))
        title_label.setObjectName("sponsor_title")
        main_layout.addWidget(title_label)
        
        # 添加介绍文字
        intro_label = QLabel(
            "这个程序由一名高中牲开发，如果喜欢赞助一下孩纸吧，孩纸爱喝瑞幸茉莉花香拿铁~ "
            "您的支持是我继续开发的动力，感谢每一位支持我的朋友！"
        )
        intro_label.setAlignment(Qt.AlignCenter)
        intro_label.setFont(self.font_manager.get_font("Regular", 14))
        intro_label.setObjectName("sponsor_intro")
        intro_label.setWordWrap(True)
        main_layout.addWidget(intro_label)
        
        # 添加描述
        desc_label = QLabel("请扫描下方二维码进行赞助，支持我们继续开发优秀软件！")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(self.font_manager.get_font("Regular", 14))
        desc_label.setObjectName("sponsor_desc")
        main_layout.addWidget(desc_label)
        
        # 创建图片容器
        images_layout = QHBoxLayout()
        images_layout.setSpacing(30)
        
        # 微信支付图片
        wechat_layout = QVBoxLayout()
        wechat_title = QLabel("微信支付")
        wechat_title.setAlignment(Qt.AlignCenter)
        wechat_title.setFont(self.font_manager.get_font("Bold", 16))
        wechat_layout.addWidget(wechat_title)
        
        self.wechat_image = QLabel()
        self.wechat_image.setAlignment(Qt.AlignCenter)
        self.wechat_image.setMinimumSize(300, 300)
        self.wechat_image.setMaximumSize(300, 300)
        self.wechat_image.setObjectName("sponsor_image")
        wechat_layout.addWidget(self.wechat_image)
        wechat_layout.addStretch()
        
        # 支付宝图片
        alipay_layout = QVBoxLayout()
        alipay_title = QLabel("支付宝")
        alipay_title.setAlignment(Qt.AlignCenter)
        alipay_title.setFont(self.font_manager.get_font("Bold", 16))
        alipay_layout.addWidget(alipay_title)
        
        self.alipay_image = QLabel()
        self.alipay_image.setAlignment(Qt.AlignCenter)
        self.alipay_image.setMinimumSize(300, 300)
        self.alipay_image.setMaximumSize(300, 300)
        self.alipay_image.setObjectName("sponsor_image")
        alipay_layout.addWidget(self.alipay_image)
        alipay_layout.addStretch()
        
        # 加载图片
        self.load_images()
        
        # 将两个图片布局添加到主布局
        images_layout.addLayout(wechat_layout)
        images_layout.addLayout(alipay_layout)
        main_layout.addLayout(images_layout)
        
        # 添加按钮容器
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(30)
        button_layout.setContentsMargins(50, 10, 50, 10)
        
        # 投币按钮
        coin_button = QPushButton("投币")
        coin_button.clicked.connect(lambda: webbrowser.open("https://space.bilibili.com/3546558473702169"))
        coin_button.setMinimumHeight(50)
        coin_button.setFont(self.font_manager.get_font("Medium", 16))
        coin_button.setStyleSheet("""
            QPushButton {
                background-color: #00A1D6;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #0092C3;
            }
        """)
        button_layout.addWidget(coin_button)
        
        # Star按钮
        star_button = QPushButton("Star")
        star_button.clicked.connect(lambda: webbrowser.open("https://github.com/Mirage-BIN/Intelligence-Calculator"))
        star_button.setMinimumHeight(50)
        star_button.setFont(self.font_manager.get_font("Medium", 16))
        star_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        button_layout.addWidget(star_button)
        
        main_layout.addWidget(button_container)
        
        # 添加倒计时按钮
        self.sponsor_button = QPushButton("我已赞助 (3)")
        self.sponsor_button.clicked.connect(self.on_sponsor_clicked)
        self.sponsor_button.setEnabled(False)
        self.sponsor_button.setMinimumHeight(50)
        self.sponsor_button.setFont(self.font_manager.get_font("Medium", 16))
        self.sponsor_button.setObjectName("sponsor_button")
        
        sponsor_button_layout = QHBoxLayout()
        sponsor_button_layout.addStretch()
        sponsor_button_layout.addWidget(self.sponsor_button, 0, Qt.AlignCenter)
        sponsor_button_layout.addStretch()
        main_layout.addLayout(sponsor_button_layout)
        
        # 设置窗口标志
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 启动倒计时
        self.countdown_time = 3
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_button_text)
        self.timer.start(1000)  # 每秒触发一次
    
    def load_images(self):
        """加载赞助二维码图片"""
        try:
            # 检查picture文件夹是否存在
            if not os.path.exists("picture"):
                os.makedirs("picture")
                print("创建了picture文件夹")
            
            # 加载微信支付图片
            wechat_path = "picture/wechatpay.png"
            if os.path.exists(wechat_path):
                wechat_pixmap = QPixmap(wechat_path)
                if not wechat_pixmap.isNull():
                    # 缩放图片到合适大小
                    wechat_pixmap = wechat_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.wechat_image.setPixmap(wechat_pixmap)
                else:
                    self.show_default_image(self.wechat_image, "微信支付")
            else:
                self.show_default_image(self.wechat_image, "微信支付")
        except Exception as e:
            print(f"加载微信支付图片失败: {e}")
            self.show_default_image(self.wechat_image, "微信支付")
        
        try:
            # 加载支付宝图片
            alipay_path = "picture/alipay.png"
            if os.path.exists(alipay_path):
                alipay_pixmap = QPixmap(alipay_path)
                if not alipay_pixmap.isNull():
                    # 缩放图片到合适大小
                    alipay_pixmap = alipay_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.alipay_image.setPixmap(alipay_pixmap)
                else:
                    self.show_default_image(self.alipay_image, "支付宝")
            else:
                self.show_default_image(self.alipay_image, "支付宝")
        except Exception as e:
            print(f"加载支付宝图片失败: {e}")
            self.show_default_image(self.alipay_image, "支付宝")
    
    def show_default_image(self, label, platform):
        """显示默认图片"""
        label.setText(f"{platform}\n(图片加载失败)\n\n请将图片放入\npicture文件夹")
        label.setFont(self.font_manager.get_font("Regular", 14))
        label.setStyleSheet("""
            QLabel {
                border: 2px dashed #999;
                padding: 10px;
                color: #666;
                background-color: #f9f9f9;
            }
        """)
    
    def update_button_text(self):
        """更新按钮倒计时文本"""
        self.countdown_time -= 1
        if self.countdown_time > 0:
            self.sponsor_button.setText(f"我已赞助 ({self.countdown_time})")
        else:
            self.sponsor_button.setText("我已赞助")
            self.sponsor_button.setEnabled(True)
            self.timer.stop()
    
    def on_sponsor_clicked(self):
        """赞助按钮点击事件"""
        QMessageBox.information(self, "感谢赞助", "非常感谢您的赞助！您的支持是我们前进的动力！")
        self.accept()


class VIPDialog(QDialog):
    """VIP充值页面"""
    
    def __init__(self, user_manager, font_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.font_manager = font_manager
        self.setWindowTitle("VIP会员中心")
        self.setMinimumSize(1000, 500)
        
        # 设置窗口属性
        self.setModal(True)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 添加标题
        title_label = QLabel("🚀 升级你的计算体验")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(self.font_manager.get_font("Bold", 24))
        title_label.setObjectName("vip_title")
        main_layout.addWidget(title_label)
        
        # 当前会员状态
        current_level = self.user_manager.get_current_level()
        expire_days = self.user_manager.get_expire_days()
        
        status_text = f"当前版本: <b>{current_level}</b>"
        if expire_days is not None:
            status_text += f" | 剩余天数: <b>{expire_days}天</b>"
        
        status_label = QLabel(status_text)
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setFont(self.font_manager.get_font("Medium", 16))
        status_label.setObjectName("vip_status")
        main_layout.addWidget(status_label)
        
        # 创建水平布局容器
        packages_container = QWidget()
        packages_layout = QHBoxLayout(packages_container)
        packages_layout.setSpacing(15)
        packages_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建每个套餐的卡片
        level_names = ["Plus", "Pro", "Max", "Ultra", "So Big"]
        
        for level_name in level_names:
            level_info = self.user_manager.get_level_info(level_name)
            if level_info:
                package_card = self.create_package_card(level_info, current_level)
                packages_layout.addWidget(package_card)
        
        # 将水平布局容器添加到主布局
        main_layout.addWidget(packages_container, 0, Qt.AlignCenter)
        
        # 添加说明文字
        note_label = QLabel("💡 仅供娱乐展示，不用真充，选择好套餐点击购买即可[doge]")
        note_label.setAlignment(Qt.AlignCenter)
        note_label.setFont(self.font_manager.get_font("Light", 12))
        note_label.setObjectName("vip_note")
        main_layout.addWidget(note_label)
        
        main_layout.addStretch()
        
        # 设置窗口标志
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    
    def create_package_card(self, level_info, current_level):
        """创建套餐卡片"""
        card = QWidget()
        card.setMinimumWidth(180)
        card.setMinimumHeight(320)
        card.setObjectName("vip_package_card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # 设置卡片样式 - 仅保留边框
        is_current = (level_info["name"] == current_level)
        if level_info["name"] == "So Big":
            border_color = "#FFD700"
        elif level_info["name"] == "Ultra":
            border_color = "#9C27B0"
        elif level_info["name"] == "Max":
            border_color = "#2196F3"
        elif level_info["name"] == "Pro":
            border_color = "#4CAF50"
        else:  # Plus
            border_color = "#9E9E9E"
        
        card.setStyleSheet(f"""
            QWidget#vip_package_card {{
                border: 2px solid {border_color};
                border-radius: 8px;
                background-color: transparent;
            }}
        """)
        
        # 套餐名称
        name_label = QLabel(level_info["name"])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setFont(self.font_manager.get_font("Bold", 16))
        name_label.setStyleSheet(f"color: {border_color};")
        card_layout.addWidget(name_label)
        
        # 套餐描述
        desc_label = QLabel(level_info["description"])
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setFont(self.font_manager.get_font("Regular", 13))
        desc_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        card_layout.addWidget(desc_label)
        
        # 功能特点
        features = QWidget()
        features_layout = QVBoxLayout(features)
        features_layout.setSpacing(6)
        features_layout.setContentsMargins(0, 0, 0, 0)
        
        if level_info["max_number"] == float('inf'):
            max_num = "∞"
        else:
            max_num = f"{level_info['max_number']}"
        
        max_label = QLabel(f"计算范围: {max_num}")
        max_label.setAlignment(Qt.AlignCenter)
        max_label.setFont(self.font_manager.get_font("Regular", 12))
        features_layout.addWidget(max_label)
        
        theme_label = QLabel(f"可用主题: {len(level_info['theme_access'])}种")
        theme_label.setAlignment(Qt.AlignCenter)
        theme_label.setFont(self.font_manager.get_font("Regular", 12))
        features_layout.addWidget(theme_label)
        
        card_layout.addWidget(features)
        card_layout.addStretch()
        
        # 价格
        price_container = QWidget()
        price_layout = QVBoxLayout(price_container)
        price_layout.setSpacing(5)
        
        if level_info["price"] > 0:
            price_label = QLabel(f"¥{level_info['price']}/月")
            price_label.setAlignment(Qt.AlignCenter)
            price_label.setFont(self.font_manager.get_font("Bold", 18))
            price_label.setStyleSheet("color: #FF6B6B; margin-bottom: 5px;")
            price_layout.addWidget(price_label)
            
            # 购买按钮
            buy_button = QPushButton("立即购买")
            buy_button.clicked.connect(lambda checked, ln=level_info['name'], p=level_info['price']: self.on_buy_clicked(ln, p))
            buy_button.setMinimumHeight(35)
            buy_button.setFont(self.font_manager.get_font("Medium", 12))
            buy_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {border_color};
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    padding: 8px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(border_color)};
                }}
            """)
            price_layout.addWidget(buy_button)
        else:
            price_label = QLabel("免费")
            price_label.setAlignment(Qt.AlignCenter)
            price_label.setFont(self.font_manager.get_font("Bold", 18))
            price_label.setStyleSheet("color: #4CAF50; margin-bottom: 5px;")
            price_layout.addWidget(price_label)
            
            # 当前版本标记
            if is_current:
                current_label = QLabel("✅ 当前版本")
                current_label.setAlignment(Qt.AlignCenter)
                current_label.setFont(self.font_manager.get_font("Regular", 12))
                current_label.setStyleSheet("color: #666;")
                price_layout.addWidget(current_label)
        
        card_layout.addWidget(price_container)
        
        return card
    
    def darken_color(self, hex_color):
        """将颜色变暗"""
        # 简单的颜色变暗处理
        if hex_color == "#FFD700":  # So Big
            return "#E6C200"
        elif hex_color == "#9C27B0":  # Ultra
            return "#8E24AA"
        elif hex_color == "#2196F3":  # Max
            return "#1E88E5"
        elif hex_color == "#4CAF50":  # Pro
            return "#43A047"
        else:  # Plus
            return "#757575"
    
    def on_buy_clicked(self, level_name, price):
        """购买按钮点击事件"""
        payment_dialog = PaymentDialog(level_name, price, self.font_manager, self)
        if payment_dialog.exec():
            # 用户点击了"我已支付"，升级用户
            if self.user_manager.upgrade_user(level_name, 1):
                # 重新加载页面以更新状态
                self.accept()
            else:
                QMessageBox.warning(self, "升级失败", "升级失败，请检查文件权限。")
        else:
            # 用户取消了支付
            pass


class ResultDialog(QDialog):
    """结果显示对话框"""
    
    def __init__(self, expression, result, font_manager, parent=None):
        super().__init__(parent)
        self.font_manager = font_manager
        self.setWindowTitle("计算成功")
        self.setMinimumSize(500, 250)
        
        # 设置窗口属性
        self.setModal(True)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 创建成功图标
        icon_label = QLabel("✅")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon_label)
        
        # 创建结果标签
        result_label = QLabel(f"{expression} = {result}")
        result_label.setAlignment(Qt.AlignCenter)
        result_label.setFont(self.font_manager.get_font("Bold", 18))
        result_label.setObjectName("result_text")
        layout.addWidget(result_label)
        
        # 添加说明标签
        info_label = QLabel("计算完成！感谢使用 Intelligence Calculator！")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(self.font_manager.get_font("Regular", 12))
        info_label.setObjectName("result_info")
        layout.addWidget(info_label)
        
        # 添加赞助按钮
        sponsor_button = QPushButton("太棒了，这就去赞助")
        sponsor_button.clicked.connect(self.open_sponsor_page)
        sponsor_button.setMinimumHeight(45)
        sponsor_button.setFont(self.font_manager.get_font("Medium", 14))
        sponsor_button.setObjectName("result_sponsor_button")
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(sponsor_button, 0, Qt.AlignCenter)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 设置窗口标志
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    
    def open_sponsor_page(self):
        """打开赞助页面"""
        self.accept()  # 关闭当前对话框
        sponsor_dialog = SponsorDialog(self.font_manager, self.parent())
        sponsor_dialog.exec()


class ThemeDialog(QDialog):
    """主题选择对话框"""
    
    def __init__(self, user_manager, font_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.font_manager = font_manager
        self.setWindowTitle("选择主题")
        self.setMinimumSize(500, 400)
        
        # 设置窗口属性
        self.setModal(True)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # 添加标题
        title_label = QLabel("选择主题")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(self.font_manager.get_font("Bold", 20))
        title_label.setObjectName("theme_title")
        main_layout.addWidget(title_label)
        
        # 当前主题信息
        current_theme = self.user_manager.theme_manager.current_theme
        current_level = self.user_manager.get_current_level()
        
        info_label = QLabel(f"当前主题: <b>{current_theme}</b> | 当前版本: <b>{current_level}</b>")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setFont(self.font_manager.get_font("Medium", 14))
        info_label.setObjectName("theme_info")
        main_layout.addWidget(info_label)
        
        # 创建主题卡片容器
        themes_container = QWidget()
        themes_layout = QGridLayout(themes_container)
        themes_layout.setSpacing(15)
        themes_layout.setContentsMargins(0, 0, 0, 0)
        
        # 定义主题信息
        themes_info = [
            {"name": "light", "display": "明亮", "color": "#F5F5F5", "text_color": "#333333", "icon": "theme.png"},
            {"name": "dark", "display": "暗夜", "color": "#1E1E1E", "text_color": "#FFFFFF", "icon": "theme.png"},
            {"name": "morandi", "display": "莫兰迪", "color": "#F5F0EB", "text_color": "#5C534E", "icon": "theme.png"},
            {"name": "golden", "display": "黑金", "color": "#0A0A0A", "text_color": "#FFD700", "icon": "theme.png"}
        ]
        
        # 创建主题卡片
        for i, theme_info in enumerate(themes_info):
            theme_card = self.create_theme_card(theme_info)
            themes_layout.addWidget(theme_card, i // 2, i % 2)
        
        main_layout.addWidget(themes_container)
        
        # 添加版本限制说明
        note_label = QLabel("💡 注意：部分主题需要更高级别的会员才能使用")
        note_label.setAlignment(Qt.AlignCenter)
        note_label.setFont(self.font_manager.get_font("Light", 12))
        note_label.setObjectName("theme_note")
        main_layout.addWidget(note_label)
        
        # 添加关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        close_button.setMinimumHeight(40)
        close_button.setFont(self.font_manager.get_font("Medium", 12))
        close_button.setObjectName("theme_close_button")
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button, 0, Qt.AlignCenter)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 设置窗口标志
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
    
    def create_theme_card(self, theme_info):
        """创建主题卡片"""
        card = QWidget()
        card.setMinimumWidth(200)
        card.setMinimumHeight(120)
        card.setObjectName("theme_card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(15, 15, 15, 15)
        
        # 检查用户是否有权限使用该主题
        can_use = self.user_manager.can_use_theme(theme_info["name"])
        
        # 设置卡片样式 - 仅保留边框
        card.setStyleSheet(f"""
            QWidget#theme_card {{
                border: 2px solid {'#4CAF50' if can_use else '#F44336'};
                border-radius: 8px;
                background-color: transparent;
            }}
        """)
        
        # 主题图标和名称
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        # 加载主题图标
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setAlignment(Qt.AlignCenter)
        
        try:
            # 检查picture文件夹是否存在
            if not os.path.exists("picture"):
                os.makedirs("picture")
                print("创建了picture文件夹")
            
            # 加载主题图标
            theme_path = "picture/theme.png"
            if os.path.exists(theme_path):
                theme_pixmap = QPixmap(theme_path)
                if not theme_pixmap.isNull():
                    # 缩放图片到合适大小
                    theme_pixmap = theme_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon_label.setPixmap(theme_pixmap)
                else:
                    icon_label.setText("🎨")
                    icon_label.setFont(QFont("Segoe UI Emoji", 16))
            else:
                icon_label.setText("🎨")
                icon_label.setFont(QFont("Segoe UI Emoji", 16))
        except Exception as e:
            print(f"加载主题图标失败: {e}")
            icon_label.setText("🎨")
            icon_label.setFont(QFont("Segoe UI Emoji", 16))
        
        header_layout.addWidget(icon_label)
        
        name_label = QLabel(theme_info["display"])
        name_label.setFont(self.font_manager.get_font("Bold", 16))
        name_label.setStyleSheet(f"color: {theme_info['text_color']};")
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        card_layout.addWidget(header_widget)
        
        # 主题描述
        desc_label = QLabel(f"主题: {theme_info['name']}")
        desc_label.setFont(self.font_manager.get_font("Regular", 13))
        desc_label.setStyleSheet(f"color: {theme_info['text_color']};")
        card_layout.addWidget(desc_label)
        
        card_layout.addStretch()
        
        # 状态标签
        if can_use:
            status_label = QLabel("✅ 可用")
            status_label.setFont(self.font_manager.get_font("Medium", 12))
            status_label.setStyleSheet(f"color: {theme_info['text_color']};")
        else:
            status_label = QLabel("🔒 需要升级")
            status_label.setFont(self.font_manager.get_font("Medium", 12))
            status_label.setStyleSheet(f"color: {theme_info['text_color']};")
        
        status_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(status_label)
        
        # 应用按钮
        apply_button = QPushButton("应用主题" if can_use else "需要升级")
        apply_button.clicked.connect(lambda checked, tn=theme_info['name']: self.apply_theme(tn))
        apply_button.setEnabled(can_use)
        apply_button.setMinimumHeight(30)
        apply_button.setFont(self.font_manager.get_font("Medium", 11))
        
        if can_use:
            apply_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {theme_info['text_color']};
                    color: {theme_info['color']};
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """)
        else:
            apply_button.setStyleSheet("""
                QPushButton {
                    background-color: #9E9E9E;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
        
        card_layout.addWidget(apply_button)
        
        return card
    
    def apply_theme(self, theme_name):
        """应用主题"""
        if self.user_manager.set_theme(theme_name):
            QMessageBox.information(self, "主题切换", f"已切换到 {theme_name} 主题！")
            self.accept()
        else:
            QMessageBox.warning(self, "主题切换失败", "您当前版本无法使用此主题，请升级到更高级别！")


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化字体管理器
        self.font_manager = FontManager()
        
        # 初始化主题管理器
        self.theme_manager = ThemeManager()
        
        # 初始化用户管理器
        self.user_manager = UserManager(self.theme_manager)
        
        # 设置窗口属性
        self.setWindowTitle("Intelligence Calculator")
        self.resize(650, 450)
        
        # 设置等级变更回调
        self.user_manager.on_level_changed = self.on_level_changed
        
        try:
            # 初始化界面
            self.init_ui()
            
            # 初始化Windows通知器
            try:
                self.toaster = ToastNotifier()
            except:
                self.toaster = None
                print("Windows通知器初始化失败，将继续运行")
            
            # 检查会员状态
            self.check_membership_status()
            
        except Exception as e:
            print(f"初始化失败: {e}")
            QMessageBox.critical(self, "初始化错误", f"程序初始化失败:\n{str(e)}")
            sys.exit(1)
    
    def init_ui(self):
        """初始化用户界面"""
        # 应用当前主题
        self.apply_theme()
        
        # 创建中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 30, 40, 30)
        
        # 第一行：按钮行（靠右）
        button_row = QWidget()
        button_layout = QHBoxLayout(button_row)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)
        
        # 左侧留空，使按钮靠右
        button_layout.addStretch()
        
        # GitHub按钮
        self.github_button = QPushButton()
        self.github_button.setFixedSize(32, 32)
        self.github_button.setCursor(Qt.PointingHandCursor)
        self.github_button.clicked.connect(lambda: webbrowser.open("https://github.com/Mirage-BIN/Intelligence-Calculator"))
        self.github_button.setToolTip("GitHub")
        self.github_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }
        """)
        self.load_github_icon()
        button_layout.addWidget(self.github_button)
        
        # 点赞按钮（打开赞助页面）
        self.like_button = QPushButton()
        self.like_button.setFixedSize(32, 32)
        self.like_button.setCursor(Qt.PointingHandCursor)
        self.like_button.clicked.connect(self.open_sponsor_page)
        self.like_button.setToolTip("点赞支持")
        self.like_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }
        """)
        self.load_like_icon()
        button_layout.addWidget(self.like_button)
        
        # 主题切换按钮
        self.theme_button = QPushButton()
        self.theme_button.setFixedSize(32, 32)
        self.theme_button.setCursor(Qt.PointingHandCursor)
        self.theme_button.clicked.connect(self.show_theme_dialog)
        self.theme_button.setToolTip("切换主题")
        self.theme_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }
        """)
        self.load_theme_icon()
        button_layout.addWidget(self.theme_button)
        
        main_layout.addWidget(button_row)
        
        # 第二行：标题和VIP等级标签（居中）
        title_row = QWidget()
        title_layout = QHBoxLayout(title_row)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(15)
        
        # 添加标题
        self.title_label = QLabel("Intelligence Calculator")
        self.title_label.setFont(self.font_manager.get_font("Black", 28))
        title_color = self.theme_manager.get_title_color()
        self.title_label.setStyleSheet(f"color: {title_color};")
        
        # 添加VIP标签 - 可点击
        current_level = self.user_manager.get_current_level()
        self.vip_label = QLabel(f" {current_level} ")
        self.vip_label.setCursor(Qt.PointingHandCursor)
        self.vip_label.setFont(self.font_manager.get_font("Medium", 14))
        self.vip_label.mousePressEvent = self.on_vip_label_clicked
        
        # 更新VIP标签样式
        self.update_vip_label_style(current_level)
        
        # 将标题和VIP标签居中
        title_layout.addStretch()
        title_layout.addWidget(self.title_label, 0, Qt.AlignVCenter)
        title_layout.addWidget(self.vip_label, 0, Qt.AlignVCenter)
        title_layout.addStretch()
        
        main_layout.addWidget(title_row)
        
        # 添加当前版本信息
        level_info = self.user_manager.get_level_info(current_level)
        self.version_info = QLabel()
        self.update_version_info(current_level, level_info)
        
        self.version_info.setAlignment(Qt.AlignCenter)
        self.version_info.setFont(self.font_manager.get_font("Medium", 12))
        self.version_info.setObjectName("version_info")
        main_layout.addWidget(self.version_info)
        
        # 添加输入框标签
        input_label = QLabel("   ")
        input_label.setFont(self.font_manager.get_font("Regular", 12))
        input_label.setObjectName("input_label")
        main_layout.addWidget(input_label)
        
        # 添加输入框
        self.input_line_edit = QLineEdit()
        self.input_line_edit.setFont(self.font_manager.get_font("Regular", 12))
        if level_info and "max_number" in level_info:
            if level_info["max_number"] == float('inf'):
                max_num_display = "无限"
            else:
                max_num_display = f"{level_info['max_number']}"
            self.input_line_edit.setPlaceholderText(f"输入算式 (当前等级支持{max_num_display}以内)")
        else:
            self.input_line_edit.setPlaceholderText("输入算式")
        main_layout.addWidget(self.input_line_edit)
        
        # 添加计算按钮
        self.calculate_button = QPushButton("开始计算")
        self.calculate_button.clicked.connect(self.start_calculation)
        self.calculate_button.setMinimumHeight(40)
        self.calculate_button.setFont(self.font_manager.get_font("Medium", 14))
        self.calculate_button.setObjectName("calculate_button")
        main_layout.addWidget(self.calculate_button)
        
        # 添加示例
        example_label = QLabel("示例: 1+1, 3.14+2.5, 10-3, 7.5-2.3 (根据版本限制)")
        example_label.setAlignment(Qt.AlignCenter)
        example_label.setFont(self.font_manager.get_font("Light", 11))
        example_label.setObjectName("example_label")
        main_layout.addWidget(example_label)
        
        main_layout.addStretch()
        
        # 添加底部信息
        footer_layout = QHBoxLayout()
        
        # 检查到期时间
        expire_days = self.user_manager.get_expire_days()
        self.expire_info = QLabel()
        if expire_days is not None:
            self.expire_info.setText(f"会员剩余: {expire_days}天")
        else:
            self.expire_info.setText("")
        
        self.expire_info.setFont(self.font_manager.get_font("Regular", 11))
        self.expire_info.setObjectName("expire_info")
        footer_layout.addWidget(self.expire_info)
        
        footer_layout.addStretch()
        
        copyright_label = QLabel("© 2026 Intelligence Calculator")
        copyright_label.setFont(self.font_manager.get_font("Light", 10))
        copyright_label.setObjectName("copyright_label")
        footer_layout.addWidget(copyright_label)
        
        main_layout.addLayout(footer_layout)
    
    def update_vip_label_style(self, current_level):
        """更新VIP标签样式"""
        if current_level == "So Big":
            label_style = """
                QLabel {
                    background-color: #FFD700;
                    color: #000;
                    font-weight: bold;
                    border: 2px solid #FF6B00;
                    border-radius: 8px;
                    padding: 5px 20px;
                }
                QLabel:hover {
                    background-color: #FFED4E;
                }
            """
        elif current_level == "Ultra":
            label_style = """
                QLabel {
                    background-color: #9C27B0;
                    color: white;
                    font-weight: bold;
                    border: 2px solid #7B1FA2;
                    border-radius: 8px;
                    padding: 5px 20px;
                }
                QLabel:hover {
                    background-color: #AB47BC;
                }
            """
        elif current_level == "Max":
            label_style = """
                QLabel {
                    background-color: #2196F3;
                    color: white;
                    font-weight: bold;
                    border: 2px solid #1976D2;
                    border-radius: 8px;
                    padding: 5px 20px;
                }
                QLabel:hover {
                    background-color: #42A5F5;
                }
            """
        elif current_level == "Pro":
            label_style = """
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    font-weight: bold;
                    border: 2px solid #388E3C;
                    border-radius: 8px;
                    padding: 5px 20px;
                }
                QLabel:hover {
                    background-color: #66BB6A;
                }
            """
        else:  # Plus
            label_style = """
                QLabel {
                    background-color: #9E9E9E;
                    color: white;
                    font-weight: bold;
                    border: 2px solid #757575;
                    border-radius: 8px;
                    padding: 5px 20px;
                }
                QLabel:hover {
                    background-color: #BDBDBD;
                }
            """
        
        self.vip_label.setStyleSheet(label_style)
    
    def update_version_info(self, current_level, level_info=None):
        """更新版本信息"""
        if level_info is None:
            level_info = self.user_manager.get_level_info(current_level)
        
        if level_info:
            if level_info["max_number"] == float('inf'):
                max_num = "无限"
            else:
                max_num = f"{level_info['max_number']}"
            
            self.version_info.setText(f"当前版本: {current_level} | 计算范围: {max_num}以内")
        else:
            self.version_info.setText(f"当前版本: {current_level}")
    
    def on_level_changed(self, new_level):
        """等级变更回调"""
        # 更新VIP标签文本和样式
        self.vip_label.setText(f" {new_level} ")
        self.update_vip_label_style(new_level)
        
        # 更新版本信息
        self.update_version_info(new_level)
        
        # 更新输入框占位符
        level_info = self.user_manager.get_level_info(new_level)
        if level_info and "max_number" in level_info:
            if level_info["max_number"] == float('inf'):
                max_num_display = "无限"
            else:
                max_num_display = f"{level_info['max_number']}"
            self.input_line_edit.setPlaceholderText(f"输入算式 (当前版本支持{max_num_display}以内)")
        
        # 更新到期信息
        expire_days = self.user_manager.get_expire_days()
        if expire_days is not None:
            self.expire_info.setText(f"会员剩余: {expire_days}天")
        else:
            self.expire_info.setText("")
    
    def load_theme_icon(self):
        """加载主题图标"""
        try:
            # 检查picture文件夹是否存在
            if not os.path.exists("picture"):
                os.makedirs("picture")
                print("创建了picture文件夹")
            
            # 加载主题图标
            theme_path = "picture/theme.png"
            if os.path.exists(theme_path):
                theme_pixmap = QPixmap(theme_path)
                if not theme_pixmap.isNull():
                    # 缩放图片到合适大小
                    theme_pixmap = theme_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.theme_button.setIcon(QIcon(theme_pixmap))
                    self.theme_button.setIconSize(QSize(24, 24))
                else:
                    # 使用文字图标
                    self.theme_button.setText("🎨")
                    self.theme_button.setFont(QFont("Segoe UI Emoji", 16))
            else:
                # 使用文字图标
                self.theme_button.setText("🎨")
                self.theme_button.setFont(QFont("Segoe UI Emoji", 16))
        except Exception as e:
            print(f"加载主题图标失败: {e}")
            # 使用文字图标
            self.theme_button.setText("🎨")
            self.theme_button.setFont(QFont("Segoe UI Emoji", 16))
    
    def load_github_icon(self):
        """加载GitHub图标"""
        try:
            # 检查picture文件夹是否存在
            if not os.path.exists("picture"):
                os.makedirs("picture")
                print("创建了picture文件夹")
            
            # 加载GitHub图标
            github_path = "picture/github.png"
            if os.path.exists(github_path):
                github_pixmap = QPixmap(github_path)
                if not github_pixmap.isNull():
                    # 缩放图片到合适大小
                    github_pixmap = github_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.github_button.setIcon(QIcon(github_pixmap))
                    self.github_button.setIconSize(QSize(24, 24))
                else:
                    # 使用文字图标
                    self.github_button.setText("🐱")
                    self.github_button.setFont(QFont("Segoe UI Emoji", 16))
            else:
                # 使用文字图标
                self.github_button.setText("🐱")
                self.github_button.setFont(QFont("Segoe UI Emoji", 16))
        except Exception as e:
            print(f"加载GitHub图标失败: {e}")
            # 使用文字图标
            self.github_button.setText("🐱")
            self.github_button.setFont(QFont("Segoe UI Emoji", 16))
    
    def load_like_icon(self):
        """加载点赞图标"""
        try:
            # 检查picture文件夹是否存在
            if not os.path.exists("picture"):
                os.makedirs("picture")
                print("创建了picture文件夹")
            
            # 加载点赞图标
            like_path = "picture/like.png"
            if os.path.exists(like_path):
                like_pixmap = QPixmap(like_path)
                if not like_pixmap.isNull():
                    # 缩放图片到合适大小
                    like_pixmap = like_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.like_button.setIcon(QIcon(like_pixmap))
                    self.like_button.setIconSize(QSize(24, 24))
                else:
                    # 使用文字图标
                    self.like_button.setText("❤️")
                    self.like_button.setFont(QFont("Segoe UI Emoji", 16))
            else:
                # 使用文字图标
                self.like_button.setText("❤️")
                self.like_button.setFont(QFont("Segoe UI Emoji", 16))
        except Exception as e:
            print(f"加载点赞图标失败: {e}")
            # 使用文字图标
            self.like_button.setText("❤️")
            self.like_button.setFont(QFont("Segoe UI Emoji", 16))
    
    def open_sponsor_page(self):
        """打开赞助页面"""
        sponsor_dialog = SponsorDialog(self.font_manager, self)
        sponsor_dialog.exec()
    
    def apply_theme(self):
        """应用当前主题"""
        theme = self.theme_manager.get_current_theme()
        title_color = self.theme_manager.get_title_color()
        
        # 更新标题颜色
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet(f"color: {title_color};")
        
        # 设置窗口样式
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['window_bg']};
            }}
            QWidget {{
                background-color: {theme['window_bg']};
                color: {theme['text_color']};
            }}
            QLabel {{
                color: {theme['text_color']};
            }}
            QLabel#version_info {{
                color: #FF6B6B;
            }}
            QLabel#input_label {{
                color: {theme['text_color']};
            }}
            QLabel#example_label {{
                color: #666666;
            }}
            QLabel#expire_info {{
                color: {theme['text_color']};
            }}
            QLabel#copyright_label {{
                color: #999999;
            }}
            QLineEdit {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['border_color']};
                border-radius: 5px;
                padding: 8px;
                color: {theme['text_color']};
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {theme['button_hover']};
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
            }}
            QPushButton#calculate_button {{
                background-color: {theme['button_bg']};
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton#calculate_button:hover {{
                background-color: {theme['button_hover']};
            }}
            QTextEdit {{
                background-color: {theme['card_bg']};
                border: 1px solid {theme['border_color']};
                color: {theme['text_color']};
            }}
            QDialog {{
                background-color: {theme['window_bg']};
            }}
            
            /* 支付对话框样式 */
            QLabel#payment_title {{
                font-size: 20px;
                font-weight: bold;
                color: {title_color};
            }}
            QLabel#payment_price {{
                font-size: 18px;
                font-weight: bold;
                color: #FF6B6B;
            }}
            QLabel#payment_desc {{
                font-size: 14px;
                color: {theme['text_color']};
            }}
            QLabel#payment_platform_title {{
                font-weight: bold;
                font-size: 16px;
                color: {theme['text_color']};
            }}
            QLabel#payment_hint {{
                font-size: 12px;
                color: #999;
                font-style: italic;
            }}
            QPushButton#payment_button {{
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }}
            QPushButton#payment_button:enabled {{
                background-color: #4CAF50;
            }}
            QPushButton#payment_button:enabled:hover {{
                background-color: #45a049;
            }}
            
            /* 赞助对话框样式 */
            QLabel#sponsor_title {{
                font-size: 20px;
                font-weight: bold;
                color: {title_color};
            }}
            QLabel#sponsor_intro {{
                font-size: 14px;
                color: {theme['text_color']};
                font-style: italic;
            }}
            QLabel#sponsor_desc {{
                font-size: 14px;
                color: {theme['text_color']};
            }}
            QLabel#sponsor_platform_title {{
                font-weight: bold;
                font-size: 16px;
                color: {theme['text_color']};
            }}
            QPushButton#sponsor_button {{
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px;
            }}
            QPushButton#sponsor_button:enabled {{
                background-color: #4CAF50;
            }}
            QPushButton#sponsor_button:enabled:hover {{
                background-color: #45a049;
            }}
            
            /* VIP对话框样式 */
            QLabel#vip_title {{
                color: {title_color};
            }}
            QLabel#vip_status {{
                color: {theme['text_color']};
            }}
            QLabel#vip_note {{
                color: #FF6B6B;
                font-style: italic;
            }}
            
            /* 结果对话框样式 */
            QLabel#result_text {{
                color: #2E7D32;
            }}
            QLabel#result_info {{
                color: {theme['text_color']};
            }}
            QPushButton#result_sponsor_button {{
                background-color: {theme['button_bg']};
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
            }}
            QPushButton#result_sponsor_button:hover {{
                background-color: {theme['button_hover']};
            }}
            
            /* 主题对话框样式 */
            QLabel#theme_title {{
                color: {title_color};
            }}
            QLabel#theme_info {{
                color: {theme['text_color']};
            }}
            QLabel#theme_note {{
                color: #FF6B6B;
                font-style: italic;
            }}
            QPushButton#theme_close_button {{
                background-color: #9E9E9E;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton#theme_close_button:hover {{
                background-color: #757575;
            }}
        """)
    
    def on_vip_label_clicked(self, event):
        """VIP标签点击事件"""
        self.show_vip_dialog()
    
    def check_membership_status(self):
        """检查会员状态"""
        # 检查是否即将过期
        if self.user_manager.check_expire_soon():
            days_left = self.user_manager.get_expire_days()
            QMessageBox.warning(self, "会员即将过期", 
                f"您的会员还有{days_left}天即将过期，请及时续费以避免降级！")
        
        # 检查是否已过期
        current_level = self.user_manager.get_current_level()
        if current_level != "Plus":
            expire_days = self.user_manager.get_expire_days()
            if expire_days == 0:
                QMessageBox.warning(self, "会员已过期", 
                    "您的会员已过期，已自动降级为Plus版本！")
    
    def show_vip_dialog(self):
        """显示VIP充值对话框"""
        vip_dialog = VIPDialog(self.user_manager, self.font_manager, self)
        if vip_dialog.exec():
            # VIP对话框关闭后，UI会自动通过回调更新
            pass
    
    def show_theme_dialog(self):
        """显示主题选择对话框"""
        theme_dialog = ThemeDialog(self.user_manager, self.font_manager, self)
        if theme_dialog.exec():
            # 应用新主题
            self.apply_theme()
    
    def start_calculation(self):
        """开始计算"""
        expression = self.input_line_edit.text().strip()
        
        if not expression:
            QMessageBox.warning(self, "错误", "请输入算式")
            return
        
        # 检查表达式格式
        if '+' not in expression and '-' not in expression:
            QMessageBox.warning(self, "错误", "请输入有效的算式 (如: 1+1 或 5-3)")
            return
        
        # 禁用按钮防止重复点击
        self.calculate_button.setEnabled(False)
        self.calculate_button.setText("计算中...")
        
        try:
            # 创建计算过程对话框
            self.calc_dialog = CalculationDialog(self)
            self.calc_dialog.show()
            
            # 创建计算线程
            self.calc_thread = CalculationThread(expression, self.user_manager)
            self.calc_thread.output_signal.connect(self.calc_dialog.append_text)
            self.calc_thread.finished_signal.connect(self.show_result)
            self.calc_thread.error_signal.connect(self.on_calculation_error)
            self.calc_thread.finished.connect(self.enable_button)
            self.calc_thread.start()
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"启动计算失败:\n{str(e)}")
            self.enable_button()
    
    def on_calculation_error(self, error_message):
        """处理计算错误"""
        if hasattr(self, 'calc_dialog'):
            self.calc_dialog.show_error(error_message)
            # 延迟关闭对话框，让用户看到错误信息
            QTimer.singleShot(2000, self.calc_dialog.close)
        else:
            QMessageBox.warning(self, "计算错误", error_message)
        
        self.enable_button()
    
    def show_result(self, operator, operand1, operand2):
        """显示计算结果"""
        # 关闭计算过程对话框
        if hasattr(self, 'calc_dialog'):
            self.calc_dialog.close()
        
        # 计算表达式和结果
        if operator == '+':
            expression = f"{operand1} + {operand2}"
            result = float(operand1) + float(operand2)
        else:  # operator == '-'
            expression = f"{operand1} - {operand2}"
            result = float(operand1) - float(operand2)
        
        # 显示结果对话框
        result_dialog = ResultDialog(expression, result, self.font_manager, self)
        result_dialog.exec()
        
        # 发送Windows通知
        self.send_notification(expression, result)
    
    def enable_button(self):
        """启用计算按钮"""
        self.calculate_button.setEnabled(True)
        self.calculate_button.setText("开始计算")
    
    def send_notification(self, expression, result):
        """发送Windows通知"""
        if self.toaster:
            try:
                self.toaster.show_toast(
                    title="Intelligence Calculator",
                    msg=f"计算成功\n{expression} = {result}",
                    icon_path=None,
                    duration=5,
                    threaded=True
                )
            except:
                pass


def main():
    """主函数"""
    try:
        # 启用高DPI缩放
        if hasattr(Qt, 'AA_EnableHighDpiScaling'):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        
        if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication(sys.argv)
        
        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)
        print("如")


if __name__ == "__main__":
    main()
    2026
    
