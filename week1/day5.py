# ===== Part 1: 列表推导式 =====
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# 传统写法
squares_old = []
for n in numbers:
    squares_old.append(n ** 2)

# 列表推导式写法（效果相同，更简洁）
squares_new = [n ** 2 for n in numbers]

print("传统写法结果:", squares_old)
print("推导式结果:", squares_new)

# 带条件的推导式：只保留偶数的平方
even_squares = [n ** 2 for n in numbers if n % 2 == 0]
print("偶数的平方:", even_squares)
# ===== Part 2: 字典操作 =====
student = {"name": "小明", "age": 20, "major": "计算机科学"}

# 访问与修改
print("姓名:", student["name"])
student["age"] = 21  # 修改
student["grade"] = "大二"  # 新增

# 遍历字典
for key, value in student.items():
    print(f"{key}: {value}")

# get方法（避免key不存在时报错）
print("不存在的key:", student.get("gpa", "未设置"))

# 字典推导式
scores = {"语文": 85, "数学": 92, "英语": 78}
passed = {subject: score for subject, score in scores.items() if score >= 80}
print("及格科目:", passed)
# ===== Part 3: 文件读写 =====
# 读取文件
with open("sample.txt", "r", encoding="utf-8") as f:
    content = f.read()
print("文件内容:\n" + content)

# 按行读取
with open("sample.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
print("共有", len(lines), "行")

# 写入新文件
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("这是写入的内容\n")
    f.write("第二行\n")

print("output.txt 已生成")
# ===== Part 4: 异常处理 =====
def divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("错误: 除数不能为0")
        return None
    except TypeError:
        print("错误: 参数类型不对，需要数字")
        return None
    finally:
        print("本次计算尝试结束")

print(divide(10, 2))
print(divide(10, 0))
print(divide(10, "a"))
# ===== Part 5: *args 和 **kwargs =====
def sum_all(*args):
    """接收任意数量的位置参数"""
    total = 0
    for num in args:
        total += num
    return total

print("求和结果:", sum_all(1, 2, 3))
print("求和结果:", sum_all(1, 2, 3, 4, 5))


def print_info(**kwargs):
    """接收任意数量的关键字参数"""
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="小红", age=19, city="北京")