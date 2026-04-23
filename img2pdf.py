import os
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def create_payment_pdf(input_folder, output_pdf, images_per_page=1):
    # --- 中文字体处理 ---
    # 尝试加载 Windows 自带的微软雅黑字体，解决文件名中文乱码问题
    font_path = "C:/Windows/Fonts/msyh.ttc"
    font_name = "MSYH"
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_path))
    except:
        font_name = "Helvetica"  # 如果找不到字体则回退
        print("警告：未找到微软雅黑字体，中文文件名可能无法正常显示。")

    # --- 获取图片 ---
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(valid_extensions)]
    files.sort()  # 按文件名排序

    if not files:
        print(f"在路径 {input_folder} 下未找到图片文件！")
        return

    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4

    # 边距设置
    margin = 40
    text_height = 30  # 留给文件名的垂直空间

    for i in range(0, len(files), images_per_page):
        batch = files[i: i + images_per_page]
        # 计算每一份（图+文）可用的总高度
        available_total_h = (height - (2 * margin)) / images_per_page

        for index, filename in enumerate(batch):
            img_path = os.path.join(input_folder, filename)
            display_name = os.path.splitext(filename)[0]  # 去掉后缀

            with Image.open(img_path) as img:
                img_w, img_h = img.size
                aspect = img_h / float(img_w)

            # 初始计算：宽度撑满页面减去边距
            draw_width = width - (2 * margin)
            draw_height = draw_width * aspect

            # 限制图片最大高度，不能超过分配区域减去文字高度
            max_img_h = available_total_h - text_height
            if draw_height > max_img_h:
                draw_height = max_img_h
                draw_width = draw_height / aspect

            # 计算坐标 (reportlab 坐标系原点在左下角)
            # page_pos 0 是该页的第一张，1 是第二张
            page_pos = index
            # 这里的计算逻辑是从上往下排
            y_base = height - margin - ((page_pos + 1) * available_total_h)
            y_img = y_base + text_height  # 图片底部在文字上方
            x_img = (width - draw_width) / 2

            # 画图
            c.drawImage(img_path, x_img, y_img, width=draw_width, height=draw_height)

            # 画文字 (居中显示在图片下方)
            c.setFont(font_name, 10)
            c.drawCentredString(width / 2, y_base + (text_height / 2) - 5, display_name)

        c.showPage()  # 换页

    c.save()
    print(f"成功！PDF 已保存在桌面: {output_pdf}")


# --- 执行 ---
# 文件夹路径
my_path = r'./images'  # 换成你自己的目标文件夹路径
# 输出路径（也放在桌面）
output_path = r'./支付记录排版.pdf'  # 换成你自己的保存路径

# 如果想一页一张，改 images_per_page=1
create_payment_pdf(my_path, output_path, images_per_page=2)