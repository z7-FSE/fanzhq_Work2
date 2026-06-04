import os
import random

from student import Student


class ExamSys:
    """学生信息与考场管理系统。"""

    def __init__(self, data_file="人工智能编程语言学生名单.txt"):
        # 用程序所在目录拼路径，避免从别的目录运行时找不到名单文件。
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(self.base_dir, data_file)
        self.students = []
        self.exam_arrangement = []
        self.load_students()

    def load_students(self):
        """从学生名单文件中读取学生信息。"""
        self.students = []
        try:
            with open(self.data_file, "r", encoding="utf-8") as file:
                for line in file:
                    text = line.strip()
                    # 空行和以 # 开头的说明行不算学生数据。
                    if not text or text.startswith("#"):
                        continue
                    student = self._parse_student_line(text)
                    if student is not None:
                        self.students.append(student)
        except FileNotFoundError:
            print("学生名单文件不存在，请检查文件是否放在程序根目录。")
        except OSError:
            print("读取学生名单文件失败，请检查文件权限或路径。")

    def _parse_student_line(self, text):
        """把一行名单文本转换为 Student 对象。"""
        if "," in text:
            parts = text.split(",")
        else:
            parts = text.split()
        if len(parts) < 2:
            return None

        # 新名单是“序号 姓名 性别 班级 学号 学院”的表格，表头需要跳过。
        if parts[0].strip() == "序号":
            return None

        # 兼容课程附件表格格式：序号、姓名、性别、班级、学号、学院。
        if len(parts) >= 5 and parts[0].strip().isdigit() and parts[4].strip().isdigit():
            return Student(parts[4].strip(), parts[1].strip())

        # 兼容“学号 姓名”和“姓名 学号”两种简化写法。
        first = parts[0].strip()
        second = parts[1].strip()
        if first.isdigit():
            return Student(first, second)
        return Student(second, first)

    def run(self):
        """显示菜单并根据用户输入调用对应功能。"""
        while True:
            print("===== 学生信息与考场管理系统 =====")
            print("1. 查询学生信息")
            print("2. 随机点名")
            print("3. 生成考场安排表")
            print("4. 生成准考证文件")
            print("+--------------------------------------------------------------------------")
            print("0. 退出系统")
            choice = input("请输入功能编号：").strip()

            if choice == "1":
                self.find_student()
            elif choice == "2":
                self.random_roll_call()
            elif choice == "3":
                self.generate_exam_arrangement()
            elif choice == "4":
                self.generate_admission_tickets()
            elif choice == "0":
                print("系统已退出，感谢使用。")
                break
            else:
                print("功能编号不存在，请正确输入功能编号（0~4）：")

    def find_student(self):
        """根据输入学号查询学生。"""
        student_id = input("请输入要查询的学号：").strip()
        for student in self.students:
            # 逐个比较学号，找到后直接 return，避免后面又打印“未找到”。
            if student.student_id == student_id:
                student.show_info()
                return
        print("未找到该学号对应的学生，请检查输入是否正确。")

    def random_roll_call(self):
        """随机抽取不重复学生名单。"""
        try:
            count_text = input("请输入需要点名的学生数量：").strip()
            # int 转换失败、人数不合理，都会交给下面的 except 统一提示。
            count = int(count_text)
            if count <= 0:
                raise ValueError("人数必须大于0")
            if count > len(self.students):
                raise ValueError("人数不能超过学生总人数")
        except ValueError:
            print("输入人数无效，请输入1到" + str(len(self.students)) + "之间的整数。")
            return

        selected_students = random.sample(self.students, count)
        print("本次随机点名结果：")
        index = 1
        for student in selected_students:
            print(str(index) + "." + student.name + " " + student.student_id)
            index += 1

    def generate_exam_arrangement(self):
        """随机打乱学生顺序并生成考场安排表。"""
        # 先复制一份列表再打乱，不改变原始学生名单顺序。
        self.exam_arrangement = self.students[:]
        random.shuffle(self.exam_arrangement)

        output_path = os.path.join(self.base_dir, "考场安排表.txt")
        try:
            with open(output_path, "w", encoding="utf-8") as file:
                seat_no = 1
                for student in self.exam_arrangement:
                    # 每行格式按题目要求写成：座位号,姓名,学号。
                    file.write(student.to_arrangement_line(seat_no) + "\n")
                    seat_no += 1
            print("考场安排表已生成：" + output_path)
        except OSError:
            print("考场安排表写入失败，请检查程序目录权限。")

    def generate_admission_tickets(self):
        """根据考场安排为每名学生生成独立准考证文件。"""
        # 如果用户没有先生成考场安排，这里尝试读取旧文件或自动生成一份。
        if not self.exam_arrangement:
            arrangement_path = os.path.join(self.base_dir, "考场安排表.txt")
            if os.path.exists(arrangement_path):
                self._load_arrangement_file(arrangement_path)
            else:
                self.generate_exam_arrangement()

        ticket_dir = os.path.join(self.base_dir, "准考证")
        try:
            if not os.path.exists(ticket_dir):
                os.mkdir(ticket_dir)
            else:
                # 重新生成时先清理旧准考证，避免名单人数变化后留下多余文件。
                for filename in os.listdir(ticket_dir):
                    if filename.endswith(".txt"):
                        os.remove(os.path.join(ticket_dir, filename))

            width = len(str(len(self.exam_arrangement)))
            if width < 2:
                width = 2

            seat_no = 1
            for student in self.exam_arrangement:
                # zfill 用来把 1 变成 01，文件名排序时更整齐。
                filename = str(seat_no).zfill(width) + ".txt"
                ticket_path = os.path.join(ticket_dir, filename)
                with open(ticket_path, "w", encoding="utf-8") as file:
                    file.write("考场座位号:" + str(seat_no) + "\n")
                    file.write("姓名:" + student.name + "\n")
                    file.write("学号:" + student.student_id + "\n")
                seat_no += 1
            print("准考证文件已生成：" + ticket_dir)
        except OSError:
            print("准考证文件生成失败，请检查文件夹权限。")

    def _load_arrangement_file(self, arrangement_path):
        """从已存在的考场安排表恢复座位顺序。"""
        self.exam_arrangement = []
        try:
            with open(arrangement_path, "r", encoding="utf-8") as file:
                for line in file:
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        self.exam_arrangement.append(Student(parts[2], parts[1]))
        except OSError:
            print("读取已有考场安排表失败，将重新生成安排表。")
            self.generate_exam_arrangement()

ExamSystem = ExamSys
