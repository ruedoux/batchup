from batchup.commands import Commands
from batchup.init import Init
from batchup.logger import SimpleLogger


logger = SimpleLogger(level="INFO")


def main() -> None:
    init = Init(logger)
    init.check_requirements()
    init.prepare_config()
    Commands(logger).parse_commands()


if __name__ == "__main__":
    main()
