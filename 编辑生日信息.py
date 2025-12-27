import json
import os
import sys
from datetime import datetime

class BirthdayManager:
    def __init__(self, json_file='birthdays.json', images_dir='images'):
        self.json_file = json_file
        self.images_dir = images_dir
        self.data = []
        self.used_images = set()
        
    def load_data(self):
        """加载现有的JSON数据"""
        if os.path.exists(self.json_file):
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            # 收集已使用的图片
            for item in self.data:
                if 'avatar' in item:
                    self.used_images.add(item['avatar'])
        else:
            self.data = []
            
    def save_data(self):
        """保存数据到JSON文件"""
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {self.json_file}")
    
    def list_unused_images(self):
        """列出images文件夹中未使用的图片"""
        if not os.path.exists(self.images_dir):
            print(f"警告：{self.images_dir} 文件夹不存在！")
            return []
        
        all_images = [f for f in os.listdir(self.images_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        unused_images = [img for img in all_images if img not in self.used_images]
        return unused_images
    
    def display_items(self):
        """显示所有项目"""
        if not self.data:
            print("当前没有任何生日记录。")
            return False
        
        print("\n=== 当前生日记录 ===")
        for i, item in enumerate(self.data, 1):
            print(f"{i}. {item['name']}")
            print(f"   生日: {item['birthday']}")
            print(f"   农历: {'是' if item['isLunar'] else '否'}")
            print(f"   头像: {item.get('avatar', '无')}")
            print()
        return True
    
    def add_item(self, first_time=False):
        """添加一个新项目"""
        if first_time:
            print(f"\n请先将要用到的好友头像图片放入 {self.images_dir} 文件夹中。")
            input("按回车键继续...")
        
        print("\n=== 添加新生日记录 ===")
        
        # 获取名称
        name = input("姓名: ").strip()
        while not name:
            print("姓名不能为空！")
            name = input("姓名: ").strip()
        
        # 获取生日
        while True:
            birthday = input("出生日期 (格式: YYYY-MM-DD): ").strip()
            try:
                datetime.strptime(birthday, '%Y-%m-%d')
                break
            except ValueError:
                print("日期格式错误，请使用 YYYY-MM-DD 格式")
        
        # 获取是否为农历
        while True:
            is_lunar_str = input("是否过农历生日? (y/n): ").strip().lower()
            if is_lunar_str in ['y', 'yes', '是']:
                is_lunar = True
                break
            elif is_lunar_str in ['n', 'no', '否']:
                is_lunar = False
                break
            else:
                print("请输入 y/n 或 是/否")
        
        # 选择图片
        print("\n选择头像图片:")
        print("1. 从已上传但未使用的图片中选择")
        print("2. 手动输入图片文件名")
        print("3. 不使用图片")
        
        avatar = ""
        while True:
            choice = input("请选择 (1-3): ").strip()
            if choice == '1':
                unused_images = self.list_unused_images()
                if unused_images:
                    print("\n可用的未使用图片:")
                    for i, img in enumerate(unused_images, 1):
                        print(f"{i}. {img}")
                    
                    try:
                        img_choice = int(input(f"选择图片 (1-{len(unused_images)}): ")) - 1
                        if 0 <= img_choice < len(unused_images):
                            avatar = unused_images[img_choice]
                            break
                        else:
                            print("选择无效！")
                    except ValueError:
                        print("请输入数字！")
                else:
                    print("没有找到未使用的图片。")
            elif choice == '2':
                avatar = input("输入图片文件名 (包括扩展名): ").strip()
                if avatar:
                    # 检查文件是否存在
                    if os.path.exists(os.path.join(self.images_dir, avatar)):
                        break
                    else:
                        print(f"警告: {self.images_dir}/{avatar} 文件不存在！")
                        use_anyway = input("仍然使用这个文件名? (y/n): ").strip().lower()
                        if use_anyway in ['y', 'yes']:
                            break
                else:
                    print("使用空文件名（无头像）")
                    break
            elif choice == '3':
                avatar = ""
                break
            else:
                print("选择无效！")
        
        # 创建新项目
        new_item = {
            "name": name,
            "birthday": birthday,
            "isLunar": is_lunar,
            "avatar": avatar
        }
        
        self.data.append(new_item)
        if avatar:
            self.used_images.add(avatar)
        
        print(f"已添加: {name}")
        return True
    
    def delete_item(self):
        """删除一个项目"""
        if not self.display_items():
            return False
        
        try:
            index = int(input("\n输入要删除的项目编号: ")) - 1
            if 0 <= index < len(self.data):
                item = self.data[index]
                print(f"\n将要删除: {item['name']}")
                confirm = input("确认删除? (y/n): ").strip().lower()
                if confirm in ['y', 'yes', '是']:
                    removed = self.data.pop(index)
                    if removed.get('avatar'):
                        self.used_images.discard(removed['avatar'])
                    print(f"已删除: {removed['name']}")
                    return True
                else:
                    print("取消删除。")
                    return False
            else:
                print("编号无效！")
                return False
        except ValueError:
            print("请输入有效的数字！")
            return False
    
    def edit_item(self):
        """修改一个项目"""
        if not self.display_items():
            return False
        
        try:
            index = int(input("\n输入要修改的项目编号: ")) - 1
            if 0 <= index < len(self.data):
                item = self.data[index]
                print(f"\n正在修改: {item['name']}")
                
                # 显示当前信息
                print("\n当前信息:")
                print(f"1. 姓名: {item['name']}")
                print(f"2. 生日: {item['birthday']}")
                print(f"3. 农历: {'是' if item['isLunar'] else '否'}")
                print(f"4. 头像: {item.get('avatar', '无')}")
                print("5. 完成修改")
                
                while True:
                    field = input("\n选择要修改的字段 (1-5): ").strip()
                    
                    if field == '1':  # 修改姓名
                        new_name = input(f"新姓名 (当前: {item['name']}): ").strip()
                        if new_name:
                            item['name'] = new_name
                            print("姓名已更新")
                    
                    elif field == '2':  # 修改生日
                        while True:
                            new_birthday = input(f"新生日 (当前: {item['birthday']}): ").strip()
                            if not new_birthday:  # 跳过
                                break
                            try:
                                datetime.strptime(new_birthday, '%Y-%m-%d')
                                item['birthday'] = new_birthday
                                print("生日已更新")
                                break
                            except ValueError:
                                print("日期格式错误，请使用 YYYY-MM-DD 格式")
                    
                    elif field == '3':  # 修改农历
                        current = '是' if item['isLunar'] else '否'
                        while True:
                            new_lunar = input(f"是否为农历? (当前: {current}) (y/n): ").strip().lower()
                            if not new_lunar:  # 跳过
                                break
                            if new_lunar in ['y', 'yes', '是']:
                                item['isLunar'] = True
                                print("已设置为农历生日")
                                break
                            elif new_lunar in ['n', 'no', '否']:
                                item['isLunar'] = False
                                print("已设置为公历生日")
                                break
                            else:
                                print("请输入 y/n 或 是/否")
                    
                    elif field == '4':  # 修改头像
                        print("\n选择头像图片:")
                        print("1. 从已上传但未使用的图片中选择")
                        print("2. 手动输入图片文件名")
                        print("3. 清空头像")
                        print("4. 跳过（不修改）")
                        
                        avatar_choice = input("请选择 (1-4): ").strip()
                        
                        if avatar_choice == '1':
                            unused_images = self.list_unused_images()
                            if unused_images:
                                print("\n可用的未使用图片:")
                                for i, img in enumerate(unused_images, 1):
                                    print(f"{i}. {img}")
                                
                                try:
                                    img_choice = int(input(f"选择图片 (1-{len(unused_images)}): ")) - 1
                                    if 0 <= img_choice < len(unused_images):
                                        old_avatar = item.get('avatar', '')
                                        new_avatar = unused_images[img_choice]
                                        item['avatar'] = new_avatar
                                        if old_avatar:
                                            self.used_images.discard(old_avatar)
                                        self.used_images.add(new_avatar)
                                        print(f"头像已更新为: {new_avatar}")
                                    else:
                                        print("选择无效！")
                                except ValueError:
                                    print("请输入数字！")
                            else:
                                print("没有找到未使用的图片。")
                        
                        elif avatar_choice == '2':
                            new_avatar = input(f"新图片文件名 (当前: {item.get('avatar', '无')}): ").strip()
                            if new_avatar:
                                old_avatar = item.get('avatar', '')
                                item['avatar'] = new_avatar
                                if old_avatar:
                                    self.used_images.discard(old_avatar)
                                self.used_images.add(new_avatar)
                                print(f"头像已更新为: {new_avatar}")
                            else:
                                print("跳过修改")
                        
                        elif avatar_choice == '3':
                            old_avatar = item.get('avatar', '')
                            item['avatar'] = ''
                            if old_avatar:
                                self.used_images.discard(old_avatar)
                            print("头像已清空")
                        
                        elif avatar_choice == '4':
                            print("跳过头像修改")
                    
                    elif field == '5':  # 完成修改
                        print("修改完成！")
                        break
                    
                    else:
                        print("选择无效！")
                
                return True
            else:
                print("编号无效！")
                return False
        except ValueError:
            print("请输入有效的数字！")
            return False
    
    def rewrite_json(self):
        """重写整个JSON文件"""
        print("\n=== 警告 ===")
        print("此操作将清空所有现有数据！")
        confirm = input("确定要清空并重新编写吗? (y/n): ").strip().lower()
        
        if confirm in ['y', 'yes', '是']:
            self.data = []
            self.used_images.clear()
            print("\n已清空所有数据。")
            
            # 进入添加模式
            first_time = True
            while True:
                self.add_item(first_time)
                first_time = False
                
                continue_add = input("\n是否继续添加? (y/n): ").strip().lower()
                if continue_add not in ['y', 'yes', '是']:
                    break
            
            if self.data:
                self.save_data()
            else:
                print("没有添加任何数据，文件保持为空。")
            return True
        else:
            print("取消操作。")
            return False
    
    def modify_existing(self):
        """修改现有JSON文件"""
        while True:
            print("\n=== 修改模式 ===")
            print("1. 添加新记录")
            print("2. 删除记录")
            print("3. 修改记录")
            print("4. 查看所有记录")
            print("5. 保存并返回主菜单")
            
            choice = input("请选择 (1-5): ").strip()
            
            if choice == '1':
                self.add_item(False)
                continue_add = input("是否继续添加? (y/n): ").strip().lower()
                while continue_add in ['y', 'yes', '是']:
                    self.add_item(False)
                    continue_add = input("是否继续添加? (y/n): ").strip().lower()
            
            elif choice == '2':
                if self.delete_item():
                    continue_del = input("是否继续删除? (y/n): ").strip().lower()
                    while continue_del in ['y', 'yes', '是']:
                        if not self.delete_item():
                            break
                        continue_del = input("是否继续删除? (y/n): ").strip().lower()
            
            elif choice == '3':
                if self.edit_item():
                    continue_edit = input("是否继续修改其他记录? (y/n): ").strip().lower()
                    while continue_edit in ['y', 'yes', '是']:
                        if not self.edit_item():
                            break
                        continue_edit = input("是否继续修改其他记录? (y/n): ").strip().lower()
            
            elif choice == '4':
                self.display_items()
                input("按回车键继续...")
            
            elif choice == '5':
                self.save_data()
                return True
            
            else:
                print("选择无效！")
    
    def run(self):
        """运行主程序"""
        self.load_data()
        
        while True:
            print("\n" + "="*40)
            print("      生日管家数据管理工具")
            print("="*40)
            print(f"当前文件: {self.json_file}")
            print(f"图片目录: {self.images_dir}")
            print(f"当前记录数: {len(self.data)}")
            print("="*40)
            print("1. 修改现有JSON文件")
            print("2. 重写整个JSON文件")
            print("3. 查看当前所有记录")
            print("4. 查看未使用的图片")
            print("5. 退出程序")
            
            choice = input("\n请选择操作 (1-5): ").strip()
            
            if choice == '1':
                self.modify_existing()
            
            elif choice == '2':
                self.rewrite_json()
            
            elif choice == '3':
                self.display_items()
                input("按回车键返回主菜单...")
            
            elif choice == '4':
                unused = self.list_unused_images()
                if unused:
                    print(f"\n{self.images_dir} 文件夹中未使用的图片:")
                    for img in unused:
                        print(f"  - {img}")
                else:
                    print(f"\n{self.images_dir} 文件夹中没有未使用的图片。")
                input("按回车键返回主菜单...")
            
            elif choice == '5':
                if self.data:
                    save_before_exit = input("退出前是否保存更改? (y/n): ").strip().lower()
                    if save_before_exit in ['y', 'yes', '是']:
                        self.save_data()
                print("感谢使用，再见！")
                break
            
            else:
                print("选择无效，请重新选择！")

def main():
    # 检查命令行参数
    json_file = 'birthdays.json'
    images_dir = 'images'
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        images_dir = sys.argv[2]
    
    # 创建必要目录
    if not os.path.exists(images_dir):
        os.makedirs(images_dir, exist_ok=True)
    
    # 运行管理器
    manager = BirthdayManager(json_file, images_dir)
    manager.run()

if __name__ == "__main__":
    main()