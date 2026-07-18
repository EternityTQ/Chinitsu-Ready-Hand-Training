"""测试图片生成功能"""
from pathlib import Path
from PIL import Image as PILImage
import random

def test_image_generation():
    """测试图片生成"""
    print("测试图片生成功能...")

    tile_path = Path(__file__).parent / "Regular"

    # 测试手牌
    hand = [1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9]
    suit = 'm'

    suit_map = {'m': 'Man', 's': 'Sou', 'p': 'Pin'}
    suit_prefix = suit_map[suit]

    print(f"手牌: {hand}")
    print(f"花色: {suit} ({suit_prefix})")

    try:
        # 加载底牌
        front_img = PILImage.open(tile_path / "Front.png")
        print(f"✓ 底牌加载成功: {front_img.size}")

        tile_width, tile_height = front_img.size

        # 创建新图片
        spacing = 2
        total_width = tile_width * 13 + spacing * 12
        total_height = tile_height

        result_img = PILImage.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

        # 逐张粘贴牌
        for idx, tile_num in enumerate(hand):
            tile_img = PILImage.open(tile_path / f"{suit_prefix}{tile_num}.png")

            # 将花色叠加到底牌上
            composite = front_img.copy()
            composite.paste(tile_img, (0, 0), tile_img if tile_img.mode == 'RGBA' else None)

            # 粘贴到结果图片
            x_pos = idx * (tile_width + spacing)
            result_img.paste(composite, (x_pos, 0))

        # 保存图片
        output_path = Path(__file__).parent / "test_hand.png"
        result_img.save(output_path)

        print(f"✓ 图片生成成功: {output_path}")
        print(f"  尺寸: {result_img.size}")
        print(f"  文件大小: {output_path.stat().st_size} bytes")

        # 检查文件是否可读
        test_read = PILImage.open(output_path)
        print(f"✓ 图片可读取: {test_read.size}")

        return True

    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_image_generation()
    if success:
        print("\n✅ 图片生成功能正常！")
    else:
        print("\n❌ 图片生成功能异常，请检查错误信息。")
