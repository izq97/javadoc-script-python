import os
import javalang
import random

# Carpeta raíz del código Java
JAVA_SRC_FOLDER = "src/main/java"

# Plantillas de frases para clases
CLASS_TEMPLATES = [
    "Provides core functionality related to {class_name}.",
    "Responsible for managing {class_name} operations.",
    "Data model representing {class_name}.",
    "Defines behaviors and state for {class_name}.",
    "Main class handling {class_name} logic."
]

# Plantillas de frases para métodos
METHOD_TEMPLATES = [
    "Executes the logic for {method_name}.",
    "Handles processing of {method_name}.",
    "Performs the operation defined by {method_name}.",
    "Responsible for executing {method_name} functionality.",
    "Initiates the process of {method_name}."
]

# Plantillas de frases para atributos
FIELD_TEMPLATES = [
    "Holds the value for {field_name}.",
    "Stores data related to {field_name}.",
    "Represents the state of {field_name}.",
    "Keeps track of {field_name}.",
    "Defines {field_name} used in this class."
]

def generate_class_comment(class_name):
    template = random.choice(CLASS_TEMPLATES)
    description = template.format(class_name=class_name)
    comment = f"/**\n * {description}\n */\n"
    return comment

def generate_method_comment(method_name, parameters, return_type):
    template = random.choice(METHOD_TEMPLATES)
    description = template.format(method_name=method_name)
    param_lines = ""
    for param in parameters:
        param_lines += f" * @param {param.name} The {param.name} parameter.\n"
    return_line = ""
    if return_type != "void":
        return_line = " * @return The result of the operation.\n"
    throws_line = " * @throws Exception if an error occurs during execution.\n"
    comment = "/**\n"
    comment += f" * {description}\n"
    comment += " *\n"
    comment += param_lines
    comment += return_line
    comment += throws_line
    comment += " */\n"
    return comment

def generate_field_comment(field_name):
    template = random.choice(FIELD_TEMPLATES)
    description = template.format(field_name=field_name)
    comment = f"/**\n * {description}\n */\n"
    return comment

def process_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    try:
        tree = javalang.parse.parse(code)
    except Exception as e:
        print(f"Skipping {file_path}: parse error {e}")
        return

    # Prepare new lines with potential new comments
    lines = code.splitlines(keepends=True)
    new_lines = []
    line_offset = 0

    # Process classes
    for path, node in tree.filter(javalang.tree.ClassDeclaration):
        class_line = node.position.line - 1
        if not is_line_commented(lines, class_line):
            comment = generate_class_comment(node.name)
            new_lines.append((class_line + line_offset, comment))
            line_offset += comment.count('\n')

    # Process methods
    for path, node in tree.filter(javalang.tree.MethodDeclaration):
        method_line = node.position.line - 1
        if not is_line_commented(lines, method_line):
            return_type = "void"
            if node.return_type is not None:
                return_type = node.return_type.name
            comment = generate_method_comment(node.name, node.parameters, return_type)
            new_lines.append((method_line + line_offset, comment))
            line_offset += comment.count('\n')

    # Process fields (only public)
    for path, node in tree.filter(javalang.tree.FieldDeclaration):
        if 'public' in node.modifiers:
            field_line = node.position.line - 1
            if not is_line_commented(lines, field_line):
                for declarator in node.declarators:
                    comment = generate_field_comment(declarator.name)
                    new_lines.append((field_line + line_offset, comment))
                    line_offset += comment.count('\n')

    # Apply changes
    if new_lines:
        print(f"Updating {file_path}")
        new_lines = sorted(new_lines, key=lambda x: x[0])
        offset = 0
        for insert_line, comment in new_lines:
            lines.insert(insert_line + offset, comment)
            offset += comment.count('\n')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

def is_line_commented(lines, index):
    # Look upwards for /** or //
    i = index - 1
    while i >= 0 and lines[i].strip() == '':
        i -= 1
    if i >= 0 and (lines[i].strip().startswith("/**") or lines[i].strip().startswith("/*") or lines[i].strip().startswith("//")):
        return True
    return False

def walk_java_files():
    for root, _, files in os.walk(JAVA_SRC_FOLDER):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                process_java_file(file_path)

if __name__ == "__main__":
    walk_java_files()
