#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频播放器调度工具 (Video Player Launcher)
功能模态：
1. 不同视频 + 自主选择播放器（批量视频启动）
2. 相同视频 + 不同播放器（多播放器同屏对比测试）
"""

import os
import sys
import subprocess
from pathlib import Path

# ================================
# 播放器配置区域
# 格式: "编号": {"name": "播放器名称", "path": r"可执行文件绝对路径"}
# ================================
PLAYERS = {
    "1": {
        "name": "MPC-HC",
        "path": r"C:\Program Files (x86)\K-Lite Codec Pack\MPC-HC64\mpc-hc64_nvo.exe"
    },
    "2": {
        "name": "mpv",
        "path": r"D:\Date\Player\mpv\mpv.exe"
    },
    # 如有其他播放器，取消下方注释并修改对应路径即可：
    # "3": {
    #     "name": "PotPlayer",
    #     "path": r"C:\Program Files\DAUM\PotPlayer\PotPlayer64.exe"
    # },
    # "4": {
    #     "name": "VLC",
    #     "path": r"C:\Program Files\VideoLAN\VLC\vlc.exe"
    # },
}

def clean_path(raw_path: str) -> str:
    """全面清洗路径文本，去除外层包裹的各种单双引号和多余空格"""
    if not raw_path:
        return ""
    p = raw_path.strip()
    while (p.startswith('"') and p.endswith('"')) or (p.startswith("'") and p.endswith("'")):
        p = p[1:-1].strip()
    return p

def show_players_config():
    """查看当前配置的所有播放器可用性状态"""
    print("\n" + "=" * 55)
    print(" 🛠️  当前播放器挂载状态")
    print("=" * 55)
    for key, player in PLAYERS.items():
        exists = os.path.isfile(player["path"])
        status = "🟢 可用" if exists else "🔴 路径不存在"
        print(f"[{key}] {player['name']:<12} {status}")
        print(f"    路径: {player['path']}")
    print("-" * 55)
    print("提示：若需新增或更改播放器，可直接修改脚本顶部的 PLAYERS 字典。")
    print("=" * 55)

def choose_single_player():
    """交互选择单个播放器"""
    while True:
        print("\n--- 可选播放器列表 ---")
        for key, player in PLAYERS.items():
            exists = os.path.isfile(player["path"])
            status = "✓" if exists else "✗ (路径无效)"
            print(f"  [{key}] {player['name']} {status}")
        print("  [0] 返回主菜单")
        
        choice = input("\n请选择播放器序号: ").strip()
        if choice == "0":
            return None, None
        if choice in PLAYERS:
            target = PLAYERS[choice]
            if os.path.isfile(target["path"]):
                return target["path"], target["name"]
            print(f"\n❌ 该播放器可执行文件不存在: {target['path']}")
        else:
            print("\n❌ 无效选项，请重新输入。")

def get_single_video_file() -> str:
    """获取并校验单个视频文件路径"""
    print("\n请提供目标视频文件：")
    print("💡 提示：可直接拖拽视频文件到此窗口，然后按回车")
    while True:
        raw_in = input("视频路径: ").strip()
        if not raw_in:
            continue
        cleaned = clean_path(raw_in)
        if os.path.isfile(cleaned):
            return cleaned
        print(f"❌ 目标文件不存在或不是有效文件: {cleaned}")

def parse_multi_paths(user_input: str) -> list:
    """解析单次或批量输入的路径文本（兼容带空格、带引号格式）"""
    paths = []
    temp = ""
    in_quotes = False
    
    for char in user_input:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ' ' and not in_quotes:
            if temp.strip():
                paths.append(clean_path(temp))
                temp = ""
        else:
            temp += char
            
    if temp.strip():
        paths.append(clean_path(temp))
        
    valid_paths = [p for p in paths if os.path.isfile(p)]
    return valid_paths

def add_videos_workflow(video_files: list):
    """批量添加视频的输入工作流"""
    print("\n--- 录入待播视频 ---")
    print("💡 提示：可直接拖拽单个或多个文件至窗口，直接按回车结束添加。")
    while True:
        user_in = input(f"输入路径 [当前队列: {len(video_files)} 个] (回车结束): ").strip()
        if not user_in:
            break
        
        new_items = parse_multi_paths(user_in)
        if not new_items:
            # 尝试作为单一整体路径处理（容忍特殊未加引号的空格路径）
            single_p = clean_path(user_in)
            if os.path.isfile(single_p):
                new_items = [single_p]
        
        if new_items:
            for item in new_items:
                if item not in video_files:
                    video_files.append(item)
                    print(f"  ✓ 已加入: {Path(item).name}")
                else:
                    print(f"  ⚠️ 已在列表中，跳过重复: {Path(item).name}")
        else:
            print("  ❌ 未检测到有效的文件路径，请重试。")

def edit_video_list(video_files: list):
    """编辑视频队列列表"""
    while True:
        if not video_files:
            print("\n当前视频队列为空！")
            break
        print(f"\n当前播放队列 ({len(video_files)} 个项目):")
        for idx, item in enumerate(video_files, 1):
            print(f"  {idx}. {Path(item).name}")
            
        print("\n队列管理: [1] 追加视频  [2] 移除指定项  [3] 清空队列  [4] 完成并返回")
        op = input("请选择操作 (1-4): ").strip()
        if op == "1":
            add_videos_workflow(video_files)
        elif op == "2":
            del_idx = input("请输入要移除的序号: ").strip()
            if del_idx.isdigit():
                i = int(del_idx) - 1
                if 0 <= i < len(video_files):
                    removed = video_files.pop(i)
                    print(f"✓ 已移除: {Path(removed).name}")
                else:
                    print("❌ 无效的序号。")
            else:
                print("❌ 请输入数字。")
        elif op == "3":
            if input("确定清空全部队列吗？(y/n): ").strip().lower() == 'y':
                video_files.clear()
                print("✓ 队列已全部清空。")
                break
        elif op == "4":
            break

def mode_different_videos_single_player():
    """模态 1：不同视频 + 自主选择播放器"""
    while True:
        player_path, player_name = choose_single_player()
        if not player_path:
            return
        
        video_files = []
        while True:
            print(f"\n当前调用播放器: 【{player_name}】")
            print("1. 添加视频到队列")
            print("2. 查看/编辑视频队列")
            print("3. 确认启动播放")
            print("4. 重新选择播放器")
            print("0. 返回主菜单")
            
            sub_choice = input("请选择 (0-4): ").strip()
            if sub_choice == "0":
                return
            elif sub_choice == "1":
                add_videos_workflow(video_files)
            elif sub_choice == "2":
                edit_video_list(video_files)
            elif sub_choice == "3":
                if not video_files:
                    print("\n⚠️ 播放队列为空，请先添加视频！")
                    continue
                print(f"\n即将使用 [{player_name}] 启动 {len(video_files)} 个视频窗口...")
                if input("确认执行？(y/n): ").strip().lower() != 'y':
                    continue
                
                success = 0
                for v in video_files:
                    try:
                        subprocess.Popen([player_path, v], creationflags=subprocess.DETACHED_PROCESS if os.name == 'nt' else 0)
                        success += 1
                    except Exception as err:
                        print(f"❌ 启动失败 [{Path(v).name}]: {err}")
                print(f"\n🎉 成功启动 {success}/{len(video_files)} 个实例！")
                input("按回车键继续...")
                break
            elif sub_choice == "4":
                break

def mode_same_video_multiple_players():
    """模态 2：相同视频 + 不同播放器（对比横评）"""
    show_players_config()
    video_path = get_single_video_file()
    video_name = Path(video_path).name
    
    # 筛选可用播放器
    active_players = [(p["name"], p["path"]) for p in PLAYERS.values() if os.path.isfile(p["path"])]
    if not active_players:
        print("\n❌ 错误：未检测到任何可用的播放器路径，请先修改脚本配置。")
        input("按回车键返回...")
        return
    
    print(f"\n待测试视频: {video_name}")
    print(f"可用播放器 ({len(active_players)} 个):")
    for name, _ in active_players:
        print(f"  ▶ {name}")
        
    if input("\n确认同时启动上述所有播放器进行同屏对比？(y/n): ").strip().lower() != 'y':
        print("操作已取消。")
        return
        
    print(f"\n正在唤起各个播放器...")
    success = 0
    for name, path in active_players:
        try:
            print(f"  正在启动: {name} ...")
            subprocess.Popen([path, video_path], creationflags=subprocess.DETACHED_PROCESS if os.name == 'nt' else 0)
            success += 1
        except Exception as err:
            print(f"  ❌ {name} 启动失败: {err}")
            
    print(f"\n🎉 完成！已使用 {success} 个播放器同时载入视频: {video_name}")
    input("\n按回车键返回主菜单...")

def main_menu():
    """脚本总入口主菜单"""
    while True:
        print("\n" + "=" * 55)
        print("🎬  视频多功能播放调度工具集")
        print("=" * 55)
        print("  1. 不同视频 + 自主选择播放器（批量调起）")
        print("  2. 相同视频 + 不同播放器（画质/渲染器同屏对比）")
        print("  3. 检查播放器挂载与环境状态")
        print("  0. 退出程序")
        print("=" * 55)
        
        sel = input("请输入选项编号 (0-3): ").strip()
        if sel == "0":
            print("\n感谢使用，程序已安全退出。")
            break
        elif sel == "1":
            mode_different_videos_single_player()
        elif sel == "2":
            mode_same_video_multiple_players()
        elif sel == "3":
            show_players_config()
            input("\n按回车键返回主菜单...")
        else:
            print("\n❌ 输入无效，请重新选择。")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n用户强行中断。")
    except Exception as e:
        print(f"\n\n💥 程序发生未捕获异常: {e}")
        input("按回车键退出...")