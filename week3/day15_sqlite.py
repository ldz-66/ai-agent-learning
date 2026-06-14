import sqlite3

# ===== Part 1：创建数据库和表 =====
print("=" * 40)
print("Part 1：创建数据库和表")
print("=" * 40)

# 连接数据库（文件不存在会自动创建）
conn = sqlite3.connect("practice.db")

# 创建一个游标对象，用来执行SQL语句
cursor = conn.cursor()

# 创建用户表（如果不存在的话）
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        email TEXT
    )
""")

# 提交操作（写操作都需要commit才会真正保存）
conn.commit()
print("users表创建成功")


# ===== Part 2：插入数据 =====
print("\n" + "=" * 40)
print("Part 2：插入数据")
print("=" * 40)

# 插入单条数据（用?占位符，防止SQL注入）
cursor.execute(
    "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
    ("小明", 20, "xiaoming@example.com")
)

# 插入多条数据
users_data = [
    ("小红", 19, "xiaohong@example.com"),
    ("小蓝", 21, "xiaolan@example.com"),
    ("小绿", 22, None),  # email可以为空
]
cursor.executemany(
    "INSERT INTO users (name, age, email) VALUES (?, ?, ?)",
    users_data
)

conn.commit()
print("数据插入成功")


# ===== Part 3：查询数据 =====
print("\n" + "=" * 40)
print("Part 3：查询数据")
print("=" * 40)

# 查询所有用户
cursor.execute("SELECT * FROM users")
all_users = cursor.fetchall()  # 获取所有结果，返回列表
print("所有用户：")
for user in all_users:
    print(f"  id={user[0]}, name={user[1]}, age={user[2]}, email={user[3]}")

# 带条件查询
cursor.execute("SELECT * FROM users WHERE age >= ?", (20,))
adult_users = cursor.fetchall()
print(f"\n年龄>=20的用户（共{len(adult_users)}人）：")
for user in adult_users:
    print(f"  {user[1]}，{user[2]}岁")

# 排序查询
cursor.execute("SELECT * FROM users ORDER BY age DESC")
sorted_users = cursor.fetchall()
print("\n按年龄从大到小排序：")
for user in sorted_users:
    print(f"  {user[1]}，{user[2]}岁")


# ===== Part 4：更新和删除 =====
print("\n" + "=" * 40)
print("Part 4：更新和删除")
print("=" * 40)

# 更新数据
cursor.execute(
    "UPDATE users SET age = ? WHERE name = ?",
    (25, "小明")
)
conn.commit()
print("更新成功：小明的年龄改为25")

# 验证更新
cursor.execute("SELECT age FROM users WHERE name = ?", ("小明",))
result = cursor.fetchone()  # 只获取一条结果
print(f"更新后小明的年龄：{result[0]}")

# 删除数据
cursor.execute("DELETE FROM users WHERE name = ?", ("小绿",))
conn.commit()
print("删除成功：小绿已删除")

# 查询剩余用户数量
cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
print(f"剩余用户数量：{count}")


# ===== 关闭连接（重要！） =====
conn.close()
print("\n数据库连接已关闭")