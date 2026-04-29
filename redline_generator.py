from redlines import Redlines

class RedlineGenerator:
    @staticmethod
    def generate_markdown_redline(original_text, revised_text):
        """
        对比原文和修改后的文本，生成带删除线和下划线的红线 Markdown 文本
        """
        tester = Redlines(original_text, revised_text, markdown_style="none")
        return tester.output_markdown