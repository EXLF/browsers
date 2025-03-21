from PIL import Image
import os

def convert_to_ico():
    """将PNG转换为ICO格式"""
    input_path = os.path.join('chrome_manager', 'resources', 'logo.png')
    output_path = os.path.join('chrome_manager', 'resources', 'logo.ico')
    
    if not os.path.exists(input_path):
        print(f"错误：找不到源文件 {input_path}")
        return
    
    try:
        # 打开PNG图像
        img = Image.open(input_path)
        
        # 转换为RGBA模式（如果不是的话）
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 创建不同尺寸的图标
        sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
        img.save(output_path, format='ICO', sizes=sizes)
        
        print(f"成功：图标已保存到 {output_path}")
    except Exception as e:
        print(f"错误：转换失败 - {str(e)}")

if __name__ == '__main__':
    convert_to_ico() 