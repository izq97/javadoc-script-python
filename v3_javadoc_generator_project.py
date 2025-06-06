import os
import re
import random

JAVA_SRC_FOLDER = "src/main/java"

# --- Plantillas para clases ---
CLASS_TEMPLATES = {
    'Service': "Provides business logic for managing {entity}.",
    'Controller': "REST controller for handling {entity} requests.",
    'Repository': "Repository for accessing {entity} data.",
    'Manager': "Manager responsible for coordinating {entity} functionality.",
    'default': "Represents the {entity} component of the application."
}

# --- Plantillas para métodos ---
METHOD_PATTERNS = [
    (r'^get', "Retrieves {entity}."),
    (r'^set', "Sets the {entity}."),
    (r'^update', "Updates the {entity}."),
    (r'^delete', "Deletes the {entity}."),
    (r'^create', "Creates a new {entity}."),
    (r'^process', "Processes the {entity}."),
    (r'^calculate', "Calculates the {entity}."),
    (r'^load', "Loads the {entity}."),
    (r'^save', "Saves the {entity}."),
    (r'^send', "Sends the {entity}."),
    (r'^is', "Checks whether the {entity}."),
    (r'^has', "Determines whether the {entity} is present."),
    (r'^', "Performs the {entity} operation.")
]

# --- Plantillas para atributos ---
FIELD_TEMPLATE = "Represents the {field_name} of this class."

# --- Helper functions ---
def extract_entity(name):
    """Extracts a human-friendly entity name from a camelCase or PascalCase name."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1).lower()

def should_skip_file(file_name, class_declaration_line):
    if file_name.endswith("XML.java") or file_name.endswith("DTO.java"):
        return True
    if '<' in class_declaration_line:
        return True
    return False

def is_commented(lines, index):
    i = index - 1
    while i >= 0 and lines[i].strip() == '':
        i -= 1
    if i >= 0 and (lines[i].strip().startswith("/**") or lines[i].strip().startswith("/*") or lines[i].strip().startswith("//")):
        return True
    return False

# --- Comment generators ---
def generate_class_comment(class_name):
    entity = extract_entity(class_name.replace("Service", "").replace("Controller", "").replace("Repository", "").replace("Manager", ""))
    for suffix, template in CLASS_TEMPLATES.items():
        if class_name.endswith(suffix):
            desc = template.format(entity=entity)
            break
    else:
        desc = CLASS_TEMPLATES['default'].format(entity=entity)
    comment = f"/**\n * {desc}\n */\n"
    return comment

def generate_method_comment(method_name, param_names, has_return):
    entity = extract_entity(method_name.replace("get", "").replace("set", "").replace("update", "").replace("delete", "").replace("create", "").replace("process", "").replace("calculate", "").replace("load", "").replace("save", "").replace("send", "").replace("is", "").replace("has", ""))
    for pattern, template in METHOD_PATTERNS:
        if re.match(pattern, method_name):
            desc = template.format(entity=entity)
            break

    comment = "/**\n"
    comment += f" * {desc}\n"
    comment += " *\n"
    for param in param_names:
        comment += f" * @param {param} The {extract_entity(param)}.\n"
    if has_return:
        comment += " * @return The result of the operation.\n"
    comment += " * @throws Exception if an error occurs during execution.\n"
    comment += " */\n"
    return comment

def generate_field_comment(field_name):
    desc = FIELD_TEMPLATE.format(field_name=extract_entity(field_name))
    comment = f"/**\n * {desc}\n */\n"
    return comment

# --- Main processing ---
def process_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check for class/interface/enum
        match_class = re.match(r'public\s+(class|interface|enum)\s+(\w+)', line)
        if match_class:
            class_name = match_class.group(2)
            if should_skip_file(file_path, line):
                print(f"Skipping {file_path} due to <...> or XML/DTO.")
                return
            if not is_commented(lines, i):
                comment = generate_class_comment(class_name)
                new_lines.append(comment)
                modified = True

        # Check for public method
        match_method = re.match(r'public\s+[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)', line)
        if match_method:
            method_name = match_method.group(1)
            param_list = match_method.group(2)
            param_names = [p.strip().split()[-1] for p in param_list.split(',') if p.strip()] if param_list.strip() else []
            has_return = not re.match(r'public\s+void\s+', line)
            if not is_commented(lines, i):
                comment = generate_method_comment(method_name, param_names, has_return)
                new_lines.append(comment)
                modified = True

        # Check for public field
        match_field = re.match(r'public\s+[\w<>\[\]]+\s+(\w+)\s*(=|;)', line)
        if match_field:
            field_name = match_field.group(1)
            if not is_commented(lines, i):
                comment = generate_field_comment(field_name)
                new_lines.append(comment)
                modified = True

        new_lines.append(line)
        i += 1

    if modified:
        print(f"Updated: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

def walk_java_files():
    for root, _, files in os.walk(JAVA_SRC_FOLDER):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                process_java_file(file_path)

if __name__ == "__main__":
    walk_java_files()
