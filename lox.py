import getopt
import sys

if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], "n:l:", ["name", "length"])

    for opt, arg in opts:
        if opt == "-n":
            app_name = arg
        if opt == "-l":
            pass_len = arg

    print(f"Name of app: {app_name}")
    print(f"Password length of app: {pass_len}")
