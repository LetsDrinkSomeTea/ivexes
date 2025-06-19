def main():
    FILE_NAME = r"out.md"
    FILE_CONTENT = """

        """
    with open(FILE_NAME, "w") as file:
        file.write(FILE_CONTENT.strip())


if __name__ == "__main__":
    main()
