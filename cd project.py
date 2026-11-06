import re
import tkinter as tk
from tkinter import messagebox, ttk

# ============================================================
# GLOBAL DATA & PARSER LOGIC
# ============================================================

temp_count = 1
label_count = 1

tac = []
quadruples = []
triples = []


def new_temp():
    global temp_count
    temp = f"t{temp_count}"
    temp_count += 1
    return temp


def new_label():
    global label_count
    label = f"L{label_count}"
    label_count += 1
    return label


def precedence(op):
    if op in ["+", "-"]:
        return 1
    if op in ["*", "/"]:
        return 2
    return 0


def infix_to_postfix(expression):
    stack = []
    output = []
    tokens = re.findall(r"[A-Za-z_]\w*|\d+|[()+\-*/]", expression)

    for token in tokens:
        if re.match(r"[A-Za-z_]\w*|\d+", token):
            output.append(token)
        elif token == "(":
            stack.append(token)
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if stack:
                stack.pop()
        else:
            while (
                stack
                and stack[-1] != "("
                and precedence(stack[-1]) >= precedence(token)
            ):
                output.append(stack.pop())
            stack.append(token)

    while stack:
        output.append(stack.pop())

    return output


def generate_expression(expression):
    postfix = infix_to_postfix(expression)
    stack = []
    triple_index = {}

    for token in postfix:
        if re.match(r"[A-Za-z_]\w*|\d+", token):
            stack.append(token)
        else:
            if len(stack) < 2:
                continue

            op2 = stack.pop()
            op1 = stack.pop()
            temp = new_temp()

            tac.append(f"{temp} = {op1} {token} {op2}")
            quadruples.append([token, op1, op2, temp])

            arg1 = f"({triple_index[op1]})" if op1 in triple_index else op1
            arg2 = f"({triple_index[op2]})" if op2 in triple_index else op2
            triple_no = len(triples)

            triples.append([token, arg1, arg2])
            triple_index[temp] = triple_no

            stack.append(temp)

    if not stack:
        return expression.strip()

    return stack[-1]


def generate_condition(condition):
    condition = condition.strip()
    operators = [">=", "<=", "==", "!=", ">", "<"]
    for op in operators:
        if op in condition:
            left, right = condition.split(op, 1)
            return left.strip(), op, right.strip()
    raise ValueError("Invalid condition: " + condition)


def generate_if(condition):
    left, operator, right = generate_condition(condition)
    true_label = new_label()
    false_label = new_label()

    tac.append(f"if {left} {operator} {right} goto {true_label}")
    tac.append(f"goto {false_label}")
    tac.append(f"{true_label}:")

    return false_label


def generate_else(false_label):
    end_label = new_label()
    tac.append(f"goto {end_label}")
    tac.append(f"{false_label}:")
    return end_label


def generate_while(condition):
    left, operator, right = generate_condition(condition)
    start_label = new_label()
    end_label = new_label()

    tac.append(f"{start_label}:")
    reverse = {
        ">": "<=",
        "<": ">=",
        ">=": "<",
        "<=": ">",
        "==": "!=",
        "!=": "==",
    }
    tac.append(f"if {left} {reverse[operator]} {right} goto {end_label}")

    return start_label, end_label


def generate_function_definition(line):
    match = re.match(r"function\s+(\w+)\s*\((.*?)\)", line)
    if not match:
        return False

    function_name = match.group(1)
    parameter_text = match.group(2).strip()
    parameters = (
        [x.strip() for x in parameter_text.split(",")] if parameter_text else []
    )

    tac.append(f"func {function_name}:")
    for parameter in parameters:
        tac.append(f"param {parameter}")

    return True


def generate_function_call(line):
    line = line.replace(";", "").strip()
    match = re.match(r"(\w+)\s*\((.*?)\)", line)
    if not match:
        return False

    function_name = match.group(1)
    argument_text = match.group(2).strip()
    arguments = (
        [x.strip() for x in argument_text.split(",")] if argument_text else []
    )

    for argument in arguments:
        tac.append(f"param {argument}")

    temp = new_temp()
    tac.append(f"{temp} = call {function_name}, {len(arguments)}")
    return True


def split_braces(line):
    line = line.replace("{", "\n{\n").replace("}", "\n}\n")
    return [part.strip() for part in line.split("\n") if part.strip()]


