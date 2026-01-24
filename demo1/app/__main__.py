"""
应用主入口
"""
import asyncio
import sys
import os

# 设置 Windows 控制台为 UTF-8 编码
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from app import TopicStrategyWorkflow


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🎯 选题策略生成器 (Topic Strategy Generator)        ║
║                                                              ║
║              基于 AutoGen 的多智能体协作系统                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def get_user_input() -> str:
    """获取用户输入（单行输入）"""
    print("\n请描述您的业务场景（例如：B2B SaaS出海、IVD产品、电商获客等）：")
    print("=" * 80)

    user_input = input("> ").strip()

    if not user_input:
        print("\n❌ 错误：输入不能为空！")
        sys.exit(1)

    return user_input


async def main():
    """主函数"""
    try:
        # 打印欢迎信息
        print_banner()

        # 创建工作流
        workflow = TopicStrategyWorkflow()

        # 显示智能体信息
        workflow.print_agent_info()

        # 获取用户输入
        user_input = get_user_input()

        # 运行工作流
        await workflow.run(user_input)

        print("\n✨ 感谢使用选题策略生成器！\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误：{str(e)}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
