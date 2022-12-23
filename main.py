import dotenv

dotenv.load_dotenv()


def main():
    # we import the package here to prevent
    # env variables to be read before initialization with dotenv
    import tweeran.cli as tweeran_cli
    args = tweeran_cli.parse_args()
    data = tweeran_cli.extract(args) if args.extract\
        else tweeran_cli.load_data()
    if args.plot:
        tweeran_cli.plot(data)


if __name__ == '__main__':
    main()