def clear_output():
    tac_box.delete("1.0", tk.END)
    for row in quad_table.get_children():
        quad_table.delete(row)
    for row in triple_table.get_children():
        triple_table.delete(row)


def display_output():
    clear_output()

    for line in tac:
        tac_box.insert(tk.END, line + "\n")

    for i, row in enumerate(quadruples, start=1):
        tag = "even" if i % 2 == 0 else "odd"
        quad_table.insert(
            "",
            "end",
            values=(i, row[0], row[1], row[2], row[3]),
            tags=(tag,),
        )

    for i, row in enumerate(triples):
        tag = "even" if i % 2 == 0 else "odd"
        triple_table.insert(
            "", "end", values=(i, row[0], row[1], row[2]), tags=(tag,)
        )


def generate():
    global temp_count, label_count

    temp_count = 1
    label_count = 1

    tac.clear()
    quadruples.clear()
    triples.clear()

    code = input_box.get("1.0", tk.END).strip()

    if not code:
        messagebox.showwarning(
            "Input Missing", "Please enter source code to parse."
        )
        return

    try:
        raw_lines = code.split("\n")
        lines = []
        for raw_line in raw_lines:
            lines.extend(split_braces(raw_line))

        block_stack = []
        i = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line or line == "{":
                i += 1
                continue

            if line == "}":
                if block_stack:
                    block = block_stack.pop()
                    block_type = block[0]

                    if block_type == "while":
                        tac.append(f"goto {block[1]}")
                        tac.append(f"{block[2]}:")
                    elif block_type == "for":
                        if block[3] and "=" in block[3]:
                            left, right = block[3].split("=", 1)
                            res = generate_expression(right.strip())
                            tac.append(f"{left.strip()} = {res}")
                        tac.append(f"goto {block[1]}")
                        tac.append(f"{block[2]}:")
                    elif block_type in ["if", "else"]:
                        tac.append(f"{block[1]}:")
                    elif block_type == "function":
                        tac.append("endfunc")

                i += 1
                continue

            if line.startswith("if"):
                match = re.search(r"if\s*\((.*?)\)", line)
                if not match:
                    raise ValueError("Invalid if statement format.")
                false_label = generate_if(match.group(1))
                block_stack.append(("if", false_label))
                i += 1
                continue

            if line.startswith("else"):
                if block_stack and block_stack[-1][0] == "if":
                    old_if = block_stack.pop()
                    end_label = generate_else(old_if[1])
                    block_stack.append(("else", end_label))
                i += 1
                continue

            if line.startswith("while"):
                match = re.search(r"while\s*\((.*?)\)", line)
                if not match:
                    raise ValueError("Invalid while statement format.")
                start_label, end_label = generate_while(match.group(1))
                block_stack.append(("while", start_label, end_label))
                i += 1
                continue

            if line.startswith("for"):
                match = re.search(r"for\s*\((.*?);(.*?);(.*?)\)", line)
                if not match:
                    raise ValueError("Invalid for loop format.")

                initialization, condition, increment = (
                    match.group(1).strip(),
                    match.group(2).strip(),
                    match.group(3).strip(),
                )

                if initialization and "=" in initialization:
                    left, right = initialization.split("=", 1)
                    res = generate_expression(right.strip())
                    tac.append(f"{left.strip()} = {res}")

                left, operator, right = generate_condition(condition)
                start_label, end_label = new_label(), new_label()

                tac.append(f"{start_label}:")
                reverse = {
                    ">": "<=",
                    "<": ">=",
                    ">=": "<",
                    "<=": ">",
                    "==": "!=",
                    "!=": "==",
                }
                tac.append(
                    f"if {left} {reverse[operator]} {right} goto {end_label}"
                )

                block_stack.append(("for", start_label, end_label, increment))
                i += 1
                continue

            if line.startswith("function"):
                if generate_function_definition(line):
                    block_stack.append(("function",))
                i += 1
                continue

            if line.startswith("return"):
                value = line[6:].replace(";", "").strip()
                if value:
                    res = generate_expression(value)
                    tac.append(f"return {res}")
                else:
                    tac.append("return")
                i += 1
                continue

            if "(" in line and ")" in line and "=" not in line:
                if generate_function_call(line.replace(";", "").strip()):
                    i += 1
                    continue

            if "=" in line and not any(
                op in line for op in ["==", "<=", ">=", "!="]
            ):
                statement = line.replace(";", "")
                left, right = statement.split("=", 1)
                left = left.strip()
                result = generate_expression(right.strip())
                if result:
                    tac.append(f"{left} = {result}")
                i += 1
                continue

            tac.append("# " + line)
            i += 1

        display_output()

    except Exception as e:
        messagebox.showerror("Parsing Error", str(e))


