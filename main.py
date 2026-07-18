from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.message_components import Image, Plain
import random
from pathlib import Path
from PIL import Image as PILImage
from typing import List, Set, Tuple, Dict, Optional
import re
import time


@register("chinitsu_training", "EternityTQ", "清一色听牌训练插件", "1.0.0")
class ChinitsuTrainingPlugin(Star):
    """清一色听牌训练插件"""

    def __init__(self, context: Context):
        super().__init__(context)
        # 存储群游戏状态：group_id -> GroupGameState
        self.group_games: Dict[str, 'GroupGameState'] = {}
        # 存储用户连胜记录：user_id -> win_streak
        self.win_streaks: Dict[str, int] = {}
        # 麻将牌图片路径
        self.tile_path = Path(__file__).parent / "Regular"

    async def initialize(self):
        """初始化插件"""
        logger.info("清一色听牌训练插件已加载")

    def generate_hand(self) -> Tuple[List[int], str]:
        """
        生成一副13张的清一色待听牌型
        返回: (手牌列表, 花色) 其中手牌是1-9的数字列表，花色是'm'/'s'/'p'
        """
        suits = ['m', 's', 'p']  # 万、索、饼
        suit = random.choice(suits)

        max_attempts = 1000
        for _ in range(max_attempts):
            # 随机生成13张牌（可能重复，但总数不超过每种4张）
            hand = []
            tile_count = [0] * 10  # index 0 unused, 1-9 for tiles

            for _ in range(13):
                tile = random.randint(1, 9)
                if tile_count[tile] < 4:
                    hand.append(tile)
                    tile_count[tile] += 1

            if len(hand) != 13:
                continue

            hand.sort()

            # 检查是否听牌
            waiting_tiles = self.check_tenpai(hand)
            if waiting_tiles:
                return hand, suit

        # 如果生成失败，返回一个保证听牌的牌型
        # 例如：1112345678999 听 147
        return [1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9], suit

    def check_tenpai(self, hand: List[int]) -> Set[int]:
        """
        检查13张牌听什么牌
        正确逻辑：从13张牌加入第14张后能和牌
        hand: 13张牌的列表
        返回: 听牌的集合（1-9）
        """
        if len(hand) != 13:
            return set()

        waiting = set()

        for tile in range(1, 10):
            # 检查是否还有这张牌可用（不超过4张）
            tile_count_in_hand = hand.count(tile)
            if tile_count_in_hand >= 4:
                continue

            # 尝试加入这张牌
            test_hand = hand + [tile]
            if self.is_winning_hand(test_hand):
                waiting.add(tile)

        return waiting

    def is_winning_hand(self, hand: List[int]) -> bool:
        """
        判断14张牌是否能和牌
        标准日本麻将：4组面子（顺子/刻子）+ 1对雀头
        """
        if len(hand) != 14:
            return False

        tile_count = [0] * 10
        for tile in hand:
            tile_count[tile] += 1

        # 尝试每种牌作为雀头（对子）
        for pair in range(1, 10):
            if tile_count[pair] >= 2:
                # 移除雀头
                remaining = tile_count.copy()
                remaining[pair] -= 2

                # 检查剩余12张牌是否都能组成面子
                if self.can_form_melds(remaining):
                    return True

        return False

    def can_form_melds(self, tile_count: List[int]) -> bool:
        """
        递归检查剩余的牌是否都能组成面子（顺子或刻子）
        tile_count: 每种牌的数量数组
        """
        # 找到第一个非零的牌
        first_tile = -1
        for i in range(1, 10):
            if tile_count[i] > 0:
                first_tile = i
                break

        # 如果没有牌了，说明所有牌都组成了面子
        if first_tile == -1:
            return True

        # 尝试组成刻子（三张相同）
        if tile_count[first_tile] >= 3:
            new_count = tile_count.copy()
            new_count[first_tile] -= 3
            if self.can_form_melds(new_count):
                return True

        # 尝试组成顺子（三张连续）
        if first_tile <= 7 and tile_count[first_tile] > 0 and tile_count[first_tile + 1] > 0 and tile_count[first_tile + 2] > 0:
            new_count = tile_count.copy()
            new_count[first_tile] -= 1
            new_count[first_tile + 1] -= 1
            new_count[first_tile + 2] -= 1
            if self.can_form_melds(new_count):
                return True

        # 如果两种方式都不行，返回False
        return False

    def create_hand_image(self, hand: List[int], suit: str) -> Path:
        """
        生成手牌图片
        hand: 手牌列表
        suit: 'm'/'s'/'p'
        返回: 生成的图片路径
        """
        suit_map = {'m': 'Man', 's': 'Sou', 'p': 'Pin'}
        suit_prefix = suit_map[suit]

        # 加载底牌
        front_img = PILImage.open(self.tile_path / "Front.png")
        tile_width, tile_height = front_img.size

        # 创建新图片：13张牌横向排列，间距2px
        spacing = 2
        total_width = tile_width * 13 + spacing * 12
        total_height = tile_height

        result_img = PILImage.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

        # 逐张粘贴牌
        for idx, tile_num in enumerate(hand):
            # 加载花色图片
            tile_img = PILImage.open(self.tile_path / f"{suit_prefix}{tile_num}.png")

            # 将花色叠加到底牌上
            composite = front_img.copy()
            composite.paste(tile_img, (0, 0), tile_img if tile_img.mode == 'RGBA' else None)

            # 粘贴到结果图片
            x_pos = idx * (tile_width + spacing)
            result_img.paste(composite, (x_pos, 0))

        # 保存临时图片
        output_path = self.tile_path.parent / f"temp_hand_{random.randint(1000, 9999)}.png"
        result_img.save(output_path)

        return output_path

    @filter.command("清一色")
    async def chinitsu_command(self, event: AstrMessageEvent):
        """清一色听牌训练"""
        group_id = event.get_group_id() or event.get_sender_id()  # 群聊用群ID，私聊用用户ID
        user_id = event.get_sender_id()
        user_name = event.get_sender_name()
        message_str = event.message_str.strip()

        # 解析命令参数
        parts = message_str.split()

        # 检查是否是停止命令
        if len(parts) >= 2 and parts[1].lower() == 'stop':
            if group_id in self.group_games:
                del self.group_games[group_id]
                yield event.plain_result("游戏已停止。")
            else:
                yield event.plain_result("当前没有进行中的游戏。")
            return

        # 如果是作答
        if len(parts) >= 2 and parts[1]:
            answer = parts[1].lower()

            # 检查是否有正在进行的游戏
            if group_id not in self.group_games:
                yield event.plain_result(f"@{user_name} 当前没有游戏，请先发送 /清一色 开始。")
                return

            game_state = self.group_games[group_id]

            # 解析用户答案
            user_tiles = self.parse_answer(answer, game_state.suit)

            if user_tiles is None:
                yield event.plain_result(f"@{user_name} 答案格式错误。请使用格式如：/清一色 1m2m")
                return

            # 判断答案是否正确
            correct_tiles = game_state.waiting_tiles

            if user_tiles == correct_tiles:
                # 答对了
                self.win_streaks[user_id] = self.win_streaks.get(user_id, 0) + 1
                streak = self.win_streaks[user_id]

                yield event.plain_result(f"@{user_name} 正确！连胜：{streak}")

                try:
                    # 生成下一题
                    logger.info("生成下一题...")
                    hand, suit = self.generate_hand()
                    waiting_tiles = self.check_tenpai(hand)

                    # 生成图片
                    img_path = self.create_hand_image(hand, suit)

                    # 更新游戏状态
                    self.group_games[group_id] = GroupGameState(hand, suit, waiting_tiles)

                    # 发送下一题
                    suit_name = {'m': '万', 's': '索', 'p': '饼'}[suit]

                    yield event.chain_result([
                        Image.fromFileSystem(str(img_path)),
                        Plain(f"\n花色：{suit_name}\n请回答听哪些牌，格式：/清一色 1m2m（数字在前，花色在后，m=万/s=索/p=饼）\n发送 /清一色 stop 结束游戏")
                    ])

                    # 删除临时图片
                    try:
                        img_path.unlink()
                    except Exception as e:
                        logger.warning(f"删除临时图片失败: {e}")

                except Exception as e:
                    logger.error(f"生成下一题时出错: {e}", exc_info=True)
                    yield event.plain_result(f"生成下一题时出错，请重新开始游戏。")
                    if group_id in self.group_games:
                        del self.group_games[group_id]
            else:
                # 答错了
                game_state.wrong_attempts += 1
                game_state.consecutive_errors[user_id] = game_state.consecutive_errors.get(user_id, 0) + 1
                game_state.last_answer_time = time.time()

                # 检查是否需要显示答案并继续
                if game_state.consecutive_errors[user_id] >= 5:
                    # 该用户连续错误5次，显示答案并继续
                    correct_answer = ''.join([f"{t}{game_state.suit}" for t in sorted(correct_tiles)])
                    yield event.plain_result(
                        f"@{user_name} 错误！已连续错误5次。\n正确答案：{correct_answer}\n\n生成下一题..."
                    )

                    # 重置该用户的连续错误
                    game_state.consecutive_errors[user_id] = 0

                    try:
                        # 生成下一题
                        hand, suit = self.generate_hand()
                        waiting_tiles = self.check_tenpai(hand)

                        # 生成图片
                        img_path = self.create_hand_image(hand, suit)

                        # 更新游戏状态
                        self.group_games[group_id] = GroupGameState(hand, suit, waiting_tiles)

                        # 发送下一题
                        suit_name = {'m': '万', 's': '索', 'p': '饼'}[suit]

                        yield event.chain_result([
                            Image.fromFileSystem(str(img_path)),
                            Plain(f"\n花色：{suit_name}\n请回答听哪些牌，格式：/清一色 1m2m\n发送 /清一色 stop 结束游戏")
                        ])

                        # 删除临时图片
                        try:
                            img_path.unlink()
                        except Exception as e:
                            logger.warning(f"删除临时图片失败: {e}")

                    except Exception as e:
                        logger.error(f"生成下一题时出错: {e}", exc_info=True)
                        yield event.plain_result(f"生成下一题时出错，请重新开始游戏。")
                        if group_id in self.group_games:
                            del self.group_games[group_id]
                else:
                    # 仅提示错误，不显示答案
                    yield event.plain_result(f"@{user_name} 错误！")

            return

        # 开始新游戏或显示超时答案
        if group_id in self.group_games:
            game_state = self.group_games[group_id]
            time_elapsed = time.time() - game_state.last_answer_time

            # 检查是否超时（5分钟 = 300秒）
            if time_elapsed >= 300:
                correct_answer = ''.join([f"{t}{game_state.suit}" for t in sorted(game_state.waiting_tiles)])
                yield event.plain_result(f"上一题超时无人作答。\n正确答案：{correct_answer}\n\n游戏已停止。请重新发送 /清一色 开始新游戏。")
                del self.group_games[group_id]
                return
            else:
                yield event.plain_result("当前已有游戏进行中，请作答或发送 /清一色 stop 结束。")
                return

        # 开始新游戏
        try:
            logger.info("开始生成新游戏...")
            hand, suit = self.generate_hand()
            waiting_tiles = self.check_tenpai(hand)
            logger.info(f"生成手牌: {hand}, 花色: {suit}, 听牌: {waiting_tiles}")

            # 生成图片
            img_path = self.create_hand_image(hand, suit)
            logger.info(f"图片已生成: {img_path}")

            # 保存游戏状态
            self.group_games[group_id] = GroupGameState(hand, suit, waiting_tiles)

            # 发送题目
            suit_name = {'m': '万', 's': '索', 'p': '饼'}[suit]
            logger.info(f"准备发送题目，花色: {suit_name}")

            yield event.chain_result([
                Image.fromFileSystem(str(img_path)),
                Plain(f"\n花色：{suit_name}\n请回答听哪些牌，格式：/清一色 1m2m（数字在前，花色在后，m=万/s=索/p=饼）\n发送 /清一色 stop 结束游戏")
            ])

            logger.info("题目已发送")

            # 删除临时图片
            try:
                img_path.unlink()
                logger.info("临时图片已删除")
            except Exception as e:
                logger.warning(f"删除临时图片失败: {e}")

        except Exception as e:
            logger.error(f"生成游戏时出错: {e}", exc_info=True)
            yield event.plain_result(f"生成游戏时出错: {str(e)}")
            # 清理失败的游戏状态
            if group_id in self.group_games:
                del self.group_games[group_id]

    def parse_answer(self, answer: str, expected_suit: str) -> Optional[Set[int]]:
        """
        解析用户答案
        answer: 如 "1m2m" 或 "1m"
        expected_suit: 期望的花色
        返回: 牌的集合，如果格式错误返回None
        """
        # 匹配格式：数字+花色，可以有多组
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

    async def terminate(self):
        """插件卸载"""
        logger.info("清一色听牌训练插件已卸载")


class GroupGameState:
    """群游戏状态"""
    def __init__(self, hand: List[int], suit: str, waiting_tiles: Set[int]):
        self.hand = hand
        self.suit = suit
        self.waiting_tiles = waiting_tiles
        self.wrong_attempts = 0
        self.consecutive_errors: Dict[str, int] = {}  # user_id -> consecutive_error_count
        self.last_answer_time = time.time()
