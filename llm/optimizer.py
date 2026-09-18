from typing import List, Dict


class TokenOptimizer:

    def __init__(
        self,
        max_length=4000
    ):
        """
        Token 优化器。

        max_length:
            单条消息允许的最大字符长度。
        """

        self.max_length = max_length

    def estimate_tokens(self, text: str) -> int:
        """
        粗略估算 Token 数量。

        这里只用于统计和控制上下文，
        不是精确 Tokenizer。
        """

        if not text:
            return 0

        return max(
            1,
            len(text) // 2
        )

    def truncate(
        self,
        text: str,
        max_chars: int
    ) -> str:
        """
        截断过长文本。
        """

        if len(text) <= max_chars:
            return text

        return (
            text[:max_chars]
            + "\n\n"
            + "[内容已截断]"
        )

    def optimize_messages(
        self,
        messages: List[Dict]
    ):
        """
        优化 Chat Messages。

        返回:
            (
                optimized_messages,
                estimated_tokens
            )
        """

        optimized_messages = []

        total_tokens = 0

        for message in messages:

            content = message.get(
                "content",
                ""
            )

            # 防止 content 不是字符串
            if not isinstance(
                content,
                str
            ):
                content = str(content)

            optimized_content = (
                self.truncate(
                    content,
                    self.max_length
                )
            )

            total_tokens += (
                self.estimate_tokens(
                    optimized_content
                )
            )

            optimized_messages.append(
                {
                    "role": message.get(
                        "role",
                        "user"
                    ),
                    "content":
                        optimized_content
                }
            )

        return (
            optimized_messages,
            total_tokens
        )