# ============================================================
# MODERN UI DESIGN & THEME SETUP
# ============================================================

root = tk.Tk()
root.title("Intermediate Code Generator - Compiler Design Tool")
root.geometry("1000x800")
root.minsize(800, 600)

BG_DARK = "#1e1e2e"
BG_CARD = "#252538"
ACCENT_BLUE = "#89b4fa"
ACCENT_GREEN = "#a6e3a1"
ACCENT_RED = "#f38ba8"
TEXT_COLOR = "#cdd6f4"
MUTED_COLOR = "#a6adc8"
LINE_COLOR = "#313244"

root.configure(bg=BG_DARK)

style = ttk.Style()
style.theme_use("clam")

style.configure("TNotebook", background=BG_DARK, borderwidth=0)
style.configure(
    "TNotebook.Tab",
    background=BG_CARD,
    foreground=MUTED_COLOR,
    padding=[12, 6],
    font=("Segoe UI", 10, "bold"),
)
style.map(
    "TNotebook.Tab",
    background=[("selected", ACCENT_BLUE)],
    foreground=[("selected", BG_DARK)],
)

style.configure(
    "Treeview",
    background=BG_CARD,
    foreground=TEXT_COLOR,
    fieldbackground=BG_CARD,
    rowheight=28,
    font=("Consolas", 10),
)
style.configure(
    "Treeview.Heading",
    background=LINE_COLOR,
    foreground=ACCENT_BLUE,
    font=("Segoe UI", 10, "bold"),
)
style.map(
    "Treeview.Heading",
    background=[("active", ACCENT_BLUE)],
    foreground=[("active", BG_DARK)],
)

header = tk.Frame(root, bg=BG_DARK, pady=10)
header.pack(fill=tk.X, padx=15, side=tk.TOP)

title = tk.Label(
    header,
    text="Intermediate Code Generator",
    font=("Segoe UI", 18, "bold"),
    fg=ACCENT_BLUE,
    bg=BG_DARK,
)
title.pack(anchor="w")

subtitle = tk.Label(
    header,
    text="Transforms C-like constructs into TAC, Quadruples, and Triples",
    font=("Segoe UI", 9),
    fg=MUTED_COLOR,
    bg=BG_DARK,
)
subtitle.pack(anchor="w")

input_frame = tk.Frame(
    root, bg=BG_CARD, highlightthickness=1, highlightbackground=LINE_COLOR
)
input_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 0), side=tk.TOP)

input_header = tk.Frame(input_frame, bg=BG_CARD, pady=5, padx=8)
input_header.pack(fill=tk.X)

input_label = tk.Label(
    input_header,
    text="Source Code Input",
    font=("Segoe UI", 10, "bold"),
    fg=TEXT_COLOR,
    bg=BG_CARD,
)
input_label.pack(side=tk.LEFT)

input_box_frame = tk.Frame(input_frame, bg=BG_CARD)
input_box_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

input_box = tk.Text(
    input_box_frame,
    font=("Consolas", 10),
    bg="#181825",
    fg=TEXT_COLOR,
    insertbackground=TEXT_COLOR,
    relief=tk.FLAT,
    undo=True,
    padx=8,
    pady=8,
    height=8,
)
input_scroll = ttk.Scrollbar(
    input_box_frame, orient=tk.VERTICAL, command=input_box.yview
)
input_box.configure(yscrollcommand=input_scroll.set)

input_scroll.pack(side=tk.RIGHT, fill=tk.Y)
input_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

button_frame = tk.Frame(root, bg=BG_DARK, pady=8)
button_frame.pack(fill=tk.X, padx=15, side=tk.TOP)

generate_btn = tk.Button(
    button_frame,
    text="⚡ Generate Representation",
    command=generate,
    bg=ACCENT_GREEN,
    fg=BG_DARK,
    font=("Segoe UI", 10, "bold"),
    padx=15,
    pady=5,
    activebackground="#94e2d5",
    activeforeground=BG_DARK,
    relief=tk.FLAT,
    cursor="hand2",
)
generate_btn.pack(side=tk.LEFT, padx=(0, 8))

