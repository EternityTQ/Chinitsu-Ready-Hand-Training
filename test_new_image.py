"""测试新的图片生成效果（缩小花色、增大间距）"""
from pathlib import Path
from PIL import Image as PILImage

def test_new_image_generation():
    """测试新的图片生成效果"""
    print("测试新的图片生成效果...")
    print("- 花色缩小到 70%")
    print("- 花色居中显示")
    print("- 牌之间间距增大到 10px\n")

    tile_path = Path(__file__).parent / "Regular"

    # 测试手牌
    hand = [1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9]
    suit = 'm'

    suit_map = {'m': 'Man', 's': 'Sou', 'p': 'Pin'}
    suit_prefix = suit_map[suit]

    print(f"手牌: {hand}")
    print(f"花色: {suit} ({suit_prefix})\n")

    try:
        # 加载底牌
        front_img = PILImage.open(tile_path / "Front.png")
        print(f"✓ 底牌加载成功: {front_img.size}")

        tile_width, tile_height = front_img.size

        # 创建新图片：间距 10px
        spacing = 10
        total_width = tile_width * 13 + spacing * 12
        total_height = tile_height

        result_img = PILImage.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

        # 逐张粘贴牌
        for idx, tile_num in enumerate(hand):
            tile_img = PILImage.open(tile_path / f"{suit_prefix}{tile_num}.png")

            # 缩小花色图片并居中
            scale_factor = 0.7
            new_width = int(tile_img.width * scale_factor)
            new_height = int(tile_img.height * scale_factor)
            tile_img_resized = tile_img.resize((new_width, new_height), PILImage.LANCZOS)

            # 计算居中位置
            x_offset = (tile_width - new_width) // 2
            y_offset = (tile_height - new_height) // 2

            # 将花色叠加到底牌上
            composite = front_img.copy()
            composite.paste(tile_img_resized, (x_offset, y_offset), tile_img_resized if tile_img_resized.mode == 'RGBA' else None)

            # 粘贴到结果图片
            x_pos = idx * (tile_width + spacing)
            result_img.paste(composite, (x_pos, 0))

        # 保存图片
        output_path = Path(__file__).parent / "test_hand_new.png"
        result_img.save(output_path)

        print(f"\n✓ 图片生成成功: {output_path}")
        print(f"  尺寸: {result_img.size}")
        print(f"  牌宽度: {tile_width}px")
        print(f"  牌间距: {spacing}px")
        print(f"  花色缩放: {scale_factor * 100}%")
        print(f"  文件大小: {output_path.stat().st_size} bytes")

        # 对比旧图片
        old_img_path = Path(__file__).parent / "test_hand.png"
        if old_img_path.exists():
            old_img = PILImage.open(old_img_path)
            print(f"\n对比:")
            print(f"  旧图片尺寸: {old_img.size}")
            print(f"  新图片尺寸: {result_img.size}")
            print(f"  宽度增加: {result_img.size[0] - old_img.size[0]}px")

        return True

    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_image_generation()
    if success:
        print("\n✅ 新图片生成功能正常！")
        print("\n请打开 test_hand_new.png 查看效果：")
        print("- 花色应该更小且居中")
        print("- 牌之间的间距应该更大")
    else:
        print("\n❌ 图片生成功能异常，请检查错误信息。")
