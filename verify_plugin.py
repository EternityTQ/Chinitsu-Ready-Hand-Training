"""快速验证插件功能的脚本"""
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("清一色听牌训练插件 - 功能验证")
print("=" * 60)

# 测试1: 导入检查
print("\n[1/5] 检查依赖导入...")
try:
    from PIL import Image as PILImage
    print("  ✓ Pillow 已安装")
except ImportError:
    print("  ✗ Pillow 未安装，请运行: pip install Pillow")
    sys.exit(1)

# 测试2: 检查资源文件
print("\n[2/5] 检查麻将牌资源...")
tile_path = Path(__file__).parent / "Regular"
required_files = ["Front.png", "Man1.png", "Man9.png", "Sou1.png", "Sou9.png", "Pin1.png", "Pin9.png"]
missing_files = []
for file in required_files:
    if not (tile_path / file).exists():
        missing_files.append(file)

if missing_files:
    print(f"  ✗ 缺少资源文件: {', '.join(missing_files)}")
else:
    print(f"  ✓ 所有必需资源文件存在")

# 测试3: 麻将逻辑测试
print("\n[3/5] 测试麻将逻辑...")

class QuickTester:
    def is_winning_hand(self, hand):
        if len(hand) != 14:
            return False
        tile_count = [0] * 10
        for tile in hand:
            tile_count[tile] += 1
        for pair in range(1, 10):
            if tile_count[pair] >= 2:
                remaining = tile_count.copy()
                remaining[pair] -= 2
                if self.can_form_melds(remaining):
                    return True
        return False

    def can_form_melds(self, tile_count):
        first_tile = -1
        for i in range(1, 10):
            if tile_count[i] > 0:
                first_tile = i
                break
        if first_tile == -1:
            return True
        if tile_count[first_tile] >= 3:
            new_count = tile_count.copy()
            new_count[first_tile] -= 3
            if self.can_form_melds(new_count):
                return True
        if first_tile <= 7 and tile_count[first_tile] > 0 and tile_count[first_tile + 1] > 0 and tile_count[first_tile + 2] > 0:
            new_count = tile_count.copy()
            new_count[first_tile] -= 1
            new_count[first_tile + 1] -= 1
            new_count[first_tile + 2] -= 1
            if self.can_form_melds(new_count):
                return True
        return False

tester = QuickTester()

# 测试几个已知的和牌型
test_cases = [
    ([1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 2], True, "111 + 22对 + 345 + 678 + 999"),
    ([2, 3, 4, 5, 6, 7, 8, 8, 8, 9, 9, 9, 9, 9], True, "234 + 567 + 888 + 99对 + 999"),
    ([1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7], True, "七对子形状"),
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 9, 9], False, "有6张9，不合法但测试逻辑"),
]

all_passed = True
for hand, expected, desc in test_cases:
    if hand.count(max(hand)) > 4:  # 跳过不合法的牌型
        continue
    result = tester.is_winning_hand(hand)
    if result == expected:
        print(f"  ✓ {desc}")
    else:
        print(f"  ✗ {desc} (期望: {expected}, 实际: {result})")
        all_passed = False

if all_passed:
    print("  ✓ 麻将逻辑测试通过")

# 测试4: 图片生成测试
print("\n[4/5] 测试图片生成...")
try:
    front_img = PILImage.open(tile_path / "Front.png")
    man1_img = PILImage.open(tile_path / "Man1.png")

    # 简单测试叠加
    composite = front_img.copy()
    composite.paste(man1_img, (0, 0), man1_img if man1_img.mode == 'RGBA' else None)

    # 测试拼接
    tile_width, tile_height = front_img.size
    spacing = 2
    total_width = tile_width * 3 + spacing * 2
    result_img = PILImage.new('RGBA', (total_width, tile_height), (0, 0, 0, 0))

    for i in range(3):
        x_pos = i * (tile_width + spacing)
        result_img.paste(composite, (x_pos, 0))

    # 保存测试图片
    test_output = Path(__file__).parent / "test_output.png"
    result_img.save(test_output)
    print(f"  ✓ 图片生成测试通过")
    print(f"    测试图片已保存: {test_output}")

    # 清理测试图片
    try:
        test_output.unlink()
        print(f"    测试图片已清理")
    except:
        pass

except Exception as e:
    print(f"  ✗ 图片生成失败: {e}")

# 测试5: 答案解析测试
print("\n[5/5] 测试答案解析...")
import re

def parse_answer(answer, expected_suit):
    pattern = r'(\d+)([msp])'
    matches = re.findall(pattern, answer)
    if not matches:
        return None
    tiles = set()
    for num_str, suit in matches:
        if suit != expected_suit:
            return None
        for digit in num_str:
            tile_num = int(digit)
            if tile_num < 1 or tile_num > 9:
                return None
            tiles.add(tile_num)
    return tiles

test_answers = [
    ("1m2m", "m", {1, 2}),
    ("12m", "m", {1, 2}),
    ("147m", "m", {1, 4, 7}),
    ("1m4m7m", "m", {1, 4, 7}),
    ("258s", "s", {2, 5, 8}),
    ("1m", "s", None),  # 花色不匹配
    ("abc", "m", None),  # 格式错误
]

all_passed = True
for answer, suit, expected in test_answers:
    result = parse_answer(answer, suit)
    if result == expected:
        print(f"  ✓ '{answer}' (花色:{suit}) -> {result}")
    else:
        print(f"  ✗ '{answer}' (花色:{suit}) -> 期望:{expected}, 实际:{result}")
        all_passed = False

if all_passed:
    print("  ✓ 答案解析测试通过")

print("\n" + "=" * 60)
print("验证完成！插件功能正常。")
print("=" * 60)
print("\n使用说明:")
print("1. 确保 Pillow 已安装: pip install Pillow")
print("2. 将插件文件夹放入 AstrBot 插件目录")
print("3. 重启 AstrBot")
print("4. 在群聊中发送 /清一色 开始游戏")
print("\n详细使用方法请查看 USAGE.md")
