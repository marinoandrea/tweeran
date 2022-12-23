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

    """
    TODO: relevant events for analysis
    [
        tweeran.TimelineEvent(date=date(2022, 9, 13), name="Arrest Mahsa Amini"),
        tweeran.TimelineEvent(date=date(2022, 9, 16), name="Death Mahsa Amini"),
        tweeran.TimelineEvent(date=date(2022, 9, 17), name="Funeral Protests"),
        tweeran.TimelineEvent(date=date(2022, 9, 22), name="National Protests"),
        tweeran.TimelineEvent(date=date(2022, 9, 30), name="Shootout Police Station"),
        tweeran.TimelineEvent(date=date(2022, 10, 3), name="Supreme Leader Talk"),
        tweeran.TimelineEvent(date=date(2022, 11, 21), name="Soccer Players Silent During Anthem"),
        tweeran.TimelineEvent(date=date(2022, 12, 4), name="Iran Abolishes Morality Police")
    ])
    """


if __name__ == '__main__':
    main()
