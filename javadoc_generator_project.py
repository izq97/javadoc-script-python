import os
import re

# Ruta raíz del código
JAVA_SRC_FOLDER = "src/main/java"

# Plantillas de comentarios

JAVADOC_TEMPLATE_CLASS = """/**
 * This class is part of the application architecture.
 * <p>
 * It encapsulates specific functionality and should be well-documented 
 * to clarify its role and usage within the system.
 * </p>
 */
"""

JAVADOC_TEMPLATE_METHOD = """/**
 * Executes the logic of this method.
 * <p>
 * Further documentation should describe the purpose of this method, 
 * its parameters, return value, and exceptions if any.
 * </p>
 *
 * @param param Description of parameter(s).
 * @return Description of the return value.
 * @throws ExceptionType Description of exceptions thrown.
 */
"""

JAVADOC_TEMPLATE_CONSTRUCTOR = """/**
 * Constructs an instance of this class.
 * <p>
 * Further documentation should clarify how this constructor initializes
 * the class and any important considerations.
 * </p>
 *
 * @param param Description of parameter(s).
 */
"""

JAVADOC_TEMPLATE_ATTRIBUTE = """/**
 * This attribute represents a part of the class state.
 * <p>
 * It should be documented to explain its role and constraints.
 * </p>
 */
"""

def has_javadoc(lines, index):
    # Mira si hay /** ... */ encima de la línea actual
    i = index - 1
    while i >= 0 and lines[i].strip() == '':
        i -= 1
    return i >= 0 and lines[i].strip().startswith("/**")

def process_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Clases / Interfaces / Enums
        if re.match(r'public\s+(class|interface|enum)\s+\w+', stripped):
            if not has_javadoc(lines, i):
                new_lines.append(JAVADOC_TEMPLATE_CLASS + "\n")
                modified = True

        # Constructores (nombre de la clase + paréntesis)
        elif re.match(r'public\s+\w+\s*\(', stripped):
            if not has_javadoc(lines, i):
                new_lines.append(JAVADOC_TEMPLATE_CONSTRUCTOR + "\n")
                modified = True

        # Métodos públicos
        elif re.match(r'public\s+[\w<>\[\]]+\s+\w+\s*\(', stripped):
            if not has_javadoc(lines, i):
                new_lines.append(JAVADOC_TEMPLATE_METHOD + "\n")
                modified = True

        # Atributos públicos
        elif re.match(r'public\s+[\w<>\[\]]+\s+\w+\s*(=|;)', stripped):
            if not has_javadoc(lines, i):
                new_lines.append(JAVADOC_TEMPLATE_ATTRIBUTE + "\n")
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
