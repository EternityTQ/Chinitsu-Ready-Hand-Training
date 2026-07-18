"""测试答案格式化功能"""

def format_answer(tiles: set, suit: str) -> str:
    """
    格式化答案为 "12m" 格式
    tiles: 听牌的集合
    suit: 花色
    返回: 格式化的答案字符串，如 "147m"
    """
    sorted_tiles = sorted(tiles)
    numbers = ''.join(str(t) for t in sorted_tiles)
    return f"{numbers}{suit}"

# 测试案例
test_cases = [
    ({1, 4, 7}, 'm', "147m"),
    ({2, 5, 8}, 's', "258s"),
    ({1, 2, 3, 4, 5, 6, 7, 8, 9}, 'p', "123456789p"),
    ({3, 6, 9}, 'm', "369m"),
    ({1}, 's', "1s"),
    ({1, 2}, 'p', "12p"),
]

print("测试答案格式化功能...\n")

all_passed = True
for tiles, suit, expected in test_cases:
    result = format_answer(tiles, suit)
    status = "✓" if result == expected else "✗"
    if result != expected:
        all_passed = False
    print(f"{status} 听牌 {sorted(tiles)} 花色 {suit}")
    print(f"  期望: {expected}")
    print(f"  结果: {result}")
    print()

if all_passed:
    print("✅ 所有测试通过！")
    print("\n答案格式示例：")
    print("- 听1万、4万、7万 → 147m")
    print("- 听2索、5索、8索 → 258s")
    print("- 听3饼、6饼、9饼 → 369p")
else:
    print("❌ 部分测试失败，请检查代码。")