clear_btn = tk.Button(
    button_frame,
    text="Clear All",
    command=lambda: (input_box.delete("1.0", tk.END), clear_output()),
    bg=BG_CARD,
    fg=ACCENT_RED,
    font=("Segoe UI", 10, "bold"),
    padx=15,
    pady=5,
    activebackground=ACCENT_RED,
    activeforeground=BG_DARK,
    relief=tk.FLAT,
    cursor="hand2",
)
clear_btn.pack(side=tk.LEFT)


def load_sample():
    sample = (
        "function sum(a, b) {\n"
        "    x = a + b * 2;\n"
        "    if (x > 10) {\n"
        "        return x;\n"
        "    } else {\n"
        "        return 0;\n"
        "    }\n"
        "}"
    )
    input_box.delete("1.0", tk.END)
    input_box.insert(tk.END, sample)


sample_btn = tk.Button(
    button_frame,
    text="Load Example Code",
    command=load_sample,
    bg=BG_CARD,
    fg=MUTED_COLOR,
    font=("Segoe UI", 9),
    padx=10,
    pady=5,
    relief=tk.FLAT,
    cursor="hand2",
)
sample_btn.pack(side=tk.RIGHT)

output_frame = tk.Frame(root, bg=BG_DARK)
output_frame.pack(
    fill=tk.BOTH, expand=True, padx=15, pady=(0, 10), side=tk.TOP
)

notebook = ttk.Notebook(output_frame)
notebook.pack(fill=tk.BOTH, expand=True)

tac_tab = tk.Frame(notebook, bg=BG_CARD)
notebook.add(tac_tab, text=" Three Address Code (TAC) ")

tac_box = tk.Text(
    tac_tab,
    font=("Consolas", 10),
    bg="#181825",
    fg=ACCENT_GREEN,
    insertbackground=TEXT_COLOR,
    relief=tk.FLAT,
    padx=8,
    pady=8,
    height=10,
)
tac_scroll = ttk.Scrollbar(
    tac_tab, orient=tk.VERTICAL, command=tac_box.yview
)
tac_box.configure(yscrollcommand=tac_scroll.set)

tac_scroll.pack(side=tk.RIGHT, fill=tk.Y)
tac_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

quad_tab = tk.Frame(notebook, bg=BG_CARD)
notebook.add(quad_tab, text=" Quadruples ")

quad_table = ttk.Treeview(
    quad_tab,
    columns=("No", "Operator", "Arg1", "Arg2", "Result"),
    show="headings",
)
quad_scroll = ttk.Scrollbar(
    quad_tab, orient=tk.VERTICAL, command=quad_table.yview
)
quad_table.configure(yscrollcommand=quad_scroll.set)

quad_table.heading("No", text="No")
quad_table.heading("Operator", text="Operator")
quad_table.heading("Arg1", text="Arg 1")
quad_table.heading("Arg2", text="Arg 2")
quad_table.heading("Result", text="Result")

quad_table.column("No", width=60, anchor="center")
quad_table.column("Operator", width=120, anchor="center")
quad_table.column("Arg1", width=160, anchor="center")
quad_table.column("Arg2", width=160, anchor="center")
quad_table.column("Result", width=160, anchor="center")

quad_table.tag_configure("even", background="#1e1e2e")
quad_table.tag_configure("odd", background="#252538")

quad_scroll.pack(side=tk.RIGHT, fill=tk.Y)
quad_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

triple_tab = tk.Frame(notebook, bg=BG_CARD)
notebook.add(triple_tab, text=" Triples ")

triple_table = ttk.Treeview(
    triple_tab, columns=("Index", "Operator", "Arg1", "Arg2"), show="headings"
)
triple_scroll = ttk.Scrollbar(
    triple_tab, orient=tk.VERTICAL, command=triple_table.yview
)
triple_table.configure(yscrollcommand=triple_scroll.set)

triple_table.heading("Index", text="Index")
triple_table.heading("Operator", text="Operator")
triple_table.heading("Arg1", text="Arg 1")
triple_table.heading("Arg2", text="Arg 2")

triple_table.column("Index", width=70, anchor="center")
triple_table.column("Operator", width=140, anchor="center")
triple_table.column("Arg1", width=200, anchor="center")
triple_table.column("Arg2", width=200, anchor="center")

triple_table.tag_configure("even", background="#1e1e2e")
triple_table.tag_configure("odd", background="#252538")

triple_scroll.pack(side=tk.RIGHT, fill=tk.Y)
triple_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.mainloop()