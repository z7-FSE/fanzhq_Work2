class Student:
    """保存单个学生的基本信息。"""

    def __init__(self, student_id, name):
        self.student_id = student_id
        self.name = name

    def show_info(self):
        print("学生完整信息：")
        print("姓名:" + self.name)
        print("学号:" + self.student_id)

    def to_arrangement_line(self, seat_no):
        return str(seat_no) + "," + self.name + "," + self.student_id
