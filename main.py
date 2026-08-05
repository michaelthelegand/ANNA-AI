from config import settings
from brain.personality import current_persona


def main():
    print(f"{settings.APP_NAME} v{settings.VERSION} (scaffold; placeholders only).")
    print(current_persona.get_intro())


if __name__ == "__main__":
    main()
