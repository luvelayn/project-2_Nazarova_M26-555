import prompt


def print_help():
    print()
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def welcome():
    print("Первая попытка запустить проект!")
    print("\n***")
    print_help()

    while True:
        command = prompt.string("Введите команду: ")

        if command == "exit":
            break
        elif command == "help":
            print_help()
