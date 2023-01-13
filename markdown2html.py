#!/usr/bin/python3
"""
Module for storing the markdown to html script.
"""
from sys import argv, stderr
from os.path import exists
from hashlib import md5
import re
from time import sleep


def h(line):
    """
    Creates a heading html element
    <h1..6>...</h1..6}>
    """
    line = line.replace("\n", "")

    line = line.strip()
    parse_space = line.split(" ")

    level = parse_space[0].count("#")

    if (level > 6):
        return(line)

    # Removes closing symbols at end of line.
    if len(parse_space[-1]) == parse_space[-1].count("#"):
        parse_space = parse_space[0:-1]

    # Concatenates the content string.
    content = ""
    for word in parse_space[1:]:
        content += word + " "
    content = content[0:-1]

    return("<h{}>{}</h{}>".format(level, content, level))


def li(line, flags):
    """
    Creates a list item html element.
    <li>...</li>
    """
    line = line.replace("\n", "")
    line = line.strip()
    parse_space = line.split(" ")

    # Concatenates the content string.
    content = ""
    for word in parse_space[1:]:
        content += word + " "
    content = content[0:-1]
    content = "<li>{}</li>\n".format(content)

    # if "-s" in flags:
    #     content = " " + content

    return(content)


def clean_line(line):
    """
    Styling tags with the use of Regular expressions.
    <b>...<\b><em>...<\em>
    [[...]] = md5(...)
    ((...)) = ... with no 'C' or 'c' characters.
    """
    # Replace ** for <b> tags
    line = re.sub(r"\*\*(\S+)", r"<b>\1", line)
    line = re.sub(r"(\S+)\*\*", r"\1</b>", line)

    # Replace __ for <em> tags
    line = re.sub(r"\_\_(\S+)", r"<em>\1", line)
    line = re.sub(r"(\S+)\_\_", r"\1</em>", line)

    # Replace [[<content>]] for md5 hash of content.
    line = re.sub(r"\[\[(.*)\]\]", md5(r"\1".encode()).hexdigest(), line)

    # Replace ((<content>)) for no C characters on content.
    result = re.search(r"(\(\((.*)\)\))", line)
    if result is not None:
        content = result.group(2)
        content = re.sub("[cC]", "", content)
        line = re.sub(r"\(\((.*)\)\)", content, line)

    return(line)


def mark2html(*argv):
    """
    Main method to parse and process markdown to html.
    """
    inputFile = argv[1]
    ouputFile = argv[2]
    flags = argv[3:]


    with open(inputFile, "r") as f:
        markdown = f.readlines()

    html = []

    # Iterate over lines of the read file.
    index = 0
    while index < len(markdown):
        line = clean_line(markdown[index])

        # If Heading.
        if line[0] == "#":
            html.append(h(line))

        # If ordered or unordered list.
        elif line[0] == "-" or line[0] == "*":
            list_type = {"-": "ul", "*": "ol"}
            current_index = index
            ul_string = "<{}>\n".format(list_type[line[0]])
            while (current_index < len(markdown) and
                   markdown[current_index][0] in ["-", "*"]):
                ul_string += li(markdown[current_index], flags)
                current_index += 1
            index = current_index - 1  # Because while ends one after.
            ul_string += "</{}>\n".format(list_type[line[0]])
            html.append(ul_string)

        # If only a newline.
        elif line[0] == "\n":
            line = ""

        # Else there are no special characters at beggining of line.
        else:
            paragraph = "<p>\n"
            new_index = index

            while new_index < len(markdown):
                line = clean_line(markdown[new_index])
                if ((new_index + 1) < len(markdown)
                        and markdown[new_index + 1] is not None):
                    next_line = markdown[new_index + 1]
                else:
                    next_line = "\n"
                if "-s" in flags:
                    line = "    " + line
                paragraph += line.strip() + "\n"
                if next_line[0] in ["*", "#", "-", "\n"]:
                    index = new_index
                    break

                # If next line has no special characters.
                if next_line[0] not in ["#", "-", "\n"]:
                    if "-s" in flags:
                        br = r"        <br />"
                    else:
                        br = r"<br/>"
                    br += "\n"
                    paragraph += br

                new_index += 1

            paragraph += "</p>\n"

            html.append(paragraph)

        index += 1

    # Create html text string with corresponding newlines.
    text = ""
    for line in html:
        if "\n" not in line:
            line += "\n"
        text += line

    if "-v" in flags:
        print(text)

    # Write into <ouputFile> file.
    with open(ouputFile, "w") as f:
        f.write(text)

    exit(0)


def perror(*args, **kwargs):
    """
    Printing to STDERR file descriptor.
    """
    print(*args, file=stderr, **kwargs)


if __name__ == "__main__":

    if len(argv) < 3:
        perror("Usage: ./markdown2html.py README.md README.html")
        # perror("Usage: ./markdown2html.py README.md README.html [-s]")
        exit(1)

    if exists(argv[1]) is False:
        perror("Missing {}".format(argv[1]))
        exit(1)

    mark2html(*argv)
